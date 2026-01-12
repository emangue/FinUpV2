#!/usr/bin/env python3
# ==========================================
# Script de Criação de Usuário Demo
# ==========================================
# 
# Cria usuário de demonstração com transações de exemplo
# para apresentar funcionalidades do sistema
#
# Uso:
#   python scripts/create_demo_user.py
#
# ==========================================

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Adicionar path do backend
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal, engine
from app.domains.users.models import User
from app.domains.transactions.models import JournalEntry
from app.domains.categories.models import BaseMarcacao
from passlib.context import CryptContext

# ==========================================
# Configurações
# ==========================================

DEMO_USER = {
    "email": "demo@financas.com",
    "name": "Usuário Demo",
    "password": "demo123",  # Senha simples para demonstração
}

# Transações de exemplo (últimos 3 meses)
SAMPLE_TRANSACTIONS = [
    # Salário
    {"estabelecimento": "Salário Empresa XYZ", "valor": 5000.00, "tipo": "Receita", "categoria": "Salário", "dia": 5},
    
    # Alimentação
    {"estabelecimento": "Supermercado Extra", "valor": -450.00, "tipo": "Despesa", "categoria": "Alimentação", "dia": 7},
    {"estabelecimento": "Padaria Central", "valor": -35.00, "tipo": "Despesa", "categoria": "Alimentação", "dia": 8},
    {"estabelecimento": "Restaurante Italiano", "valor": -120.00, "tipo": "Despesa", "categoria": "Alimentação", "dia": 12},
    {"estabelecimento": "Mercado Orgânico", "valor": -180.00, "tipo": "Despesa", "categoria": "Alimentação", "dia": 15},
    {"estabelecimento": "Delivery iFood", "valor": -65.00, "tipo": "Despesa", "categoria": "Alimentação", "dia": 18},
    
    # Transporte
    {"estabelecimento": "Uber", "valor": -45.00, "tipo": "Despesa", "categoria": "Transporte", "dia": 9},
    {"estabelecimento": "Shell Posto", "valor": -200.00, "tipo": "Despesa", "categoria": "Transporte", "dia": 10},
    {"estabelecimento": "Estacionamento Shopping", "valor": -25.00, "tipo": "Despesa", "categoria": "Transporte", "dia": 14},
    
    # Moradia
    {"estabelecimento": "Aluguel Imóvel", "valor": -1500.00, "tipo": "Despesa", "categoria": "Moradia", "dia": 1},
    {"estabelecimento": "Conta Luz - Enel", "valor": -180.00, "tipo": "Despesa", "categoria": "Moradia", "dia": 6},
    {"estabelecimento": "Conta Água - Sabesp", "valor": -85.00, "tipo": "Despesa", "categoria": "Moradia", "dia": 8},
    {"estabelecimento": "Internet Claro", "valor": -99.00, "tipo": "Despesa", "categoria": "Moradia", "dia": 10},
    
    # Saúde
    {"estabelecimento": "Farmácia São Paulo", "valor": -120.00, "tipo": "Despesa", "categoria": "Saúde", "dia": 11},
    {"estabelecimento": "Plano de Saúde Unimed", "valor": -450.00, "tipo": "Despesa", "categoria": "Saúde", "dia": 5},
    
    # Lazer
    {"estabelecimento": "Netflix", "valor": -49.90, "tipo": "Despesa", "categoria": "Lazer", "dia": 3},
    {"estabelecimento": "Spotify", "valor": -19.90, "tipo": "Despesa", "categoria": "Lazer", "dia": 4},
    {"estabelecimento": "Cinema Cinemark", "valor": -80.00, "tipo": "Despesa", "categoria": "Lazer", "dia": 16},
    {"estabelecimento": "Livraria Cultura", "valor": -95.00, "tipo": "Despesa", "categoria": "Lazer", "dia": 20},
    
    # Educação
    {"estabelecimento": "Curso Online Udemy", "valor": -129.00, "tipo": "Despesa", "categoria": "Educação", "dia": 13},
    
    # Vestuário
    {"estabelecimento": "Loja Renner", "valor": -250.00, "tipo": "Despesa", "categoria": "Vestuário", "dia": 17},
    
    # Outros
    {"estabelecimento": "PIX João Silva", "valor": -100.00, "tipo": "Despesa", "categoria": "Transferências", "dia": 19},
    {"estabelecimento": "Freelance Projeto ABC", "valor": 800.00, "tipo": "Receita", "categoria": "Trabalho Extra", "dia": 22},
]

