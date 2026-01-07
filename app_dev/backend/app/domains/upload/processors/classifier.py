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


class CascadeClassifier:
    """
    Classificador em cascata com 5 níveis hierárquicos
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.stats = {
            'total': 0,
            'Base Parcelas': 0,
            'Base Padrões': 0,
            'Journal Entries': 0,
            'Marcas Gerais': 0,
            'Não Classificado': 0,
        }
        logger.debug(f"CascadeClassifier inicializado para user_id={user_id}")
    
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
            # Tentar níveis em ordem de prioridade
            
            # Nível 1: Base Parcelas
            if marked.id_parcela:
                result = self._classify_nivel1_parcelas(marked)
                if result:
                    self.stats['Base Parcelas'] += 1
                    return result
            
            # Nível 2: Base Padrões
            result = self._classify_nivel2_padroes(marked)
            if result:
                self.stats['Base Padrões'] += 1
                return result
            
            # Nível 3: Journal Entries
            result = self._classify_nivel3_journal(marked)
            if result:
                self.stats['Journal Entries'] += 1
                return result
            
            # Nível 4: Marcas Gerais
            result = self._classify_nivel4_marcas(marked)
            if result:
                self.stats['Marcas Gerais'] += 1
                return result
            
            # Nível 5: Não Classificado
            self.stats['Não Classificado'] += 1
            return self._classify_nivel5_nao_classificado(marked)
            
        except Exception as e:
            logger.error(f"❌ Erro ao classificar: {str(e)}", exc_info=True)
            self.stats['Não Classificado'] += 1
            return self._classify_nivel5_nao_classificado(marked)
    
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
                logger.debug(f"✅ Nível 1 (Parcelas): {marked.estabelecimento_base[:30]}...")
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=parcela.GRUPO,
                    subgrupo=parcela.SUBGRUPO,
                    tipo_gasto=parcela.TipoGasto,
                    categoria_geral=parcela.CategoriaGeral,
                    origem_classificacao='Base Parcelas',
                )
        
        except Exception as e:
            logger.error(f"Erro Nível 1: {str(e)}")
        
        return None
    
    def _classify_nivel2_padroes(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 2: Base Padrões
        Usa padrões aprendidos com alta confiança
        """
        try:
            # Import aqui para evitar circular import
            from app.domains.transactions.models import BasePadroes
            from app.shared.utils import get_faixa_valor, normalizar
            
            # Normalizar estabelecimento
            estab_normalizado = normalizar(marked.estabelecimento_base)
            
            # Faixa de valor
            faixa = get_faixa_valor(marked.valor_positivo)
            
            # Query base_padroes
            padrao = self.db.query(BasePadroes).filter(
                and_(
                    BasePadroes.estabelecimento_normalizado == estab_normalizado,
                    BasePadroes.faixa_valor == faixa,
                    BasePadroes.confianca == 'alta',
                    BasePadroes.user_id == self.user_id
                )
            ).first()
            
            if padrao:
                logger.debug(f"✅ Nível 2 (Padrões): {marked.estabelecimento_base[:30]}...")
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=padrao.GRUPO,
                    subgrupo=padrao.SUBGRUPO,
                    tipo_gasto=padrao.TipoGasto,
                    categoria_geral=padrao.CategoriaGeral,
                    origem_classificacao='Base Padrões',
                )
        
        except Exception as e:
            logger.error(f"Erro Nível 2: {str(e)}")
        
        return None
    
    def _classify_nivel3_journal(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 3: Journal Entries
        Usa histórico dos últimos 12 meses (≥2 ocorrências com mesma classificação)
        """
        try:
            # Import aqui para evitar circular import
            from app.domains.transactions.models import JournalEntry
            
            # Data limite: 12 meses atrás
            data_limite = datetime.now() - timedelta(days=365)
            
            # Query journal_entries agrupando por estabelecimento_base
            # Contar ocorrências de cada classificação
            query = self.db.query(
                JournalEntry.GRUPO,
                JournalEntry.SUBGRUPO,
                JournalEntry.TipoGasto,
                JournalEntry.CategoriaGeral,
                func.count().label('count')
            ).filter(
                and_(
                    JournalEntry.EstabelecimentoBase == marked.estabelecimento_base,
                    JournalEntry.user_id == self.user_id,
                    JournalEntry.DataPostagem >= data_limite,
                    JournalEntry.GRUPO.isnot(None)
                )
            ).group_by(
                JournalEntry.GRUPO,
                JournalEntry.SUBGRUPO,
                JournalEntry.TipoGasto,
                JournalEntry.CategoriaGeral
            ).order_by(func.count().desc()).all()
            
            # Verificar se tem ≥2 ocorrências
            if query and query[0].count >= 2:
                result = query[0]
                logger.debug(f"✅ Nível 3 (Journal): {marked.estabelecimento_base[:30]}... ({result.count}x)")
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=result.GRUPO,
                    subgrupo=result.SUBGRUPO,
                    tipo_gasto=result.TipoGasto,
                    categoria_geral=result.CategoriaGeral,
                    origem_classificacao='Journal Entries',
                )
        
        except Exception as e:
            logger.error(f"Erro Nível 3: {str(e)}")
        
        return None
    
    def _classify_nivel4_marcas(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 4: Marcas Gerais
        Usa keywords de base_marcacoes validadas contra BaseMarcacao
        """
        try:
            # Import aqui para evitar circular import
            from app.domains.categories.models import BaseMarcacoes, BaseMarcacao
            
            # Query base_marcacoes que contém keywords no estabelecimento
            marcacoes = self.db.query(BaseMarcacoes).filter(
                BaseMarcacoes.user_id == self.user_id
            ).all()
            
            estab_lower = marked.estabelecimento_base.lower()
            
            for marcacao in marcacoes:
                keywords = [kw.strip().lower() for kw in marcacao.palavras_chave.split(',')]
                
                # Verificar se alguma keyword está no estabelecimento
                for keyword in keywords:
                    if keyword and keyword in estab_lower:
                        # Validar contra BaseMarcacao
                        validacao = self.db.query(BaseMarcacao).filter(
                            and_(
                                BaseMarcacao.GRUPO == marcacao.grupo_sugerido,
                                BaseMarcacao.SUBGRUPO == marcacao.subgrupo_sugerido,
                                BaseMarcacao.Ativo == 1,
                                BaseMarcacao.user_id == self.user_id
                            )
                        ).first()
                        
                        if validacao:
                            logger.debug(f"✅ Nível 4 (Marcas): {marked.estabelecimento_base[:30]}... (keyword: {keyword})")
                            
                            return ClassifiedTransaction(
                                **marked.__dict__,
                                grupo=marcacao.grupo_sugerido,
                                subgrupo=marcacao.subgrupo_sugerido,
                                tipo_gasto=validacao.TipoGasto,
                                categoria_geral=validacao.CategoriaGeral,
                                origem_classificacao='Marcas Gerais',
                            )
        
        except Exception as e:
            logger.error(f"Erro Nível 4: {str(e)}")
        
        return None
    
    def _classify_nivel5_nao_classificado(self, marked: MarkedTransaction) -> ClassifiedTransaction:
        """
        Nível 5: Não Classificado
        Fallback quando nenhum nível anterior encontrou classificação
        """
        logger.debug(f"⚠️ Nível 5 (Não Classificado): {marked.estabelecimento_base[:30]}...")
        
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
