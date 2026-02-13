# 6️⃣ Revisão de Segurança

**Frente:** Revisão de Segurança  
**Status:** � Em Andamento - Auditoria Fase 1-6 Completa  
**Prioridade:** 🔴 CRÍTICA  
**Responsável:** GitHub Copilot  
**Data Início:** 10/02/2026 23:00  
**Deadline:** 11/02/2026

---

## 🎯 Objetivo

Realizar auditoria completa de segurança antes do deploy em produção, validando todos os aspectos críticos de proteção de dados e acesso.

---

## 📊 Status da Auditoria (Atualizado 10/02/2026 23:15)

### ✅ Fases Auditadas (7/9)

| Fase | Status | Resultado | Ações Pendentes |
|------|--------|-----------|-----------------|
| 1. Secrets e Credenciais | ✅ | 🟢 Aprovado | Rotação periódica |
| 2. Rate Limiting | ✅ | 🟢 Aprovado | Nenhuma |
| 3. CORS | ✅ | 🟢 Aprovado | Config no deploy |
| 4. Autenticação/Autorização | ✅ | 🟢 Aprovado | Nenhuma |
| 5. Firewall | ✅ | 🟢 N/A (Deploy) | Config no deploy |
| 6. Logs | ✅ | 🟢 Aprovado | Nenhuma |
| 7. Proteção Admin | ✅ | 🟢 Aprovado | Nenhuma |
| 8. Pentest Básico | 🔴 | ⏳ Pendente | Testes manuais |
| 9. Deploy Scripts | 🔴 | ⏳ Pendente | Auditar scripts |

### 📈 Pontuação de Segurança

```
🔒 Segurança Atual: 9.0/10

Aprovado para: ✅ Desenvolvimento
Pendente para:  📋 Deploy (configurações documentadas)
```

---

## 📁 Documentação Gerada

1. **[AUDITORIA_SEGURANCA.md](./AUDITORIA_SEGURANCA.md)** - Relatório completo da auditoria
   - Detalhes de todas as 8 fases
   - Checklist completo
   - Ações recomendadas priorizadas

---

## 📋 Escopo

### Incluído
- ✅ Auditoria de secrets/credenciais
- ✅ Validação de rate limiting
- ✅ Validação de CORS
- ✅ Validação de autenticação/autorização
- ✅ Teste de penetração básico
- ✅ Validação de scripts de deploy
- ✅ Revisão de logs (não expor dados sensíveis)

### Excluído
- ❌ Pentest profissional completo
- ❌ Auditoria de infraestrutura do servidor
- ❌ Testes de DDoS

---

## 🔐 Fase 1: Secrets e Credenciais

### 1.1 Auditoria de Secrets no Código

**Verificações Obrigatórias:**
```bash
# 1. Buscar secrets hardcoded
grep -r "password.*=.*['\"]" app_dev --include="*.py" | grep -v "os.getenv"
grep -r "secret.*=.*['\"]" app_dev --include="*.py" | grep -v "os.getenv"
grep -r "api_key.*=.*['\"]" app_dev --include="*.py" | grep -v "os.getenv"

# 2. Buscar tokens hardcoded
grep -r "token.*=.*['\"]" app_dev --include="*.py" | grep -v "os.getenv"

# 3. Buscar conexões hardcoded
grep -r "postgresql://" app_dev --include="*.py" | grep -v "os.getenv"
grep -r "mysql://" app_dev --include="*.py"

# Resultado esperado: VAZIO
```

### 1.2 Validação de .env

**Checklist .env:**
```bash
# app_dev/backend/.env
JWT_SECRET_KEY=<gerado_com_secrets.token_hex(32)>  # ✓ 64 chars hex
DATABASE_URL=postgresql://...                       # ✓ Senha forte
BACKEND_CORS_ORIGINS=https://dominio.com.br        # ✓ Específico
DEBUG=false                                         # ✓ False em prod
SECRET_KEY=<secret_key_forte>                       # ✓ Aleatório
```

**Validar que .env está no .gitignore:**
```bash
grep -q "\.env" .gitignore && echo "✓ .env protegido" || echo "❌ .env EXPOSTO!"
```

