# 📋 Proposta: Modularidade Pragmática

**Data:** 14/02/2026  
**Contexto:** [ANALISE_MODULARIDADE_2026.md](./ANALISE_MODULARIDADE_2026.md)  
**Objetivo:** Política de imports cruzados que permite acoplamento **quando necessário**, sem exigir autocontenção total

---

## 1. PRINCÍPIO GERAL

> **Regra de ouro:** Imports cruzados são permitidos quando há **justificativa de negócio** clara. O custo de desacoplar seria maior que o benefício.

Não buscamos isolamento absoluto. Buscamos:
- **Rastreabilidade** – saber por que cada dependência existe
- **Contenção** – evitar que qualquer módulo vire um "hub" sem critério
- **Exceções documentadas** – orquestradores e agregadores têm permissão explícita

---

## 2. BACKEND - DOMÍNIOS

### 2.1 Tipos de Domínio (por papel)

| Tipo | Descrição | Imports cruzados | Exemplo |
|------|-----------|-----------------|---------|
| **Orquestrador** | Coordena fluxos que envolvem múltiplos domínios | ✅ Permitido (documentado) | upload |
| **Agregador** | Consolida dados de outros domínios para exibição | ✅ Permitido | dashboard |
| **Core** | Domínio central, outros dependem dele | ✅ Aceitável | transactions, grupos |
| **Leaf** | Domínio folha, sem dependências de outros domínios | ❌ Evitar | auth, users, cards |
| **Serviço** | Oferece capacidade reutilizável | ⚠️ Depende | classification, compatibility |

### 2.2 Critérios para Imports Cruzados Permitidos

**✅ PERMITIDO** quando:

1. **Orquestração:** O domínio coordena um fluxo de negócio que naturalmente envolve outros (ex: upload processa arquivo → cria transações → atualiza grupos → classifica).
2. **Agregação:** O domínio apenas monta dados para exibição (ex: dashboard busca de transactions + budget).
3. **Bounded context:** Dois domínios formam um só conceito (ex: auth + users).
4. **Modelo compartilhado:** O modelo é usado em múltiplos domínios e a extração para `shared/` não traria ganho real (ex: `JournalEntry`).

**❌ EVITAR** quando:

1. **Conveniência:** "Importei porque estava mais perto" – não é justificativa.
2. **Lógica de negócio:** A regra pertence ao outro domínio – mover a lógica.
3. **Circular:** A → B → C → A – refatorar para quebrar o ciclo.

### 2.3 Mapa de Domínios – Política Proposta

| Domínio | Tipo | Dependências permitidas | Justificativa |
|---------|------|-------------------------|---------------|
| **upload** | Orquestrador | transactions, grupos, categories, budget, exclusoes, compatibility | Processa arquivo → cria/atualiza transações, marcações, orçamento | 
| **dashboard** | Agregador | transactions, budget | Monta métricas e gráficos |
| **classification** | Serviço | upload (processors), transactions, grupos | Classifica transações usando regras e padrões |
| **transactions** | Core | grupos, patterns, categories, budget | Transações referenciam grupos, categorias, orçamento |
| **marcacoes** | Core | grupos, categories, transactions | Marcações ligam transações a grupos |
| **budget** | Core | transactions, grupos | Orçamento usa transações e grupos |
| **auth** | Bounded context | users | Auth e users são um conceito único |
| **grupos** | Core | transactions | Grupos podem referenciar transações |

### 2.4 Obrigação: Documentar

Todo domínio que importa de 3+ outros domínios deve ter um `DOCS.md` ou seção no `__init__.py` explicando:

```python
# domains/upload/__init__.py
"""
Upload Domain - Orquestrador

Dependências permitidas (justificativa):
- transactions: cria/atualiza JournalEntry após processar arquivo
- grupos: consulta BaseGruposConfig para classificação
- categories: consulta BaseMarcacao para marcações
- budget: atualiza valor realizado após classificação
- exclusoes: aplica regras de exclusão
- compatibility: valida formato do arquivo
"""
```

---

## 3. FRONTEND - FEATURES

### 3.1 Tipos de Feature

