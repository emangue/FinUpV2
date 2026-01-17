"""
Service para regras de classificação genérica configuráveis
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from .models import GenericClassificationRules
from .schemas import GenericRuleCreate, GenericRuleUpdate, GenericRuleResponse


logger = logging.getLogger(__name__)


class GenericClassificationService:
    """
    Service para gerenciar regras genéricas de classificação
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rule(self, rule_data: GenericRuleCreate, created_by: str = None) -> GenericClassificationRules:
        """Cria nova regra genérica"""
        rule = GenericClassificationRules(
            **rule_data.dict(),
            created_by=created_by
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"✅ Regra criada: {rule.nome_regra}")
        return rule
    
    def get_rule(self, rule_id: int) -> Optional[GenericClassificationRules]:
        """Busca regra por ID"""
        return self.db.query(GenericClassificationRules).filter(
            GenericClassificationRules.id == rule_id
        ).first()
    
    def list_rules(
        self, 
        active_only: bool = None,
        search: str = None,
        grupo: str = None,
        sort_by: str = "prioridade",
        sort_desc: bool = True
    ) -> List[GenericClassificationRules]:
        """Lista regras com filtros"""
        query = self.db.query(GenericClassificationRules)
        
        # Filtros
        if active_only is not None:
            query = query.filter(GenericClassificationRules.ativo == active_only)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                GenericClassificationRules.nome_regra.ilike(search_term),
                GenericClassificationRules.keywords.ilike(search_term),
                GenericClassificationRules.descricao.ilike(search_term)
            ))
        
        if grupo:
            query = query.filter(GenericClassificationRules.grupo == grupo)
        
        # Ordenação
        if sort_by == "prioridade":
            order_col = GenericClassificationRules.prioridade
        elif sort_by == "nome":
            order_col = GenericClassificationRules.nome_regra
        elif sort_by == "grupo":
            order_col = GenericClassificationRules.grupo
        elif sort_by == "uso":
            order_col = GenericClassificationRules.total_matches
        else:
            order_col = GenericClassificationRules.created_at
        
        if sort_desc:
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(order_col)
        
        return query.all()
    
    def update_rule(self, rule_id: int, rule_data: GenericRuleUpdate) -> Optional[GenericClassificationRules]:
        """Atualiza regra existente"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        # Atualizar apenas campos não nulos
        update_data = rule_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"✅ Regra atualizada: {rule.nome_regra}")
        return rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """Deleta regra"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        nome = rule.nome_regra
        self.db.delete(rule)
        self.db.commit()
        
        logger.info(f"🗑️ Regra deletada: {nome}")
        return True
    
    def test_rule(self, texto: str) -> Dict[str, Any]:
        """
        Testa quais regras fazem match com um texto
        
        Args:
            texto: Texto para testar (nome de estabelecimento)
            
        Returns:
            Dict com regras que fazem match
        """
        rules = self.list_rules(active_only=True)
        matched_rules = []
        
        for rule in rules:
            if rule.matches(texto):
                matched_rules.append(rule)
        
        # Ordenar por prioridade (maior primeiro)
        matched_rules.sort(key=lambda r: r.prioridade, reverse=True)
        
        return {
            'texto': texto,
            'total_matches': len(matched_rules),
            'regras_matched': [GenericRuleResponse.from_model(r) for r in matched_rules],
            'melhor_regra': GenericRuleResponse.from_model(matched_rules[0]) if matched_rules else None
        }
    
    def classify_text(self, texto: str) -> Optional[Dict[str, str]]:
        """
        Classifica texto usando regras configuráveis
        
        Args:
            texto: Texto para classificar
            
        Returns:
            Dict com classificação ou None se não encontrar
        """
        result = self.test_rule(texto)
        
        if result['melhor_regra']:
            regra = result['melhor_regra']
            
            # Incrementar contador de uso na base
            rule_model = self.get_rule(regra.id)
            if rule_model:
                rule_model.increment_usage()
                self.db.commit()
            
            return {
                'grupo': regra.grupo,
                'subgrupo': regra.subgrupo,
                'tipo_gasto': regra.tipo_gasto,
                'prioridade': regra.prioridade,
                'regra_aplicada': regra.nome_regra
            }
        
        return None
    
    def import_hardcoded_rules(self, sobrescrever: bool = False) -> Dict[str, Any]:
        """
        Importa regras hardcoded do GenericRulesClassifier para a base
        
        Args:
            sobrescrever: Se True, atualiza regras existentes
            
        Returns:
            Estatísticas da importação
        """
        from app.domains.upload.processors.generic_rules_classifier import GenericRulesClassifier
        
        classifier = GenericRulesClassifier()
        hardcoded_rules = classifier.RULES
        
        created = 0
        updated = 0
        skipped = 0
        
        for hardcoded_rule in hardcoded_rules:
            # Verificar se já existe
            keywords_str = ','.join(hardcoded_rule.keywords)
            existing = self.db.query(GenericClassificationRules).filter(
                and_(
                    GenericClassificationRules.keywords == keywords_str,
                    GenericClassificationRules.grupo == hardcoded_rule.grupo,
                    GenericClassificationRules.subgrupo == hardcoded_rule.subgrupo
                )
            ).first()
            
            if existing:
                if sobrescrever:
                    # Atualizar
                    existing.nome_regra = f"{hardcoded_rule.grupo} - {hardcoded_rule.subgrupo}"
                    existing.tipo_gasto = hardcoded_rule.tipo_gasto
                    existing.prioridade = hardcoded_rule.prioridade
                    existing.ativo = True
                    updated += 1
                else:
                    skipped += 1
                continue
            
            # Criar nova
            new_rule = GenericClassificationRules(
                nome_regra=f"{hardcoded_rule.grupo} - {hardcoded_rule.subgrupo}",
                descricao=f"Importado do código hardcoded - {', '.join(hardcoded_rule.keywords[:3])}{'...' if len(hardcoded_rule.keywords) > 3 else ''}",
                keywords=keywords_str,
                grupo=hardcoded_rule.grupo,
                subgrupo=hardcoded_rule.subgrupo,
                tipo_gasto=hardcoded_rule.tipo_gasto,
                prioridade=hardcoded_rule.prioridade,
                ativo=True,
                case_sensitive=False,
                match_completo=False,
                created_by='system_import'
            )
            
            self.db.add(new_rule)
            created += 1
        
        self.db.commit()
        
        logger.info(f"📥 Importação concluída: {created} criadas, {updated} atualizadas, {skipped} ignoradas")
        
        return {
            'total_hardcoded': len(hardcoded_rules),
            'created': created,
            'updated': updated,
            'skipped': skipped
        }
    
    def get_grupos_disponiveis(self) -> List[str]:
        """Retorna lista de grupos únicos nas regras"""
        result = self.db.query(GenericClassificationRules.grupo).distinct().all()
        return [r[0] for r in result if r[0]]
    
    def get_grupos_subgrupos_com_tipos(self) -> List[Dict[str, Any]]:
        """Retorna grupos/subgrupos com tipos de gasto baseado na base_grupos_config"""
        from app.domains.transactions.models import JournalEntry
        from app.domains.grupos.models import BaseGruposConfig
        
        # Busca combinações únicas de grupo/subgrupo das transações
        combinacoes = self.db.query(
            JournalEntry.GRUPO,
            JournalEntry.SUBGRUPO
        ).filter(
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.SUBGRUPO.isnot(None),
            JournalEntry.GRUPO != '',
            JournalEntry.SUBGRUPO != ''
        ).distinct().all()
        
        # Mapear grupos → tipos de gasto da base_grupos_config
        grupos_config = self.db.query(BaseGruposConfig).all()
        grupo_tipo_map = {g.nome_grupo: (g.tipo_gasto_padrao, g.categoria_geral) for g in grupos_config}
        
        opcoes = []
        for grupo, subgrupo in combinacoes:
            if grupo in grupo_tipo_map:
                tipo_gasto, categoria_geral = grupo_tipo_map[grupo]
                opcoes.append({
                    'grupo': grupo,
                    'subgrupo': subgrupo,
                    'tipo_gasto': tipo_gasto,
                    'categoria_geral': categoria_geral
                })
        
        return sorted(opcoes, key=lambda x: (x['grupo'], x['subgrupo']))
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das regras"""
        total = self.db.query(GenericClassificationRules).count()
        ativas = self.db.query(GenericClassificationRules).filter(
            GenericClassificationRules.ativo == True
        ).count()
        
        # Top 5 regras mais usadas
        top_used = self.db.query(GenericClassificationRules).filter(
            GenericClassificationRules.total_matches > 0
        ).order_by(desc(GenericClassificationRules.total_matches)).limit(5).all()
        
        # Grupos únicos
        grupos = self.get_grupos_disponiveis()
        
        return {
            'total_regras': total,
            'regras_ativas': ativas,
            'regras_inativas': total - ativas,
            'grupos_unicos': len(grupos),
            'grupos': grupos,
            'top_regras_usadas': [
                {
                    'nome': r.nome_regra,
                    'total_matches': r.total_matches,
                    'last_match': r.last_match_at
                } for r in top_used
            ]
        }