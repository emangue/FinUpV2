#!/usr/bin/env python3
"""
predeploy.py — Checklist automatizado pré-deploy FinUp

Uso:
  ./deploy/scripts/predeploy.sh          (recomendado — usa venv automaticamente)
  python3 deploy/scripts/predeploy.py    (se venv já ativo)

Variáveis de ambiente opcionais:
  ADMIN_EMAIL      (padrão: admin@financas.com)
  ADMIN_PASSWORD   (obrigatório — não tem padrão por segurança)
  BACKEND_URL      (padrão: http://localhost:8000)
  FRONTEND_URL     (padrão: http://localhost:3000)
"""

import subprocess
import json
import sys
import os
import getpass
from datetime import datetime
from pathlib import Path

# ── Setup ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)

BACKEND  = os.environ.get("BACKEND_URL",  "http://localhost:8000")
FRONTEND = os.environ.get("FRONTEND_URL", "http://localhost:3000")
EMAIL    = os.environ.get("ADMIN_EMAIL",  "admin@financas.com")

# ── Cores ANSI ────────────────────────────────────────────────────────────────
GN = "\033[0;32m"; RD = "\033[0;31m"; YL = "\033[1;33m"
CY = "\033[0;36m"; BL = "\033[1m";    RS = "\033[0m"

# ── Estado global ─────────────────────────────────────────────────────────────
pass_count = 0
fail_count = 0
results: dict[str, tuple[str, str]] = {}   # key → (status, note)

# ── Helpers de log ────────────────────────────────────────────────────────────
def ok(msg: str, key: str = "", note: str = "") -> str:
    global pass_count
    pass_count += 1
    print(f"  {GN}✅ PASS{RS} · {msg}")
    if key:
        results[key] = ("pass", note or msg)
    return "pass"

def fail(msg: str, key: str = "", note: str = "") -> str:
    global fail_count
    fail_count += 1
    print(f"  {RD}❌ FAIL{RS} · {msg}")
    if key:
        results[key] = ("fail", note or msg)
    return "fail"

def warn(msg: str) -> None:
    print(f"  {YL}⚠️  WARN{RS} · {msg}")

def section(title: str) -> None:
    print(f"\n{BL}{title}{RS}")

def e(status: str) -> str:
    """Status string → emoji"""
    return {"pass": "✅", "fail": "❌", "skip": "⏭️"}.get(status, "⬜")

def r(key: str) -> str:
    return results.get(key, ("skip", ""))[0]

def n(key: str) -> str:
    return results.get(key, ("skip", ""))[1]

