"""
Generic Rules Classifier v2.0
Classificador que usa regras configuráveis da base de dados
Mantém fallback para regras hardcoded se necessário
"""

import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class GenericRule:
    """Regra genérica de classificação (mantido para compatibilidade)"""
    keywords: List[str]
    grupo: str
    subgrupo: str
    tipo_gasto: str
    prioridade: int


class GenericRulesClassifier:
    """
    Classificador baseado em regras configuráveis (v2.0)
    
    v2.0: Usa regras da base de dados (generic_classification_rules)
    v1.0: Usava regras hardcoded (DEPRECATED)
    """
    
    def __init__(self, db: Session = None):
        """
        Args:
            db: Sessão do banco (None = usa apenas regras hardcoded)
        """
        self.db = db
        self._hardcoded_rules = self._get_hardcoded_rules()  # Fallback
    
    def classify(self, estabelecimento: str) -> Optional[Dict]:
        """
        Classifica estabelecimento usando regras configuráveis
        
        Args:
            estabelecimento: Nome do estabelecimento
            
        Returns:
            Dict com classificação ou None
        """
        try:
            # 1ª Tentativa: Regras configuráveis da base
            if self.db:
                result = self._classify_database_rules(estabelecimento)
                if result:
                    return result
            
            # 2ª Tentativa: Regras hardcoded (fallback)
            result = self._classify_hardcoded_rules(estabelecimento)
            if result:
                # Marcar como hardcoded para debug
                result['source'] = 'hardcoded'
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na classificação genérica: {e}")
            return None
    
    def get_marcacao_ia(self, estabelecimento: str) -> Optional[str]:
        """
        Retorna marcação IA formatada: "GRUPO > SUBGRUPO"
        
        Args:
            estabelecimento: Nome do estabelecimento
            
        Returns:
            String formatada ou None
        """
        result = self.classify(estabelecimento)
        if result:
            return f"{result['grupo']} > {result['subgrupo']}"
        return None
    
    def _classify_database_rules(self, estabelecimento: str) -> Optional[Dict]:
        """Classifica usando regras da base de dados"""
        try:
            from app.domains.classification.service import GenericClassificationService
            
            service = GenericClassificationService(self.db)
            result = service.classify_text(estabelecimento)
            
            if result:
                logger.debug(f"✅ Classificação DB: {estabelecimento[:30]}... -> {result['grupo']} > {result['subgrupo']} (regra: {result['regra_aplicada']})")
                return result
            
            return None
            
        except Exception as e:
            logger.warning(f"Erro ao usar regras da base: {e}")
            return None
    
    def _classify_hardcoded_rules(self, estabelecimento: str) -> Optional[Dict]:
        """Classifica usando regras hardcoded (fallback)"""
        try:
            estabelecimento_upper = estabelecimento.upper()
            
            # Buscar por prioridade (maior primeiro)
            matched_rules = []
            for rule in self._hardcoded_rules:
                for keyword in rule.keywords:
                    if keyword.upper() in estabelecimento_upper:
                        matched_rules.append(rule)
                        break
            
            if not matched_rules:
                return None
            
            # Ordenar por prioridade e retornar primeira
            matched_rules.sort(key=lambda r: r.prioridade, reverse=True)
            best_rule = matched_rules[0]
            
            logger.debug(f"✅ Classificação Hardcoded: {estabelecimento[:30]}... -> {best_rule.grupo} > {best_rule.subgrupo} (prioridade: {best_rule.prioridade})")
            
            return {
                'grupo': best_rule.grupo,
                'subgrupo': best_rule.subgrupo,
                'tipo_gasto': best_rule.tipo_gasto,
                'prioridade': best_rule.prioridade,
                'regra_aplicada': f"Hardcoded-{best_rule.grupo}-{best_rule.subgrupo}"
            }
            
        except Exception as e:
            logger.error(f"Erro nas regras hardcoded: {e}")
            return None
    
    def _get_hardcoded_rules(self) -> List[GenericRule]:
        """
        Retorna regras hardcoded para fallback
        Apenas as mais importantes para não duplicar código
        """
        return [
            # === REGRAS ESSENCIAIS (FALLBACK) ===
            GenericRule(
                keywords=['PIX', 'TRANSFERENCIA', 'TED', 'DOC'],
                grupo='Transferências',
                subgrupo='PIX/TED',
                tipo_gasto='Eventual',
                prioridade=8
            ),
            GenericRule(
                keywords=['SUPERMERCADO', 'MERCADO', 'EXTRA', 'CARREFOUR', 'PÃO DE AÇUCAR'],
                grupo='Alimentação',
                subgrupo='Supermercado',
                tipo_gasto='Ajustável',
                prioridade=7
            ),
            GenericRule(
                keywords=['POSTO', 'GASOLINA', 'COMBUSTIVEL', 'SHELL', 'BR', 'IPIRANGA'],
                grupo='Transporte',
                subgrupo='Combustível',
                tipo_gasto='Ajustável',
                prioridade=7
            ),
            GenericRule(
                keywords=['FARMACIA', 'DROGA', 'DROGARIA'],
                grupo='Saúde',
                subgrupo='Farmácia',
                tipo_gasto='Ajustável',
                prioridade=7
            ),
        ]
    
    # Propriedade para compatibilidade com código legado
    @property
    def RULES(self) -> List[GenericRule]:
        """Retorna regras hardcoded (para compatibilidade)"""
        return self._hardcoded_rules
