#!/usr/bin/env python3
"""
Aplica nova base_padroes (substitui a antiga pela nova validada)
"""

import sys
sys.path.insert(0, 'app_dev/backend')

from app.core.database import engine
from sqlalchemy import text
from datetime import datetime

def backup_base_antiga():
    """Faz backup da base antiga"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_table = f"base_padroes_backup_{timestamp}"
    
    print(f"💾 Criando backup: {backup_table}")
    
    with engine.connect() as conn:
        # Criar tabela de backup
        conn.execute(text(f"""
            CREATE TABLE {backup_table} AS 
            SELECT * FROM base_padroes
        """))
        
        # Contar registros
        result = conn.execute(text(f"SELECT COUNT(*) FROM {backup_table}")).fetchone()
        conn.commit()
        
        print(f"✅ Backup criado com {result[0]} registros")
        return backup_table

def aplicar_nova_base():
    """Substitui base antiga pela nova"""
    print("\n🔄 Aplicando nova base_padroes...")
    
    with engine.connect() as conn:
        # 1. Deletar registros antigos
        print("  1. Deletando registros antigos...")
        conn.execute(text("DELETE FROM base_padroes WHERE user_id = 1"))
        conn.commit()
        print("  ✅ Registros antigos deletados")
        
        # 2. Copiar novos registros
        print("  2. Copiando novos padrões...")
        conn.execute(text("""
            INSERT INTO base_padroes (
                user_id, padrao_estabelecimento, padrao_num, contagem,
                valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                tipo_gasto_sugerido, categoria_geral_sugerida, faixa_valor, segmentado, exemplos, data_criacao, status
            )
            SELECT 
                user_id, padrao_estabelecimento, padrao_num, contagem,
                valor_medio, valor_min, valor_max, desvio_padrao, coef_variacao,
                percentual_consistencia, confianca, grupo_sugerido, subgrupo_sugerido,
                tipo_gasto_sugerido, categoria_geral_sugerida, faixa_valor, segmentado, exemplos, data_criacao, status
            FROM base_padroes_new
            WHERE user_id = 1
        """))
        
        # Contar registros copiados
        result = conn.execute(text("SELECT COUNT(*) FROM base_padroes WHERE user_id = 1")).fetchone()
        conn.commit()
        
        print(f"  ✅ {result[0]} padrões copiados")
        
        # 3. Dropar tabela temporária
        print("  3. Removendo tabela temporária...")
        conn.execute(text("DROP TABLE base_padroes_new"))
        conn.commit()
        print("  ✅ Tabela temporária removida")
        
        return result[0]

def validar_aplicacao():
    """Valida que aplicação foi bem sucedida"""
    print("\n✅ Validando aplicação...")
    
    with engine.connect() as conn:
        # Contar por formato
        total = conn.execute(text("""
            SELECT COUNT(*) FROM base_padroes WHERE user_id = 1
        """)).fetchone()[0]
        
        brackets = conn.execute(text("""
            SELECT COUNT(*) FROM base_padroes 
            WHERE user_id = 1 AND padrao_estabelecimento LIKE '% [%]%'
        """)).fetchone()[0]
        
        pipe_faixa = conn.execute(text("""
            SELECT COUNT(*) FROM base_padroes 
            WHERE user_id = 1 AND padrao_estabelecimento LIKE '%|FAIXA:%'
        """)).fetchone()[0]
        
        print(f"\n📊 BASE FINAL:")
        print(f"  Total de padrões: {total}")
        print(f"  Formato [ ] (correto): {brackets}")
        print(f"  Formato |FAIXA: (antigo): {pipe_faixa}")
        
        if pipe_faixa > 0:
            print(f"\n⚠️  ATENÇÃO: Ainda existem {pipe_faixa} padrões no formato antigo!")
            print("  Execute nova regeneração para corrigir")
        else:
            print("\n✅ Todos os padrões estão no formato correto!")

if __name__ == "__main__":
    print("🔄 APLICAÇÃO DE NOVA BASE_PADROES")
    print("=" * 80)
    
    # Confirmar com usuário
    resposta = input("\n⚠️  Tem certeza que deseja substituir a base atual? (SIM/não): ")
    
    if resposta.upper() != "SIM":
        print("\n❌ Operação cancelada")
        sys.exit(0)
    
    try:
        # 1. Fazer backup
        print("\n1️⃣  Backup da base antiga...")
        backup_table = backup_base_antiga()
        
        # 2. Aplicar nova base
        print("\n2️⃣  Aplicando nova base...")
        total_padroes = aplicar_nova_base()
        
        # 3. Validar
        print("\n3️⃣  Validando...")
        validar_aplicacao()
        
        print("\n" + "=" * 80)
        print("✅ APLICAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print(f"\n📊 Resumo:")
        print(f"  - {total_padroes} padrões na nova base")
        print(f"  - Backup salvo em: {backup_table}")
        print(f"\n💡 Para reverter: restaure de {backup_table}")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n⚠️  Banco pode estar em estado inconsistente!")
        print(f"  Restaure do backup: {backup_table if 'backup_table' in locals() else 'N/A'}")
        sys.exit(1)
