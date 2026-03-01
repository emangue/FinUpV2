"""Service do domínio Plano"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from .models import UserFinancialProfile, PlanoMetaCategoria, BaseExpectativa

logger = logging.getLogger(__name__)



class PlanoService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_renda(self, user_id: int, renda: float) -> dict:
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        if not profile:
            profile = UserFinancialProfile(user_id=user_id)
            self.db.add(profile)
        profile.renda_mensal_liquida = renda
        self.db.commit()
        self.db.refresh(profile)
        return {"success": True, "renda": float(profile.renda_mensal_liquida or 0)}

    def get_renda(self, user_id: int) -> Optional[float]:
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        return float(profile.renda_mensal_liquida) if profile and profile.renda_mensal_liquida else None

    def get_resumo(self, user_id: int, ano: int, mes: int) -> dict:
        """A.07: Resumo com renda, total_budget (budget_planning Despesa), disponivel_real = renda - total_budget"""
        renda = self.get_renda(user_id)
        mes_ref = f"{ano}-{str(mes).zfill(2)}"
        from app.domains.budget.models import BudgetPlanning
        from app.domains.grupos.models import BaseGruposConfig
        total_budget = self.db.query(func.sum(BudgetPlanning.valor_planejado)).join(
            BaseGruposConfig,
            (BudgetPlanning.user_id == BaseGruposConfig.user_id)
            & (BudgetPlanning.grupo == BaseGruposConfig.nome_grupo),
        ).filter(
            BudgetPlanning.user_id == user_id,
            BudgetPlanning.mes_referencia == mes_ref,
            BudgetPlanning.ativo == True,
            BaseGruposConfig.categoria_geral == "Despesa",
        ).scalar()
        total_budget = float(total_budget or 0)
        disponivel_real = (renda - total_budget) if renda is not None else None
        return {
            "renda": renda,
            "total_budget": total_budget,
            "disponivel_real": disponivel_real,
        }

    def get_orcamento(self, user_id: int, ano: int, mes: int) -> list:
        """Gasto real vs meta por grupo. Inclui grupos com meta mesmo sem gasto (conexão restrição/metas)."""
        mes_fatura = f"{ano}{str(mes).zfill(2)}"  # YYYYMM (consistente com budget/dashboard)
        gastos_raw = self.db.execute(text("""
            SELECT "GRUPO" as grupo, COALESCE(SUM(ABS("Valor")), 0) as gasto
            FROM journal_entries
            WHERE user_id = :uid AND "MesFatura" = :mes_fatura
              AND "CategoriaGeral" = 'Despesa' AND "IgnorarDashboard" = 0
              AND "GRUPO" IS NOT NULL AND "GRUPO" != ''
            GROUP BY "GRUPO"
        """), {"uid": user_id, "mes_fatura": mes_fatura}).fetchall()
        gastos_dict = {g.grupo or "(sem grupo)": float(g.gasto) for g in gastos_raw}

        metas = {
            m.grupo: float(m.valor_meta)
            for m in self.db.query(PlanoMetaCategoria).filter(
                PlanoMetaCategoria.user_id == user_id,
                PlanoMetaCategoria.ano == ano,
                PlanoMetaCategoria.mes == mes,
            ).all()
        }

        # Fallback: metas do budget_planning (valor_planejado) - apenas grupos Despesa
        if not metas:
            from app.domains.budget.models import BudgetPlanning
            from app.domains.grupos.models import BaseGruposConfig
            mes_ref = f"{ano}-{str(mes).zfill(2)}"
            bp = (
                self.db.query(BudgetPlanning)
                .join(
                    BaseGruposConfig,
                    (BudgetPlanning.user_id == BaseGruposConfig.user_id)
                    & (BudgetPlanning.grupo == BaseGruposConfig.nome_grupo),
                )
                .filter(
                    BudgetPlanning.user_id == user_id,
                    BudgetPlanning.mes_referencia == mes_ref,
                    BudgetPlanning.ativo == True,
                    BaseGruposConfig.categoria_geral == "Despesa",
                )
                .all()
            )
            metas = {b.grupo: float(b.valor_planejado) for b in bp}

        # União: grupos com gasto OU com meta (mostra restrições mesmo sem gasto)
        all_grupos = sorted(set(gastos_dict.keys()) | set(metas.keys()))
        resultado = []
        for grupo in all_grupos:
            gasto = gastos_dict.get(grupo, 0.0)
            meta = metas.get(grupo)
            pct = (gasto / meta * 100) if meta and meta > 0 else None
            if pct is not None:
                status = "ok" if pct <= 100 else "excedido"
            else:
                status = "sem_meta"
            resultado.append({
                "grupo": grupo,
                "gasto": gasto,
                "meta": meta,
                "percentual": round(pct, 1) if pct is not None else None,
                "status": status,
            })
        return resultado

    def get_impacto_longo_prazo(self, user_id: int, ano: int, mes: int) -> Optional[dict]:
        """Anos perdidos quando gasto/plano > renda. Retorna None se sem déficit ou sem perfil."""
        resumo = self.get_resumo(user_id, ano, mes)
        renda = resumo.get("renda")
        disponivel = resumo.get("disponivel_real")
        total_budget = resumo.get("total_budget", 0)

        if renda is None or renda <= 0:
            return None
        if disponivel is None or disponivel >= 0:
            return None

        deficit_mensal = -float(disponivel)
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        if not profile:
            return {
                "deficit_mensal": deficit_mensal,
                "anos_perdidos": None,
                "mensagem": "Com esse nível de gasto você está gastando mais do que ganha.",
            }

        taxa = float(profile.taxa_retorno_anual or 0.08)
        idade_atual = profile.idade_atual or 30
        idade_apos = profile.idade_aposentadoria or 65
        anos_restantes = max(0, idade_apos - idade_atual)
        meses = anos_restantes * 12

        taxa_mensal = (1 + taxa) ** (1 / 12) - 1
        if taxa_mensal > 0 and meses > 0:
            custo_oportunidade = deficit_mensal * ((1 + taxa_mensal) ** meses - 1) / taxa_mensal
        else:
            custo_oportunidade = deficit_mensal * meses

        renda_anual = renda * 12
        anos_perdidos = custo_oportunidade / renda_anual if renda_anual > 0 else 0

        return {
            "deficit_mensal": round(deficit_mensal, 2),
            "custo_oportunidade_futuro": round(custo_oportunidade, 2),
            "anos_perdidos": round(anos_perdidos, 1),
            "anos_restantes_para_aposentadoria": anos_restantes,
            "mensagem": f"Com esse nível de gasto você está perdendo ~{anos_perdidos:.1f} anos de aposentadoria.",
        }

    def salvar_meta(self, user_id: int, grupo: str, valor_meta: float, ano: int, mes: int) -> dict:
        m = self.db.query(PlanoMetaCategoria).filter(
            PlanoMetaCategoria.user_id == user_id,
            PlanoMetaCategoria.grupo == grupo,
            PlanoMetaCategoria.ano == ano,
            PlanoMetaCategoria.mes == mes,
        ).first()
        if m:
            m.valor_meta = valor_meta
        else:
            m = PlanoMetaCategoria(
                user_id=user_id,
                grupo=grupo,
                valor_meta=valor_meta,
                ano=ano,
                mes=mes,
            )
            self.db.add(m)
        self.db.commit()
        return {"success": True}

    def update_perfil(
        self,
        user_id: int,
        renda: Optional[float] = None,
        aporte_planejado: Optional[float] = None,
        idade_atual: Optional[int] = None,
        idade_aposentadoria: Optional[int] = None,
        patrimonio_atual: Optional[float] = None,
        taxa_retorno_anual: Optional[float] = None,
    ) -> dict:
        """PUT /plano/perfil - atualiza campos do perfil financeiro"""
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        if not profile:
            profile = UserFinancialProfile(user_id=user_id)
            self.db.add(profile)
        if renda is not None:
            profile.renda_mensal_liquida = renda
        if aporte_planejado is not None:
            profile.aporte_planejado = aporte_planejado
        if idade_atual is not None:
            profile.idade_atual = idade_atual
        if idade_aposentadoria is not None:
            profile.idade_aposentadoria = idade_aposentadoria
        if patrimonio_atual is not None:
            profile.patrimonio_atual = patrimonio_atual
        if taxa_retorno_anual is not None:
            profile.taxa_retorno_anual = taxa_retorno_anual
        self.db.commit()
        self.db.refresh(profile)
        return {
            "renda_mensal_liquida": profile.renda_mensal_liquida,
            "aporte_planejado": profile.aporte_planejado,
            "idade_atual": profile.idade_atual,
            "idade_aposentadoria": profile.idade_aposentadoria,
            "patrimonio_atual": profile.patrimonio_atual,
            "taxa_retorno_anual": profile.taxa_retorno_anual,
        }

    def get_cashflow(self, user_id: int, ano: int) -> dict:
        """
        GET /plano/cashflow?ano= - 12 meses: renda, gastos, aporte, saldo, status.
        Sem base_expectativas: gastos_extras_esperados=0, expectativas=[].
        """
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        renda = float(profile.renda_mensal_liquida) if profile and profile.renda_mensal_liquida else 0.0
        aporte = float(profile.aporte_planejado or 0) if profile else 0.0

        from app.domains.budget.models import BudgetPlanning
        from app.domains.transactions.models import JournalEntry
        from app.domains.grupos.models import BaseGruposConfig

        meses = []
        hoje_ano = 0
        hoje_mes = 0
        try:
            from datetime import date
            d = date.today()
            hoje_ano, hoje_mes = d.year, d.month
        except Exception:
            pass

        for m in range(1, 13):
            mes_ref = f"{ano}-{str(m).zfill(2)}"
            mes_fatura = f"{ano}{str(m).zfill(2)}"

            # renda_realizada: SUM(Valor) WHERE CategoriaGeral = 'Receita'
            renda_real = self.db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == "Receita",
                JournalEntry.IgnorarDashboard == 0,
            ).scalar()
            renda_realizada = float(renda_real) if renda_real is not None else None
            if renda_realizada is not None and renda_realizada < 0:
                renda_realizada = 0.0  # Receita não deve ser negativa

            # investimentos_realizados: SUM(ABS(Valor)) WHERE CategoriaGeral = 'Investimentos'
            inv_real = self.db.query(func.sum(func.abs(JournalEntry.Valor))).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == "Investimentos",
                JournalEntry.IgnorarDashboard == 0,
            ).scalar()
            investimentos_realizados = float(inv_real) if inv_real is not None else None

            # gastos_recorrentes: budget_planning APENAS grupos com categoria_geral = 'Despesa'
            gastos_rec = (
                self.db.query(func.sum(BudgetPlanning.valor_planejado))
                .join(
                    BaseGruposConfig,
                    (BudgetPlanning.user_id == BaseGruposConfig.user_id)
                    & (BudgetPlanning.grupo == BaseGruposConfig.nome_grupo),
                )
                .filter(
                    BudgetPlanning.user_id == user_id,
                    BudgetPlanning.mes_referencia == mes_ref,
                    BudgetPlanning.ativo == True,
                    BaseGruposConfig.categoria_geral == "Despesa",
                )
                .scalar()
            )
            gastos_recorrentes = float(gastos_rec or 0)

            # gastos_realizados: APENAS CategoriaGeral = 'Despesa'
            gastos_real = self.db.query(func.sum(func.abs(JournalEntry.Valor))).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == "Despesa",
                JournalEntry.IgnorarDashboard == 0,
            ).scalar()
            gastos_realizados = float(gastos_real) if gastos_real else None

            # Troca para realizado quando receita >= 90% do esperado (receita, despesas, investimentos)
            use_realizado = (
                renda_realizada is not None
                and renda is not None
                and renda > 0
                and renda_realizada >= 0.9 * renda
            )

            if use_realizado:
                renda_usada = max(0.9 * renda, renda_realizada)
                gastos_usados = gastos_realizados if gastos_realizados is not None else gastos_recorrentes
                aporte_usado = investimentos_realizados if investimentos_realizados is not None else aporte
            else:
                renda_usada = renda
                gastos_usados = gastos_recorrentes
                aporte_usado = aporte

            # Fase 4: base_expectativas (debitos - creditos do mês)
            exp_mes = self.get_expectativas_por_mes(user_id, ano).get(mes_ref, {"debitos": 0.0, "creditos": 0.0, "items": []})
            gastos_extras = exp_mes["debitos"] - exp_mes["creditos"]
            expectativas_items = exp_mes.get("items", [])

            total_gastos = gastos_usados + gastos_extras
            saldo = renda_usada - total_gastos - aporte_usado if renda_usada else None

            # status_mes: ok, parcial, futuro, negativo
            if m < hoje_mes and ano <= hoje_ano:
                status_mes = "ok" if (saldo is None or saldo >= 0) else "negativo"
            elif m == hoje_mes and ano == hoje_ano:
                status_mes = "parcial"
            else:
                status_mes = "futuro"

            meses.append({
                "mes_referencia": mes_ref,
                "renda_esperada": renda,
                "renda_realizada": round(renda_realizada, 2) if renda_realizada is not None else None,
                "renda_usada": round(renda_usada, 2),
                "gastos_recorrentes": gastos_recorrentes,
                "gastos_extras_esperados": round(gastos_extras, 2),
                "gastos_realizados": gastos_realizados,
                "gastos_usados": round(gastos_usados, 2),
                "aporte_planejado": aporte,
                "investimentos_realizados": round(investimentos_realizados, 2) if investimentos_realizados is not None else None,
                "aporte_usado": round(aporte_usado, 2),
                "use_realizado": use_realizado,
                "saldo_projetado": round(saldo, 2) if saldo is not None else None,
                "status_mes": status_mes,
                "grupos": [],
                "expectativas": expectativas_items,
            })

        # nudge_acumulado: soma dos saldos negativos
        nudge = sum(
            (m["saldo_projetado"] or 0) for m in meses
            if m["saldo_projetado"] is not None and m["saldo_projetado"] < 0
        )
        return {"ano": ano, "nudge_acumulado": round(nudge, 2), "meses": meses}

    def get_projecao(
        self,
        user_id: int,
        ano: int,
        meses: int = 12,
        reducao_pct: float = 0.0,
    ) -> dict:
        """
        GET /plano/projecao - poupança acumulada mês a mês com opção de redução de gastos.
        reducao_pct: 0-100, percentual de redução nos gastos planejados.
        """
        cashflow = self.get_cashflow(user_id, ano)
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        patrimonio = float(profile.patrimonio_atual or 0) if profile else 0.0

        fator = 1.0 - (reducao_pct / 100.0)
        acumulado = patrimonio
        serie = []
        for i, m in enumerate(cashflow["meses"][:meses]):
            renda_mes = m.get("renda_usada") or 0.0
            gastos_base = m.get("gastos_usados") or (m["gastos_realizados"] or m["gastos_recorrentes"])
            extras = m.get("gastos_extras_esperados", 0) or 0
            gastos = (gastos_base * fator) + extras
            aporte_mes = m.get("aporte_usado") or m["aporte_planejado"]
            saldo_mes = renda_mes - gastos - aporte_mes
            acumulado += saldo_mes
            serie.append({
                "mes": i + 1,
                "mes_referencia": m["mes_referencia"],
                "saldo_mes": round(saldo_mes, 2),
                "acumulado": round(acumulado, 2),
            })
        return {
            "patrimonio_inicial": patrimonio,
            "reducao_pct": reducao_pct,
            "serie": serie,
        }

    def list_expectativas(self, user_id: int, mes: Optional[str] = None) -> list:
        """Lista expectativas do usuário, opcionalmente filtradas por mês."""
        q = self.db.query(BaseExpectativa).filter(
            BaseExpectativa.user_id == user_id,
            BaseExpectativa.status != "cancelado",
        )
        if mes:
            q = q.filter(BaseExpectativa.mes_referencia == mes)
        rows = q.order_by(BaseExpectativa.mes_referencia, BaseExpectativa.id).all()
        return [
            {
                "id": r.id,
                "descricao": r.descricao,
                "valor": float(r.valor),
                "grupo": r.grupo,
                "tipo_lancamento": r.tipo_lancamento or "debito",
                "mes_referencia": r.mes_referencia,
                "tipo_expectativa": r.tipo_expectativa,
                "status": r.status or "pendente",
            }
            for r in rows
        ]

    def create_expectativa(
        self,
        user_id: int,
        descricao: str,
        valor: float,
        mes_referencia: str,
        grupo: Optional[str] = None,
        tipo_lancamento: str = "debito",
        tipo_expectativa: str = "sazonal_plano",
    ) -> dict:
        """Cria expectativa (sazonal ou renda)."""
        e = BaseExpectativa(
            user_id=user_id,
            descricao=descricao,
            valor=valor,
            grupo=grupo,
            tipo_lancamento=tipo_lancamento,
            mes_referencia=mes_referencia,
            tipo_expectativa=tipo_expectativa,
            origem="usuario",
        )
        self.db.add(e)
        self.db.commit()
        self.db.refresh(e)
        return {
            "id": e.id,
            "descricao": e.descricao,
            "valor": float(e.valor),
            "grupo": e.grupo,
            "tipo_lancamento": e.tipo_lancamento or "debito",
            "mes_referencia": e.mes_referencia,
            "tipo_expectativa": e.tipo_expectativa,
            "status": e.status or "pendente",
        }

    def delete_expectativa(self, user_id: int, expectativa_id: int) -> bool:
        """Remove ou marca como cancelado."""
        e = self.db.query(BaseExpectativa).filter(
            BaseExpectativa.id == expectativa_id,
            BaseExpectativa.user_id == user_id,
        ).first()
        if not e:
            return False
        self.db.delete(e)
        self.db.commit()
        return True

    def get_expectativas_por_mes(self, user_id: int, ano: int) -> dict:
        """Retorna { mes_referencia: { debitos: float, creditos: float, items: [...] } }."""
        rows = self.db.query(BaseExpectativa).filter(
            BaseExpectativa.user_id == user_id,
            BaseExpectativa.mes_referencia.like(f"{ano}-%"),
            BaseExpectativa.status == "pendente",
        ).all()
        by_mes: dict = {}
        for r in rows:
            mes = r.mes_referencia
            if mes not in by_mes:
                by_mes[mes] = {"debitos": 0.0, "creditos": 0.0, "items": []}
            v = float(r.valor)
            if r.tipo_lancamento == "credito":
                by_mes[mes]["creditos"] += v
            else:
                by_mes[mes]["debitos"] += v
            by_mes[mes]["items"].append({
                "id": r.id,
                "descricao": r.descricao,
                "valor": v,
                "tipo_lancamento": r.tipo_lancamento,
            })
        return by_mes
