# 📊 POST-MORTEM - [Feature Name]

**Versão do Template:** 1.0  
**Data Deploy:** [DD/MM/YYYY HH:MM]  
**Data Análise:** [DD/MM/YYYY] (até 48h após deploy)  
**Responsável:** [Nome]  
**Participantes:** [Time]  
**Status Deploy:** [✅ Sucesso | ⚠️ Sucesso com Ressalvas | ❌ Falhou]

---

## 🎯 RESUMO EXECUTIVO

**O que foi entregue:**  
[Descrever em 2-3 frases o que foi deployado]

**Resultado geral:**  
[✅ Sucesso | ⚠️ Problemas menores | ❌ Rollback necessário]

**Principais aprendizados:**  
1. [Aprendizado 1]
2. [Aprendizado 2]
3. [Aprendizado 3]

---

## 📋 OBJETIVOS vs RESULTADOS

### Objetivos Planejados (do PRD)

| Objetivo SMART | Status | Evidência |
|---------------|--------|-----------|
| [Ex: Reduzir tempo de carga dashboard de 5s para 2s] | [✅/⚠️/❌] | [Lighthouse: 4.8s→2.1s] |
| [Ex: Suportar 1000 usuários simultâneos] | [✅/⚠️/❌] | [Load test: 1200 OK] |
| [Ex: Lighthouse ≥ 85 em todas as páginas] | [✅/⚠️/❌] | [Dashboard: 87, Mobile: 91] |

---

### KPIs Atingidos

| KPI | Meta | Resultado | Variação |
|-----|------|-----------|----------|
| Performance (Lighthouse) | ≥ 85 | ___ | +/- ___% |
| Acessibilidade (WCAG) | ≥ 90% | ___ | +/- ___% |
| Cobertura de Testes | ≥ 80% | ___ | +/- ___% |
| Bugs em Produção (7 dias) | ≤ 5 | ___ | +/- ___ |
| Uptime (7 dias) | ≥ 99.5% | ___ | +/- ___% |

---

## ✅ O QUE DEU CERTO

### 1️⃣ [Título do Sucesso]

**Descrição:**  
[O que funcionou bem e por quê]

**Por que deu certo:**
- [Razão 1 - ex: PRD bem detalhado]
- [Razão 2 - ex: Testes E2E cobrindo casos críticos]
- [Razão 3 - ex: Deploy em horário de baixo tráfego]

**Replicar em próximos projetos:**  
- [ ] [Ação 1 - ex: Sempre criar PRD antes de TECH_SPEC]
- [ ] [Ação 2 - ex: Rodar Playwright em CI antes de merge]

---

### 2️⃣ [Outro Sucesso]

**Descrição:**  
[...]

**Evidências:**
- Screenshot: [link]
- Métrica: [ex: Lighthouse 91]
- Feedback usuário: [quote]

---

## ❌ O QUE DEU ERRADO

### 1️⃣ [Título do Problema]

**O que aconteceu:**  
[Descrição do problema encontrado]

**Quando foi detectado:**  
[Durante deploy | Após 1h | Após 24h | Após 7 dias]

**Impacto:**  
- **Severidade:** [Crítico | Alto | Médio | Baixo]
- **Usuários afetados:** [Número ou %]
- **Downtime:** [X minutos]
- **Dados perdidos:** [Sim/Não - descrever]

**Root Cause (Causa Raiz):**  
[Por que realmente aconteceu - 5 Whys se necessário]

**Como foi resolvido:**  
[Descrever solução aplicada]

**Tempo para resolver:**  
[X minutos/horas desde detecção até correção]

**Prevenção futura:**
- [ ] [Ação 1 - ex: Adicionar validação de schema antes de migration]
- [ ] [Ação 2 - ex: Smoke test automatizado pós-deploy]
- [ ] [Ação 3 - ex: Alertar no Slack se health check falhar]

---

### 2️⃣ [Outro Problema]

**O que aconteceu:**  
[...]

**Bug Report Criado:**  
- Arquivo: `FIX_[data]_[descricao].md`
- Issue: #[número]

---

## ⚠️ PROBLEMAS MENORES / WARNINGS

### 1. [Warning 1]
- **Descrição:** [Ex: Bundle JS ficou 480KB (perto do limite 500KB)]
- **Impacto:** Baixo (ainda dentro do aceitável)
- **Ação:** Monitorar para próximo sprint

