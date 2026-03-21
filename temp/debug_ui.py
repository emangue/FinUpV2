"""Debug script para identificar por que UI-03,07,08,09,11 falham."""
import json, os, urllib.request
from pathlib import Path

# Carregar .env.local
ENV = Path(__file__).parent.parent / ".env.local"
for line in ENV.read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

EMAIL = os.environ.get("ADMIN_EMAIL", "admin@financas.com")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Obter JWT real
req = urllib.request.Request(
    "http://localhost:8000/api/v1/auth/login",
    data=json.dumps({"email": EMAIL, "password": PASSWORD}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=10) as r:
    REAL_JWT = json.loads(r.read())["access_token"]
print(f"JWT: {REAL_JWT[:30]}...\n")

from playwright.sync_api import sync_playwright

CHECKS = ["/dashboard", "/transactions", "/budget", "/investimentos", "/upload"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_cookies([
        {"name": "auth_token", "value": REAL_JWT, "domain": "localhost", "path": "/"},
    ])
    page = ctx.new_page()
    page.set_default_timeout(15000)

    # Mock /auth/me
    page.route("**/api/v1/auth/me", lambda r: r.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps({"id": 1, "email": EMAIL, "name": "Admin", "role": "admin"}),
    ))

    errors = []
    page.on("response", lambda r: errors.append(f"  {r.status} {r.url}") if r.status >= 400 else None)
    page.on("console", lambda m: print(f"  [console.error] {m.text}") if m.type == "error" else None)

    SELECTORS = [
        "main",
        "[class*='card']",
        "[class*='dashboard']",
        "table",
        "h1", "h2",
        "[class*='upload']",
        "input[type='file']",
        "[class*='budget']",
        "[class*='transaction']",
        "[class*='investimento']",
        "button",
    ]

    for url_path in CHECKS:
        errors.clear()
        page.goto(f"http://localhost:3000{url_path}", wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        current = page.url.replace("http://localhost:3000", "")
        print(f"=== {url_path} → atual: {current} ===")
        if errors:
            print("  Erros HTTP:")
            for e in errors[:8]:
                print(e)
        found = []
        for sel in SELECTORS:
            try:
                page.locator(sel).first.wait_for(timeout=300)
                found.append(sel)
            except Exception:
                pass
        if found:
            print(f"  ✅ Seletores encontrados: {', '.join(found)}")
        else:
            print("  ❌ Nenhum seletor encontrado!")
        print()

    browser.close()
