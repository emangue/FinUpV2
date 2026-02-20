#!/usr/bin/env python3
"""
Testa pipeline de upload diretamente no servidor (sem API).
Simula Fase 1→2→3 para fatura-202601.csv e verifica IdParcela/Base Parcelas.
Executar na VM: cd /var/www/finup && python3 scripts/diagnostic/test_upload_pipeline_server.py
"""
import sys
import os
from pathlib import Path

# Setup path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "app_dev" / "backend"))
os.chdir(ROOT / "app_dev" / "backend")

# CSV de teste (mesmo formato do fatura-202601.csv)
CSV_CONTENT = """data,lançamento,valor
2025-06-20,PRODUTOS GLOBO    07/12,59.9
2025-05-11,WINE.COM.BR*52723 09/12,73.18
2025-12-07,VIVARA XVL        02/03,135.34
"""

def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    from app.domains.upload.processors.raw.registry import get_processor
    from app.domains.upload.processors.marker import TransactionMarker, extrair_parcela_do_estabelecimento
    from app.domains.upload.processors.classifier import CascadeClassifier
    from app.domains.transactions.models import BaseParcelas
    
    DB_PATH = ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("=" * 60)
    print("TESTE PIPELINE UPLOAD - Base Parcelas")
    print("=" * 60)
    
    # Salvar CSV temporário
    csv_path = Path("/tmp/fatura-test-pipeline.csv")
    csv_path.write_text(CSV_CONTENT)
    
    # Fase 1: Raw
    print("\n1. FASE 1 - Raw Processing")
    processor = get_processor("itau", "fatura", "csv")
    if not processor:
        print("   ❌ Processador não encontrado!")
        return 1
    raw_list = processor(csv_path, "fatura-202601.csv", "Azul", "1234")
    print(f"   ✅ {len(raw_list)} transações brutas")
    for i, r in enumerate(raw_list[:5]):
        print(f"      [{i}] {r.lancamento[:45]:45} | R$ {r.valor}")
    
    # Fase 2: Marker (user_id=1 e user_id=4)
    print("\n2. FASE 2 - ID Marking")
    for user_id in [1, 4]:
        marker = TransactionMarker(user_id=user_id)
        for raw in raw_list:
            marked = marker.mark_transaction(raw)
            if marked.id_parcela:
                print(f"   user_id={user_id}: {marked.estabelecimento_base[:35]:35} | IdParcela={marked.id_parcela}")
    
    # Fase 3: Classifier - verificar match com base_parcelas
    print("\n3. FASE 3 - Classification (user_id=1)")
    marker = TransactionMarker(user_id=1)
    classifier = CascadeClassifier(db, user_id=1)
    base_parcelas_count = 0
    for raw in raw_list:
        marked = marker.mark_transaction(raw)
        classified = classifier.classify(marked)
        if classified.origem_classificacao == "Base Parcelas":
            base_parcelas_count += 1
            print(f"   ✅ Base Parcelas: {marked.estabelecimento_base[:40]} | {classified.grupo}/{classified.subgrupo}")
        elif marked.id_parcela:
            # Tem IdParcela mas não deu match
            parcela_in_db = db.query(BaseParcelas).filter(
                BaseParcelas.id_parcela == marked.id_parcela,
                BaseParcelas.user_id == 1
            ).first()
            print(f"   ❌ IdParcela={marked.id_parcela} mas origem={classified.origem_classificacao}")
            print(f"      Existe em base_parcelas? {parcela_in_db is not None}")
    
    print(f"\n   Total Base Parcelas: {base_parcelas_count}")
    
    # Verificar base_parcelas
    print("\n4. base_parcelas PRODUTOS GLOBO (user 1):")
    parcelas = db.query(BaseParcelas).filter(
        BaseParcelas.estabelecimento_base.like("%GLOBO%"),
        BaseParcelas.user_id == 1
    ).all()
    for p in parcelas:
        print(f"   id_parcela={p.id_parcela} | R${p.valor_parcela} | {p.qtd_parcelas}x")
    
    db.close()
    csv_path.unlink(missing_ok=True)
    print("\n" + "=" * 60)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
