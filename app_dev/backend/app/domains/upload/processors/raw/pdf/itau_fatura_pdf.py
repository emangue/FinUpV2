"""
Processador bruto para Fatura Itaú PDF
Extrai transações de PDFs de fatura do Itaú e gera a mesma estrutura que itau_fatura.py

DEPLOY → ProjetoFinancasV5
  Destino: app/domains/upload/processors/raw/pdf/itau_fatura_pdf.py
  (substitui o arquivo existente)

MUDANÇAS vs versão anterior do V5:
  - Adiciona parâmetro `senha: str = None` para PDFs protegidos
  - Compatível com PDF sem senha (comportamento idêntico ao original)
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
import pdfplumber

from ..base import RawTransaction

logger = logging.getLogger(__name__)


def process_itau_fatura_pdf(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str,
    final_cartao: str,
    senha: Optional[str] = None,
) -> List[RawTransaction]:
    """
    Processa fatura Itaú PDF (com ou sem senha).

    Args:
        file_path: Caminho do arquivo PDF
        nome_arquivo: Nome original do arquivo
        nome_cartao: Nome do cartão (ex: "Mastercard Black")
        final_cartao: Final do cartão (ex: "4321")
        senha: Senha do PDF, se protegido (geralmente CPF sem pontos/traço)
              Injetado via functools.partial no registry, ou passado diretamente.

    Returns:
        Lista de RawTransaction
    """
    logger.info(f"Processando fatura Itaú PDF: {nome_arquivo}" + (" [com senha]" if senha else ""))

    try:
        # Extrair texto de todas as páginas
        open_kwargs = {"password": senha} if senha else {}
        with pdfplumber.open(file_path, **open_kwargs) as pdf:
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
        mes_transacao = int(mm)
        if mes_transacao > mes_fatura:
            ano_transacao = ano_fatura - 1
            logger.debug(f"Transação {ddmm} no mês {mes_transacao} > mês fatura {mes_fatura}, usando ano {ano_transacao}")
        else:
            ano_transacao = ano_fatura

        data_iso = f"{ano_transacao}-{mm}-{dd}"

        estab_normalizado = estab_bruto.strip()

        eh_estorno = False
        if estab_normalizado.endswith(' -') or estab_normalizado.endswith('-'):
            estab_normalizado = re.sub(r'\s*-\s*$', '', estab_normalizado)
            eh_estorno = True

        estab_normalizado = re.sub(r'[,.\s]+$', '', estab_normalizado)

        if eh_estorno and valor > 0:
            valor = -valor
            logger.debug(f"Estorno detectado na extração: {estab_normalizado} - valor invertido para {valor}")

        contexto = texto[max(0, match.start() - 100):min(len(texto), match.end() + 100)]
        eh_internacional = bool(re.search(r'USD|EUR|GBP|ARS', contexto, re.IGNORECASE))

        if mes_transacao == mes_fatura and ano_transacao == ano_fatura:
            eh_futura = False
        elif ano_transacao > ano_fatura:
            eh_futura = True
        elif ano_transacao == ano_fatura and mes_transacao > mes_fatura:
            eh_futura = True
        elif ano_transacao < ano_fatura:
            eh_futura = False
        elif ano_transacao == ano_fatura and mes_transacao < mes_fatura:
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
    transacoes_filtradas = []
    grupos_parcelas = {}

    regex_parcela = re.compile(r'(\d{2})/(\d{2})\s*$')

    for trans in transacoes_brutas:
        estab = trans['estabelecimento']
        match_parcela = regex_parcela.search(estab)

        if match_parcela:
            parcela_atual = int(match_parcela.group(1))
            parcela_total = int(match_parcela.group(2))
            estab_sem_parcela = estab[:match_parcela.start()].strip()

            estab_norm = re.sub(r'[^A-Z0-9]', '', estab_sem_parcela.upper())

            trans['parcela_atual'] = parcela_atual
            trans['parcela_total'] = parcela_total
            trans['estabelecimento_normalizado'] = estab_norm

            if estab_norm not in grupos_parcelas:
                grupos_parcelas[estab_norm] = []
            grupos_parcelas[estab_norm].append(trans)
        else:
            trans['parcela_atual'] = None
            trans['parcela_total'] = None
            transacoes_filtradas.append(trans)

    for estab_norm, grupo in grupos_parcelas.items():
        if len(grupo) == 1:
            transacoes_filtradas.append(grupo[0])
        else:
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
    melhores_transacoes = {}

    for trans in transacoes_brutas:
        estab_base = re.sub(r'\s*\d{2}/\d{2}\s*$', '', trans['estabelecimento']).strip()
        estab_norm = re.sub(r'[^A-Z0-9]', '', estab_base.upper())
        chave_sem_parcela = f"{trans['data_iso']}|{estab_norm}|{trans['valor']}"

        if chave_sem_parcela in melhores_transacoes:
            trans_existente = melhores_transacoes[chave_sem_parcela]
            tem_parcela_atual = bool(re.search(r'\d{2}/\d{2}\s*$', trans['estabelecimento']))
            tem_parcela_existente = bool(re.search(r'\d{2}/\d{2}\s*$', trans_existente['estabelecimento']))

            if tem_parcela_atual and not tem_parcela_existente:
                logger.debug(f"Substituindo '{trans_existente['estabelecimento']}' por '{trans['estabelecimento']}' (versão com parcela)")
                melhores_transacoes[chave_sem_parcela] = trans
            elif tem_parcela_existente and not tem_parcela_atual:
                logger.debug(f"Ignorando '{trans['estabelecimento']}' - já temos '{trans_existente['estabelecimento']}' (versão com parcela)")
            else:
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
        if trans['eh_futura']:
            continue

        data_completa = trans['data_iso']
        valor_final = trans['valor']
        estabelecimento_final = trans['estabelecimento']

        if 'ESTORNO' in estabelecimento_final.upper() and valor_final > 0:
            valor_final = -valor_final
            logger.debug(f"Estorno detectado: {estabelecimento_final} - valor invertido para {valor_final}")

        transacoes.append((data_completa, estabelecimento_final, valor_final))

    # === ADICIONAR IOFs CONSOLIDADOS ===
    for iof_info in linhas_iof_consolidado:
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

    transacoes_existentes = set()
    for data, lanc, valor in transacoes:
        lanc_sem_parcela = re.sub(r'\s*\d{2}/\d{2}\s*$', '', lanc).strip()
        lanc_norm = re.sub(r'[^A-Z0-9]', '', lanc_sem_parcela.upper())
        chave = f"{data}|{lanc_norm}|{valor:.2f}"
        transacoes_existentes.add(chave)

    transacoes_servicos_unicas = []
    for data, lanc, valor in transacoes_servicos:
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

    inicio_secao = -1
    for i, linha in enumerate(linhas):
        if 'PRODUTOS/SERVIÇOS' in linha.upper():
            inicio_secao = i
            break

    if inicio_secao == -1:
        return transacoes

    i = inicio_secao + 1
    while i < len(linhas):
        linha = linhas[i].strip()

        if 'COMPRAS PARCELADAS' in linha.upper() or 'TOTAL DOS LANÇAMENTOS' in linha.upper():
            break

        regex_multiplas = r'(\d{2}/\d{2})\s+([^\n\r]+?)\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})'
        matches = list(re.finditer(regex_multiplas, linha))

        for match in matches:
            data_curta = match.group(1)
            descricao = match.group(2).strip()
            valor_str = match.group(3).strip()

            if descricao.endswith('-'):
                descricao = descricao[:-1].strip()
                if not valor_str.startswith('-'):
                    valor_str = '-' + valor_str

            descricao = re.sub(r'\d{2}/\d{2}$', '', descricao).strip()

            dd, mm = data_curta.split('/')
            data_completa = f"{ano_atual}-{mm}-{dd}"
            valor = _convert_valor_br(valor_str)

            if 'ESTORNO' in descricao.upper() and valor > 0:
                valor = -valor

            if valor != 0:
                transacoes.append((data_completa, descricao, valor))
                logger.debug(f"Produto/Serviço extraído: {data_completa} | {descricao} | {valor}")

        i += 1

    return transacoes


def _convert_valor_br(valor_str: str) -> float:
    """Converte valor no formato brasileiro (1.234,56) para float"""
    valor_str = valor_str.strip().replace(' ', '')
    if ',' in valor_str:
        valor_str = valor_str.replace('.', '')
        valor_str = valor_str.replace(',', '.')
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
    now = datetime.now()
    return now.strftime('%Y%m')
