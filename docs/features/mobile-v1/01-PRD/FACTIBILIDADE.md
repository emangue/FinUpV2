# Análise de Factibilidade - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.0  
**Analisado por:** Tech Team  

---

## 1. Análise Backend - APIs Disponíveis

### 1.1 Budget (Metas) - ✅ FACTÍVEL

#### Tabelas Existentes (4 tabelas)
```sql
1. budget_planning          -- Planejamento por GRUPO (ex: Casa, Cartão)
2. budget_geral            -- Meta geral por CATEGORIA_GERAL (categorias amplas)
3. budget_categoria_config -- Configuração de categorias customizáveis
4. budget_geral_historico  -- Histórico de ajustes automáticos
```

#### APIs Disponíveis (15 endpoints)
```
✅ GET /budget/geral?mes_referencia=YYYY-MM           # Listar metas do mês
✅ POST /budget/geral/bulk-upsert                     # Salvar múltiplas metas
✅ GET /budget/geral/grupos-disponiveis               # Listar grupos (dropdowns)
✅ GET /budget/categorias-config                      # Config de categorias
✅ POST /budget/categorias-config                     # Criar categoria
✅ PUT /budget/categorias-config/reordenar            # Drag & drop
✅ DELETE /budget/categorias-config/{id}              # Deletar categoria
✅ GET /budget/detalhamento-media                     # Média 3 meses + drill-down
✅ POST /budget/bulk-upsert                           # Salvar budget detalhado
```

**Conclusão:** ✅ **Todas as funcionalidades solicitadas já têm endpoints prontos!**

---

### 1.2 Dashboard - ✅ FACTÍVEL

#### APIs Disponíveis
```
✅ GET /dashboard/metrics?year=X&month=Y              # Métricas gerais
✅ GET /dashboard/chart-data?year=X&month=Y           # Gráfico 12 meses
✅ GET /dashboard/categories?year=X&month=Y           # Gastos por categoria
✅ GET /dashboard/budget-vs-actual?year=X&month=Y     # Realizado vs Planejado
✅ GET /dashboard/budget-vs-actual?year=X&ytd=true    # YTD (Year to Date)
```

**Funcionalidades identificadas:**
- ✅ Suporte a YTD (Year to Date) já implementado
- ✅ Top 5 + "Demais" já implementado no desktop
- ✅ Drill-down de grupos → subgrupos via modal existente

**Conclusão:** ✅ **APIs prontas, lógica YTD já existe!**

---

### 1.3 Transações - ✅ FACTÍVEL

#### APIs Disponíveis
```
✅ GET /transactions/list                             # Lista com filtros avançados
✅ GET /transactions/grupos-com-media                 # Grupos com média 3 meses
✅ GET /transactions/{id}                             # Buscar por ID
✅ PATCH /transactions/update/{id}                    # Atualizar
✅ DELETE /transactions/{id}                          # Deletar
✅ GET /transactions/filtered-total                   # Soma com filtros
```

**Conclusão:** ✅ **Todos os endpoints necessários existem**

---

### 1.4 Estrutura de Grupos → Subgrupos

#### Relacionamento no Banco
```
journal_entries (transações)
├── GRUPO (ex: Casa, Cartão de Crédito, Saúde)
└── SUBGRUPO (ex: Aluguel, Netflix, Consulta)
    └── TipoGasto (ex: Fixo, Ajustável, Variável)
        └── CategoriaGeral (ex: Despesa, Receita)
```

#### API para Drill-down ✅ **JÁ EXISTE!**
```python
# ✅ Endpoint COMPLETO já implementado no backend
GET /api/v1/dashboard/subgrupos-by-tipo?year=2026&month=2&grupo=Casa

# Suporta YTD (Year to Date)
GET /api/v1/dashboard/subgrupos-by-tipo?year=2026&ytd=true&grupo=Casa

# Retorna:
{
  "subgrupos": [
    { "subgrupo": "Aluguel", "valor": 1500.00, "percentual": 71.4 },
    { "subgrupo": "Condomínio", "valor": 400.00, "percentual": 19.0 },
    { "subgrupo": "IPTU", "valor": 200.50, "percentual": 9.6 }
  ],
  "total_realizado": 2100.50,
  "total_planejado": 2500.00
}
```

**Frontend desktop JÁ USA este endpoint:**
- Arquivo: `app_dev/frontend/src/features/dashboard/components/tipo-gasto-breakdown-modal.tsx`
- Linha 59-60: Chama `subgrupos-by-tipo` com YTD support
- Modal desktop mostra tabela de subgrupos com valores e percentuais

