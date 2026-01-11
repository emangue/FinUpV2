"""
Budget Service
Lógica de negócio para budget planning
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import json

from .repository import BudgetRepository
from .repository_geral import BudgetGeralRepository
from .repository_categoria_config import BudgetCategoriaConfigRepository, BudgetGeralHistoricoRepository
from .schemas import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse


class BudgetService:
    """Service com lógica de negócio para budget"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BudgetRepository(db)
        self.repository_geral = BudgetGeralRepository(db)
        self.repository_categoria_config = BudgetCategoriaConfigRepository(db)
        self.repository_historico = BudgetGeralHistoricoRepository(db)
    
    def get_budget(self, budget_id: int, user_id: int) -> BudgetResponse:
        """Busca budget por ID"""
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        return BudgetResponse.from_orm(budget)
    
    def get_budgets_by_month(self, user_id: int, mes_referencia: str) -> List[BudgetResponse]:
        """Lista budgets de um mês específico"""
        budgets = self.repository.get_by_month(user_id, mes_referencia)
        return [BudgetResponse.from_orm(b) for b in budgets]
    
    def get_all_budgets(self, user_id: int) -> BudgetListResponse:
        """Lista todos os budgets do usuário"""
        budgets = self.repository.get_all(user_id)
        return BudgetListResponse(
            budgets=[BudgetResponse.from_orm(b) for b in budgets],
            total=len(budgets)
        )
    
    def create_budget(self, user_id: int, data: BudgetCreate) -> BudgetResponse:
        """Cria novo budget"""
        # Verificar se já existe budget para este tipo_gasto/mês
        existing = self.repository.get_by_tipo_gasto_and_month(
            user_id, 
            data.tipo_gasto, 
            data.mes_referencia
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe budget para {data.tipo_gasto} em {data.mes_referencia}. Use PUT para atualizar."
            )
        
        budget = self.repository.create(user_id, data.dict())
        return BudgetResponse.from_orm(budget)
    
    def update_budget(self, budget_id: int, user_id: int, data: BudgetUpdate) -> BudgetResponse:
        """Atualiza budget existente"""
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        updated = self.repository.update(budget, data.dict(exclude_unset=True))
        return BudgetResponse.from_orm(updated)
    
    def delete_budget(self, budget_id: int, user_id: int) -> None:
        """Deleta budget"""
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        self.repository.delete(budget)
    
    def bulk_upsert_budgets(
        self, 
        user_id: int, 
        mes_referencia: str, 
        budgets: List[dict]
    ) -> List[BudgetResponse]:
        """Cria ou atualiza múltiplos budgets de uma vez"""
        # Validar dados
        for budget_data in budgets:
            if "tipo_gasto" not in budget_data or "valor_planejado" not in budget_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada budget deve ter 'tipo_gasto' e 'valor_planejado'"
                )
            
            if budget_data["valor_planejado"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="valor_planejado deve ser maior que zero"
                )
        
        result = self.repository.bulk_upsert(user_id, mes_referencia, budgets)
        return [BudgetResponse.from_orm(b) for b in result]
    
    # ===== MÉTODOS PARA BUDGET GERAL =====
    
    def get_budget_geral_by_month(self, user_id: int, mes_referencia: str) -> List[BudgetResponse]:
        """Lista budgets gerais de um mês específico"""
        budgets = self.repository_geral.get_by_month(user_id, mes_referencia)
        return [BudgetResponse.from_orm(b) for b in budgets]
    
    def get_all_budget_geral(self, user_id: int) -> BudgetListResponse:
        """Lista todos os budgets gerais do usuário"""
        budgets = self.repository_geral.get_all(user_id)
        return BudgetListResponse(
            budgets=[BudgetResponse.from_orm(b) for b in budgets],
            total=len(budgets)
        )
    
    def bulk_upsert_budget_geral(
        self, 
        user_id: int, 
        mes_referencia: str, 
        budgets: List[dict]
    ) -> List[BudgetResponse]:
        """Cria ou atualiza múltiplos budgets gerais de uma vez"""
        # Validar dados
        for budget_data in budgets:
            if "categoria_geral" not in budget_data or "valor_planejado" not in budget_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada budget geral deve ter 'categoria_geral' e 'valor_planejado'"
                )
            
            if budget_data["valor_planejado"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="valor_planejado deve ser maior que zero"
                )
        
        result = self.repository_geral.bulk_upsert(user_id, mes_referencia, budgets)
        return [BudgetResponse.from_orm(b) for b in result]
    
    # ===== MÉTODOS PARA CONFIGURAÇÃO DE CATEGORIAS =====
    
    def get_categorias_config(self, user_id: int, apenas_ativas: bool = True) -> List[Dict[str, Any]]:
        """Lista categorias configuradas do usuário ordenadas"""
        configs = self.repository_categoria_config.get_ordered_by_user(user_id, apenas_ativas)
        
        # Converter para dict com parse de JSON
        result = []
        for config in configs:
            config_dict = {
                "id": config.id,
                "nome_categoria": config.nome_categoria,
                "ordem": config.ordem,
                "fonte_dados": config.fonte_dados,
                "filtro_valor": config.filtro_valor,
                "tipos_gasto_incluidos": json.loads(config.tipos_gasto_incluidos) if config.tipos_gasto_incluidos else [],
                "cor_visualizacao": config.cor_visualizacao,
                "ativo": config.ativo == 1,
                "created_at": config.created_at,
                "updated_at": config.updated_at
            }
            result.append(config_dict)
        
        return result
    
    def create_categoria_config(self, user_id: int, data: dict) -> Dict[str, Any]:
        """Cria nova categoria configurada"""
        # Validações
        if not data.get("nome_categoria"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="nome_categoria é obrigatório"
            )
        
        if data.get("fonte_dados") not in ["GRUPO", "TIPO_TRANSACAO"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="fonte_dados deve ser 'GRUPO' ou 'TIPO_TRANSACAO'"
            )
        
        if not data.get("filtro_valor"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="filtro_valor é obrigatório"
            )
        
        # Verificar se já existe
        existing = self.repository_categoria_config.get_by_nome(user_id, data["nome_categoria"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Categoria '{data['nome_categoria']}' já existe"
            )
        
        # Criar
        config = self.repository_categoria_config.create(user_id, data)
        
        return {
            "id": config.id,
            "nome_categoria": config.nome_categoria,
            "ordem": config.ordem,
            "fonte_dados": config.fonte_dados,
            "filtro_valor": config.filtro_valor,
            "tipos_gasto_incluidos": json.loads(config.tipos_gasto_incluidos) if config.tipos_gasto_incluidos else [],
            "cor_visualizacao": config.cor_visualizacao,
            "ativo": config.ativo == 1
        }
    
    def update_categoria_config(self, config_id: int, user_id: int, data: dict) -> Dict[str, Any]:
        """Atualiza configuração de categoria"""
        config = self.repository_categoria_config.get_by_id(config_id, user_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuração não encontrada"
            )
        
        updated = self.repository_categoria_config.update(config, data)
        
        return {
            "id": updated.id,
            "nome_categoria": updated.nome_categoria,
            "ordem": updated.ordem,
            "fonte_dados": updated.fonte_dados,
            "filtro_valor": updated.filtro_valor,
            "tipos_gasto_incluidos": json.loads(updated.tipos_gasto_incluidos) if updated.tipos_gasto_incluidos else [],
            "cor_visualizacao": updated.cor_visualizacao,
            "ativo": updated.ativo == 1
        }
    
    def reordenar_categorias(self, user_id: int, reorders: List[Dict[str, int]]) -> List[Dict[str, Any]]:
        """Reordena categorias em batch"""
        configs = self.repository_categoria_config.reorder_batch(user_id, reorders)
        
        result = []
        for config in configs:
            config_dict = {
                "id": config.id,
                "nome_categoria": config.nome_categoria,
                "ordem": config.ordem,
                "fonte_dados": config.fonte_dados,
                "filtro_valor": config.filtro_valor,
                "tipos_gasto_incluidos": json.loads(config.tipos_gasto_incluidos) if config.tipos_gasto_incluidos else [],
                "cor_visualizacao": config.cor_visualizacao,
                "ativo": config.ativo == 1
            }
            result.append(config_dict)
        
        return result
    
    def update_tipos_gasto_categoria(
        self, 
        config_id: int, 
        user_id: int, 
        tipos_gasto: List[str]
    ) -> Dict[str, Any]:
        """Atualiza lista de TipoGasto de uma categoria"""
        config = self.repository_categoria_config.update_tipos_gasto(config_id, user_id, tipos_gasto)
        
        return {
            "id": config.id,
            "nome_categoria": config.nome_categoria,
            "ordem": config.ordem,
            "fonte_dados": config.fonte_dados,
            "filtro_valor": config.filtro_valor,
            "tipos_gasto_incluidos": json.loads(config.tipos_gasto_incluidos) if config.tipos_gasto_incluidos else [],
            "cor_visualizacao": config.cor_visualizacao,
            "ativo": config.ativo == 1
        }
    
    def bulk_upsert_budget_geral_com_validacao(
        self,
        user_id: int,
        mes_referencia: str,
        budgets: List[dict],
        total_mensal: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Cria ou atualiza budgets gerais com validação e auto-ajuste de total
        Retorna: {budgets: [...], total_ajustado: bool, novo_total: float, valor_anterior: float}
        """
        # Validar dados
        for budget_data in budgets:
            if "categoria_geral" not in budget_data or "valor_planejado" not in budget_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada budget geral deve ter 'categoria_geral' e 'valor_planejado'"
                )
        
        # Calcular soma das categorias
        soma_categorias = sum(b["valor_planejado"] for b in budgets)
        
        # Buscar total_mensal atual do banco
        budget_geral_atual = self.repository_geral.get_by_month(user_id, mes_referencia)
        valor_anterior = None
        if budget_geral_atual and len(budget_geral_atual) > 0:
            valor_anterior = budget_geral_atual[0].total_mensal
        
        # Se não tem total_mensal definido, usar o enviado ou a soma
        if valor_anterior is None:
            valor_anterior = total_mensal if total_mensal is not None else soma_categorias
        
        # Verificar se precisa ajustar
        total_ajustado = False
        novo_total = total_mensal if total_mensal is not None else valor_anterior
        
        if soma_categorias > novo_total:
            # Auto-ajuste: total = soma das categorias
            novo_total = soma_categorias
            total_ajustado = True
            
            # Registrar no histórico
            self.repository_historico.create_ajuste_log(
                user_id=user_id,
                mes_referencia=mes_referencia,
                valor_anterior=valor_anterior,
                valor_novo=novo_total,
                soma_categorias=soma_categorias,
                motivo=f"Soma das categorias (R$ {soma_categorias:.2f}) ultrapassou o total mensal (R$ {valor_anterior:.2f})"
            )
        
        # Salvar budgets com total_mensal atualizado
        result = self.repository_geral.bulk_upsert(user_id, mes_referencia, budgets)
        
        # Atualizar total_mensal no primeiro budget (convenção)
        if result and len(result) > 0:
            result[0].total_mensal = novo_total
            self.repository_geral.db.commit()
        
        return {
            "budgets": [BudgetResponse.from_orm(b) for b in result],
            "total_ajustado": total_ajustado,
            "novo_total": novo_total,
            "valor_anterior": valor_anterior,
            "soma_categorias": soma_categorias
        }
