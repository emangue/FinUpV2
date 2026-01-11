"""
Budget Service
Lógica de negócio para budget planning
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import json

from .repository import BudgetRepository
from .repository_geral import BudgetGeralRepository
from .repository_categoria_config import BudgetCategoriaConfigRepository, BudgetGeralHistoricoRepository
from .schemas import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse
from app.domains.transactions.models import JournalEntry


class BudgetService:
    """Service com lógica de negócio para budget"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BudgetRepository(db)
        self.repository_geral = BudgetGeralRepository(db)
        self.repository_categoria_config = BudgetCategoriaConfigRepository(db)
        self.repository_historico = BudgetGeralHistoricoRepository(db)
    
    def calcular_media_3_meses(self, user_id: int, tipo_gasto: str, mes_referencia: str) -> float:
        """
        Calcula média dos últimos 3 meses anteriores ao mes_referencia
        
        Args:
            user_id: ID do usuário
            tipo_gasto: Tipo de gasto
            mes_referencia: Mês no formato YYYY-MM
            
        Returns:
            float: Média calculada (ou 0 se não houver dados)
        """
        # Converter mes_referencia para calcular meses anteriores
        ano, mes = map(int, mes_referencia.split('-'))
        
        # Calcular os 3 meses anteriores
        meses_anteriores = []
        for i in range(1, 4):  # 3 meses atrás
            m = mes - i
            a = ano
            if m < 1:
                m += 12
                a -= 1
            meses_anteriores.append(f"{a:04d}-{m:02d}")
        
        # Criar condições para cada mês
        from sqlalchemy import or_
        condicoes_meses = []
        for mes_anterior in meses_anteriores:
            ano_mes, mes_num = mes_anterior.split('-')
            # Formato: dd/mm/yyyy → substr(4,2)=mm, substr(7,4)=yyyy
            condicao = func.concat(
                func.substr(JournalEntry.Data, 7, 4),  # ano
                '-',
                func.substr(JournalEntry.Data, 4, 2)   # mês
            ) == mes_anterior
            condicoes_meses.append(condicao)
        
        # Buscar transações dos 3 meses anteriores
        transacoes = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.TipoGasto == tipo_gasto,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.Valor < 0,  # Apenas saídas
            or_(*condicoes_meses)
        ).all()
        
        if not transacoes:
            return 0.0
        
        # Agrupar por mês e calcular soma
        meses_com_dados = {}
        for t in transacoes:
            # Extrair mês-ano da transação (formato dd/mm/yyyy)
            if len(t.Data) >= 10:
                mes_transacao = t.Data[3:10]  # mm/yyyy
                if mes_transacao not in meses_com_dados:
                    meses_com_dados[mes_transacao] = 0
                meses_com_dados[mes_transacao] += abs(t.Valor)
        
        # Calcular média (soma / qtd_meses_com_dados)
        if meses_com_dados:
            total = sum(meses_com_dados.values())
            qtd_meses = len(meses_com_dados)
            media = total / qtd_meses
            return round(media, 2)
        
        return 0.0
    
    def get_detalhamento_media(
        self, 
        user_id: int, 
        tipo_gasto: str, 
        mes_referencia: str
    ):
        """
        Retorna detalhamento dos 3 meses que compõem a média
        
        Args:
            user_id: ID do usuário
            tipo_gasto: Tipo de gasto
            mes_referencia: Mês de referência no formato YYYY-MM
            
        Returns:
            DetalhamentoMediaResponse com lista de meses detalhados
        """
        from .schemas import DetalhamentoMediaResponse, MesDetalhamento
        
        # Converter mes_referencia para calcular meses anteriores
        ano, mes = map(int, mes_referencia.split('-'))
        
        # Calcular os 3 meses anteriores
        meses_anteriores = []
        for i in range(1, 4):  # 3 meses atrás
            m = mes - i
            a = ano
            if m < 1:
                m += 12
                a -= 1
            meses_anteriores.append(f"{a:04d}-{m:02d}")
        
        # Nomes dos meses em português
        meses_nomes = {
            '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março',
            '04': 'Abril', '05': 'Maio', '06': 'Junho',
            '07': 'Julho', '08': 'Agosto', '09': 'Setembro',
            '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
        }
        
        # Criar condições para cada mês
        from sqlalchemy import or_
        condicoes_meses = []
        for mes_anterior in meses_anteriores:
            ano_mes, mes_num = mes_anterior.split('-')
            condicao = func.concat(
                func.substr(JournalEntry.Data, 7, 4),
                '-',
                func.substr(JournalEntry.Data, 4, 2)
            ) == mes_anterior
            condicoes_meses.append(condicao)
        
        # Buscar transações dos 3 meses anteriores
        transacoes = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.TipoGasto == tipo_gasto,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.Valor < 0,
            or_(*condicoes_meses)
        ).all()
        
        # Agrupar por mês
        detalhes_por_mes = {}
        for mes_ant in meses_anteriores:
            detalhes_por_mes[mes_ant] = {
                'transacoes': [],
                'total': 0.0
            }
        
        for t in transacoes:
            if len(t.Data) >= 10:
                # Extrair ano-mês da data (dd/mm/yyyy -> yyyy-mm)
                mes_transacao = f"{t.Data[6:10]}-{t.Data[3:5]}"
                if mes_transacao in detalhes_por_mes:
                    detalhes_por_mes[mes_transacao]['transacoes'].append(t)
                    detalhes_por_mes[mes_transacao]['total'] += abs(t.Valor)
        
        # Construir lista de MesDetalhamento
        meses_detalhados = []
        total_geral = 0.0
        
        # Ordenar meses do mais antigo para o mais recente
        for mes_ref in sorted(meses_anteriores):
            detalhes = detalhes_por_mes[mes_ref]
            ano_str, mes_str = mes_ref.split('-')
            mes_nome = f"{meses_nomes[mes_str]} {ano_str}"
            
            mes_det = MesDetalhamento(
                mes_referencia=mes_ref,
                mes_nome=mes_nome,
                valor_total=round(detalhes['total'], 2),
                quantidade_transacoes=len(detalhes['transacoes'])
            )
            meses_detalhados.append(mes_det)
            total_geral += detalhes['total']
        
        # Calcular média (apenas meses com transações)
        meses_com_dados = [m for m in meses_detalhados if m.quantidade_transacoes > 0]
        if meses_com_dados:
            media_calculada = total_geral / len(meses_com_dados)
        else:
            media_calculada = 0.0
        
        return DetalhamentoMediaResponse(
            tipo_gasto=tipo_gasto,
            mes_planejado=mes_referencia,
            meses_considerados=meses_detalhados,
            media_calculada=round(media_calculada, 2),
            total_geral=round(total_geral, 2)
        )
    
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
        
        # Criar ou atualizar cada budget com média calculada
        result = []
        for budget_data in budgets:
            # Calcular média dos 3 meses anteriores
            media = self.calcular_media_3_meses(
                user_id=user_id,
                tipo_gasto=budget_data["tipo_gasto"],
                mes_referencia=mes_referencia
            )
            
            # Upsert com média
            budget = self.repository.upsert(
                user_id=user_id,
                tipo_gasto=budget_data["tipo_gasto"],
                mes_referencia=mes_referencia,
                valor_planejado=budget_data["valor_planejado"],
                valor_medio_3_meses=media
            )
            result.append(budget)
        
        return [BudgetResponse.from_orm(b) for b in result]
    
    # ===== MÉTODOS PARA BUDGET GERAL =====
    
    def get_budget_geral_by_month(self, user_id: int, mes_referencia: str):
        """Lista budgets gerais de um mês específico"""
        from .schemas import BudgetGeralResponse
        budgets = self.repository_geral.get_by_month(user_id, mes_referencia)
        return [BudgetGeralResponse.from_orm(b) for b in budgets]
    
    def get_all_budget_geral(self, user_id: int):
        """Lista todos os budgets gerais do usuário"""
        from .schemas import BudgetGeralResponse, BudgetGeralListResponse
        budgets = self.repository_geral.get_all(user_id)
        return BudgetGeralListResponse(
            budgets=[BudgetGeralResponse.from_orm(b) for b in budgets],
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
    
    def delete_categoria_config(self, config_id: int, user_id: int) -> None:
        """Deleta (desativa) uma configuração de categoria"""
        config = self.repository_categoria_config.get_by_id(config_id, user_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada"
            )
        
        # Soft delete - apenas desativa
        self.repository_categoria_config.update(config_id, user_id, {"ativo": 0})
        
        # Ou hard delete se preferir:
        # self.repository_categoria_config.delete(config)
    
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

    def get_tipos_gasto_disponiveis(self, user_id: int, fonte_dados: str, filtro_valor: str) -> list:
        """
        Retorna lista de tipos de gasto disponíveis para um grupo ou tipo de transação
        
        Args:
            user_id: ID do usuário
            fonte_dados: "GRUPO" ou "TIPO_TRANSACAO"
            filtro_valor: Nome do grupo (ex: "Casa") ou tipo de transação (ex: "Cartão")
        
        Returns:
            Lista de tipos de gasto únicos encontrados nas transações
        """
        from sqlalchemy import distinct
        from app.domains.transactions.models import JournalEntry
        
        query = self.repository.db.query(
            distinct(JournalEntry.TipoGasto)
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.TipoGasto.isnot(None),
            JournalEntry.TipoGasto != ''
        )
        
        if fonte_dados == "GRUPO":
            query = query.filter(JournalEntry.GRUPO == filtro_valor)
        elif fonte_dados == "TIPO_TRANSACAO":
            query = query.filter(JournalEntry.TipoTransacao == filtro_valor)
        
        tipos_gasto = [row[0] for row in query.all() if row[0]]
        return sorted(tipos_gasto)
