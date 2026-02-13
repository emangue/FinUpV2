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
        Busca configuração (tipo_gasto, categoria) de base_grupos_config.
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
                detail=f"Subgrupo '{subgrupo_data.subgrupo}' já existe no grupo '{grupo}'",
                headers={"X-Existing-Id": str(existing.id)}
            )
        
        # 3. Pegar configuração do grupo (tipo_gasto e categoria vêm de lá)
        tipo_gasto = grupo_config.tipo_gasto_padrao
        categoria_geral = grupo_config.categoria_geral
        
        # 4. Permitir override se fornecido (opcional)
        if subgrupo_data.tipo_gasto:
            tipo_gasto = subgrupo_data.tipo_gasto
        if subgrupo_data.categoria_geral:
            categoria_geral = subgrupo_data.categoria_geral
        
        # 5. Criar marcação em base_marcacoes
        marcacao = self.repository.create_marcacao(
            grupo=grupo,
            subgrupo=subgrupo_data.subgrupo,
            tipo_gasto=tipo_gasto,
            categoria_geral=categoria_geral
        )
        
        # 6. Retornar resposta
        return SubgrupoResponse(
            id=marcacao.id,
            grupo=marcacao.GRUPO,
            subgrupo=marcacao.SUBGRUPO,
            tipo_gasto=marcacao.TipoGasto,
            categoria_geral=marcacao.CategoriaGeral,
            message=f"Subgrupo '{subgrupo_data.subgrupo}' criado no grupo '{grupo}'"
        )
    
    def create_marcacao_manual(self, marcacao_data: MarcacaoCreate) -> MarcacaoResponse:
        """
        Cria marcação manualmente (grupo + subgrupo).
        Verifica se grupo existe em base_grupos_config.
        """
        # 1. Verificar se grupo existe
        grupo_config = self.repository.get_grupo_config(marcacao_data.grupo)
        if not grupo_config:
            raise HTTPException(
                status_code=404,
                detail=f"Grupo '{marcacao_data.grupo}' não encontrado. Crie o grupo primeiro em /api/v1/grupos"
            )
        
        # 2. Verificar se marcação já existe
        existing = self.repository.get_by_grupo_subgrupo(
            marcacao_data.grupo,
            marcacao_data.subgrupo
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Marcação '{marcacao_data.grupo} / {marcacao_data.subgrupo}' já existe"
            )
        
        # 3. Criar marcação
        marcacao = self.repository.create_marcacao(
            grupo=marcacao_data.grupo,
            subgrupo=marcacao_data.subgrupo,
            tipo_gasto=marcacao_data.tipo_gasto,
            categoria_geral=marcacao_data.categoria_geral
        )
        
        return MarcacaoResponse.from_db_model(marcacao)
    
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