**Conclusão:** ✅ **Endpoint COMPLETO - só precisa adaptar Modal → Bottom Sheet mobile (2-3h)**

---

## 2. Análise de Funcionalidades Solicitadas

### 2.1 Edição de Metas - ✅ FACTÍVEL

#### Requisitos do Usuário
1. ✅ **Fácil de atualizar** - Bottom sheet com teclado numérico nativo
2. ✅ **Por mês específico** - Backend usa `mes_referencia` (YYYY-MM)
3. ✅ **Copiar mês anterior** - API `GET /budget/geral?mes_referencia=YYYY-MM` já existe
4. ✅ **Colar para ano inteiro (2026)** - ❌ **NÃO EXISTE** - **CRIAR NOVO ENDPOINT**
5. ✅ **Mostrar todos os grupos** - Frontend lista todos (não só top 5)
6. ✅ **Clicar no grupo → ver subgrupos** - ✅ **JÁ EXISTE** - `GET /dashboard/subgrupos-by-tipo` (adaptar modal → bottom sheet)

#### Novas Funcionalidades Necessárias

**1. Copiar para Ano Inteiro** ⚠️ **CRIAR ENDPOINT (2-3h)**
```python
# CRIAR: POST /budget/geral/copy-to-year
{
  "mes_origem": "2026-01",           # Mês a copiar
  "ano_destino": 2026,               # Copiar para todos os meses de 2026
  "substituir_existentes": false     # Se true, sobrescreve meses já preenchidos
}

# Resposta
{
  "meses_criados": 11,               # Jan já existia, criou Fev-Dez
  "meses_atualizados": 0,
  "meses_ignorados": 1               # Jan (origem)
}
```

**Conclusão:** ✅ **95% pronto. Falta APENAS 1 endpoint novo (2-3h)**

---

### 2.2 Dashboard Mobile - Top 5 + Demais

#### Implementação Desktop (Já Existe!)
```tsx
// app_dev/frontend/src/features/dashboard/components/budget-vs-actual.tsx
// Linha 154-190

// Pegar top 5
const top5 = sortedItems.slice(0, 5);

// Agrupar os demais
const others = sortedItems.slice(5);
const demaisItem = {
  grupo: 'Demais',
  realizado: others.reduce((sum, item) => sum + item.realizado, 0),
  planejado: others.reduce((sum, item) => sum + item.planejado, 0),
  tipos_inclusos: others // Lista completa
};
```

**Comportamento Desktop:**
- ✅ Mostra top 5 categorias
- ✅ Agrupa demais em "Demais"
- ✅ Clicar em "Demais" → abre modal com lista completa
- ✅ Clicar em grupo normal → abre modal com subgrupos

**Adaptação Mobile:**
- ✅ Mesmo comportamento (já implementado)
- ⚠️ Modal → substituir por **Bottom Sheet** (padrão mobile)

**Conclusão:** ✅ **Lógica pronta, só precisa adaptar UI (modal → bottom sheet)**

---

### 2.3 Filtro YTD (Year to Date)

#### Implementação Desktop (Já Existe!)
```tsx
// app_dev/frontend/src/features/dashboard/components/budget-vs-actual.tsx
// Linha 52-54

const url = month === 'all' 
  ? `${apiUrl}/dashboard/budget-vs-actual?year=${year}&ytd=true`
  : `${apiUrl}/dashboard/budget-vs-actual?year=${year}&month=${month}`;
```

**Backend suporta:**
```python
# ✅ API já implementada
GET /dashboard/budget-vs-actual?year=2026&ytd=true
# Retorna dados agregados de Jan-Dez 2026
```

**Adaptação Mobile:**
- ✅ Adicionar toggle **[Mês] / [YTD]** ao lado do MonthScrollPicker
- ✅ Quando YTD ativo, desabilitar scroll de meses (fixar em "2026 - Ano Todo")

**Conclusão:** ✅ **Backend pronto, só adicionar toggle no frontend**

---

### 2.4 MonthScrollPicker - ✅ FACTÍVEL

#### Requisito
Substituir dropdown por scroll horizontal de pills

#### Implementação
- ✅ CSS nativo: `overflow-x: auto` + `scroll-snap-type: x mandatory`
- ✅ JavaScript: Gerar últimos 12 meses + próximos 3
- ✅ Acessibilidade: ARIA role="tablist" + role="tab"
- ✅ Performance: Virtualization não necessária (≤15 itens)

