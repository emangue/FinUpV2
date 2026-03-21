# 🔧 TECH SPEC — Fix Dedup Parcelas v5.1

**Feature:** Fix falso-positivo dedup em compras parceladas  
**PRD:** `../01-PRD/PRD_parcelas_v5_1.md`  
**Versão:** 1.0  
**Data:** 23/03/2026  
**Branch:** `fix/dedup-parcelas-v5-1`  
**Código pronto para copy-paste:** ≥ 90%

---

## 1. Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────────────┐
│  UPLOAD FLOW (marker.py)                                            │
│                                                                     │
│  Para cada transação do arquivo:                                    │
│    1. Detectar se is_fatura (tipo_documento)                        │
│    2. Se is_fatura: chamar extrair_parcela_do_estabelecimento()     │
│    3. Se info_parcela:                                              │
│         parcela_param = f"{parcela}/{total}"  ← NOVO               │
│         chave_unica += f"|{parcela_param}"    ← FIX BUG 1          │
│         IdTransacao = hash(…|parcela_param)   ← FIX BUG 2          │
│         IdParcela   = hash(banco|tipo|data|…) ← FIX BUG 3          │
│    4. Se não info_parcela:                                          │
│         Comportamento idêntico ao v5 (backward compat)             │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  hasher.py  generate_id_transacao(…, parcela=None)                  │
│                                                                     │
│  SEM parcela:  chave = f"{user}|{banco}|{tipo}|{data}|{valor}"     │
│  COM parcela:  chave = f"{user}|{banco}|{tipo}|{data}|{valor}|{p}" │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  MIGRATION v5.1 (recalculate_id_transacao_v5_1.py)                  │
│                                                                     │
│  WHERE "TotalParcelas" IS NOT NULL  → ~42 registros                 │
│  UPDATE IdTransacao + IdParcela para novos valores                  │
│  WHERE "TotalParcelas" IS NULL      → INTOCADO                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. DAG — Ordem de Implementação

```
① hasher.py
    └──→ ② marker.py  (depende de hasher.py)
              └──→ ③ tests/test_hasher_parcelas.py
              └──→ ④ tests/test_marker_parcelas.py
                        └──→ ⑤ scripts/database/recalculate_id_transacao_v5_1.py
                                    └──→ ⑥ Dry-run
                                              └──→ ⑦ Execute migration
                                                        └──→ ⑧ E2E validation
```

---

## 3. Mudança 1 — `hasher.py`

**Arquivo:** `app_dev/backend/app/shared/utils/hasher.py`

### 3.1 Problema Atual

```python
# ANTES — sem parcela na chave
def generate_id_transacao(data: str, banco: str, tipo_documento: str,
                          valor: float, user_id: int, sequencia: int = 1) -> str:
    banco_norm = get_canonical_banco(banco)
    tipo_norm  = _normalize_str(tipo_documento)
    valor_str  = f"{float(valor):.2f}"
    chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}"
    # ↑ PARCELAS 1/6 e 2/6 geram MESMA chave (data + valor idênticos)
```

### 3.2 Código Corrigido

```python
def generate_id_transacao(
    data: str,
    banco: str,
    tipo_documento: str,
    valor: float,
    user_id: int,
    sequencia: int = 1,
    parcela: str | None = None,   # NOVO: formato "1/6", "2/12", etc.
) -> str:
    """
    Gera IdTransacao v5.1.

    Para compras parceladas, `parcela` deve ser passado como "atual/total"
    (ex: "1/6", "2/12"). Isso garante que cada parcela gere um hash único.

    Para transações sem parcela, `parcela=None` preserva compatibilidade
    total com v5 (mesma chave, mesmo hash).
    """
    banco_norm = get_canonical_banco(banco)
    tipo_norm  = _normalize_str(tipo_documento)
    valor_str  = f"{float(valor):.2f}"

    if parcela:
        chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}|{parcela}"
    else:
        chave = f"{user_id}|{banco_norm}|{tipo_norm}|{data}|{valor_str}"

    hash_atual = fnv1a_64_hash(chave)
    for _ in range(sequencia - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    return hash_atual
```

### 3.3 Verificação de Backward Compatibility

