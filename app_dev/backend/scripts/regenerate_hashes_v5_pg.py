"""
Regeneração de hashes — v5 (normalização de estabelecimento) — PostgreSQL
=========================================================================

Versão adaptada de regenerate_hashes_v5.py para rodar dentro do container
Docker com PostgreSQL via SQLAlchemy.

Mesma lógica do script SQLite, mas usa get_db() / SQLAlchemy em vez de sqlite3.

Tabelas alteradas:
  1. journal_entries  — IdTransacao (todos) e IdParcela (parceladas)
  2. base_parcelas    — DELETE por user_id (órfãos do hash antigo)
  3. base_padroes     — DELETE + INSERT via regenerar_base_padroes_completa

Uso (dentro do container):
    python scripts/regenerate_hashes_v5_pg.py
"""

import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import get_db
from app.shared.utils import generate_id_transacao


# ══════════════════════════════════════════════════════════════════════════════
# Normalização v5
# ══════════════════════════════════════════════════════════════════════════════

def _extrair_parcela_do_estab(estab: str):
    """
    Extrai (base, parcela, total) do Estabelecimento armazenado.
    Formatos esperados: 'NOME (3/10)', 'NOME 03/10' ou 'NOME03/10' (colado, sem espaço).
    Retorna (None, None, None) se não tiver parcela.

    CRÍTICO: usa \s* (zero ou mais espaços) no segundo padrão para capturar
    entradas "coladas" como 'POUSADA CANTOS E C02/04' — sem espaço antes da parcela.
    O marker.py também usa \s*, então ambos devem estar consistentes.
    """
    for pat in (r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$',
                r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$'):
        m = re.match(pat, estab.strip())
        if m:
            p, t = int(m.group(2)), int(m.group(3))
            if 1 <= p <= t <= 99:
                return m.group(1).strip(), p, t
    return None, None, None


def processar_estab_v5(estabelecimento: str) -> str:
    """
    Normalização v5: remove tudo que não é [A-Z0-9] da base; preserva (p/t).

    Entrada:  Estabelecimento já normalizado (coluna journal_entries)
              Exemplos: 'VIVARA VIL (6/10)', 'CONTA VIVO', 'LOUCOSPORFUTEBOL (1/3)'
    Saída:    'VIVARAVIL (6/10)', 'CONTAVIVO', 'LOUCOSPORFUTEBOL (1/3)'
    """
    base, p, t = _extrair_parcela_do_estab(estabelecimento)
    if base is not None:
        base_norm = re.sub(r'[^A-Z0-9]', '', base.upper())
        return f"{base_norm} ({p}/{t})"
    return re.sub(r'[^A-Z0-9]', '', estabelecimento.upper())


def calcular_id_parcela_v5(base_nome: str, valor_abs: float, total: int, user_id: int) -> str:
    """
    Recalcula IdParcela com normalização v5.
    Fórmula: MD5[:16] de '{base_v5}|{valor:.2f}|{total}|{user_id}'
    """
    base_v5 = re.sub(r'[^A-Z0-9]', '', base_nome.upper())
    chave = f"{base_v5}|{valor_abs:.2f}|{total}|{user_id}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]


# ══════════════════════════════════════════════════════════════════════════════
# Passo 1: Recalcular IdTransacao e IdParcela em journal_entries
# ══════════════════════════════════════════════════════════════════════════════

def regenerar_journal_entries(db):
    print("─" * 60)
    print("PASSO 1 — Recalcular IdTransacao e IdParcela")
    print("─" * 60)

    rows = db.execute(text("""
        SELECT id, user_id, "Data", "Estabelecimento", "Valor", tipodocumento, "IdParcela"
        FROM journal_entries
        ORDER BY user_id, "Data", "Estabelecimento", id
    """)).fetchall()

    total = len(rows)
    print(f"  Transações carregadas: {total}")

    def is_fatura(td):
        return bool(td) and (
            'fatura' in td.lower() or 'cartao' in td.lower() or 'cartão' in td.lower()
        )

    seen_transactions = defaultdict(int)
    updates_tx = []       # (novo_id_transacao, id_entry)
    updates_parcela = []  # (novo_id_parcela, id_entry)
    alteracoes_idp = 0

    for row in rows:
        id_entry, user_id, data, estab, valor, tipo_doc, id_parcela_atual = row

        estab = estab or ''
        valor = float(valor or 0)
        estab_v5 = processar_estab_v5(estab)

        # ── IdTransacao ────────────────────────────────────────────────────
        chave_unica = f"{data}|{estab_v5}|{valor:.2f}"
        seen_transactions[chave_unica] += 1
        sequencia = seen_transactions[chave_unica]

        novo_id_tx = generate_id_transacao(
            data=data,
            estabelecimento=estab_v5,
            valor=valor,
            user_id=user_id,
            sequencia=sequencia,
        )
        updates_tx.append((novo_id_tx, id_entry))

        # ── IdParcela (somente parceladas em faturas) ──────────────────────
        if is_fatura(tipo_doc) and id_parcela_atual is not None:
            base, p, t = _extrair_parcela_do_estab(estab)
            if base is not None and t:
                novo_id_parcela = calcular_id_parcela_v5(base, abs(valor), t, user_id)
                if novo_id_parcela != id_parcela_atual:
                    alteracoes_idp += 1
                updates_parcela.append((novo_id_parcela, id_entry))

    # ── Aplicar atualizações ──────────────────────────────────────────────
    print(f"\n  Aplicando {len(updates_tx)} atualizações de IdTransacao...")
    for i, (novo_id, id_entry) in enumerate(updates_tx, 1):
        db.execute(
            text('UPDATE journal_entries SET "IdTransacao" = :id WHERE id = :entry_id'),
            {"id": novo_id, "entry_id": id_entry},
        )
        if i % 500 == 0:
            db.flush()
            print(f"    {i}/{len(updates_tx)}...")

    db.flush()
    print(f"  ✅ IdTransacao: {len(updates_tx)} registros atualizados")

    if updates_parcela:
        print(f"\n  Aplicando {len(updates_parcela)} atualizações de IdParcela...")
        for i, (novo_id, id_entry) in enumerate(updates_parcela, 1):
            db.execute(
                text('UPDATE journal_entries SET "IdParcela" = :id WHERE id = :entry_id'),
                {"id": novo_id, "entry_id": id_entry},
            )
            if i % 200 == 0:
                db.flush()
                print(f"    {i}/{len(updates_parcela)}...")
        db.flush()
        print(f"  ✅ IdParcela: {len(updates_parcela)} registros atualizados")
        print(f"     (desses, {alteracoes_idp} tiveram o hash efetivamente alterado)")
    else:
        print("  ✅ IdParcela: nenhuma parcelada encontrada")

    duplicatas = sum(1 for seq in seen_transactions.values() if seq > 1)
    print(f"\n  Grupos de duplicatas detectados: {duplicatas}")


# ══════════════════════════════════════════════════════════════════════════════
# Passo 2: Limpar base_parcelas
# ══════════════════════════════════════════════════════════════════════════════

def limpar_base_parcelas(db):
    print("\n" + "─" * 60)
    print("PASSO 2 — Limpar base_parcelas")
    print("─" * 60)
    print("  Os registros com id_parcela antigo ficam órfãos.")
    print("  Passo 4 irá reconstruí-la a partir de journal_entries.")

    users = db.execute(
        text("SELECT DISTINCT user_id FROM journal_entries ORDER BY user_id")
    ).fetchall()
    users = [r[0] for r in users]

    total_deletado = 0
    for user_id in users:
        n = db.execute(
            text("SELECT COUNT(*) FROM base_parcelas WHERE user_id = :uid"),
            {"uid": user_id}
        ).scalar()
        db.execute(
            text("DELETE FROM base_parcelas WHERE user_id = :uid"),
            {"uid": user_id}
        )
        total_deletado += n
        print(f"  user_id {user_id}: {n} registros removidos")

    db.flush()
    print(f"  ✅ base_parcelas: {total_deletado} registros deletados no total")
    return users


# ══════════════════════════════════════════════════════════════════════════════
# Passo 3 (novo): Reconstruir base_parcelas a partir de journal_entries
# ══════════════════════════════════════════════════════════════════════════════

def reconstruir_base_parcelas(db, users: list):
    """
    Reconstrói base_parcelas a partir dos journal_entries existentes.

    Para cada IdParcela único (TotalParcelas > 1):
    - Pega dados da parcela com menor parcela_atual (base da série)
    - Calcula qtd_pagas = MAX(parcela_atual) do grupo
    - Define status = 'finalizada' se qtd_pagas >= qtd_parcelas, senão 'ativa'
    """
    from datetime import datetime

    print("\n" + "─" * 60)
    print("PASSO 3 (novo) — Reconstruir base_parcelas")
    print("─" * 60)

    SQL = text("""
        WITH ranked AS (
            SELECT
                "IdParcela",
                "EstabelecimentoBase",
                "ValorPositivo",
                "TotalParcelas",
                "GRUPO",
                "SUBGRUPO",
                "TipoGasto",
                "CategoriaGeral",
                "Data",
                user_id,
                parcela_atual,
                MAX(parcela_atual) OVER (PARTITION BY "IdParcela", user_id) AS max_parcela,
                ROW_NUMBER() OVER (PARTITION BY "IdParcela", user_id ORDER BY parcela_atual ASC) AS rn
            FROM journal_entries
            WHERE "IdParcela" IS NOT NULL
              AND "TotalParcelas" > 1
        )
        SELECT
            "IdParcela", user_id, "EstabelecimentoBase", "ValorPositivo",
            "TotalParcelas", "GRUPO", "SUBGRUPO", "TipoGasto", "CategoriaGeral",
            "Data", max_parcela
        FROM ranked
        WHERE rn = 1
        ORDER BY user_id, "IdParcela"
    """)

    rows = db.execute(SQL).fetchall()
    total = 0
    por_user = {u: 0 for u in users}

    now = datetime.now()
    for row in rows:
        (
            id_parcela, user_id, estab_base, valor_parcela,
            total_parcelas, grupo, subgrupo, tipo_gasto, categoria_geral,
            data_inicio, max_parcela
        ) = row

        status = 'finalizada' if (max_parcela or 0) >= (total_parcelas or 1) else 'ativa'
        valor_total = (valor_parcela or 0) * (total_parcelas or 1)

        db.execute(text("""
            INSERT INTO base_parcelas
                (user_id, id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas,
                 qtd_pagas, valor_total_plano, grupo_sugerido, subgrupo_sugerido,
                 tipo_gasto_sugerido, categoria_geral_sugerida, data_inicio,
                 status, created_at, updated_at)
            VALUES
                (:user_id, :id_parcela, :estab_base, :valor_parcela, :qtd_parcelas,
                 :qtd_pagas, :valor_total, :grupo, :subgrupo, :tipo_gasto,
                 :categoria_geral, :data_inicio, :status, :now, :now)
            ON CONFLICT DO NOTHING
        """), {
            'user_id': user_id,
            'id_parcela': id_parcela,
            'estab_base': estab_base,
            'valor_parcela': valor_parcela,
            'qtd_parcelas': total_parcelas,
            'qtd_pagas': max_parcela,
            'valor_total': valor_total,
            'grupo': grupo,
            'subgrupo': subgrupo,
            'tipo_gasto': tipo_gasto,
            'categoria_geral': categoria_geral,
            'data_inicio': data_inicio,
            'status': status,
            'now': now,
        })

        total += 1
        if user_id in por_user:
            por_user[user_id] += 1

    db.flush()

    for user_id, n in por_user.items():
        print(f"  ✅ user_id {user_id}: {n} parcelas inseridas")
    print(f"  ✅ base_parcelas: {total} registros reconstruídos no total")


# ══════════════════════════════════════════════════════════════════════════════
# Passo 4: Regenerar base_padroes
# ══════════════════════════════════════════════════════════════════════════════

def regenerar_base_padroes(db, users: list):
    print("\n" + "─" * 60)
    print("PASSO 4 — Regenerar base_padroes")
    print("─" * 60)

    try:
        from app.domains.upload.processors.pattern_generator import regenerar_base_padroes_completa

        for user_id in users:
            print(f"  Regenerando padrões para user_id {user_id}...")
            resultado = regenerar_base_padroes_completa(db, user_id)
            print(f"  ✅ user_id {user_id}: {resultado}")

    except Exception as e:
        print(f"  ⚠️  Erro ao regenerar base_padroes: {e}")
        import traceback; traceback.print_exc()
        print("       Alternativa: fazer upload de qualquer fatura para acionar regeneração automática.")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print()
    print("=" * 60)
    print(" REGENERAÇÃO DE HASHES — v5 (PostgreSQL)")
    print("=" * 60)
    print()
    print("Tabelas afetadas:")
    print("  • journal_entries  → IdTransacao + IdParcela (UPDATE)")
    print("  • base_parcelas    → DELETE + reconstruir a partir de journal_entries")
    print("  • base_padroes     → DELETE + regenerar")
    print()

    resposta = 's'  # auto-confirmado para execução via docker exec
    if resposta.strip().lower() != 's':
        print("❌ Cancelado pelo usuário.")
        sys.exit(0)

    print()
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    db = next(get_db())

    try:
        # Passo 1 — journal_entries
        regenerar_journal_entries(db)

        # Passo 2 — base_parcelas (limpar)
        users = limpar_base_parcelas(db)

        # Passo 3 — base_parcelas (reconstruir)
        reconstruir_base_parcelas(db, users)

        # Passo 4 — base_padroes
        regenerar_base_padroes(db, users)

        db.commit()
        print()
        print("=" * 60)
        print(f"✅ Migração concluída: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Próximos passos:")
        print("  1. Re-rodar este script para confirmar 0 alterações (idempotência)")
        print("  2. Verificar base_padroes: confiança ≥ 95% nos padrões principais")
        print("  3. Deploy em produção após validar")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()
