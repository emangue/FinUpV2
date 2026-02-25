#!/usr/bin/env python3
"""
FASE 3.1: ADICIONAR GRUPOS FALTANTES EM base_grupos_config
===========================================================

Este script adiciona os 9 grupos que existem em journal_entries
mas não estão em base_grupos_config (dos 21 grupos únicos).

GRUPOS FALTANTES:
- Alimentação → Ajustável + Despesa (delivery, restaurantes, supermercado)
- Transporte → Ajustável + Despesa (uber, transporte público)
- Doações → Ajustável + Despesa
- Serviços → Ajustável + Despesa
- Tecnologia → Ajustável + Despesa
- MeLi + Amazon → Ajustável + Despesa (compras online)
- Limpeza → Fixo + Despesa (produtos de limpeza recorrentes)
- Fatura → Transferência + Transferência (pagamento de fatura é movimentação)
- Transferência Entre Contas → Transferência + Transferência
"""

import sys
import sqlite3
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"

# Grupos faltantes a adicionar
GRUPOS_FALTANTES = [
    ('Alimentação', 'Ajustável', 'Despesa'),
    ('Transporte', 'Ajustável', 'Despesa'),
    ('Doações', 'Ajustável', 'Despesa'),
    ('Serviços', 'Ajustável', 'Despesa'),
    ('Tecnologia', 'Ajustável', 'Despesa'),
    ('MeLi + Amazon', 'Ajustável', 'Despesa'),
    ('Limpeza', 'Fixo', 'Despesa'),
    # Fatura consolidado em Transferência Entre Contas
    ('Transferência Entre Contas', 'Transferência', 'Transferência'),
]


def main():
    """Adiciona grupos faltantes em base_grupos_config"""
    print("="*80)
    print("FASE 3.1: ADICIONAR GRUPOS FALTANTES EM base_grupos_config")
    print("="*80)
    print(f"Banco: {DB_PATH}\n")
    
    if not DB_PATH.exists():
        print(f"❌ ERRO: Banco de dados não encontrado: {DB_PATH}")
        return 1
    
    # Conectar
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar grupos atuais
        cursor.execute("SELECT COUNT(*) FROM base_grupos_config")
        total_antes = cursor.fetchone()[0]
        print(f"📊 Grupos atuais em base_grupos_config: {total_antes}")
        
        # 2. Listar grupos que serão adicionados
        print(f"\n📝 Grupos a adicionar ({len(GRUPOS_FALTANTES)}):")
        print("-" * 80)
        
        for nome_grupo, tipo_gasto, categoria_geral in GRUPOS_FALTANTES:
            # Contar quantas transações têm esse grupo
            cursor.execute("""
                SELECT COUNT(*) 
                FROM journal_entries 
                WHERE GRUPO = ?
            """, (nome_grupo,))
            count = cursor.fetchone()[0]
            
            print(f"   {nome_grupo:30s} → {tipo_gasto:15s} | {categoria_geral:15s} ({count:5,} transações)")
        
        # 3. Confirmação
        print("\n" + "="*80)
        resposta = input("Confirma adição destes grupos? (sim/não): ").strip().lower()
        
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Operação cancelada pelo usuário")
            return 1
        
        # 4. Inserir grupos
        print("\n🚀 Inserindo grupos...")
        
        adicionados = 0
        for nome_grupo, tipo_gasto, categoria_geral in GRUPOS_FALTANTES:
            try:
                cursor.execute("""
                    INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral)
                    VALUES (?, ?, ?)
                """, (nome_grupo, tipo_gasto, categoria_geral))
                print(f"   ✅ {nome_grupo:30s} adicionado")
                adicionados += 1
            except sqlite3.IntegrityError:
                print(f"   ⚠️  {nome_grupo:30s} já existe (pulando)")
        
        # 5. Commit
        conn.commit()
        print(f"\n✅ {adicionados} grupos adicionados com sucesso")
        
        # 6. Validar total
        cursor.execute("SELECT COUNT(*) FROM base_grupos_config")
        total_depois = cursor.fetchone()[0]
        
        print("\n" + "="*80)
        print("📊 VALIDAÇÃO FINAL")
        print("="*80)
        print(f"   Grupos antes:  {total_antes}")
        print(f"   Grupos depois: {total_depois}")
        print(f"   Adicionados:   {adicionados}")
        
        # 7. Mostrar distribuição por tipo
        print("\n📊 Distribuição por TipoGasto:")
        print("-" * 80)
        
        cursor.execute("""
            SELECT tipo_gasto_padrao, COUNT(*) as total
            FROM base_grupos_config
            GROUP BY tipo_gasto_padrao
            ORDER BY total DESC
        """)
        
        for tipo, count in cursor.fetchall():
            print(f"   {tipo:20s} → {count:2d} grupos")
        
        print("\n✅ base_grupos_config atualizado com sucesso!")
        print("\n⏭️  PRÓXIMO PASSO: Executar migração da Fase 3")
        print("   Script: python scripts/migrate_journal_entries_tipo_gasto.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