**Conclusão:** ✅ **100% factível com CSS/React padrão**

---

## 3. Comparação Desktop vs Mobile

### 3.1 Budget Detalhado

| Feature | Desktop | Mobile (Proposto) | Factibilidade |
|---------|---------|-------------------|---------------|
| Listar categorias | Accordion expansível | Lista vertical de `TrackerCard` | ✅ Factível |
| Editar valor | Input inline | Bottom sheet com teclado numérico | ✅ Factível |
| Copiar mês anterior | Botão "Copiar Mês Anterior" | Mesmo botão | ✅ Já existe |
| Copiar para ano inteiro | ❌ Não existe | Botão "Colar para 2026" | ⚠️ CRIAR ENDPOINT |
| Filtro de mês | Dropdown | Scroll horizontal | ✅ Factível |
| Filtro YTD | ❌ Não existe na tela | Toggle [Mês/YTD] | ⚠️ Adaptar frontend |
| Drill-down Grupo → Subgrupos | Modal desktop | Bottom sheet mobile | ⚠️ CRIAR ENDPOINT |
| Drag & drop reordenar | ✅ Sim (dnd-kit) | ❌ Não (mobile) | ✅ Não necessário mobile |
| Adicionar categoria | Modal + form | ❌ Não (usar desktop) | ✅ Feature desktop-only |

**Conclusão:** ✅ **95% factível. Criar 2 endpoints novos.**

---

### 3.2 Dashboard

| Feature | Desktop | Mobile (Proposto) | Factibilidade |
|---------|---------|-------------------|---------------|
| Métricas gerais | 4 cards lado a lado | 2 cards verticais | ✅ Já existe |
| Gráfico histórico | Sempre visível | Colapsável (accordion) | ✅ Já existe |
| Filtro de mês | Dropdown | Scroll horizontal | ✅ Factível |
| Filtro YTD | `month='all'` | Toggle [Mês/YTD] | ✅ Backend pronto |
| Top 5 + Demais | ✅ Implementado | Reutilizar lógica | ✅ Já existe |
| Clicar grupo → subgrupos | Modal com subgrupos | Bottom sheet | ⚠️ Criar endpoint |
| Clicar "Demais" → lista | Modal com lista | Bottom sheet | ✅ Já existe |

**Conclusão:** ✅ **90% factível. Adaptar modals para bottom sheets.**

---

## 4. Novos Endpoints Necessários

### 4.1 Copiar Meta para Ano Inteiro

```python
# app_dev/backend/app/domains/budget/router.py

@router.post("/budget/geral/copy-to-year", summary="Copiar meta para ano inteiro")
def copy_budget_to_year(
    data: dict,  # { mes_origem, ano_destino, substituir_existentes }
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Copia metas de um mês para todos os meses de um ano
    
    Body:
    - mes_origem: str (YYYY-MM) - Mês a copiar (ex: "2026-01")
    - ano_destino: int - Ano destino (ex: 2026)
    - substituir_existentes: bool - Se true, sobrescreve meses já preenchidos
    
    Returns:
    - meses_criados: int - Quantidade de meses criados
    - meses_atualizados: int - Quantidade de meses atualizados
    - meses_ignorados: int - Quantidade de meses ignorados (já existiam)
    """
    service = BudgetService(db)
    return service.copy_budget_to_year(
        user_id=user_id,
        mes_origem=data["mes_origem"],
        ano_destino=data["ano_destino"],
        substituir_existentes=data.get("substituir_existentes", False)
    )
```

**Esforço:** 🟢 Baixo (2-3 horas)  
**Prioridade:** 🔴 Alta (requisito crítico para personas)

---

### 4.2 Drill-down Grupo → Subgrupos

```python
# app_dev/backend/app/domains/transactions/router.py (ou budget/router.py)

@router.get("/transactions/grupo-breakdown", summary="Detalhamento grupo → subgrupos")
def get_grupo_breakdown(
    grupo: str = Query(..., description="Nome do grupo"),
    year: int = Query(..., description="Ano"),
    month: Optional[int] = Query(None, description="Mês (se None, retorna ano inteiro)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna detalhamento de um grupo por subgrupos
    
    Params:
    - grupo: str (ex: "Casa", "Cartão de Crédito")
    - year: int (ex: 2026)
    - month: int opcional (ex: 1 para janeiro, None para ano todo)
    
    Returns:
    {
      "grupo": "Casa",
      "total_grupo": 2100.50,
      "subgrupos": [
        { "subgrupo": "Aluguel", "valor": 1500.00, "percentual": 71.4, "transacoes": 1 },
        { "subgrupo": "Condomínio", "valor": 400.00, "percentual": 19.0, "transacoes": 1 },
        { "subgrupo": "IPTU", "valor": 200.50, "percentual": 9.6, "transacoes": 1 }
      ]
    }
    """
    service = TransactionService(db)
    return service.get_grupo_breakdown(user_id, grupo, year, month)
```

