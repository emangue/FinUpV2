"""
Ponto de entrada da aplicação Flask
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Iniciando aplicação modularizada...")
    print("📍 Acesse: http://localhost:5001")
    print("📂 Dashboard: http://localhost:5001/dashboard/")
    print("📤 Upload: http://localhost:5001/upload/")
    print("⚙️  Admin: http://localhost:5001/admin/marcacoes")
    app.run(debug=True, host='0.0.0.0', port=5001)
