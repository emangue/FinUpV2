"""Service do domínio Plano"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from .models import UserFinancialProfile, PlanoMetaCategoria

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
        """A.07: Resumo com renda, total_budget (budget_planning), disponivel_real = renda - total_budget"""
        renda = self.get_renda(user_id)
        mes_ref = f"{ano}-{str(mes).zfill(2)}"
        from app.domains.budget.models import BudgetPlanning
        total_budget = self.db.query(func.sum(BudgetPlanning.valor_planejado)).filter(
            BudgetPlanning.user_id == user_id,
            BudgetPlanning.mes_referencia == mes_ref,
            BudgetPlanning.ativo == True,
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
              AND "CategoriaGeral" != 'Receita' AND "IgnorarDashboard" = 0
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

        # Fallback: metas do budget_planning (valor_planejado)
        if not metas:
            from app.domains.budget.models import BudgetPlanning
            mes_ref = f"{ano}-{str(mes).zfill(2)}"
            bp = self.db.query(BudgetPlanning).filter(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia == mes_ref,
                BudgetPlanning.ativo == True,  # PostgreSQL: boolean; SQLite: int 1
            ).all()
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

    def get_impacto_longo_prazo(self, user_id: int, ano: int, mes: int) -> dict | None:
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
