"""Service do domínio Onboarding"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from .schemas import OnboardingProgressResponse
from .demo_seed import DEMO_SEED, GRUPO_FALLBACK
from app.core.redis_client import redis_get, redis_set, redis_delete

logger = logging.getLogger(__name__)

# TTL do cache Redis para onboarding/progress (5 minutos)
# 1ª chamada: ~100ms (5 queries PostgreSQL)
# 2ª+ chamada: <5ms (Redis hit)
ONBOARDING_CACHE_TTL = 5 * 60  # 300 segundos


class OnboardingService:
    def __init__(self, db: Session):
        self.db = db

    def get_progress(self, user_id: int) -> OnboardingProgressResponse:
        """
        Retorna 4 flags de completude do onboarding.
        primeiro_upload: tem upload com sucesso OU tem transações demo

        Cache Redis (TTL=5min):
            HIT  → <5ms (evita 5 queries ao PostgreSQL)
            MISS → ~100ms (5 queries) → salva no Redis
        """
        cache_key = f"onboarding:progress:{user_id}"

        # Tentar cache Redis primeiro
        cached = redis_get(cache_key)
        if cached is not None:
            return OnboardingProgressResponse(**cached)

        from app.domains.upload.history_models import UploadHistory
        from app.domains.budget.models import BudgetPlanning
        from app.domains.investimentos.models import InvestimentoPortfolio
        from app.domains.transactions.models import JournalEntry

        has_upload = (
            self.db.query(UploadHistory)
            .filter(UploadHistory.user_id == user_id, UploadHistory.status == "success")
            .first()
        ) is not None

        has_demo = (
            self.db.query(func.count(JournalEntry.id))
            .filter(JournalEntry.user_id == user_id, JournalEntry.fonte == "demo")
            .scalar()
        ) or 0
        tem_demo = has_demo > 0
        primeiro_upload = has_upload or tem_demo

        has_plano = (
            self.db.query(BudgetPlanning).filter(BudgetPlanning.user_id == user_id).first()
        ) is not None

        has_invest = (
            self.db.query(InvestimentoPortfolio)
            .filter(InvestimentoPortfolio.user_id == user_id)
            .first()
        ) is not None

        onboarding_completo = primeiro_upload and has_plano and has_invest

        ultimo_upload = (
            self.db.query(func.max(UploadHistory.data_upload))
            .filter(UploadHistory.user_id == user_id, UploadHistory.status == "success")
            .scalar()
        )
        ultimo_upload_str = ultimo_upload.isoformat() if ultimo_upload else None

        result = OnboardingProgressResponse(
            conta_criada=True,
            primeiro_upload=primeiro_upload,
            plano_criado=has_plano,
            investimento_adicionado=has_invest,
            onboarding_completo=onboarding_completo,
            tem_demo=tem_demo,
            ultimo_upload_em=ultimo_upload_str,
        )

        # Salvar no cache Redis (TTL = 5 min)
        redis_set(cache_key, result.model_dump(), ex=ONBOARDING_CACHE_TTL)

        return result

    def criar_dados_demo(self, user_id: int) -> int:
        """
        Insere seed de transações demo para o usuário.
        Usa ano atual e meses 1, 2, 3 (ou últimos 3 meses).
        Retorna quantidade de transações criadas.
        """
        from app.domains.transactions.models import JournalEntry
        from app.domains.grupos.models import BaseGruposConfig
        from app.shared.utils.hasher import generate_id_transacao

        # Mapear grupo -> (tipo_gasto, categoria_geral) do usuário
        grupos_rows = (
            self.db.query(BaseGruposConfig.nome_grupo, BaseGruposConfig.tipo_gasto_padrao, BaseGruposConfig.categoria_geral)
            .filter(BaseGruposConfig.user_id == user_id)
            .all()
        )
        grupo_config = {r.nome_grupo: (r.tipo_gasto_padrao, r.categoria_geral) for r in grupos_rows}
        for g, (t, c) in GRUPO_FALLBACK.items():
            if g not in grupo_config:
                grupo_config[g] = (t, c)

        ano = datetime.now().year
        criadas = 0
        seq_por_chave = {}

        for estab, valor, grupo, subgrupo, mes in DEMO_SEED:
            tipo_gasto, categoria_geral = grupo_config.get(grupo, ("Ajustável", "Despesa"))
            valor_pos = abs(valor)
            tipo_tx = "CREDITO" if valor >= 0 else "DEBITO"
            dia = 5 + (criadas % 20)
            data_str = f"{dia:02d}/{mes:02d}/{ano}"
            mes_fatura = f"{ano}{mes:02d}"

            chave = (data_str, estab, valor)
            seq_por_chave[chave] = seq_por_chave.get(chave, 0) + 1
            seq = seq_por_chave[chave]
            id_tx = generate_id_transacao(data_str, estab, valor, user_id, sequencia=seq)

            entry = JournalEntry(
                user_id=user_id,
                Data=data_str,
                Estabelecimento=estab,
                Valor=valor,
                ValorPositivo=valor_pos,
                TipoTransacao=tipo_tx,
                TipoGasto=tipo_gasto,
                GRUPO=grupo,
                SUBGRUPO=subgrupo,
                CategoriaGeral=categoria_geral,
                IdTransacao=id_tx,
                MesFatura=mes_fatura,
                Ano=ano,
                Mes=mes,
                fonte="demo",
                is_demo=1,
                IgnorarDashboard=0,
                created_at=datetime.now(),
            )
            self.db.add(entry)
            criadas += 1

        self.db.commit()
        logger.info("Modo demo: %d transações criadas para user_id=%s", criadas, user_id)
        return criadas

    def limpar_dados_demo(self, user_id: int) -> int:
        """Remove todas as transações demo do usuário. Retorna quantidade removida."""
        from app.domains.transactions.models import JournalEntry

        result = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.fonte == "demo",
        ).delete()
        self.db.commit()
        logger.info("Modo demo: %d transações removidas para user_id=%s", result, user_id)
        return result
