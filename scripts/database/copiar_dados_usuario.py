#!/usr/bin/env python3
"""
Script para copiar dados de um usuário para outro com valores aleatorizados.
Copia TODOS os dados relacionados: transações, investimentos, orçamentos, padrões, etc.
"""

import sqlite3
import random
from datetime import datetime
from pathlib import Path

# Configurações
DB_PATH = Path("app_dev/backend/database/financas_dev.db")
USER_ORIGEM = "admin@financas.com"
USER_DESTINO = "teste@email.com"
FATOR_REDUCAO_MIN = 0.10  # 10% do valor original
FATOR_REDUCAO_MAX = 0.30  # 30% do valor original

# Tabelas a copiar (ordem de dependência)
TABELAS_COPIAR = [
    'cartoes',  # Cartões (sem valores, apenas estrutura)
    'base_padroes',  # Padrões de classificação (sem valores)
    'base_parcelas',  # Controle de parcelas (sem valores)
    'journal_entries',  # Transações (COM aleatorização)
    'budget_geral',  # Orçamento geral (COM aleatorização)
    'budget_planning',  # Planejamento (COM aleatorização)
    'investimentos_portfolio',  # Investimentos (COM aleatorização)
    'investimentos_cenarios',  # Cenários de investimento (COM aleatorização)
]

# Colunas de valor (aleatorizar em cada tabela)
COLUNAS_VALOR = {
    'journal_entries': ['Valor', 'ValorPositivo'],
    'budget_geral': ['valor_previsto', 'valor_executado'],
    'budget_planning': ['valor_previsto'],
    'investimentos_portfolio': ['quantidade', 'preco_medio', 'valor_investido', 'valor_atual'],
    'investimentos_cenarios': ['aporte_mensal', 'aporte_inicial'],
}

def copiar_dados_usuario():
    """Copia dados do usuário origem para destino com valores aleatorizados."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Buscar IDs dos usuários
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_ORIGEM,))
        user_origem_id = cursor.fetchone()
        if not user_origem_id:
            print(f"❌ Usuário origem '{USER_ORIGEM}' não encontrado!")
            return
        user_origem_id = user_origem_id[0]
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (USER_DESTINO,))
        user_destino_id = cursor.fetchone()
        if not user_destino_id:
            print(f"❌ Usuário destino '{USER_DESTINO}' não encontrado!")
            return
        user_destino_id = user_destino_id[0]
        
        print(f"✅ Usuário origem: {USER_ORIGEM} (ID: {user_origem_id})")
        print(f"✅ Usuário destino: {USER_DESTINO} (ID: {user_destino_id})")
        
        # 2. Verificar se usuário destino já tem dados
        tem_dados = False
        for tabela in TABELAS_COPIAR:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE user_id = ?", (user_destino_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                tem_dados = True
                break
        
        if tem_dados:
            resposta = input(f"\n⚠️  Usuário destino já tem dados. Deseja deletá-los? (s/N): ")
            if resposta.lower() == 's':
                for tabela in TABELAS_COPIAR:
                    cursor.execute(f"DELETE FROM {tabela} WHERE user_id = ?", (user_destino_id,))
                print(f"🗑️  Dados antigos deletados")
            else:
                print("❌ Operação cancelada")
                return
        
        # 3. Copiar cada tabela
        print(f"\n📊 Copiando dados...")
        total_copiados = {}
        
        for tabela in TABELAS_COPIAR:
            # Buscar dados do usuário origem
            cursor.execute(f"SELECT * FROM {tabela} WHERE user_id = ?", (user_origem_id,))
            colunas = [desc[0] for desc in cursor.description]
            registros = cursor.fetchall()
            
            if not registros:
                print(f"   ⚪ {tabela}: 0 registros")
                continue
            
            copiados = 0
            
            for row in registros:
                dados = dict(zip(colunas, row))
                
                # REMOVER coluna 'id' (auto-increment)
                if 'id' in dados:
                    del dados['id']
                
                # Atualizar user_id
                dados['user_id'] = user_destino_id
                
                # Aleatorizar valores se for tabela com valores
                if tabela in COLUNAS_VALOR:
                    for col_valor in COLUNAS_VALOR[tabela]:
                        if col_valor in dados and dados[col_valor] is not None:
                            valor_original = dados[col_valor]
                            if valor_original != 0:
                                fator = random.uniform(FATOR_REDUCAO_MIN, FATOR_REDUCAO_MAX)
                                novo_valor = round(abs(valor_original) * fator, 2)
                                # Manter o sinal (positivo/negativo)
                                dados[col_valor] = novo_valor if valor_original > 0 else -novo_valor
                
                # Gerar novo IdTransacao/identificador único se existir
                if 'IdTransacao' in dados:
                    id_original = dados['IdTransacao']
                    dados['IdTransacao'] = f"TESTE_{user_destino_id}_{copiados}_{id_original}"
                
                # Gerar novo padrao_num único (base_padroes)
                if 'padrao_num' in dados:
                    dados['padrao_num'] = f"TESTE_{user_destino_id}_{copiados}_{dados['padrao_num']}"
                
                # Gerar novo id_parcela único (base_parcelas)
                if 'id_parcela' in dados:
                    dados['id_parcela'] = f"TESTE_{user_destino_id}_{copiados}_{dados['id_parcela']}"
                
                # Gerar novo balance_id único (investimentos_portfolio)
                if 'balance_id' in dados:
                    dados['balance_id'] = f"TESTE_{user_destino_id}_{copiados}_{dados['balance_id']}"
                
                # Inserir novo registro
                colunas_insert = list(dados.keys())
                valores_insert = list(dados.values())
                placeholders = ','.join(['?'] * len(colunas_insert))
                
                query = f"""
                    INSERT INTO {tabela} ({','.join(colunas_insert)})
                    VALUES ({placeholders})
                """
                
                cursor.execute(query, valores_insert)
                copiados += 1
            
            total_copiados[tabela] = copiados
            print(f"   ✅ {tabela}: {copiados} registros")
        
        # 4. Commit e finalizar
        conn.commit()
        
        print(f"\n✅ Operação concluída com sucesso!")
        print(f"\n📝 Resumo:")
        for tabela, count in total_copiados.items():
            print(f"   - {tabela}: {count} registros")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🔄 COPIAR DADOS DE USUÁRIO COM VALORES ALEATORIZADOS")
    print("=" * 70)
    print(f"\n⚙️  Configurações:")
    print(f"   - Origem: {USER_ORIGEM}")
    print(f"   - Destino: {USER_DESTINO}")
    print(f"   - Valores: {FATOR_REDUCAO_MIN*100}% a {FATOR_REDUCAO_MAX*100}% dos originais")
    print(f"   - Banco: {DB_PATH}")
    print(f"\n📋 Tabelas a copiar:")
    for tabela in TABELAS_COPIAR:
        print(f"   - {tabela}")
    
    resposta = input("\n▶️  Deseja continuar? (s/N): ")
    if resposta.lower() == 's':
        copiar_dados_usuario()
    else:
        print("❌ Operação cancelada")
