#!/usr/bin/env python3
"""
Sincroniza budget_planning a partir de journal_entries (Despesa + Investimentos).

Cria linhas com valor_planejado=0 para (grupo, mes) que têm transações mas não estão em budget_planning.
Mesma lógica da Fase 6 do upload (confirm_upload).

Uso:
  cd app_dev/backend
  python scripts/sync_budget_planning_from_journal.py [--user-id USER_ID]

Se --user-id não for informado, processa todos os usuários.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Adicionar backend ao PYTHONPATH (como check_users.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.domains.transactions.models import JournalEntry
from app.domains.budget.models import BudgetPlanning
from app.domains.upload.history_models import UploadHistory  # Necessário para relationship JournalEntry


def sync_budget_planning(user_id: Optional[int] = None) -> dict:
    """Sincroniza budget_planning. Retorna {user_id: criados}."""
    db = SessionLocal()
    try:
        # Grupos (grupo, mes_fatura) com Despesa OU Investimentos
        q = db.query(JournalEntry.user_id, JournalEntry.GRUPO, JournalEntry.MesFatura).filter(
            JournalEntry.CategoriaGeral.in_(['Despesa', 'Investimentos']),
            JournalEntry.IgnorarDashboard == 0,
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.GRUPO != '',
            JournalEntry.MesFatura.isnot(None)
        ).distinct()
        if user_id is not None:
            q = q.filter(JournalEntry.user_id == user_id)
        rows = q.all()

        seen = set()
        to_create = []
        for r in rows:
            uid, grupo, mes_fatura = r.user_id, r.GRUPO, r.MesFatura
            if not grupo or not mes_fatura or len(str(mes_fatura)) != 6:
                continue
            key = (uid, grupo, mes_fatura)
            if key in seen:
                continue
            seen.add(key)
            mes_ref = f"{str(mes_fatura)[:4]}-{str(mes_fatura)[4:6]}"
            to_create.append((uid, grupo, mes_ref))

        criados_por_user = {}
        for uid, grupo, mes_ref in to_create:
            existente = db.query(BudgetPlanning).filter(
                BudgetPlanning.user_id == uid,
                BudgetPlanning.grupo == grupo,
                BudgetPlanning.mes_referencia == mes_ref
            ).first()
            if not existente:
                novo = BudgetPlanning(
                    user_id=uid,
                    grupo=grupo,
                    mes_referencia=mes_ref,
                    valor_planejado=0.0,
                    valor_medio_3_meses=0.0,
                    ativo=1
                )
                db.add(novo)
                criados_por_user[uid] = criados_por_user.get(uid, 0) + 1

        if criados_por_user:
            db.commit()
        return criados_por_user
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Sincroniza budget_planning a partir de journal_entries')
    parser.add_argument('--user-id', type=int, help='ID do usuário (opcional, processa todos se omitido)')
    args = parser.parse_args()

    print("Sincronizando budget_planning (Despesa + Investimentos)...")
    criados = sync_budget_planning(user_id=args.user_id)
    if criados:
        for uid, n in criados.items():
            print(f"  User {uid}: {n} linhas criadas")
    else:
        print("  Nenhuma linha nova criada (tudo já estava em budget_planning)")


if __name__ == '__main__':
    main()
