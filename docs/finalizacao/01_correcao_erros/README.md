# 1️⃣ Correção de Erros - app_dev

**Frente:** Correção de Erros  
**Status:** � Mapeamento Completo  
**Prioridade:** 🔴 CRÍTICA  
**Responsável:** A definir  
**Data Início:** 10/02/2026  
**Deadline:** A definir

---

## 📊 Progresso do Mapeamento

- ✅ **Fase 0 - Mapeamento:** Completo (17 erros identificados)
- ✅ **Fase 1 - Análise de Causa:** Completo
- ✅ **Fase 2 - Priorização:** Completo (9 P0, 6 P1, 2 P2)
- ✅ **Fase 3 - Investigação:** ✅ COMPLETA (10/02/2026 - 30min)
  - ✅ Backend Goal Schema analisado
  - ✅ Preview occurrences investigado
  - ⚠️ **DESCOBERTA CRÍTICA:** Interface Goal completamente errada!
- 🔄 **Fase 4 - Execução:** EM ANDAMENTO (10/02/2026 21:45)
  - ✅ Interface Goal reescrita (features/goals/types/index.ts)
  - ✅ EditGoalModal corrigido (4 erros resolvidos)
  - ⏳ ManageGoalsListItem (próximo)
  - ⏳ manage/page.tsx (próximo)
  - ⏳ Demais componentes
- ⏳ **Fase 5 - Testes Gerais:** Não iniciado (todas as telas)
- ⏳ **Fase 6 - Validação Final:** Não iniciado

### Erros Encontrados:
- **Frontend:** 17 erros TypeScript → ⚠️ **Interface Goal precisa reescrita completa**
- **Backend:** 0 erros de sintaxe
- **Tempo Estimado:** ⚠️ **8-10 horas** (interface Goal mais complexa que esperado)

### ⚠️ Descobertas Críticas da Investigação:
1. **Interface Goal completamente errada:**
   - Campos inexistentes: `nome`, `descricao`, `frequencia`, `ativo`, `progresso` aninhado
   - Campos com nome errado: `valor_alvo` → `valor_planejado`, `prazo` → `mes_referencia`
   - Campo `categoria` → `categoria_geral`
2. **Campo `occurrences` não existe** → Remover sort
3. **Impacto:** TODOS os componentes de Goals precisam ajuste

---

## 📁 Documentos Gerados

1. ✅ **[MAPEAMENTO_FRONTEND.md](./MAPEAMENTO_FRONTEND.md)** - 17 erros detalhados
2. ✅ **[MAPEAMENTO_BACKEND.md](./MAPEAMENTO_BACKEND.md)** - Backend sem erros de sintaxe
3. ✅ **[PRIORIZACAO_DETALHADA.md](./PRIORIZACAO_DETALHADA.md)** - Matriz de decisão
4. ✅ **[CHECKLIST_CORRECAO.md](./CHECKLIST_CORRECAO.md)** - Checklist executável
5. ✅ **INVESTIGACAO_GOALS.md** (/tmp/) - Análise completa Goal schema
6. ✅ **INVESTIGACAO_OCCURRENCES.md** (/tmp/) - Análise preview
7. ⏳ **RELATORIO_FINAL.md** - A gerar após correções

---

## 🎯 Objetivo

Mapear e corrigir todos os erros na pasta `app_dev/` que estão causando marcações vermelhas no VS Code, garantindo que o código esteja limpo e funcional.

---

## 📋 Escopo

### Incluído
- ✅ Mapeamento completo de arquivos com erro
- ✅ Identificação das causas dos erros
- ✅ Correção de erros TypeScript/JavaScript
- ✅ Correção de erros Python
- ✅ Correção de imports quebrados
- ✅ Correção de tipos/interfaces
- ✅ Validação pós-correção

### Excluído
- ❌ Refatoração de código funcional
- ❌ Otimizações de performance
- ❌ Mudanças de arquitetura

---

## 🔍 Fase 1: Mapeamento

### 1.1 Backend (Python)
**Path:** `app_dev/backend/`

**Categorias de Erro:**
- [ ] Imports não resolvidos
- [ ] Tipos/anotações incorretas
- [ ] Variáveis não definidas
- [ ] Funções/métodos não encontrados
- [ ] Erros de sintaxe
- [ ] Outros

**Arquivo de Mapeamento:**
```markdown
| Arquivo | Linha | Erro | Categoria | Prioridade |
|---------|-------|------|-----------|------------|
|         |       |      |           |            |
```

### 1.2 Frontend (TypeScript/React)
**Path:** `app_dev/frontend/`

**Categorias de Erro:**
- [ ] Imports não resolvidos
- [ ] Tipos TypeScript incorretos
- [ ] Propriedades faltando
- [ ] Hooks mal utilizados
- [ ] Componentes não encontrados
- [ ] Erros de compilação
- [ ] Outros