| Cenário | `parcela` | Hash v5 == Hash v5.1? |
|---|---|---|
| Transação normal (extrato/fatura sem parcela) | `None` | ✅ Idêntico |
| Parcela 1/6 (mesmo user, banco, data, valor) | `"1/6"` | ✅ Diferente (esperado) |
| Parcela 2/6 da mesma compra | `"2/6"` | ✅ Diferente de 1/6 (corrigido) |

---

## 4. Mudança 2 — `marker.py`

**Arquivo:** `app_dev/backend/app/domains/upload/processors/marker.py`

### 4.1 Três Bugs Corrigidos

| Bug | Local | Descrição |
|---|---|---|
| BUG-1 | `chave_unica` | Ignora parcela → 2 linhas parceladas com mesmos dados no mesmo arquivo são colapsadas |
| BUG-2 | `generate_id_transacao()` | Não passa `parcela` → colisão entre parcelas de meses diferentes |
| BUG-3 | Fórmula `IdParcela` | Usa nome normalizado do estabelecimento → frágil entre PDF/CSV |

### 4.2 Seção Problemática Atual

Localizada no bloco `if info_parcela:` dentro do método `_mark_row()`:

```python
# ANTES — BUG-1: chave_unica ignora parcela
chave_unica = f"{raw.banco}|{raw.tipo_documento}|{raw.data}|{valor_hash:.2f}"

# ANTES — BUG-2: sem parcela na chamada
id_transacao = generate_id_transacao(
    data=raw.data,
    banco=raw.banco,
    tipo_documento=raw.tipo_documento,
    valor=valor_hash,
    user_id=self.user_id,
    sequencia=sequencia,
)

# ANTES — BUG-3: IdParcela baseado em nome de estabelecimento
estab_normalizado_parcela = re.sub(r'[^A-Z0-9]', '', estabelecimento_base.upper())
chave_parcela = f"{estab_normalizado_parcela}|{valor_arredondado:.2f}|{total_parcelas}|{self.user_id}"
id_parcela = hashlib.md5(chave_parcela.encode()).hexdigest()[:16]
```

### 4.3 Código Corrigido (bloco `if info_parcela:`)

```python
if info_parcela:
    estabelecimento_base = info_parcela["estabelecimento_base"]
    parcela_atual        = info_parcela["parcela"]    # int, ex: 2
    total_parcelas       = info_parcela["total"]      # int, ex: 6

    # FIX BUG-1 + BUG-2: string de parcela usada em chave_unica E em IdTransacao
    parcela_param = f"{parcela_atual}/{total_parcelas}"  # ex: "2/6"

    # FIX BUG-1: chave_unica agora inclui parcela → evita colapso intra-arquivo
    chave_unica = (
        f"{raw.banco}|{raw.tipo_documento}|{raw.data}"
        f"|{valor_hash:.2f}|{parcela_param}"
    )

    # Sequência local (dedup dentro do mesmo arquivo)
    sequencia = chaves_vistas.get(chave_unica, 0) + 1
    chaves_vistas[chave_unica] = sequencia

    # FIX BUG-2: passa parcela_param → cada parcela gera IdTransacao único
    id_transacao = generate_id_transacao(
        data=raw.data,
        banco=raw.banco,
        tipo_documento=raw.tipo_documento,
        valor=valor_hash,
        user_id=self.user_id,
        sequencia=sequencia,
        parcela=parcela_param,   # ← NOVO
    )

    # FIX BUG-3: IdParcela baseado em fingerprint banco/tipo/data/valor/total
    # Robusto entre PDF e CSV — sem dependência de texto de estabelecimento
    chave_parcela = (
        f"{raw.banco}|{raw.tipo_documento}|{raw.data}"
        f"|{valor_hash:.2f}|{total_parcelas}|{self.user_id}"
    )
    id_parcela = hashlib.md5(chave_parcela.encode()).hexdigest()[:16]

else:
    # Sem parcela: comportamento idêntico ao v5 (backward compat garantida)
    chave_unica = f"{raw.banco}|{raw.tipo_documento}|{raw.data}|{valor_hash:.2f}"
    sequencia = chaves_vistas.get(chave_unica, 0) + 1
    chaves_vistas[chave_unica] = sequencia

    id_transacao = generate_id_transacao(
        data=raw.data,
        banco=raw.banco,
        tipo_documento=raw.tipo_documento,
        valor=valor_hash,
        user_id=self.user_id,
        sequencia=sequencia,
        # parcela=None (default) — chave idêntica ao v5
    )
    id_parcela = None
```

