"""
Preprocessador de Fatura de Cartão Itaú

Versão: 1.0.0
Data: 27/12/2025
Status: stable

Transforma CSV de fatura Itaú em formato padronizado.
Retorna DataFrame com colunas: ['data', 'lançamento', 'valor (R$)']

Histórico:
- 1.0.0: Criação inicial - extração de lógica específica do Itaú
"""
import pandas as pd
import re
from datetime import datetime


def converter_valor_br(valor_str):
    """
    Converte valores em formato brasileiro para float
    
    Exemplos:
        "1.232,46" → 1232.46
        "123,00" → 123.00
        "-45,67" → -45.67
    """
    if pd.isna(valor_str) or valor_str == '':
        return 0.0
    
    try:
        # Remove espaços
        valor_limpo = str(valor_str).strip()
        
        # Remove pontos de milhar e substitui vírgula por ponto
        valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        
        return float(valor_limpo)
    except:
        return 0.0


def is_fatura_itau(df_raw, filename):
    """
    Detecta se é fatura de cartão Itaú
    
    Critérios de detecção:
    1. Nome do arquivo contém 'fatura' ou 'itau'
    2. Colunas esperadas: 'data', 'lançamento' (ou estabelecimento), 'valor'
    3. CSV simples sem cabeçalhos complexos
    
    Args:
        df_raw: DataFrame bruto (pd.read_csv com header=None)
        filename: Nome do arquivo
        
    Returns:
        bool: True se for fatura Itaú
    """
    try:
        # Verifica nome do arquivo
        nome_lower = filename.lower()
        if 'fatura' not in nome_lower and 'itau' not in nome_lower:
            return False
        
        # Verifica se tem pelo menos 3 colunas
        if df_raw.shape[1] < 3:
            return False
        
        # Procura linha de cabeçalho (primeira linha não-vazia)
        for idx in range(min(5, len(df_raw))):
            linha = df_raw.iloc[idx]
            
            # Converte para string e limpa
            valores = [str(v).strip().lower() for v in linha if pd.notna(v)]
            
            # Verifica se tem palavras-chave de fatura
            if any(termo in ' '.join(valores) for termo in ['data', 'lançamento', 'estabelecimento', 'valor']):
                return True
        
        # Se não encontrou cabeçalho claro, verifica se parece CSV de transações
        # Primeira coluna deve ter datas
        primeira_col = df_raw.iloc[:, 0].dropna()
        if len(primeira_col) > 0:
            # Tenta parsear como data
            for valor in primeira_col.head(3):
                try:
                    pd.to_datetime(str(valor))
                    return True  # Tem data, pode ser fatura
                except:
                    continue
        
        return False
        
    except Exception as e:
        print(f"   ⚠️ Erro ao detectar fatura Itaú: {e}")
        return False


