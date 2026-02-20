#!/usr/bin/env python3
"""
MIGRAÇÃO COMPLETA: Revisão de Grupos e Subgrupos
================================================
Executa o plano completo de consolidação:
- 14 grupos (11 Despesa + Investimentos, Transferência, Salário)
- base_grupos_config, base_marcacoes, generic_classification_rules
- journal_entries, budget_planning, base_padroes, base_parcelas
"""
import sqlite3
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"

# 14 grupos consolidados
GRUPOS_SEED = [
    ("Alimentação", "Ajustável", "Despesa"),
    ("Moradia e Serviços", "Ajustável", "Despesa"),
    ("Carro", "Ajustável", "Despesa"),
    ("Transporte", "Ajustável", "Despesa"),
    ("Lazer", "Ajustável", "Despesa"),
    ("Saúde", "Fixo", "Despesa"),
    ("Educação", "Fixo", "Despesa"),
    ("Viagens", "Ajustável", "Despesa"),
    ("Compras e Tecnologia", "Ajustável", "Despesa"),
    ("Doações", "Ajustável", "Despesa"),
    ("Outros", "Ajustável", "Despesa"),
    ("Investimentos", "Investimentos", "Investimentos"),
    ("Transferência Entre Contas", "Transferência", "Transferência"),
    ("Salário", "Receita", "Receita"),
]