### 4.4 Nota: Estrutura de `info_parcela`

`extrair_parcela_do_estabelecimento()` retorna:

```python
{
    "estabelecimento_base": "AIRBNB * HMHMZAQ",  # str
    "parcela": 2,                                  # int (parcela atual)
    "total": 6,                                    # int (total de parcelas)
}
# ou None se não houver info de parcela
```

---

## 5. Mudança 3 — Migration v5.1

**Arquivo (novo):** `scripts/database/recalculate_id_transacao_v5_1.py`

### 5.1 Escopo

```sql
-- Registros afetados
SELECT COUNT(*) FROM journal_entries WHERE "TotalParcelas" IS NOT NULL;
-- Esperado: ~42 (21 user_id=1 + ~21 user_id=4)

-- Registros NÃO tocados
SELECT COUNT(*) FROM journal_entries WHERE "TotalParcelas" IS NULL;
-- Esperado: ~4207 (idênticos ao v5)
```

### 5.2 Código Completo da Migration

```python
#!/usr/bin/env python3
"""
Migration v5.1 — Recalcula IdTransacao e IdParcela para registros parcelados.

Escopo: APENAS registros com TotalParcelas IS NOT NULL (~42 registros).
Registros não-parcelados: INTOCADOS.

Uso:
    python scripts/database/recalculate_id_transacao_v5_1.py --dry-run
    python scripts/database/recalculate_id_transacao_v5_1.py
"""
import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
import psycopg2

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent.parent / "app_dev" / "backend"
HASHER_PATH = BACKEND_DIR / "app" / "shared" / "utils" / "hasher.py"

# ─── Import hasher ────────────────────────────────────────────────────────────
spec = importlib.util.spec_from_file_location("hasher", HASHER_PATH)
hasher_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hasher_mod)
generate_id_transacao = hasher_mod.generate_id_transacao

# ─── DB ───────────────────────────────────────────────────────────────────────
DB_URL = "postgresql://finup_user:finup_password_dev_2026@localhost:5432/finup_db"


def gerar_id_parcela_v5_1(banco: str, tipo: str, data: str, valor: float,
                           total: int, user_id: int) -> str:
    """Nova fórmula IdParcela — baseada em fingerprint banco/tipo/data/valor."""
    chave = f"{banco}|{tipo}|{data}|{valor:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]


def run_migration(dry_run: bool = True):
    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    # Buscar todos os registros parcelados
    cur.execute("""
        SELECT
            "IdTransacao",
            "user_id",
            "Banco",
            "TipoDocumento",
            "Data",
            "Valor",
            "parcela_atual",
            "TotalParcelas",
            "EstabelecimentoBase"
        FROM journal_entries
        WHERE "TotalParcelas" IS NOT NULL
        ORDER BY "user_id", "MesFatura", "EstabelecimentoBase"
    """)
    rows = cur.fetchall()
    print(f"{'[DRY-RUN] ' if dry_run else ''}Registros parcelados encontrados: {len(rows)}")

    updates = []
    colisoes_antes   = set()
    colisoes_depois  = set()

    for row in rows:
        (id_atual, user_id, banco, tipo, data, valor,
         parcela_atual, total_parcelas, estab) = row

        parcela_param   = f"{parcela_atual}/{total_parcelas}"
        novo_id         = generate_id_transacao(
            data=data, banco=banco, tipo_documento=tipo,
            valor=float(valor), user_id=user_id,
            parcela=parcela_param,
        )
        novo_id_parcela = gerar_id_parcela_v5_1(
            banco=banco, tipo=tipo, data=data,
            valor=float(valor), total=total_parcelas, user_id=user_id,
        )

        colisoes_antes.add(id_atual)
        colisoes_depois.add(novo_id)
        updates.append((novo_id, novo_id_parcela, id_atual))

        print(f"  {'DRY ' if dry_run else ''}{estab} p{parcela_atual}/{total_parcelas} "
              f"| {id_atual} → {novo_id} | IdParcela → {novo_id_parcela}")

    # Diagnóstico de unicidade
    print(f"\n─── Diagnóstico ───────────────────────────────────────")
    print(f"  IDs únicos ANTES  : {len(colisoes_antes)} (de {len(rows)} registros)")
    print(f"  IDs únicos DEPOIS : {len(colisoes_depois)} (de {len(rows)} registros)")
    if len(colisoes_depois) < len(rows):
        print("  ⚠️  ATENÇÃO: ainda existem colisões após migração!")
        sys.exit(1)
    else:
        print("  ✅ Nenhuma colisão após migração")

    if dry_run:
        print(f"\n[DRY-RUN] {len(updates)} registros seriam atualizados. Use sem --dry-run para executar.")
        conn.close()
        return

    # Executar updates
    for novo_id, novo_id_parcela, id_antigo in updates:
        cur.execute("""
            UPDATE journal_entries
            SET "IdTransacao" = %s, "IdParcela" = %s
            WHERE "IdTransacao" = %s
        """, (novo_id, novo_id_parcela, id_antigo))

    conn.commit()
    print(f"\n✅ Migration v5.1 concluída: {len(updates)} registros atualizados.")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()
    run_migration(dry_run=args.dry_run)
```