**Esforço:** 🟢 Baixo (3-4 horas)  
**Prioridade:** 🟡 Média (nice-to-have, não crítico para MVP)

---

## 5. Análise de Componentes Desktop vs Mobile

### 5.1 Budget Detalhado - Comparação

| Feature | Desktop | Mobile | Decisão |
|---------|---------|--------|---------|
| Layout | Accordion (expansível) | Lista vertical de `TrackerCard` | ✅ Adaptar |
| Edição | Input inline sempre visível | Bottom sheet (toque no [✏]) | ✅ Melhor UX mobile |
| Navegação | Sidebar esquerda | Bottom nav inferior | ✅ Padrão mobile |
| Filtro mês | Dropdown (Select) | Scroll horizontal (Pills) | ✅ Melhor UX mobile |
| YTD | ❌ Não tem | Toggle [Mês/YTD] | ✅ Adicionar mobile |
| Copiar mês anterior | ✅ Botão existente | ✅ Mesmo botão | ✅ Manter igual |
| Copiar para ano | ❌ Não tem | ✅ Novo botão | ⚠️ Criar endpoint |
| Drag & drop | ✅ Reordenar categorias | ❌ Não (desktop-only) | ✅ Desktop-only OK |
| Add categoria | ✅ Modal + form | ❌ Não (desktop-only) | ✅ Desktop-only OK |
| Delete categoria | ✅ Botão trash | ❌ Não (desktop-only) | ✅ Desktop-only OK |
| Drill-down grupo | Modal com subgrupos | Bottom sheet com subgrupos | ⚠️ Criar endpoint |

**Decisão Final:**
- ✅ **Manter features desktop-only:** Gerenciar categorias (add, delete, reorder)
- ✅ **Mobile foca em visualização e edição de valores:** Menos fricção, mais rápido
- ⚠️ **Criar 2 endpoints novos:** Copy-to-year, Grupo breakdown

---

### 5.2 Dashboard - Comparação

| Feature | Desktop | Mobile | Decisão |
|---------|---------|--------|---------|
| Métricas | 4 cards horizontal | 2 cards vertical | ✅ Já implementado |
| Gráfico histórico | Sempre visível | Colapsável | ✅ Já implementado |
| Filtro mês | Dropdown | Scroll horizontal | ✅ Adicionar |
| Filtro YTD | `month='all'` (não visível) | Toggle [Mês/YTD] | ✅ Adicionar |
| Top 5 + Demais | ✅ Implementado | Reutilizar lógica | ✅ Já existe |
| Drill-down | Modal desktop | Bottom sheet mobile | ✅ Adaptar |

**Decisão Final:**
- ✅ **Reutilizar lógica de Top 5 + Demais** (já implementado)
- ✅ **Adicionar toggle YTD explícito** (backend já suporta)
- ✅ **Substituir modals por bottom sheets** (padrão mobile)

---

## 6. Gaps Identificados

### 6.1 Backend (2 endpoints)
1. ⚠️ **POST /budget/geral/copy-to-year** - Copiar meta para ano inteiro
   - **Esforço:** 🟢 Baixo (2-3 horas)
   - **Prioridade:** 🔴 Alta
   - **Sprint:** Sprint 3

2. ⚠️ **GET /transactions/grupo-breakdown** - Drill-down grupo → subgrupos
   - **Esforço:** 🟢 Baixo (3-4 horas)
   - **Prioridade:** 🟡 Média
   - **Sprint:** Sprint 4 (polish)

### 6.2 Frontend (3 componentes + 1 adaptação)
1. ✅ **MonthScrollPicker** - Scroll horizontal de meses
   - **Esforço:** 🟢 Baixo (4-6 horas)
   - **Prioridade:** 🔴 Alta
   - **Sprint:** Sprint 1

2. ✅ **YTDToggle** - Toggle [Mês] / [YTD]
   - **Esforço:** 🟢 Baixo (2-3 horas)
   - **Prioridade:** 🟡 Média
   - **Sprint:** Sprint 1

