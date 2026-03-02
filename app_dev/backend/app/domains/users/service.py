"""
Domínio Users - Service
Lógica de negócio isolada
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime

from .repository import UserRepository
from .models import User
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserStatsResponse,
    SystemStatsResponse,
    ProfileUpdate,
    PasswordChange,
)
from ..auth.password_utils import hash_password, verify_password  # bcrypt

logger = logging.getLogger(__name__)

class UserService:
    """
    Service layer para usuários
    Contém TODA a lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def get_user(self, user_id: int) -> UserResponse:
        """
        Busca um usuário por ID
        
        Raises:
            HTTPException: Se usuário não encontrado
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        return UserResponse.from_orm(user)
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Busca um usuário por email
        
        Returns:
            UserResponse ou None se não encontrado
        """
        user = self.repository.get_by_email(email)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def list_users(self, apenas_ativos: bool = True) -> UserListResponse:
        """
        Lista todos os usuários
        """
        users = self.repository.list_all(apenas_ativos)
        total = self.repository.count_all(apenas_ativos)
        
        return UserListResponse(
            users=[UserResponse.from_orm(u) for u in users],
            total=total
        )
    
    def _inicializar_grupos_usuario(self, user_id: int) -> None:
        """
        Copia do template (base_grupos_template, base_marcacoes_template) para o novo usuário.
        Idempotente — não duplica se já inicializado.
        """
        from app.domains.grupos.models import BaseGruposConfig, BaseGruposTemplate
        from app.domains.categories.models import BaseMarcacao, BaseMarcacaoTemplate

        db = self.repository.db
        if db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user_id).count() > 0:
            return

        for t in db.query(BaseGruposTemplate).all():
            db.add(
                BaseGruposConfig(
                    user_id=user_id,
                    nome_grupo=t.nome_grupo,
                    tipo_gasto_padrao=t.tipo_gasto_padrao,
                    categoria_geral=t.categoria_geral,
                    cor=t.cor,
                    is_padrao=True,
                )
            )
        db.flush()

        for t in db.query(BaseMarcacaoTemplate).all():
            db.add(BaseMarcacao(user_id=user_id, GRUPO=t.GRUPO, SUBGRUPO=t.SUBGRUPO))
        db.flush()

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Cria novo usuário e inicializa grupos/marcações do template.
        
        Lógica de negócio:
        - Verifica se email já existe
        - Hash da senha
        - Define timestamps
        - Copia grupos e marcações do template para o novo usuário
        
        Raises:
            HTTPException: Se email já existe
        """
        # Verificar se email já existe
        if self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' já está cadastrado"
            )
        
        # Criar modelo
        now = datetime.now()
        user = User(
            email=user_data.email,
            nome=user_data.nome,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            ativo=1,
            created_at=now,
            updated_at=now
        )
        
        # Salvar (add + flush para obter ID) e inicializar grupos antes do commit
        db = self.repository.db
        db.add(user)
        db.flush()
        self._inicializar_grupos_usuario(user.id)
        db.commit()
        db.refresh(user)
        return UserResponse.from_orm(user)
    
    def update_user(
        self,
        user_id: int,
        update_data: UserUpdate
    ) -> UserResponse:
        """
        Atualiza usuário
        
        Raises:
            HTTPException: Se usuário não encontrado ou email duplicado
        """
        # Buscar usuário
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        
        # Verificar email duplicado
        if update_data.email and update_data.email != user.email:
            if self.repository.email_exists(update_data.email, user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{update_data.email}' já está cadastrado"
                )
        
        # Aplicar mudanças (apenas campos não-None)
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "password":
                user.password_hash = hash_password(value)
            else:
                setattr(user, field, value)
        
        user.updated_at = datetime.now()
        
        # Salvar
        updated = self.repository.update(user)
        return UserResponse.from_orm(updated)
    
    def get_stats(self, user_id: int) -> UserStatsResponse:
        """
        Retorna estatísticas do usuário (transações, uploads, grupos, plano, investimentos).
        base_grupos_config é por user_id — total_grupos retorna count do usuário.
        """
        from app.domains.transactions.models import JournalEntry
        from app.domains.upload.history_models import UploadHistory
        from app.domains.grupos.models import BaseGruposConfig
        from app.domains.budget.models import BudgetPlanning
        from app.domains.investimentos.models import InvestimentoPortfolio

        db = self.repository.db

        total_tx = db.query(func.count(JournalEntry.id)).filter(JournalEntry.user_id == user_id).scalar() or 0
        total_uploads = db.query(func.count(UploadHistory.id)).filter(UploadHistory.user_id == user_id).scalar() or 0
        ultimo_upload = (
            db.query(func.max(UploadHistory.data_upload))
            .filter(UploadHistory.user_id == user_id)
            .scalar()
        )
        total_grupos = db.query(func.count(BaseGruposConfig.id)).filter(BaseGruposConfig.user_id == user_id).scalar() or 0
        tem_plano = db.query(BudgetPlanning).filter(BudgetPlanning.user_id == user_id).first() is not None
        tem_invest = db.query(InvestimentoPortfolio).filter(InvestimentoPortfolio.user_id == user_id).first() is not None

        return UserStatsResponse(
            total_transacoes=total_tx,
            total_uploads=total_uploads,
            ultimo_upload_em=ultimo_upload,
            total_grupos=total_grupos,
            tem_plano=tem_plano,
            tem_investimentos=tem_invest,
        )

    def get_system_stats(self):
        """Estatísticas gerais do sistema (admin)."""
        from app.domains.transactions.models import JournalEntry
        from app.domains.upload.history_models import UploadHistory
        from app.domains.budget.models import BudgetPlanning

        db = self.repository.db

        total_usuarios = db.query(func.count(User.id)).scalar() or 0
        total_ativos = db.query(func.count(User.id)).filter(User.ativo == 1).scalar() or 0
        total_uploads = db.query(func.count(UploadHistory.id)).scalar() or 0
        total_transacoes = db.query(func.count(JournalEntry.id)).scalar() or 0
        total_planos = db.query(func.count(BudgetPlanning.id)).scalar() or 0

        return SystemStatsResponse(
            total_usuarios=total_usuarios,
            total_usuarios_ativos=total_ativos,
            total_uploads=total_uploads,
            total_transacoes=total_transacoes,
            total_planos=total_planos,
        )

    def reativar(self, user_id: int) -> dict:
        """Reativa usuário (seta ativo=1)."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )
        user.ativo = 1
        user.updated_at = datetime.now()
        self.repository.update(user)
        return {"message": "Usuário reativado"}

    def purge_user(self, user_id: int, executado_por: int) -> dict:
        """
        Remove permanentemente todos os dados do usuário.
        user_id=1 é protegido (não deve ser chamado com 1).
        Ordem de deleção respeita FKs.
        """
        if user_id == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin principal não pode ser purgado",
            )

        from app.domains.investimentos.models import (
            InvestimentoTransacao,
            InvestimentoPortfolio,
            InvestimentoCenario,
            InvestimentoPlanejamento,
        )
        from app.domains.budget.models import BudgetPlanning
        from app.domains.transactions.models import JournalEntry, BaseParcelas
        from app.domains.upload.history_models import UploadHistory
        from app.domains.upload.models import PreviewTransacao
        from app.domains.exclusoes.models import TransacaoExclusao
        from app.domains.patterns.models import BasePadroes
        from app.domains.cards.models import Cartao
        from app.domains.grupos.models import BaseGruposConfig
        from app.domains.categories.models import BaseMarcacao

        db = self.repository.db

        db.query(InvestimentoTransacao).filter(InvestimentoTransacao.user_id == user_id).delete()
        db.query(InvestimentoPortfolio).filter(InvestimentoPortfolio.user_id == user_id).delete()
        db.query(InvestimentoCenario).filter(InvestimentoCenario.user_id == user_id).delete()
        db.query(InvestimentoPlanejamento).filter(InvestimentoPlanejamento.user_id == user_id).delete()
        db.query(BudgetPlanning).filter(BudgetPlanning.user_id == user_id).delete()
        db.query(JournalEntry).filter(JournalEntry.user_id == user_id).delete()
        db.query(UploadHistory).filter(UploadHistory.user_id == user_id).delete()
        db.query(TransacaoExclusao).filter(TransacaoExclusao.user_id == user_id).delete()
        db.query(PreviewTransacao).filter(PreviewTransacao.user_id == user_id).delete()
        db.query(BaseParcelas).filter(BaseParcelas.user_id == user_id).delete()
        db.query(BasePadroes).filter(BasePadroes.user_id == user_id).delete()
        db.query(Cartao).filter(Cartao.user_id == user_id).delete()
        db.query(BaseMarcacao).filter(BaseMarcacao.user_id == user_id).delete()
        db.query(BaseGruposConfig).filter(BaseGruposConfig.user_id == user_id).delete()
        db.query(User).filter(User.id == user_id).delete()
        db.commit()

        logger.warning("PURGE user_id=%s por admin_id=%s", user_id, executado_por)
        return {"message": f"Usuário {user_id} removido permanentemente"}

    def delete_user(self, user_id: int) -> dict:
        """
        Desativa usuário (soft delete)
        
        Raises:
            HTTPException: Se usuário não encontrado ou é admin principal
        """
        if user_id == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é possível desativar o usuário administrador principal"
            )
        
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        
        user.updated_at = datetime.now()
        self.repository.soft_delete(user)
        return {"message": "Usuário desativado com sucesso"}
    
    def reset_password(self, user_id: int, nova_senha: str) -> dict:
        """
        Reseta a senha de um usuário
        
        Raises:
            HTTPException: Se usuário não encontrado
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        
        user.password_hash = hash_password(nova_senha)
        user.updated_at = datetime.now()
        
        self.repository.update(user)
        return {"message": "Senha alterada com sucesso"}
    
    def update_profile(
        self,
        user_id: int,
        profile_data: ProfileUpdate
    ) -> UserResponse:
        """
        Atualiza perfil do usuário autenticado
        
        Lógica de negócio:
        - Usuário só pode alterar seu próprio perfil
        - Valida se email não está em uso por outro usuário
        
        Raises:
            HTTPException: Se usuário não encontrado ou email duplicado
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se email já está em uso por outro usuário
        if profile_data.email != user.email:
            if self.repository.email_exists(profile_data.email, user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{profile_data.email}' já está cadastrado"
                )
        
        # Atualizar campos
        user.nome = profile_data.nome
        user.email = profile_data.email
        user.updated_at = datetime.now()
        
        updated = self.repository.update(user)
        return UserResponse.from_orm(updated)
    
    def change_password(
        self,
        user_id: int,
        password_data: PasswordChange
    ) -> dict:
        """
        Altera a senha do usuário autenticado
        
        Lógica de negócio:
        - Verifica se senha atual está correta
        - Hash da nova senha
        - Atualiza timestamp
        
        Raises:
            HTTPException: Se usuário não encontrado ou senha atual incorreta
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar senha atual
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Atualizar senha
        user.password_hash = hash_password(password_data.new_password)
        user.updated_at = datetime.now()
        
        self.repository.update(user)
        return {"message": "Senha alterada com sucesso"}