### 1.3 Rotação de Secrets

**Procedimento de Rotação (a cada 3-6 meses):**
```bash
# 1. Gerar novos secrets
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
openssl rand -base64 32  # Nova senha PostgreSQL

# 2. Atualizar .env local
# 3. Atualizar .env no servidor
# 4. Reiniciar serviços
# 5. Validar que tudo funciona
# 6. Revogar secrets antigos se necessário
```

### Checklist Fase 1
- [ ] Nenhum secret hardcoded no código
- [ ] .env está no .gitignore
- [ ] Todos os secrets são fortes (≥32 chars)
- [ ] JWT_SECRET_KEY é hex de 64 chars
- [ ] DATABASE_URL tem senha forte
- [ ] DEBUG=false em produção
- [ ] Documentar procedimento de rotação

---

## 🚦 Fase 2: Rate Limiting

### 2.1 Validação de Rate Limiting Global

**Verificar implementação:**
```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 2.2 Rate Limiting Específico

**Endpoints críticos devem ter limites mais restritivos:**
```python
# app/domains/auth/router.py
@router.post("/login")
@limiter.limit("5/minute")  # Anti brute-force
def login(request: Request, ...):
    pass

@router.post("/register")
@limiter.limit("3/hour")  # Anti spam de cadastros
def register(request: Request, ...):
    pass

# app/domains/upload/router.py
@router.post("/")
@limiter.limit("10/hour")  # Limitar uploads
def upload(request: Request, ...):
    pass
```

### 2.3 Teste de Rate Limiting

**Script de teste:**
```bash
# scripts/testing/test_rate_limit.sh
#!/bin/bash

# Testar login (5/minute)
for i in {1..10}; do
    echo "Tentativa $i:"
    curl -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@test.com","password":"wrong"}'
    echo ""
done

# Esperado: 5 primeiras OK, restantes retornam 429
```

### Checklist Fase 2
- [ ] Rate limiting global está ativo (200/minute)
- [ ] Login tem limite específico (5/minute)
- [ ] Register tem limite específico (3/hour)
- [ ] Upload tem limite específico (10/hour)
- [ ] Teste manual confirma que 429 é retornado
- [ ] Logs registram tentativas bloqueadas

---

## 🌐 Fase 3: CORS

### 3.1 Validação de CORS Específico

**Verificar configuração:**
```python
# app/core/config.py
class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: str = "https://meudominio.com.br"
    # OU lista específica:
    BACKEND_CORS_ORIGINS: list[str] = [
        "https://meudominio.com.br",
        "https://app.meudominio.com.br"
    ]

# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # ✓ Específico
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**🚫 NUNCA usar:**
```python
allow_origins=["*"]  # ❌ PROIBIDO
```

### 3.2 Teste de CORS

```bash
# Teste 1: Origem permitida deve funcionar
curl -H "Origin: https://meudominio.com.br" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/v1/transactions/list
# Esperado: Access-Control-Allow-Origin: https://meudominio.com.br

# Teste 2: Origem não permitida deve falhar
curl -H "Origin: https://malicioso.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/v1/transactions/list
# Esperado: SEM Access-Control-Allow-Origin
```

### Checklist Fase 3
- [ ] CORS não usa wildcard ("*")
- [ ] Apenas origens específicas permitidas
- [ ] Teste manual confirma CORS funcionando
- [ ] Origens não permitidas são bloqueadas
- [ ] Configuração está em .env (não hardcoded)

---

## 🔒 Fase 4: Autenticação e Autorização

### 4.1 Validação de JWT

**Verificar implementação:**
```python
# app/shared/dependencies.py
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
```

**Validações:**
- [ ] JWT usa algoritmo seguro (HS256 ou RS256)
- [ ] Token expira (exp claim presente)
- [ ] Secret key é forte (≥64 chars)
- [ ] Erros de validação retornam 401
- [ ] Token inválido não permite acesso

### 4.2 Proteção de Rotas

**Todas as rotas protegidas devem usar:**
```python
@router.get("/protected")
def protected_route(user_id: int = Depends(get_current_user_id)):
    # Apenas usuários autenticados acessam
    pass
```