# ── Utilitários ───────────────────────────────────────────────────────────────
def run(cmd: str, timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""

def http_get(url: str, token: str = "") -> int:
    """Retorna HTTP status code"""
    headers = f'-H "Authorization: Bearer {token}"' if token else ""
    code = run(f'curl -s -o /dev/null -w "%{{http_code}}" {headers} "{url}"')
    try:
        return int(code)
    except Exception:
        return 0

def api_check(key: str, label: str, url: str, token: str = "") -> None:
    """Faz GET, registra resultado em results[key]"""
    code = http_get(url, token)
    note = f"HTTP {code}"
    if code == 200:
        ok(f"{label} → {code}", key, note)
    else:
        fail(f"{label} → {code}", key, note)

def db_check(key: str, table: str, min_rows: int = 0) -> None:
    """Conta rows de tabela no PostgreSQL Docker"""
    raw = run(
        f'docker exec finup_postgres_dev psql -U finup_user -d finup_db '
        f'-t -c "SELECT COUNT(*) FROM {table};" 2>/dev/null'
    )
    try:
        count = int(raw.strip())
    except Exception:
        fail(f"DB {table} → tabela não encontrada", key, "não encontrada")
        return

    note = f"{count} registros"
    if count >= min_rows:
        ok(f"DB {table} → {note}", key, note)
    else:
        fail(f"DB {table} → {note} (esperado ≥ {min_rows})", key, note)

def run_ui_tests() -> list[dict]:
    """Executa ui_tests.py via subprocess e retorna lista de resultados."""
    ui_script = PROJECT_ROOT / "deploy" / "validations" / "ui_tests.py"
    if not ui_script.exists():
        warn("ui_tests.py não encontrado — testes de UI pulados")
        return []

    python = sys.executable
    try:
        proc = subprocess.run(
            [python, str(ui_script), "--json"],
            capture_output=True, text=True, timeout=300,
            env={**os.environ, "ADMIN_PASSWORD": os.environ.get("ADMIN_PASSWORD", "")},
        )
        # A saída contém linhas de log E o JSON no final — pegar última linha JSON
        lines = [l for l in proc.stdout.strip().splitlines() if l.strip().startswith("{")]
        if lines:
            data = json.loads(lines[-1])
            return data.get("results", [])
        else:
            warn(f"ui_tests.py sem saída JSON válida: {proc.stderr[:120]}")
            return []
    except subprocess.TimeoutExpired:
        warn("ui_tests.py timeout após 5 min")
        return []
    except Exception as e:
        warn(f"Erro ao rodar ui_tests.py: {e}")
        return []

# ── Git metadata ──────────────────────────────────────────────────────────────
now         = datetime.now()
DATE        = now.strftime("%Y-%m-%d")
TIME        = now.strftime("%H:%M:%S")
YEAR        = str(now.year)
COMMIT      = run("git log --oneline -1 | awk '{print $1}'") or "unknown"
BRANCH      = run("git branch --show-current")               or "unknown"
COMMIT_MSG  = run("git log --format='%s' -1")                or ""
OUT = PROJECT_ROOT / "deploy" / "history" / \
      f"TEST_PRE_DEPLOY_{DATE}_{COMMIT}.md"

# ─────────────────────────────────────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{BL}{CY}╔═══════════════════════════════════════════════════════╗{RS}")
print(f"{BL}{CY}║          🚀 FinUp — Checklist Pré-Deploy               ║{RS}")
print(f"{BL}{CY}╚═══════════════════════════════════════════════════════╝{RS}")
print(f"  Branch : {BL}{BRANCH}{RS}")
print(f"  Commit : {BL}{COMMIT}{RS} — {COMMIT_MSG}")
print(f"  Data   : {BL}{DATE} {TIME}{RS}")
print(f"  Output : {CY}{OUT.relative_to(PROJECT_ROOT)}{RS}\n")

# ─────────────────────────────────────────────────────────────────────────────
# SENHA ADMIN (via env ou prompt seguro)
# ─────────────────────────────────────────────────────────────────────────────
PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
if not PASSWORD:
    try:
        PASSWORD = getpass.getpass(
            f"  🔐 Senha do admin ({EMAIL}): "
        )
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RD}Abortado.{RS}")
        sys.exit(1)
    if not PASSWORD:
        warn("Senha não fornecida — testes de autenticação serão pulados.")

# ─────────────────────────────────────────────────────────────────────────────
# B: BLOQUEANTES
# ─────────────────────────────────────────────────────────────────────────────
section("🔴 B — BLOQUEANTES")

# B1: Docker — usar docker inspect (mais confiável que parsear texto)
CONTAINERS = [
    "finup_backend_dev", "finup_frontend_app_dev", "finup_frontend_admin_dev",
    "finup_postgres_dev", "finup_redis_dev",
]
docker_bad = []
for c in CONTAINERS:
    state = run(f'docker inspect --format="{{{{.State.Status}}}}" {c} 2>/dev/null')
    if state.strip() != "running":
        docker_bad.append(c)

if not docker_bad:
    ok("Docker: 5/5 containers running", "B1", "5/5 running")
else:
    fail(f"Docker: DOWN → {' '.join(docker_bad)}", "B1", f"DOWN: {' '.join(docker_bad)}")

# B2: Health
health_raw = run(f'curl -s "{BACKEND}/api/health"')
if '"healthy"' in health_raw:
    ok(f"Health: OK — {health_raw}", "B2", health_raw)
else:
    fail(f"Health: falhou — {health_raw}", "B2", health_raw)

# B3: Login → JWT
TOKEN = ""
if PASSWORD:
    payload = json.dumps({"email": EMAIL, "password": PASSWORD})
    login_raw = run(
        f"curl -s -X POST \"{BACKEND}/api/v1/auth/login\" "
        f"-H \"Content-Type: application/json\" "
        f"-d '{payload}'"
    )
    try:
        d = json.loads(login_raw)
        TOKEN = d.get("access_token", "")
    except Exception:
        pass

    if TOKEN:
        ok("Login: JWT token obtido", "B3", "Token JWT obtido")
    else:
        detail = ""
        try:
            detail = json.loads(login_raw).get("detail", login_raw[:80])
        except Exception:
            detail = login_raw[:80]
        fail(f"Login: sem token — {detail}", "B3", str(detail))
