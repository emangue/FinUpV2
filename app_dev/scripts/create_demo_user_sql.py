#!/usr/bin/env python3
# ==========================================
# Script de Criação de Usuário Demo (SQL Direto)
# ==========================================

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Configurações
DATABASE_PATH = Path(__file__).parent.parent / "backend" / "database" / "financas_dev.db"

DEMO_USER = {
    "email": "demo@financas.com",
    "name": "Usuário Demo",
    "password": "demo123",
}

# Transações de exemplo
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    print("=" * 50)
    print("  Criação de Usuário Demo - Sistema de Finanças")
    print("=" * 50)
    print()
    
    if not DATABASE_PATH.exists():
        print(f"❌ Database não encontrado: {DATABASE_PATH}")
        return
    
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    try:
        # 1. Criar usuário
        print("📋 Criando usuário demo...")
        
        # Verificar se já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", (DEMO_USER["email"],))
        existing = cursor.fetchone()
        
        if existing:
            user_id = existing[0]
            print(f"⚠️  Usuário {DEMO_USER['email']} já existe (ID: {user_id})")
        else:
            # Hash da senha
            hashed_password = pwd_context.hash(DEMO_USER["password"])
            
            # Inserir usuário
            cursor.execute("""
                INSERT INTO users (email, nome, password_hash, ativo)
                VALUES (?, ?, ?, 1)
            """, (DEMO_USER["email"], DEMO_USER["name"], hashed_password))
            
            user_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Usuário criado: {DEMO_USER['email']} (ID: {user_id})")
        
        print()
        
        # 2. Criar transações
        print("📋 Criando transações de exemplo...")
        hoje = datetime.now()
        transacoes_criadas = 0
        
        for mes_offset in range(3):  # Últimos 3 meses
            mes_base = hoje - timedelta(days=30 * mes_offset)
            
            for trans in SAMPLE_TRANSACTIONS:
                dia = trans["dia"]
                data_transacao = mes_base.replace(day=dia)
                data_str = data_transacao.strftime("%Y-%m-%d")
                
                # ID único
                id_transacao = f"DEMO_{user_id}_{data_str}_{trans['estabelecimento'][:10]}_{abs(trans['valor']):.2f}".replace(" ", "_")
                
                # Verificar se já existe
                cursor.execute("SELECT IdTransacao FROM journal_entries WHERE IdTransacao = ?", (id_transacao,))
                if cursor.fetchone():
                    continue
                
                # Inserir transação
                cursor.execute("""
                    INSERT INTO journal_entries (
                        user_id, IdTransacao, Data, Estabelecimento, Valor, TipoTransacao,
                        CategoriaGeral, arquivo_origem
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    id_transacao,
                    data_str,
                    trans["estabelecimento"],
                    trans["valor"],
                    trans["tipo"],
                    trans["categoria"],
                    "demo_data"
                ))
                
                transacoes_criadas += 1
        
        conn.commit()
        print(f"✅ Transações criadas: {transacoes_criadas} (últimos 3 meses)")
        
        print()
        
        # 4. Estatísticas
        print("📊 Estatísticas do usuário demo:")
        
        cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(Valor) FROM journal_entries WHERE user_id = ? AND TipoTransacao = 'Receita'", (user_id,))
        total_receitas = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(ABS(Valor)) FROM journal_entries WHERE user_id = ? AND TipoTransacao = 'Despesa'", (user_id,))
        total_despesas = cursor.fetchone()[0] or 0
        
        saldo = total_receitas - total_despesas
        
        print(f"   Total de transações: {total}")
        print(f"   Total de receitas: R$ {total_receitas:,.2f}")
        print(f"   Total de despesas: R$ {total_despesas:,.2f}")
        print(f"   Saldo: R$ {saldo:,.2f}")
        
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
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
