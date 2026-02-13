"""
FastAPI Main Application - Arquitetura Modular em Domínios
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .core.database import engine, Base

# Import models para SQLAlchemy resolver relationships
from .domains.upload.history_models import UploadHistory  # CRITICAL: importar antes dos routers
from .domains.compatibility.models import BankFormatCompatibility  # CRITICAL: importar para SQLAlchemy encontrar tabela

# Domínios isolados (arquitetura DDD)
from .domains.auth.router import router as auth_router
from .domains.transactions.router import router as transactions_router
from .domains.users.router import router as users_router
from .domains.categories.router import router as categories_router
from .domains.cards.router import router as cards_router
from .domains.upload.router import router as upload_router
from .domains.dashboard.router import router as dashboard_router
from .domains.compatibility.router import router as compatibility_router
from .domains.exclusoes.router import router as exclusoes_router
from .domains.budget.router import router as budget_router
from .domains.grupos.router import router as grupos_router
from .domains.marcacoes.router import router as marcacoes_router
from .domains.screen_visibility.router import router as screen_visibility_router
from .domains.classification.router import router as classification_router
from .domains.investimentos.router import router as investimentos_router

# Cria app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST para Sistema de Finanças Pessoais - Arquitetura Modular",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Rate Limiting - Proteção contra abuso
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Permite Next.js se conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers Modularizados (arquitetura DDD - Domain-Driven Design)
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(transactions_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(categories_router, prefix="/api/v1", tags=["Categories"])
app.include_router(cards_router, prefix="/api/v1", tags=["Cards"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(compatibility_router, prefix="/api/v1", tags=["Compatibility"])
app.include_router(exclusoes_router, prefix="/api/v1", tags=["Exclusoes"])
app.include_router(budget_router, prefix="/api/v1", tags=["Budget"])
app.include_router(grupos_router, prefix="/api/v1", tags=["Grupos"])
app.include_router(marcacoes_router, prefix="/api/v1", tags=["Marcações"])
app.include_router(screen_visibility_router, prefix="/api/v1/screens", tags=["Screen Visibility"])
app.include_router(classification_router, prefix="/api/v1", tags=["Classification"])
app.include_router(investimentos_router, prefix="/api/v1", tags=["Investimentos"])

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
