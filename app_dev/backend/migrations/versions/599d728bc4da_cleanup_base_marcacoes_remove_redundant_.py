"""cleanup_base_marcacoes_remove_redundant_fields

Revision ID: 599d728bc4da
Revises: 635e060a2434
Create Date: 2026-02-13 19:44:51.734014

OBJETIVO: Remover campos redundantes TipoGasto e CategoriaGeral de base_marcacoes
          A marcação única é GRUPO + SUBGRUPO
          TipoGasto/CategoriaGeral devem vir de base_grupos_config via JOIN

CONTEXTO:
- base_marcacoes: 405 registros (20 grupos, 213 subgrupos)
- Inconsistências: Alimentação tinha 4 TipoGasto diferentes
- journal_entries: 7,722 transações usam TipoGasto (vem de grupos_config, não marcacoes)
- Fonte oficial: base_grupos_config.tipo_gasto_padrao e categoria_geral

IMPACTO:
- Remove 2 colunas de base_marcacoes (TipoGasto, CategoriaGeral)
- Código deve fazer JOIN com base_grupos_config para pegar esses dados
- Reduz duplicação e previne inconsistências
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '599d728bc4da'
down_revision: Union[str, Sequence[str], None] = '635e060a2434'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove campos redundantes de base_marcacoes.
    Marcação única = GRUPO + SUBGRUPO apenas.
    TipoGasto/CategoriaGeral vêm de base_grupos_config.
    """
    print("🔍 Validando integridade antes da limpeza...")
    
    # 1. Validar: todos os grupos existem em base_grupos_config?
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT COUNT(*) as orfaos
        FROM base_marcacoes m
        LEFT JOIN base_grupos_config g ON m."GRUPO" = g.nome_grupo
        WHERE g.nome_grupo IS NULL
    """))
    orfaos = result.fetchone()[0]
    
    if orfaos > 0:
        raise Exception(
            f"❌ ERRO: {orfaos} grupos em base_marcacoes não têm config em base_grupos_config. "
            f"Execute INSERT INTO base_grupos_config para esses grupos antes da migration."
        )
    
    print(f"   ✅ Todos os grupos têm config em base_grupos_config")
    
    # 2. Log de inconsistências (opcional - apenas informativo)
    result = conn.execute(sa.text("""
        SELECT 
            m."GRUPO",
            COUNT(DISTINCT m."TipoGasto") as tipos_diferentes
        FROM base_marcacoes m
        GROUP BY m."GRUPO"
        HAVING COUNT(DISTINCT m."TipoGasto") > 1
    """))
    inconsistencias = result.fetchall()
    
    if inconsistencias:
        print(f"   ⚠️  {len(inconsistencias)} grupos com múltiplos TipoGasto (serão removidos):")
        for grupo, count in inconsistencias[:5]:  # Mostrar só 5 primeiros
            print(f"      - {grupo}: {count} valores diferentes")
    
    # 3. Remover colunas redundantes (SQLite não suporta DROP COLUMN direto)
    print("\n🗑️  Removendo colunas redundantes...")
    print("   Criando tabela temporária sem TipoGasto e CategoriaGeral...")
    
    # SQLite workaround: criar nova tabela, copiar dados, drop antiga, rename
    conn.execute(sa.text("""
        CREATE TABLE base_marcacoes_new (
            id INTEGER NOT NULL PRIMARY KEY,
            "GRUPO" VARCHAR(100) NOT NULL,
            "SUBGRUPO" VARCHAR(100) NOT NULL
        )
    """))
    
    print("   Copiando dados (GRUPO + SUBGRUPO apenas)...")
    conn.execute(sa.text("""
        INSERT INTO base_marcacoes_new (id, "GRUPO", "SUBGRUPO")
        SELECT id, "GRUPO", "SUBGRUPO"
        FROM base_marcacoes
    """))
    
    print("   Removendo tabela antiga...")
    conn.execute(sa.text("DROP TABLE base_marcacoes"))
    
    print("   Renomeando nova tabela...")
    conn.execute(sa.text("ALTER TABLE base_marcacoes_new RENAME TO base_marcacoes"))
    
    print("\n✅ Migration completa!")
    print("   base_marcacoes agora tem apenas: id, GRUPO, SUBGRUPO")
    print("   📝 Código deve fazer JOIN com base_grupos_config para TipoGasto/CategoriaGeral")


def downgrade() -> None:
    """
    Restaura colunas TipoGasto e CategoriaGeral populando de base_grupos_config.
    """
    print("⚠️  Downgrade: Recriando colunas TipoGasto e CategoriaGeral...")
    
    conn = op.get_bind()
    
    # Recriar tabela com colunas
    print("   Criando tabela temporária com todas as colunas...")
    conn.execute(sa.text("""
        CREATE TABLE base_marcacoes_new (
            id INTEGER NOT NULL PRIMARY KEY,
            "GRUPO" VARCHAR(100) NOT NULL,
            "SUBGRUPO" VARCHAR(100) NOT NULL,
            "TipoGasto" VARCHAR(100),
            "CategoriaGeral" VARCHAR(100)
        )
    """))
    
    print("   Copiando dados e populando de base_grupos_config...")
    conn.execute(sa.text("""
        INSERT INTO base_marcacoes_new (id, "GRUPO", "SUBGRUPO", "TipoGasto", "CategoriaGeral")
        SELECT 
            m.id,
            m."GRUPO",
            m."SUBGRUPO",
            COALESCE(g.tipo_gasto_padrao, 'Ajustável') as "TipoGasto",
            COALESCE(g.categoria_geral, 'Despesa') as "CategoriaGeral"
        FROM base_marcacoes m
        LEFT JOIN base_grupos_config g ON m."GRUPO" = g.nome_grupo
    """))
    
    print("   Substituindo tabela...")
    conn.execute(sa.text("DROP TABLE base_marcacoes"))
    conn.execute(sa.text("ALTER TABLE base_marcacoes_new RENAME TO base_marcacoes"))
    
    print("✅ Downgrade completo (dados recriados de base_grupos_config)")
