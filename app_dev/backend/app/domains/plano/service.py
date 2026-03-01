"""Service do domínio Plano"""
import json
import logging
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from .models import UserFinancialProfile, PlanoMetaCategoria, BaseExpectativa, ExpectativaMes

logger = logging.getLogger(__name__)

# Intervalo em meses por recorrência (para expansão em expectativas_mes)
RECORRENCIA_INTERVAL = {"unico": 0, "bimestral": 2, "trimestral": 3, "semestral": 6, "anual": 12}



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

    def get_planejado_por_grupo_mes(self, user_id: int, ano: int, mes: int) -> dict:
        """
        Total planejado por grupo = budget_planning + expectativas_mes (seção 5.1).
        Retorna { grupo: valor_total } apenas para grupos Despesa.
        """
        mes_ref = f"{ano}-{str(mes).zfill(2)}"
        from app.domains.budget.models import BudgetPlanning
        from app.domains.grupos.models import BaseGruposConfig

        # Budget base (Despesa)
        bp_rows = (
            self.db.query(BudgetPlanning.grupo, BudgetPlanning.valor_planejado)
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
        result = {r.grupo: float(r.valor_planejado or 0) for r in bp_rows}

        # Extraordinários (expectativas_mes, tipo debito)
        exp_rows = (
            self.db.query(ExpectativaMes.grupo, func.sum(ExpectativaMes.valor))
            .filter(
                ExpectativaMes.user_id == user_id,
                ExpectativaMes.mes_referencia == mes_ref,
                ExpectativaMes.tipo == "debito",
                ExpectativaMes.grupo.isnot(None),
                ExpectativaMes.grupo != "",
            )
            .group_by(ExpectativaMes.grupo)
            .all()
        )
        for r in exp_rows:
            if r.grupo:
                result[r.grupo] = result.get(r.grupo, 0) + float(r[1] or 0)

        return result

    def get_resumo(self, user_id: int, ano: int, mes: int) -> dict:
        """A.07: Resumo com renda, total_budget (budget + expectativas_mes), disponivel_real = renda - total_budget"""
        renda = self.get_renda(user_id)
        planejado = self.get_planejado_por_grupo_mes(user_id, ano, mes)
        total_budget = sum(planejado.values())
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

        # Fallback: metas = budget_planning + expectativas_mes (get_planejado_por_grupo_mes)
        if not metas:
            metas = self.get_planejado_por_grupo_mes(user_id, ano, mes)

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

            # renda_realizada: sum(Valor) de CategoriaGeral=Receita (sem exigir GRUPO, como gastos)
            renda_total = self.db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == "Receita",
                JournalEntry.IgnorarDashboard == 0,
            ).scalar()
            renda_realizada = max(0.0, float(renda_total)) if renda_total else None

            # investimentos_realizados: sum(Valor) de CategoriaGeral=Investimentos (sem exigir GRUPO, como gastos)
            inv_total = self.db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == "Investimentos",
                JournalEntry.IgnorarDashboard == 0,
            ).scalar()
            investimentos_realizados = abs(float(inv_total)) if inv_total else None

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

            # gastos_realizados: sum(Valor) real (como dashboard) — neta estornos; abs só para exibição
            gastos_real = self.db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.user_id == user_id,
                JournalEntry.MesFatura == mes_fatura,
                JournalEntry.CategoriaGeral == "Despesa",
                JournalEntry.IgnorarDashboard == 0,
            ).scalar()
            gastos_realizados = abs(float(gastos_real)) if gastos_real else None

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

            # Fase 4: base_expectativas — APENAS em modo planejado (não misturar real com expectativa)
            exp_mes = self.get_expectativas_por_mes(user_id, ano).get(mes_ref, {"debitos": 0.0, "creditos": 0.0, "items": []})
            gastos_extras = exp_mes["debitos"] - exp_mes["creditos"] if not use_realizado else 0.0
            expectativas_items = exp_mes.get("items", []) if not use_realizado else []

            total_gastos = gastos_usados + gastos_extras
            # Saldo = Renda - Gastos (aporte não entra no saldo; é o que sobra após despesas)
            r = round(renda_usada / 100) * 100
            g = round(total_gastos / 100) * 100
            a = round(aporte_usado / 100) * 100
            saldo = r - g if renda_usada else None

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
                "renda_usada": r,
                "gastos_recorrentes": gastos_recorrentes,
                "gastos_extras_esperados": round(gastos_extras, 2),
                "gastos_realizados": gastos_realizados,
                "gastos_usados": round(gastos_usados, 2),
                "total_gastos": g,
                "aporte_planejado": aporte,
                "investimentos_realizados": round(investimentos_realizados, 2) if investimentos_realizados is not None else None,
                "aporte_usado": a,
                "use_realizado": use_realizado,
                "saldo_projetado": saldo,
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
            # Redução só em meses não realizados — janeiro já foi, não dá pra economizar nele
            if m.get("use_realizado"):
                gastos = gastos_base + extras
            else:
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

    def get_projecao_longa(
        self,
        user_id: int,
        inflacao_pct: float = 4.5,
    ) -> dict:
        """
        Projeção de patrimônio até aposentadoria (até 30 anos).
        Usa user_financial_profile + expectativas tipo credito (aportes extras).
        Retorna série mês a mês: patrimonio_nominal, patrimonio_real.
        """
        profile = self.db.query(UserFinancialProfile).filter(
            UserFinancialProfile.user_id == user_id
        ).first()
        if not profile:
            return {"serie": [], "patrimonio_final_nominal": 0, "patrimonio_final_real": 0}
        patrimonio = float(profile.patrimonio_atual or 0)
        aporte = float(profile.aporte_planejado or 0)
        taxa = float(profile.taxa_retorno_anual or 0.08)
        idade = profile.idade_atual or 35
        idade_apos = profile.idade_aposentadoria or 65
        anos = max(1, idade_apos - idade)
        meses_total = anos * 12
        inflacao = inflacao_pct / 100.0
        taxa_real = (1 + taxa) / (1 + inflacao) - 1 if inflacao < 1 else 0
        rate_nom = (1 + taxa) ** (1 / 12) - 1
        rate_real = (1 + taxa_real) ** (1 / 12) - 1 if taxa_real > -0.99 else 0

        extras = self.db.query(BaseExpectativa).filter(
            BaseExpectativa.user_id == user_id,
            BaseExpectativa.tipo_lancamento == "credito",
            BaseExpectativa.status == "pendente",
        ).all()
        from datetime import date
        hoje = date.today()
        ano_base, mes_base = hoje.year, hoje.month
        extra_map: dict[int, float] = {}
        for e in extras:
            meta = {}
            if e.metadata_json:
                try:
                    meta = json.loads(e.metadata_json)
                except (json.JSONDecodeError, TypeError):
                    pass
            rec = meta.get("recorrencia", "unico")
            meses_exp = self._expandir_meses_recorrencia(e.mes_referencia, rec, meses_total)
            for i, yyyy_mm in enumerate(meses_exp):
                y, m = int(yyyy_mm[:4]), int(yyyy_mm[5:7])
                idx = (y - ano_base) * 12 + (m - mes_base)
                if 0 <= idx < meses_total:
                    extra_map[idx] = extra_map.get(idx, 0) + float(e.valor)

        p_nom, p_real = patrimonio, patrimonio
        serie = []
        for mes_idx in range(meses_total):
            extra = extra_map.get(mes_idx, 0)
            aporte_mes = aporte + extra
            p_nom = (p_nom + aporte_mes) * (1 + rate_nom)
            p_real = (p_real + aporte_mes) * (1 + rate_real)
            ano_m = ano_base + (mes_base - 1 + mes_idx) // 12
            mes_m = (mes_base - 1 + mes_idx) % 12 + 1
            serie.append({
                "mes_num": mes_idx + 1,
                "ano": ano_m,
                "mes": mes_m,
                "patrimonio_nominal": round(p_nom, 2),
                "patrimonio_real": round(p_real, 2),
                "aporte_mes": round(aporte_mes, 2),
            })
        return {
            "patrimonio_inicial": patrimonio,
            "patrimonio_final_nominal": round(p_nom, 2),
            "patrimonio_final_real": round(p_real, 2),
            "meses": meses_total,
            "serie": serie,
        }

    def get_grupos_media_3_meses(self, user_id: int, ano: int, mes: int) -> list:
        """Grupos Despesa com valor_planejado e valor_medio_3_meses para o mês."""
        mes_ref = f"{ano}-{str(mes).zfill(2)}"
        from app.domains.budget.models import BudgetPlanning
        from app.domains.grupos.models import BaseGruposConfig
        rows = (
            self.db.query(BudgetPlanning.grupo, BudgetPlanning.valor_planejado, BudgetPlanning.valor_medio_3_meses)
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
        return [
            {"grupo": r.grupo, "valor_planejado": float(r.valor_planejado or 0), "valor_medio_3_meses": float(r.valor_medio_3_meses or 0)}
            for r in rows
        ]

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

    def _expandir_meses_recorrencia(
        self, mes_referencia: str, recorrencia: str, num_meses: int = 12
    ) -> list[str]:
        """Expande recorrência para lista de YYYY-MM nos próximos num_meses a partir de hoje."""
        ano_inicio, mes_inicio = int(mes_referencia[:4]), int(mes_referencia[5:7])
        hoje = date.today()
        ano_hoje, mes_hoje = hoje.year, hoje.month
        interval = RECORRENCIA_INTERVAL.get(recorrencia or "unico", 0)
        meses_out: list[str] = []
        mes_cal, ano_cal = mes_inicio, ano_inicio
        count = 0
        while count <= num_meses + 12:
            if (ano_cal > ano_hoje) or (ano_cal == ano_hoje and mes_cal >= mes_hoje):
                meses_out.append(f"{ano_cal}-{str(mes_cal).zfill(2)}")
            if interval == 0:
                break
            mes_cal += interval
            while mes_cal > 12:
                mes_cal -= 12
                ano_cal += 1
            count += 1
            if len(meses_out) >= num_meses:
                break
        return meses_out[:num_meses]

    def _materializar_expectativa(self, expectativa: BaseExpectativa, meses: list[str]) -> None:
        """Insere expectativas_mes para os meses dados."""
        for mes_ref in meses:
            em = ExpectativaMes(
                user_id=expectativa.user_id,
                mes_referencia=mes_ref,
                grupo=expectativa.grupo,
                subgrupo=expectativa.subgrupo,
                tipo=expectativa.tipo_lancamento or "debito",
                valor=expectativa.valor,
                origem_expectativa_id=expectativa.id,
            )
            self.db.add(em)
        self.db.flush()

    def create_expectativa(
        self,
        user_id: int,
        descricao: str,
        valor: float,
        mes_referencia: str,
        grupo: Optional[str] = None,
        subgrupo: Optional[str] = None,
        tipo_lancamento: str = "debito",
        tipo_expectativa: str = "sazonal_plano",
        recorrencia: Optional[str] = "unico",
    ) -> dict:
        """Cria expectativa e materializa em expectativas_mes (expande por recorrência)."""
        metadata = {"recorrencia": recorrencia or "unico"}
        e = BaseExpectativa(
            user_id=user_id,
            descricao=descricao,
            valor=valor,
            grupo=grupo,
            subgrupo=subgrupo,
            metadata_json=json.dumps(metadata) if metadata else None,
            tipo_lancamento=tipo_lancamento,
            mes_referencia=mes_referencia,
            tipo_expectativa=tipo_expectativa,
            origem="usuario",
        )
        self.db.add(e)
        self.db.flush()
        meses = self._expandir_meses_recorrencia(mes_referencia, recorrencia or "unico")
        self._materializar_expectativa(e, meses)
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
        """Remove expectativa e linhas em expectativas_mes."""
        e = self.db.query(BaseExpectativa).filter(
            BaseExpectativa.id == expectativa_id,
            BaseExpectativa.user_id == user_id,
        ).first()
        if not e:
            return False
        self.db.query(ExpectativaMes).filter(
            ExpectativaMes.origem_expectativa_id == expectativa_id,
        ).delete(synchronize_session=False)
        self.db.delete(e)
        self.db.commit()
        return True

    def get_expectativas_por_mes(self, user_id: int, ano: int) -> dict:
        """
        Retorna { mes_referencia: { debitos: float, creditos: float, items: [...] } }.
        Lê apenas de expectativas_mes (extraordinários materializados).
        """
        exp_rows = (
            self.db.query(ExpectativaMes, BaseExpectativa.descricao)
            .outerjoin(BaseExpectativa, ExpectativaMes.origem_expectativa_id == BaseExpectativa.id)
            .filter(
                ExpectativaMes.user_id == user_id,
                ExpectativaMes.mes_referencia.like(f"{ano}-%"),
            )
            .all()
        )
        by_mes: dict = {}
        for em, descricao in exp_rows:
            mes = em.mes_referencia
            if mes not in by_mes:
                by_mes[mes] = {"debitos": 0.0, "creditos": 0.0, "items": []}
            v = float(em.valor)
            if em.tipo == "credito":
                by_mes[mes]["creditos"] += v
            else:
                by_mes[mes]["debitos"] += v
            by_mes[mes]["items"].append({
                "id": em.origem_expectativa_id or em.id,
                "descricao": descricao or "(extraordinário)",
                "valor": v,
                "tipo_lancamento": em.tipo,
            })
        return by_mes
