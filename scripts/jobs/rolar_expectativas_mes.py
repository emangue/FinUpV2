#!/usr/bin/env python3
"""
Job: Garantir expectativas_mes tem os próximos 12 meses materializados.
Executar diariamente (cron) ou após deploy.

Para cada expectativa em base_expectativas (status=pendente) com metadata_json:
- Lê recorrencia do metadata
- Expande para os próximos 12 meses a partir de hoje
- Faz UPSERT em expectativas_mes (delete + insert por origem_expectativa_id)

Uso: cd app_dev/backend && python ../../scripts/jobs/rolar_expectativas_mes.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "app_dev" / "backend"))

from app.core.database import SessionLocal
from app.domains.plano.models import BaseExpectativa, ExpectativaMes
from app.domains.plano.service import PlanoService

def main():
    db = SessionLocal()
    try:
        svc = PlanoService(db)
        pendentes = db.query(BaseExpectativa).filter(BaseExpectativa.status == "pendente").all()
        total_inseridos = 0
        for e in pendentes:
            metadata = {}
            if e.metadata_json:
                try:
                    metadata = json.loads(e.metadata_json)
                except (json.JSONDecodeError, TypeError):
                    pass
            recorrencia = metadata.get("recorrencia", "unico")
            meses = svc._expandir_meses_recorrencia(e.mes_referencia, recorrencia)
            db.query(ExpectativaMes).filter(
                ExpectativaMes.origem_expectativa_id == e.id,
            ).delete(synchronize_session=False)
            for mes_ref in meses:
                em = ExpectativaMes(
                    user_id=e.user_id,
                    mes_referencia=mes_ref,
                    grupo=e.grupo,
                    subgrupo=e.subgrupo,
                    tipo=e.tipo_lancamento or "debito",
                    valor=e.valor,
                    origem_expectativa_id=e.id,
                )
                db.add(em)
                total_inseridos += 1
        db.commit()
        print(f"✅ Rolagem concluída: {len(pendentes)} expectativas, {total_inseridos} linhas em expectativas_mes")
    finally:
        db.close()


if __name__ == "__main__":
    main()