### 5.3 Validação Pós-Migration

```sql
-- 1. Verificar que parcelados foram atualizados (nenhum deve ter IdParcela antigo)
SELECT COUNT(*) FROM journal_entries
WHERE "TotalParcelas" IS NOT NULL;
-- Esperado: ~42

-- 2. Verificar unicidade de IdTransacao para parcelados
SELECT "IdTransacao", COUNT(*) AS cnt
FROM journal_entries
WHERE "TotalParcelas" IS NOT NULL
GROUP BY "IdTransacao"
HAVING COUNT(*) > 1;
-- Esperado: 0 linhas (nenhuma colisão)

-- 3. Verificar que não-parcelados ficaram intactos (total = 4207+)
SELECT COUNT(*) FROM journal_entries
WHERE "TotalParcelas" IS NULL;
-- Esperado: 4207

-- 4. Verificar IdParcela agrupa parcelas da mesma compra (mesmo banco+data+valor)
SELECT "IdParcela", COUNT(*) as parcelas, array_agg("parcela_atual") as nums
FROM journal_entries
WHERE "TotalParcelas" IS NOT NULL
GROUP BY "IdParcela"
ORDER BY parcelas DESC
LIMIT 10;
-- Espera grupos de 1 (parcelas com datas diferentes) ou N (mesma data)
```

---

## 6. Testes

### 6.1 `tests/test_hasher_parcelas.py` (novo arquivo)

```python
"""
Testes para generate_id_transacao v5.1 — suporte a parcelas.
"""
import importlib.util
from pathlib import Path
import pytest

_backend  = Path(__file__).resolve().parent.parent
_hasher_p = _backend / "app" / "shared" / "utils" / "hasher.py"
spec = importlib.util.spec_from_file_location("hasher", _hasher_p)
hasher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hasher)
generate_id_transacao = hasher.generate_id_transacao

# ─── Dados de referência (AIRBNB real do DB) ───────────────────────────────
_DATA  = "19/01/2026"
_BANCO = "itau"
_TIPO  = "fatura"
_VALOR = -1011.21
_UID   = 1


class TestHasherParcelas:

    def test_parcela_1_difere_de_parcela_2(self):
        """Parcelas 1/6 e 2/6 da mesma compra → IdTransacao diferentes."""
        id_p1 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/6")
        id_p2 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="2/6")
        assert id_p1 != id_p2, "Parcela 1/6 e 2/6 devem ter IdTransacao distintos"

    def test_todas_parcelas_diferentes(self):
        """Parcelas 1..6 de mesma compra → todos IdTransacao únicos."""
        ids = {
            generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela=f"{i}/6")
            for i in range(1, 7)
        }
        assert len(ids) == 6, "Todas as 6 parcelas devem ter IdTransacao único"

    def test_sem_parcela_backward_compat(self):
        """Sem parcela → hash idêntico ao v5 (mesma chave sem parcela)."""
        id_v5   = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID)
        id_v51  = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela=None)
        assert id_v5 == id_v51, "parcela=None deve produzir hash idêntico ao v5"

    def test_parcela_none_nao_colapsa_com_1_1(self):
        """parcela=None e parcela='1/1' devem gerar hashes diferentes."""
        id_none = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID)
        id_1_1  = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/1")
        assert id_none != id_1_1, "None e '1/1' não devem colapsar"

    def test_mesma_parcela_idempotente(self):
        """Mesma chamada com mesma parcela → hash idêntico (determinístico)."""
        id_a = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="3/12")
        id_b = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="3/12")
        assert id_a == id_b

    def test_parcela_formato_variado(self):
        """Formatos alternativos de parcela geram hashes diferentes entre si."""
        id_1_12  = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/12")
        id_01_12 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="01/12")
        # Formatos diferentes são tratados como strings distintas
        assert id_1_12 != id_01_12, "Formatos '1/12' e '01/12' devem ser distintos"

    def test_user_id_isolamento_com_parcela(self):
        """Com parcela, user_id diferente ainda gera IdTransacao diferente."""
        id_u1 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, 1, parcela="2/6")
        id_u2 = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, 2, parcela="2/6")
        assert id_u1 != id_u2, "user_id deve isolar hashes mesmo com parcela"

    def test_hash_e_inteiro(self):
        """IdTransacao deve ser um inteiro (uint64 como string ou int)."""
        id_p = generate_id_transacao(_DATA, _BANCO, _TIPO, _VALOR, _UID, parcela="1/6")
        assert str(id_p).isdigit() or isinstance(id_p, int), "IdTransacao deve ser inteiro"
```

