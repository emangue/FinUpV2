"""
Cascade Classifier - Fase 3
Classifica transações em 5 níveis hierárquicos
"""

import logging
from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from .marker import MarkedTransaction
from .generic_rules_classifier import GenericRulesClassifier
from app.core.database import Base

logger = logging.getLogger(__name__)


@dataclass
class ClassifiedTransaction(MarkedTransaction):
    """
    Transação classificada
    Extends MarkedTransaction com campos de classificação
    """
    
    grupo: Optional[str] = None
    subgrupo: Optional[str] = None
    tipo_gasto: Optional[str] = None
    categoria_geral: Optional[str] = None
    origem_classificacao: str = 'Não Classificado'
    padrao_buscado: Optional[str] = None  # Debug: padrão montado para busca
    marcacao_ia: Optional[str] = None  # Sugestão da base_marcacoes (sempre preenchido)


class CascadeClassifier:
    """
    Classificador em cascata com 5 níveis hierárquicos
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.generic_classifier = GenericRulesClassifier()  # Classificador de regras genéricas
        self.stats = {
            'total': 0,
            'base_parcelas': 0,
            'base_padroes': 0,
            'journal_entries': 0,
            'regras_genericas': 0,
            'nao_classificado': 0,
        }
        logger.debug(f"CascadeClassifier inicializado para user_id={user_id}")
    
    def _determine_categoria_geral(self, grupo: Optional[str], valor: float) -> Optional[str]:
        """
        Determina CategoriaGeral baseado no GRUPO e valor da transação
        
        Regras:
        - Transferência Entre Contas → Transferência
        - Investimentos → Investimentos
        - Valor positivo → Receita
        - Valor negativo → Despesa
        """
        if not grupo:
            return None
        
        # Normalizar grupo para comparação
        grupo_lower = grupo.lower().strip()
        
        # Regra 1: Transferência
        if 'transferencia' in grupo_lower or 'transferência' in grupo_lower:
            return 'Transferência'
        
        # Regra 2: Investimentos
        if 'investimento' in grupo_lower:
            return 'Investimentos'
        
        # Regra 3: Baseado no sinal do valor
        if valor >= 0:
            return 'Receita'
        else:
            return 'Despesa'
    
    def classify(self, marked: MarkedTransaction) -> ClassifiedTransaction:
        """
        Classifica uma transação marcada
        
        Args:
            marked: MarkedTransaction da Fase 2
            
        Returns:
            ClassifiedTransaction com classificação
        """
        self.stats['total'] += 1
        
        try:
            # MONTAR PADRÃO PARA TODAS AS TRANSAÇÕES (como n8n)
            from app.shared.utils import get_faixa_valor, normalizar_estabelecimento
            
            estab_normalizado = normalizar_estabelecimento(marked.estabelecimento_base)
            faixa = get_faixa_valor(marked.valor_positivo)
            padrao_montado = f"{estab_normalizado} [{faixa}]"
            
            # BUSCAR MARCAÇÃO IA PARA TODAS AS TRANSAÇÕES (base_marcacoes)
            marcacao_ia = self._buscar_marcacao_ia(marked.estabelecimento_base)
            
            logger.debug(f"📍 Padrão: '{padrao_montado}' | MarcaçãoIA: '{marcacao_ia}' | R$ {marked.valor_positivo:.2f}")
            
            # Tentar níveis em ordem de prioridade
            
            # Nível 1: Base Parcelas
            if marked.id_parcela:
                result = self._classify_nivel1_parcelas(marked)
                if result:
                    result.padrao_buscado = padrao_montado
                    result.marcacao_ia = marcacao_ia
                    self.stats['base_parcelas'] += 1
                    return result
            
            # Nível 2: Base Padrões
            result = self._classify_nivel2_padroes(marked, padrao_montado)
            if result:
                result.marcacao_ia = marcacao_ia
                self.stats['base_padroes'] += 1
                return result
            
            # Nível 3: Journal Entries
            result = self._classify_nivel3_journal(marked)
            if result:
                result.padrao_buscado = padrao_montado
                result.marcacao_ia = marcacao_ia
                self.stats['journal_entries'] += 1
                return result
            
            # Nível 4: Regras Genéricas (hardcoded n8n)
            result = self._classify_nivel4_regras_genericas(marked)
            if result:
                result.padrao_buscado = padrao_montado
                result.marcacao_ia = marcacao_ia
                self.stats['regras_genericas'] += 1
                return result
            
            # Nível 5: Não Classificado
            self.stats['nao_classificado'] += 1
            result = self._classify_nivel5_nao_classificado(marked)
            result.padrao_buscado = padrao_montado
            result.marcacao_ia = marcacao_ia
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao classificar: {str(e)}", exc_info=True)
            self.stats['nao_classificado'] += 1
            result = self._classify_nivel5_nao_classificado(marked)
            
            # Tentar montar padrão e marcação IA mesmo com erro
            try:
                from app.shared.utils import get_faixa_valor, normalizar_estabelecimento
                estab_normalizado = normalizar_estabelecimento(marked.estabelecimento_base)
                faixa = get_faixa_valor(marked.valor_positivo)
                result.padrao_buscado = f"{estab_normalizado} [{faixa}]"
                result.marcacao_ia = self._buscar_marcacao_ia(marked.estabelecimento_base)
            except:
                result.padrao_buscado = "ERRO AO MONTAR PADRÃO"
                result.marcacao_ia = None
            
            return result
            return result
    
    def classify_batch(self, marked_transactions: list[MarkedTransaction]) -> list[ClassifiedTransaction]:
        """
        Classifica lote de transações
        
        Args:
            marked_transactions: Lista de MarkedTransaction
            
        Returns:
            Lista de ClassifiedTransaction
        """
        logger.info(f"Classificando {len(marked_transactions)} transações...")
        
        classified_transactions = []
        for i, marked in enumerate(marked_transactions, 1):
            classified = self.classify(marked)
            classified_transactions.append(classified)
            
            if i % 50 == 0:
                logger.info(f"  Progresso: {i}/{len(marked_transactions)} transações classificadas")
        
        logger.info(f"✅ Classificação concluída: {len(classified_transactions)} transações")
        self._log_stats()
        
        return classified_transactions
    
    def _classify_nivel1_parcelas(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 1: Base Parcelas
        Copia classificação de parcelas anteriores usando IdParcela
        """
        try:
            # Import aqui para evitar circular import
            from app.domains.transactions.models import BaseParcelas
            
            parcela = self.db.query(BaseParcelas).filter(
                and_(
                    BaseParcelas.id_parcela == marked.id_parcela,
                    BaseParcelas.user_id == self.user_id
                )
            ).first()
            
            if parcela:
                logger.debug(f"✅ Nível 1 (Parcelas): {marked.estabelecimento_base[:30]}... (status: {parcela.status})")
                
                grupo = parcela.grupo_sugerido
                categoria_geral = self._determine_categoria_geral(grupo, marked.valor)
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=grupo,
                    subgrupo=parcela.subgrupo_sugerido,
                    tipo_gasto=parcela.tipo_gasto_sugerido,
                    categoria_geral=categoria_geral,
                    origem_classificacao='Base Parcelas',
                )
        
        except Exception as e:
            logger.error(f"Erro Nível 1: {str(e)}")
        
        return None
    
    def _classify_nivel2_padroes(self, marked: MarkedTransaction, padrao_montado: str) -> Optional[ClassifiedTransaction]:
        """
        Nível 2: Base Padrões
        Usa padrões aprendidos com alta confiança
        LÓGICA DO N8N: Recebe padrão já montado = "ESTABELECIMENTO [FAIXA]"
        """
        try:
            # Import aqui para evitar circular import
            from app.domains.patterns.models import BasePadroes
            from app.shared.utils import normalizar_estabelecimento
            
            # Padrão já foi montado no classify() - usar diretamente
            logger.debug(f"🔍 Buscando padrão: '{padrao_montado}'")
            
            # Buscar padrão EXATO (segmentado) ou fallback para padrão simples
            # Tenta primeiro com faixa no nome
            padrao = self.db.query(BasePadroes).filter(
                and_(
                    BasePadroes.padrao_estabelecimento == padrao_montado,
                    BasePadroes.confianca == 'alta',
                    BasePadroes.user_id == self.user_id
                )
            ).first()
            
            # Se não achar segmentado, tenta padrão simples (sem faixa)
            if not padrao:
                estab_normalizado = normalizar_estabelecimento(marked.estabelecimento_base)
                padrao = self.db.query(BasePadroes).filter(
                    and_(
                        BasePadroes.padrao_estabelecimento == estab_normalizado,
                        BasePadroes.confianca == 'alta',
                        BasePadroes.user_id == self.user_id
                    )
                ).first()
                if padrao:
                    logger.debug(f"✅ Match padrão simples: '{estab_normalizado}'")
            else:
                logger.debug(f"✅ Match padrão segmentado: '{padrao_montado}'")
            
            if padrao:
                grupo = padrao.grupo_sugerido
                categoria_geral = self._determine_categoria_geral(grupo, marked.valor)
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=grupo,
                    subgrupo=padrao.subgrupo_sugerido,
                    tipo_gasto=padrao.tipo_gasto_sugerido,
                    categoria_geral=categoria_geral,
                    origem_classificacao='Base Padrões',
                    padrao_buscado=padrao_montado  # DEBUG: mostrar padrão usado
                )
            else:
                logger.debug(f"❌ Nenhum padrão encontrado para: '{padrao_montado}'")
        
        except Exception as e:
            logger.error(f"Erro Nível 2: {str(e)}")
        
        return None
    
    def _classify_nivel3_journal(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 3: Journal Entries
        Usa histórico com matching por tokens válidos (igual ao n8n)
        """
        try:
            # Import aqui para evitar circular import
            from app.domains.transactions.models import JournalEntry
            from app.shared.utils import tokensValidos, intersecaoCount, toNumberFlexible
            
            # Buscar todo o histórico com classificação completa
            historico = self.db.query(JournalEntry).filter(
                and_(
                    JournalEntry.user_id == self.user_id,
                    JournalEntry.GRUPO.isnot(None),
                    JournalEntry.SUBGRUPO.isnot(None),
                    JournalEntry.TipoGasto.isnot(None)
                )
            ).all()
            
            if not historico:
                return None
            
            # Implementar lógica igual ao n8n
            tokens_estab = tokensValidos(marked.estabelecimento_base)
            v_trans = abs(toNumberFlexible(marked.valor_positivo))
            
            candidatos = []
            for h in historico:
                tokens_hist = tokensValidos(h.Estabelecimento or '')
                inter = intersecaoCount(tokens_hist, tokens_estab)
                v_hist = abs(toNumberFlexible(h.Valor))
                
                # Lógica de valor igual ao n8n
                if not (v_trans and v_hist):  # Se algum valor inválido
                    valor_ok = True
                elif abs(v_hist - v_trans) <= 5:  # Diferença <= 5
                    valor_ok = True
                else:  # Diferença percentual <= 20%
                    valor_ok = abs(v_hist - v_trans) / max(v_hist, v_trans) <= 0.20
                
                completo = bool(h.GRUPO and h.SUBGRUPO and h.TipoGasto)
                
                # Calcular limiar de interseção igual ao n8n
                limiar = 1 if min(len(tokens_estab), len(tokens_hist)) == 1 else 2
                
                if completo and valor_ok and inter >= limiar:
                    candidatos.append({
                        'h': h,
                        'inter': inter,
                        'valor_ok': valor_ok,
                        'data': h.Data or datetime.min
                    })
            
            if not candidatos:
                return None
            
            # Ordenar por data mais recente primeiro (igual ao n8n)
            candidatos.sort(key=lambda x: x['data'], reverse=True)
            
            # Filtrar PIX igual ao n8n (não usar histórico de PIX)
            estab_upper = marked.estabelecimento_base.upper()
            if 'PIX' in estab_upper:
                logger.debug(f"❌ Nível 3 (Journal): PIX ignorado: {marked.estabelecimento_base[:30]}...")
                return None
            
            # Retornar o primeiro candidato (mais recente)
            escolhido = candidatos[0]['h']
            logger.debug(f"✅ Nível 3 (Journal): {marked.estabelecimento_base[:30]}... (inter: {candidatos[0]['inter']}, valor_ok: {candidatos[0]['valor_ok']})")
            
            grupo = escolhido.GRUPO
            categoria_geral = self._determine_categoria_geral(grupo, marked.valor)
            
            return ClassifiedTransaction(
                **marked.__dict__,
                grupo=grupo,
                subgrupo=escolhido.SUBGRUPO,
                tipo_gasto=escolhido.TipoGasto,
                categoria_geral=categoria_geral,
                origem_classificacao='Journal Entries',
            )
        
        except Exception as e:
            logger.error(f"Erro Nível 3: {str(e)}")
        
        return None
    
    def _classify_nivel4_regras_genericas(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 4: Regras Genéricas (hardcoded do n8n)
        Usa classificador de regras genéricas independente de banco
        """
        try:
            resultado = self.generic_classifier.classify(marked.estabelecimento_base)
            
            if resultado:
                logger.debug(f"✅ Nível 4 (Regras Genéricas): {marked.estabelecimento_base[:30]}... (prioridade: {resultado['prioridade']})")
                
                grupo = resultado['grupo']
                categoria_geral = self._determine_categoria_geral(grupo, marked.valor)
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=grupo,
                    subgrupo=resultado['subgrupo'],
                    tipo_gasto=resultado['tipo_gasto'],
                    categoria_geral=categoria_geral,
                    origem_classificacao='Regras Genéricas',
                )
        
        except Exception as e:
            logger.error(f"Erro Nível 4.5: {str(e)}")
        
        return None
    
    def _buscar_marcacao_ia(self, estabelecimento: str) -> Optional[str]:
        """
        Busca sugestão de marcação IA para QUALQUER transação
        Usa apenas regras genéricas (hardcoded do n8n)
        
        Returns:
            String formatada: "GRUPO > SUBGRUPO" ou None
        """
        try:
            # PRIMEIRA TENTATIVA: Regras genéricas (prioridade)
            marcacao_generica = self.generic_classifier.get_marcacao_ia(estabelecimento)
            if marcacao_generica:
                logger.debug(f"🎯 MarcaçãoIA (Regras Genéricas): {marcacao_generica}")
                return marcacao_generica
            
            # Não há segunda tentativa - só regras genéricas
            return None
        
        except Exception as e:
            logger.error(f"Erro ao buscar marcação IA: {str(e)}")
            return None
    
    def _classify_nivel5_nao_classificado(self, marked: MarkedTransaction) -> ClassifiedTransaction:
        """
        Nível 5: Não Classificado
        Fallback quando nenhum nível anterior encontrou classificação
        """
        logger.debug(f"⚠️ Nível 5 (Não Classificado): {marked.estabelecimento_base[:30]}...")
        
        # Categoria geral None para não classificado (sem grupo definido)
        return ClassifiedTransaction(
            **marked.__dict__,
            grupo=None,
            subgrupo=None,
            tipo_gasto=None,
            categoria_geral=None,
            origem_classificacao='Não Classificado',
        )
    
    def _log_stats(self):
        """Log estatísticas de classificação"""
        logger.info("📊 Estatísticas de Classificação:")
        for nivel, count in self.stats.items():
            if nivel != 'total':
                pct = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                logger.info(f"  {nivel}: {count} ({pct:.1f}%)")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas de classificação"""
        return self.stats.copy()