### 2. [Warning 2]
- **Descrição:** [Ex: 1 teste E2E flaky (falha intermitente)]
- **Impacto:** Médio (pode mascarar bugs reais)
- **Ação:** Investigar e estabilizar teste

---

## 📊 MÉTRICAS DO DEPLOY

### Timing

| Fase | Tempo Planejado | Tempo Real | Variação |
|------|-----------------|------------|----------|
| Parar servidores | 2 min | ___ min | +/- ___ |
| Pull código | 1 min | ___ min | +/- ___ |
| Instalar deps | 5 min | ___ min | +/- ___ |
| Migrations | 2 min | ___ min | +/- ___ |
| Iniciar servidores | 3 min | ___ min | +/- ___ |
| Smoke tests | 5 min | ___ min | +/- ___ |
| **TOTAL** | **18 min** | **___ min** | **+/- ___** |

**Downtime:**  
- Planejado: ___ min  
- Real: ___ min  
- Motivo diferença: [se houver]

---

### Qualidade do Código

| Métrica | Antes | Depois | Variação |
|---------|-------|--------|----------|
| Linhas de código | ___ | ___ | +___% |
| Cobertura testes | ___% | ___% | +___% |
| Bugs conhecidos | ___ | ___ | -___ |
| Tech debt | ___ | ___ | +/- ___ |

---

### Performance

| Página | Lighthouse (antes) | Lighthouse (depois) | Variação |
|--------|-------------------|---------------------|----------|
| Dashboard | ___ | ___ | +/- ___ |
| Transações | ___ | ___ | +/- ___ |
| Upload | ___ | ___ | +/- ___ |
| Mobile | ___ | ___ | +/- ___ |

**Queries lentas detectadas:**
- [ ] Nenhuma query > 1s
- [ ] [Se houver] `[query]` levou ___s (otimizar)

---

### Bugs Encontrados

| ID | Descrição | Severidade | Status | Tempo Resolução |
|----|-----------|-----------|--------|-----------------|
| 1 | [Ex: Modal não fecha no mobile] | Médio | ✅ Resolvido | 2h |
| 2 | [Ex: Migration falhou no primeiro try] | Alto | ✅ Resolvido | 30min |
| 3 | [...] | Baixo | ⏳ Pendente | - |

**Total de bugs:** ___  
**Bugs críticos:** ___  
**Bugs resolvidos em 24h:** ___

---

## 🔍 ANÁLISE DE PROCESSO (WoW)

### Fase 1 - PRD

**O que funcionou:**
- [Ex: User stories claras aceleraram desenvolvimento]
- [Ex: Wireframes evitaram refações de UI]

**O que melhorar:**
- [Ex: PRD muito longo (3500 linhas) - considerar split]
- [Ex: Acceptance criteria poderia ser mais específico]

**Nota:** [1-10] ___/10

---

### Fase 2 - TECH SPEC

**O que funcionou:**
- [Ex: Código copy-paste ready economizou tempo]
- [Ex: DAG (Dependency Graph) evitou bloquear devs]

**O que melhorar:**
- [Ex: Faltou especificar error handling em detalhes]
- [Ex: Migrations poderiam ter exemplo de downgrade]

**Nota:** [1-10] ___/10

---

### Fase 3 - SPRINT (Execução)

**O que funcionou:**
- [Ex: Commits pequenos facilitaram debug]
- [Ex: CHANGELOG atualizado diariamente manteve histórico]

**O que melhorar:**
- [Ex: Testes E2E só no final - deveria ser contínuo]
- [Ex: Code review demorou 2 dias - atrapalhou fluxo]

**Nota:** [1-10] ___/10

---

### Fase 4 - DEPLOY

**O que funcionou:**
- [Ex: Checklist preveniu esquecimento de backup]
- [Ex: Smoke tests detectaram problema antes de usuário]

**O que melhorar:**
- [Ex: Rollback não foi testado previamente]
- [Ex: Documentação SSH estava desatualizada]

**Nota:** [1-10] ___/10

---

### Fase 5 - POST-MORTEM (Este Documento)

**Prazo cumprido:**  
- [ ] Criado em até 48h após deploy

**Participação:**
- [Nome 1] - [Papel]
- [Nome 2] - [Papel]

**Nota:** [1-10] ___/10

---

## 🎯 AÇÕES DE MELHORIA (ACTION ITEMS)

