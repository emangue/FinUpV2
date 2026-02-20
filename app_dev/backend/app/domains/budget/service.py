"""
Budget Service
Lógica de negócio para budget planning

CHANGELOG 13/02/2026:
- ✅ Removidos imports obsoletos: repository_geral, repository_categoria_config
- ✅ Apenas BudgetRepository (para budget_planning)
"""
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import json

from .repository import BudgetRepository
from .schemas import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse
from app.domains.transactions.models import JournalEntry


class BudgetService:
    """Service com lógica de negócio para budget"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BudgetRepository(db)
    
    def copy_budget_to_year(
        self,
        user_id: int,
        mes_origem: str,
        ano_destino: int,
        substituir_existentes: bool
    ) -> dict:
        """
        Copia metas de mes_origem para todos os meses de ano_destino
        
        Args:
            user_id: ID do usuário
            mes_origem: Mês de origem no formato YYYY-MM
            ano_destino: Ano de destino (ex: 2026)
            substituir_existentes: Se deve sobrescrever metas existentes
            
        Returns:
            dict com sucesso, meses_criados, metas_copiadas, mensagem
        """
        from .models import BudgetGeral
        
        # 1. Buscar metas do mês de origem
        metas_origem = self.db.query(BudgetGeral).filter(
            BudgetGeral.user_id == user_id,
            BudgetGeral.mes_referencia == mes_origem
        ).all()
        
        if not metas_origem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nenhuma meta encontrada para {mes_origem}"
            )
        
        # 2. Gerar lista de meses do ano
        meses_ano = [f"{ano_destino}-{str(m).zfill(2)}" for m in range(1, 13)]
        
        # 3. Para cada mês, copiar ou atualizar metas
        meses_criados = 0
        metas_copiadas = 0
        
        for mes_destino in meses_ano:
            if mes_destino == mes_origem:
                continue  # Pular mês de origem
            
            for meta_origem in metas_origem:
                # Verificar se já existe
                meta_existente = self.db.query(BudgetGeral).filter(
                    BudgetGeral.user_id == user_id,
                    BudgetGeral.categoria_geral == meta_origem.categoria_geral,
                    BudgetGeral.mes_referencia == mes_destino
                ).first()
                
                if meta_existente and not substituir_existentes:
                    continue  # Pular se já existe e não deve substituir
                
                if meta_existente:
                    # Atualizar
                    meta_existente.valor_planejado = meta_origem.valor_planejado
                else:
                    # Criar nova
                    nova_meta = BudgetGeral(
                        user_id=user_id,
                        categoria_geral=meta_origem.categoria_geral,
                        mes_referencia=mes_destino,
                        valor_planejado=meta_origem.valor_planejado
                    )
                    self.db.add(nova_meta)
                    meses_criados += 1
                
                metas_copiadas += 1
        
        self.db.commit()
        
        return {
            "sucesso": True,
            "meses_criados": meses_criados,
            "metas_copiadas": metas_copiadas,
            "mensagem": f"Metas copiadas de {mes_origem} para {meses_criados} meses de {ano_destino}"
        }
    
    def get_budget_planning(self, user_id: int, mes_referencia: str) -> dict:
        """
        Lista metas de budget planning + grupos com gastos sem meta definida.
        Todo grupo que tem gasto no mês aparece na lista (com valor_planejado=0 se não tiver meta).
        """
        try:
            return self._get_budget_planning_impl(user_id, mes_referencia)
        except Exception as e:
            logger.exception(
                "get_budget_planning falhou: user_id=%s mes_referencia=%s erro=%s",
                user_id, mes_referencia, e
            )
            raise
    
    def _get_budget_planning_impl(self, user_id: int, mes_referencia: str) -> dict:
        from .models import BudgetPlanning
        from app.domains.grupos.models import BaseGruposConfig
        
        budgets = self.db.query(BudgetPlanning).filter(
            BudgetPlanning.user_id == user_id,
            BudgetPlanning.mes_referencia == mes_referencia
        ).all()
        
        try:
            grupos_rows = self.db.query(BaseGruposConfig.nome_grupo, BaseGruposConfig.categoria_geral).all()
            grupos_config = {nome: cat for nome, cat in grupos_rows}
        except Exception as e:
            logger.warning("get_budget_planning: base_grupos_config inacessível, usando fallback: %s", e)
            grupos_config = {}
        
        # Mapa grupo -> budget (para juntar com grupos que têm gastos)
        by_grupo = {b.grupo: b for b in budgets}
        
        # Grupos com gastos no mês (Despesa) que não estão em budget_planning
        ano, mes = mes_referencia.split('-')
        mes_fatura = f"{ano}{mes}"
        grupos_com_gasto = (
            self.db.query(JournalEntry.GRUPO, func.sum(JournalEntry.Valor).label('total'))
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == 'Despesa',
                JournalEntry.IgnorarDashboard == 0,
                JournalEntry.GRUPO.isnot(None),
                JournalEntry.GRUPO != ''
            )
            .group_by(JournalEntry.GRUPO)
            .all()
        )
        # Grupos com investimentos no mês que não estão em budget_planning
        grupos_com_investimento = (
            self.db.query(JournalEntry.GRUPO, func.sum(JournalEntry.Valor).label('total'))
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == 'Investimentos',
                JournalEntry.IgnorarDashboard == 0,
                JournalEntry.GRUPO.isnot(None),
                JournalEntry.GRUPO != ''
            )
            .group_by(JournalEntry.GRUPO)
            .all()
        )
        
        resultado = []
        for budget in budgets:
            categoria_geral = grupos_config.get(budget.grupo) or 'Despesa'
            valor_realizado_raw = self._calcular_valor_realizado_grupo(
                user_id, budget.grupo, mes_referencia, categoria_geral
            )
            valor_realizado = abs(float(valor_realizado_raw)) if valor_realizado_raw else 0.0
            percentual = (valor_realizado / budget.valor_planejado * 100) if budget.valor_planejado > 0 else 0
            resultado.append({
                "id": budget.id,
                "grupo": budget.grupo,
                "categoria_geral": categoria_geral,
                "cor": getattr(budget, 'cor', None),
                "valor_planejado": float(budget.valor_planejado),
                "valor_realizado": valor_realizado,
                "percentual": round(percentual, 2),
                "ativo": budget.ativo,
                "valor_medio_3_meses": float(budget.valor_medio_3_meses)
            })
        
        # Adicionar grupos com gasto que não têm budget_planning
        for grupo, total in grupos_com_gasto:
            if grupo in by_grupo:
                continue
            valor_realizado = abs(float(total))
            categoria_geral = grupos_config.get(grupo) or 'Despesa'
            resultado.append({
                "id": None,  # Sem meta definida
                "grupo": grupo,
                "categoria_geral": categoria_geral,
                "cor": None,
                "valor_planejado": 0.0,
                "valor_realizado": valor_realizado,
                "percentual": 0.0,
                "ativo": 1,
                "valor_medio_3_meses": 0.0
            })
        # Adicionar grupos com investimento que não têm budget_planning
        for grupo, total in grupos_com_investimento:
            if grupo in by_grupo:
                continue
            valor_realizado = abs(float(total))
            categoria_geral = grupos_config.get(grupo) or 'Investimentos'
            resultado.append({
                "id": None,  # Sem meta definida
                "grupo": grupo,
                "categoria_geral": categoria_geral,
                "cor": None,
                "valor_planejado": 0.0,
                "valor_realizado": valor_realizado,
                "percentual": 0.0,
                "ativo": 1,
                "valor_medio_3_meses": 0.0
            })
        
        return {
            "mes_referencia": mes_referencia,
            "budgets": resultado
        }
    
    def get_budget_planning_by_id(self, user_id: int, budget_id: int) -> dict:
        """
        Busca uma meta de planning por ID com valor_realizado e percentual
        """
        budget = self.repository.get_by_id(budget_id, user_id)
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta não encontrada"
            )
        from app.domains.grupos.models import BaseGruposConfig
        mes_referencia = budget.mes_referencia
        grupo_config = self.db.query(BaseGruposConfig).filter(
            BaseGruposConfig.nome_grupo == budget.grupo
        ).first()
        categoria_geral = grupo_config.categoria_geral if grupo_config else 'Despesa'
        valor_realizado_raw = self._calcular_valor_realizado_grupo(
            user_id, budget.grupo, mes_referencia, categoria_geral
        )
        valor_realizado = abs(float(valor_realizado_raw)) if valor_realizado_raw else 0.0
        percentual = (valor_realizado / budget.valor_planejado * 100) if budget.valor_planejado > 0 else 0
        subgrupos = self._get_subgrupos_grupo(user_id, budget.grupo, mes_referencia)
        return {
            "id": budget.id,
            "grupo": budget.grupo,
            "categoria_geral": categoria_geral,
            "cor": getattr(budget, 'cor', None),
            "mes_referencia": mes_referencia,
            "valor_planejado": float(budget.valor_planejado),
            "valor_realizado": valor_realizado,
            "percentual": round(percentual, 2),
            "ativo": budget.ativo,
            "valor_medio_3_meses": float(budget.valor_medio_3_meses),
            "subgrupos": subgrupos,
        }
    
    def bulk_upsert_budget_planning(
        self, 
        user_id: int, 
        mes_referencia: str, 
        budgets: List[dict]
    ) -> List[dict]:
        """
        Cria ou atualiza múltiplas metas de planning
        
        Args:
            user_id: ID do usuário
            mes_referencia: Mês no formato YYYY-MM
            budgets: Lista de dicts com grupo e valor_planejado
            
        Returns:
            Lista de budgets criados/atualizados
        """
        from .models import BudgetPlanning
        
        resultado = []
        for budget_data in budgets:
            grupo = budget_data["grupo"]
            valor_planejado = budget_data["valor_planejado"]
            cor = budget_data.get("cor")
            budget_id = budget_data.get("id")
            
            # Se id fornecido, buscar por id; senão por grupo+mes
            if budget_id:
                budget_existente = self.db.query(BudgetPlanning).filter(
                    BudgetPlanning.id == budget_id,
                    BudgetPlanning.user_id == user_id
                ).first()
                if budget_existente:
                    budget_existente.grupo = grupo  # permite alterar grupo
            else:
                budget_existente = self.db.query(BudgetPlanning).filter(
                    BudgetPlanning.user_id == user_id,
                    BudgetPlanning.grupo == grupo,
                    BudgetPlanning.mes_referencia == mes_referencia
                ).first()
            
            if budget_existente:
                # Atualizar (também por id se fornecido)
                budget_existente.valor_planejado = valor_planejado
                if cor is not None:
                    budget_existente.cor = cor
                self.db.flush()
                resultado.append({
                    "id": budget_existente.id,
                    "grupo": budget_existente.grupo,
                    "cor": getattr(budget_existente, 'cor', None),
                    "mes_referencia": budget_existente.mes_referencia,
                    "valor_planejado": float(budget_existente.valor_planejado)
                })
            else:
                # Criar novo
                novo_budget = BudgetPlanning(
                    user_id=user_id,
                    grupo=grupo,
                    mes_referencia=mes_referencia,
                    valor_planejado=valor_planejado,
                    cor=cor
                )
                self.db.add(novo_budget)
                self.db.flush()
                resultado.append({
                    "id": novo_budget.id,
                    "grupo": novo_budget.grupo,
                    "cor": getattr(novo_budget, 'cor', None),
                    "mes_referencia": novo_budget.mes_referencia,
                    "valor_planejado": float(novo_budget.valor_planejado)
                })
        
        self.db.commit()
        return resultado
    
    def _calcular_valor_realizado_grupo(
        self, user_id: int, grupo: str, mes_referencia: str, categoria_geral: str = 'Despesa'
    ) -> float:
        """
        Calcula valor realizado de um grupo em um mês.
        Usa CategoriaGeral conforme categoria_geral do grupo (Despesa ou Investimentos).
        
        Args:
            user_id: ID do usuário
            grupo: Nome do grupo
            mes_referencia: Mês no formato YYYY-MM
            categoria_geral: 'Despesa' ou 'Investimentos' (define qual CategoriaGeral filtrar)
            
        Returns:
            Valor realizado (float)
        """
        ano, mes = mes_referencia.split('-')
        mes_fatura = f"{ano}{mes}"  # YYYYMM
        cat_geral = 'Investimentos' if categoria_geral == 'Investimentos' else 'Despesa'
        
        total = self.db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo,
            JournalEntry.MesFatura == mes_fatura,
            JournalEntry.CategoriaGeral == cat_geral,
            JournalEntry.IgnorarDashboard == 0
        ).scalar()
        
        return float(total) if total else 0.0
    
    def _get_subgrupos_grupo(self, user_id: int, grupo: str, mes_referencia: str) -> List[dict]:
        """
        Retorna subgrupos de um grupo no mês - mesma fonte que valor realizado
        Garante que a soma dos subgrupos = valor realizado total
        """
        ano, mes = mes_referencia.split('-')
        mes_fatura = f"{ano}{mes}"
        
        from sqlalchemy import func
        results = (
            self.db.query(
                JournalEntry.SUBGRUPO.label('subgrupo'),
                func.sum(JournalEntry.Valor).label('valor')
            )
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.GRUPO == grupo,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == 'Despesa',
                JournalEntry.IgnorarDashboard == 0
            )
            .group_by(JournalEntry.SUBGRUPO)
        ).all()
        
        total_abs = abs(sum(r.valor for r in results)) or 1.0
        return [
            {
                "subgrupo": r.subgrupo or "Sem subgrupo",
                "valor": abs(float(r.valor)),
                "percentual": round((abs(r.valor) / total_abs) * 100, 1)
            }
            for r in sorted(results, key=lambda x: abs(x.valor), reverse=True)
        ]
    
    def calcular_media_3_meses(self, user_id: int, grupo: str, mes_referencia: str) -> float:
        """
        Calcula média dos últimos 3 meses anteriores ao mes_referencia
        
        Args:
            user_id: ID do usuário
            grupo: Grupo (Casa, Cartão, etc)
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
            mes_fatura_format = f"{ano_mes}{mes_num}"  # YYYYMM
            condicoes_meses.append(JournalEntry.MesFatura == mes_fatura_format)
        
        # Buscar transações dos 3 meses anteriores
        transacoes = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0,  # Excluir transações ignoradas
            or_(*condicoes_meses)
        ).all()
        
        if not transacoes:
            return 0.0
        
        # Agrupar por mês e calcular soma
        meses_com_dados = {}
        for t in transacoes:
            # Usar MesFatura para agrupar
            if t.MesFatura:
                mes_fatura = t.MesFatura  # YYYYMM
                if mes_fatura not in meses_com_dados:
                    meses_com_dados[mes_fatura] = 0
                meses_com_dados[mes_fatura] += abs(t.Valor)
        
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
        grupo: str, 
        mes_referencia: str
    ):
        """
        Retorna detalhamento dos 3 meses que compõem a média
        
        Args:
            user_id: ID do usuário
            grupo: Grupo (Casa, Cartão, etc)
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
            mes_fatura_format = f"{ano_mes}{mes_num}"  # YYYYMM
            condicoes_meses.append(JournalEntry.MesFatura == mes_fatura_format)
        
        # Buscar transações dos 3 meses anteriores
        transacoes = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.GRUPO == grupo,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.IgnorarDashboard == 0,  # Excluir transações ignoradas
            or_(*condicoes_meses)
        ).all()
        
        # Agrupar por mês
        detalhes_por_mes = {}
        for mes_ant in meses_anteriores:
            ano_mes, mes_num = mes_ant.split('-')
            mes_fatura_format = f"{ano_mes}{mes_num}"  # YYYYMM
            detalhes_por_mes[mes_fatura_format] = {
                'mes_referencia': mes_ant,
                'transacoes': [],
                'total': 0.0
            }
        
        for t in transacoes:
            if t.MesFatura and t.MesFatura in detalhes_por_mes:
                detalhes_por_mes[t.MesFatura]['transacoes'].append(t)
                detalhes_por_mes[t.MesFatura]['total'] += abs(t.Valor)
                
                # Agrupar por subgrupo
                if 'subgrupos' not in detalhes_por_mes[t.MesFatura]:
                    detalhes_por_mes[t.MesFatura]['subgrupos'] = {}
                
                subgrupo_key = t.SUBGRUPO if t.SUBGRUPO else '__SEM_SUBGRUPO__'
                if subgrupo_key not in detalhes_por_mes[t.MesFatura]['subgrupos']:
                    detalhes_por_mes[t.MesFatura]['subgrupos'][subgrupo_key] = {
                        'valor': 0.0,
                        'quantidade': 0
                    }
                
                detalhes_por_mes[t.MesFatura]['subgrupos'][subgrupo_key]['valor'] += abs(t.Valor)
                detalhes_por_mes[t.MesFatura]['subgrupos'][subgrupo_key]['quantidade'] += 1
        
        # Construir lista de MesDetalhamento
        meses_detalhados = []
        total_geral = 0.0
        
        # Ordenar meses do mais antigo para o mais recente
        for mes_ref in sorted(meses_anteriores):
            ano_mes, mes_num = mes_ref.split('-')
            mes_fatura_format = f"{ano_mes}{mes_num}"  # YYYYMM
            
            if mes_fatura_format in detalhes_por_mes:
                detalhes = detalhes_por_mes[mes_fatura_format]
                mes_nome = f"{meses_nomes[mes_num]} {ano_mes}"
                
                # Criar lista de subgrupos
                subgrupos_list = []
                if 'subgrupos' in detalhes:
                    from .schemas import SubgrupoDetalhamento
                    for subgrupo_key, dados in detalhes['subgrupos'].items():
                        subgrupo_nome = None if subgrupo_key == '__SEM_SUBGRUPO__' else subgrupo_key
                        subgrupos_list.append(SubgrupoDetalhamento(
                            subgrupo=subgrupo_nome,
                            valor_total=round(dados['valor'], 2),
                            quantidade_transacoes=dados['quantidade']
                        ))
                    # Ordenar por valor decrescente
                    subgrupos_list.sort(key=lambda x: x.valor_total, reverse=True)
                
                mes_det = MesDetalhamento(
                    mes_referencia=mes_ref,
                    mes_nome=mes_nome,
                    valor_total=round(detalhes['total'], 2),
                    quantidade_transacoes=len(detalhes['transacoes']),
                    subgrupos=subgrupos_list if subgrupos_list else None
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
            grupo=grupo,
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
        # Verificar se já existe budget para este grupo/mês
        existing = self.repository.get_by_tipo_gasto_and_month(
            user_id, 
            data.grupo,
            data.mes_referencia
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe budget para {data.grupo} em {data.mes_referencia}. Use PUT para atualizar."
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
        
        # Verificar conflitos se alterar grupo ou mês
        if data.grupo or data.mes_referencia:
            new_grupo = data.grupo if data.grupo else budget.grupo
            new_mes = data.mes_referencia if data.mes_referencia else budget.mes_referencia
            
            # Só verifica se mudou algo
            if new_grupo != budget.grupo or new_mes != budget.mes_referencia:
                existing = self.repository.get_by_tipo_gasto_and_month(
                    user_id, 
                    new_grupo,
                    new_mes
                )
                
                if existing and existing.id != budget_id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Já existe budget para {new_grupo} em {new_mes}. Use outro grupo ou mês."
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
    
    def toggle_budget_ativo(self, budget_id: int, user_id: int, ativo: int) -> dict:
        """
        Toggle campo 'ativo' do budget (0=inativo, 1=ativo)
        
        IMPORTANTE: Não modifica valor_planejado - apenas status
        """
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        # Atualizar apenas campo ativo (repository.update precisa de dict)
        updated_budget = self.repository.update(budget, {"ativo": ativo})
        
        return {
            "id": updated_budget.id,
            "grupo": updated_budget.grupo,
            "mes_referencia": updated_budget.mes_referencia,
            "valor_planejado": updated_budget.valor_planejado,
            "ativo": updated_budget.ativo,
            "message": f"Meta {'ativada' if ativo == 1 else 'desativada'} com sucesso"
        }
    
    def bulk_upsert_budgets(
        self, 
        user_id: int, 
        mes_referencia: str, 
        budgets: List[dict]
    ) -> List[BudgetResponse]:
        """Cria ou atualiza múltiplos budgets de uma vez"""
        # Validar dados
        for budget_data in budgets:
            if "grupo" not in budget_data or "valor_planejado" not in budget_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada budget deve ter 'grupo' e 'valor_planejado'"
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
                grupo=budget_data["grupo"],
                mes_referencia=mes_referencia
            )
            
            # Upsert com média
            budget = self.repository.upsert(
                user_id=user_id,
                grupo=budget_data["grupo"],
                mes_referencia=mes_referencia,
                valor_planejado=budget_data["valor_planejado"],
                valor_medio_3_meses=media
            )
            result.append(budget)
        
        return [BudgetResponse.from_orm(b) for b in result]

    
    # ═══════════════════════════════════════════════════════════════════════════════
    # MÉTODOS OBSOLETOS - REMOVIDOS EM 13/02/2026
    # ═══════════════════════════════════════════════════════════════════════════════
    # Retornam HTTP 410 Gone se chamados
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_budget_geral_by_month(self, user_id: int, mes_referencia: str):
        """OBSOLETO - Use get_budget_planning()"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Use /api/v1/budget/planning")
    
    def get_all_budget_geral(self, user_id: int):
        """OBSOLETO - Use get_budget_planning()"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Use /api/v1/budget/planning")
    
    def bulk_upsert_budget_geral(self, user_id: int, mes_referencia: str, budgets: List[dict]):
        """OBSOLETO - Use bulk_upsert_budget_planning()"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Use /api/v1/budget/planning/bulk-upsert")
    
    def get_categorias_config(self, user_id: int, apenas_ativas: bool = True):
        """OBSOLETO - Categorias fixas"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def create_categoria_config(self, user_id: int, data: dict):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def update_categoria_config(self, config_id: int, user_id: int, data: dict):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def reordenar_categorias(self, user_id: int, reorders: List[Dict[str, int]]):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def update_tipos_gasto_categoria(self, config_id: int, user_id: int, tipos_gasto: list):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def delete_categoria_config(self, config_id: int, user_id: int):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def bulk_upsert_budget_geral_com_validacao(self, user_id: int, mes_referencia: str, budgets: List[dict], total_mensal: float = None):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Endpoint removido")
    
    def get_tipos_gasto_disponiveis(self, user_id: int, fonte_dados: str, filtro_valor: str):
        """OBSOLETO"""
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Tipos fixos (base_grupos_config)")
