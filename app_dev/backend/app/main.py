"""
FastAPI Main Application - Arquitetura Modular em Domínios
Com Autenticação JWT e Segurança
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do .env
# IMPORTANTE: Fazer isso ANTES de importar settings
load_dotenv()

from .core.config import settings
from .core.database import engine, Base

# Import models para SQLAlchemy resolver relationships
from .domains.upload.history_models import UploadHistory  # CRITICAL: importar antes dos routers
from .domains.users.models import RefreshToken  # IMPORTANT: criar tabela refresh_tokens

# Domínios isolados (arquitetura DDD)
from .domains.transactions.router import router as transactions_router
from .domains.users.router import router as users_router
from .domains.categories.router import router as categories_router
from .domains.cards.router import router as cards_router
from .domains.upload.router import router as upload_router
from .domains.dashboard.router import router as dashboard_router
from .domains.compatibility.router import router as compatibility_router
from .domains.exclusoes.router import router as exclusoes_router
from .domains.budget.router import router as budget_router

# Cria app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para Sistema de Finanças Pessoais - Arquitetura Modular com JWT",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS - Permite Next.js se conectar COM cookies (allow_credentials=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,  # IMPORTANTE: Permite envio de cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"]  # IMPORTANTE: Expõe header de cookie
)

# Routers Modularizados (arquitetura DDD - Domain-Driven Design)
app.include_router(users_router, prefix="/api/v1")  # Auth: /api/v1/auth/*, Users: /api/v1/users/*
app.include_router(transactions_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(categories_router, prefix="/api/v1", tags=["Categories"])
app.include_router(cards_router, prefix="/api/v1", tags=["Cards"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(compatibility_router, prefix="/api/v1", tags=["Compatibility"])
app.include_router(exclusoes_router, prefix="/api/v1", tags=["Exclusoes"])
app.include_router(budget_router, prefix="/api/v1", tags=["Budget"])

@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }

@app.get("/api/health")
def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "Recurso não encontrado",
                "details": {"path": str(request.url)}
            }
        }
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Erro interno do servidor",
                "details": {}
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
