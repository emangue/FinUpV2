#!/usr/bin/env python3
"""
Script para copiar dados de investimentos do admin para o user teste
Com valores aleatórios menores (10-30% dos originais)
Incluindo tabelas com foreign keys
"""

import sqlite3
import random
from datetime import datetime

# Configurações
DB_PATH = "app_dev/backend/database/financas_dev.db"
USER_ID_ORIGEM = 1  # admin
USER_ID_DESTINO = 4  # teste@email.com
FATOR_REDUCAO_MIN = 0.10  # 10% mínimo
FATOR_REDUCAO_MAX = 0.30  # 30% máximo

# Tabelas de investimentos a copiar (ORDEM IMPORTA - pais antes de filhos)
TABELAS = {
    'investimentos_portfolio': {
        'id_col': 'id',
        'colunas_randomizar': ['quantidade', 'preco_medio', 'total_investido'],
        'mapear_ids': None  # Tabela pai
    },
    'investimentos_cenarios': {
        'id_col': 'id',
        'colunas_randomizar': ['retorno_esperado', 'retorno_pessimista', 'retorno_otimista'],
        'mapear_ids': None  # Tabela pai
    },
    'investimentos_planejamento': {
        'id_col': 'id',
        'colunas_randomizar': ['meta_aporte_mensal', 'meta_patrimonio', 'aporte_realizado', 'patrimonio_realizado'],
        'mapear_ids': None
    },
    'investimentos_historico': {
        'id_col': 'id',
        'fk_col': 'investimento_id',  # FK para portfolio
        'fk_tabela': 'investimentos_portfolio',
        'colunas_randomizar': ['quantidade', 'valor_unitario', 'valor_total', 'aporte_mes', 'rendimento_mes', 'rendimento_acumulado'],
        'mapear_ids': 'portfolio_map'  # Mapeia IDs do portfolio
    },
    'investimentos_aportes_extraordinarios': {
        'id_col': 'id',
        'fk_col': 'cenario_id',  # FK para cenarios
        'fk_tabela': 'investimentos_cenarios',
        'colunas_randomizar': ['valor'],
        'mapear_ids': 'cenarios_map'  # Mapeia IDs dos cenarios
    }
}

def randomizar_valor(valor_original):
    """Retorna valor entre 10-30% do original"""
    if valor_original is None or valor_original == 0:
        return valor_original
    
    fator = random.uniform(FATOR_REDUCAO_MIN, FATOR_REDUCAO_MAX)
    return round(valor_original * fator, 2)

def copiar_investimentos():
    """Copia todos os dados de investimentos com valores randomizados"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"\n{'='*70}")
    print(f"COPIAR INVESTIMENTOS: user_id {USER_ID_ORIGEM} → {USER_ID_DESTINO}")
    print(f"Valores: {FATOR_REDUCAO_MIN*100:.0f}%-{FATOR_REDUCAO_MAX*100:.0f}% dos originais")
    print(f"{'='*70}\n")
    
    total_copiados = 0
    
    # Mapas de IDs antigos → novos (para foreign keys)
    id_maps = {
        'portfolio_map': {},  # portfolio: old_id → new_id
        'cenarios_map': {}    # cenarios: old_id → new_id
    }
    
    try:
        # 1. Limpar dados antigos do user_id_destino
        print("🗑️  LIMPANDO DADOS ANTIGOS:\n")
        for tabela in TABELAS.keys():
            cursor.execute(f"DELETE FROM {tabela} WHERE user_id = ?", (USER_ID_DESTINO,))
            deletados = cursor.rowcount
            if deletados > 0:
                print(f"  • {tabela}: {deletados} registros removidos")
        
        conn.commit()
        print()
        
        # 2. Copiar dados com valores randomizados
        print("📋 COPIANDO DADOS:\n")
        for tabela, config in TABELAS.items():
            # Buscar dados originais
            cursor.execute(f"SELECT * FROM {tabela} WHERE user_id = ?", (USER_ID_ORIGEM,))
            registros = cursor.fetchall()
            
            if not registros:
                print(f"  ⚠️  {tabela}: Sem dados para copiar")
                continue
            
            # Pegar colunas
            id_col = config['id_col']
            colunas_randomizar = config['colunas_randomizar']
            
            # Copiar cada registro
            copiados = 0
            for reg in registros:
                novo_registro = dict(reg)
                old_id = novo_registro[id_col]
                
                # Alterar user_id
                novo_registro['user_id'] = USER_ID_DESTINO
                
                # Se for portfolio, gerar novo balance_id único
                if tabela == 'investimentos_portfolio' and 'balance_id' in novo_registro:
                    # Prefixar com TESTE_ para garantir unicidade
                    novo_registro['balance_id'] = f"TESTE_{USER_ID_DESTINO}_{old_id}_{novo_registro['balance_id']}"
                
                # Se tiver foreign key, mapear para o novo ID
                if 'fk_col' in config and config['mapear_ids']:
                    fk_col = config['fk_col']
                    map_name = config['mapear_ids']
                    old_fk_id = novo_registro[fk_col]
                    
                    if old_fk_id in id_maps[map_name]:
                        novo_registro[fk_col] = id_maps[map_name][old_fk_id]
                    else:
                        print(f"    ⚠️  FK {fk_col}={old_fk_id} não encontrada no mapa {map_name}, pulando...")
                        continue  # Pular este registro
                
                # Randomizar valores
                for col in colunas_randomizar:
                    if col in novo_registro and novo_registro[col] is not None:
                        novo_registro[col] = randomizar_valor(novo_registro[col])
                
                # Remover ID original (será auto-incrementado)
                del novo_registro[id_col]
                
                # Insert
                colunas_insert = list(novo_registro.keys())
                placeholders = ','.join(['?'] * len(colunas_insert))
                valores = [novo_registro[col] for col in colunas_insert]
                
                sql = f"INSERT INTO {tabela} ({','.join(colunas_insert)}) VALUES ({placeholders})"
                cursor.execute(sql, valores)
                
                # Pegar o novo ID e guardar no mapa (se for tabela pai)
                new_id = cursor.lastrowid
                if config['mapear_ids'] is None:
                    if tabela == 'investimentos_portfolio':
                        id_maps['portfolio_map'][old_id] = new_id
                    elif tabela == 'investimentos_cenarios':
                        id_maps['cenarios_map'][old_id] = new_id
                
                copiados += 1
            
            conn.commit()
            total_copiados += copiados
            print(f"  ✅ {tabela}: {copiados} registros copiados")
        
        print(f"\n{'='*70}")
        print(f"RESULTADO: {total_copiados} registros copiados com sucesso!")
        print(f"{'='*70}\n")
        
        # 3. Estatísticas finais
        print("📊 ESTATÍSTICAS POR TABELA:\n")
        for tabela in TABELAS.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE user_id = ?", (USER_ID_DESTINO,))
            count = cursor.fetchone()[0]
            print(f"  • {tabela}: {count} registros")
        
        # 4. Exemplos de valores randomizados
        print(f"\n💰 EXEMPLOS DE VALORES RANDOMIZADOS:\n")
        
        # Portfolio
        cursor.execute(f"""
            SELECT ticker, quantidade, total_investido 
            FROM investimentos_portfolio 
            WHERE user_id = ? 
            LIMIT 3
        """, (USER_ID_DESTINO,))
        print("  📊 Portfolio:")
        for row in cursor.fetchall():
            print(f"      {row[0]}: {row[1]:.2f} unidades, R$ {row[2]:,.2f}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    copiar_investimentos()
