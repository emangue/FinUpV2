"""
Regeneração de hashes — v5 (normalização de estabelecimento)
=============================================================

Substitui a normalização v4.2.3 (mantém espaços) pela v5 (remove [^A-Z0-9])
em todos os registros do banco.

Tabelas alteradas:
  1. journal_entries  — IdTransacao (todos) e IdParcela (parceladas)
  2. base_parcelas    — DELETE por user_id (órfãos do hash antigo)
  3. base_padroes     — DELETE + INSERT via regenerar_base_padroes_completa

Modelado a partir de regenerate_id_transacao_v4_2_3.py.

Uso:
    cd backend
    python scripts/regenerate_hashes_v5.py
"""

import sys
import re
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.shared.utils import generate_id_transacao


# ═══════════════════════════════════════════════════════════════════════════════
# Normalização v5
# ═══════════════════════════════════════════════════════════════════════════════

def _extrair_parcela_do_estab(estab: str):
    """
    Extrai (base, parcela, total) do estab_normalizado armazenado.
    Formatos esperados: 'NOME (3/10)' ou 'NOME 03/10' (legado).
    Retorna (None, None, None) se não tiver parcela.
    """
    for pat in (r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$',
                r'^(.+?)\s+(\d{1,2})/(\d{1,2})\s*$'):
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


# ═══════════════════════════════════════════════════════════════════════════════
# Funções de banco
# ═══════════════════════════════════════════════════════════════════════════════

def _get_db_path() -> Path:
    candidates = [
        Path(__file__).parent.parent / 'database' / 'financas_dev.db',
        Path(__file__).parent.parent / 'financas_dev.db',
        Path(__file__).parent.parent / 'financas.db',
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Banco de dados não encontrado. Tentativas: {[str(c) for c in candidates]}"
    )


def _listar_users(cursor) -> list:
    cursor.execute("SELECT DISTINCT user_id FROM journal_entries ORDER BY user_id")
    return [r[0] for r in cursor.fetchall()]


# ═══════════════════════════════════════════════════════════════════════════════
# Passo 1: Recalcular IdTransacao e IdParcela em journal_entries
# ═══════════════════════════════════════════════════════════════════════════════

def regenerar_journal_entries(cursor, conn):
    print("─" * 60)
    print("PASSO 1 — Recalcular IdTransacao e IdParcela")
    print("─" * 60)

    cursor.execute("""
        SELECT id, user_id, Data, Estabelecimento, Valor, tipodocumento, IdParcela
        FROM journal_entries
        ORDER BY user_id, Data, Estabelecimento, id
    """)
    rows = cursor.fetchall()
    total = len(rows)
    print(f"  Transações carregadas: {total}")

    is_fatura = lambda td: bool(td) and (
        'fatura' in td.lower() or 'cartao' in td.lower() or 'cartão' in td.lower()
    )

    seen_transactions = defaultdict(int)
    updates_tx     = []   # (novo_id_transacao, id_entry)
    updates_parcela = []  # (novo_id_parcela, id_entry)
    alteracoes_tx  = 0
    alteracoes_idp = 0

    for row in rows:
        id_entry, user_id, data, estab, valor, tipo_doc, id_parcela_atual = row

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
    contador = 0
    for novo_id, id_entry in updates_tx:
        cursor.execute(
            "UPDATE journal_entries SET IdTransacao = ? WHERE id = ?",
            (novo_id, id_entry),
        )
        contador += 1
        if contador % 500 == 0:
            conn.commit()
            print(f"    {contador}/{len(updates_tx)}...")
    conn.commit()
    print(f"  ✅ IdTransacao: {len(updates_tx)} registros atualizados")

    if updates_parcela:
        print(f"\n  Aplicando {len(updates_parcela)} atualizações de IdParcela...")
        contador = 0
        for novo_id, id_entry in updates_parcela:
            cursor.execute(
                "UPDATE journal_entries SET IdParcela = ? WHERE id = ?",
                (novo_id, id_entry),
            )
            contador += 1
            if contador % 200 == 0:
                conn.commit()
                print(f"    {contador}/{len(updates_parcela)}...")
        conn.commit()
        print(f"  ✅ IdParcela: {len(updates_parcela)} registros atualizados")
        print(f"     (desses, {alteracoes_idp} tiveram o hash efetivamente alterado)")
    else:
        print("  ✅ IdParcela: nenhuma parcelada encontrada")

    duplicatas = sum(1 for seq in seen_transactions.values() if seq > 1)
    print(f"\n  Grupos de duplicatas detectados: {duplicatas}")