# Mapeamento: (grupo_antigo, subgrupo_antigo) -> (grupo_novo, subgrupo_novo)
MAPEAMENTO_GRUPO_SUBGRUPO = {
    # Compras e Tecnologia
    ("MeLi + Amazon", "MeLi + Amazon"): ("Compras e Tecnologia", "MeLi + Amazon"),
    ("MeLi   Amazon", "MeLi   Amazon"): ("Compras e Tecnologia", "MeLi + Amazon"),
    ("MeLi + Amazon", "MeLi + Amazon"): ("Compras e Tecnologia", "MeLi + Amazon"),
    # Tecnologia -> Compras e Tecnologia
    ("Tecnologia", None): ("Compras e Tecnologia", "Eletrônicos"),
    # Casa, Serviços -> Moradia e Serviços
    ("Casa", None): ("Moradia e Serviços", None),  # manter subgrupo
    ("Serviços", None): ("Moradia e Serviços", None),
    # Assinaturas - por subgrupo
    ("Assinaturas", "ConectCar"): ("Carro", "ConnectCar"),
    ("Assinaturas", "ConnectCar"): ("Carro", "ConnectCar"),
    ("Assinaturas", "CONECTCAR"): ("Carro", "ConnectCar"),
    ("Assinaturas", "Connetcar"): ("Carro", "ConnectCar"),
    ("Assinaturas", "Sem Parar"): ("Carro", "Sem Parar"),
    ("Assinaturas", "Rappi"): ("Alimentação", "Delivery"),
    ("Assinaturas", "Tem Bici"): ("Transporte", "Bike"),
    ("Assinaturas", "Spotify"): ("Lazer", "Spotify"),
    ("Assinaturas", "Premiere"): ("Lazer", "Premiere"),
    ("Assinaturas", "Disney+"): ("Lazer", "Disney+"),
    ("Assinaturas", "Apple"): ("Lazer", "Apple"),
    ("Assinaturas", "Audible"): ("Lazer", "Audible"),
    ("Assinaturas", "Amazon"): ("Compras e Tecnologia", "Amazon"),
    ("Assinaturas", "Amazon Prime"): ("Compras e Tecnologia", "Amazon Prime"),
    ("Assinaturas", "MeLi+"): ("Compras e Tecnologia", "MeLi+"),
    ("Assinaturas", "Meli+"): ("Compras e Tecnologia", "MeLi+"),
    ("Assinaturas", "Paramount"): ("Lazer", "Paramount+"),
    ("Assinaturas", "Paramount+"): ("Lazer", "Paramount+"),
    ("Assinaturas", "Youtube"): ("Lazer", "Youtube"),
    ("Assinaturas", "DAZN"): ("Lazer", "DAZN"),
    ("Assinaturas", "Folha SP"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Folha de SP"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Anuidade"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Seguro TC"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Mensagem Cartão"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Mensagem Automática"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Outros"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Gympass"): ("Saúde", "Gympass"),
    ("Assinaturas", "ICloud"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Google Photos"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Gemini"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Mobills"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Moni"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Valor"): ("Lazer", "Assinaturas"),
    ("Assinaturas", "Wine"): ("Lazer", "Assinaturas"),
    # Entretenimento, Roupas, Presentes -> Lazer
    ("Entretenimento", None): ("Lazer", None),
    ("Roupas", None): ("Lazer", None),
    ("Presentes", None): ("Lazer", None),
    # Manter 1:1
    ("Alimentação", None): ("Alimentação", None),
    ("Carro", None): ("Carro", None),
    ("Transporte", None): ("Transporte", None),
    ("Saúde", None): ("Saúde", None),
    ("Educação", None): ("Educação", None),
    ("Viagens", None): ("Viagens", None),
    ("Doações", None): ("Doações", None),
    ("Outros", None): ("Outros", None),
    ("Investimentos", None): ("Investimentos", None),
    ("Transferência Entre Contas", None): ("Transferência Entre Contas", None),
    ("Salário", None): ("Salário", None),
}

# Subgrupos Assinaturas -> Lazer (genérico quando não mapeado)
ASSINATURAS_TO_LAZER = {"Gympass"}  # Gympass -> Saúde
ASSINATURAS_TO_SAUDE = {"Gympass"}


def get_mapping(grupo: str, subgrupo: str) -> tuple:
    """Retorna (grupo_novo, subgrupo_novo). None em subgrupo = manter original."""
    key = (grupo, subgrupo)
    if key in MAPEAMENTO_GRUPO_SUBGRUPO:
        gn, sn = MAPEAMENTO_GRUPO_SUBGRUPO[key]
        return (gn, sn if sn else subgrupo)
    key_any = (grupo, None)
    if key_any in MAPEAMENTO_GRUPO_SUBGRUPO:
        gn, sn = MAPEAMENTO_GRUPO_SUBGRUPO[key_any]
        return (gn, subgrupo if sn is None else sn)
    return (grupo, subgrupo)


def run_migration(dry_run: bool = False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print("=" * 80)
    print("MIGRAÇÃO COMPLETA: Revisão Grupos e Subgrupos")
    print("=" * 80)
    print(f"Banco: {DB_PATH}")
    print(f"Modo: {'DRY RUN (sem alterações)' if dry_run else 'EXECUÇÃO REAL'}")
    print()

    try:
        # 0. Fix MeLi   Amazon typo
        print("0. Corrigindo MeLi   Amazon -> MeLi + Amazon em journal_entries...")
        cur.execute(
            "UPDATE journal_entries SET GRUPO=?, SUBGRUPO=? WHERE GRUPO=? AND SUBGRUPO=?",
            ("MeLi + Amazon", "MeLi + Amazon", "MeLi   Amazon", "MeLi   Amazon"),
        )
        print(f"   {cur.rowcount} linhas atualizadas")

        if not dry_run:
            conn.commit()

        # 1. Backup base_grupos_config e base_marcacoes
        print("\n1. Backup de base_grupos_config e base_marcacoes...")
        cur.execute("SELECT * FROM base_grupos_config")
        backup_grupos = cur.fetchall()
        cur.execute("SELECT * FROM base_marcacoes")
        backup_marcacoes = cur.fetchall()
        print(f"   Backup: {len(backup_grupos)} grupos, {len(backup_marcacoes)} marcações")

        # 2. Recriar base_grupos_config
        print("\n2. Recriando base_grupos_config com 14 grupos...")
        if not dry_run:
            cur.execute("DELETE FROM base_grupos_config")
            for nome, tipo, cat in GRUPOS_SEED:
                cur.execute(
                    "INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral) VALUES (?, ?, ?)",
                    (nome, tipo, cat),
                )
            conn.commit()
        print(f"   {len(GRUPOS_SEED)} grupos inseridos")

        # 3. Coletar combinações únicas de journal_entries + base_marcacoes mapeadas
        print("\n3. Construindo novas combinações base_marcacoes...")
        combinacoes = set()

        cur.execute("SELECT DISTINCT GRUPO, SUBGRUPO FROM journal_entries WHERE GRUPO IS NOT NULL AND SUBGRUPO IS NOT NULL")
        for row in cur.fetchall():
            g, s = row[0], row[1]
            gn, sn = get_mapping(g, s)
            combinacoes.add((gn, sn))

        cur.execute('SELECT DISTINCT "GRUPO", "SUBGRUPO" FROM base_marcacoes')
        for row in cur.fetchall():
            g, s = row[0], row[1]
            gn, sn = get_mapping(g, s)
            combinacoes.add((gn, sn))

        # Adicionar combinações padrão dos novos grupos
        for grupo, _, _ in GRUPOS_SEED:
            if grupo == "Moradia e Serviços":
                combinacoes.update([
                    ("Moradia e Serviços", "Aluguel"), ("Moradia e Serviços", "Condomínio"),
                    ("Moradia e Serviços", "Energia"), ("Moradia e Serviços", "Internet"),
                    ("Moradia e Serviços", "Celular"), ("Moradia e Serviços", "Limpeza"),
                    ("Moradia e Serviços", "Cabeleireiro"), ("Moradia e Serviços", "Lavanderia"),
                    ("Moradia e Serviços", "Serviços"), ("Moradia e Serviços", "Outros"),
                ])
            elif grupo == "Compras e Tecnologia":
                combinacoes.update([
                    ("Compras e Tecnologia", "MeLi + Amazon"), ("Compras e Tecnologia", "Amazon"),
                    ("Compras e Tecnologia", "Eletrônicos"), ("Compras e Tecnologia", "Computador"),
                    ("Compras e Tecnologia", "Outros"),
                ])
            elif grupo == "Lazer":
                combinacoes.update([
                    ("Lazer", "Saídas"), ("Lazer", "Entretenimento"), ("Lazer", "Roupas"),
                    ("Lazer", "Presentes"), ("Lazer", "Assinaturas"), ("Lazer", "Spotify"),
                    ("Lazer", "Cinema"), ("Lazer", "Eventos"),
                ])

        # Filtrar apenas combinações cujo grupo existe
        grupos_validos = {g[0] for g in GRUPOS_SEED}
        combinacoes = [(g, s) for g, s in combinacoes if g in grupos_validos and s]

        print(f"   {len(combinacoes)} combinações únicas")

        # 4. Recriar base_marcacoes
        print("\n4. Recriando base_marcacoes...")
        if not dry_run:
            cur.execute("DELETE FROM base_marcacoes")
            for i, (g, s) in enumerate(sorted(combinacoes), 1):
                cur.execute('INSERT INTO base_marcacoes (id, "GRUPO", "SUBGRUPO") VALUES (?, ?, ?)', (i, g, s))
            conn.commit()
        print(f"   {len(combinacoes)} marcações inseridas")

        # 5. UPDATE generic_classification_rules
        print("\n5. Atualizando generic_classification_rules...")
        cur.execute("SELECT id, grupo, subgrupo FROM generic_classification_rules WHERE ativo=1")
        rules = cur.fetchall()
        updates = 0
        for r in rules:
            g_old, s_old = r[1], r[2]
            g_new, s_new = get_mapping(g_old, s_old)
            # Limpeza órfã -> Moradia e Serviços > Limpeza
            if g_old == "Limpeza":
                g_new, s_new = "Moradia e Serviços", "Limpeza"
            if (g_old, s_old) != (g_new, s_new):
                if not dry_run:
                    cur.execute(
                        "UPDATE generic_classification_rules SET grupo=?, subgrupo=? WHERE id=?",
                        (g_new, s_new, r[0]),
                    )
                updates += 1
        print(f"   {updates} regras atualizadas")

        if not dry_run:
            conn.commit()

        # 6. UPDATE journal_entries
        print("\n6. Atualizando journal_entries...")
        cur.execute("SELECT id, GRUPO, SUBGRUPO FROM journal_entries WHERE GRUPO IS NOT NULL")
        rows = cur.fetchall()
        je_updates = 0
        for r in rows:
            g_new, s_new = get_mapping(r[1], r[2])
            if (r[1], r[2]) != (g_new, s_new):
                cat = next((c for n, t, c in GRUPOS_SEED if n == g_new), "Despesa")
                if not dry_run:
                    cur.execute(
                        "UPDATE journal_entries SET GRUPO=?, SUBGRUPO=?, CategoriaGeral=? WHERE id=?",
                        (g_new, s_new, cat, r[0]),
                    )
                je_updates += 1
        print(f"   {je_updates} transações atualizadas")

        if not dry_run:
            conn.commit()

        # 7. UPDATE budget_planning (mapear grupo e merge duplicatas)
        print("\n7. Atualizando budget_planning...")
        mapeamento_budget = {
            "Alimentação 2": "Alimentação",
            "Teste Criacao": "Outros",
            "Casa": "Moradia e Serviços",
            "Serviços": "Moradia e Serviços",
            "MeLi + Amazon": "Compras e Tecnologia",
            "Tecnologia": "Compras e Tecnologia",
            "Entretenimento": "Lazer",
            "Roupas": "Lazer",
            "Presentes": "Lazer",
            "Assinaturas": "Lazer",
        }
        if not dry_run:
            cur.execute("""
                CREATE TEMP TABLE budget_temp AS
                SELECT id, user_id, grupo, mes_referencia, valor_planejado, valor_medio_3_meses, cor, ativo, created_at, updated_at
                FROM budget_planning
            """)
            for g_old, g_new in mapeamento_budget.items():
                cur.execute("UPDATE budget_temp SET grupo=? WHERE grupo=?", (g_new, g_old))
            # Agrupar por user_id, grupo, mes e somar
            cur.execute("""
                SELECT user_id, grupo, mes_referencia,
                       SUM(valor_planejado) as total, MAX(valor_medio_3_meses) as valor_medio,
                       MAX(cor) as cor, MAX(ativo) as ativo
                FROM budget_temp
                GROUP BY user_id, grupo, mes_referencia
            """)
            novos = cur.fetchall()
            cur.execute("DELETE FROM budget_planning")
            for n in novos:
                cur.execute("""
                    INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, valor_medio_3_meses, cor, ativo, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (n[0], n[1], n[2], n[3], n[4] or 0, n[5], n[6] or 1))
            conn.commit()
        print(f"   Metas mapeadas e duplicatas mescladas")

        # 8. UPDATE base_padroes
        print("\n8. Atualizando base_padroes...")
        cur.execute("SELECT id, grupo_sugerido, subgrupo_sugerido FROM base_padroes")
        padroes = cur.fetchall()
        pad_updates = 0
        for p in padroes:
            g_new, s_new = get_mapping(p[1] or "", p[2] or "")
            if (p[1], p[2]) != (g_new, s_new):
                if not dry_run:
                    cur.execute(
                        "UPDATE base_padroes SET grupo_sugerido=?, subgrupo_sugerido=? WHERE id=?",
                        (g_new, s_new, p[0]),
                    )
                pad_updates += 1
        print(f"   {pad_updates} padrões atualizados")

        if not dry_run:
            conn.commit()

        # 9. UPDATE base_parcelas
        print("\n9. Atualizando base_parcelas...")
        cur.execute("SELECT id, grupo_sugerido, subgrupo_sugerido FROM base_parcelas")
        parcelas = cur.fetchall()
        par_updates = 0
        for p in parcelas:
            g_new, s_new = get_mapping(p[1] or "", p[2] or "")
            if (p[1], p[2]) != (g_new, s_new):
                if not dry_run:
                    cur.execute(
                        "UPDATE base_parcelas SET grupo_sugerido=?, subgrupo_sugerido=? WHERE id=?",
                        (g_new, s_new, p[0]),
                    )
                par_updates += 1
        print(f"   {par_updates} parcelas atualizadas")

        if not dry_run:
            conn.commit()

        # Validação
        print("\n" + "=" * 80)
        print("VALIDAÇÃO")
        print("=" * 80)
        cur.execute("SELECT COUNT(*) FROM base_grupos_config")
        print(f"   base_grupos_config: {cur.fetchone()[0]} grupos (esperado: 14)")
        cur.execute("SELECT COUNT(*) FROM base_marcacoes")
        print(f"   base_marcacoes: {cur.fetchone()[0]} combinações")
        cur.execute(
            "SELECT COUNT(*) FROM journal_entries j LEFT JOIN base_marcacoes m ON j.GRUPO=m.\"GRUPO\" AND j.SUBGRUPO=m.\"SUBGRUPO\" WHERE j.GRUPO IS NOT NULL AND m.id IS NULL"
        )
        orfaos = cur.fetchone()[0]
        print(f"   journal_entries órfãos (GRUPO/SUBGRUPO fora de base_marcacoes): {orfaos}")

        if dry_run:
            print("\n⚠️  DRY RUN - Nenhuma alteração foi persistida.")
            conn.rollback()
        else:
            print("\n✅ Migração concluída com sucesso!")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    run_migration(dry_run=dry)
