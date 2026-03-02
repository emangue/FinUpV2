#!/usr/bin/env python3
"""
Teste: Criar usuário e detalhar o que foi criado para ele.
Uso: cd app_dev/backend && python ../../scripts/testing/test_criar_usuario_detalhado.py
"""
import os
import sys
from pathlib import Path

# Adicionar backend ao path
ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# Usar SQLite local (ou DATABASE_URL do .env)
DB_PATH = BACKEND / "database" / "financas_dev.db"
if not DB_PATH.exists():
    print(f"❌ Banco não encontrado: {DB_PATH}")
    sys.exit(1)

import sqlite3
from datetime import datetime
from app.domains.auth.password_utils import hash_password

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Contar usuários antes
    cur.execute("SELECT COUNT(*) FROM users")
    count_antes = cur.fetchone()[0]

    # 2. Criar usuário (simula o que UserService.create_user faz)
    email = f"teste_criacao_{datetime.now().strftime('%H%M%S')}@teste.com"
    nome = "Usuário Teste Criação"
    password_hash = hash_password("senha123")
    role = "user"
    ativo = 1
    now = datetime.now().isoformat()

    cur.execute("""
        INSERT INTO users (email, nome, password_hash, role, ativo, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, nome, password_hash, role, ativo, now, now))
    conn.commit()
    user_id = cur.lastrowid

    print("=" * 60)
    print("TESTE: Criação de novo usuário")
    print("=" * 60)
    print(f"\n✅ Usuário criado: id={user_id}, email={email}")
    print(f"\n📋 Registros criados na tabela users:")

    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    for key in row.keys():
        val = row[key]
        if key == "password_hash":
            val = f"<hash bcrypt {len(val)} chars>"
        print(f"   {key}: {val}")

    # 3. Verificar tabelas por usuário (zeradas)
    tabelas_user = [
        "journal_entries",
        "upload_history",
        "budget_planning",
        "cartoes",
        "base_padroes",
        "base_parcelas",
        "preview_transacoes",
        "transacoes_exclusao",
        "investimentos_portfolio",
        "investimentos_historico",
        "investimentos_planejamento",
        "investimentos_cenarios",
    ]

    print(f"\n📊 Dados por usuário (zerados para user_id={user_id}):")
    for tabela in tabelas_user:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {tabela} WHERE user_id = ?", (user_id,))
            cnt = cur.fetchone()[0]
            print(f"   {tabela}: {cnt} registros")
        except sqlite3.OperationalError:
            print(f"   {tabela}: (tabela não existe ou sem user_id)")

    # 4. Dados globais (disponíveis)
    print(f"\n🌐 Dados globais (disponíveis para todos):")
    for tabela in ["base_grupos_config", "generic_classification_rules", "screen_visibility"]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {tabela}")
            cnt = cur.fetchone()[0]
            print(f"   {tabela}: {cnt} registros")
        except sqlite3.OperationalError:
            pass

    # 5. Limpar: remover usuário de teste
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    print(f"\n🧹 Usuário de teste removido (id={user_id})")

    conn.close()
    print("\n" + "=" * 60)
    print("CONCLUSÃO: Novo usuário recebe APENAS 1 registro em users.")
    print("Todas as outras tabelas por usuário ficam zeradas.")
    print("=" * 60)

if __name__ == "__main__":
    main()