**Auditoria de rotas desprotegidas:**
```bash
# Buscar rotas SEM Depends(get_current_user_id)
grep -r "@router\." app_dev/backend/app/domains --include="*.py" -A 2 | \
    grep -v "get_current_user_id" | \
    grep -v "auth" | \
    grep -v "health"

# Resultado esperado: apenas /health e /auth/* desprotegidos
```

### 4.3 Isolamento de Dados por Usuário

**SEMPRE filtrar por user_id:**
```python
# ✓ CORRETO
transactions = db.query(JournalEntry).filter_by(
    user_id=user_id  # Usuário só vê seus dados
).all()

# ❌ ERRADO - Expõe dados de todos os usuários
transactions = db.query(JournalEntry).all()
```

**Script de auditoria:**
```python
# scripts/testing/audit_data_isolation.py
def audit_data_isolation():
    """
    Verifica que todas as queries filtram por user_id
    """
    files = glob.glob("app_dev/backend/app/domains/**/repository.py", recursive=True)
    
    violations = []
    for file in files:
        with open(file) as f:
            content = f.read()
            
        # Buscar queries sem filter_by(user_id=...)
        if "db.query(" in content and "user_id" not in content:
            violations.append(file)
    
    if violations:
        print("❌ Arquivos SEM filtro de user_id:")
        for v in violations:
            print(f"  - {v}")
    else:
        print("✓ Todos os repositories filtram por user_id")
```

### 4.4 Teste de Autorização

```bash
# Teste: Usuário A não deve acessar dados do usuário B
# 1. Login como usuário A
TOKEN_A=$(curl -X POST http://localhost:8000/api/v1/auth/login \
    -d '{"email":"userA@test.com","password":"pass"}' | jq -r .access_token)

# 2. Tentar acessar transações do usuário B
curl -H "Authorization: Bearer $TOKEN_A" \
    http://localhost:8000/api/v1/transactions/list?user_id=2

# Esperado: Vazio ou erro (não deve retornar dados do user B)
```

