# 📋 PRD - [Nome da Feature]

**Status:** 🟡 Em Aprovação  
**Versão:** 1.0  
**Data:** DD/MM/YYYY  
**Autor:** [Nome]  
**Stakeholders:** [Nome1, Nome2]

---

## 📊 Sumário Executivo

**O que:** [Descrição em 1-2 frases]  
**Por quê:** [Problema que resolve]  
**Para quem:** [Usuário alvo]  
**Quando:** [Prazo]  
**ROI Estimado:** [Benefício esperado]

---

## 🎯 1. Contexto e Problema

### 1.1 Situação Atual
[Descrever estado atual do sistema/processo]

### 1.2 Problema a Resolver
[Problema específico que esta feature resolve]

**Impacto do Problema:**
- 🔴 **Crítico:** [Exemplo: "Usuários não conseguem X"]
- 🟡 **Médio:** [Exemplo: "Processo manual leva 30min"]
- 🟢 **Baixo:** [Exemplo: "UX poderia ser melhor"]

### 1.3 Justificativa
**Por que fazer agora?**
- [Razão 1]
- [Razão 2]
- [Razão 3]

---

## 🎯 2. Objetivos

### 2.1 Objetivo Principal
[Objetivo primário em 1 frase]

### 2.2 Objetivos Secundários
1. [Objetivo 2]
2. [Objetivo 3]

### 2.3 Objetivos SMART

| Critério | Descrição |
|----------|-----------|
| **S**pecific | [O que exatamente será feito] |
| **M**easurable | [Como medir sucesso - KPI] |
| **A**chievable | [É viável com recursos atuais?] |
| **R**elevant | [Alinha com objetivos empresa?] |
| **T**ime-bound | [Prazo: DD/MM/YYYY] |

---

## 👥 3. Personas e User Stories

### 3.1 Persona Principal

**Nome:** [Ex: Maria, Usuária Ativa]  
**Idade:** [Ex: 28 anos]  
**Ocupação:** [Ex: Analista Financeira]  
**Comportamento:** [Ex: Usa app diariamente, tech-savvy]  
**Dores:** [Ex: Gasta muito tempo em tarefas manuais]  
**Objetivos:** [Ex: Controlar gastos de forma rápida]

### 3.2 User Stories

#### **US-01: [Título]**
**Como** [persona]  
**Quero** [ação]  
**Para** [benefício]

**Acceptance Criteria:**
- [ ] Critério 1
- [ ] Critério 2
- [ ] Critério 3

**Prioridade:** 🔴 Alta | 🟡 Média | 🟢 Baixa

---

#### **US-02: [Título]**
[Repetir estrutura]

---

## 📋 4. Requisitos Funcionais

### 4.1 Requisitos de Interface

**RF-01: [Nome do Requisito]**
- **Descrição:** [O que o usuário vê/faz]
- **Comportamento:** [Como funciona]
- **Validações:** [Regras de negócio]
- **Prioridade:** Must Have | Should Have | Nice to Have

**RF-02: [Outro Requisito]**
[Repetir estrutura]

### 4.2 Requisitos de Lógica de Negócio

**RF-10: [Cálculo/Processamento]**
- **Descrição:** [Lógica a implementar]
- **Fórmula:** [Se aplicável]
- **Exemplo:** [Caso de uso concreto]

### 4.3 Requisitos de Integração

**RF-20: [Integração com Sistema X]**
- **Sistema:** [Nome do sistema externo]
- **Endpoint:** [API endpoint]
- **Dados:** [Payload request/response]

---

## ⚙️ 5. Requisitos Não-Funcionais

### 5.1 Performance
- **RNF-01:** Tempo de carregamento ≤2s (4G)
- **RNF-02:** Lighthouse Performance ≥85
- **RNF-03:** Suportar 100 requisições/min

### 5.2 Acessibilidade
- **RNF-10:** WCAG 2.1 AA (conformidade ≥90%)
- **RNF-11:** Touch targets ≥44px
- **RNF-12:** Contraste mínimo 4.5:1

### 5.3 Segurança
- **RNF-20:** Autenticação JWT
- **RNF-21:** HTTPS obrigatório
- **RNF-22:** Rate limiting (5 req/min por IP)

### 5.4 Compatibilidade
- **RNF-30:** iOS 14+ (Safari)
- **RNF-31:** Android 10+ (Chrome)
- **RNF-32:** Desktop Chrome/Firefox/Safari

---

## 📐 6. Wireframes e Mockups

### 6.1 Fluxo Principal

```
┌─────────────────────┐
│   Tela Inicial      │
│                     │
│  [ Botão Ação ]     │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│   Tela Destino      │
│                     │
│  [ Formulário ]     │
└─────────────────────┘
```

### 6.2 Layout Mobile

```
┌─────────────────────┐
│  Header [← Voltar]  │
├─────────────────────┤
│                     │
│  [ Card 1 ]         │
│                     │
│  [ Card 2 ]         │
│                     │
│  [ Card 3 ]         │
│                     │
├─────────────────────┤
│  Bottom Navigation  │
└─────────────────────┘
```

### 6.3 Links Figma/Design
- [Link para protótipo interativo]
- [Link para design system]

---

## 🎨 7. Design System

