"""
📄 PROCESSADOR BTG PACTUAL - EXTRATO DE CONTA CORRENTE (Formato XLS)

=== FORMATO ESPERADO ===
Arquivo XLS com estrutura:
- Header na linha 9: "Data e hora | Categoria | Transação | Descrição | Valor"
- Dados a partir da linha 10
- Formato de data: "DD/MM/YYYY HH:MM" (exemplo: "12/12/2025 21:06")
- Valores em formato numérico ou string com vírgula
- Contém linhas "Saldo Diário" que devem ser IGNORADAS

=== COLUNA LANÇAMENTO ===
**IMPORTANTE**: A coluna 'lançamento' é formada por:
    Categoria + " - " + Transação + " - " + Descrição

Exemplos:
- "Transferência - Pix recebido - Emanuel Guerra Leandro"
- "Salário - Portabilidade de salário - Pagamento recebido"
- "Compras - Compra no débito - Mercado Carrefour"

(Quando a coluna Transação não existir, usa o formato antigo:
    Categoria + " - " + Descrição)

=== ESTRATÉGIA DE PROCESSAMENTO ===
1. Buscar linha com header "Data e hora"
2. Extrair todas as linhas após o header
3. Normalizar nomes de colunas (lowercase, strip)
4. Identificar colunas: data, categoria, descrição, valor
5. **FILTRAR "Saldo Diário" ANTES de criar lançamento** (crítico!)
6. Criar coluna lançamento = Categoria + " - " + Descrição
7. Converter data (extrair apenas DD/MM/YYYY, ignorar hora)
8. Converter valor para float (tratando vírgulas)
9. Filtrar lançamentos vazios/inválidos
10. Filtrar valores zero
11. Determinar tipo (Receitas/Despesas) baseado no sinal

=== VALIDAÇÕES ===
- Linhas "Saldo Diário": REMOVIDAS (não são transações reais)
- Lançamentos vazios (" - ", "nan - nan"): REMOVIDOS
- Valores zero: REMOVIDOS
- Datas inválidas: REMOVIDAS

=== HISTÓRICO ===
- V1: Processador original com problemas de extração (apenas 2/10 transações)
- V2: Redesenhado após análise completa do formato BTG
  - Extração: 10/10 transações ✅
  - Saldo validado: R$ 3.004,50 ✅
  - Filtros de "Saldo Diário" funcionando ✅
- V3 (15/03/2026): Corrigido bug crítico + suporte multi-página + campo Transação
  - [T1] Fix filtro nan: str.contains('nan') → regex \\bnan\\b
    ("Crédito e Financiamento" continha 'nan' como substring → 3 transações perdidas)
  - [T2] Suporte multi-página: encontra TODOS os headers, concatena blocos
    (extrato multi-mês exportado pelo JasperReports tem 3 blocos de header)
  - [T3] Campo Transação incluído no lançamento:
    Antes: 'Transferência - Emanuel Guerra Leandro'
    Depois: 'Transferência - Pix recebido - Emanuel Guerra Leandro'
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

try:
    from ..base import RawTransaction
except ImportError:
    # Para testes standalone
    RawTransaction = None

logger = logging.getLogger(__name__)


def process_btg_extrato(file_path: Path, banco: str, tipo_documento: str, user_email: str) -> List[RawTransaction]:
    """
    Processa arquivo XLS de extrato BTG Pactual (Interface padrão do sistema)
    
    Args:
        file_path: Caminho do arquivo XLS
        banco: Nome do banco
        tipo_documento: Tipo de documento ('extrato')
        user_email: Email do usuário
        
    Returns:
        Lista de RawTransaction
    """
    # Extrato BTG só suporta .xls (exportado pelo portal). Arquivo .xlsx é fatura.
    if str(file_path).lower().endswith('.xlsx'):
        raise ValueError(
            "Arquivo XLSX detectado na aba Extrato. "
            "O extrato BTG Pactual é exportado em formato XLS (.xls). "
            "Se quiser importar uma fatura BTG, selecione a aba \"Fatura Cartão\" e tente novamente."
        )

    # Chamar processador interno (para manter compatibilidade com testes)
    transacoes_dict = processar_btg_extrato_interno(file_path, user_id=1)
    
    # Converter para RawTransaction
    raw_transactions = []
    nome_arquivo = file_path.name
    data_criacao = datetime.now()
    
    for t in transacoes_dict:
        # Valor já vem com sinal correto (+ para receitas, - para despesas)
        raw_tx = RawTransaction(
            banco=banco,
            tipo_documento=tipo_documento,
            nome_arquivo=nome_arquivo,
            data_criacao=data_criacao,
            data=t['data'],
            lancamento=t['lancamento'],
            valor=t['valor'],  # Positivo para receitas, negativo para despesas
            nome_cartao=None,
            final_cartao=None,
            mes_fatura=None,
        )
        raw_transactions.append(raw_tx)
    
    return raw_transactions


def processar_btg_extrato_interno(file_path: Path, user_id: int) -> List[Dict[str, Any]]:
    """
    Processa arquivo XLS de extrato BTG Pactual
    
    Args:
        file_path: Caminho do arquivo XLS
        user_id: ID do usuário
        
    Returns:
        Lista de dicionários com transações extraídas
    """
    try:
        # 1. Encontrar header "Data e hora"
        with pd.ExcelFile(file_path, engine='xlrd') as xls:
            df_full = pd.read_excel(xls, header=None)
        
        # Encontrar TODAS as posições de header 'Data e hora'
        # (arquivo multi-mês pode ter 3+ blocos repetidos pelo JasperReports)
        header_rows = []
        for idx, row in df_full.iterrows():
            row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
            if 'data e hora' in row_str:
                header_rows.append(idx)

        if not header_rows:
            raise ValueError("Header 'Data e hora' não encontrado no arquivo")

        logger.info(f"✅ {len(header_rows)} bloco(s) encontrado(s) nas linhas {header_rows}")

        # 2. Para cada bloco, extrair apenas as linhas entre esse header e o próximo
        # Assim as linhas de cabeçalho/rodapé dos blocos intermediários são ignoradas
        dfs = []
        for i, hr in enumerate(header_rows):
            next_start = header_rows[i + 1] if i + 1 < len(header_rows) else df_full.shape[0]
            bloco = df_full.iloc[hr + 1 : next_start].copy()
            bloco.columns = df_full.iloc[hr].values
            bloco = bloco.reset_index(drop=True)
            dfs.append(bloco)
            logger.info(f"   Bloco {i+1}: linhas {hr+1}–{next_start-1} ({len(bloco)} linhas)")

        df = pd.concat(dfs, ignore_index=True)
        
        logger.info(f"📊 Linhas de dados extraídas: {len(df)}")
        
        # 3. Normalizar nomes de colunas (lowercase, strip)
        df.columns = [
            str(col).lower().strip() 
            if not (isinstance(col, float) and pd.isna(col)) 
            else None 
            for col in df.columns
        ]
        
        # 4. Identificar colunas importantes
        col_data = None
        col_categoria = None
        col_transacao = None  # T3: coluna 'Transação' (col D no XLS)
        col_descricao = None
        col_valor = None

        for col in df.columns:
            if col is None:
                continue
            col_str = str(col).lower()

            if 'data' in col_str and col_data is None:
                col_data = col
            elif 'categoria' in col_str and col_categoria is None:
                col_categoria = col
            elif ('transa' in col_str) and col_transacao is None:
                col_transacao = col
            elif 'descri' in col_str and col_descricao is None:
                col_descricao = col
            elif 'valor' in col_str and col_valor is None:
                col_valor = col

        # Validar que encontrou colunas obrigatórias
        if not all([col_data, col_categoria, col_descricao, col_valor]):
            missing = []
            if not col_data: missing.append('data')
            if not col_categoria: missing.append('categoria')
            if not col_descricao: missing.append('descrição')
            if not col_valor: missing.append('valor')
            raise ValueError(f"Colunas não encontradas: {', '.join(missing)}")

        logger.info(f"✅ Colunas: data={col_data}, categoria={col_categoria}, transacao={col_transacao}, descrição={col_descricao}, valor={col_valor}")

        # 5. Selecionar e renomear colunas
        colunas_sel = [col_data, col_categoria, col_descricao, col_valor]
        if col_transacao:
            colunas_sel = [col_data, col_categoria, col_transacao, col_descricao, col_valor]

        df_trabalho = df[colunas_sel].copy()

        if col_transacao:
            df_trabalho.columns = ['data_hora', 'categoria', 'transacao', 'descricao', 'valor_bruto']
        else:
            df_trabalho.columns = ['data_hora', 'categoria', 'descricao', 'valor_bruto']
        
        # 6. Preencher NaN com string vazia (evitar perda de dados)
        df_trabalho['categoria'] = df_trabalho['categoria'].fillna('').astype(str)
        df_trabalho['descricao'] = df_trabalho['descricao'].fillna('').astype(str)
        if 'transacao' in df_trabalho.columns:
            df_trabalho['transacao'] = df_trabalho['transacao'].fillna('').astype(str)
        
        logger.info(f"📝 Transações antes de filtrar Saldo Diário: {len(df_trabalho)}")
        
        # 7. Filtrar "Saldo Diário" ANTES de criar lançamento
        # (pode aparecer em qualquer coluna dependendo do bloco)
        mask_saldo = (
            df_trabalho['descricao'].str.contains('Saldo Diário', case=False, na=False) |
            df_trabalho['categoria'].str.contains('Saldo Diário', case=False, na=False)
        )
        df_trabalho = df_trabalho[~mask_saldo].copy()
        
        logger.info(f"🧹 Transações após filtrar Saldo Diário: {len(df_trabalho)}")
        
        # 8. Criar lançamento: Categoria - Transação - Descrição (T3)
        # Inclui a coluna Transação quando disponível para melhor classificação
        if 'transacao' in df_trabalho.columns:
            df_trabalho['lancamento'] = (
                df_trabalho['categoria'] + ' - ' +
                df_trabalho['transacao'] + ' - ' +
                df_trabalho['descricao']
            )
        else:
            # Fallback para compatibilidade com formato antigo sem coluna Transação
            df_trabalho['lancamento'] = df_trabalho['categoria'] + ' - ' + df_trabalho['descricao']
        
        # 9. Limpar lançamentos vazios ou inválidos
        # [T1] FIX CRÍTICO: usar \bnan\b (word boundary) em vez de str.contains('nan')
        # A categoria 'Crédito e Financiamento' contém 'nan' como substring
        # (Fina[nan]ciamento), o que causava remoção incorreta de 3 transações.
        # \bnan\b só casa 'nan' como palavra isolada, não como parte de outra palavra.
        df_trabalho['lancamento'] = df_trabalho['lancamento'].str.strip()
        mask_lancamento_valido = (
            (df_trabalho['lancamento'] != '') &
            (df_trabalho['lancamento'] != '-') &
            (~df_trabalho['lancamento'].str.lower().str.match(r'^nan\s*-\s*nan(\s*-\s*nan)?$')) &
            (~df_trabalho['lancamento'].str.lower().str.contains(r'\bnan\b', regex=True))
        )
        df_trabalho = df_trabalho[mask_lancamento_valido].copy()
        
        logger.info(f"📝 Transações após filtrar lançamentos inválidos: {len(df_trabalho)}")
        
        # 10. Converter data (extrair apenas DD/MM/YYYY, ignorar hora)
        def parse_data_btg(data_str):
            """Extrai DD/MM/YYYY de "DD/MM/YYYY HH:MM" """
            try:
                if pd.isna(data_str):
                    return None
                
                data_str = str(data_str).strip()
                
                # Se já está em formato datetime, converter
                if isinstance(data_str, pd.Timestamp):
                    return data_str.strftime('%d/%m/%Y')
                
                # Se é string "DD/MM/YYYY HH:MM", extrair apenas data
                if ' ' in data_str:
                    data_parte = data_str.split(' ')[0]
                    return data_parte
                
                # Se é string "DD/MM/YYYY", retornar direto
                if '/' in data_str:
                    return data_str
                
                # Tentar parse com pandas
                dt = pd.to_datetime(data_str, dayfirst=True, errors='coerce')
                if pd.notna(dt):
                    return dt.strftime('%d/%m/%Y')
                
                return None
            except:
                return None
        
        df_trabalho['data'] = df_trabalho['data_hora'].apply(parse_data_btg)
        
        # Filtrar datas inválidas
        df_trabalho = df_trabalho[df_trabalho['data'].notna()].copy()
        
        logger.info(f"📅 Transações após converter datas: {len(df_trabalho)}")
        
        # 11. Converter valor para float
        def parse_valor_btg(valor):
            """Converte valor para float, tratando formatos BTG"""
            try:
                if pd.isna(valor):
                    return 0.0
                
                valor_str = str(valor).strip()
                
                # Remover espaços
                valor_str = valor_str.replace(' ', '')
                
                # Se já é float/int direto
                if isinstance(valor, (int, float)):
                    return float(valor)
                
                # Substituir vírgula por ponto
                valor_str = valor_str.replace(',', '.')
                
                return float(valor_str)
            except:
                return 0.0
        
        df_trabalho['valor'] = df_trabalho['valor_bruto'].apply(parse_valor_btg)
        
        # 12. Filtrar valores zero
        df_trabalho = df_trabalho[df_trabalho['valor'] != 0].copy()
        
        logger.info(f"💰 Transações após filtrar valores zero: {len(df_trabalho)}")
        
        # 13. Criar resultado final
        transacoes = []
        for _, row in df_trabalho.iterrows():
            # Manter sinal original: positivo para receitas, negativo para despesas
            valor_com_sinal = row['valor'] if row['valor'] > 0 else -abs(row['valor'])
            
            transacao = {
                'data': row['data'],
                'lancamento': row['lancamento'],
                'valor': valor_com_sinal,  # Com sinal correto
                'tipo': 'Receitas' if row['valor'] > 0 else 'Despesas',
                'user_id': user_id,
                'banco': 'BTG Pactual',
                'tipo_documento': 'extrato'
            }
            transacoes.append(transacao)
        
        # 14. Calcular saldo total
        saldo_total = sum(t['valor'] for t in transacoes)
        
        logger.info(f"✅ SUCESSO: {len(transacoes)} transações extraídas")
        logger.info(f"💵 Saldo total: R$ {saldo_total:,.2f}")
        
        return transacoes
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar arquivo BTG: {str(e)}")
        raise


# Para testes diretos
if __name__ == '__main__':
    import sys
    
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    if len(sys.argv) < 2:
        print("Uso: python btg_extrato_v2.py <caminho_arquivo.xls>")
        sys.exit(1)
    
    arquivo = Path(sys.argv[1])
    if not arquivo.exists():
        print(f"❌ Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    
    print("="*70)
    print("🏦 PROCESSADOR BTG EXTRATO V2 - TESTE")
    print("="*70)
    print()
    
    resultado = processar_btg_extrato_interno(arquivo, user_id=1)
    
    print()
    print("="*70)
    print("📋 TRANSAÇÕES EXTRAÍDAS")
    print("="*70)
    
    for i, t in enumerate(resultado, 1):
        sinal = '+' if t['tipo'] == 'Receitas' else '-'
        print(f"{i:2d}. {t['data']} | {t['lancamento'][:50]:<50} | {sinal}R$ {t['valor']:>10,.2f}")
    
    print()
    print("="*70)
    saldo = sum(t['valor'] if t['tipo'] == 'Receitas' else -t['valor'] for t in resultado)
    print(f"💵 Saldo Total: R$ {saldo:,.2f}")
    print("="*70)