else:
    results["B3"] = ("skip", "Senha não fornecida")
    warn("B3 — Login pulado (sem senha)")

# B4: Git status
dirty = run("git status --short | grep -v '^??'")
if not dirty:
    ok("Git: workspace limpo", "B4", "Sem uncommitted")
else:
    lines = dirty.split("\n")[:3]
    note  = "; ".join(lines)
    fail(f"Git: mudanças pendentes — {note}", "B4", note)

# ─────────────────────────────────────────────────────────────────────────────
# API: SMOKE TESTS
# ─────────────────────────────────────────────────────────────────────────────
section("🔌 API — Smoke Tests (automatizados)")

MONTH = now.strftime("%Y-%m")

api_tests = [
    ("A1",  "GET /api/health",                          f"{BACKEND}/api/health",                                      ""),
    ("A2",  "GET /api/v1/dashboard/last-month-with-data", f"{BACKEND}/api/v1/dashboard/last-month-with-data",          TOKEN),
    ("A3",  "GET /api/v1/dashboard/metrics",            f"{BACKEND}/api/v1/dashboard/metrics?mes_referencia={MONTH}", TOKEN),
    ("A4",  "GET /api/v1/budget",                       f"{BACKEND}/api/v1/budget?mes_referencia={MONTH}",            TOKEN),
    ("A5",  "GET /api/v1/investimentos",                f"{BACKEND}/api/v1/investimentos/",                           TOKEN),
    ("A6",  "GET /api/v1/investimentos/cenarios",       f"{BACKEND}/api/v1/investimentos/cenarios",                   TOKEN),
    ("A7",  "GET /api/v1/plano/perfil",                 f"{BACKEND}/api/v1/plano/perfil",                             TOKEN),
    ("A8",  "GET /api/v1/plano/cashflow",               f"{BACKEND}/api/v1/plano/cashflow?ano={YEAR}",                TOKEN),
    ("A9",  "GET /api/v1/upload/history",               f"{BACKEND}/api/v1/upload/history",                           TOKEN),
    ("A10", "GET /api/v1/grupos",                       f"{BACKEND}/api/v1/grupos/",                                  TOKEN),
    ("A11", "GET /docs",                                f"{BACKEND}/docs",                                            ""),
]

if not TOKEN:
    warn("Token ausente — endpoints autenticados serão marcados como ⏭️ pulados")
    for key, label, *_ in api_tests:
        if key not in ("A1", "A11"):
            results[key] = ("skip", "Sem token de autenticação")
    api_tests = [(k, l, u, t) for k, l, u, t in api_tests if k in ("A1", "A11")]

for key, label, url, token in api_tests:
    api_check(key, label, url, token)

# ─────────────────────────────────────────────────────────────────────────────
# DB: BANCO DE DADOS
# ─────────────────────────────────────────────────────────────────────────────
section("🗄️  DB — Banco de dados (automatizado)")

db_checks = [
    ("DB1", "journal_entries",           100),
    ("DB2", "investimentos_portfolio",     1),
    ("DB3", "investimentos_cenarios",      1),
    ("DB4", "plano_cashflow_mes",          1),
    ("DB5", "budget_planning",             0),
    ("DB6", "base_marcacoes",              1),
    ("DB7", "users",                       1),
]
for key, table, min_r in db_checks:
    db_check(key, table, min_r)

# ─────────────────────────────────────────────────────────────────────────────
# UI: TESTES DE INTERFACE (Playwright)
# ─────────────────────────────────────────────────────────────────────────────
section("🖥️  UI — Testes de Interface (Playwright)")
ui_raw = run_ui_tests()

# Mapear resultados para dicionário e contar
ui_pass = ui_fail = ui_skip = 0
ui_table_rows = ""
for item in ui_raw:
    st = item.get("status", "skip")
    nm = item.get("name", "?")
    nt = item.get("note", "")
    sc = item.get("screenshot", "")
    icon = {"pass": "✅", "fail": "❌", "skip": "⏭️", "error": "💥"}.get(st, "⬜")
    color = {"pass": GN, "fail": RD, "skip": YL, "error": RD}.get(st, RS)
    if st == "pass":
        ui_pass += 1
    elif st in ("fail", "error"):
        ui_fail += 1
        print(f"  {color}{icon} FAIL{RS} · {nm}" + (f"  ↳ {nt}" if nt else ""))
    else:
        ui_skip += 1
    sc_md = f" ([screenshot]({sc}))" if sc else ""
    ui_table_rows += f"| {nm} | {icon} | {nt}{sc_md} |\n"

