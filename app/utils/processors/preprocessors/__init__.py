"""
Pacote de preprocessadores para arquivos especiais

Preprocessadores tratam arquivos com formatos não-padronizados antes
de passar para o sistema de detecção automática.

Versão: 2.1.0
Data: 27/12/2025

Preprocessadores disponíveis:
- Itaú XLS: Extrato com validação de saldo
- Itaú CSV: Fatura de cartão de crédito
- BTG: Extrato com "Saldo Diário" e validação
- Mercado Pago: Extrato XLSX com INITIAL/FINAL_BALANCE

Direcionador automático:
- detect_and_preprocess(): Detecta banco e preprocessa automaticamente
- Retorna: {'df': DataFrame, 'validacao': dict, 'banco': str, 'tipodocumento': str, 'preprocessado': bool}
"""

from .extrato_itau_xls import is_extrato_itau_xls, preprocessar_extrato_itau_xls
from .extrato_btg import is_extrato_btg, preprocessar_extrato_btg
from .extrato_mercadopago import is_extrato_mercadopago, preprocessar_extrato_mercadopago, converter_valor_br
from .fatura_itau import is_fatura_itau, preprocessar_fatura_itau


def detect_and_preprocess(df_raw, filename):
    """
    Detecta automaticamente o banco e preprocessa arquivo
    
    Ordem de detecção:
    1. Itaú XLS (extrato com validação de saldo)
    2. Itaú CSV (fatura de cartão de crédito)
    3. BTG (extrato com "Saldo Diário")
    4. Mercado Pago (XLSX com INITIAL_BALANCE)
    5. None (arquivo genérico - processamento normal)
    
    Args:
        df_raw: DataFrame bruto lido com pd.read_excel() ou pd.read_csv()
        filename: Nome do arquivo original
        
    Returns:
        dict: {
            'df': DataFrame processado ou df_raw,
            'validacao': dict com resultado da validação ou None,
            'banco': str nome do banco ('Itaú', 'BTG', 'Mercado Pago', 'Genérico'),
            'tipodocumento': str ('Extrato', 'Fatura Cartão de Crédito', None),
            'preprocessado': bool True se foi preprocessado
        }
        
    Raises:
        ValueError: Se arquivo não for reconhecido como extrato ou fatura
    """
    print(f"\n🔍 Detectando tipo de arquivo: {filename}")
    
    # Tentar Itaú XLS (Extrato)
    try:
        if is_extrato_itau_xls(df_raw, filename):
            print("   ✓ Extrato Itaú XLS detectado")
            df_processado, validacao = preprocessar_extrato_itau_xls(df_raw)
            return {
                'df': df_processado,
                'validacao': validacao,
                'banco': 'Itaú',
                'tipodocumento': 'Extrato',
                'preprocessado': True
            }
    except Exception as e:
        print(f"   ⚠️ Erro ao testar Itaú XLS: {e}")
    
    # Tentar Itaú CSV (Fatura de Cartão)
    try:
        if is_fatura_itau(df_raw, filename):
            print("   ✓ Fatura Itaú detectada")
            df_processado, validacao = preprocessar_fatura_itau(df_raw)
            return {
                'df': df_processado,
                'validacao': validacao,
                'banco': 'Itaú',
                'tipodocumento': 'Fatura Cartão de Crédito',
                'preprocessado': True
            }
    except Exception as e:
        print(f"   ⚠️ Erro ao testar Fatura Itaú: {e}")
    
    # Tentar BTG
    try:
        if is_extrato_btg(df_raw, filename):
            print("   ✓ BTG detectado")
            df_processado, validacao = preprocessar_extrato_btg(df_raw)
            return {
                'df': df_processado,
                'validacao': validacao,
                'banco': 'BTG',
                'tipodocumento': 'Extrato',
                'preprocessado': True
            }
    except Exception as e:
        print(f"   ⚠️ Erro ao testar BTG: {e}")
    
    # Tentar Mercado Pago
    try:
        if is_extrato_mercadopago(df_raw, filename):
            print("   ✓ Mercado Pago detectado")
            df_processado, validacao = preprocessar_extrato_mercadopago(df_raw)
            return {
                'df': df_processado,
                'validacao': validacao,
                'banco': 'Mercado Pago',
                'tipodocumento': 'Extrato',
                'preprocessado': True
            }
    except Exception as e:
        print(f"   ⚠️ Erro ao testar Mercado Pago: {e}")
    
    # Tentar detecção genérica via sistema de detecção
    print("   ℹ️ Nenhum preprocessador específico reconheceu o arquivo")
    print("   ℹ️ Tentando detecção genérica...")
    
    # Importar detector genérico
    try:
        from app.blueprints.upload.utils import detectar_tipo_arquivo
        
        # Tentar detectar tipo (fatura ou extrato)
        tipo_detectado = detectar_tipo_arquivo(df_raw)
        
        if tipo_detectado and tipo_detectado.get('tipo'):
            tipo = tipo_detectado['tipo']
            print(f"   ✓ Tipo genérico detectado: {tipo}")
            
            # Definir tipodocumento
            if tipo == 'fatura':
                tipodocumento = 'Fatura Cartão de Crédito'
            elif tipo == 'extrato':
                tipodocumento = 'Extrato'
            else:
                tipodocumento = None
            
            return {
                'df': df_raw,
                'validacao': None,
                'banco': 'Genérico',
                'tipodocumento': tipodocumento,
                'preprocessado': False
            }
    except Exception as e:
        print(f"   ⚠️ Erro na detecção genérica: {e}")
    
    # Nenhum tipo reconhecido - REJEITAR
    raise ValueError(
        f"❌ Documento não reconhecido: {filename}\n"
        f"   Não foi possível identificar como Extrato ou Fatura de Cartão.\n"
        f"   Bancos suportados: Itaú, BTG, Mercado Pago\n"
        f"   Certifique-se de que o arquivo está no formato correto."
    )


__all__ = [
    'is_extrato_itau_xls',
    'preprocessar_extrato_itau_xls',
    'is_fatura_itau',
    'preprocessar_fatura_itau',
    'is_extrato_btg',
    'preprocessar_extrato_btg',
    'is_extrato_mercadopago',
    'preprocessar_extrato_mercadopago',
    'converter_valor_br',
    'detect_and_preprocess',
]