**Arquivo de Mapeamento:**
```markdown
| Arquivo | Linha | Erro | Categoria | Prioridade |
|---------|-------|------|-----------|------------|
|         |       |      |           |            |
```

---

## 🛠️ Fase 2: Análise de Causas

### Causas Comuns Identificadas

**Backend:**
1. Imports de módulos antigos (arquitetura anterior)
2. Paths incorretos após refatoração modular
3. Tipos Python faltando anotações
4. Dependências não instaladas

**Frontend:**
5. Imports de componentes movidos/renomeados
6. Props interfaces incompletas
7. Tipos retorno de API desatualizados
8. Dependências @types faltando

**Comum:**
9. Arquivos deletados mas ainda referenciados
10. Configuração TypeScript/Python desatualizada

---

## 🔧 Fase 3: Plano de Correção

### Priorização
**P0 - BLOQUEANTE:** Erros que impedem compilação/execução  
**P1 - CRÍTICO:** Erros que afetam funcionalidades principais  
**P2 - IMPORTANTE:** Erros que afetam funcionalidades secundárias  
**P3 - MENOR:** Warnings e erros de linting  

### Estratégia de Correção

#### 3.1 Backend
```bash
# 1. Validar ambiente virtual
cd app_dev/backend
source venv/bin/activate

# 2. Verificar dependências
pip list | grep -i <package_name>

# 3. Verificar imports
python -c "from app.domains.transactions import models"

# 4. Executar linter
pylint app/ --disable=C,R
mypy app/ --ignore-missing-imports
```

#### 3.2 Frontend
```bash
# 1. Verificar dependências
cd app_dev/frontend
npm list

# 2. Limpar cache e reinstalar
rm -rf node_modules .next
npm install

# 3. Executar type-check
npm run type-check  # ou tsc --noEmit

# 4. Build de teste
npm run build
```

---

## ✅ Fase 4: Execução

### Checklist de Correção

**Por arquivo com erro:**
- [ ] Identificar erro exato
- [ ] Entender causa raiz
- [ ] Implementar correção
- [ ] Validar que erro sumiu
- [ ] Testar funcionalidade relacionada
- [ ] Commitar correção isolada

**Padrão de commit:**
```bash
git commit -m "fix(backend): corrige import quebrado em transactions/service.py"
git commit -m "fix(frontend): adiciona tipo faltante em TransactionProps"
```

---

## 🧪 Fase 5: Validação

### Backend
```bash
# 1. Sem erros de sintaxe
python -m py_compile app/**/*.py

# 2. Servidor inicia sem erros
./scripts/deploy/quick_start.sh
tail -f temp/logs/backend.log | grep -i error

# 3. Health check OK
curl http://localhost:8000/api/health
```

### Frontend
```bash
# 1. Build sem erros
npm run build

# 2. Type-check limpo
npm run type-check

# 3. Servidor inicia sem erros
npm run dev
# Abrir http://localhost:3000
```

### Integração
```bash
# 1. Testar fluxo completo
# - Login
# - Dashboard carrega
# - Upload funciona
# - Edição de transação funciona
# - Navegação entre telas funciona
```

---

## 📊 Métricas

### Progresso
```
Backend:  ███░░░░░░░ X/Y erros corrigidos
Frontend: ███░░░░░░░ X/Y erros corrigidos
Total:    ███░░░░░░░ X/Y erros corrigidos (0%)
```

### Erros por Categoria
```markdown
| Categoria            | Backend | Frontend | Total |
|----------------------|---------|----------|-------|
| Imports              |         |          |       |
| Tipos                |         |          |       |
| Sintaxe              |         |          |       |
| Dependências         |         |          |       |
| Outros               |         |          |       |
```

---

## 🚧 Riscos e Bloqueadores

### Riscos Identificados
1. **Alto:** Correções podem quebrar funcionalidades existentes
2. **Médio:** Tempo de mapeamento pode ser maior que esperado
3. **Médio:** Erros podem estar relacionados (corrigir um quebra outro)

### Mitigações
1. Testar cada correção isoladamente
2. Usar git branches para correções grandes
3. Manter backups antes de correções massivas
4. Priorizar erros bloqueantes primeiro

---

## 📝 Próximos Passos

1. [ ] Executar mapeamento completo (usar `get_errors` do Copilot)
2. [ ] Preencher tabelas de mapeamento
3. [ ] Priorizar erros (P0 → P3)
4. [ ] Iniciar correções por prioridade
5. [ ] Validar continuamente
6. [ ] Atualizar métricas de progresso

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](./PLANO_FINALIZACAO.md)
- Copilot Tool: `get_errors` - ver erros no workspace
- [Documentação Arquitetura](../architecture/MODULARIDADE.md)

---

**Última Atualização:** 10/02/2026
