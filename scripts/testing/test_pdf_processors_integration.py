"""
Script de validação dos processadores PDF integrados ao sistema
Testa extração de transações e validação de saldos
"""

import sys
from pathlib import Path

# Ajustar path para imports
sys.path.insert(0, str(Path(__file__).parent / "app_dev" / "backend"))

from app.domains.upload.processors.raw.registry import get_processor
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_processor(banco: str, tipo: str, formato: str, file_path: Path):
    """Testa um processador específico"""
    print(f"\n{'='*70}")
    print(f"🔍 Testando: {banco} / {tipo} / {formato}")
    print(f"📄 Arquivo: {file_path.name}")
    print(f"{'='*70}")
    
    # Buscar processador
    processor = get_processor(banco, tipo, formato)
    
    if not processor:
        print(f"❌ Processador não encontrado para: {banco}/{tipo}/{formato}")
        return False
    
    print(f"✅ Processador encontrado!")
    
    # Processar arquivo
    try:
        # Extrair parâmetros do nome do arquivo
        nome_arquivo = file_path.name
        nome_cartao = "Mastercard Black" if tipo == "fatura" else None
        final_cartao = "1234" if tipo == "fatura" else None
        
        # Processar
        transactions = processor(
            file_path=file_path,
            nome_arquivo=nome_arquivo,
            nome_cartao=nome_cartao,
            final_cartao=final_cartao
        )
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Total de transações: {len(transactions)}")
        
        if transactions:
            # Calcular soma
            soma_total = sum(t.valor for t in transactions)
            print(f"   💰 Soma total: R$ {soma_total:,.2f}")
            
            # Mostrar primeiras 5
            print(f"\n📋 Primeiras 5 transações:")
            for i, t in enumerate(transactions[:5], 1):
                print(f"   {i}. {t.data} | {t.lancamento[:50]:50s} | R$ {t.valor:10.2f}")
            
            # Mostrar últimas 3
            if len(transactions) > 5:
                print(f"\n📋 Últimas 3 transações:")
                for i, t in enumerate(transactions[-3:], len(transactions)-2):
                    print(f"   {i}. {t.data} | {t.lancamento[:50]:50s} | R$ {t.valor:10.2f}")
        
        print(f"\n✅ Processamento concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO ao processar: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Testa todos os processadores PDF"""
    base_path = Path("_arquivos_historicos/_csvs_historico")
    
    # Definir testes
    tests = [
        # Itaú Extrato
        ("itau", "extrato", "pdf", base_path / "extrato-itau-2025.pdf"),
        
        # Itaú Fatura
        ("itau", "fatura", "pdf", base_path / "fatura-202509.pdf"),
        ("itau", "fatura", "pdf", base_path / "fatura-202510.pdf"),
        ("itau", "fatura", "pdf", base_path / "fatura-202511.pdf"),
        ("itau", "fatura", "pdf", base_path / "fatura-202512.pdf"),
        
        # MercadoPago Extrato
        ("mercadopago", "extrato", "pdf", base_path / "MP202508.pdf"),
        ("mercadopago", "extrato", "pdf", base_path / "MP202509.pdf"),
        ("mercadopago", "extrato", "pdf", base_path / "MP202510.pdf"),
        ("mercadopago", "extrato", "pdf", base_path / "MP202511.pdf"),
        ("mercadopago", "extrato", "pdf", base_path / "MP202512.pdf"),
    ]
    
    print("\n" + "="*70)
    print("🚀 VALIDAÇÃO DE PROCESSADORES PDF - INTEGRAÇÃO")
    print("="*70)
    
    # Executar testes
    results = []
    for banco, tipo, formato, file_path in tests:
        if not file_path.exists():
            print(f"\n⚠️  Arquivo não encontrado: {file_path}")
            results.append(False)
            continue
        
        success = test_processor(banco, tipo, formato, file_path)
        results.append(success)
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n✅ Aprovados: {passed}/{total}")
    print(f"❌ Falharam: {failed}/{total}")
    
    if failed == 0:
        print(f"\n🎉 TODOS OS PROCESSADORES PDF ESTÃO FUNCIONANDO!")
    else:
        print(f"\n⚠️  Alguns processadores falharam. Verificar logs acima.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
