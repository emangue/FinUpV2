# 2️⃣ Limpeza de Console Logs

**Frente:** Limpeza de Logs  
**Status:** 🟡 Mapeamento Iniciado  
**Prioridade:** 🟡 MÉDIA  
**Responsável:** A definir  
**Data Início:** A definir  
**Deadline:** A definir

---

## 🎯 Objetivo

**Limpar logs que poluem o front (console do browser)** e **implementar logs de manutenção importantes** para monitoramento do sistema.

**Foco:**
- ❌ Remover logs de debug que aparecem no console do usuário
- ❌ Remover logs temporários ("test", "debug", "chegou aqui")
- ✅ Manter/adicionar logs de erro importantes
- ✅ Adicionar logs de auditoria (login, uploads, mudanças críticas)
- ✅ Implementar logs estruturados para manutenção

---

## 📋 Escopo

### Incluído
- ✅ Mapeamento de logs expostos no console do browser
- ✅ Remoção de logs de debug temporários ("test", "debug", etc)
- ✅ Implementação de logs de manutenção importantes
- ✅ Logs de auditoria (login, logout, upload, edições críticas)
- ✅ Logs estruturados para troubleshooting
- ✅ Sistema de log levels (DEBUG, INFO, WARNING, ERROR)
- ✅ Validação que console do usuário está limpo

### Excluído
- ❌ Remoção de logs de erro (devem permanecer)
- ❌ Remoção de logs do backend (Python logging está OK)
- ❌ Logs de performance/monitoramento

---

## 🔍 Fase 1: Mapeamento (Iniciado)

### 1.1 Arquivo Base
**Path:** `/docs/planning/CONSOLE_LOGS_MAPEAMENTO.md`

Status: 🟡 **Mapeamento iniciado** (arquivo já existe)

### 1.2 Mapeamento Adicional

#### Backend (Python)
```bash
# Buscar todos os prints
grep -r "print(" app_dev/backend/app --include="*.py" | wc -l

# Buscar logs
grep -r "logger\." app_dev/backend/app --include="*.py" | wc -l
```

#### Frontend (TypeScript/JavaScript)
```bash
# Buscar console.logs
grep -r "console\.log" app_dev/frontend/src --include="*.ts" --include="*.tsx" --include="*.js" | wc -l

# Buscar console.error/warn
grep -r "console\.(error|warn)" app_dev/frontend/src --include="*.ts" --include="*.tsx" | wc -l
```

---

## 📊 Categorização de Logs

### Categorias

#### 🟢 MANTER - Logs Úteis
**Critérios:**
- Logs de erro crítico
- Logs de auditoria (login, alterações importantes)
- Logs de performance (início/fim de operações pesadas)
- Logs de segurança (tentativas de acesso negado)

**Exemplos:**
```python
# ✅ MANTER
logger.error(f"Falha ao conectar ao banco: {error}")
logger.info(f"Usuário {user_id} fez login com sucesso")
logger.warning(f"Rate limit atingido para IP {ip}")
```

```typescript
// ✅ MANTER
console.error('Falha ao carregar transações:', error)
console.warn('Token expirando em 5 minutos')
```

#### 🟡 AJUSTAR - Logs a Melhorar
**Critérios:**
- Logs informativos úteis mas muito verbosos
- Logs sem contexto suficiente
- Logs com informações sensíveis

**Exemplos:**
```python
# 🟡 AJUSTAR
print(f"Processando arquivo {filename}")  # → logger.info
print(data)  # → logger.debug com limite de chars
```

```typescript
// 🟡 AJUSTAR
console.log('Data:', data)  // → Adicionar contexto
console.log(user)  // → Remover dados sensíveis
```

#### 🔴 REMOVER - Logs Desnecessários
**Critérios:**
- Logs de debug temporários
- Logs duplicados
- Logs em loops (poluição)
- Logs que expõem dados sensíveis

**Exemplos:**
```python
# 🔴 REMOVER
print("Chegou aqui")
print("Debug:", x, y, z)
print(f"Loop iteration {i}")  # dentro de loop
print(user_password)  # NUNCA logar senhas!
```

```typescript
// 🔴 REMOVER
console.log('test')
console.log('Debug:', value)
console.log(apiKey)  // NUNCA logar secrets!
```

---

## 🛠️ Fase 2: Plano de Ação

### 2.1 Backend - Padrão de Logging

**Implementar logger adequado:**
```python
# app/core/logger.py
import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Produção: WARNING, Dev: DEBUG
    level = logging.DEBUG if settings.DEBUG else logging.WARNING
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

**Uso nos domínios:**
```python
# domains/transactions/service.py
from app.core.logger import setup_logger

logger = setup_logger(__name__)

def update_transaction(id: str, data):
    logger.info(f"Atualizando transação {id}")
    try:
        # ...
        logger.info(f"Transação {id} atualizada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao atualizar transação {id}: {e}")
        raise
```

### 2.2 Frontend - Padrão de Logging

**Implementar logger wrapper:**
```typescript
// src/core/utils/logger.ts
const isDev = process.env.NODE_ENV === 'development'