if not ui_raw:
    ui_table_rows = "| — | ⏭️ | Testes de UI não executados |\n"
    warn("Nenhum resultado de UI (Playwright pode não estar instalado ou frontend offline)")
else:
    total_ui = ui_pass + ui_fail + ui_skip
    status_ui = f"{GN}✅ {ui_pass}/{total_ui}{RS}" if ui_fail == 0 else f"{RD}❌ {ui_fail} falha(s){RS}"
    print(f"  Resultado UI: {status_ui}")

# ─────────────────────────────────────────────────────────────────────────────
# GERAR ARQUIVO MARKDOWN
# ─────────────────────────────────────────────────────────────────────────────
section("📝 Gerando arquivo de checklist...")

OUT.parent.mkdir(parents=True, exist_ok=True)

# Sumário automatizado para o cabeçalho
auto_pass = sum(1 for v in results.values() if v[0] == "pass")
auto_fail = sum(1 for v in results.values() if v[0] == "fail")
auto_skip = sum(1 for v in results.values() if v[0] == "skip")
auto_total = auto_pass + auto_fail
bloqueante_ok = all(r(k) == "pass" for k in ["B1", "B2", "B3", "B4"])
auto_status = "✅ OK — prosseguir com testes manuais" if bloqueante_ok else "❌ BLOQUEANTES com falha — verificar antes de continuar"

# Sumário de UI para o cabeçalho
ui_status_str = (
    f"✅ {ui_pass}/{ui_pass + ui_fail + ui_skip}" if ui_fail == 0 and ui_raw
    else f"❌ {ui_fail} falha(s)" if ui_fail > 0
    else "⏭️ não executado"
)

