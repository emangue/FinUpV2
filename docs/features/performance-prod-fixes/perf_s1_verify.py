#!/usr/bin/env python3
"""
perf_s1_verify.py — Verifica eliminação de double-fetch após Sprint 1 (P7 + P8)

Testa se:
  P7: Carteira e Investimentos disparam apenas 1 batch de requests (não 2)
  P8: Transações disparam apenas 1 par de list+resumo (não 2 com offset 400ms)

Uso:
  python3 scripts/testing/perf_s1_verify.py
  python3 scripts/testing/perf_s1_verify.py --url https://meufinup.com.br
  python3 scripts/testing/perf_s1_verify.py --headed   (abre browser para debug)

Variáveis de ambiente (ou .env.local):
  ADMIN_EMAIL     (padrão: admin@financas.com)
  ADMIN_PASSWORD  (obrigatório)
  FRONTEND_URL    (padrão: https://meufinup.com.br)
"""

import sys
import os
import json
import time
import argparse
import urllib.request
from pathlib import Path

# ── Carregar .env.local ───────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_LOCAL = PROJECT_ROOT / ".env.local"
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            if k.strip() and k.strip() not in os.environ:
                os.environ[k.strip()] = v.strip()

FRONTEND = os.environ.get("FRONTEND_URL", "https://meufinup.com.br")
EMAIL    = os.environ.get("ADMIN_EMAIL", "admin@financas.com")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# ── Cores ANSI ────────────────────────────────────────────────────────────────
GN = "\033[0;32m"; RD = "\033[0;31m"; YL = "\033[1;33m"
CY = "\033[0;36m"; BL = "\033[1m";    RS = "\033[0m"; GR = "\033[0;90m"


def get_jwt(base_url: str) -> str:
    """Obtém JWT via API."""
    try:
        data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
        req = urllib.request.Request(
            f"{base_url}/api/v1/auth/login",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()).get("access_token", "")
    except Exception as e:
        print(f"  {RD}❌ Erro ao obter JWT: {e}{RS}")
        return ""


def detectar_batches(requests_log: list, pattern: str, window_ms: float = 300) -> tuple[int, list]:
    """
    Agrupa requests que correspondem ao padrão em 'batches' separados por silêncio > window_ms.
    Retorna (número de batches, lista de calls filtradas).
    """
    calls = sorted(
        [r for r in requests_log if pattern in r.get("url", "")],
        key=lambda x: x["t_ms"],
    )
    if not calls:
        return 0, []

    batches = 1
    for i in range(1, len(calls)):
        if calls[i]["t_ms"] - calls[i - 1]["t_ms"] > window_ms:
            batches += 1
    return batches, calls


def medir_tela(page, url: str, pattern: str, base_url: str) -> tuple[int, list]:
    """
    Navega para a URL e captura requests que contêm o padrão.
    Retorna (tempo_total_ms, lista_de_requests).
    """
    log = []

    def on_response(resp):
        if pattern in resp.url:
            log.append({"url": resp.url.replace(base_url, ""), "t_ms": time.time() * 1000})

    page.on("response", on_response)
    t0 = time.time()
    page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    try:
        page.wait_for_load_state("networkidle", timeout=10_000)
    except Exception:
        pass
    time.sleep(0.6)  # buffer para capturar requests atrasados (como o debounce de 400ms)
    page.remove_listener("response", on_response)

    return round((time.time() - t0) * 1000), log


