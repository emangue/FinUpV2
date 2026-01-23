# 🔐 PRÓXIMOS PASSOS - SEGURANÇA

**Data de criação:** 22/01/2026  
**Score atual de segurança:** 7/10 (ACCEPTABLE)  
**Meta:** 9/10 (EXCELLENT)

---

## 📊 RESUMO EXECUTIVO

### ✅ **JÁ IMPLEMENTADO** (22/01/2026)

- ✅ **JWT Secret forte** - 64 chars hex (256 bits)
- ✅ **PostgreSQL password forte** - 43 chars base64
- ✅ **CORS específico** - https://meufinup.com.br apenas
- ✅ **Firewall UFW** - Portas 22,80,443 apenas
- ✅ **Rate limiting** - slowapi (200/min global, 5/min login)
- ✅ **Fail2Ban** - Proteção SSH contra brute-force
- ✅ **.env com chmod 600** - Secrets isolados do código
- ✅ **DEBUG=false** - Modo produção ativo

**Pontuação atual:**
- HTTPS: 2/2 ✅
- Autenticação: 3/3 ✅
- Database: 2/2 ✅
- Network: 0/2 ⚠️
- Logging: 0.5/1 ⚠️

---

## 🎯 MELHORIAS PENDENTES

### 🟡 PRIORIDADE MÉDIA

#### 1. HTTPS Redirect Validation

**Problema:** Não validamos se HTTP → HTTPS está funcionando corretamente

**Impacto no score:** +0.5 pontos (Network)

**Implementação:**
```bash
# 1. Testar redirect atual
curl -I http://meufinup.com.br
# Esperado: 301 Moved Permanently → https://

# 2. Se não estiver funcionando, configurar nginx
# /etc/nginx/sites-available/finup
server {
    listen 80;
    server_name meufinup.com.br;
    return 301 https://$server_name$request_uri;
}

# 3. Validar
curl -I http://meufinup.com.br
# Deve mostrar: Location: https://meufinup.com.br/
```

**Arquivo a modificar:** Configuração do nginx no servidor

**Validação:**
- [ ] HTTP redireciona para HTTPS (301)
- [ ] Não expõe conteúdo em porta 80
- [ ] Certificado SSL válido

---

#### 2. Filtrar Dados Sensíveis em Logs

**Problema:** Logs podem conter tokens JWT, senhas, informações sensíveis

**Impacto no score:** +0.5 pontos (Logging)

**Implementação:**
```python
# app_dev/backend/app/core/logging.py
import logging
import re

class SensitiveDataFilter(logging.Filter):
    """Filtra dados sensíveis dos logs"""
    
    PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'password=***'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'token=***'),
        (r'jwt["\']?\s*[:=]\s*["\']?([^"\'}\s]+)', 'jwt=***'),
        (r'Authorization:\s*Bearer\s+([^\s]+)', 'Authorization: Bearer ***'),
        (r'[0-9]{16}', '****-****-****-****'),  # Cartões de crédito
    ]
    
    def filter(self, record):
        message = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        record.msg = message
        record.args = ()
        return True

# Aplicar ao logger
logger = logging.getLogger("uvicorn")
logger.addFilter(SensitiveDataFilter())
```

**Arquivos a modificar:**
- `app_dev/backend/app/core/logging.py` (criar)
- `app_dev/backend/app/main.py` (importar filtro)

**Validação:**
- [ ] Logs não mostram senhas
- [ ] Logs não mostram tokens JWT
- [ ] Logs não mostram números de cartão
- [ ] Informações necessárias ainda aparecem

---

#### 3. Criptografar Backups

**Problema:** Backups diários não estão criptografados

**Impacto no score:** +0.5 pontos (Database)

