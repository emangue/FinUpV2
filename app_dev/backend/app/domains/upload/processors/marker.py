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
    Marca transações com IDs únicos
    """
    
    def __init__(self):
        self.seen_transactions = {}  # {chave_unica: count} para rastrear duplicatas
        logger.debug("TransactionMarker inicializado")
    
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
            
            # 3. Gerar chave única para detectar duplicatas no arquivo
            chave_unica = f"{raw.data}|{estabelecimento_base}|{valor_arredondado:.2f}"
            
            # 4. Verificar se é duplicata dentro do arquivo e obter row_number
            row_number = self._get_row_number_for_duplicate(chave_unica)
            
            # 5. Gerar IdTransacao (FNV-1a) com row_number se for duplicata
            id_transacao = generate_id_transacao(
                data=raw.data,
                estabelecimento=estabelecimento_base,
                valor=valor_arredondado,
                timestamp_micro=str(row_number) if row_number > 0 else None
            )
            
            # 6. Gerar IdParcela se tem parcela (usando mesma lógica de populate_id_parcela.py)
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
    
    def _get_row_number_for_duplicate(self, chave_unica: str) -> int:
        """
        Retorna row_number sequencial para transações duplicadas no arquivo
        
        Para transações idênticas (mesma data, estabelecimento, valor),
        retorna um número sequencial (0, 1, 2...) para diferenciar.
        
        Args:
            chave_unica: Chave "Data|Estabelecimento|Valor"
            
        Returns:
            int: 0 para primeira ocorrência, 1+ para duplicatas
        """
        if chave_unica not in self.seen_transactions:
            # Primeira ocorrência desta transação
            self.seen_transactions[chave_unica] = 0
            return 0
        
        # Duplicata detectada - incrementar contador
        self.seen_transactions[chave_unica] += 1
        row_number = self.seen_transactions[chave_unica]
        
        logger.info(
            f"🔄 Transação duplicada #{row_number + 1} detectada no arquivo: {chave_unica}"
        )
        
        return row_number
