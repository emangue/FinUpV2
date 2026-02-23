# 🛡️ PRD - Segurança Avançada: Admin Panel & Backend Hardening

**Data:** 22/02/2026  
**Status:** 📋 PLANEJADO (Futuro)  
**Prioridade:** Alta  
**Sprint alvo:** A definir  

---

## 1. Problema

O sistema possui um painel admin separado (`app_admin`, port 3001) para organização, mas a segurança real depende exclusivamente do backend. Atualmente:

- ❌ Não há verificação de role granular (RBAC) em todas as rotas admin
- ❌ Não há 2FA (Two-Factor Authentication) para admins
- ❌ Não há rate limiting específico para rotas administrativas
- ❌ Não há IP whitelist para acesso admin em produção
- ❌ Não há auditoria (audit log) de ações administrativas
- ❌ Não há política de expiração de sessão diferenciada para admin

---

## 2. Objetivos

### 2.1 Segurança de Autenticação

| Item | Descrição | Prioridade |
|------|-----------|------------|
| **RBAC Granular** | Middleware `@require_role("admin")` em TODAS as rotas sensíveis | 🔴 Crítica |
| **2FA para Admins** | TOTP (Google Authenticator / Authy) obrigatório para role=admin | 🔴 Crítica |
| **Sessão Admin** | JWT com TTL curto (15min) + refresh token (1h) para admins | 🟡 Alta |
| **Password Policy** | Mínimo 12 chars, upper+lower+number+special para admins | 🟡 Alta |

### 2.2 Segurança de Autorização

| Item | Descrição | Prioridade |
|------|-----------|------------|
| **IP Whitelist** | Admin só acessível de IPs configurados (.env) | 🟡 Alta |
| **Rate Limiting Admin** | 10 req/min em rotas `/admin/*` | 🟡 Alta |
| **CORS Restritivo** | Admin frontend CORS separado do app frontend | 🟢 Média |
| **CSP Headers** | Content-Security-Policy para admin frontend | 🟢 Média |

### 2.3 Auditoria e Monitoramento

| Item | Descrição | Prioridade |
|------|-----------|------------|
| **Audit Log** | Registrar TODA ação admin (quem, quando, o quê, IP) | 🔴 Crítica |
| **Login Alerts** | Notificar admin por email em login de outro admin | 🟡 Alta |
| **Failed Login Monitor** | Alertar após 3 falhas consecutivas em conta admin | 🟡 Alta |
| **Dashboard Security** | Painel mostrando logins, ações, IPs recentes | 🟢 Média |

---

## 3. Implementação Técnica

### 3.1 RBAC - Role-Based Access Control

```python
# app/shared/auth/rbac.py

from enum import Enum
from functools import wraps
from fastapi import HTTPException, Request

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class Permission(str, Enum):
    # Transações
    TRANSACTIONS_READ = "transactions:read"
    TRANSACTIONS_WRITE = "transactions:write"
    TRANSACTIONS_DELETE = "transactions:delete"
    
    # Usuários
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"
    
    # Sistema
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"

ROLE_PERMISSIONS = {
    Role.USER: [
        Permission.TRANSACTIONS_READ,
        Permission.TRANSACTIONS_WRITE,
    ],
    Role.ADMIN: [
        Permission.TRANSACTIONS_READ,
        Permission.TRANSACTIONS_WRITE,
        Permission.TRANSACTIONS_DELETE,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
    ],
    Role.SUPER_ADMIN: [
        # Todas as permissões
        *[p for p in Permission]
    ],
}

def require_role(*roles: Role):
    """Decorator para exigir role específica."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            user = request.state.user
            if user.role not in roles:
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission: Permission):
    """Decorator para exigir permissão específica."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            user = request.state.user
            user_permissions = ROLE_PERMISSIONS.get(Role(user.role), [])
            if permission not in user_permissions:
                raise HTTPException(403, f"Missing permission: {permission}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3.2 Two-Factor Authentication (2FA/TOTP)

```python
# app/domains/auth/totp.py

