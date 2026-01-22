#!/usr/bin/env python3
"""
Script para verificar todos os usuários no banco
"""
import sys
from pathlib import Path

# Adicionar app ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.domains.users.models import User

def check_users():
    """Lista todos os usuários"""
    
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        print(f"\n📋 Total de usuários: {len(users)}\n")
        
        for user in users:
            print(f"{'='*60}")
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Nome: {user.nome}")
            print(f"Role: {user.role}")
            print(f"Ativo: {user.ativo}")
            print(f"Hash: {user.password_hash[:50]}...")
        
        print(f"{'='*60}\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    check_users()
