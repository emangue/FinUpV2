"""
Migration: Add budget_geral table for general budget categories

Creates budget_geral table to store high-level budget goals
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, text
from sqlalchemy.sql import func
from datetime import datetime


def upgrade():
    """Create budget_geral table"""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS budget_geral (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                categoria_geral TEXT NOT NULL,
                mes_referencia TEXT NOT NULL,
                valor_planejado REAL NOT NULL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, categoria_geral, mes_referencia)
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_budget_geral_user_mes 
            ON budget_geral(user_id, mes_referencia);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_budget_geral_categoria 
            ON budget_geral(categoria_geral);
        """))
        
        print("✅ Table budget_geral created successfully")


def downgrade():
    """Drop budget_geral table"""
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS budget_geral;"))
        print("✅ Table budget_geral dropped")


if __name__ == "__main__":
    print("🚀 Running migration: add_budget_geral_table")
    upgrade()
    print("✅ Migration completed successfully")