import pyotp
import qrcode
from io import BytesIO
import base64

class TOTPService:
    @staticmethod
    def generate_secret() -> str:
        """Gera secret TOTP para o usuário."""
        return pyotp.random_base32()
    
    @staticmethod
    def get_provisioning_uri(secret: str, email: str) -> str:
        """Gera URI para QR code (Google Authenticator)."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name="FinUp"
        )
    
    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """Gera QR code em base64 para exibir no frontend."""
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        """Verifica código TOTP (aceita janela de ±30s)."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

# Dependências necessárias:
# pip install pyotp qrcode[pil]
```

### 3.3 Audit Log

```python
# app/shared/audit/models.py

from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, nullable=False)
    user_email = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "user.delete", "transaction.update"
    resource_type = Column(String, nullable=True)  # "user", "transaction"
    resource_id = Column(String, nullable=True)  # ID do recurso afetado
    details = Column(JSON, nullable=True)  # Detalhes da ação (before/after)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    status = Column(String, default="success")  # "success", "failed", "blocked"

# app/shared/audit/service.py

class AuditService:
    def __init__(self, db: Session):
        self.db = db
    
    async def log(
        self,
        user_id: int,
        user_email: str,
        user_role: str,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        status: str = "success",
    ):
        entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
        )
        self.db.add(entry)
        self.db.commit()
```

### 3.4 IP Whitelist Middleware

```python
# app/shared/middleware/ip_whitelist.py

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import ipaddress

class AdminIPWhitelistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_ips: list[str] = None):
        super().__init__(app)
        self.allowed_networks = []
        for ip in (allowed_ips or []):
            try:
                self.allowed_networks.append(ipaddress.ip_network(ip))
            except ValueError:
                pass
    
    async def dispatch(self, request: Request, call_next):
        # Só aplica em rotas admin
        if not request.url.path.startswith("/api/v1/admin"):
            return await call_next(request)
        
        # Se não configurou whitelist, permitir tudo
        if not self.allowed_networks:
            return await call_next(request)
        
        client_ip = ipaddress.ip_address(request.client.host)
        
        for network in self.allowed_networks:
            if client_ip in network:
                return await call_next(request)
        
        raise HTTPException(
            status_code=403,
            detail="Admin access restricted to whitelisted IPs"
        )
```

### 3.5 Rate Limiting Admin

```python
# Atualizar app/main.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Rotas admin: 10 req/min
# Login admin: 3 req/min (anti brute-force)
# Rotas normais: 200 req/min

# Em cada router admin:
@router.delete("/users/{user_id}")
@limiter.limit("10/minute")
@require_role(Role.ADMIN)
async def delete_user(request: Request, user_id: int):
    # ... audit log + delete
    pass
