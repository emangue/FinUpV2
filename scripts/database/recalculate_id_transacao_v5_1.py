#!/usr/bin/env python3
"""
Migration v5.1 — Recalcula IdTransacao e IdParcela para registros parcelados.

Escopo: APENAS registros com "TotalParcelas" IS NOT NULL (~42 registros).
Registros não-parcelados (TotalParcelas IS NULL): INTOCADOS.

Uso:
    # Visualizar o que seria alterado (sem tocar no banco)
    python scripts/database/recalculate_id_transacao_v5_1.py --dry-run

    # Executar de verdade
    python scripts/database/recalculate_id_transacao_v5_1.py

Referência:
    PRD:       docs/features/upload-banco-manual/01-PRD/PRD_parcelas_v5_1.md
    Tech Spec: docs/features/upload-banco-manual/02-TECH_SPEC/TECH_SPEC_parcelas_v5_1.md
    Sprint:    docs/features/upload-banco-manual/03-SPRINT/SPRINT3_parcelas.md
"""
import argparse
import hashlib
import importlib.util
import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 não instalado. Ative o venv: source app_dev/venv/bin/activate")
    sys.exit(1)

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
BACKEND_DIR = PROJECT_DIR / "app_dev" / "backend"
HASHER_PATH = BACKEND_DIR / "app" / "shared" / "utils" / "hasher.py"

# Fallback: dentro do container Docker, app está em /app/
DOCKER_HASHER = Path("/app/app/shared/utils/hasher.py")
if not HASHER_PATH.exists() and DOCKER_HASHER.exists():
    HASHER_PATH = DOCKER_HASHER

if not HASHER_PATH.exists():
    print(f"❌ hasher.py não encontrado em: {HASHER_PATH}")
    sys.exit(1)

# ─── Import hasher.py (sem FastAPI) ───────────────────────────────────────────
spec = importlib.util.spec_from_file_location("hasher", HASHER_PATH)
hasher_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hasher_mod)
generate_id_transacao = hasher_mod.generate_id_transacao

# ─── DB ───────────────────────────────────────────────────────────────────────
DB_URL = os.getenv("DATABASE_URL", "postgresql://finup_user:finup_password_dev_2026@localhost:5432/finup_db")


# ─── Fórmula IdParcela v5.1 ───────────────────────────────────────────────────
def gerar_id_parcela_v5_1(banco: str, tipo: str, data: str,
                           valor: float, total: int, user_id: int) -> str:
    """
    Nova fórmula IdParcela v5.1 — fingerprint banco|tipo|data|valor|total|user_id.

    Remove dependência de nome de estabelecimento (frágil entre PDF/CSV).
    Consistente para a mesma compra independente do formato do arquivo.
    """
    chave = f"{banco}|{tipo}|{data}|{valor:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]


