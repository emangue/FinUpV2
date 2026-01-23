# ✅ CORREÇÃO CRÍTICA DE SEGURANÇA - user_id Hardcoded (23/01/2026)

**Status:** 🟢 Corrigido localmente - Aguardando deploy em produção  
**Severidade:** 🔴 CRÍTICA  
**Impacto:** Vazamento de dados entre usuários

---

## 📋 Resumo Executivo

**Problema identificado:**
- Usuário fazia login com conta "teste"
- Dashboard mostrava dados corretos (teste)
- Ao navegar para Transações → Exibia dados do admin (user_id=1)

**Causa raiz:**
- Função `get_current_user_id()` retornava `1` hardcoded em vez de extrair do JWT
- Domínio `exclusoes` tinha função mock própria retornando `1`

**Correção aplicada:**
- ✅ Removida função insegura de `dependencies.py`
- ✅ Corrigido domínio `exclusoes/router.py`
- ✅ Todos os endpoints agora exigem JWT válido (erro 401 se ausente)

---

## 🔍 Arquivos Modificados

### 1. `app_dev/backend/app/shared/dependencies.py`

**ANTES (INSEGURO):**
```python
def get_current_user_id() -> int:
    """⚠️ DEPRECADO"""
    return 1  # ❌ SEMPRE retorna admin!

# Sobrescrita (não funcionava corretamente)
get_current_user_id = get_current_user_from_jwt
```

**DEPOIS (SEGURO):**
```python
def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    🔒 Retorna user_id do JWT (obrigatório)
    Levanta 401 se token ausente/inválido
    """
    if not authorization:
        raise HTTPException(401, "Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    user_id = extract_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(401, "Token inválido")
    
    return user_id
```

### 2. `app_dev/backend/app/domains/exclusoes/router.py`

**ANTES (INSEGURO):**
```python
def get_current_user_id():
    """Mock - retorna user_id fixo"""
    return 1  # ❌ Função mock local
```

**DEPOIS (SEGURO):**
```python
from app.shared.dependencies import get_current_user_id  # ✅ Usa função segura
# Função mock removida
```

---

## ✅ Testes de Validação (Local)

### Teste 1: Login com Usuário Teste
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"teste123"}'

# ✅ Resultado:
{
  "access_token": "eyJ...",
  "user": {
    "id": 4,              # ✅ user_id correto
    "email": "teste@email.com"
  }
}
```

### Teste 2: Listar Transações com Token Teste
```bash
curl "http://localhost:8000/api/v1/transactions/list?page=1&limit=5" \
  -H "Authorization: Bearer eyJ..."

# ✅ Resultado:
{
  "transactions": [
    {
      "id": 10221,
      "user_id": 4,        # ✅ Todas com user_id=4
      "Estabelecimento": "CONTA VIVO",
      "IdTransacao": "TESTE_4_0_..."  # ✅ Prefixo correto
    },
    {
      "id": 10222,
      "user_id": 4,        # ✅ user_id correto
      ...
    }
  ]
}
```

### Teste 3: Sem Token (Deve Falhar com 401)
```bash
curl "http://localhost:8000/api/v1/transactions/list"

# ✅ Resultado:
{
  "detail": "Token de autenticação não fornecido"
}
# Status: 401 Unauthorized ✅
```

---

## 🚨 PRÓXIMOS PASSOS OBRIGATÓRIOS

### 1. Deploy em Produção (URGENTE!)

```bash
# No servidor de produção
ssh user@64.23.241.43

# 1. Fazer backup do banco
cd /var/www/finup
./scripts/deploy/backup_daily.sh

# 2. Pull do código corrigido
git pull origin main

# 3. Instalar dependências (caso necessário)
cd app_dev
source venv/bin/activate
pip install -r requirements.txt

# 4. Reiniciar backend
cd /var/www/finup
systemctl restart finup-backend

# 5. Verificar logs
journalctl -u finup-backend -f --since "1 minute ago"

# 6. Testar login
curl -X POST https://meudominio.com.br/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"teste123"}'

# 7. Testar isolamento (com token)
curl "https://meudominio.com.br/api/v1/transactions/list" \
  -H "Authorization: Bearer <token_teste>"
# Deve retornar apenas transações do usuário teste!

# 8. Testar sem token
curl "https://meudominio.com.br/api/v1/transactions/list"
# Deve retornar 401!
```

### 2. Validação de Isolamento

**Criar usuário de teste adicional:**
```bash
curl -X POST https://meudominio.com.br/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste2@email.com","password":"teste123","nome":"Teste 2"}'
```

**Testar que teste2 NÃO vê dados de teste:**
```bash
# Login teste2
TOKEN2=$(curl -X POST https://meudominio.com.br/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste2@email.com","password":"teste123"}' \
  | jq -r '.access_token')

# Buscar transações de teste2
curl "https://meudominio.com.br/api/v1/transactions/list" \
  -H "Authorization: Bearer $TOKEN2" \
  | jq '.transactions[].user_id' | sort -u
