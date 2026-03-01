"""Router do domínio Plano"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id

from .service import PlanoService
from .schemas import RendaUpdate, MetaCreate, PerfilUpdate, ExpectativaCreate

router = APIRouter(prefix="/plano", tags=["plano"])


@router.post("/renda")
def atualizar_renda(
    data: RendaUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Upsert renda mensal líquida no perfil financeiro"""
    service = PlanoService(db)
    return service.upsert_renda(user_id, data.renda_mensal_liquida)


@router.get("/renda")
def obter_renda(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retorna renda declarada ou null"""
    service = PlanoService(db)
    renda = service.get_renda(user_id)
    return {"renda": renda}


@router.get("/resumo")
def resumo_plano(
    ano: int = Query(...),
    mes: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """A.07: Retorna renda, total_budget, disponivel_real (renda - total budget)"""
    service = PlanoService(db)
    return service.get_resumo(user_id, ano, mes)


@router.get("/impacto-longo-prazo")
def impacto_longo_prazo(
    ano: int = Query(...),
    mes: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Anos perdidos quando gasto/plano > renda. Retorna null quando sem déficit."""
    service = PlanoService(db)
    result = service.get_impacto_longo_prazo(user_id, ano, mes)
    return result if result else {}


@router.get("/orcamento")
def orcamento_por_categoria(
    ano: int = Query(...),
    mes: int = Query(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retorna gasto real vs meta por grupo para o mês"""
    service = PlanoService(db)
    return service.get_orcamento(user_id, ano, mes)


@router.post("/metas/{grupo}")
def salvar_meta(
    grupo: str,
    data: MetaCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Salva meta de gasto para um grupo no mês"""
    service = PlanoService(db)
    return service.salvar_meta(user_id, grupo, data.valor_meta, data.ano, data.mes)


@router.get("/perfil")
def obter_perfil(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Retorna perfil financeiro completo (renda, aporte, idade, etc.)"""
    from .models import UserFinancialProfile
    profile = db.query(UserFinancialProfile).filter(UserFinancialProfile.user_id == user_id).first()
    if not profile:
        return {
            "renda_mensal_liquida": None,
            "aporte_planejado": None,
            "idade_atual": None,
            "idade_aposentadoria": None,
            "patrimonio_atual": None,
            "taxa_retorno_anual": None,
        }
    return {
        "renda_mensal_liquida": profile.renda_mensal_liquida,
        "aporte_planejado": profile.aporte_planejado,
        "idade_atual": profile.idade_atual,
        "idade_aposentadoria": profile.idade_aposentadoria,
        "patrimonio_atual": profile.patrimonio_atual,
        "taxa_retorno_anual": profile.taxa_retorno_anual,
    }


@router.put("/perfil")
def atualizar_perfil(
    data: PerfilUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Atualiza perfil financeiro: renda, idade, aposentadoria, patrimônio, taxa"""
    service = PlanoService(db)
    return service.update_perfil(
        user_id,
        renda=data.renda_mensal_liquida,
        aporte_planejado=data.aporte_planejado,
        idade_atual=data.idade_atual,
        idade_aposentadoria=data.idade_aposentadoria,
        patrimonio_atual=data.patrimonio_atual,
        taxa_retorno_anual=data.taxa_retorno_anual,
    )


@router.get("/cashflow/detalhe-mes")
def cashflow_detalhe_mes(
    ano: int = Query(..., ge=2020, le=2100),
    mes: int = Query(..., ge=1, le=12),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Diagnóstico: cálculo exato dos gastos do mês com dados brutos."""
    from app.domains.budget.models import BudgetPlanning
    from app.domains.transactions.models import JournalEntry
    from sqlalchemy import func, text

    mes_ref = f"{ano}-{str(mes).zfill(2)}"
    mes_fatura = f"{ano}{str(mes).zfill(2)}"

    # Transações que entram em gastos: apenas Despesa (Investimentos = aporte)
    transacoes = db.query(
        JournalEntry.id,
        JournalEntry.Estabelecimento,
        JournalEntry.Valor,
        JournalEntry.GRUPO,
        JournalEntry.SUBGRUPO,
        JournalEntry.CategoriaGeral,
        JournalEntry.MesFatura,
        JournalEntry.Data,
    ).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.MesFatura == mes_fatura,
        JournalEntry.CategoriaGeral == "Despesa",
        JournalEntry.IgnorarDashboard == 0,
    ).order_by(JournalEntry.id).all()

    # Cálculo: SUM(ABS(Valor)) por transação
    itens = []
    for t in transacoes:
        valor_abs = abs(float(t.Valor)) if t.Valor is not None else 0
        itens.append({
            "id": t.id,
            "estabelecimento": t.Estabelecimento,
            "valor_original": float(t.Valor) if t.Valor is not None else None,
            "valor_abs_usado": round(valor_abs, 2),
            "grupo": t.GRUPO or "(sem grupo)",
            "subgrupo": t.SUBGRUPO or "",
            "categoria_geral": t.CategoriaGeral or "",
            "mes_fatura": t.MesFatura,
            "data": t.Data,
        })

    total_realizado = sum(x["valor_abs_usado"] for x in itens)

    # Agrupado por grupo
    por_grupo = {}
    for x in itens:
        g = x["grupo"]
        por_grupo[g] = por_grupo.get(g, 0) + x["valor_abs_usado"]
    por_grupo_lista = [{"grupo": k, "total": round(v, 2)} for k, v in sorted(por_grupo.items())]

    # Budget (planejado) - apenas grupos Despesa (CategoriaGeral)
    from app.domains.grupos.models import BaseGruposConfig
    planejados = (
        db.query(BudgetPlanning.grupo, func.sum(BudgetPlanning.valor_planejado))
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
        .group_by(BudgetPlanning.grupo)
        .all()
    )
    total_planejado = sum(float(p[1] or 0) for p in planejados)

    # Fonte usada no cashflow
    gastos_efetivos = total_realizado if total_realizado > 0 else total_planejado
    fonte = "realizado" if total_realizado > 0 else "planejado"

    return {
        "mes_referencia": mes_ref,
        "mes_fatura_filtro": mes_fatura,
        "formula": "gastos = SUM(ABS(Valor)) WHERE user_id=X AND MesFatura=YYYYMM AND CategoriaGeral='Despesa' AND IgnorarDashboard=0",
        "fonte_usada": fonte,
        "total_realizado": round(total_realizado, 2),
        "total_planejado": round(total_planejado, 2),
        "valor_exibido_no_cashflow": round(gastos_efetivos, 2),
        "qtd_transacoes": len(itens),
        "transacoes": itens,
        "soma_por_grupo": por_grupo_lista,
        "planejado_por_grupo": [{"grupo": p[0], "total": round(float(p[1] or 0), 2)} for p in planejados],
    }


@router.get("/cashflow")
def cashflow_anual(
    ano: int = Query(..., ge=2020, le=2100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """12 meses: renda_esperada, gastos_recorrentes, gastos_realizados, aporte, saldo, status"""
    service = PlanoService(db)
    return service.get_cashflow(user_id, ano)


@router.get("/expectativas")
def listar_expectativas(
    mes: Optional[str] = Query(None, description="YYYY-MM para filtrar por mês"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Lista expectativas (sazonais, parcelas). Opcional: ?mes=YYYY-MM"""
    service = PlanoService(db)
    return service.list_expectativas(user_id, mes)


@router.post("/expectativas", status_code=201)
def criar_expectativa(
    data: ExpectativaCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Cria expectativa (sazonal ou renda extra)"""
    service = PlanoService(db)
    return service.create_expectativa(
        user_id,
        descricao=data.descricao,
        valor=data.valor,
        mes_referencia=data.mes_referencia,
        grupo=data.grupo,
        subgrupo=data.subgrupo,
        tipo_lancamento=data.tipo_lancamento,
        tipo_expectativa=data.tipo_expectativa,
        recorrencia=data.recorrencia,
    )


@router.delete("/expectativas/{expectativa_id}", status_code=204)
def deletar_expectativa(
    expectativa_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Remove expectativa"""
    service = PlanoService(db)
    service.delete_expectativa(user_id, expectativa_id)


@router.get("/projecao")
def projecao_poupanca(
    ano: int = Query(None, ge=2020, le=2100),
    meses: int = Query(12, ge=1, le=60),
    reducao_pct: float = Query(0, ge=0, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Poupança acumulada mês a mês. reducao_pct = % de redução nos gastos."""
    ano = ano or date.today().year
    service = PlanoService(db)
    return service.get_projecao(user_id, ano, meses, reducao_pct)