md = f"""# ✅ Checklist Pré-Deploy — FinUp

> **Gerado automaticamente por** `./deploy/scripts/predeploy.sh` em {DATE} {TIME}
> Legenda: ✅ Passou (auto) | ❌ Falhou (auto) | ⬜ Requer teste manual | ⏭️ Pulado

---

## 📋 Cabeçalho do Teste

| Campo                | Valor                                                         |
|----------------------|---------------------------------------------------------------|
| **Data**             | {DATE}                                                        |
| **Branch**           | `{BRANCH}`                                                    |
| **Commit (HEAD)**    | `{COMMIT}`                                                    |
| **Descrição commit** | {COMMIT_MSG}                                                  |
| **Testador(a)**      | _____________                                                 |
| **Ambiente**         | Local Docker (dev)                                            |
| **Backend URL**      | {BACKEND}                                                     |
| **Frontend URL**     | {FRONTEND}                                                    |
| **Gerado em**        | {DATE} {TIME}                                                 |
| **Auto: pass/fail**  | {auto_pass} ✅ / {auto_fail} ❌ / {auto_skip} ⏭️ de {auto_total} testes |
| **UI (Playwright)**  | {ui_status_str}                                               |
| **Status auto**      | {auto_status}                                                 |
| **Resultado Geral**  | ⬜ APROVADO / ⬜ REPROVADO ← *preencher ao final dos testes manuais* |

---

## 🔴 BLOQUEANTES (automatizados)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| B1 | Docker: todos os 5 containers `Up` | {e(r("B1"))} | {n("B1")} |
| B2 | `GET /api/health` retorna `{{"status":"healthy"}}` | {e(r("B2"))} | {n("B2")} |
| B3 | Login `{EMAIL}` retorna JWT token | {e(r("B3"))} | {n("B3")} |
| B4 | `git status` limpo (sem uncommitted) | {e(r("B4"))} | {n("B4")} |
| B5 | Nenhum erro 500 no console do navegador após login | ⬜ | *Manual* |

---

## 🖥️ UI — Testes de Interface (Playwright — automatizados)

| Teste | Resultado | Observação |
|-------|-----------|------------|
{ui_table_rows}
---

## 1. 🔑 AUTENTICAÇÃO (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 1.1 | Tela de login exibe logo, campos e botão | ⬜ | |
| 1.2 | Login com credenciais inválidas exibe mensagem de erro | ⬜ | |
| 1.3 | Login com credenciais válidas redireciona para dashboard | ⬜ | |
| 1.4 | Logout encerra sessão e redireciona para `/login` | ⬜ | |
| 1.5 | Acesso direto a rota protegida sem login → redireciona | ⬜ | |

---

## 2. 📊 DASHBOARD (manual)

### 2a. Modo MÊS

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2a.1 | Seletor exibe mês atual como padrão | ⬜ | |
| 2a.2 | Cards Receitas / Despesas / Saldo carregam | ⬜ | |
| 2a.3 | Gráfico de categorias exibe | ⬜ | |
| 2a.4 | Widget Budget vs Realizado exibe | ⬜ | |
| 2a.5 | Troca de mês atualiza todos os cards | ⬜ | |

### 2b. Modo YTD

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2b.1 | Seletor muda para YTD | ⬜ | |
| 2b.2 | Valores acumulam Jan → mês atual | ⬜ | |
| 2b.3 | Gráficos atualizam para visão acumulada | ⬜ | |

### 2c. Modo ANO COMPLETO

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2c.1 | Seletor muda para Ano Completo | ⬜ | |
| 2c.2 | Soma cobre 12 meses do ano | ⬜ | |
| 2c.3 | Troca de ano (2025 ↔ 2026) atualiza dados | ⬜ | |

---

## 3. 💸 TRANSAÇÕES (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 3.1 | Lista carrega com paginação | ⬜ | |
| 3.2 | Filtro por mês/período funciona | ⬜ | |
| 3.3 | Filtro por grupo/categoria funciona | ⬜ | |
| 3.4 | Filtro por texto (estabelecimento) funciona | ⬜ | |
| 3.5 | Edição: alterar Grupo e Subgrupo salva | ⬜ | |
| 3.6 | Edição: alterar valor salva | ⬜ | |
| 3.7 | Marcar IgnorarDashboard funciona | ⬜ | |
| 3.8 | Exclusão lógica funciona | ⬜ | |
| 3.9 | Somatório dos valores filtrados exibe | ⬜ | |

---

## 4. 💰 ORÇAMENTO / BUDGET (manual)

| # | Tela / Ação | Resultado | Observação |
|---|-------------|-----------|------------|
| 4a.1 | `/budget` — cards com grupos e valores | ⬜ | |
| 4b.1 | `/budget/simples` — barras de progresso | ⬜ | |
| 4c.1 | `/budget/detalhada` — drill-down em subgrupos | ⬜ | |
| 4d.1 | `/budget/planning` — metas mensais carregam | ⬜ | |
| 4d.2 | Edição de meta mensal salva | ⬜ | |
| 4d.3 | Copiar mês anterior funciona | ⬜ | |
| 4e.1 | `/budget/configuracoes` — salva | ⬜ | |

---

## 5. 📅 HISTÓRICO (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 5.1 | `/history` carrega gráfico de evolução | ⬜ | |
| 5.2 | Troca de grupo/categoria atualiza gráfico | ⬜ | |
| 5.3 | Comparativo entre anos funciona | ⬜ | |

---

## 6. 🏦 INVESTIMENTOS / PATRIMÔNIO (manual)

### 6a. Portfólio

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6a.1 | Lista de investimentos carrega | ⬜ | |
| 6a.2 | Valor total e distribuição por tipo exibem | ⬜ | |
| 6a.3 | Adicionar / editar investimento funciona | ⬜ | |

### 6b. Cenários — Construção

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6b.1 | "Novo Cenário" abre form | ⬜ | |
| 6b.2 | Campos base (nome, patrimônio, rendimento, aporte, período) salvam | ⬜ | |
| 6b.3 | Campos aposentadoria (idades, renda alvo) salvam | ⬜ | |
| 6b.4 | Cenário aparece na lista e gráfico exibe | ⬜ | |

### 6c. Cenários — Ajuste fino

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6c.1 | Editar cenário carrega valores atuais | ⬜ | |
| 6c.2 | Alterar aporte re-calcula projeção | ⬜ | |
| 6c.3 | Adicionar aporte extraordinário funciona | ⬜ | |
| 6c.4 | Deletar cenário funciona | ⬜ | |

### 6d. Simulador `/investimentos/simulador`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6d.1 | Tela carrega | ⬜ | |
| 6d.2 | Parâmetros atualizam resultado e gráfico | ⬜ | |

---

## 7. 📋 PLANO FINANCEIRO (manual)

### 7a-b. Wizard e Visualização

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7a.1 | Wizard abre se perfil incompleto | ⬜ | |
| 7a.2 | Steps 1–4 do wizard salvam | ⬜ | |
| 7b.1 | Card Resumo do Plano exibe | ⬜ | |
| 7b.2 | ProjecaoChart exibe curva de crescimento | ⬜ | |
| 7b.3 | TabelaReciboAnual exibe | ⬜ | |

### 7c. Ajuste do Plano

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7c.1 | Form de ajuste abre | ⬜ | |
| 7c.2 | Alterar renda re-calcula cashflow | ⬜ | |
| 7c.3 | Alterar aporte planejado re-calcula | ⬜ | |
| 7c.4 | Crescimento de renda/gastos salvam | ⬜ | |

### 7d. Base Cashflow `plano_cashflow_mes` (automatizado)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7d.1 | Tabela existe no banco | {e(r("DB4"))} | {n("DB4")} |
| 7d.2 | `GET /api/v1/plano/cashflow?ano={YEAR}` → 200 | {e(r("A8"))} | {n("A8")} |
| 7d.3 | Após upload, cashflow re-calcula no próximo request | ⬜ | *Manual* |
| 7d.4 | Meses passados usam `use_realizado=true` | ⬜ | *Manual* |

---

## 8. 📤 UPLOAD DE ARQUIVOS (manual)

> Critério: sem erro 500, preview correto, importação OK, duplicatas detectadas

| # | Banco / Formato | Resultado | Observação |
|---|-----------------|-----------|------------|
| 8a | Itaú — Fatura CSV | ⬜ | |
| 8b | Itaú — Extrato Excel | ⬜ | |
| 8c | Itaú — Extrato PDF | ⬜ | |
| 8d | Itaú — Fatura PDF | ⬜ | |
| 8e | BTG — Extrato Excel | ⬜ | |
| 8f | BTG — Fatura Excel | ⬜ | |
| 8g | BTG — Fatura PDF | ⬜ | |
| 8h | Mercado Pago — Extrato Excel | ⬜ | |
| 8i | Mercado Pago — Extrato PDF | ⬜ | |
| 8j | Mercado Pago — Fatura PDF | ⬜ | |
| 8k | Planilha Genérica | ⬜ | |
| 8l.1 | Arquivo inválido → erro amigável (não 500) | ⬜ | |
| 8l.2 | Re-upload → aviso de duplicata | ⬜ | |
| 8l.3 | Histórico de uploads exibe arquivos enviados | ⬜ | |

---

## 9. ⚙️ CONFIGURAÇÕES (manual)

| # | Tela | Resultado | Observação |
|---|------|-----------|------------|
| 9a | `/settings/profile` — salva alterações | ⬜ | |
| 9b | `/settings/bancos` — CRUD funciona | ⬜ | |
| 9c | `/settings/cartoes` — CRUD funciona | ⬜ | |
| 9d | `/settings/grupos` — CRUD + aparece em filtros | ⬜ | |
| 9e | `/settings/marcacoes` — CRUD funciona | ⬜ | |
| 9f | `/settings/categorias` — CRUD funciona | ⬜ | |
| 9g | `/settings/categorias-genericas` — CRUD funciona | ⬜ | |
| 9h | `/settings/exclusoes` — restaurar funciona | ⬜ | |
| 9i | `/settings/screens` — toggle ativa/desativa telas | ⬜ | |
| 9j | `/settings/backup` — download funciona | ⬜ | |

---

## 10. 📱 MOBILE (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 10.1 | Layout responsivo 375px (DevTools) | ⬜ | |
| 10.2 | Menu hamburguer abre/fecha | ⬜ | |
| 10.3 | Dashboard mobile exibe cards | ⬜ | |

---

## 11. 🧑‍💼 ADMIN — porta 3001 (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 11.1 | http://localhost:3001 abre | ⬜ | |
| 11.2 | Lista de usuários carrega | ⬜ | |
| 11.3 | Não-admin recebe 403 em rotas admin | ⬜ | |

---

## 12. 🔌 API — Smoke Tests (automatizados)

| # | Endpoint | Resultado | Observação |
|---|----------|-----------|------------|
| 12.1  | `GET /api/health`                           | {e(r("A1"))}  | {n("A1")}  |
| 12.2  | `GET /api/v1/dashboard/last-month-with-data`| {e(r("A2"))}  | {n("A2")}  |
| 12.3  | `GET /api/v1/dashboard/metrics`             | {e(r("A3"))}  | {n("A3")}  |
| 12.4  | `GET /api/v1/budget`                        | {e(r("A4"))}  | {n("A4")}  |
| 12.5  | `GET /api/v1/investimentos/`                | {e(r("A5"))}  | {n("A5")}  |
| 12.6  | `GET /api/v1/investimentos/cenarios`        | {e(r("A6"))}  | {n("A6")}  |
| 12.7  | `GET /api/v1/plano/perfil`                  | {e(r("A7"))}  | {n("A7")}  |
| 12.8  | `GET /api/v1/plano/cashflow?ano={YEAR}`     | {e(r("A8"))}  | {n("A8")}  |
| 12.9  | `GET /api/v1/upload/history`                | {e(r("A9"))}  | {n("A9")}  |
| 12.10 | `GET /api/v1/grupos/`                       | {e(r("A10"))} | {n("A10")} |
| 12.11 | `GET /docs` (Swagger UI)                    | {e(r("A11"))} | {n("A11")} |

---

## 🗄️ Banco de Dados (automatizado)

| Tabela | Status | Registros |
|--------|--------|-----------|
| `journal_entries`          | {e(r("DB1"))} | {n("DB1")} |
| `investimentos_portfolio`  | {e(r("DB2"))} | {n("DB2")} |
| `investimentos_cenarios`   | {e(r("DB3"))} | {n("DB3")} |
| `plano_cashflow_mes`       | {e(r("DB4"))} | {n("DB4")} |
| `budget_planning`          | {e(r("DB5"))} | {n("DB5")} |
| `base_marcacoes`           | {e(r("DB6"))} | {n("DB6")} |
| `users`                    | {e(r("DB7"))} | {n("DB7")} |

---

## 13. 🚀 PÓS-APROVAÇÃO — Deploy (preencher ao executar)

| # | Ação | Resultado | Observação |
|---|------|-----------|------------|
| 13.1 | `git push origin {BRANCH}` concluído | ⬜ | |
| 13.2 | `./deploy/scripts/deploy_docker_build_local.sh` executado | ⬜ | |
| 13.3 | Health produção: `curl https://meufinup.com.br/api/health` | ⬜ | |
| 13.4 | Login em produção funciona | ⬜ | |
| 13.5 | Dashboard em produção carrega sem erros | ⬜ | |

---

## 📝 Observações Gerais

```
[Escreva aqui qualquer nota durante ou após os testes manuais]
```

---

## 🐛 Bugs Encontrados

| ID | Descrição | Severidade | Status | Fix commit |
|----|-----------|-----------|--------|------------|
|    |           |           |        |            |

---

*FinUp · Gerado por `predeploy.sh` · Branch: {BRANCH} · Commit: {COMMIT} · {DATE} {TIME}*
"""

