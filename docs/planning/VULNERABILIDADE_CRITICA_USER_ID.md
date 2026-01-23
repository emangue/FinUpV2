# 🚨 VULNERABILIDADE CRÍTICA DE SEGURANÇA - user_id Hardcoded

**Data:** 23/01/2026  
**Severidade:** 🔴 **CRÍTICA**  
**Status:** 🔍 Identificada - Correção urgente necessária

---

## 📋 Sumário Executivo

Foi identificada uma **vulnerabilidade crítica de segurança** que permite que usuários vejam dados de outras contas. O problema está no arquivo `dependencies.py` que contém código contraditório sobre autenticação.

---

## 🔍 Problema Identificado

### Evidência do Bug

**Sintoma reportado pelo usuário:**
- Login com conta "teste" → Dashboard mostra "teste" ✅
- Navegação para tela Transações → App muda para conta "admin" ❌

### Causa Raiz - Código Contraditório

**Arquivo:** `app_dev/backend/app/shared/dependencies.py`

```python
# Linhas 14-22: FUNÇÃO ORIGINAL (INSEGURA)
def get_current_user_id() -> int:
    """
    ⚠️ DEPRECADO - Use get_current_user_from_jwt()
    
    Por enquanto fixo em 1 (admin padrão)  # ❌ HARDCODED!
    """
    return 1  # ❌❌❌ SEMPRE RETORNA ADMIN!

# Linha 106: TENTATIVA DE SOBRESCRITA (NÃO FUNCIONA CORRETAMENTE)
get_current_user_id = get_current_user_from_jwt  # ⚠️ Conflito
```

### Por Que o Problema Ocorre?

1. **Importações acontecem antes da linha 106:**
   - Quando `router.py` faz `from app.shared.dependencies import get_current_user_id`
   - Python importa a FUNÇÃO ORIGINAL (linha 14) ANTES de chegar na sobrescrita (linha 106)
   - Resultado: `Depends(get_current_user_id)` usa a função que retorna `1`

2. **Ordem de execução do Python:**
   ```python
   # Momento da importação em router.py:
   from app.shared.dependencies import get_current_user_id
   # ↑ Importa FUNÇÃO definida na linha 14 (return 1)
   
   # Linha 106 em dependencies.py (executada DEPOIS):
   get_current_user_id = get_current_user_from_jwt
   # ↑ Sobrescreve NO MÓDULO, mas imports anteriores já têm a função antiga
   ```

3. **Resultado:**
   - Dashboard: Pode estar usando JWT corretamente (componente novo)
   - Transações: Usa `get_current_user_id` antigo → sempre retorna `user_id=1` (admin)

---

## 🎯 Impacto da Vulnerabilidade

### Severidade: 🔴 CRÍTICA

**Dados expostos:**
- ✅ Todas as transações do user_id=1 (admin)
- ✅ Dashboard do admin
- ✅ Categorias, grupos, uploads do admin
- ✅ Orçamentos e planejamento do admin

**Usuários afetados:**
- ❌ Todos os usuários NÃO-admin veem dados do admin
- ❌ Usuário "teste" (id=2) vê dados do "admin" (id=1)
- ❌ Qualquer novo usuário vê dados do admin

**Violações:**
- 🚫 Quebra de isolamento de dados entre usuários
- 🚫 Exposição de informações financeiras sensíveis
- 🚫 Violação de privacidade (LGPD)
- 🚫 Falha de autenticação/autorização

---

## ✅ Solução Correta

### 1. Remover Função Insegura

**Antes (INSEGURO):**
```python
def get_current_user_id() -> int:
    """⚠️ DEPRECADO"""
    return 1  # ❌ NUNCA fazer isso!

# Sobrescrita (não funciona bem)
get_current_user_id = get_current_user_from_jwt
```

**Depois (SEGURO):**
```python
# REMOVER função antiga completamente

# Definir get_current_user_id como ALIAS DIRETO
def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    Retorna o ID do usuário autenticado via JWT (obrigatório)
    
    Esta função REQUER autenticação válida.
    Se o token não for fornecido ou for inválido, levanta exceção.
    
    Returns:
        user_id extraído do token JWT
        
    Raises:
        HTTPException 401: Se token não fornecido ou inválido
    """
    from fastapi import HTTPException, status
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        user_id = extract_user_id_from_token(token)
        if not user_id:
            raise ValueError("Token inválido")
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 2. Validar TODOS os Endpoints

**Verificar que TODOS os routers usam:**
```python
@router.get("/transactions")
def list_transactions(
    user_id: int = Depends(get_current_user_id),  # ✅ Agora seguro
    db: Session = Depends(get_db)
):
    pass