export const logger = {
  debug: (...args: any[]) => {
    if (isDev) console.log('[DEBUG]', ...args)
  },
  info: (...args: any[]) => {
    console.log('[INFO]', ...args)
  },
  warn: (...args: any[]) => {
    console.warn('[WARN]', ...args)
  },
  error: (...args: any[]) => {
    console.error('[ERROR]', ...args)
    // Aqui pode enviar para serviço de monitoramento
  }
}
```

**Uso nos componentes:**
```typescript
import { logger } from '@/core/utils/logger'

export function TransactionList() {
  useEffect(() => {
    logger.debug('Componente TransactionList montado')
    fetchTransactions()
      .then(data => logger.info('Transações carregadas:', data.length))
      .catch(err => logger.error('Erro ao carregar transações:', err))
  }, [])
}
```

---

## ✅ Fase 3: Execução

### 3.1 Backend

**Script de limpeza automática:**
```bash
# scripts/maintenance/clean_logs_backend.sh
#!/bin/bash

# Remover prints de debug óbvios
find app_dev/backend/app -name "*.py" -type f -exec sed -i '' '/print("Debug/d' {} +
find app_dev/backend/app -name "*.py" -type f -exec sed -i '' '/print("Chegou/d' {} +
find app_dev/backend/app -name "*.py" -type f -exec sed -i '' '/print("test/d' {} +

echo "Limpeza automática concluída. Revisar manualmente!"
```

**Checklist manual:**
- [ ] Buscar todos os `print(` restantes
- [ ] Avaliar cada um (manter/remover/ajustar)
- [ ] Substituir prints úteis por `logger.info/debug`
- [ ] Remover prints desnecessários
- [ ] Validar que código ainda funciona

### 3.2 Frontend

**Script de limpeza automática:**
```bash
# scripts/maintenance/clean_logs_frontend.sh
#!/bin/bash

# Remover console.logs de debug óbvios
find app_dev/frontend/src -name "*.ts*" -type f -exec sed -i '' '/console\.log("test/d' {} +
find app_dev/frontend/src -name "*.ts*" -type f -exec sed -i '' '/console\.log("debug/d' {} +

echo "Limpeza automática concluída. Revisar manualmente!"
```

**Checklist manual:**
- [ ] Buscar todos os `console.log` restantes
- [ ] Avaliar cada um (manter/remover/ajustar)
- [ ] Substituir logs úteis por `logger.info/debug`
- [ ] Remover logs desnecessários
- [ ] Validar que código ainda funciona

---

## 🧪 Fase 4: Validação

### 4.1 Validação Automática

**Garantir zero logs desnecessários:**
```bash
# Backend - não deve haver prints simples
grep -r "^[[:space:]]*print(" app_dev/backend/app --include="*.py"
# Retorno esperado: vazio ou apenas prints justificados

# Frontend - não deve haver console.log em produção
grep -r "console\.log" app_dev/frontend/src --include="*.ts*"
# Retorno esperado: apenas logs via logger wrapper
```

### 4.2 Validação Manual

**Checklist de testes:**
- [ ] Backend inicia sem logs desnecessários
- [ ] Frontend compila sem warnings de logs
- [ ] Logs de erro ainda aparecem quando apropriado
- [ ] Logs de auditoria funcionam (login, etc)
- [ ] Sem poluição de logs no console em produção
- [ ] Debug logs só aparecem em desenvolvimento

### 4.3 Teste de Produção

**Simular ambiente de produção:**
```bash
# Backend
export DEBUG=false
./scripts/deploy/quick_start.sh
# Verificar logs: apenas INFO/WARNING/ERROR

# Frontend
npm run build
npm run start
# Verificar console no browser: sem console.log de debug
```

---

## 📊 Métricas

### Progresso
```
Mapeamento:  ████████░░ 80% (arquivo base existe)
Backend:     ░░░░░░░░░░ 0/X logs revisados
Frontend:    ░░░░░░░░░░ 0/Y logs revisados
Total:       ░░░░░░░░░░ 0% concluído
```

### Logs por Categoria
```markdown
| Categoria | Backend | Frontend | Total |
|-----------|---------|----------|-------|
| 🟢 Manter |         |          |       |
| 🟡 Ajustar|         |          |       |
| 🔴 Remover|         |          |       |
| **TOTAL** |         |          |       |
```

---

## 🚧 Riscos e Bloqueadores

### Riscos
1. **Médio:** Remover logs importantes acidentalmente
2. **Baixo:** Quebrar funcionalidades ao remover logs

### Mitigações
1. Revisar cada log manualmente antes de remover
2. Testar funcionalidade após remoção
3. Usar git branches para limpeza
4. Commitar remoções em pequenos lotes

---

## 📝 Próximos Passos

1. [ ] Completar mapeamento baseado em `/docs/planning/CONSOLE_LOGS_MAPEAMENTO.md`
2. [ ] Executar busca completa de logs (backend + frontend)
3. [ ] Categorizar todos os logs encontrados
4. [ ] Implementar logger padronizado (se necessário)
5. [ ] Executar limpeza (automática + manual)
6. [ ] Validar que funcionalidades não quebraram
7. [ ] Commitar limpeza

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- [CONSOLE_LOGS_MAPEAMENTO.md](../planning/CONSOLE_LOGS_MAPEAMENTO.md)
- Python logging: https://docs.python.org/3/library/logging.html

---

**Última Atualização:** 10/02/2026