**Implementação:**
```bash
# Modificar scripts/deploy/backup_daily.sh

# 1. Instalar GPG (se não estiver)
apt-get install gnupg

# 2. Gerar chave GPG (apenas uma vez)
gpg --gen-key
# Email: backups@meufinup.com.br

# 3. Modificar script de backup
BACKUP_FILE="financas_dev_$(date +%Y%m%d).db"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# Fazer backup
sqlite3 financas_dev.db ".backup $BACKUP_FILE"

# Criptografar
gpg --symmetric --cipher-algo AES256 --output "$ENCRYPTED_FILE" "$BACKUP_FILE"

# Remover versão não-criptografada
rm "$BACKUP_FILE"

# Manter últimos 7 dias criptografados
find . -name "*.db.gpg" -mtime +7 -delete
```

**Decriptografar quando necessário:**
```bash
gpg --decrypt financas_dev_20260122.db.gpg > financas_dev.db
```

**Arquivos a modificar:**
- `scripts/deploy/backup_daily.sh`
- Documentação de restore

**Validação:**
- [ ] Backups são criptografados (.gpg)
- [ ] Versões não-criptografadas são removidas
- [ ] Consegue decriptografar e restaurar
- [ ] Senha GPG está segura (não no código)

---

#### 4. Security Headers

**Problema:** Faltam headers HTTP de segurança

**Impacto no score:** +1.0 pontos (Network)

**Implementação:**
```python
# app_dev/backend/app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # HSTS - Force HTTPS por 1 ano
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevenir clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevenir MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (antiga Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        return response
```

**Adicionar ao main.py:**
```python
from app.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

**Arquivos a criar/modificar:**
- `app_dev/backend/app/middleware/security_headers.py` (criar)
- `app_dev/backend/app/main.py` (adicionar middleware)

**Validação:**
```bash
# Testar headers
curl -I https://meufinup.com.br/api/health

# Deve mostrar:
# Strict-Transport-Security: max-age=31536000
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
# Content-Security-Policy: ...
```

**Checklist:**
- [ ] HSTS configurado (1 ano)
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] CSP configurado
- [ ] Testar em https://securityheaders.com

---

### 🟢 PRIORIDADE BAIXA

#### 5. Monitoramento e Alertas

**Problema:** Não temos alertas automáticos de problemas

**Impacto no score:** Não afeta score direto, mas melhora resposta a incidentes

**Implementação:**

**Opção 1: Prometheus + Grafana (completo)**
```bash
# Instalar Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Configurar prometheus.yml
scrape_configs:
  - job_name: 'finup-backend'
    static_configs:
      - targets: ['localhost:8000']

# Instalar Grafana
apt-get install -y grafana

# Dashboards prontos:
# - CPU, RAM, Disk
# - Requests/min
# - Erros 4xx, 5xx
# - Latência P50, P95, P99
```

**Opção 2: Uptime Kuma (simples)**
```bash
# Docker
docker run -d \
  --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1

# Acessar http://servidor:3001
# Adicionar monitores:
# - https://meufinup.com.br/api/health (a cada 1 min)
# - PostgreSQL (localhost:5432)
# - Disco >80% cheio
```

**Opção 3: Script Bash Simples**
```bash
# scripts/monitoring/health_check.sh
#!/bin/bash

HEALTH_URL="https://meufinup.com.br/api/health"
EMAIL="admin@meufinup.com.br"

# Testar endpoint
if ! curl -s "$HEALTH_URL" | grep -q "healthy"; then
    echo "⚠️ BACKEND DOWN!" | mail -s "ALERTA: FinUp Backend" "$EMAIL"
fi

# Testar PostgreSQL
if ! pg_isready -h localhost -p 5432 -U finup_user; then
    echo "⚠️ POSTGRESQL DOWN!" | mail -s "ALERTA: PostgreSQL" "$EMAIL"
fi

