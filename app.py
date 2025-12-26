"""
Entry Point - Inicia servidor Flask
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Sistema de Gestão Financeira")
    print("="*50)
    print("📍 Acesse: http://localhost:5001")
    print("📂 Dashboard: http://localhost:5001/dashboard/")
    print("📤 Upload: http://localhost:5001/upload/")
    print("⚙️  Admin: http://localhost:5001/admin/marcacoes")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
