"""
Transaction Marker - Fase 2 (v5.0.0)
Marca transações com IDs únicos (IdTransacao, IdParcela)
Integra hasher.py e normalizer.py

v5.0.0 (2026-02-25):
- Normalização invariante à renderização PDF/CSV
- Remove tudo que não é [A-Z0-9] da base do estabelecimento
- Resolve: PDF 202602+ sem espaços ("CONTAVIVO") ≡ CSV ("CONTA VIVO")
- IdParcela usa a mesma normalização [^A-Z0-9] na base do estabelecimento

v4.2.3 (2026-01-16):
- CRÍTICO: Adicionado .upper() ANTES de normalizar parcela
- Resolve: "Ebn *vpd Travel01/10" vs "EBN *VPD TRAVEL10/10" agora geram mesmo hash
- Normalização completa: espaços + uppercase + parcela (se fatura)
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

# Imports de utilitários compartilhados
from app.shared.utils import (
    fnv1a_64_hash,
    generate_id_transacao,
    normalizar_estabelecimento,
    arredondar_2_decimais
)

from .raw.base import RawTransaction

logger = logging.getLogger(__name__)


def extrair_parcela_do_estabelecimento(estabelecimento: str) -> Optional[dict]:
    """
    Extrai informação de parcela do estabelecimento
    Suporta formatos: "LOJA (3/12)" ou "LOJA 3/12"
    
    Args:
        estabelecimento: String com possível indicação de parcela
        
    Returns:
        dict: {'estabelecimento_base': str, 'parcela': int, 'total': int} ou None
    """
    # Tenta formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        # Validação básica
        if 1 <= parcela <= total <= 99:
            return {
                'estabelecimento_base': match.group(1).strip(),
                'parcela': parcela,
                'total': total
            }
    
    # Tenta formato sem parênteses: "LOJA 3/12" OU "LOJA3/12" (colado)
    match = re.search(r'^(.+?)\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        # Validação básica
        if 1 <= parcela <= total <= 99:
            return {
                'estabelecimento_base': match.group(1).strip(),
                'parcela': parcela,
                'total': total
            }
    
    return None


def normalizar_espacos(texto: str) -> str:
    """
    Normaliza espaços múltiplos para um único espaço
    
    Remove espaços extras que podem causar hashes diferentes:
    - "PIX TRANSF  GABRIEL" → "PIX TRANSF GABRIEL"
    - "LOJA   XYZ" → "LOJA XYZ"
    
    Args:
        texto: Texto com possíveis espaços múltiplos
        
    Returns:
        Texto com espaços normalizados
    """
    # Substituir múltiplos espaços por um único espaço
    return re.sub(r'\s+', ' ', texto.strip())


def normalizar_formato_parcela(estabelecimento: str) -> str:
    """
    Normaliza formato de parcela para padrão único: "LOJA (X/Y)"
    
    Converte:
    - "LOJA 01/05" → "LOJA (1/5)"
    - "LOJA 1/5" → "LOJA (1/5)"
    - "LOJA (01/05)" → "LOJA (1/5)"
    - "LOJA (1/5)" → "LOJA (1/5)" (já está no padrão)
    
    Args:
        estabelecimento: Nome do estabelecimento com possível parcela
        
    Returns:
        Estabelecimento com formato normalizado
    """
    info = extrair_parcela_do_estabelecimento(estabelecimento)
    
    if info:
        # Reconstruir com formato padrão (X/Y sem zeros à esquerda)
        return f"{info['estabelecimento_base']} ({info['parcela']}/{info['total']})"
    
    # Sem parcela, retorna original
    return estabelecimento


@dataclass
class MarkedTransaction(RawTransaction):
    """
    Transação com IDs marcados
    Extends RawTransaction com campos de identificação
    
    IMPORTANTE: Todos os campos precisam ter default porque RawTransaction
    tem campos opcionais, e Python não permite campos sem default depois
    de campos com default na herança de dataclasses.
    """
    
    # Campos de identificação (preenchidos sempre, mas têm default para herança funcionar)
    id_transacao: str = ""                  # Hash FNV-1a 64-bit
    estabelecimento_base: str = ""          # Sem XX/YY parcela
    valor_positivo: float = 0.0             # abs(valor)
    
    # Campos de parcela (opcionais)
    id_parcela: Optional[str] = None        # MD5 16-char (se tem parcela)
    parcela_atual: Optional[int] = None     # Ex: 1 de 12
    total_parcelas: Optional[int] = None    # Ex: 12
    
    # Campos temporais e tipo
    tipo_transacao: str = ""                # "Cartão de Crédito", "Despesas", "Receitas"
    ano: int = 0                            # 2025, 2026, etc
    mes: int = 0                            # 1 a 12


class TransactionMarker:
    """
    Marca transações com IDs únicos (v4.2.1 - com user_id)
    """
    
    def __init__(self, user_id: int):
        """
        Inicializa marker com controle de duplicados por arquivo
        
        Args:
            user_id: ID do usuário (necessário para isolamento no hash)
        """
        self.user_id = user_id
        logger.debug(f"TransactionMarker inicializado - v4.2.1 (user_id={user_id})")
        # Dict para rastrear duplicados dentro do arquivo
        # Chave: "data|lancamento_upper|valor" → Valor: contador de ocorrências
        # Ex: "15/10/2025|PIX TRANSF EMANUEL15/10|1000.00" → 1, depois 2, depois 3, ..., N
        self.seen_transactions = {}
    
    def _extrair_ano_mes(self, data_str: str) -> tuple[int, int]:
        """
        Extrai ano e mês de data DD/MM/YYYY
        
        Returns:
            (ano, mes) Ex: (2025, 12)
        """
        from datetime import datetime
        try:
            dt = datetime.strptime(data_str, '%d/%m/%Y')
            return dt.year, dt.month
        except ValueError as e:
            logger.error(f"Erro ao parsear data '{data_str}': {e}")
            # Fallback: tentar extrair manualmente
            partes = data_str.split('/')
            if len(partes) == 3:
                return int(partes[2]), int(partes[1])
            raise ValueError(f"Data inválida: {data_str}")
    
    def _determinar_tipo_transacao(self, nome_cartao: Optional[str], valor: float) -> str:
        """
        Determina tipo de transação baseado em cartão e valor
        
        Regras (mesma lógica atual do sistema):
        1. Se tem cartão → "Cartão de Crédito"
        2. Se extrato + negativo → "Despesas"
        3. Se extrato + positivo → "Receitas"
        
        Returns:
            "Cartão de Crédito" | "Despesas" | "Receitas"
        """
        # Regra 1: Cartão sempre primeiro
        if nome_cartao and nome_cartao.strip():
            return "Cartão de Crédito"
        
        # Regra 2 e 3: Baseado no sinal
        if valor < 0:
            return "Despesas"
        else:
            return "Receitas"
    
    def _get_sequence_for_duplicate(self, chave_unica: str) -> int:
        """
        Retorna número de sequência para a chave única
        
        Args:
            chave_unica: "data|lancamento_upper|valor"
            
        Returns:
            1 para primeira ocorrência, 2 para segunda, 3 para terceira, ..., N para N-ésima
            
        Exemplos:
            >>> marker = TransactionMarker(user_id=1)
            >>> marker._get_sequence_for_duplicate("15/10/2025|PIX|100.00")
            1  # Primeira vez
            >>> marker._get_sequence_for_duplicate("15/10/2025|PIX|100.00")
            2  # Segunda vez (duplicado!)
            >>> marker._get_sequence_for_duplicate("15/10/2025|PIX|100.00")
            3  # Terceira vez
            >>> marker._get_sequence_for_duplicate("15/10/2025|PIX|100.00")
            4  # Quarta vez
            >>> # ... funciona para qualquer N
        """
        if chave_unica in self.seen_transactions:
            # Já vimos antes - incrementa contador
            self.seen_transactions[chave_unica] += 1
        else:
            # Primeira ocorrência
            self.seen_transactions[chave_unica] = 1
        
        return self.seen_transactions[chave_unica]
    
    def mark_transaction(self, raw: RawTransaction) -> MarkedTransaction:
        """
        Marca uma transação raw com IDs
        
        Args:
            raw: RawTransaction da Fase 1
            
        Returns:
            MarkedTransaction com IDs marcados
        """
        try:
            # 1. Detectar parcela e extrair estabelecimento base
            info_parcela = extrair_parcela_do_estabelecimento(raw.lancamento)
            
            if info_parcela:
                # Tem parcela
                estabelecimento_base = info_parcela['estabelecimento_base']
                parcela_atual = info_parcela['parcela']
                total_parcelas = info_parcela['total']
            else:
                # Sem parcela
                estabelecimento_base = raw.lancamento
                parcela_atual = None
                total_parcelas = None
            
            # 2. Valor positivo
            valor_positivo = abs(raw.valor)
            valor_arredondado = arredondar_2_decimais(valor_positivo)
            
            # 2b. Determinar TipoTransacao baseado em cartão e valor
            tipo_transacao = self._determinar_tipo_transacao(raw.nome_cartao, raw.valor)
            
            # 3. Detectar duplicados no arquivo e obter sequência
            # ESTRATÉGIA v4.2.3 CONDICIONAL COM NORMALIZAÇÃO COMPLETA:
            # - SEMPRE: Normaliza espaços múltiplos + UPPERCASE para evitar hashes diferentes
            # - FATURA: Normaliza parcela ("LOJA 01/05" → "LOJA (1/5)")
            # - EXTRATO: NÃO normaliza parcela (mantém original, pois "BA04/10" é parte do nome)
            tipo_doc_lower = raw.tipo_documento.lower() if raw.tipo_documento else ''
            is_fatura = 'fatura' in tipo_doc_lower or 'cartao' in tipo_doc_lower or 'cartão' in tipo_doc_lower
            
            # 2c. Ano e Mes: FATURA → da MesFatura | EXTRATO → da Data da transação
            if is_fatura and raw.mes_fatura:
                # Fatura: Ano e Mes vêm da MesFatura (ex: 202601 → ano=2026, mes=1)
                mes_fatura = raw.mes_fatura.replace('-', '').strip()
                if len(mes_fatura) >= 6:
                    ano = int(mes_fatura[:4])
                    mes = int(mes_fatura[4:6])
                else:
                    ano, mes = self._extrair_ano_mes(raw.data)
            else:
                # Extrato: Ano e Mes da Data da transação
                ano, mes = self._extrair_ano_mes(raw.data)
            
            # v5: remove tudo que não é [A-Z0-9] da base — invariante à renderização PDF/CSV
            if info_parcela and is_fatura:
                # Parcelada: normaliza base + recompõe (p/t)
                base_norm = re.sub(r'[^A-Z0-9]', '', estabelecimento_base.upper())
                estab_normalizado = f"{base_norm} ({parcela_atual}/{total_parcelas})"
            else:
                # Sem parcela (ou extrato): remove tudo que não é [A-Z0-9]
                estab_normalizado = re.sub(r'[^A-Z0-9]', '', raw.lancamento.upper())

            estab_hash = estab_normalizado
            valor_hash = arredondar_2_decimais(raw.valor)  # VALOR EXATO (com sinal)
            
            chave_unica = f"{raw.data}|{estab_hash}|{valor_hash:.2f}"
            sequencia = self._get_sequence_for_duplicate(chave_unica)
            
            # 4. Gerar IdTransacao (v4.2.1 - com user_id + formato normalizado apenas para faturas)
            id_transacao = generate_id_transacao(
                data=raw.data,
                estabelecimento=estab_normalizado,  # Normalizado apenas se fatura
                valor=raw.valor,  # VALOR EXATO (com sinal)
                user_id=self.user_id,  # Isola por usuário
                sequencia=sequencia
            )
            
            # 5. Gerar IdParcela se tem parcela
            # FÓRMULA OBRIGATÓRIA: estab|valor|total|user_id (user_id SEMPRE no hash!)
            id_parcela = None
            if info_parcela and total_parcelas:
                import hashlib
                # v5: mesma normalização do estab_hash (remove [^A-Z0-9])
                estab_normalizado_parcela = re.sub(r'[^A-Z0-9]', '', estabelecimento_base.upper())
                chave = f"{estab_normalizado_parcela}|{valor_arredondado:.2f}|{total_parcelas}|{self.user_id}"
                assert self.user_id is not None, "user_id OBRIGATÓRIO no hash IdParcela"
                id_parcela = hashlib.md5(chave.encode()).hexdigest()[:16]
                logger.debug(f"IdParcela: {id_parcela} para {estab_normalizado_parcela} {parcela_atual}/{total_parcelas} (user_id={self.user_id})")
                logger.debug(f"  Chave IdParcela: '{chave}'")
            
            # 7. Criar MarkedTransaction
            marked = MarkedTransaction(
                # Copiar campos de RawTransaction
                banco=raw.banco,
                tipo_documento=raw.tipo_documento,
                nome_arquivo=raw.nome_arquivo,
                data_criacao=raw.data_criacao,
                data=raw.data,
                lancamento=raw.lancamento,
                valor=raw.valor,
                nome_cartao=raw.nome_cartao,
                final_cartao=raw.final_cartao,
                mes_fatura=raw.mes_fatura,
                # Novos campos (Fase 2)
                id_transacao=id_transacao,
                estabelecimento_base=estabelecimento_base,
                valor_positivo=valor_positivo,
                id_parcela=id_parcela,
                parcela_atual=parcela_atual,
                total_parcelas=total_parcelas,
                tipo_transacao=tipo_transacao,  # ✅ NOVO
                ano=ano,                          # ✅ NOVO
                mes=mes,                          # ✅ NOVO
            )
            
            logger.debug(
                f"Transação marcada: {estabelecimento_base[:30]}... | "
                f"ID: {id_transacao} | Parcela: {parcela_atual}/{total_parcelas} | "
                f"Tipo: {tipo_transacao} | Data: {mes:02d}/{ano} | "
                f"Valor: {valor_positivo:.2f}"
            )
            
            return marked
            
        except Exception as e:
            logger.error(f"❌ Erro ao marcar transação: {str(e)}", exc_info=True)
            raise
    
    def mark_batch(self, raw_transactions: list[RawTransaction]) -> list[MarkedTransaction]:
        """
        Marca lote de transações
        
        Args:
            raw_transactions: Lista de RawTransaction
            
        Returns:
            Lista de MarkedTransaction
        """
        logger.info(f"Marcando {len(raw_transactions)} transações...")
        
        marked_transactions = []
        for i, raw in enumerate(raw_transactions, 1):
            try:
                marked = self.mark_transaction(raw)
                marked_transactions.append(marked)
                
                if i % 50 == 0:
                    logger.info(f"  Progresso: {i}/{len(raw_transactions)} transações marcadas")
                    
            except Exception as e:
                logger.error(f"Erro ao marcar transação {i}: {str(e)}")
                # Continuar com próxima transação
        
        logger.info(f"✅ Marcação concluída: {len(marked_transactions)}/{len(raw_transactions)}")
        return marked_transactions
