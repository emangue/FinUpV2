#!/usr/bin/env python3
"""
perf_measure.py — Medição de performance real do FinUp em produção via Playwright + CDP

Mede tempo de carregamento de cada tela principal e cada filtro de mês/modo,
além de capturar quais chamadas de API são responsáveis pela demora.

Uso:
  python3 scripts/testing/perf_measure.py               → relatório no terminal
  python3 scripts/testing/perf_measure.py --headed      → abre janela do browser (debug)
  python3 scripts/testing/perf_measure.py --url https://meufinup.com.br  → URL customizada

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
import statistics
from pathlib import Path
from datetime import datetime

# ── Carregar .env.local ───────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_LOCAL = PROJECT_ROOT / ".env.local"
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            if key.strip() and key.strip() not in os.environ:
                os.environ[key.strip()] = value.strip()

# ── Cores ANSI ────────────────────────────────────────────────────────────────
GN = "\033[0;32m"; RD = "\033[0;31m"; YL = "\033[1;33m"
CY = "\033[0;36m"; BL = "\033[1m";    RS = "\033[0m"; GR = "\033[0;90m"

# ── Config ────────────────────────────────────────────────────────────────────
FRONTEND = os.environ.get("FRONTEND_URL", "https://meufinup.com.br")
BACKEND  = FRONTEND  # produção usa mesmo domínio (nginx proxy)
EMAIL    = os.environ.get("ADMIN_EMAIL", "admin@financas.com")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

SCREENSHOT_DIR = PROJECT_ROOT / "deploy" / "history" / "screenshots" / "perf"

# Telas do menu inferior (mobile) + telas desktop para medir
TELAS = [
    {"nome": "Dashboard (mobile)", "url": "/mobile/dashboard",    "esperar": "[class*='card'], h1, h2"},
    {"nome": "Transações",         "url": "/mobile/transactions",  "esperar": "[class*='transaction'], table, h1, [class*='list']"},
    {"nome": "Budget/Plano",       "url": "/mobile/plano",         "esperar": "main, h1, h2, [class*='budget'], [class*='plano']"},
    {"nome": "Investimentos",      "url": "/mobile/investimentos",  "esperar": "main, h1, h2, [class*='investimento']"},
    {"nome": "Upload",             "url": "/mobile/upload",         "esperar": "main, h1, button, [class*='upload']"},
]

# Filtros de modo do dashboard para medir separadamente
MODOS_DASHBOARD = ["Mês", "YTD", "Ano"]


def fmt_ms(ms: float) -> str:
    color = GN if ms < 500 else YL if ms < 1500 else RD
    return f"{color}{ms:.0f}ms{RS}"


def fmt_bar(ms: float, max_ms: float = 3000) -> str:
    pct = min(ms / max_ms, 1.0)
    filled = int(pct * 20)
    color = GN if ms < 500 else YL if ms < 1500 else RD
    return f"{color}{'█' * filled}{'░' * (20 - filled)}{RS}"


def save_screenshot(page, name: str) -> str:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    path = SCREENSHOT_DIR / f"{name.replace('/', '_').replace(' ', '_')}_{ts}.png"
    try:
        page.screenshot(path=str(path), full_page=False)
        return str(path.relative_to(PROJECT_ROOT))
    except Exception:
        return ""


def get_jwt_via_api(base_url: str) -> str:
    """Obtém JWT real via chamada direta à API (Python requests)."""
    try:
        import urllib.request
        req_data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
        req = urllib.request.Request(
            f"{base_url}/api/v1/auth/login",
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            return body.get("access_token", "")
    except Exception as e:
        print(f"  {RD}❌ Erro ao obter JWT: {e}{RS}")
        return ""


def login(page, ctx, base_url: str) -> bool:
    """Injeta cookie de auth via JWT obtido pela API e navega para dashboard."""
    jwt = get_jwt_via_api(base_url)
    if not jwt:
        return False

    # Injetar cookie auth_token no contexto do browser
    # O backend usa httpOnly cookie chamado auth_token
    ctx.add_cookies([
        {
            "name": "auth_token",
            "value": jwt,
            "domain": base_url.replace("https://", "").replace("http://", "").split("/")[0],
            "path": "/",
            "httpOnly": True,
            "secure": base_url.startswith("https"),
        }
    ])

    # Verificar que o cookie funciona navegando para uma página protegida
    try:
        page.goto(f"{base_url}/mobile/dashboard", wait_until="domcontentloaded", timeout=20_000)
        if "/auth/login" in page.url:
            print(f"  {RD}❌ Cookie não aceito — redirecionou para login{RS}")
            return False
        return True
    except Exception as e:
        print(f"  {RD}❌ Erro ao verificar autenticação: {e}{RS}")
        return False


def medir_api_calls(requests_log: list) -> list:
    """Filtra e ordena chamadas de API por duração."""
    api_calls = [r for r in requests_log if "/api/" in r.get("url", "")]
    return sorted(api_calls, key=lambda x: x.get("duration_ms", 0), reverse=True)


def medir_tela(page, tela: dict, base_url: str) -> dict:
    """Navega para uma tela e mede o tempo até estar visível e sem spinner."""
    requests_log = []

    def on_request(req):
        req._start_time = time.time()

    def on_response(resp):
        try:
            start = getattr(resp.request, "_start_time", time.time())
            duration = (time.time() - start) * 1000
            requests_log.append({
                "url": resp.url.replace(base_url, ""),
                "status": resp.status,
                "duration_ms": round(duration),
                "method": resp.request.method,
            })
        except Exception:
            pass

    page.on("request", on_request)
    page.on("response", on_response)

    t0 = time.time()
    try:
        page.goto(f"{base_url}{tela['url']}", wait_until="domcontentloaded", timeout=30_000)
        # Esperar conteúdo visível
        page.wait_for_selector(tela["esperar"], timeout=20_000)
        # Esperar network ficar idle (APIs concluírem)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        total_ms = round((time.time() - t0) * 1000)
        screenshot = save_screenshot(page, tela["nome"])

        # Remover listeners
        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)

        return {
            "nome": tela["nome"],
            "url": tela["url"],
            "total_ms": total_ms,
            "status": "ok",
            "screenshot": screenshot,
            "api_calls": medir_api_calls(requests_log),
        }

    except Exception as e:
        total_ms = round((time.time() - t0) * 1000)
        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)
        return {
            "nome": tela["nome"],
            "url": tela["url"],
            "total_ms": total_ms,
            "status": "erro",
            "erro": str(e),
            "api_calls": medir_api_calls(requests_log),
        }


def medir_filtro_mes(page, base_url: str, btn_texto: str) -> dict:
    """Clica no botão de filtro de modo e mede o tempo até a tela atualizar."""
    requests_log = []

    def on_request(req):
        req._start_time = time.time()

    def on_response(resp):
        try:
            start = getattr(resp.request, "_start_time", time.time())
            duration = (time.time() - start) * 1000
            if "/api/" in resp.url:
                requests_log.append({
                    "url": resp.url.replace(base_url, ""),
                    "status": resp.status,
                    "duration_ms": round(duration),
                    "method": resp.request.method,
                })
        except Exception:
            pass

    page.on("request", on_request)
    page.on("response", on_response)

    t0 = time.time()
    try:
        btn = page.locator(f"button:has-text('{btn_texto}')").first
        btn.wait_for(timeout=5_000)
        btn.click()

        # Aguardar respostas de API (network idle após o click)
        try:
            page.wait_for_load_state("networkidle", timeout=8_000)
        except Exception:
            pass
        # Buffer extra para renderização
        time.sleep(0.3)

        total_ms = round((time.time() - t0) * 1000)

        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)

        return {
            "modo": btn_texto,
            "total_ms": total_ms,
            "status": "ok",
            "api_calls": sorted(requests_log, key=lambda x: x["duration_ms"], reverse=True),
        }
    except Exception as e:
        total_ms = round((time.time() - t0) * 1000)
        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)
        return {
            "modo": btn_texto,
            "total_ms": total_ms,
            "status": "erro",
            "erro": str(e),
            "api_calls": [],
        }


def medir_troca_mes(page, base_url: str) -> list:
    """Mede o tempo de trocar para o mês anterior (seta ←) várias vezes."""
    resultados = []
    # Localizar botão de mês anterior
    setas = [
        "button[aria-label*='anterior'], button[aria-label*='prev']",
        "button:has-text('<'), button:has-text('‹'), button:has-text('←')",
        "[data-testid*='prev'], [data-testid*='anterior']",
    ]
    for _ in range(3):  # 3 trocas de mês
        requests_log = []

        def on_request(req):
            req._start_time = time.time()

        def on_response(resp):
            try:
                start = getattr(resp.request, "_start_time", time.time())
                duration = (time.time() - start) * 1000
                if "/api/" in resp.url:
                    requests_log.append({
                        "url": resp.url.replace(base_url, ""),
                        "status": resp.status,
                        "duration_ms": round(duration),
                    })
            except Exception:
                pass

        page.on("request", on_request)
        page.on("response", on_response)
        t0 = time.time()

        clicou = False
        for sel in setas:
            try:
                btn = page.locator(sel).first
                btn.wait_for(timeout=2_000)
                btn.click()
                clicou = True
                break
            except Exception:
                continue

        if clicou:
            try:
                page.wait_for_load_state("networkidle", timeout=8_000)
            except Exception:
                pass
            time.sleep(0.2)
            total_ms = round((time.time() - t0) * 1000)
            resultados.append({
                "acao": "troca_mes_anterior",
                "total_ms": total_ms,
                "api_calls": sorted(requests_log, key=lambda x: x["duration_ms"], reverse=True),
            })
        else:
            resultados.append({
                "acao": "troca_mes_anterior",
                "total_ms": 0,
                "status": "nao_encontrado",
                "api_calls": [],
            })
            break

        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)

    return resultados


def print_api_calls(api_calls: list, top: int = 5):
    """Imprime as top N chamadas de API mais lentas."""
    if not api_calls:
        print(f"    {GR}(nenhuma chamada de API capturada){RS}")
        return
    for call in api_calls[:top]:
        dur = call["duration_ms"]
        color = GN if dur < 200 else YL if dur < 800 else RD
        endpoint = call["url"][:65]
        print(f"    {color}{dur:>5}ms{RS}  {GR}{call.get('method','GET')}{RS}  {endpoint}")


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

    resultados_telas = []
    resultados_modos = []
    resultados_mes = []

    print(f"\n{BL}{CY}╔═══════════════════════════════════════════════════════════╗{RS}")
    print(f"{BL}{CY}║        ⏱️  FinUp — Medição de Performance (Playwright)      ║{RS}")
    print(f"{BL}{CY}╚═══════════════════════════════════════════════════════════╝{RS}")
    print(f"  Site     : {CY}{base_url}{RS}")
    print(f"  Usuário  : {CY}{EMAIL}{RS}")
    print(f"  Início   : {datetime.now().strftime('%H:%M:%S')}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        # Viewport mobile (390x844 = iPhone 14 Pro)
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        )
        page = ctx.new_page()
        page.set_default_timeout(25_000)

        # ── Login ─────────────────────────────────────────────────────────────
        print(f"{BL}1. Autenticando via API + cookie injection...{RS}")
        t_login0 = time.time()
        ok = login(page, ctx, base_url)
        t_login = round((time.time() - t_login0) * 1000)
        if not ok:
            browser.close()
            return
        print(f"  {GN}✅ Login OK{RS}  {fmt_ms(t_login)}\n")

        # ── Medição de cada tela ──────────────────────────────────────────────
        print(f"{BL}2. Medindo tempo de carregamento de cada tela...{RS}")
        for tela in TELAS:
            r = medir_tela(page, tela, base_url)
            resultados_telas.append(r)

            status_icon = GN + "✅" + RS if r["status"] == "ok" else RD + "❌" + RS
            print(f"\n  {status_icon}  {BL}{r['nome']}{RS}  →  {fmt_ms(r['total_ms'])}")
            print(f"       {fmt_bar(r['total_ms'])}")
            if r.get("erro"):
                print(f"       {RD}Erro: {r['erro'][:80]}{RS}")
            if r["api_calls"]:
                print(f"       {GR}Top APIs mais lentas:{RS}")
                print_api_calls(r["api_calls"], top=5)
            if r.get("screenshot"):
                print(f"       {GR}Screenshot: {r['screenshot']}{RS}")

        # ── Medição dos filtros de modo (Mês/YTD/Ano) ─────────────────────────
        print(f"\n{BL}3. Medindo troca de modo (Mês / YTD / Ano) no Dashboard...{RS}")
        page.goto(f"{base_url}/mobile/dashboard", wait_until="domcontentloaded", timeout=30_000)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        for modo in MODOS_DASHBOARD:
            r = medir_filtro_mes(page, base_url, modo)
            resultados_modos.append(r)
            status_icon = GN + "✅" + RS if r["status"] == "ok" else RD + "❌" + RS
            print(f"\n  {status_icon}  Modo {BL}{modo}{RS}  →  {fmt_ms(r['total_ms'])}")
            print(f"       {fmt_bar(r['total_ms'])}")
            if r["api_calls"]:
                print(f"       {GR}APIs disparadas:{RS}")
                print_api_calls(r["api_calls"], top=6)

        # ── Medição de troca de mês (← anterior) ─────────────────────────────
        print(f"\n{BL}4. Medindo troca de mês (botão ← anterior) 3x...{RS}")
        page.goto(f"{base_url}/mobile/dashboard", wait_until="domcontentloaded", timeout=30_000)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        resultados_mes = medir_troca_mes(page, base_url)
        for i, r in enumerate(resultados_mes, 1):
            if r["total_ms"] == 0 and r.get("status") == "nao_encontrado":
                print(f"\n  {YL}⚠️  Botão de mês anterior não encontrado — verificar seletor{RS}")
                break
            print(f"\n  Troca {i}:  {fmt_ms(r['total_ms'])}")
            print(f"       {fmt_bar(r['total_ms'])}")
            if r["api_calls"]:
                print(f"       {GR}APIs disparadas:{RS}")
                print_api_calls(r["api_calls"], top=6)

        browser.close()

    # ── Resumo final ──────────────────────────────────────────────────────────
    print(f"\n{BL}{CY}{'═' * 60}{RS}")
    print(f"{BL}RESUMO — Tempos de carregamento{RS}")
    print(f"{BL}{CY}{'═' * 60}{RS}")

    todos_tempos = [r["total_ms"] for r in resultados_telas if r["status"] == "ok"]

    print(f"\n  {'Tela':<28} {'Tempo':>8}  {'Barra'}")
    print(f"  {'─'*28} {'─'*8}  {'─'*20}")
    for r in resultados_telas:
        status = "" if r["status"] == "ok" else f" {RD}(erro){RS}"
        color = GN if r["total_ms"] < 500 else YL if r["total_ms"] < 1500 else RD
        print(f"  {r['nome']:<28} {color}{r['total_ms']:>6}ms{RS}  {fmt_bar(r['total_ms'])}{status}")

    print(f"\n  {'Modo Dashboard':<28} {'Tempo':>8}  {'Barra'}")
    print(f"  {'─'*28} {'─'*8}  {'─'*20}")
    for r in resultados_modos:
        status = "" if r["status"] == "ok" else f" {RD}(erro){RS}"
        color = GN if r["total_ms"] < 300 else YL if r["total_ms"] < 800 else RD
        print(f"  Filtro → {r['modo']:<19} {color}{r['total_ms']:>6}ms{RS}  {fmt_bar(r['total_ms'], 1500)}{status}")

    if [r for r in resultados_mes if r["total_ms"] > 0]:
        print(f"\n  {'Troca de mês':<28} {'Tempo':>8}  {'Barra'}")
        print(f"  {'─'*28} {'─'*8}  {'─'*20}")
        for i, r in enumerate([x for x in resultados_mes if x["total_ms"] > 0], 1):
            color = GN if r["total_ms"] < 300 else YL if r["total_ms"] < 800 else RD
            print(f"  Troca {i:<22} {color}{r['total_ms']:>6}ms{RS}  {fmt_bar(r['total_ms'], 1500)}")

    if todos_tempos:
        print(f"\n  {GR}Média telas:  {statistics.mean(todos_tempos):.0f}ms{RS}")
        print(f"  {GR}Máximo:       {max(todos_tempos)}ms  ({[r['nome'] for r in resultados_telas if r['total_ms'] == max(todos_tempos)][0]}){RS}")
        print(f"  {GR}Mínimo:       {min(todos_tempos)}ms{RS}")

    print(f"\n  {GR}Legenda: {GN}< 500ms ✅  {RS}{GR}| {YL}500–1500ms ⚠️   {RS}{GR}| {RD}>1500ms ❌{RS}\n")

    # Salvar JSON completo
    output = {
        "timestamp": datetime.now().isoformat(),
        "site": base_url,
        "telas": resultados_telas,
        "modos_dashboard": resultados_modos,
        "troca_mes": resultados_mes,
    }
    out_path = PROJECT_ROOT / "deploy" / "history" / f"perf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"  {GR}Relatório JSON salvo em: {out_path.relative_to(PROJECT_ROOT)}{RS}\n")


def main():
    parser = argparse.ArgumentParser(description="FinUp Performance Measurement (Playwright)")
    parser.add_argument("--headed", action="store_true", help="Abre janela do browser")
    parser.add_argument("--url", default=FRONTEND, help="URL base do site (padrão: https://meufinup.com.br)")
    args = parser.parse_args()
    run(headed=args.headed, base_url=args.url.rstrip("/"))


if __name__ == "__main__":
    main()
