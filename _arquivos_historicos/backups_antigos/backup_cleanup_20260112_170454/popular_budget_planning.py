#!/usr/bin/env python3
"""
Script para popular budget_planning com médias pré-calculadas
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar app_dev ao path
sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.core.database import SessionLocal
from app.domains.budget.models import BudgetPlanning
from app.domains.budget.service import BudgetService
from app.domains.transactions.models import JournalEntry
from sqlalchemy import func, distinct

def popular_budget_planning():
    """Popula budget_planning com médias para todos os tipos de gasto"""
    db = SessionLocal()
    
    try:
        # Buscar todos os tipos de gasto únicos e meses únicos do banco
        tipos_gasto = db.query(distinct(JournalEntry.TipoGasto)).filter(
            JournalEntry.TipoGasto.isnot(None),
            JournalEntry.TipoGasto != ''
        ).all()
        
        meses = db.query(distinct(JournalEntry.MesFatura)).filter(
            JournalEntry.MesFatura.isnot(None),
            JournalEntry.MesFatura != ''
        ).all()
        
        print(f"📊 Encontrados {len(tipos_gasto)} tipos de gasto")
        print(f"📅 Encontrados {len(meses)} meses")
        print("🔄 Populando budget_planning...\n")
        
        service = BudgetService(db)
        user_id = 1  # Admin padrão
        inseridos = 0
        atualizados = 0
        
        # Converter meses de YYYYMM para YYYY-MM
        meses_formatados = []
        for (mes_fatura,) in meses:
            if mes_fatura and len(mes_fatura) == 6:
                ano = mes_fatura[:4]
                mes = mes_fatura[4:6]
                meses_formatados.append(f"{ano}-{mes}")
        
        meses_formatados = sorted(set(meses_formatados))
        
        for (tipo_gasto,) in tipos_gasto:
            for mes_referencia in meses_formatados:
                # Verificar se já existe
                existing = db.query(BudgetPlanning).filter(
                    BudgetPlanning.user_id == user_id,
                    BudgetPlanning.tipo_gasto == tipo_gasto,
                    BudgetPlanning.mes_referencia == mes_referencia
                ).first()
                
                # Calcular média
                media = service.calcular_media_3_meses(user_id, tipo_gasto, mes_referencia)
                
                if media > 0:  # Só inserir se houver média
                    if existing:
                        # Atualizar
                        existing.valor_medio_3_meses = media
                        existing.updated_at = datetime.now()
                        atualizados += 1
                    else:
                        # Inserir novo
                        budget = BudgetPlanning(
                            user_id=user_id,
                            tipo_gasto=tipo_gasto,
                            mes_referencia=mes_referencia,
                            valor_planejado=None,
                            valor_medio_3_meses=media
                        )
                        db.add(budget)
                        inseridos += 1
                    
                    if (inseridos + atualizados) % 50 == 0:
                        print(f"  Processados: {inseridos + atualizados}")
                        db.commit()
        
        # Commit final
        db.commit()
        
        print(f"\n✅ Processo concluído!")
        print(f"   Inseridos: {inseridos}")
        print(f"   Atualizados: {atualizados}")
        print(f"   Total: {inseridos + atualizados}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro ao popular budget_planning: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Popular Budget Planning")
    print("=" * 60)
    print()
    
    popular_budget_planning()
