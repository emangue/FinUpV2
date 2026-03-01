#!/usr/bin/env python3
"""
Backfill expectativas_mes a partir de base_expectativas.
Executar uma vez após deploy da migration m8n9o0p1q2r3.

Uso (com SQLite local):
  cd app_dev/backend && python -c "
  from app.core.database import SessionLocal
  from app.domains.plano.models import BaseExpectativa, ExpectativaMes
  db = SessionLocal()
  for e in db.query(BaseExpectativa).filter(BaseExpectativa.status == 'pendente').all():
      if not db.query(ExpectativaMes).filter(ExpectativaMes.origem_expectativa_id == e.id).first():
          em = ExpectativaMes(user_id=e.user_id, mes_referencia=e.mes_referencia, grupo=e.grupo,
              subgrupo=e.subgrupo, tipo=e.tipo_lancamento or 'debito', valor=e.valor,
              origem_expectativa_id=e.id)
          db.add(em)
  db.commit()
  print('Backfill concluído')
  "
"""
