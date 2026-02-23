"""
Domínio Transactions - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from .models import JournalEntry
from .schemas import TransactionFilters

class TransactionRepository:
    """
    Repository pattern para transações
    Isola TODAS as queries SQL do resto do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, transaction_id: str, user_id: int) -> Optional[JournalEntry]:
        """Busca transação por ID"""
        return self.db.query(JournalEntry).filter(
            JournalEntry.IdTransacao == transaction_id,
            JournalEntry.user_id == user_id
        ).first()
    
    def list_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[JournalEntry]:
        """Lista todas as transações do usuário"""
        return self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def list_with_filters(
        self,
        user_id: int,
        filters: TransactionFilters,
        skip: int = 0,
        limit: int = 100
    ) -> List[JournalEntry]:
        """Lista transações com filtros. Ordenação: mais recentes primeiro."""
        query = self.db.query(JournalEntry).filter(JournalEntry.user_id == user_id)
        
        # Sprint F: período customizado (year_inicio/month_inicio até year_fim/month_fim)
        if filters.year_inicio is not None and filters.month_inicio is not None and filters.year_fim is not None and filters.month_fim is not None:
            mes_ini = f"{filters.year_inicio}{filters.month_inicio:02d}"
            mes_fim = f"{filters.year_fim}{filters.month_fim:02d}"
            query = query.filter(
                JournalEntry.MesFatura >= mes_ini,
                JournalEntry.MesFatura <= mes_fim
            )
        elif filters.year and filters.month:
            # Mês específico: usa MesFatura exato
            mes_fatura = f"{filters.year}{filters.month:02d}"
            query = query.filter(JournalEntry.MesFatura == mes_fatura)
        elif filters.year:
            # Ano inteiro: filtra MesFatura começando com o ano
            query = query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        
        if filters.estabelecimento:
            query = query.filter(
                JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%")
            )
        
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        
        if getattr(filters, 'subgrupo_null', None):
            query = query.filter(
                or_(JournalEntry.SUBGRUPO.is_(None), JournalEntry.SUBGRUPO == '')
            )
        elif filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        
        if filters.tipo:
            query = query.filter(JournalEntry.TipoTransacao == filters.tipo)
        
        if filters.categoria_geral:
            query = query.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        
        if filters.tipo_gasto:
            if isinstance(filters.tipo_gasto, list):
                query = query.filter(JournalEntry.TipoGasto.in_(filters.tipo_gasto))
            else:
                query = query.filter(JournalEntry.TipoGasto == filters.tipo_gasto)
        
        if filters.cartao:
            query = query.filter(JournalEntry.NomeCartao == filters.cartao)
        
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.Data.ilike(f"%{filters.search}%")
                )
            )
        
        # Sprint F: ordenação mais recentes primeiro (MesFatura DESC, id DESC)
        query = query.order_by(JournalEntry.MesFatura.desc(), JournalEntry.id.desc())
        return query.offset(skip).limit(limit).all()
    
    def count_with_filters(self, user_id: int, filters: TransactionFilters) -> int:
        """Conta transações com filtros"""
        query = self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.user_id == user_id
        )
        
        # Aplicar mesmos filtros (incl. período customizado Sprint F)
        if filters.year_inicio is not None and filters.month_inicio is not None and filters.year_fim is not None and filters.month_fim is not None:
            mes_ini = f"{filters.year_inicio}{filters.month_inicio:02d}"
            mes_fim = f"{filters.year_fim}{filters.month_fim:02d}"
            query = query.filter(
                JournalEntry.MesFatura >= mes_ini,
                JournalEntry.MesFatura <= mes_fim
            )
        elif filters.year and filters.month:
            mes_fatura = f"{filters.year}{filters.month:02d}"
            query = query.filter(JournalEntry.MesFatura == mes_fatura)
        elif filters.year:
            query = query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        if filters.estabelecimento:
            query = query.filter(
                JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%")
            )
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        if getattr(filters, 'subgrupo_null', None):
            query = query.filter(
                or_(JournalEntry.SUBGRUPO.is_(None), JournalEntry.SUBGRUPO == '')
            )
        elif filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        if filters.tipo:
            query = query.filter(JournalEntry.TipoTransacao == filters.tipo)
        if filters.categoria_geral:
            query = query.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        if filters.tipo_gasto:
            if isinstance(filters.tipo_gasto, list):
                query = query.filter(JournalEntry.TipoGasto.in_(filters.tipo_gasto))
            else:
                query = query.filter(JournalEntry.TipoGasto == filters.tipo_gasto)
        if filters.cartao:
            query = query.filter(JournalEntry.NomeCartao == filters.cartao)
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.Data.ilike(f"%{filters.search}%")
                )
            )
        
        return query.scalar()
    
    def create(self, transaction: JournalEntry) -> JournalEntry:
        """Cria nova transação"""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def update(self, transaction: JournalEntry) -> JournalEntry:
        """Atualiza transação existente"""
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def delete(self, transaction: JournalEntry) -> None:
        """Deleta transação"""
        self.db.delete(transaction)
        self.db.commit()
    
    def get_total_by_filters(self, user_id: int, filters: TransactionFilters) -> float:
        """Soma total de valores com filtros"""
        query = self.db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.user_id == user_id
        )
        
        # Aplicar filtros (incl. período customizado Sprint F)
        if filters.year_inicio is not None and filters.month_inicio is not None and filters.year_fim is not None and filters.month_fim is not None:
            mes_ini = f"{filters.year_inicio}{filters.month_inicio:02d}"
            mes_fim = f"{filters.year_fim}{filters.month_fim:02d}"
            query = query.filter(
                JournalEntry.MesFatura >= mes_ini,
                JournalEntry.MesFatura <= mes_fim
            )
        elif filters.year and filters.month:
            mes_fatura = f"{filters.year}{filters.month:02d}"
            query = query.filter(JournalEntry.MesFatura == mes_fatura)
        elif filters.year:
            query = query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        if filters.tipo:
            query = query.filter(JournalEntry.TipoTransacao == filters.tipo)
        if filters.categoria_geral:
            query = query.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        if filters.tipo_gasto:
            if isinstance(filters.tipo_gasto, list):
                query = query.filter(JournalEntry.TipoGasto.in_(filters.tipo_gasto))
            else:
                query = query.filter(JournalEntry.TipoGasto == filters.tipo_gasto)
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        if getattr(filters, 'subgrupo_null', None):
            query = query.filter(
                or_(JournalEntry.SUBGRUPO.is_(None), JournalEntry.SUBGRUPO == '')
            )
        elif filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        if filters.estabelecimento:
            query = query.filter(JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%"))
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.Data.ilike(f"%{filters.search}%")
                )
            )
        if filters.cartao:
            query = query.filter(JournalEntry.NomeCartao == filters.cartao)
        
        result = query.scalar()
        return result or 0.0
    
    def get_resumo(self, user_id: int, filters: TransactionFilters) -> dict:
        """Sprint F: Resumo (total, quantidade, maior_gasto, media_por_dia) com filtros."""
        total = self.get_total_by_filters(user_id, filters)
        qtd = self.count_with_filters(user_id, filters)
        
        # Maior gasto (maior abs(Valor) entre despesas)
        q_max = self.db.query(func.max(func.abs(JournalEntry.Valor))).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.Valor < 0
        )
        q_max = self._apply_period_filters(q_max, filters)
        if filters.estabelecimento:
            q_max = q_max.filter(JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%"))
        if filters.grupo:
            q_max = q_max.filter(JournalEntry.GRUPO == filters.grupo)
        if getattr(filters, 'subgrupo_null', None):
            q_max = q_max.filter(or_(JournalEntry.SUBGRUPO.is_(None), JournalEntry.SUBGRUPO == ''))
        elif filters.subgrupo:
            q_max = q_max.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        if filters.categoria_geral:
            q_max = q_max.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        if filters.search:
            q_max = q_max.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.Data.ilike(f"%{filters.search}%")
                )
            )
        maior_gasto = q_max.scalar() or 0
        
        # Dias no período (approx)
        dias = self._get_dias_periodo(filters)
        media_por_dia = abs(total) / dias if dias > 0 else 0
        
        return {
            "total": total,
            "quantidade": qtd,
            "maior_gasto": float(maior_gasto),
            "media_por_dia": round(media_por_dia, 2)
        }
    
    def _apply_period_filters(self, query, filters: TransactionFilters):
        """Aplica filtros de período na query."""
        if filters.year_inicio is not None and filters.month_inicio is not None and filters.year_fim is not None and filters.month_fim is not None:
            mes_ini = f"{filters.year_inicio}{filters.month_inicio:02d}"
            mes_fim = f"{filters.year_fim}{filters.month_fim:02d}"
            return query.filter(
                JournalEntry.MesFatura >= mes_ini,
                JournalEntry.MesFatura <= mes_fim
            )
        if filters.year and filters.month:
            mes_fatura = f"{filters.year}{filters.month:02d}"
            return query.filter(JournalEntry.MesFatura == mes_fatura)
        if filters.year:
            return query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        return query
    
    def _get_dias_periodo(self, filters: TransactionFilters) -> int:
        """Retorna número de dias no período (approx)."""
        if filters.year_inicio is not None and filters.month_inicio is not None and filters.year_fim is not None and filters.month_fim is not None:
            from datetime import datetime
            d1 = datetime(filters.year_inicio, filters.month_inicio, 1)
            d2 = datetime(filters.year_fim, filters.month_fim, 1)
            delta = (d2 - d1).days + 30  # +30 para incluir mês fim
            return max(1, delta)
        if filters.year and filters.month:
            return 30
        if filters.year:
            return 365
        return 365  # default ano inteiro
    
    def get_gastos_por_grupo(self, user_id: int, filters: TransactionFilters) -> list:
        """Sprint F: Agregação por GRUPO (Despesa) com filtros."""
        query = self.db.query(
            JournalEntry.GRUPO,
            func.sum(func.abs(JournalEntry.Valor)).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.CategoriaGeral == 'Despesa',
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.GRUPO != ''
        )
        query = self._apply_period_filters(query, filters)
        if filters.estabelecimento:
            query = query.filter(JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%"))
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        if getattr(filters, 'subgrupo_null', None):
            query = query.filter(or_(JournalEntry.SUBGRUPO.is_(None), JournalEntry.SUBGRUPO == ''))
        elif filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.Data.ilike(f"%{filters.search}%")
                )
            )
        rows = query.group_by(JournalEntry.GRUPO).order_by(func.sum(func.abs(JournalEntry.Valor)).desc()).all()
        return [{"grupo": r.GRUPO, "total": float(r.total)} for r in rows]

    def get_gastos_por_subgrupo(self, user_id: int, filters: TransactionFilters) -> list:
        """Agregação por SUBGRUPO de um grupo específico (Despesa) com filtros."""
        query = self.db.query(
            JournalEntry.SUBGRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.CategoriaGeral == 'Despesa',
        )
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        query = self._apply_period_filters(query, filters)
        if filters.estabelecimento:
            query = query.filter(JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%"))
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%"),
                )
            )
        rows = (
            query
            .group_by(JournalEntry.SUBGRUPO)
            .order_by(func.abs(func.sum(JournalEntry.Valor)).desc())
            .all()
        )
        return [{"grupo": r.SUBGRUPO or 'Sem subgrupo', "total": float(r.total)} for r in rows]
