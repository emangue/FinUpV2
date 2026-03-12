#!/usr/bin/env python3
"""
perf_s2_verify.py — Verifica eliminação de fetches redundantes de onboarding após Sprint 2 (P1)

Testa se:
  P1-A: Dashboard 2ª visita não faz fetch de /onboarding/progress (cache localStorage ativo)
  P1-B: Navegação via bottom nav não faz fetch de /onboarding/progress
  P1-C: localStorage contém 'onboarding_completo = true' após primeira visita

Uso:
  python3 scripts/testing/perf_s2_verify.py
  python3 scripts/testing/perf_s2_verify.py --url https://meufinup.com.br
  python3 scripts/testing/perf_s2_verify.py --headed   (abre browser para debug)

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
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # docs/features/performance-prod-fixes/ → 4 níveis → raiz do projeto
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

ONBOARDING_URL_PATTERN = "/api/v1/onboarding/progress"


def get_jwt(base_url: str) -> str:
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


def contar_onboarding_calls(page, url: str, base_url: str, wait_ms: float = 2000) -> tuple[int, int]:
    """
    Navega para a URL e conta quantas vezes /onboarding/progress foi chamada.
    Retorna (tempo_ms, quantidade_de_calls).
    """
    count = 0

    def on_response(resp):
        nonlocal count
        if ONBOARDING_URL_PATTERN in resp.url:
            count += 1

    page.on("response", on_response)
    t0 = time.time()
    page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    try:
        page.wait_for_load_state("networkidle", timeout=8_000)
    except Exception:
        pass
    time.sleep(wait_ms / 1000)
    page.remove_listener("response", on_response)

    return round((time.time() - t0) * 1000), count


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
    print(f"{BL}{CY}║     🧪 Sprint 2 — Verificação de Onboarding Cache (P1)     ║{RS}")
    print(f"{BL}{CY}╚═══════════════════════════════════════════════════════════╝{RS}")
    print(f"  Site  : {CY}{base_url}{RS}\n")

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
        print(f"{BL}1. Autenticando...{RS}")
        jwt = get_jwt(base_url)
        if not jwt:
            browser.close()
            sys.exit(2)
        domain = base_url.replace("https://", "").replace("http://", "").split("/")[0]
        ctx.add_cookies([{
            "name": "auth_token", "value": jwt, "domain": domain,
            "path": "/", "httpOnly": True, "secure": base_url.startswith("https"),
        }])
        page.goto(f"{base_url}/mobile/dashboard", wait_until="domcontentloaded", timeout=20_000)
        if "/auth/login" in page.url:
            print(f"  {RD}❌ Cookie não aceito{RS}"); browser.close(); sys.exit(2)
        print(f"  {GN}✅ Login OK{RS}\n")

        # ── P1-A: Dashboard 1ª visita ─────────────────────────────────────────
        # (o localStorage pode já ter o cache se o usuário visitou antes)
        # Limpar localStorage para simular primeira visita
        print(f"{BL}2. Limpando localStorage para simular primeira visita...{RS}")
        page.evaluate("""() => {
            localStorage.removeItem('onboarding_completo');
            localStorage.removeItem('onboarding_pulado');
            sessionStorage.removeItem('sem_demo');
        }""")
        print(f"  {GR}localStorage.removeItem('onboarding_completo') executado{RS}\n")

        print(f"{BL}3. Dashboard — PRIMEIRA visita (espera 1 fetch de onboarding)...{RS}")
        ms_1, calls_1 = contar_onboarding_calls(page, f"{base_url}/mobile/dashboard", base_url)
        # Na 1ª visita, é ESPERADO que haja 1 fetch (OnboardingGuard verifica pela primeira vez)
        ok_1 = calls_1 <= 2 and ms_1 < 5000  # até 2 é aceitável (guard + um componente)
        status_1 = f"{GN}✅ PASS{RS}" if ok_1 else f"{RD}❌ FAIL{RS}"
        nota_1 = f"{ms_1}ms, {calls_1} chamada(s) de /onboarding/progress"
        print(f"  {status_1}  1ª visita  ({nota_1})")
        if calls_1 > 2:
            print(f"         {YL}→ {calls_1} chamadas na 1ª visita é muitas — OnboardingGuard deduplicando?{RS}")
        resultados.append(("P1-A: Dashboard 1ª visita (≤2 chamadas)", ok_1, nota_1))

        # ── Verificar que o cache foi persistido ──────────────────────────────
        print(f"\n{BL}4. Verificando localStorage após 1ª visita...{RS}")
        ls_value = page.evaluate("() => localStorage.getItem('onboarding_completo')")
        ok_ls = ls_value == "true"
        status_ls = f"{GN}✅ PASS{RS}" if ok_ls else f"{RD}❌ FAIL{RS}"
        nota_ls = f"localStorage['onboarding_completo'] = {repr(ls_value)}"
        print(f"  {status_ls}  Cache persistido  ({nota_ls})")
        if not ok_ls:
            print(f"         {YL}→ OnboardingGuard não chamou localStorage.setItem após onboarding_completo?{RS}")
        resultados.append(("P1-B: Cache persistido no localStorage", ok_ls, nota_ls))

        # ── P1-C: Dashboard 2ª visita (cache deve bloquear fetch) ─────────────
        print(f"\n{BL}5. Dashboard — SEGUNDA visita (espera 0 fetches de onboarding)...{RS}")
        ms_2, calls_2 = contar_onboarding_calls(page, f"{base_url}/mobile/dashboard", base_url)
        ok_2 = calls_2 == 0 and ms_2 < 2000
        status_2 = f"{GN}✅ PASS{RS}" if ok_2 else f"{RD}❌ FAIL{RS}"
        nota_2 = f"{ms_2}ms, {calls_2} chamada(s) de /onboarding/progress"
        print(f"  {status_2}  2ª visita (cache hit)  ({nota_2})")
        if calls_2 > 0:
            print(f"         {YL}→ {calls_2} chamada(s) na 2ª visita — cache localStorage não funciona?{RS}")
            print(f"         {YL}→ Verificar: 'const completo = localStorage.getItem(ONBOARDING_COMPLETO_KEY)'{RS}")
        resultados.append(("P1-C: Dashboard 2ª visita (0 chamadas)", ok_2, nota_2))

        # ── P1-D: Navegação bottom nav ────────────────────────────────────────
        print(f"\n{BL}6. Navegação via bottom nav — Transações (espera 0 fetches)...{RS}")
        ms_3, calls_3 = contar_onboarding_calls(page, f"{base_url}/mobile/transactions", base_url, wait_ms=1500)
        ok_3 = calls_3 == 0 and ms_3 < 2000
        status_3 = f"{GN}✅ PASS{RS}" if ok_3 else f"{RD}❌ FAIL{RS}"
        nota_3 = f"{ms_3}ms, {calls_3} chamada(s) de /onboarding/progress"
        print(f"  {status_3}  Navegação bottom nav  ({nota_3})")
        if calls_3 > 0:
            print(f"         {YL}→ OnboardingGuard ainda fazendo fetch na troca de rota?{RS}")
        resultados.append(("P1-D: Navegação bottom nav (0 chamadas)", ok_3, nota_3))

        browser.close()

    # ── Resumo ────────────────────────────────────────────────────────────────
    print(f"\n{BL}{CY}{'═' * 55}{RS}")
    print(f"{BL}RESUMO — Sprint 2{RS}")
    print(f"{BL}{CY}{'═' * 55}{RS}\n")

    todos_ok = True
    for nome, ok, nota in resultados:
        icon = f"{GN}✅ PASS{RS}" if ok else f"{RD}❌ FAIL{RS}"
        print(f"  {icon}  {nome}  ({nota})")
        if not ok:
            todos_ok = False

    print()
    if todos_ok:
        print(f"  {GN}🎉 Sprint 2 completo — onboarding cache funcionando!{RS}")
        print(f"  {GR}Próximo: Sprint 3 — Backend Cache Cashflow (P2){RS}\n")
    else:
        print(f"  {RD}❌ Falhas detectadas — verificar os itens acima antes do deploy.{RS}\n")

    sys.exit(0 if todos_ok else 1)


def main():
    parser = argparse.ArgumentParser(description="Sprint 2 — Verificação de Onboarding Cache (P1)")
    parser.add_argument("--headed", action="store_true", help="Abre janela do browser")
    parser.add_argument("--url", default=FRONTEND, help="URL base do site")
    args = parser.parse_args()

    if not PASSWORD:
        print(f"\n{RD}❌ ADMIN_PASSWORD não definido. Adicione em .env.local{RS}\n")
        sys.exit(2)

    run(headed=args.headed, base_url=args.url.rstrip("/"))


if __name__ == "__main__":
    main()
