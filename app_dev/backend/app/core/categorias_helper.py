"""
Helper functions para determinação de TipoGasto e CategoriaGeral via base_grupos_config

FASE 2: Helper Functions
- Funções isoladas que consultam base_grupos_config
- NÃO são usadas ainda pelo sistema (zero impacto)
- Podem ser testadas independentemente
"""

from sqlalchemy.orm import Session
from typing import Optional
import sqlite3


def determinar_tipo_gasto_via_config(session: Session, grupo: str) -> Optional[str]:
    """
    Busca tipo_gasto_padrao baseado no GRUPO usando base_grupos_config
    
    Args:
        session: SQLAlchemy session (ou None para usar sqlite3 direto)
        grupo: Nome do grupo (ex: 'Viagens')
    
    Returns:
        tipo_gasto_padrao (ex: 'Ajustável') ou None se não encontrado
    
    Exemplos:
        >>> determinar_tipo_gasto_via_config(db, 'Viagens')
        'Ajustável'
        
        >>> determinar_tipo_gasto_via_config(db, 'Moradia')
        'Fixo'
        
        >>> determinar_tipo_gasto_via_config(db, 'GrupoInexistente')
        None
    """
    if not grupo:
        return None
    
    # Se session é SQLAlchemy session
    if hasattr(session, 'execute'):
        result = session.execute(
            "SELECT tipo_gasto_padrao FROM base_grupos_config WHERE nome_grupo = :grupo",
            {"grupo": grupo}
        ).fetchone()
        
        return result[0] if result else None
    
    # Fallback: Se é connection sqlite3
    else:
        cursor = session.cursor()
        cursor.execute(
            "SELECT tipo_gasto_padrao FROM base_grupos_config WHERE nome_grupo = ?",
            (grupo,)
        )
        result = cursor.fetchone()
        return result[0] if result else None


def determinar_categoria_geral_via_config(session: Session, grupo: str) -> Optional[str]:
    """
    Busca categoria_geral baseada no GRUPO usando base_grupos_config
    
    Args:
        session: SQLAlchemy session (ou None para usar sqlite3 direto)
        grupo: Nome do grupo (ex: 'Salário')
    
    Returns:
        categoria_geral (ex: 'Receita') ou None se não encontrado
    
    Exemplos:
        >>> determinar_categoria_geral_via_config(db, 'Salário')
        'Receita'
        
        >>> determinar_categoria_geral_via_config(db, 'Aplicações')
        'Investimentos'
        
        >>> determinar_categoria_geral_via_config(db, 'Viagens')
        'Despesa'
    """
    if not grupo:
        return None
    
    # Se session é SQLAlchemy session
    if hasattr(session, 'execute'):
        result = session.execute(
            "SELECT categoria_geral FROM base_grupos_config WHERE nome_grupo = :grupo",
            {"grupo": grupo}
        ).fetchone()
        
        return result[0] if result else None
    
    # Fallback: Se é connection sqlite3
    else:
        cursor = session.cursor()
        cursor.execute(
            "SELECT categoria_geral FROM base_grupos_config WHERE nome_grupo = ?",
            (grupo,)
        )
        result = cursor.fetchone()
        return result[0] if result else None


def get_todos_grupos_config(session: Session) -> list[dict]:
    """
    Retorna todos os grupos configurados
    
    Returns:
        Lista de dicts: [{'nome_grupo': 'Viagens', 'tipo_gasto_padrao': 'Ajustável', 'categoria_geral': 'Despesa'}, ...]
    """
    if hasattr(session, 'execute'):
        result = session.execute("""
            SELECT nome_grupo, tipo_gasto_padrao, categoria_geral 
            FROM base_grupos_config 
            ORDER BY tipo_gasto_padrao, nome_grupo
        """).fetchall()
        
        return [
            {
                'nome_grupo': row[0],
                'tipo_gasto_padrao': row[1],
                'categoria_geral': row[2]
            }
            for row in result
        ]
    else:
        cursor = session.cursor()
        cursor.execute("""
            SELECT nome_grupo, tipo_gasto_padrao, categoria_geral 
            FROM base_grupos_config 
            ORDER BY tipo_gasto_padrao, nome_grupo
        """)
        
        return [
            {
                'nome_grupo': row[0],
                'tipo_gasto_padrao': row[1],
                'categoria_geral': row[2]
            }
            for row in cursor.fetchall()
        ]