# ==========================================
# Funções
# ==========================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db, email, name, password):
    """Criar usuário demo"""
    # Verificar se já existe
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"⚠️  Usuário {email} já existe (ID: {existing.id})")
        return existing
    
    # Hash da senha
    hashed_password = pwd_context.hash(password)
    
    # Criar usuário
    user = User(
        email=email,
        nome=name,
        password_hash=hashed_password,
        ativo=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✅ Usuário criado: {email} (ID: {user.id})")
    return user

def create_categories(db, user_id):
    """Criar categorias padrão"""
    categories = [
        {"nome": "Salário", "tipo": "Receita"},
        {"nome": "Trabalho Extra", "tipo": "Receita"},
        {"nome": "Alimentação", "tipo": "Despesa"},
        {"nome": "Transporte", "tipo": "Despesa"},
        {"nome": "Moradia", "tipo": "Despesa"},
        {"nome": "Saúde", "tipo": "Despesa"},
        {"nome": "Lazer", "tipo": "Despesa"},
        {"nome": "Educação", "tipo": "Despesa"},
        {"nome": "Vestuário", "tipo": "Despesa"},
        {"nome": "Transferências", "tipo": "Despesa"},
    ]
    
    created = []
    for cat in categories:
        # Verificar se já existe
        existing = db.query(BaseMarcacao).filter(
            BaseMarcacao.user_id == user_id,
            BaseMarcacao.nome == cat["nome"]
        ).first()
        
        if not existing:
            categoria = BaseMarcacao(
                user_id=user_id,
                nome=cat["nome"],
                tipo=cat["tipo"]
            )
            db.add(categoria)
            created.append(cat["nome"])
    
    db.commit()
    
    if created:
        print(f"✅ Categorias criadas: {', '.join(created)}")
    else:
        print("ℹ️  Categorias já existiam")
    
    return True

def create_transactions(db, user_id):
    """Criar transações de exemplo (últimos 3 meses)"""
    hoje = datetime.now()
    
    transacoes_criadas = 0
    
    # Criar transações para os últimos 3 meses
    for mes_offset in range(3):  # 0, 1, 2 (mês atual e 2 anteriores)
        mes_base = hoje - timedelta(days=30 * mes_offset)
        
        for trans in SAMPLE_TRANSACTIONS:
            # Data da transação
            dia = trans["dia"]
            data_transacao = mes_base.replace(day=dia)
            
            # Buscar categoria
            categoria = db.query(BaseMarcacao).filter(
                BaseMarcacao.user_id == user_id,
                BaseMarcacao.nome == trans["categoria"]
            ).first()
            
            if not categoria:
                print(f"⚠️  Categoria não encontrada: {trans['categoria']}")
                continue
            
            # Gerar IdTransacao único
            id_transacao = f"DEMO_{user_id}_{data_transacao.strftime('%Y%m%d')}_{trans['estabelecimento'][:10]}_{abs(trans['valor']):.2f}".replace(" ", "_")
            
            # Verificar se já existe
            existing = db.query(JournalEntry).filter(
                JournalEntry.IdTransacao == id_transacao
            ).first()
            
            if existing:
                continue
            
            # Criar transação
            transacao = JournalEntry(
                user_id=user_id,
                IdTransacao=id_transacao,
                Data=data_transacao.strftime("%Y-%m-%d"),
                Lancamento=trans["estabelecimento"],
                Valor=trans["valor"],
                Tipo=trans["tipo"],
                Categoria=trans["categoria"],
                Grupo=None,
                TipoGasto=None,
                IdParcela=None,
                TipoPagamento="Débito" if trans["tipo"] == "Despesa" else "Crédito",
                origem_arquivo="demo_data"
            )
            
            db.add(transacao)
            transacoes_criadas += 1
    
    db.commit()
    
    print(f"✅ Transações criadas: {transacoes_criadas} (últimos 3 meses)")
    return transacoes_criadas

def calculate_stats(db, user_id):
    """Calcular estatísticas do usuário"""
    # Total de transações
    total = db.query(JournalEntry).filter(JournalEntry.user_id == user_id).count()
    
    # Total receitas
    receitas = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.Tipo == "Receita"
    ).all()
    total_receitas = sum([t.Valor for t in receitas])
    
    # Total despesas
    despesas = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        JournalEntry.Tipo == "Despesa"
    ).all()
    total_despesas = sum([abs(t.Valor) for t in despesas])
    
    # Saldo
    saldo = total_receitas - total_despesas
    
    return {
        "total": total,
        "receitas": total_receitas,
        "despesas": total_despesas,
        "saldo": saldo
    }

# ==========================================
# Main
# ==========================================

def main():
    print("=" * 50)
    print("  Criação de Usuário Demo - Sistema de Finanças")
    print("=" * 50)
    print()
    
    # Conectar ao banco
    db = SessionLocal()
    
    try:
        # 1. Criar usuário
        print("📋 Criando usuário demo...")
        user = create_user(
            db,
            email=DEMO_USER["email"],
            name=DEMO_USER["name"],
            password=DEMO_USER["password"]
        )
        
        print()
        
        # 2. Criar categorias
        print("📋 Criando categorias padrão...")
        create_categories(db, user.id)
        
        print()
        
        # 3. Criar transações
        print("📋 Criando transações de exemplo...")
        create_transactions(db, user.id)
        
        print()
        
        # 4. Estatísticas
        print("📊 Estatísticas do usuário demo:")
        stats = calculate_stats(db, user.id)
        print(f"   Total de transações: {stats['total']}")
        print(f"   Total de receitas: R$ {stats['receitas']:,.2f}")
        print(f"   Total de despesas: R$ {stats['despesas']:,.2f}")
        print(f"   Saldo: R$ {stats['saldo']:,.2f}")
        
        print()
        print("=" * 50)
        print("✅ Usuário demo criado com sucesso!")
        print("=" * 50)
        print()
        print("🔑 Credenciais para login:")
        print(f"   Email:    {DEMO_USER['email']}")
        print(f"   Senha:    {DEMO_USER['password']}")
        print()
        print("🌐 Acessar: http://localhost:3000")
        print()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