OUT.write_text(md, encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# SUMÁRIO FINAL
# ─────────────────────────────────────────────────────────────────────────────
total_auto = pass_count + fail_count
pct = round(pass_count / total_auto * 100) if total_auto else 0

print(f"\n{BL}{'═' * 56}{RS}")
print(f"{BL}  📊 RESULTADO AUTOMATIZADO{RS}")
print(f"{'═' * 56}")
print(f"  Passaram : {GN}{pass_count}{RS} / {total_auto}  ({pct}%)")
print(f"  Falharam : {RD}{fail_count}{RS}")
print(f"  Pulados  : {YL}{auto_skip}{RS}")
print(f"{'─' * 56}")

if fail_count == 0:
    print(f"  {GN}{BL}✅ TODOS OS TESTES AUTOMATIZADOS PASSARAM!{RS}")
    print(f"  {YL}👉 Prossiga com os testes manuais no arquivo abaixo.{RS}")
else:
    print(f"  {RD}{BL}❌ {fail_count} TESTE(S) FALHARAM — verificar antes do deploy!{RS}")

print(f"{'═' * 56}")
print(f"\n  📄 {CY}{OUT.relative_to(PROJECT_ROOT)}{RS}\n")
print(f"  Próximo passo: abra o arquivo, faça os testes manuais (⬜)")
print(f"  e preencha 'Resultado Geral' ao finalizar.\n")
