"""
Processador bruto para Fatura Itaú PDF
Extrai transações de PDFs de fatura do Itaú e gera a mesma estrutura que itau_fatura.py
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import pdfplumber

logger = logging.getLogger(__name__)


class RawTransaction:
    """Classe para armazenar transação bruta"""
    def __init__(self, banco, tipo_documento, nome_arquivo, data_criacao, 
                 data, lancamento, valor, nome_cartao, final_cartao, mes_fatura):
        self.banco = banco
        self.tipo_documento = tipo_documento
        self.nome_arquivo = nome_arquivo
        self.data_criacao = data_criacao
        self.data = data
        self.lancamento = lancamento
        self.valor = valor
        self.nome_cartao = nome_cartao
        self.final_cartao = final_cartao
        self.mes_fatura = mes_fatura


def process_itau_fatura_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str,
    final_cartao: str
) -> List[RawTransaction]:
    """
    Processa fatura Itaú PDF
    
    Args:
        file_path: Caminho do arquivo PDF
        nome_arquivo: Nome original do arquivo
        nome_cartao: Nome do cartão (ex: "Mastercard Black")
        final_cartao: Final do cartão (ex: "4321")
        
    Returns:
        Lista de RawTransaction
    """
    logger.info(f"Processando fatura Itaú PDF: {nome_arquivo}")
    
    try:
        # Extrair texto de todas as páginas
        with pdfplumber.open(file_path) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text() + "\n"
        
        logger.debug(f"PDF lido: {len(pdf.pages)} páginas")
        
        # Extrair transações do texto
        transacoes = _extract_transactions_from_text(texto_completo)
        logger.info(f"Fatura PDF processada: {len(transacoes)} transações")
        
        # Extrair mês da fatura do nome do arquivo (ex: fatura-202601.pdf)
        mes_fatura = _extract_mes_fatura(nome_arquivo)
        
        # Converter para RawTransaction
        transactions = []
        data_criacao = datetime.now()
        
        for data, lancamento, valor in transacoes:
            # CSV usa: compras positivas, créditos negativos
            # PDF extrai: compras positivas, créditos negativos
            # Então NÃO precisa inverter
            transaction = RawTransaction(
                banco='Itaú',
                tipo_documento='fatura',
                nome_arquivo=nome_arquivo,
                data_criacao=data_criacao,
                data=data,
                lancamento=lancamento,
                valor=valor,
                nome_cartao=nome_cartao,
                final_cartao=final_cartao,
                mes_fatura=mes_fatura,
            )
            transactions.append(transaction)
        
        logger.info(f"✅ Fatura Itaú PDF processada: {len(transactions)} transações")
        return transactions
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar fatura Itaú PDF: {str(e)}", exc_info=True)
        raise


def _extract_transactions_from_text(texto: str) -> List[Tuple[str, str, float]]:
    """
    Extrai transações do texto do PDF seguindo EXATAMENTE a lógica do n8n JavaScript
    
    Returns:
        Lista de tuplas (data_formatada, estabelecimento, valor)
    """
    transacoes = []
    
    # === DETECTAR ANO E MÊS DA FATURA ===
    ano_fatura = None
    mes_fatura = None
    match_postagem = re.search(r'Postagem:\s*(\d{2})/(\d{2})/(\d{4})', texto, re.IGNORECASE)
    if match_postagem:
        mes_fatura = int(match_postagem.group(2))
        ano_fatura = int(match_postagem.group(3))
    
    if not ano_fatura:
        match_emissao = re.search(r'Emissão:\s*(\d{2})/(\d{2})/(\d{4})', texto, re.IGNORECASE)
        if match_emissao:
            mes_fatura = int(match_emissao.group(2))
            ano_fatura = int(match_emissao.group(3))
    
    if not ano_fatura:
        ano_fatura = datetime.now().year
        mes_fatura = datetime.now().month
    
    logger.debug(f"Ano da fatura: {ano_fatura}, Mês da fatura: {mes_fatura}")
    
    # === DETECTAR POSIÇÃO DE "COMPRAS PARCELADAS" ===
    pos_compras_parceladas = texto.lower().find('compras parceladas')
    logger.debug(f"Posição 'compras parceladas': {pos_compras_parceladas}")
    
    # === DETECTAR IOF CONSOLIDADO (Repasse de IOF) ===
    # O PDF traz IOFs consolidados como "Repasse de IOF em R$ XXX"
    # Diferente do CSV que traz linha por linha
    regex_repasse_iof = r'Repasse de IOF em R\$\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})'
    linhas_iof_consolidado = []
    
    for match in re.finditer(regex_repasse_iof, texto, re.IGNORECASE):
        valor_str = match.group(1)
        valor_iof = _convert_valor_br(valor_str)
        linhas_iof_consolidado.append({
            'valor': abs(valor_iof),
            'posicao': match.start()
        })
        logger.debug(f"IOF consolidado encontrado: R$ {valor_iof}")
    
    logger.debug(f"Total de IOFs consolidados: {len(linhas_iof_consolidado)}")
    
    # === EXTRAIR TRANSAÇÕES ===
    # Regex: DD/MM ESTABELECIMENTO VALOR
    regex = r'(\d{2}/\d{2})\s+([^\n\r]+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})'
    transacoes_brutas = []
    
    for match in re.finditer(regex, texto, re.IGNORECASE | re.MULTILINE):
        ddmm = match.group(1)
        estab_bruto = match.group(2)
        valor_str = match.group(3)
        
        valor = _convert_valor_br(valor_str)
        
        dd = ddmm[:2]
        mm = ddmm[3:5]
        
        # === INFERIR ANO CORRETO ===
        # Se o mês da transação é DEPOIS do mês da fatura, é do ano anterior
        # Exemplo: fatura setembro (09), transação dezembro (12) → ano anterior
        mes_transacao = int(mm)
        if mes_transacao > mes_fatura:
            ano_transacao = ano_fatura - 1
            logger.debug(f"Transação {ddmm} no mês {mes_transacao} > mês fatura {mes_fatura}, usando ano {ano_transacao}")
        else:
            ano_transacao = ano_fatura
        
        data_iso = f"{ano_transacao}-{mm}-{dd}"
        
        # Normalizar estabelecimento: remover pontuação final (vírgulas, pontos)
        estab_normalizado = estab_bruto.strip()
        
        # Se termina com " -", é estorno - remover o traço e inverter sinal do valor
        eh_estorno = False
        if estab_normalizado.endswith(' -') or estab_normalizado.endswith('-'):
            estab_normalizado = re.sub(r'\s*-\s*$', '', estab_normalizado)
            eh_estorno = True
        
        estab_normalizado = re.sub(r'[,.\s]+$', '', estab_normalizado)
        
        # Inverter sinal se for estorno
        if eh_estorno and valor > 0:
            valor = -valor
            logger.debug(f"Estorno detectado na extração: {estab_normalizado} - valor invertido para {valor}")
        
        # Detectar se é internacional (USD, EUR, etc no contexto)
        contexto = texto[max(0, match.start() - 100):min(len(texto), match.end() + 100)]
        eh_internacional = bool(re.search(r'USD|EUR|GBP|ARS', contexto, re.IGNORECASE))
        
        # Marcar se é futura: transação é do mês POSTERIOR à fatura
        # Exemplo: fatura 11/2025, transação 12/2025 ou 01/2026 → futura
        # Transação 10/2025 ou 11/2025 → atual
        if mes_transacao == mes_fatura and ano_transacao == ano_fatura:
            # Mesmo mês/ano da fatura → atual
            eh_futura = False
        elif ano_transacao > ano_fatura:
            # Ano posterior → futura
            eh_futura = True
        elif ano_transacao == ano_fatura and mes_transacao > mes_fatura:
            # Mesmo ano mas mês posterior → futura
            eh_futura = True
        elif ano_transacao < ano_fatura:
            # Ano anterior (parcela de compra antiga) → atual
            eh_futura = False
        elif ano_transacao == ano_fatura and mes_transacao < mes_fatura:
            # Mesmo ano mas mês anterior → atual
            eh_futura = False
        else:
            eh_futura = False
        
        transacoes_brutas.append({
            'ddmm': ddmm,
            'data_iso': data_iso,
            'estabelecimento': estab_normalizado,
            'valor': valor,
            'valor_positivo': abs(valor),
            'eh_internacional': eh_internacional,
            'eh_futura': eh_futura,
            'posicao': match.start()
        })
    
    logger.debug(f"Transações brutas extraídas: {len(transacoes_brutas)}")
    
    # === FILTRAR PARCELAS DUPLICADAS ===
    # Se temos a mesma compra parcelada com diferentes números de parcela (ex: 03/10 e 04/10),
    # manter apenas a de MENOR número (mais antiga = que vence nesta fatura)
    transacoes_filtradas = []
    grupos_parcelas = {}  # {estabelecimento_normalizado: [transações com parcelas]}
    
    # Regex para detectar parcelas no formato DD/DD no final
    regex_parcela = re.compile(r'(\d{2})/(\d{2})\s*$')
    
    for trans in transacoes_brutas:
        estab = trans['estabelecimento']
        match_parcela = regex_parcela.search(estab)
        
        if match_parcela:
            # Tem parcela - extrair número da parcela
            parcela_atual = int(match_parcela.group(1))
            parcela_total = int(match_parcela.group(2))
            estab_sem_parcela = estab[:match_parcela.start()].strip()
            
            # Normalizar estabelecimento (ignorar espaços, pontuação)
            estab_norm = re.sub(r'[^A-Z0-9]', '', estab_sem_parcela.upper())
            
            trans['parcela_atual'] = parcela_atual
            trans['parcela_total'] = parcela_total
            trans['estabelecimento_normalizado'] = estab_norm
            
            # Agrupar por estabelecimento normalizado
            if estab_norm not in grupos_parcelas:
                grupos_parcelas[estab_norm] = []
            grupos_parcelas[estab_norm].append(trans)
        else:
            # Sem parcela - adicionar direto
            trans['parcela_atual'] = None
            trans['parcela_total'] = None
            transacoes_filtradas.append(trans)
    
    # Para cada grupo de parcelas, manter apenas a de menor número
    for estab_norm, grupo in grupos_parcelas.items():
        if len(grupo) == 1:
            # Só uma parcela desse estabelecimento - manter
            transacoes_filtradas.append(grupo[0])
        else:
            # Múltiplas parcelas - verificar se são valores similares (mesma compra)
            # Agrupar por valor similar (diferença < 10%)
            subgrupos = []
            for trans in grupo:
                adicionado = False
                for subgrupo in subgrupos:
                    valor_ref = subgrupo[0]['valor_positivo']
                    if abs(trans['valor_positivo'] - valor_ref) / valor_ref < 0.1:
                        subgrupo.append(trans)
                        adicionado = True
                        break
                if not adicionado:
                    subgrupos.append([trans])
            
            # Para cada subgrupo, manter apenas a de menor parcela_atual
            for subgrupo in subgrupos:
                trans_menor_parcela = min(subgrupo, key=lambda t: t['parcela_atual'])
                transacoes_filtradas.append(trans_menor_parcela)
                
                if len(subgrupo) > 1:
                    removidas = [t for t in subgrupo if t != trans_menor_parcela]
                    parcelas_removidas = [f"{t['parcela_atual']}/{t['parcela_total']}" for t in removidas]
                    logger.debug(f"Removendo {len(removidas)} parcelas duplicadas de {estab_norm}: " +
                               f"mantendo {trans_menor_parcela['parcela_atual']}/{trans_menor_parcela['parcela_total']}, " +
                               f"removendo {parcelas_removidas}")
    
    logger.debug(f"Após filtro de parcelas: {len(transacoes_filtradas)} transações (removidas {len(transacoes_brutas) - len(transacoes_filtradas)})")
    transacoes_brutas = transacoes_filtradas
    
    # === REMOVER DUPLICATAS DE PARCELAS (COM E SEM NÚMERO) ===
    # Algumas transações aparecem duas vezes: uma com parcela "DD/DD" e outra sem
    # Exemplo: "AZULEH87JC 12/12" e "AZULEH87JC" na mesma data/valor - são a mesma compra
    # Manter apenas a versão COM parcela (mais informativa)
    melhores_transacoes = {}  # chave -> transação
    
    for trans in transacoes_brutas:
        # Criar chave normalizada SEM parcela
        estab_base = re.sub(r'\s*\d{2}/\d{2}\s*$', '', trans['estabelecimento']).strip()
        estab_norm = re.sub(r'[^A-Z0-9]', '', estab_base.upper())
        chave_sem_parcela = f"{trans['data_iso']}|{estab_norm}|{trans['valor']}"
        
        if chave_sem_parcela in melhores_transacoes:
            # Já existe - verificar qual tem parcela
            trans_existente = melhores_transacoes[chave_sem_parcela]
            tem_parcela_atual = bool(re.search(r'\d{2}/\d{2}\s*$', trans['estabelecimento']))
            tem_parcela_existente = bool(re.search(r'\d{2}/\d{2}\s*$', trans_existente['estabelecimento']))
            
            if tem_parcela_atual and not tem_parcela_existente:
                # Substituir - a atual tem parcela, a existente não
                logger.debug(f"Substituindo '{trans_existente['estabelecimento']}' por '{trans['estabelecimento']}' (versão com parcela)")
                melhores_transacoes[chave_sem_parcela] = trans
            elif tem_parcela_existente and not tem_parcela_atual:
                # Manter a existente - ela tem parcela
                logger.debug(f"Ignorando '{trans['estabelecimento']}' - já temos '{trans_existente['estabelecimento']}' (versão com parcela)")
            else:
                # Ambas com ou sem parcela e mesmo texto
                # Podem ser transações legítimas repetidas (mesma compra 2x) ou duplicatas
                # Para não perder transações, vamos MANTER AMBAS
                # A remoção de duplicatas entre seções (principal vs produtos/serviços) resolve duplicatas reais
                chave_unica = f"{chave_sem_parcela}#{len(melhores_transacoes)}"
                melhores_transacoes[chave_unica] = trans
                logger.debug(f"Transação repetida: '{trans['estabelecimento']}' - mantendo ambas (podem ser compras legítimas)")
        else:
            melhores_transacoes[chave_sem_parcela] = trans
    
    transacoes_unicas = list(melhores_transacoes.values())
    logger.debug(f"Após remover duplicatas de parcelas: {len(transacoes_unicas)} transações (removidas {len(transacoes_brutas) - len(transacoes_unicas)})")
    transacoes_brutas = transacoes_unicas
    
    # === CRIAR REGISTROS FINAIS ===
    for trans in transacoes_brutas:
        # Ignorar transações futuras (compras parceladas)
        if trans['eh_futura']:
            continue
        
        # Formato YYYY-MM-DD (igual ao CSV)
        data_completa = trans['data_iso']
        valor_final = trans['valor']
        estabelecimento_final = trans['estabelecimento']
        
        # Se contém "ESTORNO" no estabelecimento, forçar valor negativo
        if 'ESTORNO' in estabelecimento_final.upper() and valor_final > 0:
            valor_final = -valor_final
            logger.debug(f"Estorno detectado: {estabelecimento_final} - valor invertido para {valor_final}")
        
        transacoes.append((data_completa, estabelecimento_final, valor_final))
    
    # === ADICIONAR IOFs CONSOLIDADOS ===
    # PDF traz IOFs como "Repasse de IOF" consolidados
    # Adicionar como transações genéricas, igual ao CSV faz com "IOF COMPRA INTERNACIONA"
    for iof_info in linhas_iof_consolidado:
        # Usar a data da fatura para os IOFs consolidados
        data_iof = f"{ano_fatura}-{mes_fatura:02d}-01"
        transacoes.append((
            data_iof,
            "IOF COMPRA INTERNACIONA",
            iof_info['valor']
        ))
        logger.debug(f"IOF consolidado adicionado: R$ {iof_info['valor']}")
    
    logger.debug(f"Transações finais (com IOFs consolidados): {len(transacoes)}")
    
    # === PRODUTOS/SERVIÇOS (anuidades, estornos, taxas) ===
    linhas = texto.split('\n')
    transacoes_servicos = _extract_produtos_servicos(linhas, ano_fatura)
    
    # Remover duplicatas entre transações principais e produtos/serviços
    # Considerar versões com e sem parcela como mesma transação
    transacoes_existentes = set()
    for data, lanc, valor in transacoes:
        # Remover parcela antes de normalizar
        lanc_sem_parcela = re.sub(r'\s*\d{2}/\d{2}\s*$', '', lanc).strip()
        lanc_norm = re.sub(r'[^A-Z0-9]', '', lanc_sem_parcela.upper())
        chave = f"{data}|{lanc_norm}|{valor:.2f}"
        transacoes_existentes.add(chave)
    
    transacoes_servicos_unicas = []
    for data, lanc, valor in transacoes_servicos:
        # Remover parcela antes de normalizar
        lanc_sem_parcela = re.sub(r'\s*\d{2}/\d{2}\s*$', '', lanc).strip()
        lanc_norm = re.sub(r'[^A-Z0-9]', '', lanc_sem_parcela.upper())
        chave = f"{data}|{lanc_norm}|{valor:.2f}"
        
        if chave not in transacoes_existentes:
            transacoes_servicos_unicas.append((data, lanc, valor))
        else:
            logger.debug(f"Duplicata entre produtos/serviços e transações principais: {data} | {lanc} | {valor}")
    
    transacoes.extend(transacoes_servicos_unicas)
    logger.debug(f"Total após produtos/serviços: {len(transacoes)} (duplicatas removidas: {len(transacoes_servicos) - len(transacoes_servicos_unicas)})")
    
    return transacoes


def _extract_produtos_servicos(linhas: List[str], ano_atual: int) -> List[Tuple[str, str, float]]:
    """
    Extrai transações da seção 'Lançamentos: produtos e serviços'
    """
    transacoes = []
    
    # Encontrar início da seção
    inicio_secao = -1
    for i, linha in enumerate(linhas):
        if 'PRODUTOS/SERVIÇOS' in linha.upper():
            inicio_secao = i
            break
    
    if inicio_secao == -1:
        return transacoes
    
    # Processar linhas após o cabeçalho
    i = inicio_secao + 1
    while i < len(linhas):
        linha = linhas[i].strip()
        
        # Parar ao encontrar seção de compras parceladas ou total
        if 'COMPRAS PARCELADAS' in linha.upper() or 'TOTAL DOS LANÇAMENTOS' in linha.upper():
            break
        
        # Usar o MESMO regex que funciona na extração principal
        # Isso garante consistência e evita capturar parcelas como valores
        regex_multiplas = r'(\d{2}/\d{2})\s+([^\n\r]+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})'
        matches = list(re.finditer(regex_multiplas, linha))
        
        for match in matches:
            data_curta = match.group(1)
            descricao = match.group(2).strip()
            valor_str = match.group(3).strip()
            
            # Se a descrição termina com "-", é estorno - juntar com valor
            if descricao.endswith('-'):
                descricao = descricao[:-1].strip()
                if not valor_str.startswith('-'):
                    valor_str = '-' + valor_str
            
            # Remover parcela se houver (ex: "03/12" em "ANUIDADE DIFERENCI03/12")
            descricao = re.sub(r'\d{2}/\d{2}$', '', descricao).strip()
            
            # Formato YYYY-MM-DD (igual ao CSV)
            dd, mm = data_curta.split('/')
            data_completa = f"{ano_atual}-{mm}-{dd}"
            valor = _convert_valor_br(valor_str)
            
            # Se contém "ESTORNO" na descrição, forçar valor negativo
            if 'ESTORNO' in descricao.upper() and valor > 0:
                valor = -valor
            
            if valor != 0:
                transacoes.append((data_completa, descricao, valor))
                logger.debug(f"Produto/Serviço extraído: {data_completa} | {descricao} | {valor}")
        
        i += 1
    
    return transacoes


def _convert_valor_br(valor_str: str) -> float:
    """
    Converte valor no formato brasileiro (1.234,56) para float
    """
    valor_str = valor_str.strip()
    
    # Remover espaços extras (ex: "- 36.75" -> "-36.75")
    valor_str = valor_str.replace(' ', '')
    
    # Formato brasileiro: remover ponto (milhar) e trocar vírgula por ponto (decimal)
    if ',' in valor_str:
        valor_str = valor_str.replace('.', '')  # Remove separador de milhar
        valor_str = valor_str.replace(',', '.')  # Troca vírgula por ponto
    
    try:
        return float(valor_str)
    except ValueError:
        logger.warning(f"Não foi possível converter valor: {valor_str}")
        return 0.0


def _extract_mes_fatura(nome_arquivo: str) -> str:
    """
    Extrai mês da fatura do nome do arquivo
    Ex: fatura-202601.pdf → '202601'
    """
    match = re.search(r'(\d{6})', nome_arquivo)
    if match:
        return match.group(1)
    
    # Fallback: usar mês/ano atual
    now = datetime.now()
    return now.strftime('%Y%m')


# Teste standalone
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    # Testar com arquivo de exemplo
    file_path = Path('fatura-202509.pdf')
    if file_path.exists():
        transactions = process_itau_fatura_pdf(
            file_path=file_path,
            nome_arquivo='fatura-202509.pdf',
            nome_cartao='Mastercard',
            final_cartao='9266'
        )
        
        print(f"\n✅ Total de transações: {len(transactions)}")
        print(f"💰 Soma total: R$ {sum(t.valor for t in transactions):.2f}")
        print("\n📋 Primeiras 10 transações:")
        for t in transactions[:10]:
            print(f"  {t.data} | {t.lancamento[:50]:50s} | R$ {t.valor:10.2f}")