3. ✅ **GrupoBreakdownBottomSheet** - Drill-down grupo → subgrupos
   - **Esforço:** 🟢 Baixo (4-6 horas)
   - **Prioridade:** 🟡 Média
   - **Sprint:** Sprint 4

4. ⚠️ **Adaptar BudgetVsActual para mobile** - Modal → Bottom Sheet
   - **Esforço:** 🟢 Baixo (2-3 horas)
   - **Prioridade:** 🔴 Alta
   - **Sprint:** Sprint 1

**Total de esforço adicional:** ~20-25 horas (≈3-4 dias)

---

## 7. Decisões de Design - Desktop vs Mobile

### 7.1 Features que Permanecem Desktop-Only

**Justificativa:** Complexidade alta, uso menos frequente, tela maior necessária

1. ✅ **Gerenciar categorias de budget** (add, delete, reorder)
   - **Por quê:** Operação administrativa, não frequente
   - **Mobile:** Link "Gerenciar no desktop" se tentar acessar

2. ✅ **Configurar categorias genéricas de classificação**
   - **Por quê:** Setup inicial, interface complexa
   - **Mobile:** Não disponível

3. ✅ **Settings avançados** (bancos, compatibilidade, exclusões, API)
   - **Por quê:** Configuração técnica, formulários extensos
   - **Mobile:** Apenas profile básico

4. ✅ **Relatórios e exportações** (Excel/PDF)
   - **Por quê:** Download/visualização melhor em desktop
   - **Mobile:** V2.0 (share API)

---

### 7.2 Features Mobile-First (Melhores no Mobile)

1. ✅ **MonthScrollPicker** - Scroll horizontal de meses
   - **Desktop:** Pode adicionar também (opcional)
   - **Mobile:** UX superior a dropdown

2. ✅ **Pull-to-refresh** - Atualizar dados
   - **Desktop:** Botão "Atualizar" (já existe)
   - **Mobile:** Gesto nativo

3. ✅ **Bottom sheets** - Modals deslizam de baixo
   - **Desktop:** Modal tradicional (centro da tela)
   - **Mobile:** Bottom sheet (melhor alcance do polegar)

4. ✅ **Swipe actions** - Deslizar para editar/excluir
   - **Desktop:** Botões explícitos
   - **Mobile:** Gestos naturais

---

## 8. Roadmap Ajustado com Novos Requisitos

### Sprint 1 (Semana 1) - Setup + Dashboard ✅
- [ ] Setup rotas mobile (`/mobile/*`)
- [ ] Bottom Navigation component
- [ ] **MonthScrollPicker** (scroll horizontal de meses) 🆕
- [ ] **YTDToggle** (toggle [Mês/YTD]) 🆕
- [ ] Dashboard mobile (reutilizar `MetricCards`)
- [ ] Adaptar BudgetVsActual (modal → bottom sheet)

### Sprint 2 (Semana 2) - Transações e Upload ✅
- [ ] Transações mobile (melhorias)
- [ ] Upload mobile

### Sprint 3 (Semana 3) - Metas + Backend ⚠️
- [ ] **Backend: POST /budget/geral/copy-to-year** 🆕 (copiar para ano)
- [ ] Metas mobile (criar do zero com `TrackerCard`)
- [ ] **Botão "Colar para 2026"** (usa endpoint acima) 🆕
- [ ] Profile mobile (adaptar)

### Sprint 4 (Semana 4) - Polish + Drill-down ⚠️
- [ ] **Backend: GET /transactions/grupo-breakdown** 🆕 (drill-down)
- [ ] **GrupoBreakdownBottomSheet** (mostra subgrupos) 🆕
- [ ] Testes E2E
- [ ] Otimizações

**Novo esforço total:** 4 semanas + 3-4 dias (novos endpoints + componentes)

---

## 9. Recomendações Finais

### 9.1 Implementar Agora (MVP V1.0)
1. ✅ MonthScrollPicker (melhor UX que dropdown)
2. ✅ YTDToggle (backend já suporta)
3. ✅ TrackerCard para lista de metas
4. ✅ Bottom sheets (substituir modals)
5. ✅ Top 5 + Demais (lógica já existe)
6. ⚠️ **POST /budget/geral/copy-to-year** (endpoint novo - crítico)

### 9.2 Adiar para V1.1 (Polish)
1. ⚠️ GET /transactions/grupo-breakdown (drill-down subgrupos)
2. ✅ Swipe actions (editar/excluir com gestos)
3. ✅ Animações refinadas (Framer Motion)
4. ✅ Haptic feedback (vibração ao tocar)

