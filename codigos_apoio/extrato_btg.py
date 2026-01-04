"""
Preprocessador para arquivos XLS de extrato do BTG

O arquivo XLS do BTG tem estrutura especial:
- Linhas 0-6: Cabeçalhos do banco e info da conta
- Linha 7: "Lançamentos:" + "Saldo atual:"
- Linha 9: Headers reais (Data e hora, Categoria, Transação, Descrição, Valor)
- Linha 10+: Transações (algumas linhas são "Saldo Diário")

Validação:
- Primeiro "Saldo Diário" = saldo inicial
- Último "Saldo Diário" = saldo final
- Valida: saldo_inicial + Σ(transações após primeiro Saldo) ≈ saldo_final (±0.01)
- IMPORTANTE: Retorna TODAS as transações (inclui linha 10), mas valida apenas subset

Versão: 1.0.0
Data: 27/12/2025
"""

import pandas as pd
import numpy as np
from datetime import datetime


def converter_valor_brasileiro(valor_raw):
    """
    Converte valor brasileiro (14.830,40) para float (14830.40)
    
    Args:
        valor_raw: Valor em formato string ou número
        
    Returns:
        float ou None se conversão falhar
    """
    if pd.isna(valor_raw):
        return None
    
    # Se já é número, retorna diretamente
    if isinstance(valor_raw, (int, float)):
        return float(valor_raw)
    
    # Se é string, tratar formato brasileiro
    valor_str = str(valor_raw).strip()
    if not valor_str:
        return None
    
    try:
        # Remover pontos (separador de milhar) e trocar vírgula por ponto (decimal)
        valor_str = valor_str.replace('.', '').replace(',', '.')
        return float(valor_str)
    except ValueError:
        return None


def is_extrato_btg(df_raw, filename):
    """
    Detecta se o arquivo é um extrato BTG
    
    Args:
        df_raw: DataFrame lido sem tratamento
        filename: Nome do arquivo
        
    Returns:
        bool: True se for extrato BTG
    """
    try:
        if not filename.lower().endswith('.xls'):
            return False
        
        if df_raw.shape[0] < 10:
            return False
        
        # Verifica se linha 7 contém "Lançamentos:"
        if df_raw.shape[0] > 7:
            linha7 = df_raw.iloc[7].tolist()
            linha7_str = [str(x) for x in linha7 if pd.notna(x)]
            if any('Lançamentos' in s or 'LANÇAMENTOS' in s.upper() for s in linha7_str):
                return True
        
        # Verifica se linha 9 tem headers esperados (Data e hora, Categoria, etc)
        if df_raw.shape[0] > 9:
            linha9 = df_raw.iloc[9].tolist()
            linha9_str = [str(x).lower() for x in linha9 if pd.notna(x)]
            if 'data' in ' '.join(linha9_str) and 'categoria' in ' '.join(linha9_str):
                return True
        
        # Verifica se tem "Saldo Diário" nas transações
        for idx in range(10, min(20, len(df_raw))):
            row_str = ' '.join([str(x) for x in df_raw.iloc[idx].tolist() if pd.notna(x)])
            if 'Saldo Diário' in row_str or 'SALDO DIÁRIO' in row_str.upper():
                return True
        
        return False
        
    except Exception as e:
        print(f"⚠️ Erro ao detectar BTG: {e}")
        return False