# Testar disco
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️ DISCO EM $DISK_USAGE%!" | mail -s "ALERTA: Disco Cheio" "$EMAIL"
fi
```

**Cron (executar a cada 5 minutos):**
```bash
crontab -e
*/5 * * * * /var/www/finup/scripts/monitoring/health_check.sh
```

**Arquivos a criar:**
- `scripts/monitoring/health_check.sh`
- Configuração de email (postfix ou sendmail)
- Dashboard Grafana (se escolher Prometheus)

**Validação:**
- [ ] Alerta dispara quando backend cai
- [ ] Alerta dispara quando disco >80%
- [ ] Alerta dispara quando PostgreSQL cai
- [ ] Recebe notificação em menos de 5 minutos

---

#### 6. Auditoria de Dependências

**Problema:** Não verificamos vulnerabilidades em bibliotecas

**Impacto no score:** Prevenção de vulnerabilidades futuras

**Implementação:**
```bash
# 1. Instalar safety (scanner de vulnerabilidades)
pip install safety

# 2. Verificar vulnerabilidades
safety check --json

# 3. Adicionar ao CI/CD (GitHub Actions)
# .github/workflows/security.yml
name: Security Audit
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r app_dev/backend/requirements.txt
      - name: Run safety check
        run: safety check --json
      - name: Run bandit (security linter)
        run: |
          pip install bandit
          bandit -r app_dev/backend/app
```

**Cron mensal (local ou servidor):**
```bash
# Executar todo dia 1 do mês
crontab -e
0 0 1 * * cd /var/www/finup && safety check --json > security_report.json
```

**Arquivos a criar:**
- `.github/workflows/security.yml`
- Script mensal de auditoria

**Validação:**
- [ ] Safety check rodando no CI/CD
- [ ] Relatório mensal gerado
- [ ] Vulnerabilidades são corrigidas em <7 dias

---

#### 7. Rotação Automática de Secrets

**Problema:** Secrets nunca expiram

**Impacto no score:** Reduz janela de exposição se secret vazar

**Implementação:**
```bash
# scripts/maintenance/rotate_secrets.sh
#!/bin/bash
# Executar a cada 6 meses

# 1. Gerar novos secrets
NEW_JWT=$(python3 -c "import secrets; print(secrets.token_hex(32))")
NEW_DB_PASS=$(openssl rand -base64 32)

# 2. Criar novo .env
cat > /var/www/finup/app_dev/backend/.env.new << EOF
JWT_SECRET_KEY=$NEW_JWT
DATABASE_URL=postgresql://finup_user:$NEW_DB_PASS@localhost:5432/finup_db
BACKEND_CORS_ORIGINS=https://meufinup.com.br
DEBUG=false
EOF

# 3. Alterar senha PostgreSQL
sudo -u postgres psql -c "ALTER USER finup_user WITH PASSWORD '$NEW_DB_PASS';"

# 4. Backup do .env antigo
cp .env .env.backup.$(date +%Y%m%d)

# 5. Ativar novo .env
mv .env.new .env
chmod 600 .env

# 6. Reiniciar backend
systemctl restart finup-backend

# 7. Validar
sleep 5
curl -s https://meufinup.com.br/api/health | grep healthy && echo "✅ Secrets rotacionados!"
```

**Lembrete no calendário:**
```bash
# Executar a cada 6 meses (jan/jul)
crontab -e
0 0 1 1,7 * /var/www/finup/scripts/maintenance/rotate_secrets.sh
```

**Arquivos a criar:**
- `scripts/maintenance/rotate_secrets.sh`
- Documentação de processo

**Validação:**
- [ ] Script roda sem erros
- [ ] Backend funciona após rotação
- [ ] .env antigo é backupado
- [ ] PostgreSQL aceita nova senha

---

#### 8. Logs de Auditoria

**Problema:** Não registramos ações sensíveis (login, alteração de dados)

**Impacto no score:** Rastreabilidade de incidentes

**Implementação:**
```python
# app_dev/backend/app/domains/audit/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.core.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # LOGIN, LOGOUT, UPDATE, DELETE
    resource = Column(String(100))  # transactions, users, etc
    resource_id = Column(String(50))
    ip_address = Column(String(50))
    user_agent = Column(String(200))
    details = Column(Text)  # JSON com detalhes
    timestamp = Column(DateTime, default=datetime.utcnow)