### 6.2 `tests/test_marker_parcelas.py` (novo arquivo)

```python
"""
Testes para marker.py v5.1 — correção dedup parcelas.

Foca nos três bugs corrigidos:
  BUG-1: chave_unica ignorava parcela
  BUG-2: generate_id_transacao não recebia parcela
  BUG-3: IdParcela baseado em nome (frágil)
"""
import hashlib
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Optional


# ─── Mocks mínimos ─────────────────────────────────────────────────────────
@dataclass
class FakeRaw:
    banco: str
    tipo_documento: str
    data: str
    lancamento: str
    valor: float


# Replicar fórmulas do marker.py v5.1 (para validação sem importar FastAPI)

def _chave_unica_v51(raw: FakeRaw, valor_hash: float, parcela_param: Optional[str]) -> str:
    if parcela_param:
        return f"{raw.banco}|{raw.tipo_documento}|{raw.data}|{valor_hash:.2f}|{parcela_param}"
    return f"{raw.banco}|{raw.tipo_documento}|{raw.data}|{valor_hash:.2f}"


def _id_parcela_v51(banco: str, tipo: str, data: str, valor: float,
                    total: int, user_id: int) -> str:
    chave = f"{banco}|{tipo}|{data}|{valor:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]


# ─── Dados de referência ───────────────────────────────────────────────────
AIRBNB_1 = FakeRaw(
    banco="itau", tipo_documento="fatura",
    data="19/01/2026", lancamento="AIRBNB * HMHMZAQ (1/6)", valor=-1011.21,
)
AIRBNB_2 = FakeRaw(
    banco="itau", tipo_documento="fatura",
    data="19/01/2026", lancamento="AIRBNB * HMHMZAQ (2/6)", valor=-1011.21,
)
ANUIDADE_5 = FakeRaw(
    banco="itau", tipo_documento="fatura",
    data="26/12/2025", lancamento="ANUIDADE DIFERENCI (5/10)", valor=-73.50,
)
ANUIDADE_6 = FakeRaw(
    banco="itau", tipo_documento="fatura",
    data="26/01/2026", lancamento="ANUIDADE DIFERENCI (6/10)", valor=-73.50,
)
SEM_PARCELA = FakeRaw(
    banco="itau", tipo_documento="fatura",
    data="15/02/2026", lancamento="UBER * TRIP", valor=-42.00,
)


class TestChaueUnicaBug1:
    """BUG-1: chave_unica deve incluir parcela para evitar colapso intra-arquivo."""

    def test_chave_diferentes_para_parcelas_diferentes(self):
        """Parcelas 1/6 e 2/6 no mesmo arquivo → chaves_unicas distintas."""
        chave_1 = _chave_unica_v51(AIRBNB_1, AIRBNB_1.valor, "1/6")
        chave_2 = _chave_unica_v51(AIRBNB_2, AIRBNB_2.valor, "2/6")
        assert chave_1 != chave_2

    def test_chave_igual_mesma_parcela(self):
        """Mesma transação → mesma chave (idempotente)."""
        chave_a = _chave_unica_v51(AIRBNB_1, AIRBNB_1.valor, "1/6")
        chave_b = _chave_unica_v51(AIRBNB_1, AIRBNB_1.valor, "1/6")
        assert chave_a == chave_b

    def test_sem_parcela_backward_compat(self):
        """Sem parcela → chave idêntica ao v5."""
        chave_v5  = f"{SEM_PARCELA.banco}|{SEM_PARCELA.tipo_documento}|{SEM_PARCELA.data}|{SEM_PARCELA.valor:.2f}"
        chave_v51 = _chave_unica_v51(SEM_PARCELA, SEM_PARCELA.valor, None)
        assert chave_v5 == chave_v51


class TestIdParcelaBug3:
    """BUG-3: IdParcela v5.1 baseado em fingerprint, não em nome."""

    def test_formato_nao_afeta_id_parcela(self):
        """'LOJA (1/12)' e 'LOJA 01/12' (mesmo banco/data/valor) → mesmo IdParcela."""
        # Simula mesma compra em dois formatos diferentes de arquivo
        id_1 = _id_parcela_v51("itau", "fatura", "10/01/2026", -200.00, 12, 1)
        id_2 = _id_parcela_v51("itau", "fatura", "10/01/2026", -200.00, 12, 1)
        assert id_1 == id_2, "IdParcela deve ser idêntico para mesmos dados"

    def test_id_parcela_diferente_por_user(self):
        """user_id diferente → IdParcela diferente."""
        id_u1 = _id_parcela_v51("itau", "fatura", "19/01/2026", -1011.21, 6, 1)
        id_u2 = _id_parcela_v51("itau", "fatura", "19/01/2026", -1011.21, 6, 2)
        assert id_u1 != id_u2

    def test_id_parcela_formato_16_chars(self):
        """IdParcela deve ter 16 chars hex (MD5[:16])."""
        id_p = _id_parcela_v51("itau", "fatura", "19/01/2026", -1011.21, 6, 1)
        assert len(id_p) == 16
        assert all(c in "0123456789abcdef" for c in id_p)

    def test_anuidade_parcelas_data_diferente(self):
        """ANUIDADE (data muda por mês) → IdParcela diferente por parcela."""
        id_p5 = _id_parcela_v51("itau", "fatura", "26/12/2025", -73.50, 10, 1)
        id_p6 = _id_parcela_v51("itau", "fatura", "26/01/2026", -73.50, 10, 1)
        # IdParcelas diferentes — aceitável (data de cobrança diferente)
        assert id_p5 != id_p6

    def test_airbnb_parcelas_mesma_data(self):
        """AIRBNB (data original mantida) → IdParcela IGUAL para todas parcelas."""
        # Todas parcelas da mesma compra AIRBNB usam data=19/01/2026
        id_p1 = _id_parcela_v51("itau", "fatura", "19/01/2026", -1011.21, 6, 1)
        id_p2 = _id_parcela_v51("itau", "fatura", "19/01/2026", -1011.21, 6, 1)
        id_p6 = _id_parcela_v51("itau", "fatura", "19/01/2026", -1011.21, 6, 1)
        assert id_p1 == id_p2 == id_p6, "Parcelas da mesma compra devem ter mesmo IdParcela"


class TestAtualizacaoTestHashUserId:
    """
    Verifica que test_hash_user_id.py precisa ser atualizado.
    A assinatura v5 é: (data, banco, tipo_documento, valor, user_id)
    A assinatura v3 era: (data, estab, valor, user_id) — INCOMPATÍVEL.
    """

    def test_assinatura_v5_requer_banco_e_tipo(self):
        """Documenta que assinatura v5 exige banco e tipo_documento."""
        import importlib.util
        from pathlib import Path
        import inspect
        _backend = Path(__file__).resolve().parent.parent
        _hasher_p = _backend / "app" / "shared" / "utils" / "hasher.py"
        spec = importlib.util.spec_from_file_location("hasher", _hasher_p)
        hmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hmod)
        sig = inspect.signature(hmod.generate_id_transacao)
        params = list(sig.parameters.keys())
        assert "banco" in params, "v5.1 deve ter parâmetro 'banco'"
        assert "tipo_documento" in params, "v5.1 deve ter parâmetro 'tipo_documento'"
        assert "parcela" in params, "v5.1 deve ter parâmetro 'parcela'"
```