### 7.1 Cores
- **Primary:** `#3B82F6` (blue-600)
- **Success:** `#10B981` (green-500)
- **Error:** `#EF4444` (red-500)
- **Background:** `#F9FAFB` (gray-50)

### 7.2 Tipografia
- **Heading:** `font-semibold text-gray-900`
- **Body:** `text-gray-600`
- **Caption:** `text-xs text-gray-500`

### 7.3 Componentes
- Botões: Rounded-xl, padding 16px, touch 48px
- Cards: Shadow-sm, rounded-2xl, border gray-100
- Inputs: Rounded-xl, border-2, focus ring

---

## 🔄 8. Fluxos de Usuário

### 8.1 Fluxo: [Nome do Fluxo]

```
1. Usuário acessa tela X
2. Visualiza lista de Y
3. Toca em item Z
4. Bottom sheet abre
5. Edita valor
6. Toca em "Salvar"
7. API atualiza banco
8. Toast de sucesso
9. Lista atualiza
```

### 8.2 Fluxo de Erro

```
1. Usuário tenta ação X
2. Validação falha
3. Mensagem de erro inline
4. Campo com border vermelho
5. Usuário corrige
6. Validação passa
7. Ação prossegue
```

---

## 📏 9. Escopo

### 9.1 Incluído (In Scope)
✅ [Feature 1]  
✅ [Feature 2]  
✅ [Feature 3]

### 9.2 Excluído (Out of Scope)
❌ [Feature X - será feito em V2]  
❌ [Feature Y - fora do objetivo]  
❌ [Feature Z - depende de outro projeto]

### 9.3 Futuro (Nice to Have - V2)
🔮 [Feature futura 1]  
🔮 [Feature futura 2]

---

## 📊 10. Métricas de Sucesso

### 10.1 KPIs Primários
| Métrica | Baseline | Meta | Como Medir |
|---------|----------|------|------------|
| [Ex: Tempo médio tarefa] | 5min | 2min | Analytics |
| [Ex: Taxa conversão] | 30% | 50% | Mixpanel |
| [Ex: NPS] | 7 | 9 | Survey |

### 10.2 KPIs Secundários
- **Técnicos:** Lighthouse ≥85, WCAG ≥90%, Coverage ≥80%
- **Negócio:** Redução custos, aumento receita
- **Usuário:** Satisfação, tempo na tarefa, taxa erro

---

## ⏱️ 11. Cronograma

### 11.1 Milestones

| Fase | Entregável | Prazo | Responsável |
|------|------------|-------|-------------|
| PRD | Aprovação | DD/MM | [Nome] |
| TECH SPEC | Completo | DD/MM | [Nome] |
| Sprint 1 | Backend | DD/MM | [Nome] |
| Sprint 2 | Frontend | DD/MM | [Nome] |
| Deploy | Produção | DD/MM | [Nome] |

### 11.2 Estimativa de Esforço

| Atividade | Small | Medium | Large |
|-----------|-------|--------|-------|
| PRD | 4h | 8h | 16h |
| TECH SPEC | 4h | 8h | 16h |
| Development | 16h | 40h | 80h |
| Testing | 4h | 8h | 16h |
| Deploy | 2h | 4h | 8h |
| **TOTAL** | **30h** | **68h** | **136h** |

---

## 🚧 12. Riscos e Mitigações

### 12.1 Riscos Técnicos

**Risco 1: [Descrição]**
- **Probabilidade:** Alta | Média | Baixa
- **Impacto:** Crítico | Médio | Baixo
- **Mitigação:** [Ação preventiva]
- **Plano B:** [Se ocorrer]

### 12.2 Riscos de Negócio

**Risco 2: [Descrição]**
[Mesma estrutura]

---

## 📚 13. Dependências

### 13.1 Dependências Técnicas
- [ ] Sistema X deve estar funcionando
- [ ] API Y deve estar disponível
- [ ] Framework Z versão N instalado

### 13.2 Dependências de Negócio
- [ ] Aprovação legal
- [ ] Contrato com fornecedor
- [ ] Budget aprovado

---

## ✅ 14. Aprovação

### 14.1 Stakeholders

| Nome | Papel | Status | Data |
|------|-------|--------|------|
| [Nome1] | Product Owner | ⏳ Pendente | - |
| [Nome2] | Tech Lead | ⏳ Pendente | - |
| [Nome3] | Designer | ⏳ Pendente | - |
| [Nome4] | QA Lead | ⏳ Pendente | - |

### 14.2 Critérios de Aprovação
- [ ] Todos stakeholders aprovaram
- [ ] Zero ambiguidades identificadas
- [ ] Budget aprovado
- [ ] Cronograma validado

**Data de Aprovação:** DD/MM/YYYY  
**Aprovado por:** [Nome + Assinatura]

---

## 📖 15. Anexos

### 15.1 Referências
- [Link para documentação técnica]
- [Link para pesquisa de usuário]
- [Link para benchmark competidores]

### 15.2 Histórico de Versões

| Versão | Data | Autor | Mudanças |
|--------|------|-------|----------|
| 1.0 | DD/MM | [Nome] | Criação inicial |
| 1.1 | DD/MM | [Nome] | Ajustes após feedback |

---

**Próximo Passo:** Criar TECH SPEC (`/docs/features/[nome]/02-TECH_SPEC/TECH_SPEC.md`)
