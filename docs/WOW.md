# 📋 Way of Working (WoW) - FinUp Development Process

**Versão:** 1.0  
**Data:** 01/02/2026  
**Status:** 🎯 ATIVO

---

## 🎯 Visão Geral

Sistema estruturado para desenvolvimento de features com **5 fases obrigatórias**:

```
1. PRD → 2. TECH SPEC → 3. SPRINT → 4. DEPLOY → 5. POST-MORTEM
```

**Objetivo:** Zero bugs de requisitos, 100% rastreabilidade, processo replicável.

---

## 🔄 Fluxo Completo - 5 Fases

### **1️⃣ PRD (Product Requirements Document)**
**O QUÊ será construído e POR QUÊ**

📁 **Pasta:** `/docs/features/[nome]/01-PRD/`

**Entregáveis:**
- `PRD.md` - Requisitos completos (1.000-3.000 linhas)
- `USER_STORIES.md` - Personas e cenários
- `WIREFRAMES.md` - Layouts visuais

**Checklist:**
- [ ] Problema e contexto claramente definidos
- [ ] Objetivos SMART (mensuráveis)
- [ ] Requisitos funcionais e não-funcionais
- [ ] Escopo definido (incluído/excluído)
- [ ] Wireframes/mockups
- [ ] ✅ **Aprovação stakeholder** (bloqueante!)

**Template:** `/docs/templates/TEMPLATE_PRD.md`

---

### **2️⃣ TECH SPEC (Technical Specification)**
**COMO será construído**

📁 **Pasta:** `/docs/features/[nome]/02-TECH_SPEC/`

**Entregáveis:**
- `TECH_SPEC.md` - Arquitetura e decisões (2.000-3.000 linhas)
- `API_SPEC.md` - Endpoints (request/response)
- `COMPONENTS.md` - Código copy-paste ready
- `DEPENDENCY_GRAPH.md` - DAG de implementação

**Checklist:**
- [ ] Arquitetura definida (diagrama)
- [ ] Componentes com código completo (≥80%)
- [ ] APIs especificadas (curl examples)
- [ ] DAG completo (ordem de implementação)
- [ ] Database schema + migrations
- [ ] Testing strategy (cobertura ≥80%)
- [ ] Performance budget (Lighthouse ≥85)

**Template:** `/docs/templates/TEMPLATE_TECH_SPEC.md`

---

### **3️⃣ SPRINT (Execution)**
**IMPLEMENTAÇÃO seguindo TECH SPEC**

📁 **Pasta:** `/docs/features/[nome]/02-TECH_SPEC/` (mesma)

**Entregáveis:**
- `SPRINT1_COMPLETE.md` - Relatório sprint 1
- `SPRINT2_COMPLETE.md` - Relatório sprint 2
- `FIX_BUG_DESCRIPTION.md` - Bugs corrigidos
- `SESSION_SUMMARY.md` - Consolidação

**Workflow Diário:**

**Manhã:**
1. Review ontem (ler SPRINT_X_WIP.md)
2. Escolher próximo item do DAG
3. Implementar seguindo TECH SPEC

**Tarde:**
4. Testar localmente
5. Documentar mudanças
6. Commitar código

**Noite:**
7. Atualizar CHANGELOG.md
8. Criar FIX_*.md se bugs
9. Push para GitHub

**Checklist Sprint:**
- [ ] Todos itens do DAG implementados
- [ ] Código testado (manual + automated)
- [ ] Bugs documentados em FIX_*.md
- [ ] SPRINT_X_COMPLETE.md finalizado
- [ ] CHANGELOG.md atualizado

**Templates:** 
- `/docs/templates/TEMPLATE_SPRINT.md`
- `/docs/templates/TEMPLATE_FIX.md`

---

### **4️⃣ DEPLOY (Release to Production)**
**PUBLICAÇÃO segura em produção**

📁 **Pasta:** `/docs/features/[nome]/03-DEPLOY/`

**Entregáveis:**
- `DEPLOY_CHECKLIST.md` - 250+ itens validação
- `ROLLBACK_PLAN.md` - Plano B
- `MONITORING_SETUP.md` - Alertas e logs
- `DEPLOY_REPORT.md` - Métricas finais

**Workflow Deploy:**

**Pré-Deploy (1-2h antes):**
1. ✅ Git limpo (main atualizada)
2. ✅ Testes 100% passando
3. ✅ Build sem erros
4. ✅ Backup banco de dados
5. ✅ Migrations testadas staging
6. ✅ Secrets configurados prod