def preprocessar_fatura_itau(df_raw):
    """
    Preprocessa fatura de cartão Itaú para formato padronizado
    
    Entrada esperada:
        - CSV com colunas: data, lançamento/estabelecimento, valor
        - Valores em formato brasileiro (1.234,56)
        - Pode ter cabeçalho ou não
        
    Saída padronizada:
        DataFrame com colunas: ['data', 'lançamento', 'valor (R$)']
        - data: string DD/MM/AAAA
        - lançamento: string (nome do estabelecimento)
        - valor (R$): float (negativo para despesas)
        
    Validação:
        - Não há validação matemática para faturas
        - Apenas verifica se tem transações válidas
        
    Returns:
        tuple: (df_processado, validacao_dict)
        
    Raises:
        ValueError: Se não conseguir processar o arquivo
    """
    print("\n💳 Preprocessando fatura Itaú...")
    
    try:
        # Encontra linha de cabeçalho
        header_idx = None
        for idx in range(min(5, len(df_raw))):
            linha = df_raw.iloc[idx]
            valores = [str(v).strip().lower() for v in linha if pd.notna(v)]
            texto_linha = ' '.join(valores)
            
            if any(termo in texto_linha for termo in ['data', 'lançamento', 'estabelecimento', 'valor']):
                header_idx = idx
                break
        
        # Se achou cabeçalho, usa ele
        if header_idx is not None:
            # Define cabeçalho e pega dados a partir da próxima linha
            df_trabalho = df_raw.iloc[header_idx + 1:].copy()
            df_trabalho.columns = df_raw.iloc[header_idx].values
            df_trabalho.reset_index(drop=True, inplace=True)
        else:
            # Não tem cabeçalho explícito - assume primeiras 3 colunas
            df_trabalho = df_raw.copy()
            # Renomeia colunas para padrão esperado
            if df_trabalho.shape[1] >= 3:
                df_trabalho.columns = ['data', 'lançamento', 'valor'] + [f'col_{i}' for i in range(3, df_trabalho.shape[1])]
        
        # Normaliza nomes de colunas
        df_trabalho.columns = [str(c).strip().lower() for c in df_trabalho.columns]
        
        # Identifica colunas
        col_data = None
        col_lancamento = None
        col_valor = None
        
        for col in df_trabalho.columns:
            if 'data' in col:
                col_data = col
            elif any(termo in col for termo in ['lançamento', 'lancamento', 'estabelecimento', 'descricao', 'descrição']):
                col_lancamento = col
            elif 'valor' in col or 'r$' in col:
                col_valor = col
        
        if not all([col_data, col_lancamento, col_valor]):
            raise ValueError(
                f"Não foi possível identificar todas as colunas necessárias.\n"
                f"Colunas encontradas: {list(df_trabalho.columns)}\n"
                f"Esperado: data, lançamento, valor"
            )
        
        # Remove linhas vazias
        df_trabalho = df_trabalho.dropna(subset=[col_data, col_lancamento, col_valor], how='all')
        
        # Cria DataFrame de saída
        df_saida = pd.DataFrame()
        
        # Processa data
        datas_processadas = []
        for data_raw in df_trabalho[col_data]:
            if pd.isna(data_raw):
                datas_processadas.append(None)
                continue
            
            try:
                # Tenta vários formatos
                if isinstance(data_raw, str):
                    for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                        try:
                            dt = datetime.strptime(data_raw.strip(), fmt)
                            break
                        except:
                            continue
                    else:
                        dt = pd.to_datetime(data_raw)
                else:
                    dt = pd.to_datetime(data_raw)
                
                datas_processadas.append(dt.strftime('%d/%m/%Y'))
            except:
                datas_processadas.append(None)
        
        df_saida['data'] = datas_processadas
        
        # Processa lançamento (limpa strings)
        df_saida['lançamento'] = df_trabalho[col_lancamento].apply(lambda x: str(x).strip() if pd.notna(x) else '')
        
        # Processa valores
        df_saida['valor (R$)'] = df_trabalho[col_valor].apply(converter_valor_br)
        
        # Remove linhas com data inválida ou lançamento vazio
        df_saida = df_saida[df_saida['data'].notna() & (df_saida['lançamento'] != '')]
        
        # Ignora linhas de pagamento/saldo
        termos_ignorar = [
            'PAGAMENTO EFETUADO', 'PAGAMENTO RECEBIDO', 'CRÉDITO FATURA',
            'SALDO ANTERIOR', 'SALDO DO DIA', 'TOTAL'
        ]
        for termo in termos_ignorar:
            df_saida = df_saida[~df_saida['lançamento'].str.upper().str.contains(termo, na=False)]
        
        # Remove valores zero
        df_saida = df_saida[df_saida['valor (R$)'] != 0]
        
        df_saida.reset_index(drop=True, inplace=True)
        
        # Validação básica
        if len(df_saida) == 0:
            raise ValueError("Nenhuma transação válida encontrada no arquivo")
        
        validacao = {
            'validado': True,
            'transacoes_encontradas': len(df_saida),
            'soma_total': df_saida['valor (R$)'].sum(),
            'observacao': 'Faturas de cartão não têm validação matemática automática'
        }
        
        print(f"   ✓ {len(df_saida)} transações extraídas")
        print(f"   ✓ Soma total: R$ {validacao['soma_total']:.2f}")
        
        return df_saida, validacao
        
    except Exception as e:
        print(f"   ❌ Erro ao preprocessar fatura Itaú: {e}")
        raise ValueError(f"Erro ao processar fatura Itaú: {str(e)}")


# Exemplo de uso e testes
if __name__ == '__main__':
    # Teste básico
    print("Testes do preprocessador de fatura Itaú")
    print("=" * 60)
    
    # Simula um CSV de fatura
    dados_teste = {
        0: ['data', 'lançamento', 'valor'],
        1: ['15/11/2025', 'RESTAURANTE ABC', '150,00'],
        2: ['16/11/2025', 'SUPERMERCADO XYZ 1/3', '200,00'],
        3: ['17/11/2025', 'FARMACIA DEF', '45,50'],
    }
    
    df_teste = pd.DataFrame.from_dict(dados_teste, orient='index', columns=[0, 1, 2])
    
    if is_fatura_itau(df_teste, 'fatura-itau-202511.csv'):
        print("✓ Detecção funcionou")
        df_proc, val = preprocessar_fatura_itau(df_teste)
        print(f"\nDataFrame processado:")
        print(df_proc)
        print(f"\nValidação: {val}")
    else:
        print("❌ Não detectou como fatura Itaú")