# app_dev/backend/app/domains/audit/service.py
class AuditService:
    @staticmethod
    def log_action(
        user_id: int,
        action: str,
        resource: str = None,
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        details: dict = None
    ):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=json.dumps(details) if details else None
        )
        db.add(log)
        db.commit()

# Uso nos endpoints
from app.domains.audit.service import AuditService

@router.post("/login")
def login(request: Request, ...):
    # ... autenticação ...
    
    AuditService.log_action(
        user_id=user.id,
        action="LOGIN",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
```

**Queries úteis:**
```python
# Listar todos os logins de um usuário
SELECT * FROM audit_logs WHERE user_id = 1 AND action = 'LOGIN' ORDER BY timestamp DESC;

# Detectar múltiplos IPs
SELECT user_id, COUNT(DISTINCT ip_address) 
FROM audit_logs 
WHERE action = 'LOGIN' AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY user_id
HAVING COUNT(DISTINCT ip_address) > 3;
```

**Arquivos a criar:**
- `app_dev/backend/app/domains/audit/models.py`
- `app_dev/backend/app/domains/audit/service.py`
- `app_dev/backend/app/domains/audit/router.py` (visualização de logs)
- Migration Alembic para criar tabela

**Validação:**
- [ ] Logins são registrados
- [ ] Alterações em transações são registradas
- [ ] IP e user agent são salvos
- [ ] Query de logs suspeitos funciona

---

## 📅 CRONOGRAMA SUGERIDO

### Mês 1 (Fevereiro 2026)
- [ ] HTTPS Redirect Validation (1h)
- [ ] Filtrar Dados Sensíveis em Logs (2h)
- [ ] Security Headers (2h)

### Mês 2 (Março 2026)
- [ ] Criptografar Backups (2h)
- [ ] Monitoramento básico (4h)

### Mês 3 (Abril 2026)
- [ ] Logs de Auditoria (6h)
- [ ] Auditoria de Dependências (2h)

### Mês 4+ (Maio 2026+)
- [ ] Rotação Automática de Secrets (3h)
- [ ] Revisão geral de segurança

---

## 🎯 META FINAL

**Score atual:** 7/10 (ACCEPTABLE)  
**Score após implementações:** 9/10 (EXCELLENT)

**Breakdown esperado:**
- HTTPS: 2/2 ✅
- Autenticação: 3/3 ✅
- Database: 2/2 ✅
- Network: 2/2 ✅ (após HTTPS redirect + headers)
- Logging: 1/1 ✅ (após filtrar dados + audit logs)
- Monitoring: +bonus ✅
- Backup: +bonus ✅ (criptografado)

---

## 📋 REFERÊNCIAS

### Documentos Relacionados:
- `docs/deploy/AUDITORIA_SEGURANCA_22JAN2026.md` - Auditoria inicial
- `docs/deploy/CORRECOES_SEGURANCA_APLICADAS_22JAN2026.md` - O que já foi feito
- `.github/copilot-instructions.md` - Regras de segurança obrigatórias

### Ferramentas Úteis:
- https://securityheaders.com - Testar headers HTTP
- https://observatory.mozilla.org - Análise completa de segurança
- https://www.ssllabs.com/ssltest/ - Testar certificado SSL
- https://safety.cyberbrain.pw - Verificar vulnerabilidades Python

### Padrões e Guidelines:
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CIS Controls: https://www.cisecurity.org/controls

---

**Criado em:** 22/01/2026  
**Última atualização:** 22/01/2026  
**Autor:** GitHub Copilot  
**Revisão:** Pendente após cada implementação
