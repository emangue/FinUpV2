"""
Script para corrigir datas invertidas do Mercado Pago
Problema: Datas foram importadas como MM/DD/YYYY quando deveriam ser DD/MM/YYYY
"""
import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path('app_dev/backend/database/financas_dev.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔍 Analisando transações do Mercado Pago com datas invertidas...")

# Buscar todas as transações MP com arquivo_origem = 'dado_historico'
cursor.execute("""
    SELECT id, Data, Estabelecimento, Valor
    FROM journal_entries
    WHERE banco_origem = 'MP' AND arquivo_origem = 'dado_historico'
    ORDER BY id
""")

transacoes = cursor.fetchall()
print(f"\n📊 Total de transações MP históricas: {len(transacoes)}")

# Analisar padrões de data
datas_corretas = 0
datas_invertidas = 0
erros = 0

correcoes = []

for id_trans, data, estab, valor in transacoes:
    try:
        # Data atual no banco: pode estar como DD/MM/YYYY ou MM/DD/YYYY
        partes = data.split('/')
        if len(partes) != 3:
            print(f"❌ Formato inválido: {data}")
            erros += 1
            continue
        
        dia, mes, ano = partes
        dia_int = int(dia)
        mes_int = int(mes)
        
        # Se dia > 12, está correto (DD/MM/YYYY)
        if dia_int > 12:
            datas_corretas += 1
            continue
        
        # Se mês > 12, está invertido (MM/DD/YYYY)
        if mes_int > 12:
            # Inverter: MM/DD/YYYY → DD/MM/YYYY
            data_correta = f"{mes}/{dia}/{ano}"
            correcoes.append((data_correta, id_trans))
            datas_invertidas += 1
        else:
            # Ambíguo (ambos <= 12) - precisamos de lógica adicional
            # Por padrão, vamos considerar que se está em 'dado_historico' e ano é 2024-2025,
            # provavelmente está invertido (dados foram importados errados)
            # Validação: se mês seria inválido após inversão, não inverter
            if dia_int <= 12 and mes_int <= 12:
                # Inverter por padrão para dados históricos MP
                data_correta = f"{mes}/{dia}/{ano}"
                correcoes.append((data_correta, id_trans))
                datas_invertidas += 1
            else:
                datas_corretas += 1
    
    except Exception as e:
        print(f"❌ Erro ao processar data '{data}': {e}")
        erros += 1

print(f"\n📈 Análise:")
print(f"   ✅ Datas corretas: {datas_corretas}")
print(f"   🔄 Datas invertidas (a corrigir): {datas_invertidas}")
print(f"   ❌ Erros: {erros}")

if correcoes:
    print(f"\n💾 Aplicando {len(correcoes)} correções...")
    
    # Mostrar amostras
    print("\n📋 Amostras de correções:")
    for i, (nova_data, id_trans) in enumerate(correcoes[:10], 1):
        cursor.execute("SELECT Data, Estabelecimento FROM journal_entries WHERE id = ?", (id_trans,))
        data_antiga, estab = cursor.fetchone()
        print(f"   {i}. ID {id_trans}: {data_antiga} → {nova_data} | {estab[:50]}")
    
    if len(correcoes) > 10:
        print(f"   ... e mais {len(correcoes) - 10} correções")
    
    resposta = input("\n⚠️  Deseja aplicar as correções? (s/N): ").strip().lower()
    
    if resposta == 's':
        for nova_data, id_trans in correcoes:
            cursor.execute("UPDATE journal_entries SET Data = ? WHERE id = ?", (nova_data, id_trans))
        
        conn.commit()
        print(f"✅ {len(correcoes)} transações corrigidas com sucesso!")
        
        # Validar amostra
        print("\n🔍 Validando correções (amostra):")
        for nova_data, id_trans in correcoes[:5]:
            cursor.execute("SELECT Data, Estabelecimento FROM journal_entries WHERE id = ?", (id_trans,))
            data_atual, estab = cursor.fetchone()
            print(f"   ID {id_trans}: {data_atual} | {estab[:50]}")
    else:
        print("❌ Operação cancelada")
else:
    print("\n✅ Nenhuma correção necessária!")

conn.close()