**Deploy (15-30min):**
1. SSH no servidor
2. `git pull origin main`
3. `alembic upgrade head`
4. `npm run build`
5. `systemctl restart backend frontend`
6. Validar health checks

**Pós-Deploy (1-2h):**
1. ✅ Smoke tests
2. ✅ Monitoring (logs, CPU, memória)
3. ✅ Lighthouse (≥85)
4. ✅ WCAG 2.1 AA (≥90)
5. ✅ Feedback primeiras 24h

**Checklist Deploy:**
- [ ] Pré-deploy validado (250+ itens)
- [ ] Deploy executado sem erros
- [ ] Smoke tests passando
- [ ] DEPLOY_REPORT criado
- [ ] Tag Git (vX.Y.Z)
- [ ] Stakeholders notificados

**Template:** `/docs/templates/TEMPLATE_DEPLOY.md`

---

### **5️⃣ POST-MORTEM (Retrospective)**
**APRENDIZADO e melhoria contínua**

📁 **Pasta:** `/docs/features/[nome]/03-DEPLOY/` (mesma)

**Entregáveis:**
- `POST_MORTEM.md` - Retrospectiva completa (500-1.000 linhas)
- `LESSONS_LEARNED.md` - Lições aprendidas

**Perguntas Guia:**
1. ✅ **O que deu certo?** - Replicar em próximos projetos
2. ❌ **O que deu errado?** - Evitar em futuros
3. 💡 **O que aprendemos?** - Conhecimento novo
4. 🔄 **O que mudaríamos?** - Melhorias processo

**Checklist Post-Mortem:**
- [ ] Reunião retrospectiva (30-60min)
- [ ] POST_MORTEM.md escrito
- [ ] 3-5 ações de melhoria identificadas
- [ ] Ações atribuídas com prazo
- [ ] Lições documentadas

**Template:** `/docs/templates/TEMPLATE_POST_MORTEM.md`

---

## 📊 Métricas de Sucesso

| Fase | Indicador | Alvo | Como Medir |
|------|-----------|------|------------|
| PRD | Aprovação stakeholder | 100% | Assinatura/email |
| PRD | Bugs de requisitos | 0 | Issues mal definidos |
| TECH | Código ready | ≥80% | Componentes copy-paste |
| SPRINT | Cobertura testes | ≥80% | Jest coverage |
| DEPLOY | Tempo deploy | ≤30min | Pull → serviços ativos |
| DEPLOY | Rollbacks | 0 | Deploys revertidos |
| ALL | Documentação | 100% | Docs = código atual |

---

## 🚨 Red Flags - Processo Quebrando

### 🔴 **Crítico - PARAR IMEDIATAMENTE:**
1. Código sem PRD/TECH SPEC
2. Bugs de requisitos ("não era isso")
3. Retrabalho >20%
4. Deploy >3 rollbacks

### ⚠️ **Moderado - Ajustar:**
1. Sprint >50% estimativa
2. Bugs >15
3. CHANGELOG desatualizado
4. Post-mortem não feito

---

## 🎯 Checklist Executivo - Feature Completa

### **Fase 1 - PRD ✅**
- [ ] PRD.md criado (1.000-3.000 linhas)
- [ ] User stories documentadas
- [ ] Wireframes incluídos
- [ ] Stakeholder aprovou

### **Fase 2 - TECH SPEC ✅**
- [ ] TECH_SPEC.md criado (2.000-3.000 linhas)
- [ ] Código copy-paste ready (≥80%)
- [ ] DAG completo
- [ ] APIs especificadas

### **Fase 3 - SPRINT ✅**
- [ ] SPRINT_X_COMPLETE.md (1 por sprint)
- [ ] Bugs em FIX_*.md
- [ ] CHANGELOG atualizado
- [ ] Código testado

### **Fase 4 - DEPLOY ✅**
- [ ] DEPLOY_CHECKLIST validado
- [ ] Backup criado
- [ ] Deploy sem erros
- [ ] Smoke tests OK
- [ ] DEPLOY_REPORT criado

### **Fase 5 - POST-MORTEM ✅**
- [ ] POST_MORTEM.md criado
- [ ] 3-5 ações identificadas
- [ ] Ações atribuídas
- [ ] Lições documentadas

---

## 📂 Estrutura de Arquivos Obrigatória

