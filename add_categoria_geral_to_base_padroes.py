#!/usr/bin/env python3
"""
Adiciona coluna categoria_geral_sugerida na tabela base_padroes
"""

import sys
sys.path.insert(0, 'app_dev/backend')

from app.core.database import engine
from sqlalchemy import text

def adicionar_coluna_categoria_geral():
    """Adiciona coluna categoria_geral_sugerida se não existir"""
    print("🔄 Adicionando coluna categoria_geral_sugerida à base_padroes...")
    
    with engine.connect() as conn:
        # Verificar se coluna já existe
        result = conn.execute(text("PRAGMA table_info(base_padroes)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'categoria_geral_sugerida' in columns:
            print("✅ Coluna categoria_geral_sugerida já existe")
            return
        
        # Adicionar coluna
        conn.execute(text("""
            ALTER TABLE base_padroes 
            ADD COLUMN categoria_geral_sugerida TEXT
        """))
        conn.commit()
        
        print("✅ Coluna categoria_geral_sugerida adicionada com sucesso")
        
        # Verificar resultado
        result = conn.execute(text("PRAGMA table_info(base_padroes)"))
        columns = [row[1] for row in result.fetchall()]
        
        print(f"\n📊 Colunas atuais em base_padroes: {len(columns)}")
        print("   Últimas 5 colunas:")
        for col in columns[-5:]:
            print(f"   - {col}")

if __name__ == "__main__":
    adicionar_coluna_categoria_geral()
