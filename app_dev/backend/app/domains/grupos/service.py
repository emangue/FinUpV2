"""
Domínio Grupos - Service
Lógica de negócio para configuração de grupos
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from .repository import GrupoRepository
from .schemas import GrupoCreate, GrupoUpdate, GrupoResponse, GrupoListResponse
from .models import BaseGruposConfig


class GrupoService:
    def __init__(self, db: Session):
        self.repository = GrupoRepository(db)
    
    def list_grupos(self) -> GrupoListResponse:
        """Lista todos os grupos configurados"""
        grupos = self.repository.get_all()
        return GrupoListResponse(
            grupos=[GrupoResponse.model_validate(grupo) for grupo in grupos],
            total=len(grupos)
        )
    
    def get_grupo(self, grupo_id: int) -> GrupoResponse:
        """Busca grupo por ID"""
        grupo = self.repository.get_by_id(grupo_id)
        if not grupo:
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        return GrupoResponse.model_validate(grupo)
    
    def create_grupo(self, grupo_data: GrupoCreate) -> GrupoResponse:
        """Cria novo grupo"""
        # Verificar se nome já existe
        existing = self.repository.get_by_nome(grupo_data.nome_grupo)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Já existe um grupo com o nome '{grupo_data.nome_grupo}'"
            )
        
        # Validar tipo_gasto_padrao
        tipos_validos = self.repository.get_tipos_gasto_disponiveis()
        if grupo_data.tipo_gasto_padrao not in tipos_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de gasto deve ser um de: {', '.join(tipos_validos)}"
            )
        
        # Validar categoria_geral
        categorias_validas = self.repository.get_categorias_disponiveis()
        if grupo_data.categoria_geral not in categorias_validas:
            raise HTTPException(
                status_code=400,
                detail=f"Categoria geral deve ser uma de: {', '.join(categorias_validas)}"
            )
        
        grupo = self.repository.create(grupo_data)
        return GrupoResponse.model_validate(grupo)
    
    def update_grupo(self, grupo_id: int, grupo_data: GrupoUpdate) -> GrupoResponse:
        """Atualiza grupo existente"""
        # Verificar se grupo existe
        existing = self.repository.get_by_id(grupo_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        
        # Se mudando nome, verificar se novo nome já existe
        if grupo_data.nome_grupo and grupo_data.nome_grupo != existing.nome_grupo:
            nome_exists = self.repository.get_by_nome(grupo_data.nome_grupo)
            if nome_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Já existe um grupo com o nome '{grupo_data.nome_grupo}'"
                )
        
        # Validar tipo_gasto_padrao se fornecido
        if grupo_data.tipo_gasto_padrao:
            tipos_validos = self.repository.get_tipos_gasto_disponiveis()
            if grupo_data.tipo_gasto_padrao not in tipos_validos:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de gasto deve ser um de: {', '.join(tipos_validos)}"
                )
        
        # Validar categoria_geral se fornecida
        if grupo_data.categoria_geral:
            categorias_validas = self.repository.get_categorias_disponiveis()
            if grupo_data.categoria_geral not in categorias_validas:
                raise HTTPException(
                    status_code=400,
                    detail=f"Categoria geral deve ser uma de: {', '.join(categorias_validas)}"
                )
        
        grupo = self.repository.update(grupo_id, grupo_data)
        return GrupoResponse.model_validate(grupo)
    
    def delete_grupo(self, grupo_id: int) -> dict:
        """Exclui grupo"""
        # Verificar se grupo existe
        existing = self.repository.get_by_id(grupo_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Grupo não encontrado")
        
        # Verificar se há transações usando este grupo
        transacoes_count = self.repository.count_transacoes_by_grupo(existing.nome_grupo)
        if transacoes_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível excluir o grupo '{existing.nome_grupo}' pois ele possui {transacoes_count} transações associadas. Exclua ou reclassifique as transações primeiro."
            )
        
        success = self.repository.delete(grupo_id)
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao excluir grupo")
        
        return {"message": f"Grupo '{existing.nome_grupo}' excluído com sucesso"}
    
    def get_opcoes(self) -> dict:
        """Retorna opções disponíveis para formulários (Sprint C: inclui paleta de cores)"""
        return {
            "tipos_gasto": self.repository.get_tipos_gasto_disponiveis(),
            "categorias": self.repository.get_categorias_disponiveis(),
            "paleta_cores": [
                "#001D39", "#0A4174", "#2D5A7B", "#49769F", "#4E8EA2",
                "#5E9AB0", "#6EA2B3", "#7BBDE8", "#9AC9E8", "#BDD8E9", "#D4E8F0"
            ]
        }