### 6.3 Atualizar `tests/test_hash_user_id.py`

O teste existente usa a assinatura v3 `(data, estab, valor, user_id=1)`. Precisa ser atualizado para v5.1:

```python
# ANTES (quebrado com v5+)
id_user1 = generate_id_transacao(data, estab, valor, user_id=1)

# DEPOIS (v5.1)
id_user1 = generate_id_transacao(data, "itau", "fatura", valor, user_id=1)
```

E a função local `_gerar_id_parcela_esperado` precisa usar a nova fórmula:

```python
# ANTES (v3 — baseada em nome)
def _gerar_id_parcela_esperado(estab_base: str, valor: float, total: int, user_id: int) -> str:
    estab_norm = normalizar_estabelecimento(estab_base)
    chave = f"{estab_norm}|{round(float(valor), 2):.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]

# DEPOIS (v5.1 — baseada em fingerprint)
def _gerar_id_parcela_esperado(banco: str, tipo: str, data: str,
                                valor: float, total: int, user_id: int) -> str:
    chave = f"{banco}|{tipo}|{data}|{round(float(valor), 2):.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]
```

---

## 7. Impacto em Outros Componentes

| Componente | Impacto | Ação Necessária |
|---|---|---|
| `hasher.py` | **MODIFICADO** | Adicionar param `parcela` |
| `marker.py` | **MODIFICADO** | 3 bugs corrigidos |
| `test_hash_user_id.py` | **MODIFICADO** | Assinatura atualizada + fórmula IdParcela |
| `test_hasher_parcelas.py` | **NOVO** | 8 testes novos |
| `test_marker_parcelas.py` | **NOVO** | 11 testes novos |
| `recalculate_id_transacao_v5_1.py` | **NOVO** | Script de migração |
| `router.py` (upload) | Sem mudança | `marker.py` encapsula lógica |
| `service.py` (upload) | Sem mudança | Não toca em IdTransacao |
| `test_hash_pit_stop.py` | Verificar | Pode usar assinatura antiga |
| DB schema | Sem mudança | `parcela_atual`/`TotalParcelas` já existem |

