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
            'Base Parcelas': 0,
            'Base Padrões': 0,
            'Journal Entries': 0,
            'Marcas Gerais': 0,
            'Regras Genéricas': 0,
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
                    self.stats['Base Parcelas'] += 1
                    return result
            
            # Nível 2: Base Padrões
            result = self._classify_nivel2_padroes(marked, padrao_montado)
            if result:
                result.marcacao_ia = marcacao_ia
                self.stats['Base Padrões'] += 1
                return result
            
            # Nível 3: Journal Entries
            result = self._classify_nivel3_journal(marked)
            if result:
                result.padrao_buscado = padrao_montado
                result.marcacao_ia = marcacao_ia
                self.stats['Journal Entries'] += 1
                return result
            
            # Nível 4: Marcas Gerais
            result = self._classify_nivel4_marcas(marked)
            if result:
                result.padrao_buscado = padrao_montado
                result.marcacao_ia = marcacao_ia
                self.stats['Marcas Gerais'] += 1
                return result
            
            # Nível 4.5: Regras Genéricas (hardcoded n8n)
            result = self._classify_nivel45_regras_genericas(marked)
            if result:
                result.padrao_buscado = padrao_montado
                result.marcacao_ia = marcacao_ia
                self.stats['Regras Genéricas'] += 1
                return result
            
            # Nível 5: Não Classificado
            self.stats['Não Classificado'] += 1
            result = self._classify_nivel5_nao_classificado(marked)
            result.padrao_buscado = padrao_montado
            result.marcacao_ia = marcacao_ia
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao classificar: {str(e)}", exc_info=True)
            self.stats['Não Classificado'] += 1
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
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=padrao.grupo_sugerido,
                    subgrupo=padrao.subgrupo_sugerido,
                    tipo_gasto=padrao.tipo_gasto_sugerido,
                    categoria_geral=None,
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
    
    def _classify_nivel45_regras_genericas(self, marked: MarkedTransaction) -> Optional[ClassifiedTransaction]:
        """
        Nível 4.5: Regras Genéricas (hardcoded do n8n)
        Usa classificador de regras genéricas independente de banco
        """
        try:
            resultado = self.generic_classifier.classify(marked.estabelecimento_base)
            
            if resultado:
                logger.debug(f"✅ Nível 4.5 (Regras Genéricas): {marked.estabelecimento_base[:30]}... (prioridade: {resultado['prioridade']})")
                
                return ClassifiedTransaction(
                    **marked.__dict__,
                    grupo=resultado['grupo'],
                    subgrupo=resultado['subgrupo'],
                    tipo_gasto=resultado['tipo_gasto'],
                    categoria_geral=None,
                    origem_classificacao='Regras Genéricas',
                )
        
        except Exception as e:
            logger.error(f"Erro Nível 4.5: {str(e)}")
        
        return None
    
    def _buscar_marcacao_ia(self, estabelecimento: str) -> Optional[str]:
        """
        Busca sugestão de marcação IA para QUALQUER transação
        PRIMEIRO tenta regras genéricas (hardcoded do n8n)
        DEPOIS tenta base_marcacoes (database do usuário)
        
        Returns:
            String formatada: "GRUPO > SUBGRUPO" ou None
        """
        try:
            # PRIMEIRA TENTATIVA: Regras genéricas (prioridade)
            marcacao_generica = self.generic_classifier.get_marcacao_ia(estabelecimento)
            if marcacao_generica:
                logger.debug(f"🎯 MarcaçãoIA (Regras Genéricas): {marcacao_generica}")
                return marcacao_generica
            
            # SEGUNDA TENTATIVA: base_marcacoes (database)
            from app.domains.categories.models import BaseMarcacoes
            
            marcacoes = self.db.query(BaseMarcacoes).filter(
                BaseMarcacoes.user_id == self.user_id
            ).all()
            
            estab_lower = estabelecimento.lower()
            
            for marcacao in marcacoes:
                keywords = [kw.strip().lower() for kw in marcacao.palavras_chave.split(',')]
                
                # Verificar se alguma keyword está no estabelecimento
                for keyword in keywords:
                    if keyword and keyword in estab_lower:
                        # Retornar primeira marcação encontrada
                        resultado = f"{marcacao.grupo_sugerido} > {marcacao.subgrupo_sugerido}"
                        logger.debug(f"🎯 MarcaçãoIA (Base Marcações): {resultado}")
                        return resultado
            
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
