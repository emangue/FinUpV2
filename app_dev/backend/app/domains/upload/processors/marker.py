"""
Transaction Marker - Fase 2
Marca transações com IDs únicos (IdTransacao, IdParcela)
Integra hasher.py e normalizer.py
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


class TransactionMarker:
    """
    Marca transações com IDs únicos (v4.0.0 - Simplificado)
    """
    
    def __init__(self):
        """Inicializa marker com controle de duplicados por arquivo"""
        logger.debug("TransactionMarker inicializado - v4.1.0 (hash recursivo)")
        # Dict para rastrear duplicados dentro do arquivo
        # Chave: "data|lancamento_upper|valor" → Valor: contador de ocorrências
        # Ex: "15/10/2025|PIX TRANSF EMANUEL15/10|1000.00" → 1, depois 2, depois 3, ..., N
        self.seen_transactions = {}
    
    def _get_sequence_for_duplicate(self, chave_unica: str) -> int:
        """
        Retorna número de sequência para a chave única
        
        Args:
            chave_unica: "data|lancamento_upper|valor"
            
        Returns:
            1 para primeira ocorrência, 2 para segunda, 3 para terceira, ..., N para N-ésima
            
        Exemplos:
            >>> marker = TransactionMarker()
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
            
            # 3. Detectar duplicados no arquivo e obter sequência
            # Normaliza para UPPERCASE (case-insensitive)
            lancamento_upper = raw.lancamento.upper().strip()
            chave_unica = f"{raw.data}|{lancamento_upper}|{valor_arredondado:.2f}"
            sequencia = self._get_sequence_for_duplicate(chave_unica)
            
            # 4. Gerar IdTransacao (v4.1.0 - hash recursivo para duplicados)
            # seq=1: hash(chave)
            # seq=2: hash(hash_seq1)
            # seq=N: hash aplicado N-1 vezes recursivamente
            # Garante hashes únicos para QUALQUER quantidade de duplicados
            id_transacao = generate_id_transacao(
                data=raw.data,
                estabelecimento=raw.lancamento,  # ORIGINAL (com parcelas, datas, tudo)
                valor=valor_arredondado,
                sequencia=sequencia
            )
            
            # 5. Gerar IdParcela se tem parcela (usando mesma lógica de populate_id_parcela.py)
            id_parcela = None
            if info_parcela and total_parcelas:
                # IMPORTANTE: Usar estabelecimento NORMALIZADO para match com base_parcelas
                import hashlib
                estab_normalizado_parcela = normalizar_estabelecimento(estabelecimento_base)
                chave = f"{estab_normalizado_parcela}|{valor_arredondado:.2f}|{total_parcelas}"
                id_parcela = hashlib.md5(chave.encode()).hexdigest()[:16]
                logger.debug(f"IdParcela: {id_parcela} para {estab_normalizado_parcela} {parcela_atual}/{total_parcelas}")
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
                # Novos campos
                id_transacao=id_transacao,
                estabelecimento_base=estabelecimento_base,
                valor_positivo=valor_positivo,
                id_parcela=id_parcela,
                parcela_atual=parcela_atual,
                total_parcelas=total_parcelas,
            )
            
            logger.debug(
                f"Transação marcada: {estabelecimento_base[:30]}... | "
                f"ID: {id_transacao} | Parcela: {parcela_atual}/{total_parcelas} | "
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
