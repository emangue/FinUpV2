#!/usr/bin/env python3
"""
Remove cartões duplicados do usuário teste@email.com
"""

import sys
import os
from pathlib import Path

# Criar conexão direta com SQLite
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Path do banco de dados
DB_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criar engine e session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def main():
    db = SessionLocal()
    
    try:
        print('🗑️  Deletando cartões duplicados do teste@email.com...')
        print()
        
        # Deletar IDs maiores (os copiados recentemente)
        ids_para_deletar = [9, 10, 11, 12]
        
        for card_id in ids_para_deletar:
            result = db.execute(
                text('SELECT id, nome_cartao, final_cartao FROM cartoes WHERE id = :id'), 
                {'id': card_id}
            ).fetchone()
            
            if result:
                card_id_val = result[0]
                nome = result[1]
                final = result[2]
                print(f'  ❌ Deletando ID {card_id_val:3} - {nome:20} final {final}')
                db.execute(text('DELETE FROM cartoes WHERE id = :id'), {'id': card_id})
        
        db.commit()
        
        print()
        print('✅ Cartões duplicados removidos!')
        print()
        
        # Verificar resultado
        print('=== CARTÕES RESTANTES (user_id=4) ===')
        result = db.execute(
            text('SELECT id, nome_cartao, final_cartao, banco FROM cartoes WHERE user_id = 4 ORDER BY nome_cartao')
        ).fetchall()
        
        for row in result:
            card_id_val = row[0]
            nome = row[1]
            final = row[2]
            banco = row[3]
            print(f'ID: {card_id_val:3} | Nome: {nome:20} | Final: {final:6} | Banco: {banco:15}')
        
        print(f'\n📊 Total: {len(result)} cartões únicos')
        
    finally:
        db.close()

if __name__ == '__main__':
    main()
