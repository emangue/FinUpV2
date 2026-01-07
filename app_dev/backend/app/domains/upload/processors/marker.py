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
    generate_id_simples,
    normalizar_estabelecimento,
    detectar_parcela,
    arredondar_2_decimais
)

from .raw.base import RawTransaction

logger = logging.getLogger(__name__)


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
        self.collision_counts = {}  # Track collisions for suffix
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
            # 1. Normalizar estabelecimento
            estab_normalizado = normalizar_estabelecimento(raw.lancamento)
            
            # 2. Detectar parcela (retorna {'parcela': int, 'total': int} ou None)
            info_parcela = detectar_parcela(raw.lancamento, raw.tipo_documento)
            
            if info_parcela:
                # Tem parcela - remover XX/YY do final do estabelecimento
                tem_parcela = True
                parcela_atual = info_parcela['parcela']
                total_parcelas = info_parcela['total']
                # Remover padrão XX/YY do final
                estabelecimento_base = re.sub(r'\s*\(?(\d{1,2})/(\d{1,2})\)?\s*$', '', raw.lancamento).strip()
            else:
                # Sem parcela
                tem_parcela = False
                parcela_atual = None
                total_parcelas = None
                estabelecimento_base = raw.lancamento
            
            # 3. Valor positivo
            valor_positivo = abs(raw.valor)
            valor_arredondado = arredondar_2_decimais(valor_positivo)
            
            # 3. Gerar IdTransacao (FNV-1a)
            id_transacao = generate_id_simples(
                data=raw.data,
                estabelecimento=estabelecimento_base,
                valor=valor_arredondado
            )
            
            # 4. Handle collision (adicionar sufixo se necessário)
            id_transacao = self._handle_collision(id_transacao)
            
            # 5. Gerar IdParcela se tem parcela
            id_parcela = None
            if tem_parcela and total_parcelas:
                # IdParcela = MD5(estabelecimento_base + valor + total)
                from hashlib import md5
                parcela_str = f"{estabelecimento_base}_{valor_arredondado}_{total_parcelas}"
                id_parcela = md5(parcela_str.encode()).hexdigest()[:16]
            
            # 6. Criar MarkedTransaction
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
    
    def _handle_collision(self, id_transacao: str) -> str:
        """
        Handle hash collision adicionando sufixo
        
        Args:
            id_transacao: ID base
            
        Returns:
            ID único com sufixo se necessário
        """
        if id_transacao not in self.collision_counts:
            self.collision_counts[id_transacao] = 0
            return id_transacao
        
        # Collision detected
        self.collision_counts[id_transacao] += 1
        suffix = self.collision_counts[id_transacao]
        
        logger.warning(f"⚠️ Collision detectada para {id_transacao}, usando sufixo _{suffix}")
        
        return f"{id_transacao}_{suffix}"