```

**Endpoints a validar:**
- ✅ `/transactions/*` - Transações
- ✅ `/dashboard/*` - Dashboard
- ✅ `/categories/*` - Categorias
- ✅ `/grupos/*` - Grupos
- ✅ `/upload/*` - Uploads
- ✅ `/users/*` - Usuários (menos /login, /register)

### 3. Testes de Validação

**Teste 1: Login com usuário teste**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"teste123"}'

# Resposta esperada:
{"access_token":"eyJ...","user":{"id":2,"email":"teste@email.com"}}

# Testar transações com token
curl http://localhost:8000/api/v1/transactions/list \
  -H "Authorization: Bearer eyJ..."

# Resposta esperada: Transações do user_id=2 (não do user_id=1!)
```

**Teste 2: Sem token (deve falhar)**
```bash
curl http://localhost:8000/api/v1/transactions/list

# Resposta esperada: 401 Unauthorized
```

---

## 📋 Checklist de Correção

### Ambiente Local (Dev)

- [ ] 1. Remover função `get_current_user_id()` antiga (linha 14-22)
- [ ] 2. Renomear `get_current_user_from_jwt` → `get_current_user_id`
- [ ] 3. Remover linha 106 (sobrescrita)
- [ ] 4. Testar login com usuário teste
- [ ] 5. Verificar que transações filtram por user_id correto
- [ ] 6. Verificar logs: `tail -f temp/logs/backend.log`
- [ ] 7. Commitar correção no git

### Servidor de Produção (URGENTE!)

- [ ] 1. SSH no servidor
- [ ] 2. Fazer backup do banco: `./scripts/deploy/backup_daily.sh`
- [ ] 3. Pull do código corrigido: `git pull origin main`
- [ ] 4. Reiniciar backend: `systemctl restart finup-backend`
- [ ] 5. Testar login com conta teste
- [ ] 6. Verificar logs: `journalctl -u finup-backend -f`
- [ ] 7. Confirmar isolamento de dados OK

---

## 🔒 Medidas Preventivas

### 1. Nunca Mais Usar Hardcoded user_id

**❌ PROIBIDO:**
```python
user_id = 1  # NUNCA fazer isso!
return 1     # NUNCA fazer isso!
```

**✅ SEMPRE:**
```python
user_id: int = Depends(get_current_user_id)  # Extrai do JWT
```

### 2. Middleware Global de Autenticação

**Adicionar middleware que valida JWT em TODAS as rotas:**
```python
# app/main.py
from app.core.middleware import AuthMiddleware

app.add_middleware(AuthMiddleware, exclude_paths=["/login", "/register", "/docs"])
```

### 3. Auditoria de Segurança Mensal

**Verificações obrigatórias:**
- [ ] Grep por `return 1` em dependencies
- [ ] Grep por `user_id = 1` em routers
- [ ] Testar login com 2+ usuários diferentes
- [ ] Validar isolamento de dados no banco
- [ ] Revisar logs de autenticação 401/403

### 4. Testes Automatizados

**Criar testes de isolamento:**
```python
# tests/test_auth_isolation.py
def test_user_cannot_see_other_user_transactions():
    # Login user 1
    token1 = login("admin@email.com", "admin123")
    
    # Login user 2
    token2 = login("teste@email.com", "teste123")
    
    # Buscar transações com token do user 2
    response = client.get(
        "/api/v1/transactions/list",
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # Validar que NENHUMA transação do user 1 aparece
    transactions = response.json()["items"]
    for t in transactions:
        assert t["user_id"] == 2  # NUNCA 1!
```

---

## 🚨 Próximos Passos Imediatos

1. **URGENTE:** Corrigir `dependencies.py` no local
2. **URGENTE:** Testar correção localmente
3. **URGENTE:** Fazer backup do servidor
4. **URGENTE:** Deploy da correção em produção
5. **URGENTE:** Testar isolamento no servidor
6. Criar testes automatizados
7. Implementar middleware global
8. Documentar lição aprendida
9. Adicionar auditoria mensal

---

## 📚 Lições Aprendidas

### 1. Sobrescrita de Função em Python É Perigosa

**Problema:**
- Imports acontecem antes de sobrescritas
- Módulos diferentes podem ter versões diferentes da função

**Solução:**
- Definir função UMA ÚNICA VEZ com implementação correta
- Nunca usar aliases tardios (`func = other_func` no final do arquivo)

### 2. Hardcoded Values São Vulnerabilidades

**Problema:**
- `return 1` cria falsa sensação de segurança
- Comentário "DEPRECADO" não impede uso

**Solução:**
- Remover código deprecado IMEDIATAMENTE
- Se deprecado, fazer `raise NotImplementedError("Use nova_funcao()")`

### 3. Autenticação Deve Ser Obrigatória Por Padrão

**Problema:**
- Fallback para user_id=1 quando sem token

**Solução:**
- SEMPRE retornar 401 se token não fornecido
- Nenhum endpoint (exceto login/register) deve funcionar sem JWT

---

## 📊 Histórico de Alterações

| Data       | Ação                                      | Autor   |
|------------|-------------------------------------------|---------|
| 23/01/2026 | Vulnerabilidade identificada              | Emanuel |
| 23/01/2026 | Documento de auditoria criado             | Copilot |
| 23/01/2026 | Correção implementada localmente          | Pendente |
| 23/01/2026 | Deploy em produção                        | Pendente |
| 23/01/2026 | Validação de isolamento em prod           | Pendente |

---

**🚨 ESTE É UM INCIDENTE DE SEGURANÇA CRÍTICO - CORREÇÃO URGENTE NECESSÁRIA**
