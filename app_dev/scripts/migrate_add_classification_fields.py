"""
Script de Migração: Adiciona campos de classificação e banco

Adiciona as colunas:
- banco: Nome do banco (Itaú, BTG, Mercado Pago, Genérico)
- tipodocumento: Tipo do documento (Extrato, Fatura Cartão de Crédito)
- forma_classificacao: Como foi classificada (Automática-BasePadrao, Automática-MarcacaoIA, Semi-Automática, Manual)

Data: 27/12/2025
"""
import sqlite3
import sys

def migrate_database(db_path='financas.db'):
    """Adiciona colunas no banco de dados"""
    
    print("="*60)
    print("MIGRAÇÃO: Adiciona campos de classificação e banco")
    print("="*60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica colunas existentes
        cursor.execute('PRAGMA table_info(journal_entries)')
        colunas = [col[1] for col in cursor.fetchall()]
        
        print(f"\n✓ Conectado ao banco: {db_path}")
        print(f"✓ Colunas existentes: {len(colunas)}")
        
        changes_made = False
        
        # 1. Adiciona coluna banco
        if 'banco' not in colunas:
            print('\n[1/3] Adicionando coluna banco...')
            cursor.execute('ALTER TABLE journal_entries ADD COLUMN banco TEXT')
            print('      ✅ Coluna banco adicionada')
            changes_made = True
        else:
            print('\n[1/3] ⚠️  Coluna banco já existe')
        
        # 2. Adiciona coluna tipodocumento
        if 'tipodocumento' not in colunas:
            print('[2/3] Adicionando coluna tipodocumento...')
            cursor.execute('ALTER TABLE journal_entries ADD COLUMN tipodocumento TEXT')
            print('      ✅ Coluna tipodocumento adicionada')
            changes_made = True
        else:
            print('[2/3] ⚠️  Coluna tipodocumento já existe')
        
        # 3. Adiciona coluna forma_classificacao
        if 'forma_classificacao' not in colunas:
            print('[3/3] Adicionando coluna forma_classificacao...')
            cursor.execute('ALTER TABLE journal_entries ADD COLUMN forma_classificacao TEXT')
            print('      ✅ Coluna forma_classificacao adicionada')
            changes_made = True
        else:
            print('[3/3] ⚠️  Coluna forma_classificacao já existe')
        
        # Cria índices
        if changes_made:
            print('\n📊 Criando índices...')
            try:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_banco ON journal_entries(banco)')
                print('   ✅ idx_banco')
            except Exception as e:
                print(f'   ⚠️  idx_banco: {e}')
            
            try:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_forma_classificacao ON journal_entries(forma_classificacao)')
                print('   ✅ idx_forma_classificacao')
            except Exception as e:
                print(f'   ⚠️  idx_forma_classificacao: {e}')
        
        # Commit
        conn.commit()
        
        # Verifica resultado
        cursor.execute('PRAGMA table_info(journal_entries)')
        colunas_final = [col[1] for col in cursor.fetchall()]
        
        print(f"\n✅ Migração concluída!")
        print(f"   Total de colunas: {len(colunas_final)}")
        
        if changes_made:
            print("\n📋 Colunas adicionadas:")
            if 'banco' in colunas_final and 'banco' not in colunas:
                print("   • banco")
            if 'tipodocumento' in colunas_final and 'tipodocumento' not in colunas:
                print("   • tipodocumento")
            if 'forma_classificacao' in colunas_final and 'forma_classificacao' not in colunas:
                print("   • forma_classificacao")
        else:
            print("\n   Nenhuma mudança necessária - todas as colunas já existem")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na migração: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'financas.db'
    success = migrate_database(db_path)
    sys.exit(0 if success else 1)