def run(headed: bool, base_url: str):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"\n{RD}❌ Playwright não instalado:{RS}")
        print("   pip install playwright && playwright install chromium\n")
        sys.exit(2)

    if not PASSWORD:
        print(f"\n{RD}❌ ADMIN_PASSWORD não definido. Adicione em .env.local{RS}\n")
        sys.exit(2)

    print(f"\n{BL}{CY}╔═══════════════════════════════════════════════════════════╗{RS}")
    print(f"{BL}{CY}║       🧪 Sprint 1 — Verificação de Double-Fetch (P7+P8)    ║{RS}")
    print(f"{BL}{CY}╚═══════════════════════════════════════════════════════════╝{RS}")
    print(f"  Site  : {CY}{base_url}{RS}")
    print(f"  Email : {CY}{EMAIL}{RS}\n")

    resultados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        )
        page = ctx.new_page()
        page.set_default_timeout(25_000)

        # Autenticar
        print(f"{BL}Autenticando...{RS}")
        jwt = get_jwt(base_url)
        if not jwt:
            browser.close()
            sys.exit(2)

        domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]
        ctx.add_cookies([{
            "name": "auth_token",
            "value": jwt,
            "domain": domain,
            "path": "/",
            "httpOnly": True,
            "secure": base_url.startswith("https"),
        }])

        # Navegar para dashboard para pré-aquecer auth
        page.goto(f"{base_url}/mobile/dashboard", wait_until="domcontentloaded", timeout=20_000)
        if "/auth/login" in page.url:
            print(f"  {RD}❌ Cookie não aceito — redirecionou para login{RS}")
            browser.close()
            sys.exit(2)
        print(f"  {GN}✅ Login OK{RS}\n")

        # ── P7: Carteira ──────────────────────────────────────────────────────
        print(f"{BL}P7 — Carteira (double-fetch com selectedMonth = new Date()){RS}")
        ms, log = medir_tela(
            page,
            f"{base_url}/mobile/carteira",
            "/api/v1/investimentos",
            base_url,
        )
        batches, calls = detectar_batches(log, "/api/v1/investimentos")
        ok = batches <= 1 and ms < 1000
        status = f"{GN}✅ PASS{RS}" if ok else f"{RD}❌ FAIL{RS}"
        nota = f"{ms}ms, {batches} batch(es) de /investimentos"
        print(f"  {status}  P7 Carteira  ({nota})")
        if not ok:
            print(f"         {YL}→ selectedMonth ainda iniciando com new Date() na linha 241?{RS}")
            print(f"         {YL}→ Verificar: guard 'if (!selectedMonth) return' no useEffect{RS}")
        for c in calls[:4]:
            print(f"         {GR}{c['url'][:70]}{RS}")
        resultados.append(("P7 Carteira (double-fetch)", ok, nota))

        # ── P7: Investimentos ─────────────────────────────────────────────────
        print(f"\n{BL}P7 — Investimentos (double-fetch com selectedMonth = new Date()){RS}")
        ms, log = medir_tela(
            page,
            f"{base_url}/mobile/investimentos",
            "/api/v1/investimentos",
            base_url,
        )
        batches, calls = detectar_batches(log, "/api/v1/investimentos")
        ok = batches <= 1 and ms < 1000
        status = f"{GN}✅ PASS{RS}" if ok else f"{RD}❌ FAIL{RS}"
        nota = f"{ms}ms, {batches} batch(es) de /investimentos"
        print(f"  {status}  P7 Investimentos  ({nota})")
        if not ok:
            print(f"         {YL}→ selectedMonth na linha 51 de investimentos/page.tsx?{RS}")
            print(f"         {YL}→ Verificar: loadInvestimentos tem guard 'if (!isAuth || !selectedMonth) return'{RS}")
        resultados.append(("P7 Investimentos (double-fetch)", ok, nota))

        # ── P8: Transações ────────────────────────────────────────────────────
        print(f"\n{BL}P8 — Transações (debounce instável com periodFilterRef){RS}")
        ms, log = medir_tela(
            page,
            f"{base_url}/mobile/transactions",
            "transactions/list",
            base_url,
        )
        batches, calls = detectar_batches(log, "transactions/list", window_ms=300)
        ok = batches <= 1 and ms < 700
        status = f"{GN}✅ PASS{RS}" if ok else f"{RD}❌ FAIL{RS}"
        nota = f"{ms}ms, {batches} batch(es) de transactions/list"
        print(f"  {status}  P8 Transações  ({nota})")
        if not ok:
            print(f"         {YL}→ setDebouncedPeriod ainda cria novo objeto? (linhas 132-144){RS}")
            print(f"         {YL}→ Verificar: usa setState funcional com comparação de igualdade?{RS}")
        resultados.append(("P8 Transações (debounce race)", ok, nota))

        browser.close()

    # ── Resumo ────────────────────────────────────────────────────────────────
    print(f"\n{BL}{CY}{'═' * 55}{RS}")
    print(f"{BL}RESUMO — Sprint 1{RS}")
    print(f"{BL}{CY}{'═' * 55}{RS}\n")

    todos_ok = True
    for nome, ok, nota in resultados:
        icon = f"{GN}✅ PASS{RS}" if ok else f"{RD}❌ FAIL{RS}"
        print(f"  {icon}  {nome}  ({nota})")
        if not ok:
            todos_ok = False

    print()
    if todos_ok:
        print(f"  {GN}🎉 Sprint 1 completo — todos os double-fetches eliminados!{RS}")
        print(f"  {GR}Próximo: Sprint 2 — Onboarding Cache (P1){RS}\n")
    else:
        print(f"  {RD}❌ Falhas detectadas — verificar os itens acima antes do deploy.{RS}\n")

    sys.exit(0 if todos_ok else 1)


def main():
    parser = argparse.ArgumentParser(description="Sprint 1 — Verificação de Double-Fetch (P7+P8)")
    parser.add_argument("--headed", action="store_true", help="Abre janela do browser")
    parser.add_argument("--url", default=FRONTEND, help="URL base do site")
    args = parser.parse_args()

    if not PASSWORD:
        print(f"\n{RD}❌ ADMIN_PASSWORD não definido. Adicione em .env.local:{RS}")
        print("   ADMIN_PASSWORD=sua_senha_aqui\n")
        sys.exit(2)

    run(headed=args.headed, base_url=args.url.rstrip("/"))


if __name__ == "__main__":
    main()
