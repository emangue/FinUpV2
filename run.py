"""
Ponto de entrada da aplicação Flask
"""
from app import create_app, __version__
import re

app = create_app()

if __name__ == '__main__':
    # Detecção de estado da versão
    version_parts = __version__.split('-')
    base_version = version_parts[0]
    status = version_parts[1] if len(version_parts) > 1 else 'stable'
    
    # Banner com versão
    print("\n" + "="*60)
    print("  Sistema de Gestão Financeira")
    
    if status == 'dev':
        print(f"  Versão: {__version__} 🟡 (DESENVOLVIMENTO)")
        print("  ⚠️  AVISO: Código em desenvolvimento ativo")
        print("  ⚠️  Não commitar neste estado!")
    elif status == 'test':
        print(f"  Versão: {__version__} 🟠 (TESTE)")
        print("  🧪 Versão em fase de testes")
    else:
        print(f"  Versão: {__version__} 🟢 (ESTÁVEL)")
    
    print("="*60 + "\n")
    
    print("🚀 Iniciando aplicação modularizada...")
    print("📍 Acesse: http://localhost:5001")
    print("📂 Dashboard: http://localhost:5001/dashboard/")
    print("📤 Upload: http://localhost:5001/upload/")
    print("⚙️  Admin: http://localhost:5001/admin/marcacoes")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
