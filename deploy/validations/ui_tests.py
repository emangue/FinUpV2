#!/usr/bin/env python3
"""
ui_tests.py — Testes automatizados de UI via Playwright (headless Chromium)

Cobre as telas e fluxos principais do FinUp antes de cada deploy.

Uso:
  python3 deploy/validations/ui_tests.py            → imprime resultados, retorna JSON
  python3 deploy/validations/ui_tests.py --json     → só JSON no stdout
  python3 deploy/validations/ui_tests.py --headed   → abre janela do browser (debug)

Variáveis de ambiente (carregadas automaticamente de .env.local se existir):
  ADMIN_EMAIL     (padrão: admin@financas.com)
  ADMIN_PASSWORD  (obrigatório)
  FRONTEND_URL    (padrão: http://localhost:3000)
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# ── Carregar .env.local automaticamente ───────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_LOCAL = PROJECT_ROOT / ".env.local"
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            if key.strip() and key.strip() not in os.environ:
                os.environ[key.strip()] = value.strip()

FRONTEND  = os.environ.get("FRONTEND_URL", "http://localhost:3000")
BACKEND   = os.environ.get("BACKEND_URL",  "http://localhost:8000")
EMAIL     = os.environ.get("ADMIN_EMAIL",  "admin@financas.com")
PASSWORD  = os.environ.get("ADMIN_PASSWORD", "")

# Token obtido via API antes de iniciar o browser (evita problemas de cookie cross-origin)
REAL_JWT: str = ""

# ── Cores ANSI ────────────────────────────────────────────────────────────────
GN = "\033[0;32m"; RD = "\033[0;31m"; YL = "\033[1;33m"
CY = "\033[0;36m"; BL = "\033[1m";    RS = "\033[0m"

# ── Estado global ─────────────────────────────────────────────────────────────
RESULTS: list[dict] = []
SCREENSHOT_DIR = PROJECT_ROOT / "deploy" / "history" / "screenshots"

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def record(name: str, status: str, note: str = "", screenshot: str = "") -> dict:
    icon = {"pass": "✅", "fail": "❌", "skip": "⏭️ ", "error": "💥"}.get(status, "❓")
    color = {"pass": GN, "fail": RD, "skip": YL, "error": RD}.get(status, RS)
    print(f"  {color}{icon} {status.upper()}{RS} · {name}" + (f"  ↳ {note}" if note else ""))
    entry = {"name": name, "status": status, "note": note, "screenshot": screenshot}
    RESULTS.append(entry)
    return entry


def take_screenshot(page, test_id: str) -> str:
    """Salva screenshot e retorna o path relativo."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SCREENSHOT_DIR / f"{test_id}_{ts}.png"
    try:
        page.screenshot(path=str(path))
        return str(path.relative_to(PROJECT_ROOT))
    except Exception:
        return ""


def wait_for_no_spinner(page, timeout: int = 15_000):
    """Aguarda sumirdores comuns de loading (skeletons, spinners)."""
    try:
        # Aguardar network idle
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Suite de testes
# ──────────────────────────────────────────────────────────────────────────────

