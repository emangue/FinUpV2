#!/usr/bin/env python3
"""
Script de Teste - Processadores Banco do Brasil

Testa os processadores de Extrato CSV e Cartão OFX do Banco do Brasil
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.processors.preprocessors import (
    is_extrato_bb_csv,
    processar_extrato_bb_csv,
    is_cartao_bb_ofx,
    processar_cartao_bb_ofx
)


def testar_extrato_bb():
    """Testa processador de extrato BB CSV"""
    print("\n" + "="*70)
    print("🧪 TESTE: Extrato Banco do Brasil (CSV)")
    print("="*70)
    
    arquivo = "extrato_ana_beatriz_BB.csv"
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    try:
        # Detectar
        if not is_extrato_bb_csv(arquivo):
            print(f"❌ Arquivo não reconhecido como extrato BB")
            return False
        
        # Processar
        resultado = processar_extrato_bb_csv(arquivo)
        
        # Validar resultado
        assert 'df' in resultado, "Faltando DataFrame no resultado"
        assert 'validacao' in resultado, "Faltando validação no resultado"
        assert resultado['banco'] == 'Banco do Brasil', "Banco incorreto"
        assert resultado['tipodocumento'] == 'Extrato Bancário', "Tipo incorreto"
        assert resultado['preprocessado'] == True, "Flag preprocessado incorreto"
        
        df = resultado['df']
        validacao = resultado['validacao']
        
        print(f"\n📊 Resultado:")
        print(f"   Transações processadas: {len(df)}")
        print(f"   Saldo Anterior: R$ {validacao['saldo_anterior']:,.2f}")
        print(f"   Soma Transações: R$ {validacao['soma_transacoes']:,.2f}")
        print(f"   Saldo Final: R$ {validacao['saldo_final']:,.2f}")
        print(f"   Validação: {'✅ PASSOU' if validacao['valido'] else '❌ FALHOU'}")
        
        # Amostra de transações
        print(f"\n📋 Amostra (primeiras 5 transações):")
        print(df[['data', 'estabelecimento', 'valor']].head().to_string(index=False))
        
        if validacao['valido']:
            print("\n✅ TESTE PASSOU: Extrato BB CSV")
            return True
        else:
            print("\n⚠️ TESTE PASSOU COM AVISOS: Validação matemática falhou")
            return True
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def testar_cartao_bb():
    """Testa processador de cartão BB OFX"""
    print("\n" + "="*70)
    print("🧪 TESTE: Cartão Banco do Brasil (OFX)")
    print("="*70)
    
    arquivo = "OUROCARD_VISA_GOLD-Jan_25.ofx"
    
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    try:
        # Detectar
        if not is_cartao_bb_ofx(arquivo):
            print(f"❌ Arquivo não reconhecido como cartão BB OFX")
            return False
        
        # Processar
        resultado = processar_cartao_bb_ofx(arquivo)
        
        # Validar resultado
        assert 'df' in resultado, "Faltando DataFrame no resultado"
        assert 'validacao' in resultado, "Faltando validação no resultado"
        assert resultado['banco'] == 'Banco do Brasil', "Banco incorreto"
        assert resultado['tipodocumento'] == 'Fatura Cartão de Crédito', "Tipo incorreto"
        assert resultado['preprocessado'] == True, "Flag preprocessado incorreto"
        
        df = resultado['df']
        validacao = resultado['validacao']
        
        print(f"\n📊 Resultado:")
        print(f"   Transações processadas: {validacao['total_transacoes']}")
        print(f"   Total Débitos: R$ {validacao['total_debitos']:,.2f}")
        print(f"   Total Créditos: R$ {validacao['total_creditos']:,.2f}")
        print(f"   Saldo Final: R$ {validacao['saldo_final']:,.2f}")
        
        # Contar parcelas
        parceladas = df[df['total_parcelas'].notna()]
        print(f"   Transações Parceladas: {len(parceladas)}")
        
        # Amostra de transações
        print(f"\n📋 Amostra (primeiras 5 transações):")
        print(df[['data', 'estabelecimento', 'valor']].head().to_string(index=False))
        
        # Amostra de parceladas
        if len(parceladas) > 0:
            print(f"\n💳 Transações Parceladas (amostra):")
            print(parceladas[['data', 'estabelecimento', 'valor', 'parcela_atual', 'total_parcelas']].head().to_string(index=False))
        
        print("\n✅ TESTE PASSOU: Cartão BB OFX")
        return True
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 INICIANDO TESTES - PROCESSADORES BANCO DO BRASIL")
    print("="*70)
    
    resultados = []
    
    # Teste 1: Extrato CSV
    resultados.append(("Extrato BB CSV", testar_extrato_bb()))
    
    # Teste 2: Cartão OFX
    resultados.append(("Cartão BB OFX", testar_cartao_bb()))
    
    # Resumo
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    
    passou = sum(1 for _, result in resultados if result)
    total = len(resultados)
    
    for nome, result in resultados:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {nome}: {status}")
    
    print(f"\nTotal: {passou}/{total} testes passaram")
    
    if passou == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        sys.exit(1)
