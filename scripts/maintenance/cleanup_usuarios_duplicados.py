#!/usr/bin/env python3
"""
Script de Limpeza - Usuários Duplicados/Inativos
Data: 23/01/2026

PROBLEMA:
- Duas contas admin (admin@financas.com ATIVA, admin@email.com INATIVA)
- Confusão ao testar autenticação

SOLUÇÕES PROPOSTAS:
1. Deletar conta admin@email.com (INATIVA) - RECOMENDADO
2. Mudar role de admin@email.com para 'user' - ALTERNATIVA
"""
import sys
from pathlib import Path

# Adicionar app ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app_dev" / "backend"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def listar_usuarios_admin(session):
    """Lista todos os usuários admin"""
    print("\n📋 Usuários Admin no Sistema:")
    print("=" * 80)
    
    result = session.execute(text("""
        SELECT id, email, nome, ativo, role, created_at 
        FROM users 
        WHERE role = 'admin'
        ORDER BY id
    """))
    
    usuarios = result.fetchall()
    
    for user in usuarios:
        status = "✅ ATIVO" if user.ativo else "❌ INATIVO"
        print(f"\nID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Nome: {user.nome}")
        print(f"  Status: {status}")
        print(f"  Criado: {user.created_at}")
    
    return usuarios

def contar_transacoes_usuario(session, user_id):
    """Conta transações do usuário"""
    result = session.execute(text("""
        SELECT COUNT(*) as total FROM journal_entries WHERE user_id = :user_id
    """), {"user_id": user_id})
    
    return result.fetchone().total

def opcao_1_deletar_inativo(session):
    """Opção 1: Deletar conta admin@email.com (INATIVA)"""
    print("\n🗑️  OPÇÃO 1: Deletar conta admin@email.com (INATIVA)")
    print("=" * 80)
    
    # Verificar se tem transações
    total_transacoes = contar_transacoes_usuario(session, 3)
    
    if total_transacoes > 0:
        print(f"⚠️  ATENÇÃO: Esta conta tem {total_transacoes} transações!")
        print("   Ao deletar a conta, as transações serão mantidas mas ficarão órfãs.")
        print("   Recomendo migrar transações para outra conta antes de deletar.\n")
        
        confirma = input("Deseja continuar mesmo assim? (digite 'SIM' para confirmar): ")
        if confirma != "SIM":
            print("❌ Operação cancelada")
            return
    else:
        print(f"✅ Esta conta NÃO tem transações (seguro deletar)")
    
    # Confirmar novamente
    print("\n⚠️  CONFIRMAÇÃO FINAL")
    print("Você está prestes a DELETAR PERMANENTEMENTE:")
    print("  - Usuário: admin@email.com (ID=3)")
    print("  - Esta ação NÃO pode ser desfeita!\n")
    
    confirma = input("Digite 'DELETAR' para confirmar: ")
    
    if confirma == "DELETAR":
        # Deletar usuário
        session.execute(text("DELETE FROM users WHERE id = 3"))
        session.commit()
        
        print("\n✅ Usuário admin@email.com (ID=3) deletado com sucesso!")
        print("   Sistema agora tem apenas 1 admin: admin@financas.com")
    else:
        print("❌ Operação cancelada")

def opcao_2_mudar_role(session):
    """Opção 2: Mudar role de admin@email.com para 'user'"""
    print("\n🔄 OPÇÃO 2: Mudar role de admin@email.com para 'user'")
    print("=" * 80)
    
    print("Esta operação irá:")
    print("  - Manter a conta admin@email.com")
    print("  - Mudar role de 'admin' para 'user'")
    print("  - Conta continua INATIVA (ativo=0)")
    print("  - Transações são mantidas\n")
    
    confirma = input("Digite 'SIM' para confirmar: ")
    
    if confirma == "SIM":
        # Atualizar role
        session.execute(text("""
            UPDATE users 
            SET role = 'user', 
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = 3
        """))
        session.commit()
        
        print("\n✅ Role alterado com sucesso!")
        print("   admin@email.com agora é 'user' (ainda inativo)")
    else:
        print("❌ Operação cancelada")

def opcao_3_ativar_e_mudar_role(session):
    """Opção 3: Ativar admin@email.com e mudar para 'user'"""
    print("\n✅ OPÇÃO 3: Ativar admin@email.com e mudar para 'user'")
    print("=" * 80)
    
    print("Esta operação irá:")
    print("  - ATIVAR a conta admin@email.com")
    print("  - Mudar role de 'admin' para 'user'")
    print("  - Pode ser usada para testes de usuário comum\n")
    
    confirma = input("Digite 'SIM' para confirmar: ")
    
    if confirma == "SIM":
        # Atualizar role e status
        session.execute(text("""
            UPDATE users 
            SET role = 'user', 
                ativo = 1,
                updated_at = CURRENT_TIMESTAMP 
            WHERE id = 3
        """))
        session.commit()
        
        print("\n✅ Conta atualizada com sucesso!")
        print("   admin@email.com agora é 'user' ativo")
        print("   Pode fazer login com a senha cadastrada")
    else:
        print("❌ Operação cancelada")

def main():
    print("🔧 SCRIPT DE LIMPEZA - Usuários Duplicados/Inativos")
    print("=" * 80)
    
    # Conectar ao banco
    engine = create_engine(f"sqlite:///{settings.DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Listar usuários admin
        usuarios = listar_usuarios_admin(session)
        
        if len(usuarios) <= 1:
            print("\n✅ Sistema tem apenas 1 admin - nenhuma ação necessária")
            return
        
        # Menu de opções
        print("\n")
        print("=" * 80)
        print("OPÇÕES DE LIMPEZA:")
        print("=" * 80)
        print("1. Deletar admin@email.com (INATIVA) - RECOMENDADO")
        print("2. Mudar role de admin@email.com para 'user' (manter inativo)")
        print("3. Ativar admin@email.com e mudar para 'user' (usar para testes)")
        print("0. Cancelar")
        print("=" * 80)
        
        opcao = input("\nEscolha uma opção (0-3): ")
        
        if opcao == "1":
            opcao_1_deletar_inativo(session)
        elif opcao == "2":
            opcao_2_mudar_role(session)
        elif opcao == "3":
            opcao_3_ativar_e_mudar_role(session)
        elif opcao == "0":
            print("❌ Operação cancelada")
        else:
            print("❌ Opção inválida")
        
        # Listar novamente após mudanças
        if opcao in ["1", "2", "3"]:
            print("\n")
            listar_usuarios_admin(session)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
