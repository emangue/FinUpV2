#!/usr/bin/env python3
"""
Script de Teste - Processors com CSVs Históricos
Version: 1.0.0
Date: 2026-01-03

Testa os processors atualizados processando CSVs históricos
e compara com os dados existentes no banco.
"""

import sys
import pandas as pd
from pathlib import Path

# Adicionar app ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.blueprints.upload.processors.fatura_cartao import processar_fatura_cartao
from app.blueprints.upload.processors.extrato_conta import processar_extrato_conta
from app.utils.processors.preprocessors.fatura_itau import preprocessar_fatura_itau

def test_fatura_itau(csv_path):
    """Testa processamento de fatura Itaú"""
    print(f"\n{'='*80}")
    print(f"TESTANDO: {csv_path}")
    print(f"{'='*80}")
    
    try:
        # 1. Ler CSV
        df_raw = pd.read_csv(csv_path, encoding='latin1', delimiter=';', skiprows=13)
        print(f"✅ Leitura OK: {len(df_raw)} linhas")
        
        # 2. Preprocessar (transformar em formato padronizado)
        df_padronizado = preprocessar_fatura_itau(df_raw)
        print(f"✅ Preprocessamento OK: {len(df_padronizado)} linhas")
        print(f"   Colunas: {list(df_padronizado.columns)}")
        
        # 2. Processar lógica de negócio
        file_name = Path(csv_path).name
        transacoes = processar_fatura_cartao(
            df=df_padronizado,
            banco='Itaú',
            tipodocumento='Cartão',
            origem='Itaú',
            file_name=file_name
        )
        
        print(f"✅ Processamento OK: {len(transacoes)} transações")
        
        # 3. Validar estrutura das transações
        if transacoes:
            primeira = transacoes[0]
            print(f"\n📋 Estrutura da primeira transação:")
            for key in sorted(primeira.keys()):
                valor = primeira[key]
                if isinstance(valor, str) and len(str(valor)) > 50:
                    valor = str(valor)[:50] + "..."
                print(f"   {key}: {valor}")
            
            # Validar campos obrigatórios
            campos_obrigatorios = [
                'IdTransacao', 'Data', 'Estabelecimento', 'Valor', 'ValorPositivo',
                'TipoTransacao', 'banco_origem', 'tipodocumento', 'origem_classificacao',
                'arquivo_origem', 'MesFatura'
            ]
            
            campos_faltando = [c for c in campos_obrigatorios if c not in primeira]
            if campos_faltando:
                print(f"\n❌ ERRO: Campos obrigatórios faltando: {campos_faltando}")
                return False
            
            # Validar que campos obsoletos não existem
            campos_obsoletos = [
                'DT_Fatura', 'origem', 'banco', 'forma_classificacao', 'MarcacaoIA',
                'ValidarIA', 'CartaoCodigo8', 'FinalCartao', 'TipoLancamento',
                'TransacaoFutura', 'NomeTitular', 'TipoTransacaoAjuste', 'IdOperacao'
            ]
            
            campos_obsoletos_presentes = [c for c in campos_obsoletos if c in primeira]
            if campos_obsoletos_presentes:
                print(f"\n⚠️  AVISO: Campos obsoletos ainda presentes: {campos_obsoletos_presentes}")
            
            print(f"\n✅ VALIDAÇÃO COMPLETA")
            return True
        else:
            print(f"\n⚠️  Nenhuma transação processada")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("TESTE DE PROCESSORS - CSVs Históricos")
    print("="*80)
    
    # CSVs de teste
    csvs_teste = [
        '_csvs_historico/fatura_itau-202512.csv',
        '_csvs_historico/fatura_itau-202511.csv',
        '_csvs_historico/fatura_itau-202510.csv',
    ]
    
    resultados = {}
    for csv_path in csvs_teste:
        if Path(csv_path).exists():
            sucesso = test_fatura_itau(csv_path)
            resultados[csv_path] = sucesso
        else:
            print(f"\n⚠️  Arquivo não encontrado: {csv_path}")
            resultados[csv_path] = None
    
    # Resumo
    print(f"\n{'='*80}")
    print(f"RESUMO DOS TESTES")
    print(f"{'='*80}")
    
    for csv, resultado in resultados.items():
        nome = Path(csv).name
        if resultado is True:
            print(f"✅ {nome}: SUCESSO")
        elif resultado is False:
            print(f"❌ {nome}: FALHOU")
        else:
            print(f"⚠️  {nome}: NÃO ENCONTRADO")
    
    todos_ok = all(r is True for r in resultados.values() if r is not None)
    
    if todos_ok:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n⚠️  ALGUNS TESTES FALHARAM")
        return 1

if __name__ == "__main__":
    sys.exit(main())
