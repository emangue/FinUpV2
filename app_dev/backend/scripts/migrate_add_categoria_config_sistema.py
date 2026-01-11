"""
Migration: Add budget categoria config system

Creates:
1. budget_categoria_config - User-customizable budget categories with drag & drop ordering
2. budget_geral_historico - Audit log for automatic budget adjustments
3. categoria_orcamento_id column in journal_entries - Performance optimization
4. Seed default categories for all users
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, get_db
from sqlalchemy import text
from datetime import datetime


def upgrade():
    """Create tables and add column"""
    with engine.begin() as conn:
        # 1. Create budget_categoria_config table
        print("📋 Creating budget_categoria_config table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS budget_categoria_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nome_categoria TEXT NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 999,
                fonte_dados TEXT NOT NULL CHECK(fonte_dados IN ('GRUPO', 'TIPO_TRANSACAO')),
                filtro_valor TEXT NOT NULL,
                tipos_gasto_incluidos TEXT,
                cor_visualizacao TEXT NOT NULL DEFAULT '#94a3b8',
                ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, nome_categoria)
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_categoria_config_user_ordem 
            ON budget_categoria_config(user_id, ordem);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_categoria_config_ativo 
            ON budget_categoria_config(ativo);
        """))
        
        print("✅ Table budget_categoria_config created")
        
        # 2. Create budget_geral_historico table
        print("📋 Creating budget_geral_historico table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS budget_geral_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mes_referencia TEXT NOT NULL,
                valor_anterior REAL NOT NULL,
                valor_novo REAL NOT NULL,
                motivo TEXT NOT NULL,
                soma_categorias REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_historico_user_mes 
            ON budget_geral_historico(user_id, mes_referencia);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_historico_created 
            ON budget_geral_historico(created_at);
        """))
        
        print("✅ Table budget_geral_historico created")
        
        # 3. Add categoria_orcamento_id column to journal_entries
        print("📋 Adding categoria_orcamento_id column to journal_entries...")
        try:
            conn.execute(text("""
                ALTER TABLE journal_entries 
                ADD COLUMN categoria_orcamento_id INTEGER;
            """))
            print("✅ Column categoria_orcamento_id added")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️  Column categoria_orcamento_id already exists")
            else:
                raise
        
        # Create index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_journal_categoria_orcamento 
            ON journal_entries(categoria_orcamento_id);
        """))
        
        # 4. Add total_mensal column to budget_geral
        print("📋 Adding total_mensal column to budget_geral...")
        try:
            conn.execute(text("""
                ALTER TABLE budget_geral 
                ADD COLUMN total_mensal REAL;
            """))
            print("✅ Column total_mensal added")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️  Column total_mensal already exists")
            else:
                raise


def seed_default_categories():
    """Seed default budget categories for all existing users"""
    print("\n🌱 Seeding default categories...")
    
    # Default categories configuration
    default_categories = [
        {
            "nome_categoria": "Casa",
            "ordem": 1,
            "fonte_dados": "GRUPO",
            "filtro_valor": "Moradia",
            "tipos_gasto_incluidos": json.dumps(["Ajustável - Casa"]),
            "cor_visualizacao": "#10b981"  # Green
        },
        {
            "nome_categoria": "Cartão de Crédito",
            "ordem": 2,
            "fonte_dados": "TIPO_TRANSACAO",
            "filtro_valor": "Cartão",
            "tipos_gasto_incluidos": json.dumps([
                "Ajustável",
                "Fixo",
                "Ajustável - Delivery",
                "Ajustável - Saídas",
                "Ajustável - Supermercado",
                "Ajustável - Roupas",
                "Ajustável - Presentes",
                "Ajustável - Assinaturas",
                "Ajustável - Tech"
            ]),
            "cor_visualizacao": "#ef4444"  # Red
        },
        {
            "nome_categoria": "Doações",
            "ordem": 3,
            "fonte_dados": "GRUPO",
            "filtro_valor": "Doações",
            "tipos_gasto_incluidos": json.dumps(["Ajustável - Doações"]),
            "cor_visualizacao": "#8b5cf6"  # Purple
        },
        {
            "nome_categoria": "Saúde",
            "ordem": 4,
            "fonte_dados": "GRUPO",
            "filtro_valor": "Saúde",
            "tipos_gasto_incluidos": json.dumps(["Ajustável - Esportes"]),
            "cor_visualizacao": "#06b6d4"  # Cyan
        },
        {
            "nome_categoria": "Viagens",
            "ordem": 5,
            "fonte_dados": "GRUPO",
            "filtro_valor": "Viagens",
            "tipos_gasto_incluidos": json.dumps(["Ajustável - Viagens"]),
            "cor_visualizacao": "#f59e0b"  # Amber
        },
        {
            "nome_categoria": "Outros",
            "ordem": 6,
            "fonte_dados": "GRUPO",
            "filtro_valor": "Outros",
            "tipos_gasto_incluidos": json.dumps(["Ajustável - Carro", "Ajustável - Uber"]),
            "cor_visualizacao": "#94a3b8"  # Slate
        }
    ]
    
    with engine.begin() as conn:
        # Get all user IDs
        result = conn.execute(text("SELECT id FROM users"))
        user_ids = [row[0] for row in result]
        
        if not user_ids:
            print("⚠️  No users found, skipping seed")
            return
        
        # Insert default categories for each user
        for user_id in user_ids:
            for cat in default_categories:
                conn.execute(text("""
                    INSERT OR IGNORE INTO budget_categoria_config 
                    (user_id, nome_categoria, ordem, fonte_dados, filtro_valor, tipos_gasto_incluidos, cor_visualizacao, ativo)
                    VALUES (:user_id, :nome_categoria, :ordem, :fonte_dados, :filtro_valor, :tipos_gasto_incluidos, :cor_visualizacao, 1)
                """), {
                    "user_id": user_id,
                    **cat
                })
            
            print(f"✅ Seeded categories for user {user_id}")


def downgrade():
    """Drop tables and column"""
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS budget_geral_historico;"))
        conn.execute(text("DROP TABLE IF EXISTS budget_categoria_config;"))
        # Note: SQLite doesn't support DROP COLUMN easily, would need table recreation
        print("⚠️  Note: categoria_orcamento_id column not removed (SQLite limitation)")
        print("✅ Tables dropped")


if __name__ == "__main__":
    import sys
    
    print("🚀 Running migration: add_categoria_config_sistema")
    upgrade()
    
    # Ask user if want to seed
    if "--no-seed" not in sys.argv:
        seed_default_categories()
    
    print("✅ Migration completed successfully")