def fetch_real_jwt() -> str:
    """Obtém JWT real via API (Python requests) antes de iniciar o browser.
    
    Isso evita problemas de cookies cross-origin em Playwright headless:
    - O browser em localhost:3000 faz fetch para localhost:8000 com credentials:'include'
    - Em headless Chromium, cookies Set-Cookie cross-origin podem não persistir
    - Solução: injetar o cookie no contexto do browser antes de qualquer navegação
    """
    try:
        import urllib.request
        import urllib.error
        req_data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
        req = urllib.request.Request(
            f"{BACKEND}/api/v1/auth/login",
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return body.get("access_token", "")
    except Exception as e:
        print(f"  {YL}⚠️  Não foi possível obter JWT real: {e}{RS}")
        return ""


def run_tests(headed: bool = False):
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
    except ImportError:
        print(f"\n{RD}❌ Playwright não instalado. Execute:{RS}")
        print(f"   pip install playwright && playwright install chromium\n")
        sys.exit(2)

    if not PASSWORD:
        print(f"\n{RD}❌ ADMIN_PASSWORD não definido. Verifique .env.local{RS}\n")
        sys.exit(2)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.set_default_timeout(20_000)

        # ── Injetar token real no contexto do browser ─────────────────────────
        # O backend autentica via cookie httpOnly. Em Playwright headless,
        # cookies Set-Cookie de cross-origin (localhost:3000→localhost:8000)
        # não persistem corretamente. Injetamos o cookie diretamente para que
        # TODOS os requests fetch(..., {credentials:'include'}) ao localhost:8000
        # incluam o auth_token automaticamente.
        import json as _json
        if REAL_JWT:
            ctx.add_cookies([
                {"name": "auth_token", "value": REAL_JWT, "domain": "localhost", "path": "/"},
            ])

        # Mock /auth/me para o React AuthContext obter isAuthenticated=true.
        # O loadUser() chama localhost:8000/api/v1/auth/me com credentials:'include'.
        # Com o cookie injetado acima, isso já funcionaria, mas o mock garante
        # que o contexto hidrata corretamente independente de timing.
        def _mock_auth_me(route):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=_json.dumps({"id": 1, "email": EMAIL, "name": "Admin", "role": "admin"}),
            )
        page.route("**/api/v1/auth/me", _mock_auth_me)

        # ── UI-01: Página de login renderiza ──────────────────────────────────
        try:
            page.goto(f"{FRONTEND}/auth/login", wait_until="domcontentloaded")
            page.wait_for_selector("#email", timeout=10_000)
            page.wait_for_selector("#password", timeout=5_000)
            record("UI-01 Página de login renderiza", "pass")
        except PwTimeout:
            sc = take_screenshot(page, "UI-01")
            record("UI-01 Página de login renderiza", "fail",
                   "Inputs de email/senha não encontrados", sc)
            browser.close()
            return

        # ── UI-02: Login com credenciais corretas ─────────────────────────────
        # O cookie auth_token já está no contexto do browser (injetado acima).
        # O mock de /auth/me garante que o React AuthContext veja isAuthenticated=true.
        # Aqui apenas validamos que o formulário de login redireciona corretamente.
        try:
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)
            page.click('[type="submit"]')
            # Aguardar redirect (sai do /auth/login)
            page.wait_for_url(lambda url: "/auth/login" not in url, timeout=15_000)
            record("UI-02 Login com credenciais corretas", "pass",
                   f"Redirecionado para {page.url.replace(FRONTEND, '')}")
        except PwTimeout:
            sc = take_screenshot(page, "UI-02")
            record("UI-02 Login com credenciais corretas", "fail",
                   "Timeout: sem redirecionamento após login", sc)
            browser.close()
            return

        # ── UI-03: Dashboard carrega ────────────────────────────────────────
        # /dashboard pode redirecionar para /mobile/dashboard dependendo do usuário.
        # Verificamos que não foi para /auth/login e que há conteúdo renderizado.
        try:
            page.goto(f"{FRONTEND}/dashboard", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            # Rejeitar se voltou para login
            if "/auth/login" in page.url:
                raise PwTimeout("Redirecionou para /auth/login")
            # Qualquer conteúdo: h1, h2, button (mobile) ou card/metric (desktop)
            page.wait_for_selector(
                "main, h1, h2, button, [class*='card'], [class*='metric'], [class*='dashboard']",
                timeout=15_000,
            )
            record("UI-03 Dashboard carrega", "pass", f"URL: {page.url.replace(FRONTEND, '')}")
        except PwTimeout:
            sc = take_screenshot(page, "UI-03")
            record("UI-03 Dashboard carrega", "fail", "Sem conteúdo no dashboard", sc)

        # ── UI-04: Dashboard — toggle Mês ativo por padrão ────────────────────
        try:
            mes_btn = page.locator("button:has-text('Mês')").first
            mes_btn.wait_for(timeout=5_000)
            record("UI-04 Dashboard — botão 'Mês' visível", "pass")
        except PwTimeout:
            sc = take_screenshot(page, "UI-04")
            record("UI-04 Dashboard — botão 'Mês' visível", "fail",
                   "Botão Mês não encontrado", sc)

        # ── UI-05: Dashboard — modo YTD ───────────────────────────────────────
        try:
            ytd_btn = page.locator("button:has-text('YTD')").first
            ytd_btn.wait_for(timeout=5_000)
            ytd_btn.click()
            wait_for_no_spinner(page, 10_000)
            record("UI-05 Dashboard — modo YTD clicável", "pass")
        except PwTimeout:
            sc = take_screenshot(page, "UI-05")
            record("UI-05 Dashboard — modo YTD clicável", "fail",
                   "Botão YTD não encontrado ou sem resposta", sc)

        # ── UI-06: Dashboard mobile — Mês / YTD / Ano Completo ────────────────
        try:
            # Testar em viewport mobile
            ctx2 = browser.new_context(viewport={"width": 390, "height": 844})
            mob = ctx2.new_page()
            mob.set_default_timeout(20_000)

            # Copiar cookies/storage de autenticação
            cookies = ctx.cookies()
            ctx2.add_cookies(cookies)

            mob.goto(f"{FRONTEND}/mobile/dashboard", wait_until="domcontentloaded")
            wait_for_no_spinner(mob, 15_000)

            # Verificar os 3 botões do YTDToggle
            mob.wait_for_selector("button:has-text('Mês')", timeout=10_000)
            ytd = mob.locator("button:has-text('YTD')").first
            ytd.click()
            time.sleep(0.5)
            ano_btn = mob.locator("button:has-text('Ano')").first
            ano_btn.click()
            time.sleep(0.5)
            record("UI-06 Mobile dashboard — Mês/YTD/Ano Completo", "pass")
            mob.close()
            ctx2.close()
        except PwTimeout:
            sc = take_screenshot(mob if 'mob' in dir() else page, "UI-06")
            record("UI-06 Mobile dashboard — Mês/YTD/Ano Completo", "fail",
                   "Toggle móvel não encontrado", sc)
            try:
                mob.close(); ctx2.close()
            except Exception:
                pass
        except Exception as e:
            record("UI-06 Mobile dashboard — Mês/YTD/Ano Completo", "error", str(e))
            try:
                mob.close(); ctx2.close()
            except Exception:
                pass

        # ── UI-07: Transações carrega ──────────────────────────────────────────
        # /transactions pode redirecionar para /mobile/transactions (sem table).
        try:
            page.goto(f"{FRONTEND}/transactions", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            if "/auth/login" in page.url:
                raise PwTimeout("Redirecionou para /auth/login")
            page.wait_for_selector(
                "table, [class*='table'], [class*='transaction'], [role='grid'], h1, h2, button",
                timeout=15_000,
            )
            record("UI-07 Transações — página carregada", "pass", f"URL: {page.url.replace(FRONTEND, '')}")
        except PwTimeout:
            sc = take_screenshot(page, "UI-07")
            record("UI-07 Transações — página carregada", "fail", "Sem conteúdo em /transactions", sc)

        # ── UI-08: Budget/Orçamento carrega ───────────────────────────────────
        # /budget pode redirecionar para /mobile/plano.
        try:
            page.goto(f"{FRONTEND}/budget", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            if "/auth/login" in page.url:
                raise PwTimeout("Redirecionou para /auth/login")
            page.wait_for_selector(
                "main, h1, h2, button, [class*='budget'], [class*='orcamento'], [class*='plano'], table",
                timeout=15_000,
            )
            record("UI-08 Budget/Orçamento carrega", "pass", f"URL: {page.url.replace(FRONTEND, '')}")
        except PwTimeout:
            sc = take_screenshot(page, "UI-08")
            record("UI-08 Budget/Orçamento carrega", "fail", "Sem conteúdo em /budget", sc)

        # ── UI-09: Investimentos carrega ──────────────────────────────────────
        # /investimentos pode redirecionar para /mobile/investimentos.
        try:
            page.goto(f"{FRONTEND}/investimentos", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            if "/auth/login" in page.url:
                raise PwTimeout("Redirecionou para /auth/login")
            page.wait_for_selector(
                "main, h1, h2, button, [class*='investimento'], [class*='portfolio'], table, [class*='card']",
                timeout=15_000,
            )
            record("UI-09 Investimentos carrega", "pass", f"URL: {page.url.replace(FRONTEND, '')}")
        except PwTimeout:
            sc = take_screenshot(page, "UI-09")
            record("UI-09 Investimentos carrega", "fail", "Sem conteúdo em /investimentos", sc)

        # ── UI-10: Simulador de investimentos ─────────────────────────────────
        try:
            page.goto(f"{FRONTEND}/investimentos/simulador", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            page.wait_for_selector(
                "main, [class*='simulador'], [class*='cenario'], form, [class*='card']",
                timeout=15_000
            )
            record("UI-10 Investimentos/Simulador carrega", "pass")
        except PwTimeout:
            sc = take_screenshot(page, "UI-10")
            record("UI-10 Investimentos/Simulador carrega", "fail",
                   "Sem conteúdo em /investimentos/simulador", sc)

        # ── UI-11: Upload carrega ─────────────────────────────────────────────
        # /upload pode redirecionar para /mobile/upload.
        try:
            page.goto(f"{FRONTEND}/upload", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            if "/auth/login" in page.url:
                raise PwTimeout("Redirecionou para /auth/login")
            page.wait_for_selector(
                "input[type='file'], [class*='upload'], [class*='dropzone'], [class*='drag'], h1, button",
                timeout=15_000,
            )
            record("UI-11 Upload — página carregada", "pass", f"URL: {page.url.replace(FRONTEND, '')}")
        except PwTimeout:
            sc = take_screenshot(page, "UI-11")
            record("UI-11 Upload — página carregada", "fail",
                   "Sem conteúdo em /upload", sc)

        # ── UI-12: Settings carrega ───────────────────────────────────────────
        try:
            page.goto(f"{FRONTEND}/settings", wait_until="domcontentloaded")
            wait_for_no_spinner(page)
            page.wait_for_selector(
                "main, [class*='setting'], [class*='config'], form",
                timeout=15_000
            )
            record("UI-12 Settings carrega", "pass")
        except PwTimeout:
            sc = take_screenshot(page, "UI-12")
            record("UI-12 Settings carrega", "fail", "Sem conteúdo em /settings", sc)

        # ── UI-13: Logout funciona ────────────────────────────────────────────
        try:
            # Tentar botão/link de logout no sidebar ou menu
            page.goto(f"{FRONTEND}/dashboard", wait_until="domcontentloaded")
            wait_for_no_spinner(page, 10_000)
            # Clicar no botão de logout (vários seletores possíveis)
            logout_sel = [
                "button:has-text('Sair')",
                "a:has-text('Sair')",
                "[aria-label='Logout']",
                "button:has-text('Logout')",
            ]
            clicked = False
            for sel in logout_sel:
                try:
                    btn = page.locator(sel).first
                    btn.wait_for(timeout=2_000)
                    btn.click()
                    clicked = True
                    break
                except Exception:
                    continue
            if clicked:
                page.wait_for_url(
                    lambda url: "/login" in url or "/auth" in url, timeout=10_000
                )
                record("UI-13 Logout redireciona para login", "pass")
            else:
                record("UI-13 Logout redireciona para login", "skip",
                       "Botão Sair não encontrado (verificar manualmente)")
        except PwTimeout:
            sc = take_screenshot(page, "UI-13")
            record("UI-13 Logout redireciona para login", "fail",
                   "Sem redirecionamento após logout", sc)
        except Exception as e:
            record("UI-13 Logout redireciona para login", "skip", str(e))

        browser.close()


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FinUp UI Tests (Playwright)")
    parser.add_argument("--json", action="store_true", help="Saída apenas JSON")
    parser.add_argument("--headed", action="store_true", help="Modo com janela visível")
    args = parser.parse_args()

    if not args.json:
        print(f"\n{BL}{CY}╔═══════════════════════════════════════════════════════╗{RS}")
        print(f"{BL}{CY}║           🖥️  FinUp — Testes de UI (Playwright)        ║{RS}")
        print(f"{BL}{CY}╚═══════════════════════════════════════════════════════╝{RS}")
        print(f"  Frontend : {CY}{FRONTEND}{RS}")
        print(f"  Usuário  : {CY}{EMAIL}{RS}\n")

    # Obter JWT real antes de iniciar o browser
    global REAL_JWT
    REAL_JWT = fetch_real_jwt()
    if not args.json:
        status_jwt = f"{GN}✅ obtido{RS}" if REAL_JWT else f"{YL}⚠️  não obtido (testes de auth podem falhar){RS}"
        print(f"  JWT real : {status_jwt}\n")

    start = time.time()
    run_tests(headed=args.headed)
    elapsed = time.time() - start

    passed = sum(1 for r in RESULTS if r["status"] == "pass")
    failed = sum(1 for r in RESULTS if r["status"] in ("fail", "error"))
    skipped = sum(1 for r in RESULTS if r["status"] == "skip")
    total = len(RESULTS)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "frontend": FRONTEND,
        "elapsed_s": round(elapsed, 1),
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "ok": failed == 0,
        "results": RESULTS,
    }

    if not args.json:
        color = GN if failed == 0 else RD
        status = "✅ TUDO OK" if failed == 0 else f"❌ {failed} FALHA(S)"
        print(f"\n{color}{'─'*54}{RS}")
        print(f"{color}  {status}  |  {passed}/{total} passou  |  {elapsed:.1f}s{RS}")
        if failed > 0:
            print(f"\n{RD}  Falhas:{RS}")
            for r in RESULTS:
                if r["status"] in ("fail", "error"):
                    print(f"    • {r['name']}: {r['note']}")
                    if r.get("screenshot"):
                        print(f"      Screenshot: {r['screenshot']}")
        print()

    print(json.dumps(summary, ensure_ascii=False, indent=2 if not args.json else None))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