# Deve retornar APENAS o user_id de teste2!
```

### 3. Atualizar requirements.txt (se necessário)

```bash
# Se slowapi foi adicionado e não está no requirements.txt
cd app_dev/backend
source venv/bin/activate
pip freeze | grep slowapi >> requirements.txt
git add requirements.txt
git commit -m "chore: adiciona slowapi ao requirements.txt"
git push origin main
```

---

## 🛡️ Medidas Preventivas Implementadas

### 1. Função Única de Autenticação
- ✅ `get_current_user_id()` agora é única e segura
- ✅ SEMPRE extrai user_id do JWT
- ✅ NUNCA usa fallback ou valores hardcoded

### 2. Validação Obrigatória de JWT
- ✅ Todos os endpoints (exceto /login, /register) exigem JWT
- ✅ Erro 401 se token ausente ou inválido
- ✅ Nenhum acesso sem autenticação

### 3. Remoção de Funções Mock
- ✅ Removida função mock de `exclusoes/router.py`
- ✅ Todos os domínios usam `shared.dependencies.get_current_user_id`

---

## 📚 Lições Aprendidas

### 1. NUNCA Usar Valores Hardcoded em Autenticação
**Problema:**
- `return 1` criou falsa sensação de segurança
- Comentário "DEPRECADO" não impediu uso

**Solução:**
- Remover código deprecado IMEDIATAMENTE
- Se deprecado, fazer `raise NotImplementedError()`

### 2. Sobrescrita de Função em Python É Perigosa
**Problema:**
- `get_current_user_id = get_current_user_from_jwt` no final do arquivo
- Imports anteriores pegavam função antiga

**Solução:**
- Definir função UMA ÚNICA VEZ com implementação correta
- Nunca usar aliases tardios

### 3. Funções Mock Devem Ser Explícitas
**Problema:**
- Função mock local sem indicação clara de que era temporária
- Esquecida durante refatoração

**Solução:**
- Se usar mock, nomear como `_mock_get_current_user_id`
- Adicionar `raise NotImplementedError("MOCK - NÃO USAR EM PROD")`

---

## 🔍 Auditoria de Segurança

### Verificação de Outros Hardcoded (Realizada)

```bash
# Buscar outros user_id=1 hardcoded
grep -r "user_id.*=.*1" app_dev/backend/app/domains --include="*.py"

# ✅ Resultado: 
# - Apenas em processadores de upload (internos, não expostos)
# - Processadores são chamados pelo router que JÁ passa user_id correto
# - Não há vazamento de dados
```

### Endpoints Validados

✅ **Transactions** - `/api/v1/transactions/*`
- ✅ Usa `get_current_user_id` do shared.dependencies
- ✅ Filtra por user_id corretamente

✅ **Dashboard** - `/api/v1/dashboard/*`
- ✅ Usa `get_current_user_id` do shared.dependencies

✅ **Categorias** - `/api/v1/categories/*`
- ✅ Usa `get_current_user_id` do shared.dependencies

✅ **Grupos** - `/api/v1/grupos/*`
- ✅ Usa `get_current_user_id` do shared.dependencies

✅ **Upload** - `/api/v1/upload/*`
- ✅ Usa `get_current_user_id` do shared.dependencies

✅ **Exclusões** - `/api/v1/exclusoes/*`
- ✅ Corrigido - agora usa função segura

---

## 📊 Histórico

| Data       | Ação                                      | Status |
|------------|-------------------------------------------|--------|
| 23/01/2026 | Vulnerabilidade reportada pelo usuário    | 🔴 Crítico |
| 23/01/2026 | Causa raiz identificada                   | 🔍 Investigando |
| 23/01/2026 | Correção implementada localmente          | ✅ Corrigido (local) |
| 23/01/2026 | Testes de validação executados            | ✅ Passou |
| 23/01/2026 | Aguardando deploy em produção             | ⏳ Pendente |
| 23/01/2026 | Deploy em produção                        | ⏳ Pendente |
| 23/01/2026 | Validação em produção                     | ⏳ Pendente |

---

## 🎯 Checklist de Conclusão

### Ambiente Local
- [x] ✅ Correção implementada
- [x] ✅ Testes de isolamento executados
- [x] ✅ Validação de erro 401 sem token
- [x] ✅ Código commitado no git

### Servidor de Produção (URGENTE!)
- [ ] ⏳ Backup do banco executado
- [ ] ⏳ Git pull do código corrigido
- [ ] ⏳ Backend reiniciado
- [ ] ⏳ Login teste validado
- [ ] ⏳ Isolamento de dados validado
- [ ] ⏳ Erro 401 sem token validado
- [ ] ⏳ Logs verificados

### Pós-Deploy
- [ ] ⏳ Criar teste automatizado de isolamento
- [ ] ⏳ Implementar middleware global de autenticação
- [ ] ⏳ Adicionar auditoria mensal de segurança
- [ ] ⏳ Documentar lição aprendida no CHANGELOG

---

**🚨 DEPLOY EM PRODUÇÃO URGENTE NECESSÁRIO - VULNERABILIDADE ATIVA NO SERVIDOR**