```
/docs/features/[feature-name]/
├── README.md                    # Overview + Quick Start
├── INDEX.md                     # Índice navegável
├── CHANGELOG.md                 # Histórico de mudanças
│
├── 01-PRD/                      # Product Requirements
│   ├── PRD.md                   # 👈 PRINCIPAL
│   ├── USER_STORIES.md
│   ├── WIREFRAMES.md
│   └── STYLE_GUIDE.md (opcional)
│
├── 02-TECH_SPEC/                # Technical Specification
│   ├── TECH_SPEC.md             # 👈 PRINCIPAL
│   ├── API_SPEC.md
│   ├── COMPONENTS.md
│   ├── DEPENDENCY_GRAPH.md      # DAG
│   ├── SPRINT1_COMPLETE.md      # Sprints
│   ├── SPRINT2_COMPLETE.md
│   ├── FIX_BUG_NAME.md          # Fixes
│   └── SESSION_SUMMARY.md
│
└── 03-DEPLOY/                   # Deploy e Produção
    ├── DEPLOY_CHECKLIST.md      # 250+ itens
    ├── ROLLBACK_PLAN.md
    ├── MONITORING_SETUP.md
    ├── DEPLOY_REPORT.md
    └── POST_MORTEM.md
```

---

## 🎓 Onboarding - Novos Membros (5 dias)

**Dia 1:**
1. Ler `WOW.md` (este arquivo) - 2h
2. Ler `/docs/features/mobile-v1/README.md` - 30min
3. Navegar INDEX.md - 1h

**Dia 2:**
4. Estudar templates (PRD, TECH_SPEC) - 2h
5. Ler mobile-v1 PRD completo - 3h
6. Ler mobile-v1 TECH_SPEC completo - 3h

**Dia 3:**
7. Implementar feature simples - 4h
8. Documentar (PRD → TECH → SPRINT) - 4h

**Dia 4:**
9. Code review com mentor - 2h
10. Ajustar documentação - 2h
11. Deploy staging - 1h

**Dia 5:**
12. Post-mortem da feature - 1h
13. Apresentar aprendizados - 1h

**Total:** 28h (1 semana)

---

## 🔗 Integração com GitHub Copilot

**Adicionar em:** `.github/copilot-instructions.md`

```markdown
## 📋 WORKFLOW OBRIGATÓRIO - WAY OF WORKING (WoW)

**REGRA CRÍTICA:** SEMPRE seguir processo de 5 fases:

1. **PRD** - Criar `/docs/features/[nome]/01-PRD/PRD.md`
2. **TECH SPEC** - Criar `02-TECH_SPEC/TECH_SPEC.md`
3. **SPRINT** - Documentar em `SPRINT_X_COMPLETE.md`
4. **DEPLOY** - Validar `DEPLOY_CHECKLIST.md`
5. **POST-MORTEM** - Criar `POST_MORTEM.md`

🚫 **PROIBIDO:** Codificar sem PRD e TECH SPEC!

**Referência:** `/docs/WOW.md`
**Templates:** `/docs/templates/`
**Exemplo:** `/docs/features/mobile-v1/`
```

---

## 📖 Referência: mobile-v1 (Benchmark)

**Ver:** `/docs/features/mobile-v1/`

**Estrutura completa:**
- 43 arquivos markdown
- ~19.000 linhas documentação
- 85% MVP funcional
- 0 bugs de requisitos
- 12 bugs técnicos (todos documentados)

**Usar como:**
- ✅ **Referência de estrutura** (pastas, nomenclatura)
- ✅ **Nível de detalhamento** (código copy-paste)
- ✅ **Padrões de documentação** (FIX_*.md, SPRINT_*.md)

**Melhorias aplicadas:**
- ⚠️ Evitar duplicação README/INDEX (consolidar)
- ⚠️ Criar templates reutilizáveis (não existiam)
- ⚠️ Simplificar PRD (3.500 linhas → alvo 2.000)

---

## 🔄 Evolução do Processo

**v1.0** (atual) - 01/02/2026
- Processo base 5 fases
- Templates criados
- Integração Copilot

**v1.1** (próxima) - Q2 2026
- [ ] ADR (Architecture Decision Records)
- [ ] CI/CD pipeline validações
- [ ] Dashboard métricas (Grafana)

**v2.0** (futuro) - Q4 2026
- [ ] Feature flags
- [ ] A/B testing
- [ ] Internacionalização docs (EN)

---

**Responsável:** Tech Lead / Product Manager  
**Revisão:** Trimestral  
**Próxima:** 01/05/2026

---

**Sugestões de melhoria:** Criar issue GitHub com label `process`
