#!/usr/bin/env python3
"""
FASE 2: Testes ISOLADOS dos helper functions

Testa as funções de categorias_helper.py SEM afetar o sistema
- Valida que base_grupos_config foi criada corretamente
- Valida que helpers retornam valores esperados
- 100% isolado (não modifica dados)
"""

import sys
from pathlib import Path

# Adiciona app_dev/backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import sqlite3
from app.core.categorias_helper import (
    determinar_tipo_gasto_via_config,
    determinar_categoria_geral_via_config,
    get_todos_grupos_config
)

DB_PATH = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db")


def test_helper_functions():
    """Testa todos os helpers isoladamente"""
    
    print("=" * 80)
    print("FASE 2: TESTE DE HELPER FUNCTIONS")
    print("=" * 80)
    print()
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    
    # Verificar que tabela existe
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='base_grupos_config'
    """)
    if not cursor.fetchone():
        print("❌ ERRO: Tabela base_grupos_config não existe!")
        print("   Execute primeiro: python scripts/migrate_create_base_grupos_config.py")
        return False
    
    print("✅ Tabela base_grupos_config encontrada\n")
    
    # TESTE 1: Grupos Ajustáveis
    print("🧪 TESTE 1: Grupos Ajustáveis")
    print("-" * 80)
    
    grupos_ajustaveis = ['Viagens', 'Uber', 'Delivery', 'Casa', 'Entretenimento', 
                         'Supermercado', 'Roupas', 'Presentes', 'Assinaturas', 'Carro']
    
    erros = 0
    for grupo in grupos_ajustaveis:
        tipo = determinar_tipo_gasto_via_config(conn, grupo)
        cat = determinar_categoria_geral_via_config(conn, grupo)
        
        if tipo != 'Ajustável':
            print(f"  ❌ {grupo:<20} → TipoGasto={tipo} (esperado: Ajustável)")
            erros += 1
        elif cat != 'Despesa':
            print(f"  ❌ {grupo:<20} → Categoria={cat} (esperado: Despesa)")
            erros += 1
        else:
            print(f"  ✅ {grupo:<20} → {tipo:<15} | {cat}")
    
    if erros == 0:
        print(f"\n✅ TESTE 1 PASSOU: {len(grupos_ajustaveis)} grupos ajustáveis OK\n")
    else:
        print(f"\n❌ TESTE 1 FALHOU: {erros} erros\n")
        return False
    
    # TESTE 2: Grupos Fixos
    print("🧪 TESTE 2: Grupos Fixos")
    print("-" * 80)
    
    grupos_fixos = ['Moradia', 'Educação', 'Saúde']
    
    erros = 0
    for grupo in grupos_fixos:
        tipo = determinar_tipo_gasto_via_config(conn, grupo)
        cat = determinar_categoria_geral_via_config(conn, grupo)
        
        if tipo != 'Fixo':
            print(f"  ❌ {grupo:<20} → TipoGasto={tipo} (esperado: Fixo)")
            erros += 1
        elif cat != 'Despesa':
            print(f"  ❌ {grupo:<20} → Categoria={cat} (esperado: Despesa)")
            erros += 1
        else:
            print(f"  ✅ {grupo:<20} → {tipo:<15} | {cat}")
    
    if erros == 0:
        print(f"\n✅ TESTE 2 PASSOU: {len(grupos_fixos)} grupos fixos OK\n")
    else:
        print(f"\n❌ TESTE 2 FALHOU: {erros} erros\n")
        return False
    
    # TESTE 3: Receitas
    print("🧪 TESTE 3: Grupos de Receita")
    print("-" * 80)
    
    grupos_receita = ['Salário', 'Outros']
    
    erros = 0
    for grupo in grupos_receita:
        tipo = determinar_tipo_gasto_via_config(conn, grupo)
        cat = determinar_categoria_geral_via_config(conn, grupo)
        
        if tipo != 'Receita':
            print(f"  ❌ {grupo:<20} → TipoGasto={tipo} (esperado: Receita)")
            erros += 1
        elif cat != 'Receita':
            print(f"  ❌ {grupo:<20} → Categoria={cat} (esperado: Receita)")
            erros += 1
        else:
            print(f"  ✅ {grupo:<20} → {tipo:<15} | {cat}")
    
    if erros == 0:
        print(f"\n✅ TESTE 3 PASSOU: {len(grupos_receita)} grupos de receita OK\n")
    else:
        print(f"\n❌ TESTE 3 FALHOU: {erros} erros\n")
        return False
    
    # TESTE 4: Investimentos
    print("🧪 TESTE 4: Investimentos")
    print("-" * 80)
    
    tipo = determinar_tipo_gasto_via_config(conn, 'Aplicações')
    cat = determinar_categoria_geral_via_config(conn, 'Aplicações')
    
    if tipo == 'Investimentos' and cat == 'Investimentos':
        print(f"  ✅ Aplicações        → {tipo:<15} | {cat}")
        print("\n✅ TESTE 4 PASSOU: Investimentos OK\n")
    else:
        print(f"  ❌ Aplicações → TipoGasto={tipo}, Categoria={cat}")
        print("     Esperado: TipoGasto=Investimentos, Categoria=Investimentos\n")
        return False
    
    # TESTE 5: Transferência
    print("🧪 TESTE 5: Transferência")
    print("-" * 80)
    
    tipo = determinar_tipo_gasto_via_config(conn, 'Movimentações')
    cat = determinar_categoria_geral_via_config(conn, 'Movimentações')
    
    if tipo == 'Transferência' and cat == 'Transferência':
        print(f"  ✅ Movimentações     → {tipo:<15} | {cat}")
        print("\n✅ TESTE 5 PASSOU: Transferência OK\n")
    else:
        print(f"  ❌ Movimentações → TipoGasto={tipo}, Categoria={cat}")
        print("     Esperado: TipoGasto=Transferência, Categoria=Transferência\n")
        return False
    
    # TESTE 6: Grupo Inexistente
    print("🧪 TESTE 6: Grupo Inexistente")
    print("-" * 80)
    
    tipo = determinar_tipo_gasto_via_config(conn, 'GrupoQueNaoExiste')
    cat = determinar_categoria_geral_via_config(conn, 'GrupoQueNaoExiste')
    
    if tipo is None and cat is None:
        print(f"  ✅ GrupoQueNaoExiste → None | None")
        print("\n✅ TESTE 6 PASSOU: Grupo inexistente retorna None\n")
    else:
        print(f"  ❌ GrupoQueNaoExiste → TipoGasto={tipo}, Categoria={cat}")
        print("     Esperado: ambos None\n")
        return False
    
    # TESTE 7: Valores None/Empty
    print("🧪 TESTE 7: Valores None/Empty")
    print("-" * 80)
    
    tipo_none = determinar_tipo_gasto_via_config(conn, None)
    tipo_empty = determinar_tipo_gasto_via_config(conn, '')
    cat_none = determinar_categoria_geral_via_config(conn, None)
    cat_empty = determinar_categoria_geral_via_config(conn, '')
    
    if tipo_none is None and tipo_empty is None and cat_none is None and cat_empty is None:
        print(f"  ✅ None/Empty        → None | None")
        print("\n✅ TESTE 7 PASSOU: Valores None/Empty retornam None\n")
    else:
        print(f"  ❌ None → TipoGasto={tipo_none}, Categoria={cat_none}")
        print(f"  ❌ Empty → TipoGasto={tipo_empty}, Categoria={cat_empty}")
        print("     Esperado: todos None\n")
        return False
    
    # TESTE 8: get_todos_grupos_config
    print("🧪 TESTE 8: get_todos_grupos_config()")
    print("-" * 80)
    
    todos_grupos = get_todos_grupos_config(conn)
    
    if len(todos_grupos) == 17:
        print(f"  ✅ Retornou 17 grupos")
        
        # Validar estrutura
        primeiro = todos_grupos[0]
        if 'nome_grupo' in primeiro and 'tipo_gasto_padrao' in primeiro and 'categoria_geral' in primeiro:
            print(f"  ✅ Estrutura correta (dict com 3 chaves)")
            
            # Mostrar primeiros 3
            print(f"\n  Primeiros 3 grupos:")
            for grupo in todos_grupos[:3]:
                print(f"    - {grupo['nome_grupo']:<20} {grupo['tipo_gasto_padrao']:<15} {grupo['categoria_geral']}")
            
            print("\n✅ TESTE 8 PASSOU: get_todos_grupos_config() OK\n")
        else:
            print(f"  ❌ Estrutura incorreta: {primeiro}")
            return False
    else:
        print(f"  ❌ Retornou {len(todos_grupos)} grupos (esperado: 17)")
        return False
    
    # RESUMO FINAL
    print("=" * 80)
    print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 80)
    print()
    print("✅ Fase 2 concluída:")
    print("   - Helper functions criadas: categorias_helper.py")
    print("   - 8 testes passaram (17 grupos validados)")
    print("   - Sistema continua funcionando normalmente")
    print()
    print("⏭️  PRÓXIMO PASSO: Fase 3 - Migração Journal Entries")
    print("   Script: migrate_journal_entries_tipo_gasto.py")
    print("   ⚠️  ATENÇÃO: Fase 3 modifica dados (criar backup antes!)")
    print()
    
    conn.close()
    return True


if __name__ == "__main__":
    try:
        success = test_helper_functions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