```

---

## 4. Dependências Python Necessárias

```txt
# requirements.txt (adicionar)
pyotp>=2.9.0          # TOTP 2FA
qrcode[pil]>=7.4      # QR Code generation
slowapi>=0.1.9         # Rate limiting (já usado?)
```

---

## 5. Migration Alembic Necessária

```python
# Tabela audit_logs
def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(), nullable=False),
        sa.Column('user_role', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('status', sa.String(), default='success'),
    )
    
    # Coluna 2FA no users
    op.add_column('users', sa.Column('totp_secret', sa.String(), nullable=True))
    op.add_column('users', sa.Column('totp_enabled', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('totp_verified_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_table('audit_logs')
    op.drop_column('users', 'totp_secret')
    op.drop_column('users', 'totp_enabled')
    op.drop_column('users', 'totp_verified_at')
```

---

## 6. Configuração .env Necessária

```bash
# .env (adicionar)
# Admin Security
ADMIN_2FA_REQUIRED=true
ADMIN_JWT_TTL_MINUTES=15
ADMIN_REFRESH_TTL_MINUTES=60
ADMIN_ALLOWED_IPS=  # Vazio = permitir tudo; "10.0.0.0/8,192.168.1.0/24"
ADMIN_RATE_LIMIT=10/minute
ADMIN_LOGIN_RATE_LIMIT=3/minute
ADMIN_FAILED_LOGIN_ALERT_THRESHOLD=3
ADMIN_AUDIT_LOG_RETENTION_DAYS=365
```

---

## 7. Checklist de Implementação

### Sprint 1 - RBAC + Audit Log (1 semana)

- [ ] Criar `app/shared/auth/rbac.py` com decorators
- [ ] Adicionar `@require_role` em TODAS as rotas admin existentes
- [ ] Criar model `AuditLog` + migration Alembic
- [ ] Criar `AuditService` com método `log()`
- [ ] Integrar audit log em rotas admin críticas (delete user, update config)
- [ ] Testes: verificar que user comum não acessa rotas admin

### Sprint 2 - 2FA (1 semana)

- [ ] Instalar pyotp + qrcode
- [ ] Criar `TOTPService` com generate/verify
- [ ] Adicionar colunas `totp_secret`, `totp_enabled` no model User
- [ ] Criar endpoints: `POST /auth/2fa/setup`, `POST /auth/2fa/verify`, `POST /auth/2fa/disable`
- [ ] Criar UI de setup 2FA no admin (QR code + campo de verificação)
- [ ] Modificar flow de login: após senha, exigir código TOTP se `totp_enabled=true`
- [ ] Testes: login com 2FA, login sem 2FA (bloqueado se required)

### Sprint 3 - Rate Limiting + IP Whitelist (3 dias)

- [ ] Configurar slowapi com limites diferenciados (admin vs user)
- [ ] Criar `AdminIPWhitelistMiddleware`
- [ ] Adicionar variáveis no .env
- [ ] Testar rate limiting (enviar 11+ requests em 1 min)
- [ ] Testar IP whitelist (acesso de IP não autorizado = 403)

### Sprint 4 - Monitoramento + Alertas (3 dias)

- [ ] Endpoint `GET /admin/audit-logs` com filtros (user, action, date range)
- [ ] UI de audit logs no painel admin
- [ ] Sistema de alertas: email quando admin loga de IP novo
- [ ] Dashboard de segurança: últimos logins, ações, IPs

---

## 8. Prioridade de Implementação

```
🔴 CRÍTICO (fazer primeiro):
   1. RBAC em rotas admin
   2. Audit Log
   3. 2FA para admins

🟡 ALTO (fazer segundo):
   4. Rate limiting admin
   5. IP Whitelist
   6. Sessão admin com TTL curto

🟢 MÉDIO (fazer depois):
   7. Dashboard de segurança
   8. Alertas por email
   9. CSP Headers
```

---

## 9. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Admin perde TOTP device | Não consegue logar | Recovery codes (10 códigos únicos gerados no setup) |
| Rate limiting muito agressivo | Admin bloqueado durante operações | Whitelist de IPs admin ignora rate limit |
| Audit log enche disco | Banco cresce indefinidamente | Retention policy: purge logs > 365 dias |
| IP dinâmico do admin | Whitelist falha | Opção de usar VPN com IP fixo |

---

## 10. Métricas de Sucesso

- [ ] 100% das rotas admin protegidas por RBAC
- [ ] 100% dos admins com 2FA ativo
- [ ] 0 ações admin sem audit log
- [ ] < 1s latência adicional por middleware de segurança
- [ ] Recovery: admin consegue recuperar acesso em < 5 minutos

---

**Próximo passo:** Aprovar PRD → Criar TECH_SPEC detalhado → Implementar Sprint 1

**Estimativa total:** 3 semanas de desenvolvimento  
**Dependências:** pyotp, qrcode, slowapi  
**Breaking changes:** Nenhum (adições apenas)
