#!/usr/bin/env python3
"""
Backfill expectativas_mes a partir de base_expectativas.
Executar uma vez após a migration m8n9o0p1q2r3 (ou migrate_expectativas_mes_sqlite.py).

Uso: cd app_dev/backend && python ../../scripts/migration/backfill_expectativas_mes.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "app_dev" / "backend"))

from app.core.database import SessionLocal
from app.domains.plano.models import BaseExpectativa, ExpectativaMes


def main():
    db = SessionLocal()
    try:
        pendentes = db.query(BaseExpectativa).filter(BaseExpectativa.status == "pendente").all()
        inseridos = 0
        for e in pendentes:
            existe = db.query(ExpectativaMes).filter(
                ExpectativaMes.origem_expectativa_id == e.id,
            ).first()
            if not existe:
                em = ExpectativaMes(
                    user_id=e.user_id,
                    mes_referencia=e.mes_referencia,
                    grupo=e.grupo,
                    subgrupo=getattr(e, "subgrupo", None),
                    tipo=e.tipo_lancamento or "debito",
                    valor=e.valor,
                    origem_expectativa_id=e.id,
                )
                db.add(em)
                inseridos += 1
        db.commit()
        print(f"✅ Backfill concluído: {inseridos} expectativas materializadas (de {len(pendentes)} pendentes)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
