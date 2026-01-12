import sqlite3
import hashlib

def normalizar_estabelecimento(texto):
    """Versão simplificada da normalização"""
    import re
    # Remove caracteres especiais, espaços extras, normaliza maiúsculas
    texto = re.sub(r'[^\w\s]', ' ', texto)  # Remove especiais
    texto = re.sub(r'\s+', ' ', texto)      # Remove espaços extras
    return texto.strip().upper()

def gerar_id_original(estabelecimento, valor, total):
    chave = f"{estabelecimento}|{valor:.2f}|{total}"
    return hashlib.md5(chave.encode()).hexdigest()[:16]

conn = sqlite3.connect('app_dev/backend/database/financas_dev.db')
cursor = conn.cursor()

print('\n=== VERIFICANDO IdParcela APÓS CORREÇÃO ===\n')

cursor.execute("""
SELECT 
    data,
    lancamento,
    valor,
    IdParcela,
    ParcelaAtual,
    TotalParcelas,
    EstabelecimentoBase,
    origem_classificacao
FROM preview_transacoes
WHERE session_id = 'session_20260108_205753_1'
AND lancamento LIKE '%VPD TRAVEL%'
ORDER BY valor DESC
""")

results = cursor.fetchall()
for row in results:
    data, lanc, valor, id_parc, parc_atual, total_parc, estab_base, origem = row
    print(f'Data: {data}')
    print(f'  Lançamento: {lanc}')
    print(f'  EstabelecimentoBase: "{estab_base}"')
    print(f'  Valor: R$ {valor:.2f}')
    print(f'  IdParcela: {id_parc}')
    print(f'  Parcela: {parc_atual}/{total_parc}')
    print(f'  Classificação: {origem}')
    
    # Testar normalização manual
    estab_normalizado = normalizar_estabelecimento(estab_base)
    valor_positivo = abs(valor)
    id_esperado = gerar_id_original(estab_normalizado, valor_positivo, total_parc)
    
    print(f'  EstabNormalizado: "{estab_normalizado}"')
    print(f'  Chave: "{estab_normalizado}|{valor_positivo:.2f}|{total_parc}"')
    print(f'  IdEsperado: {id_esperado}')
    print(f'  Match: {"✅" if id_parc == id_esperado else "❌"}')
    
    # Buscar na base_parcelas
    cursor.execute("""
    SELECT id_parcela, grupo_sugerido, subgrupo_sugerido, status
    FROM base_parcelas
    WHERE id_parcela = ?
    """, (id_parc,))
    
    parcela = cursor.fetchone()
    if parcela:
        print(f'  ✅ ENCONTRADA na base_parcelas: {parcela[1]} > {parcela[2]} ({parcela[3]})')
    else:
        print(f'  ❌ NÃO ENCONTRADA na base_parcelas')
    print()

conn.close()