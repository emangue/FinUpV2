"""
Script para reimportar arquivos MP com processador correto
"""
import requests
from pathlib import Path
import time

base_url = "http://localhost:8000"
historico_path = Path("_arquivos_historicos/_csvs_historico")

# Arquivos MP de 2025 (janeiro a dezembro)
arquivos_mp = [
    "MP202501.xlsx",  # Janeiro
    "MP202502.xlsx",  # Fevereiro  
    "MP202503.xlsx",  # Março
    "MP202504.xlsx",  # Abril
    "MP202505.xlsx",  # Maio
    "MP202506.xlsx",  # Junho
    "MP202507.xlsx",  # Julho
    "MP202508.xlsx",  # Agosto
    "MP202509.xlsx",  # Setembro
    "MP202510.xlsx",  # Outubro
    "MP202511.xlsx",  # Novembro
    "MP202512.xlsx",  # Dezembro
]

print("🚀 Iniciando reimportação dos arquivos Mercado Pago...")
print(f"📁 Total de arquivos: {len(arquivos_mp)}\n")

resultados = []

for i, arquivo in enumerate(arquivos_mp, 1):
    file_path = historico_path / arquivo
    
    if not file_path.exists():
        print(f"❌ {i}/12 - Arquivo não encontrado: {arquivo}")
        resultados.append((arquivo, "não encontrado", 0))
        continue
    
    print(f"📤 {i}/12 - Processando: {arquivo}")
    
    try:
        # Fazer upload
        with open(file_path, 'rb') as f:
            files = {'file': (arquivo, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'banco': 'Mercado Pago',
                'tipo_documento': 'extrato'
            }
            
            response = requests.post(
                f"{base_url}/api/v1/upload/raw",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                session_id = result.get('sessionId')
                total_registros = result.get('totalRegistros', 0)
                print(f"   ✅ Upload OK - Session: {session_id}")
                print(f"   📊 Transações processadas: {total_registros}")
                
                # Confirmar importação
                confirm_response = requests.post(
                    f"{base_url}/api/v1/upload/confirm/{session_id}",
                    timeout=30
                )
                
                if confirm_response.status_code == 200:
                    confirm_result = confirm_response.json()
                    importadas = confirm_result.get('transacoes_importadas', 0)
                    print(f"   ✅ Importadas: {importadas} transações\n")
                    resultados.append((arquivo, "sucesso", importadas))
                else:
                    print(f"   ⚠️  Erro ao confirmar: {confirm_response.status_code}\n")
                    resultados.append((arquivo, "erro_confirmação", total_registros))
            else:
                print(f"   ❌ Erro no upload: {result.get('error', 'Desconhecido')}\n")
                resultados.append((arquivo, "erro_upload", 0))
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}\n")
            resultados.append((arquivo, f"http_{response.status_code}", 0))
    
    except Exception as e:
        print(f"   ❌ Exceção: {str(e)}\n")
        resultados.append((arquivo, "exceção", 0))
    
    # Pausa entre uploads
    time.sleep(1)

# Resumo
print("\n" + "="*80)
print("📊 RESUMO DA REIMPORTAÇÃO")
print("="*80)

total_importadas = sum(r[2] for r in resultados if r[1] == "sucesso")
sucesso = sum(1 for r in resultados if r[1] == "sucesso")
erros = len(resultados) - sucesso

print(f"\n✅ Arquivos processados com sucesso: {sucesso}/{len(arquivos_mp)}")
print(f"❌ Arquivos com erro: {erros}")
print(f"📈 Total de transações importadas: {total_importadas}")

if erros > 0:
    print("\n❌ Arquivos com erro:")
    for arquivo, status, _ in resultados:
        if status != "sucesso":
            print(f"   - {arquivo}: {status}")

print("\n" + "="*80)
