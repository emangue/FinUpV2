#!/usr/bin/env python3
"""
Seed Script: Regras de Ignore padrão em transacoes_exclusao
Versão: 1.0.0
Data: 04/01/2026

Popula tabela transacoes_exclusao com regras padrão de acao='IGNORAR'
para cada usuário existente no sistema.

IMPORTANTE: Todas as regras hoje são acao='EXCLUIR' por padrão.
Este script é para uso futuro quando o usuário quiser configurar
regras de IGNORAR ao invés de EXCLUIR.
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def seed_ignore_rules():
    """Popula regras padrão de ignore para cada usuário"""
    
    # Determinar caminho do banco
    db_paths = [
        'app_dev/backend/database/financas_dev.db',
        'app/financas.db',
        'database/financas_dev.db'
    ]
    
    db_path = None
    for path in db_paths:
        full_path = os.path.join(project_root, path)
        if os.path.exists(full_path):
            db_path = full_path
            break
    
    if not db_path:
        print("❌ Banco de dados não encontrado!")
        return False
    
    print(f"📂 Usando banco: {db_path}")
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se coluna 'acao' existe
        cursor.execute("PRAGMA table_info(transacoes_exclusao)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'acao' not in columns:
            print("❌ Coluna 'acao' não existe!")
            print("   Execute primeiro: python scripts/migrate_add_acao_column.py")
            conn.close()
            return False
        
        # Buscar todos os usuários
        cursor.execute("SELECT id, nome, email FROM users WHERE ativo = 1")
        users = cursor.fetchall()
        
        if not users:
            print("⚠️  Nenhum usuário ativo encontrado")
            conn.close()
            return True
        
        print(f"\n👥 Encontrados {len(users)} usuários ativos")
        print()
        
        # Regras padrão de IGNORAR (exemplos - HOJE TUDO É EXCLUIR)
        # Estas regras são para referência futura
        regras_exemplo = [
            {
                'nome_transacao': 'AJUSTE SALDO',
                'descricao': 'Ajustes técnicos de saldo bancário',
                'banco': '',
                'tipo_documento': 'Extrato Conta'
            },
            {
                'nome_transacao': 'TARIFA MANUTENCAO',
                'descricao': 'Tarifas administrativas (opcional ignorar)',
                'banco': '',
                'tipo_documento': 'Extrato Conta'
            }
        ]
        
        total_inseridas = 0
        
        for user_id, nome, email in users:
            print(f"📝 Processando usuário: {nome} ({email})")
            
            # IMPORTANTE: Por enquanto, NÃO inserir nada automaticamente
            # Apenas mostrar o que PODERIA ser configurado
            print(f"   ℹ️  Usuário pode configurar regras de IGNORAR via interface admin")
            print(f"   ℹ️  Hoje todas as regras são acao='EXCLUIR' por padrão")
            
            # Exemplo comentado (não executar por enquanto):
            # for regra in regras_exemplo:
            #     cursor.execute("""
            #         INSERT OR IGNORE INTO transacoes_exclusao 
            #         (nome_transacao, descricao, banco, tipo_documento, user_id, ativo, acao, created_at)
            #         VALUES (?, ?, ?, ?, ?, 1, 'IGNORAR', ?)
            #     """, (
            #         regra['nome_transacao'],
            #         regra['descricao'],
            #         regra['banco'],
            #         regra['tipo_documento'],
            #         user_id,
            #         datetime.now()
            #     ))
            #     total_inseridas += cursor.rowcount
        
        conn.commit()
        
        print(f"\n✅ Seed concluído")
        print(f"📊 Total de regras IGNORAR inseridas: {total_inseridas}")
        print()
        print("ℹ️  LEMBRETE: Hoje TUDO é acao='EXCLUIR' por padrão")
        print("ℹ️  Configure regras de IGNORAR via interface admin quando necessário")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Erro durante seed: {e}")
        return False


def show_current_rules():
    """Mostra regras atuais de exclusão/ignore"""
    
    db_paths = [
        'app_dev/backend/database/financas_dev.db',
        'app/financas.db',
        'database/financas_dev.db'
    ]
    
    db_path = None
    for path in db_paths:
        full_path = os.path.join(project_root, path)
        if os.path.exists(full_path):
            db_path = full_path
            break
    
    if not db_path:
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se coluna 'acao' existe
        cursor.execute("PRAGMA table_info(transacoes_exclusao)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'acao' not in columns:
            print("⚠️  Coluna 'acao' ainda não existe - execute migrate_add_acao_column.py")
            cursor.execute("""
                SELECT nome_transacao, banco, tipo_documento, ativo
                FROM transacoes_exclusao
                ORDER BY nome_transacao
            """)
            print("\n📋 Regras atuais (sem coluna acao):")
            print("-" * 70)
            for row in cursor.fetchall():
                status = "✅ Ativa" if row[3] else "❌ Inativa"
                print(f"  {row[0]:<30} | {row[1]:<15} | {row[2]:<20} | {status}")
        else:
            cursor.execute("""
                SELECT nome_transacao, banco, tipo_documento, acao, ativo
                FROM transacoes_exclusao
                ORDER BY acao, nome_transacao
            """)
            
            print("\n📋 Regras atuais:")
            print("-" * 80)
            print(f"{'Nome':<30} | {'Banco':<15} | {'Tipo Doc':<20} | {'Ação':<10} | {'Status'}")
            print("-" * 80)
            
            count_excluir = 0
            count_ignorar = 0
            
            for row in cursor.fetchall():
                nome, banco, tipo_doc, acao, ativo = row
                status = "✅" if ativo else "❌"
                print(f"{nome:<30} | {banco:<15} | {tipo_doc:<20} | {acao:<10} | {status}")
                
                if ativo:
                    if acao == 'EXCLUIR':
                        count_excluir += 1
                    elif acao == 'IGNORAR':
                        count_ignorar += 1
            
            print("-" * 80)
            print(f"\n📊 Resumo:")
            print(f"   Regras EXCLUIR ativas: {count_excluir}")
            print(f"   Regras IGNORAR ativas: {count_ignorar}")
        
        conn.close()
    
    except Exception as e:
        print(f"❌ Erro ao consultar regras: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed de regras de ignore em transacoes_exclusao')
    parser.add_argument('--show', action='store_true', help='Apenas mostrar regras atuais')
    parser.add_argument('--seed', action='store_true', help='Inserir regras padrão (futuro)')
    
    args = parser.parse_args()
    
    if args.show:
        show_current_rules()
    elif args.seed:
        print("\n" + "="*70)
        print("⚠️  SEED: Regras de IGNORAR em transacoes_exclusao")
        print("="*70)
        print("\nIMPORTANTE:")
        print("  - Hoje TUDO é acao='EXCLUIR' por padrão")
        print("  - Este seed é para referência futura")
        print("  - Configure regras via interface admin")
        print()
        
        resposta = input("⚠️  Deseja continuar? (sim/não): ")
        
        if resposta.lower() in ['sim', 's', 'yes', 'y']:
            sucesso = seed_ignore_rules()
            sys.exit(0 if sucesso else 1)
        else:
            print("\n❌ Seed cancelado")
            sys.exit(1)
    else:
        # Default: mostrar ajuda
        parser.print_help()
        print()
        print("Exemplos:")
        print("  python scripts/seed_ignore_rules.py --show   # Ver regras atuais")
        print("  python scripts/seed_ignore_rules.py --seed   # Inserir regras (futuro)")