**REGRA:** Identificar 3-5 ações concretas para próximo projeto

### 1️⃣ [Ação 1 - Alta Prioridade]

**O quê:**  
[Descrição clara da ação - ex: Criar script de validação de PRD]

**Por quê:**  
[Problema que resolve - ex: PRD estava incompleto, causou refação]

**Como:**  
[Passos concretos]
```bash
# Exemplo de script
python scripts/validate_prd.py --feature [nome]
# Valida:
# - Seção "Objetivos SMART" existe
# - User stories têm acceptance criteria
# - Wireframes incluídos
```

**Responsável:** [Nome]  
**Prazo:** [Data]  
**Status:** [ ] Não iniciado | [ ] Em progresso | [ ] Concluído

---

### 2️⃣ [Ação 2 - Alta Prioridade]

[...]

---

### 3️⃣ [Ação 3 - Média Prioridade]

[...]

---

### 4️⃣ [Ação 4 - Baixa Prioridade]

[...]

---

## 📚 DOCUMENTAÇÃO GERADA

- [ ] ✅ PRD completo (`01-PRD/PRD.md`)
- [ ] ✅ TECH SPEC completo (`02-TECH_SPEC/TECH_SPEC.md`)
- [ ] ✅ SPRINTs documentados (`SPRINT1_COMPLETE.md`, ...)
- [ ] ✅ DEPLOY CHECKLIST preenchido (`03-DEPLOY/DEPLOY_CHECKLIST.md`)
- [ ] ✅ CHANGELOG atualizado (`CHANGELOG.md`)
- [ ] ✅ FIXes documentados (`FIX_*.md` para cada bug)
- [ ] ✅ POST-MORTEM (este documento)

**Total de documentação:** ___ páginas / ___ linhas

---

## 💬 FEEDBACK DOS USUÁRIOS

### Feedback Positivo

> "[Quote de usuário]"  
> — [Nome/Função]

> "[Outro feedback]"  
> — [Nome/Função]

---

### Feedback Negativo / Sugestões

> "[Quote de usuário]"  
> — [Nome/Função]

**Ação tomada:** [Criar issue #___ para endereçar]

---

## 🔗 REFERÊNCIAS

- **PRD:** `/docs/features/[nome]/01-PRD/PRD.md`
- **TECH SPEC:** `/docs/features/[nome]/02-TECH_SPEC/TECH_SPEC.md`
- **Deploy Checklist:** `/docs/features/[nome]/03-DEPLOY/DEPLOY_CHECKLIST.md`
- **Git Tag:** `v1.2.0` ([link GitHub])
- **Issues relacionadas:** #[número], #[número]

---

## 🏆 RETROSPECTIVA - NOTAS FINAIS

### O que o time aprendeu:

1. [Aprendizado técnico - ex: PostgreSQL migrations requerem validação em staging primeiro]
2. [Aprendizado de processo - ex: PRD detalhado economiza tempo no sprint]
3. [Aprendizado de comunicação - ex: Sync diário evitou bloqueios]

---

### Satisfação do time:

**Escala 1-10:**
- Clareza dos requisitos: ___/10
- Qualidade do código: ___/10
- Processo de deploy: ___/10
- Trabalho em equipe: ___/10
- **Média geral:** ___/10

---

### Próximos passos:

- [ ] Aplicar ações de melhoria listadas
- [ ] Monitorar KPIs nos próximos 30 dias
- [ ] Agendar retrospectiva de impacto (30 dias após deploy)
- [ ] Usar este POST-MORTEM como benchmark para próximo projeto

---

**✅ POST-MORTEM Completo!**  
**📅 Data Análise:** [PREENCHER]  
**👤 Responsável:** [NOME]  
**🏷️ Feature:** [NOME]

---

## 📊 ANEXOS

### A. Screenshots

- [Screenshot 1: Dashboard funcionando]
- [Screenshot 2: Lighthouse scores]
- [Screenshot 3: Erro encontrado (se houver)]

### B. Logs Relevantes

```
[Cole logs de erro importantes aqui]
```

### C. Queries Lentas

```sql
-- Query 1 (3.2s)
SELECT ...
```

### D. Código Problemático

```python
# Antes (lento)
for user in users:
    db.query(Transaction).filter(...).all()

# Depois (otimizado)
users_with_transactions = db.query(User).options(
    joinedload(User.transactions)
).all()
```
