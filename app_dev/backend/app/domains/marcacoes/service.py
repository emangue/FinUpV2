"""
Domínio Marcações - Service
Lógica de negócio para marcações (grupos e subgrupos)
"""
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from .repository import MarcacaoRepository
from .schemas import (
    MarcacaoCreate,
    MarcacaoResponse,
    MarcacaoListResponse,
    SubgrupoCreate,
    SubgrupoResponse,
    GrupoComSubgrupos
)
from app.domains.grupos.repository import GrupoRepository


class MarcacaoService:
    def __init__(self, db: Session):
        self.repository = MarcacaoRepository(db)
        self.grupo_repository = GrupoRepository(db)
    
    def list_marcacoes(self) -> MarcacaoListResponse:
        """Lista todas as marcações (grupo + subgrupo)"""
        marcacoes = self.repository.get_all()
        return MarcacaoListResponse(
            marcacoes=[MarcacaoResponse.from_db_model(m) for m in marcacoes],
            total=len(marcacoes)
        )
    
    def get_marcacoes_by_grupo(self, grupo: str) -> List[MarcacaoResponse]:
        """Lista marcações de um grupo específico"""
        marcacoes = self.repository.get_by_grupo(grupo)
        return [MarcacaoResponse.from_db_model(m) for m in marcacoes]
    
    def get_grupos_com_subgrupos(self) -> List[GrupoComSubgrupos]:
        """Retorna grupos com seus subgrupos"""
        grupos = self.repository.get_grupos_unicos()
        result = []
        
        for grupo in grupos:
            subgrupos = self.repository.get_subgrupos_by_grupo(grupo)
            result.append(GrupoComSubgrupos(
                grupo=grupo,
                subgrupos=subgrupos,
                total_subgrupos=len(subgrupos)
            ))
        
        return result
    
    def create_subgrupo(self, grupo: str, subgrupo_data: SubgrupoCreate) -> SubgrupoResponse:
        """
        Cria novo subgrupo para um grupo existente.
        Herda configuração (tipo_gasto, categoria) de base_grupos_config.
        """
        # 1. Verificar se grupo existe em base_grupos_config
        grupo_config = self.repository.get_grupo_config(grupo)
        if not grupo_config:
            raise HTTPException(
                status_code=404,
                detail=f"Grupo '{grupo}' não encontrado em base_grupos_config. Crie o grupo primeiro."
            )
        
        # 2. Verificar se subgrupo já existe
        existing = self.repository.get_by_grupo_subgrupo(grupo, subgrupo_data.subgrupo)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Subgrupo '{subgrupo_data.subgrupo}' já existe no grupo '{grupo}'"
            )
        
        # 3. Criar marcação em base_marcacoes (apenas GRUPO + SUBGRUPO)
        marcacao = self.repository.create_marcacao(
            grupo=grupo,
            subgrupo=subgrupo_data.subgrupo
        )
        
        # 4. Retornar resposta com config do grupo
        return SubgrupoResponse(
            id=marcacao.id,
            grupo=marcacao.GRUPO,
            subgrupo=marcacao.SUBGRUPO,
            tipo_gasto=grupo_config.tipo_gasto_padrao,
            categoria_geral=grupo_config.categoria_geral,
            message=f"Subgrupo '{subgrupo_data.subgrupo}' criado no grupo '{grupo}' (herda config: {grupo_config.tipo_gasto_padrao})"
        )
    
    def create_grupo_com_subgrupo(self, grupo: str, subgrupo: str, tipo_gasto: str, categoria_geral: str = "Despesa") -> dict:
        """
        Cria grupo em base_grupos_config E subgrupo em base_marcacoes (atomicamente).
        """
        # 1. Verificar se grupo já existe
        existing_grupo = self.repository.get_grupo_config(grupo)
        if existing_grupo:
            raise HTTPException(
                status_code=409,
                detail=f"Grupo '{grupo}' já existe em base_grupos_config"
            )
        
        # 2. Criar grupo em base_grupos_config
        from app.domains.grupos.models import BaseGruposConfig
        novo_grupo = BaseGruposConfig(
            nome_grupo=grupo,
            tipo_gasto_padrao=tipo_gasto,
            categoria_geral=categoria_geral
        )
        self.repository.db.add(novo_grupo)
        self.repository.db.flush()  # Flush para obter ID mas não commit ainda
        
        # 3. Criar subgrupo em base_marcacoes
        marcacao = self.repository.create_marcacao(
            grupo=grupo,
            subgrupo=subgrupo
        )
        
        # 4. Commit de tudo junto (atomic)
        self.repository.db.commit()
        
        return {
            "grupo": grupo,
            "subgrupo": subgrupo,
            "tipo_gasto": tipo_gasto,
            "categoria_geral": categoria_geral,
            "grupo_id": novo_grupo.id,
            "marcacao_id": marcacao.id,
            "message": f"Grupo '{grupo}' e subgrupo '{subgrupo}' criados com sucesso"
        }
    
    def delete_subgrupo(self, grupo: str, subgrupo: str) -> dict:
        """Exclui subgrupo (marcação específica)"""
        # 1. Verificar se existe
        existing = self.repository.get_by_grupo_subgrupo(grupo, subgrupo)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Subgrupo '{subgrupo}' não encontrado no grupo '{grupo}'"
            )
        
        # 2. Verificar se há transações usando esta marcação
        transacoes_count = self.repository.count_transacoes_by_marcacao(grupo, subgrupo)
        if transacoes_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir. Há {transacoes_count} transações usando '{grupo} / {subgrupo}'"
            )
        
        # 3. Excluir
        success = self.repository.delete_marcacao(grupo, subgrupo)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao excluir subgrupo")
        
        return {"message": f"Subgrupo '{subgrupo}' excluído do grupo '{grupo}'"}