| Tipo | Descrição | Imports cruzados | Exemplo |
|------|-----------|-----------------|---------|
| **Orquestrador** | Coordena fluxo entre telas/componentes | ✅ Permitido | upload (preview + confirm) |
| **Composição** | Monta UI de várias sub-features | ✅ Permitido | dashboard mobile (métricas + budget) |
| **Leaf** | Feature independente | ❌ Evitar | auth, goals |
| **Shared** | Componente usado por 2+ features | → Mover para `components/` | BottomNav, AddGroupDialog |

### 3.2 Regra: 2+ Features = Componente Compartilhado

Se um componente de **feature A** é usado por **feature B** (e não por página):

- **Se A orquestra B** (ex: preview orquestra upload): permitir import de A → B.
- **Se não há orquestração:** mover para `components/` ou `components/mobile/`.

**Exemplos:**

| Caso | Componente | Usado por | Ação |
|------|------------|-----------|------|
| BottomNav | dashboard | dashboard, transactions, investimentos | Mover para `components/mobile/` – não há orquestração |
| AddGroupDialog | upload | preview, upload | **Manter em upload** – preview é parte do fluxo de upload (preview → confirm). Preview orquestra o fluxo de upload. |

### 3.3 Exceção: Fluxo de Upload

O fluxo **upload → preview → confirm** é um único fluxo de negócio:

- `preview` mostra transações e permite editar (incluindo adicionar grupo)
- `AddGroupDialog` é específico do contexto de upload/preview
- **Decisão:** Import de `preview` → `upload` (AddGroupDialog) é **permitido** – preview faz parte do fluxo de upload.

**Alternativa:** Se preview e upload forem tratados como features separadas, mover `AddGroupDialog` para `components/dialogs/` – pois é usado em dois contextos (preview e upload).

### 3.4 Resumo: O Que Fazer

| Item | Ação |
|------|------|
| **BottomNav** | Mover para `components/mobile/bottom-nav.tsx` – usado por 3 features sem orquestração |
| **AddGroupDialog** | Manter em upload e documentar: "preview usa AddGroupDialog pois faz parte do fluxo de upload" |
| **Novos imports cruzados** | Perguntar: "é orquestração/agregação ou conveniência?" Só aprovar se for o primeiro |

---

## 4. CHECKLIST DE DECISÃO

Antes de criar um import cruzado, responder:

1. **É orquestração?** O módulo A coordena um fluxo que naturalmente envolve B?
2. **É agregação?** O módulo A apenas monta dados de B para exibir?
3. **É shared?** O componente é usado por 2+ features sem relação de orquestração?
4. **É conveniência?** Se sim → **não fazer**. Encontrar outra forma.

---

## 5. MUDANÇAS CONCRETAS PROPOSTAS

### 5.1 Backend (documentação)

- [ ] Adicionar `DOCS.md` ou docstring em `domains/upload/` explicando dependências
- [ ] Adicionar `DOCS.md` em `domains/dashboard/` (agregador)
- [ ] Atualizar `copilot-instructions.md` com link para esta política

### 5.2 Frontend (código)

- [ ] **Mover BottomNav** para `components/mobile/bottom-nav.tsx`
- [ ] **Manter AddGroupDialog** em upload – documentar que preview é parte do fluxo de upload
- [ ] Se houver mais dialogs compartilhados no futuro, criar `components/dialogs/`

### 5.3 Não fazer (por agora)

- [ ] ~~Extrair modelos para shared~~ – custo alto, benefício incerto
- [ ] ~~Event-driven para upload~~ – complexidade desnecessária no estágio atual
- [ ] ~~100% autocontenção~~ – não é o objetivo

---

## 6. ATUALIZAÇÃO DO COPLOT-INSTRUCTIONS

Sugestão de adição no `.github/copilot-instructions.md`:

```markdown
### Política de Imports Cruzados (Pragmática)

- **Backend:** Domínios orquestradores (upload) e agregadores (dashboard) podem importar de outros.
  Documentar dependências em DOCS.md do domínio.
- **Frontend:** Componentes usados por 2+ features sem orquestração → mover para components/.
  Preview → upload (AddGroupDialog) é permitido (fluxo de upload).
- **Regra:** Imports cruzados só quando há justificativa de negócio. Ver docs/architecture/PROPOSTA_MODULARIDADE_PRAGMATICA.md
```

---

**Documento:** Proposta de Modularidade Pragmática  
**Status:** Proposta para aprovação  
**Última atualização:** 14/02/2026
