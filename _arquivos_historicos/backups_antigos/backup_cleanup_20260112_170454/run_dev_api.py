"""
Servidor de desenvolvimento - Backend API
python run_dev_api.py
"""
from app_dev.backend import create_app_dev

app = create_app_dev()

if __name__ == '__main__':
    print("=" * 60)
    print("  🚀 Backend API DEV - Sistema Financeiro v4.0.0-dev")
    print("=" * 60)
    print("  📍 API: http://localhost:5002/api/v1")
    print("  ❤️  Health: http://localhost:5002/api/health")
    print("  📚 Endpoints:")
    print("     - POST /api/v1/auth/login")
    print("     - POST /api/v1/auth/register")
    print("     - GET /api/v1/dashboard/metrics")
    print("     - GET /api/v1/transactions")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
