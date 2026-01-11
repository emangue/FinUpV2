#!/usr/bin/env python3
"""
Script para recalcular todas as médias dos últimos 3 meses no budget_planning
Usa MesFatura + IgnorarDashboard para cálculo correto
"""
import sys
from pathlib import Path

# Adicionar app_dev ao path
sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.core.database import SessionLocal
from app.domains.budget.models import BudgetPlanning
from app.domains.budget.service import BudgetService
from app.domains.upload.history_models import UploadHistory  # Importar para resolver relationship

def recalcular_todas_medias():
    """Recalcula valor_medio_3_meses para todos os registros de budget_planning"""
    db = SessionLocal()
    
    try:
        # Buscar todos os budgets
        budgets = db.query(BudgetPlanning).all()
        
        print(f"📊 Encontrados {len(budgets)} registros de budget_planning")
        print("🔄 Recalculando médias...\n")
        
        service = BudgetService(db)
        atualizados = 0
        
        for budget in budgets:
            # Calcular nova média
            nova_media = service.calcular_media_3_meses(
                user_id=budget.user_id,
                tipo_gasto=budget.tipo_gasto,
                mes_referencia=budget.mes_referencia
            )
            
            # Atualizar se mudou
            if budget.valor_medio_3_meses != nova_media:
                print(f"  • {budget.tipo_gasto} - {budget.mes_referencia}")
                print(f"    Antes: R$ {budget.valor_medio_3_meses:.2f}")
                print(f"    Depois: R$ {nova_media:.2f}")
                
                budget.valor_medio_3_meses = nova_media
                atualizados += 1
        
        # Commit das mudanças
        db.commit()
        
        print(f"\n✅ Recálculo concluído!")
        print(f"   Total de registros: {len(budgets)}")
        print(f"   Atualizados: {atualizados}")
        print(f"   Sem mudança: {len(budgets) - atualizados}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro ao recalcular médias: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Recálculo de Médias - Budget Planning")
    print("=" * 60)
    print()
    
    recalcular_todas_medias()
