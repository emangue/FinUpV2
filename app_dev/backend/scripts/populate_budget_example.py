"""
Script para popular budget_planning com dados de exemplo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dados de exemplo para Novembro/2025
BUDGET_DATA = [
    {"tipo_gasto": "Fixo", "valor": 10000.00},
    {"tipo_gasto": "Ajustável", "valor": 15000.00},
    {"tipo_gasto": "Ajustável - Casa", "valor": 1000.00},
    {"tipo_gasto": "Ajustável - Delivery", "valor": 500.00},
    {"tipo_gasto": "Ajustável - Saídas", "valor": 2000.00},
    {"tipo_gasto": "Ajustável - Uber", "valor": 600.00},
    {"tipo_gasto": "Ajustável - Viagens", "valor": 1500.00},
    {"tipo_gasto": "Ajustável - Supermercado", "valor": 800.00},
    {"tipo_gasto": "Ajustável - Roupas", "valor": 1500.00},
    {"tipo_gasto": "Ajustável - Presentes", "valor": 800.00},
    {"tipo_gasto": "Ajustável - Assinaturas", "valor": 800.00},
    {"tipo_gasto": "Ajustável - Carro", "valor": 2000.00},
    {"tipo_gasto": "Ajustável - Doações", "valor": 2000.00},
    {"tipo_gasto": "Ajustável - Esportes", "valor": 1000.00},
]


def populate_budget():
    """Popula tabela budget_planning com dados de exemplo"""
    try:
        logger.info("🚀 Populando budget_planning com dados de exemplo...")
        
        with engine.begin() as conn:
            # Limpar dados anteriores de novembro/2025 para usuário 1
            conn.execute(text("""
                DELETE FROM budget_planning 
                WHERE user_id = 1 AND mes_referencia = '2025-11'
            """))
            
            for budget in BUDGET_DATA:
                # Inserir novo registro
                conn.execute(text("""
                    INSERT INTO budget_planning (user_id, tipo_gasto, mes_referencia, valor_planejado)
                    VALUES (1, :tipo_gasto, '2025-11', :valor)
                """), {
                    "tipo_gasto": budget["tipo_gasto"],
                    "valor": budget["valor"]
                })
                logger.info(f"  ✅ {budget['tipo_gasto']}: R$ {budget['valor']:.2f}")
        
        logger.info(f"✅ {len(BUDGET_DATA)} registros inseridos com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao popular dados: {e}")
        raise


if __name__ == "__main__":
    populate_budget()
