import pandas as pd
import unicodedata

def _remove_accents(text):
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

file_path = "/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/_csvs_historico/fatura_itau-202511.csv"

# Tentar diferentes encodings
for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
    try:
        df = pd.read_csv(file_path, encoding=encoding, sep=',')
        print(f"\n✅ Sucesso com {encoding}")
        print(f"Colunas originais: {df.columns.tolist()}")
        print(f"Primeira linha (row 0):")
        print(df.iloc[0])
        
        # Testar primeira linha
        row_str = ' '.join(str(val).lower() for val in df.iloc[0].values if pd.notna(val))
        row_str_norm = _remove_accents(row_str)
        print(f"\nString normalizada da linha 0: {row_str_norm}")
        print(f"Contém 'data': {'data' in row_str_norm}")
        print(f"Contém 'lancamento': {'lancamento' in row_str_norm}")
        break
    except Exception as e:
        print(f"❌ {encoding}: {e}")
