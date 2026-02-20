#!/usr/bin/env python3
"""
Verifica se o IdParcela gerado pelo marker é IGUAL ao id_parcela na base_parcelas.

Executa:
1. Marker gera IdParcela para PRODUTOS GLOBO 07/12 (user_id=1)
2. Busca em base_parcelas por user_id=1
3. Compara: id gerado == id na base?

Uso:
  Local:  cd app_dev/backend && python ../../scripts/diagnostic/verificar_marker_vs_base.py
  Server: cd /var/www/finup && source app_dev/backend/venv/bin/activate && python scripts/diagnostic/verificar_marker_vs_base.py
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# CSV com PRODUTOS GLOBO (igual fatura-202601.csv)
CSV_LINE = "2025-06-20,PRODUTOS GLOBO    07/12,59.9"


def main():
    from sqlalchemy.orm import sessionmaker
    from app.core.database import engine
    from app.domains.upload.processors.raw.registry import get_processor
    from app.domains.upload.processors.marker import TransactionMarker
    from app.domains.transactions.models import BaseParcelas

    Session = sessionmaker(bind=engine)
    db = Session()

    print("=" * 70)
    print("VERIFICAÇÃO: Marker IdParcela vs base_parcelas.id_parcela")
    print("=" * 70)

    # Fase 1: Raw
    csv_path = Path("/tmp/verif_marker.csv")
    csv_path.write_text("data,lançamento,valor\n" + CSV_LINE)

    processor = get_processor("itau", "fatura", "csv")
    if not processor:
        print("❌ Processador não encontrado")
        return 1

    raw_list = processor(csv_path, "fatura-202601.csv", "Azul", "1234")
    if not raw_list:
        print("❌ Nenhuma transação raw")
        return 1

    raw = raw_list[0]
    print(f"\n1. Transação raw: {raw.lancamento} | R$ {raw.valor}")

    # Fase 2: Marker (user_id=1)
    marker = TransactionMarker(user_id=1)
    marked = marker.mark_transaction(raw)

    id_gerado = marked.id_parcela
    estab_base = marked.estabelecimento_base
    total = marked.total_parcelas

    print(f"\n2. Marker (user_id=1):")
    print(f"   estabelecimento_base: '{estab_base}'")
    print(f"   total_parcelas: {total}")
    print(f"   IdParcela GERADO: {id_gerado}")

    # Buscar em base_parcelas
    parcelas_user1 = db.query(BaseParcelas).filter(
        BaseParcelas.user_id == 1,
        BaseParcelas.estabelecimento_base.ilike("%GLOBO%")
    ).all()

    print(f"\n3. base_parcelas (user_id=1, GLOBO):")
    if not parcelas_user1:
        print("   ❌ Nenhuma parcela encontrada para PRODUTOS GLOBO!")
        print("   → Por isso Base Parcelas = 0 no preview")
        db.close()
        csv_path.unlink(missing_ok=True)
        return 1

    match_exato = False
    for p in parcelas_user1:
        status = "✅ IGUAL" if p.id_parcela == id_gerado else "❌ DIFERENTE"
        if p.id_parcela == id_gerado:
            match_exato = True
        print(f"   id_parcela na base: {p.id_parcela} | {status}")
        print(f"      valor: R$ {p.valor_parcela} | {p.qtd_parcelas}x")

    print(f"\n4. RESULTADO:")
    if match_exato:
        print("   ✅ Marker gera IdParcela IGUAL ao da base → classificação deve funcionar")
    else:
        print("   ❌ Marker gera IdParcela DIFERENTE do que está na base!")
        print("   → Possível causa: base_parcelas foi populada com fórmula antiga (sem user_id)")
        print("   → Solução: rodar fix_id_parcela_vm.py para recalcular id_parcela na base")

    db.close()
    csv_path.unlink(missing_ok=True)
    print("\n" + "=" * 70)
    return 0 if match_exato else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
