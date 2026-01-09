#!/usr/bin/env python3
import pandas as pd

arquivo = '_csvs_historico/extrato_itau.xls'
df = pd.read_excel(arquivo, header=None)

print(f"Analisando: {arquivo}")
print(f"Total de linhas: {len(df)}")
print()

# Procurar linha SAÍDAS FUTURAS
for i in range(len(df)):
    row_values = df.iloc[i].values
    row_str = ' '.join(str(val) for val in row_values if pd.notna(val))
    
    if 'SAÍDA' in row_str.upper() or 'FUTURA' in row_str.upper():
        print(f"Linha {i}: {row_str}")
        # Mostrar próximas 5 linhas
        for j in range(1, 6):
            if i+j < len(df):
                next_row = ' '.join(str(val) for val in df.iloc[i+j].values if pd.notna(val))
                if next_row.strip():
                    print(f"Linha {i+j}: {next_row}")
        break
else:
    print("Não encontrou linha com SAÍDA ou FUTURA")
    print()
    print("Últimas 10 linhas do arquivo:")
    for i in range(max(0, len(df)-10), len(df)):
        row_str = ' '.join(str(val) for val in df.iloc[i].values if pd.notna(val))
        if row_str.strip():
            print(f"Linha {i}: {row_str}")
