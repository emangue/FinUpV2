"""
Budget Categoria Config Repository
Camada de acesso a dados para budget_categoria_config (categorias personalizáveis)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from typing import List, Optional, Dict
from datetime import datetime
import json

from .models import BudgetCategoriaConfig, BudgetGeralHistorico


class BudgetCategoriaConfigRepository:
    """Repository para operações de configuração de categorias de orçamento"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, config_id: int, user_id: int) -> Optional[BudgetCategoriaConfig]:
        """Busca configuração por ID"""
        return self.db.query(BudgetCategoriaConfig).filter(
            and_(
                BudgetCategoriaConfig.id == config_id,
                BudgetCategoriaConfig.user_id == user_id
            )
        ).first()
    
    def get_ordered_by_user(self, user_id: int, apenas_ativas: bool = True) -> List[BudgetCategoriaConfig]:
        """Busca categorias ordenadas do usuário"""
        query = self.db.query(BudgetCategoriaConfig).filter(
            BudgetCategoriaConfig.user_id == user_id
        )
        
        if apenas_ativas:
            query = query.filter(BudgetCategoriaConfig.ativo == 1)
        
        return query.order_by(BudgetCategoriaConfig.ordem).all()
    
    def get_by_nome(self, user_id: int, nome_categoria: str) -> Optional[BudgetCategoriaConfig]:
        """Busca categoria por nome"""
        return self.db.query(BudgetCategoriaConfig).filter(
            and_(
                BudgetCategoriaConfig.user_id == user_id,
                BudgetCategoriaConfig.nome_categoria == nome_categoria
            )
        ).first()
    
    def create(self, user_id: int, data: dict) -> BudgetCategoriaConfig:
        """Cria nova categoria"""
        # Garantir que tipos_gasto_incluidos é string JSON
        if 'tipos_gasto_incluidos' in data and isinstance(data['tipos_gasto_incluidos'], list):
            data['tipos_gasto_incluidos'] = json.dumps(data['tipos_gasto_incluidos'])
        
        config = BudgetCategoriaConfig(
            user_id=user_id,
            **data
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update(self, config: BudgetCategoriaConfig, data: dict) -> BudgetCategoriaConfig:
        """Atualiza configuração existente"""
        # Garantir que tipos_gasto_incluidos é string JSON
        if 'tipos_gasto_incluidos' in data and isinstance(data['tipos_gasto_incluidos'], list):
            data['tipos_gasto_incluidos'] = json.dumps(data['tipos_gasto_incluidos'])
        
        for key, value in data.items():
            setattr(config, key, value)
        
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def delete(self, config: BudgetCategoriaConfig) -> None:
        """Deleta configuração"""
        self.db.delete(config)
        self.db.commit()
    
    def reorder_batch(self, user_id: int, reorders: List[Dict[int, int]]) -> List[BudgetCategoriaConfig]:
        """
        Reordena múltiplas categorias em batch
        reorders: [{"id": 1, "nova_ordem": 3}, {"id": 2, "nova_ordem": 1}, ...]
        """
        result = []
        for item in reorders:
            config = self.get_by_id(item["id"], user_id)
            if config:
                config.ordem = item["nova_ordem"]
                config.updated_at = datetime.now()
                result.append(config)
        
        self.db.commit()
        for config in result:
            self.db.refresh(config)
        
        return result
    
    def update_tipos_gasto(
        self, 
        config_id: int, 
        user_id: int, 
        tipos_gasto: List[str]
    ) -> BudgetCategoriaConfig:
        """Atualiza lista de TipoGasto incluídos"""
        config = self.get_by_id(config_id, user_id)
        if not config:
            raise ValueError(f"Configuração {config_id} não encontrada")
        
        config.tipos_gasto_incluidos = json.dumps(tipos_gasto)
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def desativar(self, config_id: int, user_id: int) -> BudgetCategoriaConfig:
        """Desativa categoria (soft delete)"""
        config = self.get_by_id(config_id, user_id)
        if not config:
            raise ValueError(f"Configuração {config_id} não encontrada")
        
        config.ativo = 0
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def ativar(self, config_id: int, user_id: int) -> BudgetCategoriaConfig:
        """Ativa categoria"""
        config = self.get_by_id(config_id, user_id)
        if not config:
            raise ValueError(f"Configuração {config_id} não encontrada")
        
        config.ativo = 1
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return config


class BudgetGeralHistoricoRepository:
    """Repository para histórico de ajustes automáticos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_ajuste_log(
        self,
        user_id: int,
        mes_referencia: str,
        valor_anterior: float,
        valor_novo: float,
        soma_categorias: float,
        motivo: str
    ) -> BudgetGeralHistorico:
        """Registra ajuste automático no histórico"""
        log = BudgetGeralHistorico(
            user_id=user_id,
            mes_referencia=mes_referencia,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
            soma_categorias=soma_categorias,
            motivo=motivo
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_historico_mes(self, user_id: int, mes_referencia: str) -> List[BudgetGeralHistorico]:
        """Busca histórico de ajustes de um mês"""
        return self.db.query(BudgetGeralHistorico).filter(
            and_(
                BudgetGeralHistorico.user_id == user_id,
                BudgetGeralHistorico.mes_referencia == mes_referencia
            )
        ).order_by(BudgetGeralHistorico.created_at.desc()).all()
    
    def get_historico_recente(self, user_id: int, limit: int = 10) -> List[BudgetGeralHistorico]:
        """Busca histórico recente de ajustes"""
        return self.db.query(BudgetGeralHistorico).filter(
            BudgetGeralHistorico.user_id == user_id
        ).order_by(BudgetGeralHistorico.created_at.desc()).limit(limit).all()