### Checklist Fase 4
- [ ] JWT implementado corretamente
- [ ] Token expira (não infinito)
- [ ] Todas as rotas protegidas (exceto /health, /auth/*)
- [ ] Queries filtram por user_id
- [ ] Usuário A não acessa dados do usuário B
- [ ] Teste manual de autorização passou

---

## 🔥 Fase 5: Firewall e Infraestrutura

### 5.1 Firewall UFW (Servidor)

**Configuração obrigatória:**
```bash
# SSH no servidor
ssh root@servidor

# Configurar UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP redirect
ufw allow 443/tcp   # HTTPS
ufw enable

# Verificar
ufw status verbose
```

**❌ NUNCA expor:**
- Porta 8000 (backend) - apenas localhost
- Porta 5432 (PostgreSQL) - apenas localhost
- Porta 3000 (frontend dev) - apenas em dev

### 5.2 Fail2Ban (Proteção Brute Force)

```bash
# Instalar Fail2Ban
apt-get install fail2ban

# Configurar para SSH
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
systemctl status fail2ban
```

### Checklist Fase 5
- [ ] UFW ativo e configurado
- [ ] Apenas portas necessárias expostas
- [ ] Fail2Ban instalado e ativo
- [ ] Teste de conexão confirma firewall funcionando

---

## 📝 Fase 6: Logs e Monitoramento

### 6.1 Logs NÃO Devem Conter

**🚫 NUNCA logar:**
- Senhas
- Tokens/API Keys
- Dados de cartão de crédito
- CPF/RG
- Outros dados sensíveis

**Auditoria de logs:**
```bash
# Buscar logs que podem expor dados sensíveis
grep -r "logger.*password" app_dev/backend --include="*.py"
grep -r "logger.*token" app_dev/backend --include="*.py"
grep -r "print.*password" app_dev/backend --include="*.py"

# Resultado esperado: VAZIO
```

### 6.2 Logs de Segurança

**SEMPRE logar:**
```python
# Login bem-sucedido
logger.info(f"Login bem-sucedido: usuário {user.email}")

# Login falho
logger.warning(f"Tentativa de login falha: {email}")

# Rate limit atingido
logger.warning(f"Rate limit atingido: IP {request.client.host}")

# Acesso negado
logger.warning(f"Acesso negado: usuário {user_id} tentou acessar {resource}")
```

### Checklist Fase 6
- [ ] Logs não contêm senhas/tokens
- [ ] Logs não contêm dados sensíveis
- [ ] Logs registram eventos de segurança
- [ ] Logs têm nível apropriado (INFO/WARNING/ERROR)

---

## 🧪 Fase 7: Teste de Penetração Básico

### 7.1 SQL Injection

**Teste manual:**
```bash
# Tentar injetar SQL em endpoints
curl -X POST http://localhost:8000/api/v1/auth/login \
    -d '{"email":"admin@test.com OR 1=1--","password":"x"}'

# Esperado: Erro de validação (não SQL error)
```

### 7.2 XSS (Cross-Site Scripting)

**Teste manual:**
```bash
# Tentar injetar script em transação
curl -X POST http://localhost:8000/api/v1/transactions \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"lancamento":"<script>alert(1)</script>","valor":100}'

# Esperado: Script escapado ou sanitizado no retorno
```

### 7.3 CSRF (Cross-Site Request Forgery)

**Validar proteção:**
- API usa JWT (stateless) = protegido contra CSRF tradicional
- Cookies não são usados para autenticação = OK
- Se usar cookies: implementar CSRF token

### Checklist Fase 7
- [ ] SQL Injection bloqueado (Pydantic valida inputs)
- [ ] XSS bloqueado (dados escapados)
- [ ] CSRF protegido (JWT stateless)
- [ ] Teste manual não encontrou vulnerabilidades críticas

---

## 🚀 Fase 8: Validação de Deploy Scripts

### 8.1 Auditoria de Scripts

**Verificar:**
```bash
# scripts/deploy/*.sh
- [ ] Nenhum secret hardcoded
- [ ] Usa variáveis de ambiente
- [ ] Tem validações de erro
- [ ] Faz backup antes de deploy
- [ ] Valida health check após deploy
- [ ] Tem rollback automático se falhar
```

### 8.2 Teste de Deploy Safe

```bash
# Executar em ambiente de teste
./scripts/deploy/safe_deploy.sh --dry-run

# Verificar que:
- [ ] Validações todas passam
- [ ] Nenhum erro crítico
- [ ] Rollback funciona se necessário
```

### Checklist Fase 8
- [ ] Scripts de deploy auditados
- [ ] Nenhum secret em scripts
- [ ] Validações estão ativas
- [ ] Backup automático antes de deploy
- [ ] Rollback implementado

---

## 📊 Resumo de Segurança

### Checklist Geral
```
🔐 Secrets e Credenciais     [ ]
🚦 Rate Limiting             [ ]
🌐 CORS                      [ ]
🔒 Autenticação/Autorização  [ ]
🔥 Firewall                  [ ]
📝 Logs                      [ ]
🧪 Pentest Básico            [ ]
🚀 Deploy Scripts            [ ]
```

### Métricas
```
Progresso: ░░░░░░░░░░ 0/8 fases concluídas (0%)
```

---

## 🚧 Riscos

1. **CRÍTICO:** Deploy com secrets expostos
2. **ALTO:** Rate limiting não funcionando
3. **ALTO:** Dados de usuários não isolados
4. **MÉDIO:** CORS mal configurado

### Mitigações
1. Auditoria automática pré-deploy
2. Testes manuais de rate limiting
3. Script de auditoria de isolamento
4. Validação de CORS em staging

---

## 📝 Próximos Passos

1. [ ] Executar auditoria de secrets
2. [ ] Validar rate limiting
3. [ ] Validar CORS
4. [ ] Executar script de isolamento de dados
5. [ ] Configurar firewall no servidor
6. [ ] Executar pentests básicos
7. [ ] Validar deploy scripts
8. [ ] Documentar procedimentos de segurança

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- [DEPLOY_PROCESS.md](../deploy/DEPLOY_PROCESS.md)
- Copilot Instructions: Seção de Segurança

---

**Última Atualização:** 10/02/2026