# ═══════════════════════════════════════════════════════════════════════════════
# Passo 2: Limpar base_parcelas
# ═══════════════════════════════════════════════════════════════════════════════

def limpar_base_parcelas(cursor, conn, users: list):
    print("\n" + "─" * 60)
    print("PASSO 2 — Limpar base_parcelas")
    print("─" * 60)
    print("  Os registros com id_parcela antigo ficam órfãos.")
    print("  A tabela é recriada automaticamente no próximo upload.")

    total_deletado = 0
    for user_id in users:
        cursor.execute(
            "SELECT COUNT(*) FROM base_parcelas WHERE user_id = ?", (user_id,)
        )
        n = cursor.fetchone()[0]
        cursor.execute(
            "DELETE FROM base_parcelas WHERE user_id = ?", (user_id,)
        )
        total_deletado += n
        print(f"  user_id {user_id}: {n} registros removidos")
    conn.commit()
    print(f"  ✅ base_parcelas: {total_deletado} registros deletados no total")


# ═══════════════════════════════════════════════════════════════════════════════
# Passo 3: Regenerar base_padroes
# ═══════════════════════════════════════════════════════════════════════════════

def regenerar_base_padroes(users: list):
    print("\n" + "─" * 60)
    print("PASSO 3 — Regenerar base_padroes")
    print("─" * 60)

    try:
        from app.domains.upload.processors.pattern_generator import regenerar_base_padroes_completa
        from app.core.database import get_db_session  # ajuste o import se necessário

        with get_db_session() as db:
            for user_id in users:
                print(f"  Regenerando padrões para user_id {user_id}...")
                resultado = regenerar_base_padroes_completa(db, user_id)
                print(f"  ✅ user_id {user_id}: {resultado}")

    except ImportError as e:
        print(f"  ⚠️  Não foi possível importar regenerar_base_padroes_completa: {e}")
        print("       Execute manualmente via API ou ajuste o import acima.")
        print("       Alternativa: fazer um upload de qualquer fatura para cada usuário,")
        print("       o que aciona a regeneração automática de base_padroes.")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print()
    print("=" * 60)
    print(" REGENERAÇÃO DE HASHES — v5 (normalização de estabelecimento)")
    print("=" * 60)
    print()
    print("Tabelas afetadas:")
    print("  • journal_entries  → IdTransacao + IdParcela (UPDATE)")
    print("  • base_parcelas    → DELETE por user_id")
    print("  • base_padroes     → DELETE + regenerar")
    print()

    try:
        db_path = _get_db_path()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    print(f"Banco:  {db_path}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    resposta = input("⚠️  Isso irá REGENERAR todos os hashes. Continuar? (s/N): ")
    if resposta.strip().lower() != 's':
        print("❌ Cancelado pelo usuário.")
        sys.exit(0)

    print()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        users = _listar_users(cursor)
        print(f"Usuários encontrados: {users}")
        print()

        # Passo 1 — journal_entries
        regenerar_journal_entries(cursor, conn)

        # Passo 2 — base_parcelas
        limpar_base_parcelas(cursor, conn, users)

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()

    # Passo 3 — base_padroes (usa SQLAlchemy session separada)
    regenerar_base_padroes(users)

    print()
    print("=" * 60)
    print(f"✅ Migração concluída: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Próximos passos:")
    print("  1. Re-rodar este script para confirmar 0 alterações (idempotência)")
    print("  2. Verificar base_padroes: confiança ≥ 95% nos padrões principais")
    print("  3. Deploy em produção + repetir passo 4 e 5 do README")
    print("=" * 60)


if __name__ == '__main__':
    main()
