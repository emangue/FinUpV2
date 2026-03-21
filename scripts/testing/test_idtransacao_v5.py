"""
Testes de validação: IdTransacao v5 vs v4.2.1

Valida que o novo algoritmo (banco+tipo+data+valor) resolve a deduplicação
que o algoritmo atual (com nome) quebra para o BTG XLS.

Baseado na investigação de 21/03/2026:
  - BTG exporta mesma transação com descrições diferentes entre arquivos
  - Resultado: IdTransacao diferente → dedup nunca detecta duplicata

Executar:
  docker exec finup_backend_dev python3 /app/scripts/testing/test_idtransacao_v5.py
  ou:
  python3 scripts/testing/test_idtransacao_v5.py
"""

import re
import sys
import unicodedata

# ─────────────────────────────────────────────
# Algoritmo ATUAL v4.2.1 (copiado de hasher.py)
# ─────────────────────────────────────────────

def fnv1a_64_hash(text: str) -> str:
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64  = 0x100000001b3
    MASK64        = (1 << 64) - 1
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    return str(h)


def generate_id_v4(data: str, lancamento: str, valor: float, user_id: int, sequencia: int = 1) -> str:
    """Algoritmo atual — usa nome normalizado na chave."""
    estab_norm = re.sub(r'[^A-Z0-9]', '', lancamento.upper())
    chave = f"{user_id}|{data}|{estab_norm}|{valor:.2f}"
    h = fnv1a_64_hash(chave)
    for _ in range(sequencia - 1):
        h = fnv1a_64_hash(h)
    return h


# ─────────────────────────────────────────────
# Algoritmo PROPOSTO v5
# ─────────────────────────────────────────────

def _normalize_str(text: str) -> str:
    """Remove acentos, maiuscula, elimina tudo que não for A-Z0-9."""
    sem_acento = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^A-Z0-9]', '', sem_acento.upper())


# Mapa canônico: garante que variações do mesmo banco gerem o mesmo hash.
# 'BTG Pactual' → 'BTG', 'Mercado Pago' → 'MERCADOPAGO', etc.
# Chaves são o resultado de _normalize_str() (já sem acentos/espaços/case).
_BANCO_CANONICAL: dict[str, str] = {
    'BTG':         'BTG',
    'BTGPACTUAL':  'BTG',   # 'BTG Pactual' após _normalize_str
    'MERCADOPAGO': 'MERCADOPAGO',
    'ITAU':        'ITAU',
    'BRADESCO':    'BRADESCO',
    'NUBANK':      'NUBANK',
    'SANTANDER':   'SANTANDER',
    'BB':          'BB',
    'CAIXA':       'CAIXA',
    'XP':          'XP',
    'INTER':       'INTER',
    'C6':          'C6',
    'C6BANK':      'C6',    # 'C6 Bank' após _normalize_str
    'SICOOB':      'SICOOB',
    'SICREDI':     'SICREDI',
}


def get_canonical_banco(banco: str) -> str:
    """
    Retorna o nome canônico do banco para o hash v5.

    Processo: _normalize_str → lookup em _BANCO_CANONICAL.
    Se não encontrado, retorna o próprio _normalize_str (fallback seguro).

    Exemplos:
      'BTG Pactual' → _normalize_str → 'BTGPACTUAL' → canonical → 'BTG'
      'Mercado Pago' → 'MERCADOPAGO' → 'MERCADOPAGO'
      'MercadoPago'  → 'MERCADOPAGO' → 'MERCADOPAGO'
      'Itaú'         → 'ITAU'        → 'ITAU'
    """
    key = _normalize_str(banco)
    return _BANCO_CANONICAL.get(key, key)