def preprocessar_extrato_btg(df_raw):
    """
    Preprocessa arquivo XLS do extrato BTG para formato padronizado
    
    Args:
        df_raw: DataFrame bruto lido com pd.read_excel()
        
    Returns:
        tuple: (DataFrame processado, dict com validação)
    """
    print("🏦 Detectado: Extrato BTG")
    print(f"   Shape bruto: {df_raw.shape[0]} linhas x {df_raw.shape[1]} colunas")
    
    try:
        # 1. Extrair informações da conta (linhas 1-5)
        info_conta = {}
        try:
            if len(df_raw) > 1:
                cliente_row = df_raw.iloc[1].tolist()
                if len(cliente_row) >= 2 and str(cliente_row[0]).strip() == 'Cliente:':
                    info_conta['cliente'] = str(cliente_row[1]).strip()
            
            if len(df_raw) > 4:
                conta_row = df_raw.iloc[4].tolist()
                if len(conta_row) >= 2 and str(conta_row[0]).strip() == 'Conta:':
                    info_conta['conta'] = str(conta_row[1]).strip()
            
            if len(df_raw) > 5:
                periodo_row = df_raw.iloc[5].tolist()
                if len(periodo_row) >= 2 and 'Período' in str(periodo_row[0]):
                    info_conta['periodo'] = str(periodo_row[1]).strip()
                    
            if info_conta:
                print(f"   ✓ Conta: {info_conta.get('conta', 'N/A')}")
                print(f"   ✓ Período: {info_conta.get('periodo', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Não foi possível extrair info da conta: {e}")
        
        # 2. Detectar linha de headers (linha 9, começando na coluna B)
        print("\n📊 ETAPA 1: Detectando estrutura do arquivo...")
        linha_header = 9
        
        # Extrair headers (começam na coluna 1 = B)
        headers_raw = df_raw.iloc[linha_header].tolist()[1:]  # Ignora coluna A
        headers = [str(h).strip() if pd.notna(h) else f'col_{i}' for i, h in enumerate(headers_raw)]
        
        print(f"   ✓ Linha de headers: {linha_header}")
        print(f"   ✓ Headers: {headers}")
        
        # 3. Extrair dados (começam na linha 10, coluna B em diante)
        print("\n📊 ETAPA 2: Extraindo transações...")
        linha_dados_inicio = 10
        
        df_dados = df_raw.iloc[linha_dados_inicio:, 1:].copy()  # Ignora coluna A
        df_dados.columns = headers
        df_dados = df_dados.reset_index(drop=True)
        
        print(f"   ✓ Dados brutos: {len(df_dados)} linhas")
        
        # 4. Identificar coluna de Descrição (procurar coluna com "Saldo Diário")
        col_descricao = None
        for col in df_dados.columns:
            if df_dados[col].astype(str).str.contains('Saldo Diário', case=False, na=False).any():
                col_descricao = col
                break
        
        if not col_descricao:
            # Fallback: usar última coluna antes de Valor
            col_descricao = df_dados.columns[-2] if len(df_dados.columns) > 1 else df_dados.columns[0]
        
        print(f"   ✓ Coluna de Descrição identificada: '{col_descricao}'")
        
        # 5. Mapear colunas
        col_data = headers[0]  # Data e hora
        col_categoria = headers[1] if len(headers) > 1 else None
        col_valor = headers[-1]  # Última coluna = Valor
        
        # 6. Filtrar linhas vazias
        df_dados = df_dados.dropna(how='all')
        
        # 7. Extrair saldos diários ANTES de filtrar
        print("\n📊 ETAPA 3: Extraindo saldos para validação...")
        saldos_mask = df_dados[col_descricao].astype(str).str.contains('Saldo Diário', case=False, na=False)
        saldos_df = df_dados[saldos_mask].copy()
        
        if len(saldos_df) == 0:
            print("   ⚠️ Nenhum 'Saldo Diário' encontrado - validação desabilitada")
            saldo_inicial = None
            saldo_final = None
            primeiro_saldo_idx = None
        else:
            saldo_inicial_row = saldos_df.iloc[0]
            saldo_final_row = saldos_df.iloc[-1]
            
            saldo_inicial = converter_valor_brasileiro(saldo_inicial_row[col_valor])
            saldo_final = converter_valor_brasileiro(saldo_final_row[col_valor])
            primeiro_saldo_idx = saldos_df.index[0]
            
            print(f"   ✓ Primeiro Saldo Diário ({saldo_inicial_row[col_data]}): R$ {saldo_inicial:.2f}")
            print(f"   ✓ Último Saldo Diário ({saldo_final_row[col_data]}): R$ {saldo_final:.2f}")
        
        # 8. SALVAR TODAS as transações (incluindo linha 10), exceto Saldos Diários
        print("\n📊 ETAPA 4: Preparando DataFrame final...")
        df_transacoes = df_dados[~saldos_mask].copy()
        
        print(f"   ✓ Transações a salvar: {len(df_transacoes)} linhas (TODAS, exceto Saldos)")
        
        # 9. Para VALIDAÇÃO: usar apenas transações APÓS primeiro Saldo
        if primeiro_saldo_idx is not None:
            df_validacao = df_transacoes[df_transacoes.index > primeiro_saldo_idx].copy()
            print(f"   ℹ️  Validação usará {len(df_validacao)} transações (APÓS primeiro Saldo)")
        else:
            df_validacao = df_transacoes.copy()
        
        # 10. Processar todas as transações
        transacoes_processadas = []
        indices_processados = []  # Rastrear índices originais
        
        print(f"\n📊 Processando {len(df_transacoes)} linhas...")
        
        for idx, row in df_transacoes.iterrows():
            data_raw = row[col_data]
            categoria = str(row[col_categoria]).strip() if col_categoria and pd.notna(row[col_categoria]) else ''
            descricao = str(row[col_descricao]).strip() if pd.notna(row[col_descricao]) else ''
            valor_raw = row[col_valor]
            
            # Pular linhas vazias
            if pd.isna(data_raw) or pd.isna(valor_raw):
                print(f"   ⏭️  Linha {idx}: Pulando (data ou valor vazio)")
                continue
            
            # Tratar Data: "12/12/2025 21:06" → "12/12/2025"
            try:
                data_str = str(data_raw).strip()
                if ' ' in data_str:
                    data_str = data_str.split(' ')[0]  # Remove hora
                data_final = data_str
            except:
                print(f"   ⚠️ Data inválida na linha {idx}: {data_raw}")
                continue
            
            # Converter valor (formato brasileiro: 14.830,40)
            valor = converter_valor_brasileiro(valor_raw)
            if valor is None:
                print(f"   ⚠️ Valor inválido na linha {idx}: {valor_raw}")
                continue
            
            # Criar Lançamento: Categoria - Descrição
            if categoria and descricao:
                lancamento = f"{categoria} - {descricao}"
            elif descricao:
                lancamento = descricao
            elif categoria:
                lancamento = categoria
            else:
                lancamento = "Transação BTG"
            
            print(f"   ✓ {data_final}: {lancamento[:40]:40s} R$ {valor:>12.2f}")
            
            transacoes_processadas.append({
                'data': data_final,
                'lançamento': lancamento,
                'valor (R$)': valor
            })
            indices_processados.append(idx)  # Guardar índice original do DataFrame
        
        df_final = pd.DataFrame(transacoes_processadas)
        
        print(f"\n   ✓ DataFrame final: {len(df_final)} transações processadas")
        
        # 11. VALIDAÇÃO - usa transações APÓS primeiro Saldo Diário
        print("\n📊 ETAPA 5: Validando integridade dos dados...")
        validacao = {
            'valido': False,
            'saldo_anterior': saldo_inicial,
            'soma_transacoes': 0.0,
            'saldo_calculado': 0.0,
            'saldo_final_arquivo': saldo_final,
            'diferenca': 0.0,
            'mensagem': ''
        }
        
        if saldo_inicial is not None and saldo_final is not None:
            # CORRETO: Primeiro Saldo + transações APÓS ele = Último Saldo
            # Usar índices rastreados para mapear corretamente
            indices_validacao_set = set(df_validacao.index.tolist())
            transacoes_validacao = [
                t for t, idx_original in zip(transacoes_processadas, indices_processados)
                if idx_original in indices_validacao_set
            ]
            
            print(f"   🔍 Debug: {len(transacoes_processadas)} transações totais, {len(transacoes_validacao)} para validação")
            
            soma_transacoes = sum(t['valor (R$)'] for t in transacoes_validacao)
            saldo_calculado = saldo_inicial + soma_transacoes
            diferenca = saldo_calculado - saldo_final
            
            validacao['soma_transacoes'] = soma_transacoes
            validacao['saldo_calculado'] = saldo_calculado
            validacao['diferenca'] = diferenca
            
            # Tolerância de 10 centavos para arredondamentos
            if abs(diferenca) <= 0.10:
                validacao['valido'] = True
                validacao['mensagem'] = "✅ Extrato validado: Primeiro Saldo + Transações (após) = Último Saldo"
                print(f"   ✅ Validação APROVADA")
                print(f"      Primeiro Saldo Diário: R$ {saldo_inicial:.2f}")
                print(f"      Soma Transações (após 1º Saldo): R$ {soma_transacoes:.2f}")
                print(f"      Saldo Calculado: R$ {saldo_calculado:.2f}")
                print(f"      Último Saldo Diário: R$ {saldo_final:.2f}")
                print(f"      Diferença: R$ {diferenca:.4f} (tolerância: ±0.10)")
                print(f"      ✓ Retornando TODAS as transações (inclui antes do 1º Saldo)")
            else:
                validacao['valido'] = False
                validacao['mensagem'] = f"❌ ERRO DE VALIDAÇÃO: Diferença de R$ {diferenca:.2f}"
                print(f"   ❌ Validação REPROVADA - Diferença: R$ {diferenca:.2f}")
        else:
            validacao['mensagem'] = "⚠️ Validação desabilitada (sem Saldos Diários)"
            print("   ⚠️ Validação desabilitada")
        
        # 12. Adicionar informações extras na validação
        validacao['info_conta'] = info_conta
        validacao['periodo'] = info_conta.get('periodo')
        validacao['total_transacoes'] = len(df_final)
        
        print(f"\n✅ Preprocessamento BTG concluído: {len(df_final)} transações")
        print(f"   Colunas finais: {list(df_final.columns)}")
        
        return df_final, validacao
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERRO ao preprocessar BTG: {e}")
        print(traceback.format_exc())
        raise