### 9.3 Desktop-Only (Não portar para mobile)
1. ✅ Gerenciar categorias (add, delete, reorder)
2. ✅ Configurações avançadas
3. ✅ Relatórios e exportações (V2.0 mobile)

---

## 10. Análise de Risco vs Benefício

| Funcionalidade | Esforço | Benefício | Decisão |
|----------------|---------|-----------|---------|
| MonthScrollPicker | 🟢 4-6h | 🔴 Muito Alto (UX melhor) | ✅ MVP |
| YTDToggle | 🟢 2-3h | 🟡 Alto (visão anual) | ✅ MVP |
| Copy-to-year | 🟢 2-3h | 🔴 Muito Alto (produtividade) | ✅ MVP |
| TrackerCard | 🟢 4-6h | 🔴 Muito Alto (design system) | ✅ MVP |
| Bottom sheets | 🟡 8-10h | 🟡 Alto (padrão mobile) | ✅ MVP |
| Grupo breakdown | 🟢 3-4h | 🟢 Médio (drill-down) | ⏭️ V1.1 |
| Swipe actions | 🟡 6-8h | 🟢 Médio (gestos) | ⏭️ V1.1 |

**Total esforço MVP:** ~30-35 horas (≈4-5 dias)  
**Total esforço V1.1:** +10-12 horas (≈1-2 dias)

---

## 11. Conclusão - FACTÍVEL ✅

### Resumo
- ✅ **Backend:** 95% pronto (faltam 2 endpoints simples)
- ✅ **Frontend:** 80% reutilizável (componentes mobile existentes)
- ✅ **Design System:** 100% especificado e pronto para implementar
- ✅ **APIs:** Todas as funcionalidades críticas têm endpoints
- ✅ **Estrutura de dados:** Suporta todas as features solicitadas

### Riscos Baixos
- 🟢 Tecnologia conhecida (React, Next.js, FastAPI)
- 🟢 Padrões estabelecidos (componentes reutilizáveis)
- 🟢 Arquitetura modular (fácil adicionar endpoints)
- 🟢 Design system completo (paleta + dimensões documentadas)

### Ajustes Recomendados
1. ✅ **Copiar para ano inteiro:** CRIAR endpoint (Sprint 3)
2. ✅ **Drill-down subgrupos:** CRIAR endpoint (Sprint 4 ou V1.1)
3. ✅ **MonthScrollPicker:** Substituir dropdown (Sprint 1)
4. ✅ **YTD Toggle:** Adicionar ao dashboard (Sprint 1)
5. ✅ **Top 5 + Demais:** Reutilizar lógica desktop (Sprint 1)

---

## 12. Checklist de Validação

### Backend
- [x] APIs de budget existem?
- [x] APIs de dashboard existem?
- [x] APIs de transações existem?
- [x] Suporte a YTD existe?
- [x] Estrutura grupo → subgrupo existe?
- [ ] Endpoint copy-to-year existe? **CRIAR**
- [ ] Endpoint grupo-breakdown existe? **CRIAR**

### Frontend
- [x] Componentes mobile existem (MetricCards)?
- [x] Lógica Top 5 + Demais existe?
- [x] Design system definido?
- [x] Paleta de cores documentada?
- [ ] MonthScrollPicker criado? **CRIAR**
- [ ] YTDToggle criado? **CRIAR**
- [ ] TrackerCard criado? **CRIAR**

### Design
- [x] Imagem "Trackers" analisada?
- [x] Cores extraídas?
- [x] Dimensões mapeadas?
- [x] Tipografia documentada?
- [x] Componentes especificados?
- [x] Acessibilidade validada (WCAG AA)?

---

## 13. Parecer Final

**Status:** ✅ **PROJETO 100% FACTÍVEL**

**Justificativa:**
1. Backend maduro com APIs completas (95% pronto)
2. Componentes mobile já existentes e testados
3. Design system completo e documentado
4. Arquitetura modular facilita adição de 2 endpoints
5. Equipe tem experiência com stack (Next.js, FastAPI)
6. Esforço total (MVP) cabe em 4 semanas

**Recomendação:** 🚀 **APROVAR para implementação imediata**

**Próximo passo:** Criar TECH_SPEC com arquitetura detalhada dos 2 novos endpoints + componentes mobile.

---

**Fim da Análise de Factibilidade**