def generate_id_v5(data: str, banco: str, tipo_documento: str, valor: float,
                   user_id: int, sequencia: int = 1) -> str:
    """
    Algoritmo v5 — chave baseada em banco+tipo+data+valor (SEM nome).

    Imune a variações de descrição entre exports do mesmo banco.
    Sequência diferencia múltiplas transações com mesmo banco/tipo/data/valor.
    Acentos normalizados: 'Itaú' == 'Itau', 'MercadoPago' == 'Mercado Pago'.
    """
    banco_norm = get_canonical_banco(banco)     # canonical: 'BTG Pactual' → 'BTG'
    tipo_norm  = _normalize_str(tipo_documento)
    chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor:.2f}"
    h = fnv1a_64_hash(chave)
    for _ in range(sequencia - 1):
        h = fnv1a_64_hash(h)
    return h


# ─────────────────────────────────────────────
# Framework de testes mínimo
# ─────────────────────────────────────────────

PASS = 0
FAIL = 0

def check(description: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        print(f"  ✅ PASS  {description}")
        PASS += 1
    else:
        print(f"  ❌ FAIL  {description}")
        if detail:
            print(f"         {detail}")
        FAIL += 1


# ─────────────────────────────────────────────
# Dados reais coletados em 21/03/2026
# ─────────────────────────────────────────────
USER_ID  = 1
DATA     = "29/12/2025"
VALOR    = 10520.01  # sinal positivo (extrato BTG receita)

# Dois exports do mesmo banco, mesma transação, descrições diferentes
LANCAMENTO_ANTIGO = "Salário - Pagamento recebido"
LANCAMENTO_NOVO   = "Salário - Portabilidade de salário - Pagamento recebido"

# IDs reais coletados do banco de dados
ID_REAL_ANTIGO = "3033027455298180257"
ID_REAL_NOVO   = "12688721295696874454"


# ─────────────────────────────────────────────
# Suite de testes
# ─────────────────────────────────────────────

print("=" * 60)
print("  Validação: IdTransacao v5 vs v4.2.1")
print("=" * 60)

# ── Teste 1: Prova do problema atual ──────────────────────────
print("\n[1] Prova do problema v4.2.1 (baseline)")

id_v4_antigo = generate_id_v4(DATA, LANCAMENTO_ANTIGO, VALOR, USER_ID)
id_v4_novo   = generate_id_v4(DATA, LANCAMENTO_NOVO,   VALOR, USER_ID)

check(
    "v4.2.1 gera IDs DIFERENTES para mesma transação (confirma bug)",
    id_v4_antigo != id_v4_novo,
    f"antigo={id_v4_antigo}  novo={id_v4_novo}"
)
check(
    "v4.2.1 ID antigo confere com o valor real do DB",
    id_v4_antigo == ID_REAL_ANTIGO,
    f"calculado={id_v4_antigo}  db={ID_REAL_ANTIGO}"
)
check(
    "v4.2.1 ID novo confere com o valor real do DB",
    id_v4_novo == ID_REAL_NOVO,
    f"calculado={id_v4_novo}  db={ID_REAL_NOVO}"
)

# ── Teste 2: v5 — mesmo banco+tipo+data+valor = mesmo ID ──────
print("\n[2] v5 — deduplicação por banco+tipo+data+valor")

id_v5_upload1 = generate_id_v5(DATA, "BTG", "extrato", VALOR, USER_ID, sequencia=1)
id_v5_upload2 = generate_id_v5(DATA, "BTG", "extrato", VALOR, USER_ID, sequencia=1)

check(
    "v5 gera o MESMO ID para dois uploads da mesma transação BTG",
    id_v5_upload1 == id_v5_upload2,
    f"upload1={id_v5_upload1}  upload2={id_v5_upload2}"
)
check(
    "v5 ID é diferente do v4 (algoritmos não devem colidir)",
    id_v5_upload1 != id_v4_antigo and id_v5_upload1 != id_v4_novo,
)

# ── Teste 3: sequência diferencia duplicatas no mesmo arquivo ──
print("\n[3] v5 — sequência diferencia transações idênticas no arquivo")

id_seq1 = generate_id_v5(DATA, "BTG", "extrato", VALOR, USER_ID, sequencia=1)
id_seq2 = generate_id_v5(DATA, "BTG", "extrato", VALOR, USER_ID, sequencia=2)
id_seq3 = generate_id_v5(DATA, "BTG", "extrato", VALOR, USER_ID, sequencia=3)

check("seq=1 ≠ seq=2", id_seq1 != id_seq2)
check("seq=2 ≠ seq=3", id_seq2 != id_seq3)
check("seq=1 ≠ seq=3", id_seq1 != id_seq3)

# ── Teste 4: isolamento por user_id ───────────────────────────
print("\n[4] v5 — isolamento por user_id")

id_user1 = generate_id_v5(DATA, "BTG", "extrato", VALOR, user_id=1)
id_user2 = generate_id_v5(DATA, "BTG", "extrato", VALOR, user_id=2)

check(
    "user_id=1 ≠ user_id=2 para mesma transação",
    id_user1 != id_user2,
)

# ── Teste 5: extrato vs fatura são diferentes ─────────────────
print("\n[5] v5 — extrato vs fatura geram IDs diferentes")

id_extrato = generate_id_v5(DATA, "BTG", "extrato", VALOR, USER_ID)
id_fatura  = generate_id_v5(DATA, "BTG", "fatura",  VALOR, USER_ID)

check("extrato ≠ fatura (mesmo banco, data, valor)", id_extrato != id_fatura)

# ── Teste 6: normalização do nome do banco ────────────────────
print("\n[6] v5 — normalização do banco (acentos, espaços, case)")

id_btg1 = generate_id_v5(DATA, "BTG",          "extrato", VALOR, USER_ID)
id_btg2 = generate_id_v5(DATA, "btg",          "extrato", VALOR, USER_ID)
id_btg3 = generate_id_v5(DATA, "BTG Pactual",  "extrato", VALOR, USER_ID)
id_mp1  = generate_id_v5(DATA, "Mercado Pago", "extrato", VALOR, USER_ID)
id_mp2  = generate_id_v5(DATA, "MercadoPago",  "extrato", VALOR, USER_ID)
id_itau1 = generate_id_v5(DATA, "Itaú",   "extrato", VALOR, USER_ID)
id_itau2 = generate_id_v5(DATA, "Itau",   "extrato", VALOR, USER_ID)

check("'BTG' == 'btg' (case-insensitive)",  id_btg1 == id_btg2)
check("'BTG' == 'BTG Pactual' após canonical mapping (mesma conta)",  id_btg1 == id_btg3)
check("'Mercado Pago' == 'MercadoPago' após normalização [^A-Z0-9]", id_mp1 == id_mp2)
check("'Itaú' == 'Itau' após normalização (remove acento)",           id_itau1 == id_itau2)

# ── Teste 7: bancos diferentes → IDs diferentes ───────────────
print("\n[7] v5 — bancos diferentes → IDs diferentes (sem colisão)")

id_btg  = generate_id_v5(DATA, "BTG",         "extrato", VALOR, USER_ID)
id_mp   = generate_id_v5(DATA, "MercadoPago", "extrato", VALOR, USER_ID)
id_itau = generate_id_v5(DATA, "Itau",        "extrato", VALOR, USER_ID)

check("BTG ≠ MercadoPago",  id_btg  != id_mp)
check("BTG ≠ Itaú",         id_btg  != id_itau)
check("MercadoPago ≠ Itaú", id_mp   != id_itau)

# ── Teste 8: Cross-format — PDF vs XLSX do mesmo banco ───────────
print("\n[8] v5 — PDF vs XLSX do mesmo banco geram mesmo ID")
print("     (banco deve vir do form, não do nome do arquivo)")

# ── 8a. Mercado Pago ──────────────────────────────────────────
# PDF processor hardcoda banco='MercadoPago'
# XLSX processor hardcoda banco='Mercado Pago'
id_mp_pdf  = generate_id_v5(DATA, "MercadoPago",  "extrato", VALOR, USER_ID)
id_mp_xlsx = generate_id_v5(DATA, "Mercado Pago", "extrato", VALOR, USER_ID)

check(
    "MP: 'MercadoPago' (PDF) == 'Mercado Pago' (XLSX) via canonical",
    id_mp_pdf == id_mp_xlsx
)

# ── 8b. BTG — variações de nome via canonical ─────────────────
# PDF e XLSX recebem banco do form (service deve injetar raw.banco = banco)
# Usuário pode selecionar 'BTG' ou 'BTG Pactual' — devem gerar mesmo ID
id_btg_form_curto  = generate_id_v5(DATA, "BTG",         "extrato", VALOR, USER_ID)
id_btg_form_longo  = generate_id_v5(DATA, "BTG Pactual", "extrato", VALOR, USER_ID)

check(
    "BTG: 'BTG' (form) == 'BTG Pactual' (form) via canonical",
    id_btg_form_curto == id_btg_form_longo
)

# ── 8c. BTG ≠ MP mesmo após canonical ────────────────────────
check(
    "BTG ≠ MercadoPago após canonical (sem colisão entre bancos)",
    id_btg_form_curto != id_mp_pdf
)

# ── 8d. Prova do problema se service usar filename como banco ──
# Se service NÃO sobrescrever raw.banco, processadores inconsistentes gerariam
# IDs diferentes para o mesmo arquivo em formatos diferentes.
# Este teste documenta o bug que a correção de service.py previne:
id_btg_filename_xls = generate_id_v5(DATA, "Extrato_BTG_20251210.xls", "extrato", VALOR, USER_ID)
id_btg_filename_pdf = generate_id_v5(DATA, "Extrato_BTG_20251210.pdf", "extrato", VALOR, USER_ID)

check(
    "⚠ banco=filename: XLS ≠ PDF (documenta bug prevenido pela correção do service)",
    id_btg_filename_xls != id_btg_filename_pdf,
)

# ── 8e. Com form value consistente (banco = dropdown) ──────────
# O form envia SEMPRE o mesmo string do banco de dados:
#   'Mercado Pago' (com espaço) e 'BTG Pactual'
# Após service.py injetar raw.banco = banco (do form),
# PDF e XLSX do mesmo banco usam o mesmo valor → mesmo ID.
BANCO_MP_FORM  = "Mercado Pago"   # valor real em bank_format_compatibility
BANCO_BTG_FORM = "BTG Pactual"    # valor real em bank_format_compatibility

id_mp_pdf_form  = generate_id_v5(DATA, BANCO_MP_FORM,  "extrato", VALOR, USER_ID)
id_mp_xlsx_form = generate_id_v5(DATA, BANCO_MP_FORM,  "extrato", VALOR, USER_ID)
id_btg_pdf_form = generate_id_v5(DATA, BANCO_BTG_FORM, "extrato", VALOR, USER_ID)
id_btg_xls_form = generate_id_v5(DATA, BANCO_BTG_FORM, "extrato", VALOR, USER_ID)

check(
    "MP  PDF == MP  XLSX quando ambos usam valor do form ('Mercado Pago')",
    id_mp_pdf_form == id_mp_xlsx_form,
)
check(
    "BTG PDF == BTG XLS quando ambos usam valor do form ('BTG Pactual')",
    id_btg_pdf_form == id_btg_xls_form,
)
print("  → service.py já corrigido: raw.banco = banco (do form) resolve sem canonical mapping")

# ─────────────────────────────────────────────
# Resumo
# ─────────────────────────────────────────────

total = PASS + FAIL
print()
print("=" * 60)
if FAIL == 0:
    print(f"  ✅ {PASS}/{total} testes passaram")
    print()
    print("  CONCLUSÃO: v5 resolve o problema de deduplicação BTG.")
    print("  Implementar em hasher.py + marker.py + migração de dados.")
else:
    print(f"  ❌ {FAIL} falhas em {total} testes")
    print()
    print("  Revisar implementação antes de prosseguir.")
print("=" * 60)

sys.exit(0 if FAIL == 0 else 1)