def run_migration(dry_run: bool = True) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""

    try:
        conn = psycopg2.connect(DB_URL)
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        print("   Verifique se o Docker está rodando: docker-compose ps")
        sys.exit(1)

    cur = conn.cursor()

    # ── 1. Contar registros não-parcelados (devem ficar intocados) ─────────────
    cur.execute('SELECT COUNT(*) FROM journal_entries WHERE "TotalParcelas" IS NULL')
    count_nao_parcelados = cur.fetchone()[0]

    # ── 2. Buscar todos os registros parcelados ────────────────────────────────
    cur.execute("""
        SELECT
            "IdTransacao",
            "user_id",
            "banco_origem",
            "tipodocumento",
            "Data",
            "Valor",
            "parcela_atual",
            "TotalParcelas",
            "EstabelecimentoBase",
            "MesFatura"
        FROM journal_entries
        WHERE "TotalParcelas" IS NOT NULL
        ORDER BY "user_id", "MesFatura", "EstabelecimentoBase", "parcela_atual"
    """)
    rows = cur.fetchall()

    print(f"\n{'═'*70}")
    print(f"  MIGRATION v5.1 — Recálculo IdTransacao + IdParcela (parcelas)")
    print(f"{'═'*70}")
    print(f"  {prefix}Registros parcelados encontrados : {len(rows)}")
    print(f"  Registros não-parcelados (intocados): {count_nao_parcelados}")
    print(f"{'─'*70}\n")

    updates = []
    ids_antes  = set()
    ids_depois = set()
    colisoes_antes  = {}  # id_antigo → contagem
    colisoes_depois = {}  # id_novo   → contagem

    for row in rows:
        (id_atual, user_id, banco, tipo, data, valor,
         parcela_atual, total_parcelas, estab, mes_fatura) = row

        parcela_param = f"{parcela_atual}/{total_parcelas}"
        novo_id = generate_id_transacao(
            data=data,
            banco=banco,
            tipo_documento=tipo,
            valor=float(valor),
            user_id=user_id,
            parcela=parcela_param,
        )
        novo_id_parcela = gerar_id_parcela_v5_1(
            banco=banco,
            tipo=tipo,
            data=data,
            valor=float(valor),
            total=total_parcelas,
            user_id=user_id,
        )

        ids_antes.add(id_atual)
        ids_depois.add(novo_id)
        colisoes_antes[id_atual]  = colisoes_antes.get(id_atual, 0) + 1
        colisoes_depois[novo_id]  = colisoes_depois.get(novo_id, 0) + 1
        updates.append((novo_id, novo_id_parcela, id_atual))

        mudou = "✏️ " if id_atual != novo_id else "✅ "
        print(f"  {mudou}{prefix}"
              f"user={user_id} | {estab} | p{parcela_atual}/{total_parcelas} "
              f"| MesFatura={mes_fatura}")
        print(f"       IdTransacao: {id_atual}")
        print(f"               → : {novo_id}")
        print(f"       IdParcela  → {novo_id_parcela}\n")

    # ── 3. Diagnóstico de unicidade ────────────────────────────────────────────
    print(f"{'─'*70}")
    print(f"  DIAGNÓSTICO DE UNICIDADE")
    print(f"{'─'*70}")
    print(f"  IDs únicos ANTES   : {len(ids_antes):3d} (de {len(rows)} registros)")
    print(f"  IDs únicos DEPOIS  : {len(ids_depois):3d} (de {len(rows)} registros)")

    # Verificar colisões antes
    colisoes_antes_list = [(k, v) for k, v in colisoes_antes.items() if v > 1]
    if colisoes_antes_list:
        print(f"\n  ⚠️  Colisões ANTES da migração: {len(colisoes_antes_list)} grupos")
        for id_col, cnt in colisoes_antes_list[:5]:
            print(f"       {id_col}: {cnt} registros")
    else:
        print(f"  ✅ Sem colisões antes (esperado se v5 já ok para extrato)")

    # Verificar colisões depois
    colisoes_depois_list = [(k, v) for k, v in colisoes_depois.items() if v > 1]
    if colisoes_depois_list:
        print(f"\n  ❌ COLISÕES APÓS MIGRAÇÃO: {len(colisoes_depois_list)} grupos")
        for id_col, cnt in colisoes_depois_list[:10]:
            print(f"       {id_col}: {cnt} registros — PROBLEMA!")
        print(f"\n  ❌ ABORTANDO — migração geraria colisões. Investigar antes de prosseguir.")
        conn.close()
        sys.exit(1)
    else:
        print(f"  ✅ Nenhuma colisão após migração")

    # ── 4. Executar ou apenas simular ─────────────────────────────────────────
    print(f"\n{'─'*70}")
    if dry_run:
        print(f"  [DRY-RUN] {len(updates)} registros seriam atualizados.")
        print(f"  Use sem --dry-run para executar a migração real.")
        conn.close()
        return

    print(f"  Executando {len(updates)} updates...")
    erros = 0
    for novo_id, novo_id_parcela, id_antigo in updates:
        try:
            cur.execute("""
                UPDATE journal_entries
                SET "IdTransacao" = %s, "IdParcela" = %s
                WHERE "IdTransacao" = %s
            """, (novo_id, novo_id_parcela, id_antigo))
        except Exception as e:
            print(f"  ❌ Erro ao atualizar {id_antigo}: {e}")
            erros += 1

    if erros > 0:
        conn.rollback()
        print(f"\n  ❌ {erros} erros durante update. Rollback executado.")
        conn.close()
        sys.exit(1)

    conn.commit()

    # ── 5. Validação pós-migration ─────────────────────────────────────────────
    cur.execute("""
        SELECT "IdTransacao", COUNT(*) AS cnt
        FROM journal_entries
        WHERE "TotalParcelas" IS NOT NULL
        GROUP BY "IdTransacao"
        HAVING COUNT(*) > 1
    """)
    colisoes_pos = cur.fetchall()

    cur.execute('SELECT COUNT(*) FROM journal_entries WHERE "TotalParcelas" IS NULL')
    count_nao_parcelados_pos = cur.fetchone()[0]

    print(f"\n{'═'*70}")
    print(f"  RESULTADO DA MIGRAÇÃO v5.1")
    print(f"{'═'*70}")
    print(f"  ✅ {len(updates)} registros atualizados com sucesso")
    print(f"  ✅ Não-parcelados (intocados): {count_nao_parcelados_pos} "
          f"(era {count_nao_parcelados})")

    if colisoes_pos:
        print(f"  ❌ AINDA HÁ COLISÕES após migração: {len(colisoes_pos)} grupos")
        for row in colisoes_pos[:5]:
            print(f"     {row[0]}: {row[1]} registros")
    else:
        print(f"  ✅ 0 colisões em IdTransacao (parcelados)")

    print(f"{'═'*70}\n")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migration v5.1 — Recalcula IdTransacao + IdParcela para parcelas"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simula a migração sem alterar o banco (default: False)",
    )
    args = parser.parse_args()
    run_migration(dry_run=args.dry_run)
