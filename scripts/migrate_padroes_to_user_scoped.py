#!/usr/bin/env python3
"""
Migração: Base Padrões para User-Scoped (Não-Híbrido)

Converte base_padroes de híbrida (user_id nullable) para totalmente separada por usuário.

Mudanças:
1. Duplica padrões globais (user_id=NULL) para cada usuário
2. Torna user_id NOT NULL (obrigatório)
3. Remove coluna "shared" (não é mais necessária)

Data: 2025-12-28
Versão: 3.0.1
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import get_db_session, User, BasePadrao
from sqlalchemy import text
import shutil
from datetime import datetime


def backup_database():
    """Cria backup antes da migração"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"financas.db.backup_{timestamp}"
    
    if os.path.exists('financas.db'):
        shutil.copy2('financas.db', backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    else:
        print("⚠️  Banco de dados não encontrado")
        return None


def migrate_padroes_to_user_scoped():
    """Migra base_padroes para modelo totalmente separado por usuário"""
    print("\n" + "="*70)
    print("🔄 MIGRAÇÃO: Base Padrões → User-Scoped (Não-Híbrido)")
    print("="*70)
    
    # Backup
    backup_path = backup_database()
    if not backup_path:
        print("❌ Falha ao criar backup. Abortando migração.")
        return False
    
    db = get_db_session()
    
    try:
        # 1. Listar usuários ativos
        usuarios = db.query(User).filter(User.ativo == True).all()
        print(f"\n📋 Usuários ativos: {len(usuarios)}")
        for user in usuarios:
            print(f"   - {user.nome} ({user.email}) [ID: {user.id}]")
        
        # 2. Recriar tabela com constraints corretas (ANTES de duplicar)
        print("\n🔧 Recriando tabela para permitir padrões duplicados por usuário...")
        try:
            # SQLite não suporta ALTER TABLE para modificar constraints, precisa recriar
            db.execute(text("""
                CREATE TABLE base_padroes_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    padrao_estabelecimento TEXT NOT NULL,
                    padrao_num TEXT NOT NULL,
                    contagem INTEGER NOT NULL,
                    valor_medio REAL NOT NULL,
                    valor_min REAL,
                    valor_max REAL,
                    desvio_padrao REAL,
                    coef_variacao REAL,
                    percentual_consistencia INTEGER NOT NULL,
                    confianca TEXT NOT NULL,
                    grupo_sugerido TEXT,
                    subgrupo_sugerido TEXT,
                    tipo_gasto_sugerido TEXT,
                    faixa_valor TEXT,
                    segmentado INTEGER DEFAULT 0,
                    exemplos TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ativo',
                    UNIQUE(user_id, padrao_estabelecimento),
                    UNIQUE(padrao_num),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            
            db.execute(text("""
                INSERT INTO base_padroes_new 
                SELECT id, user_id, padrao_estabelecimento, padrao_num, contagem, 
                       valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                       percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                       tipo_gasto_sugerido, faixa_valor, segmentado, exemplos, data_criacao, status
                FROM base_padroes
            """))
            
            db.execute(text("DROP TABLE base_padroes"))
            db.execute(text("ALTER TABLE base_padroes_new RENAME TO base_padroes"))
            db.execute(text("CREATE INDEX idx_base_padroes_user_id ON base_padroes(user_id)"))
            
            db.commit()
            print("✅ Tabela recriada (constraint: UNIQUE por user_id + estabelecimento)")
        except Exception as e:
            print(f"❌ Erro ao recriar tabela: {e}")
            raise
        
        # 3. Contar padrões globais (user_id=NULL) usando SQL direto
        result = db.execute(text("SELECT COUNT(*) FROM base_padroes WHERE user_id IS NULL")).fetchone()
        qtd_padroes_globais = result[0]
        print(f"\n🌍 Padrões globais encontrados: {qtd_padroes_globais}")
        
        if qtd_padroes_globais == 0:
            print("⚠️  Nenhum padrão global para duplicar")
        else:
            # 4. Duplicar padrões globais para cada usuário usando SQL direto
            print(f"\n📋 Duplicando padrões globais para cada usuário...")
            total_duplicados = 0
            
            for user in usuarios:
                print(f"\n   Processando {user.nome}...")
                
                # Inserir cópias para o usuário
                db.execute(text(f"""
                    INSERT INTO base_padroes (
                        user_id, padrao_estabelecimento, padrao_num, contagem,
                        valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                        percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                        tipo_gasto_sugerido, faixa_valor, segmentado, exemplos, data_criacao, status
                    )
                    SELECT 
                        {user.id},
                        padrao_estabelecimento,
                        padrao_num || '_user{user.id}',
                        contagem, valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                        percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                        tipo_gasto_sugerido, faixa_valor, segmentado, exemplos, data_criacao, status
                    FROM base_padroes
                    WHERE user_id IS NULL
                """))
                
                db.commit()
                duplicados_usuario = db.execute(text(f"SELECT COUNT(*) FROM base_padroes WHERE user_id = {user.id}")).fetchone()[0]
                print(f"      ✅ {duplicados_usuario} padrões criados")
                total_duplicados += duplicados_usuario
            
            print(f"\n✅ Total de padrões duplicados: {total_duplicados}")
        
        # 5. Deletar padrões globais (user_id=NULL)
        if qtd_padroes_globais > 0:
            print(f"\n🗑️  Removendo {qtd_padroes_globais} padrões globais...")
            db.execute(text("DELETE FROM base_padroes WHERE user_id IS NULL"))
            db.commit()
            print("✅ Padrões globais removidos")
        
        # 6. Verificar se há padrões órfãos (user_id não existe)
        print("\n🔍 Verificando padrões órfãos...")
        padroes_orfaos = db.execute(text("""
            SELECT COUNT(*) as total 
            FROM base_padroes 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)).fetchone()
        
        if padroes_orfaos[0] > 0:
            print(f"⚠️  {padroes_orfaos[0]} padrões órfãos encontrados")
            print("   Associando ao primeiro usuário ativo...")
            primeiro_usuario = usuarios[0]
            db.execute(text(f"""
                UPDATE base_padroes 
                SET user_id = {primeiro_usuario.id} 
                WHERE user_id NOT IN (SELECT id FROM users)
            """))
            db.commit()
            print(f"✅ Padrões órfãos associados a {primeiro_usuario.nome}")
        else:
            print("✅ Nenhum padrão órfão encontrado")
        
        # 7. Tornar user_id NOT NULL
        print("\n🔧 Tornando user_id obrigatório (NOT NULL)...")
        try:
            db.execute(text("""
                CREATE TABLE base_padroes_final (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    padrao_estabelecimento TEXT NOT NULL,
                    padrao_num TEXT NOT NULL,
                    contagem INTEGER NOT NULL,
                    valor_medio REAL NOT NULL,
                    valor_min REAL,
                    valor_max REAL,
                    desvio_padrao REAL,
                    coef_variacao REAL,
                    percentual_consistencia INTEGER NOT NULL,
                    confianca TEXT NOT NULL,
                    grupo_sugerido TEXT,
                    subgrupo_sugerido TEXT,
                    tipo_gasto_sugerido TEXT,
                    faixa_valor TEXT,
                    segmentado INTEGER DEFAULT 0,
                    exemplos TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'ativo',
                    UNIQUE(user_id, padrao_estabelecimento),
                    UNIQUE(padrao_num),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            
            db.execute(text("""
                INSERT INTO base_padroes_final 
                SELECT * FROM base_padroes
            """))
            
            db.execute(text("DROP TABLE base_padroes"))
            db.execute(text("ALTER TABLE base_padroes_final RENAME TO base_padroes"))
            db.execute(text("CREATE INDEX idx_base_padroes_user_id ON base_padroes(user_id)"))
            
            db.commit()
            print("✅ user_id agora é NOT NULL")
        except Exception as e:
            print(f"❌ Erro ao tornar user_id NOT NULL: {e}")
            raise
        
        # 8. Verificar integridade final
        print("\n🔍 Verificando integridade final...")
        
        total_padroes = db.execute(text("SELECT COUNT(*) FROM base_padroes")).fetchone()[0]
        padroes_sem_user = db.execute(text("SELECT COUNT(*) FROM base_padroes WHERE user_id IS NULL")).fetchone()[0]
        
        print(f"   Total de padrões: {total_padroes}")
        print(f"   Padrões sem usuário: {padroes_sem_user}")
        
        if padroes_sem_user > 0:
            print("❌ ERRO: Ainda existem padrões sem usuário!")
            return False
        
        # Verificar distribuição por usuário
        print("\n📊 Distribuição de padrões por usuário:")
        for user in usuarios:
            qtd = db.execute(text(f"SELECT COUNT(*) FROM base_padroes WHERE user_id = {user.id}")).fetchone()[0]
            print(f"   {user.nome}: {qtd} padrões")
        
        print("\n" + "="*70)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print(f"\n📦 Backup disponível em: {backup_path}")
        print("\n🎯 Base Padrões agora é totalmente separada por usuário")
        print("   - user_id é obrigatório (NOT NULL)")
        print("   - Cada usuário tem seus próprios padrões")
        print("   - Sem compartilhamento global")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n🔄 Para reverter, use: cp {backup_path} financas.db")
        return False
    
    finally:
        db.close()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("⚠️  ATENÇÃO: Esta migração irá modificar base_padroes")
    print("="*70)
    print("\nMudanças:")
    print("  1. Duplicar padrões globais para cada usuário")
    print("  2. Remover padrões globais")
    print("  3. Tornar user_id obrigatório (NOT NULL)")
    print("  4. Remover coluna 'shared'")
    print("\nUm backup será criado automaticamente.")
    
    resposta = input("\n⚠️  Deseja continuar? (sim/não): ")
    
    if resposta.lower() in ['sim', 's', 'yes', 'y']:
        sucesso = migrate_padroes_to_user_scoped()
        sys.exit(0 if sucesso else 1)
    else:
        print("\n❌ Migração cancelada pelo usuário")
        sys.exit(1)