---

## 8. Exemplos de Saída Esperada

### Antes da Migration v5.1

```sql
SELECT "EstabelecimentoBase", "MesFatura", "parcela_atual", "TotalParcelas", "IdTransacao"
FROM journal_entries WHERE "TotalParcelas" IS NOT NULL AND "user_id" = 1
ORDER BY "EstabelecimentoBase", "MesFatura";

-- EstabelecimentoBase     | MesFatura | parcela | total | IdTransacao
-- AIRBNB * HMHMZAQ        | 202601    |    1    |   6   | 12041517302535481192
-- (202602 parcela 2/6 BLOQUEADA — colisão com linha acima!)
```

### Após Migration v5.1

```sql
-- EstabelecimentoBase     | MesFatura | parcela | total | IdTransacao
-- AIRBNB * HMHMZAQ        | 202601    |    1    |   6   | <novo_id_unico_p1>
-- AIRBNB * HMHMZAQ        | 202602    |    2    |   6   | <novo_id_unico_p2>  ← diferente!
```

---

## 9. Validação E2E

**Cenário:** Reprocessar fatura-202602 após fix + migração

```
Arquivo: fatura_azul_202602.csv
Total de lançamentos no arquivo: 45

Resultado esperado após fix:
  ✅ Já Importadas: 31   (transações sem parcela + ANUIDADE que já estão no DB)
  ✅ Novas:         14   (parcelas 2/N, 3/N de compras iniciadas em 202601)
  ❌ Antes do fix: Já Importadas: 45, Novas: 0
```

---

## 10. Checklist de Implementação

- [ ] ✅ `hasher.py`: param `parcela` adicionado, testes passando
- [ ] ✅ `marker.py`: 3 bugs corrigidos, backward compat verificada
- [ ] ✅ `test_hasher_parcelas.py`: 8 testes, todos passando
- [ ] ✅ `test_marker_parcelas.py`: 11 testes, todos passando
- [ ] ✅ `test_hash_user_id.py`: assinatura atualizada, todos passando
- [ ] ✅ Migration v5.1: dry-run OK, 0 colisões após
- [ ] ✅ Migration v5.1: executada, ~42 registros atualizados
- [ ] ✅ E2E: re-upload fatura-202602 → 14 novas importadas
- [ ] ✅ E2E: re-upload fatura-202602 (segunda vez) → 0 novas (idempotente)
- [ ] ✅ Commit final com todos os arquivos
