# Visão do Projeto — Fluxo de Dados e Coerência

**Feature:** plano-metas-ux-improvements  
**Data:** 28/02/2026  
**Objetivo:** Documentar como os dados fluem no sistema e como os sub-projetos se conectam para cumprir a promessa central do produto.

---

## 1. Promessa Central

> **"Ajudar a pessoa a construir um plano financeiro realista que conecta seus gastos reais ao seu futuro."**

O módulo de Metas existe, mas o plano de gastos e o plano de investimentos (aposentadoria) são ilhas separadas. A pessoa pode criar um plano de gastos desconectado da renda e um plano de investimentos que não considera o que sobra dos gastos. O produto precisa unificar isso.

---

## 2. Fluxo de Dados (Visão Geral)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ENTRADA DE DADOS                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Upload Extrato/Fatura  │  Import Planilha  │  Modo Demo                         │
│  (Nubank, Itaú, BTG…)   │  (CSV/XLS)       │  (dados fictícios)                  │
└─────────────────────────┴──────────────────┴────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA 1 — REALIZADO                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  journal_entries          │  base_marcacoes        │  base_parcelas             │
│  (transações confirmadas) │  (classificação)       │  (parcelamentos realizados) │
└───────────────────────────┴───────────────────────┴─────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│  CAMADA 2             │  │  CAMADA 3              │  │  PATRIMÔNIO            │
│  EXPECTATIVAS         │  │  PLANO BASE            │  │                        │
│  (fase futura)        │  │                        │  │  investimentos_        │
│                       │  │  user_financial_       │  │  portfolio             │
│  base_expectativas    │  │  profile (renda)       │  │  investimentos_        │
│  (sazonais, parcelas  │  │  budget_planning       │  │  transacoes (vínculos)  │
│   futuras)            │  │  (metas por grupo)     │  │                        │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
```

---

## 3. Três Camadas Conceituais

| Camada | Tabelas | Papel |
|--------|---------|-------|
| **1. Realizado** | `journal_entries`, `base_parcelas` | O que já aconteceu (imutável após confirmado) |
| **2. Expectativas** | `base_expectativas` | O que se espera para meses futuros (sazonais, parcelas vindouras) |
| **3. Plano base** | `budget_planning`, `user_financial_profile` | Metas mensais por grupo + âncora de renda |

A camada 2 (`base_expectativas`) está fora do escopo da fase atual, mas o modelo conceitual já está definido no UX doc para evoluções futuras.

---

## 4. Conexões Principais

### 4.1 Renda → Plano

Sem renda declarada, metas e aportes não têm âncora. O sub-projeto 05 (Plano) traz:
- Declaração de renda em `user_financial_profile`
- Compromissos fixos (financiamento, aluguel)
- Desvio real vs. planejado por categoria
- Card "Anos perdidos" quando gasto > plano

### 4.2 Budget ↔ Patrimônio

Quando o usuário faz TED para corretora, o lançamento fica em `journal_entries` com `GRUPO='Investimentos'` mas **não tem conexão** com o que foi comprado. O sub-projeto 06 (Patrimônio) traz:
- Vínculo manual: aporte no extrato ↔ investimento cadastrado
- Match automático por valor + data + corretora
- Rentabilidade CDI, posição em ações, IR estimado
- Resgate/venda vinculado ao extrato

### 4.3 Nudge de Aposentadoria

Cada desvio (gasto acima do plano) tem impacto em anos de trabalho. O sub-projeto 05 calcula:
- "Seus gastos acima do plano este mês representam X dias/meses/anos a mais de trabalho"
- Linguagem motivacional, não punitiva

### 4.4 Upload como Ação Central

O upload alimenta:
- Categorização → `base_marcacoes`
- Conciliação do Plano → `budget_planning`
- Vínculo de aportes na Carteira → `investimentos_transacoes`

Por isso o FAB central passa a ser **Upload**, não Metas. O sub-projeto 02 (UX) implementa essa mudança.

### 4.5 Construtor Unificado (fase futura)

O legado prevê um wizard 4 etapas que une gastos + aposentadoria:
1. Renda e ganhos extraordinários
2. Gastos base (âncora na média dos últimos 3 meses)
3. Gastos sazonais (IPVA, IPTU, matrícula)
4. Aporte + recibo mês a mês

Fora do escopo da fase atual, mas é o destino da evolução.

---

## 5. O Que Cada Sub-projeto Entrega

| Sub-projeto | Entrega | Papel no Todo |
|-------------|---------|---------------|
| **01-admin** | Ciclo de vida de contas, trigger de grupos | Garante que novos usuários chegam com grupos e perfil prontos |
| **02-ux-fundacao** | Bugs, nav, empty states, Perfil na engrenagem | Base de navegação e UX para o resto |
| **03-onboarding** | Welcome, demo, checklist, nudges | Jornada do novo usuário até o primeiro upload |
| **04-upload** | Detecção, rollback, multi-file, planilha | Entrada de dados com menos fricção |
| **05-plano** | Renda, compromissos, desvio, anos perdidos | Âncora de renda e consciência de desvio |
| **06-patrimonio** | Vínculos, CDI, IR, ações, resgate | Fecha o ciclo Budget ↔ Patrimônio |

---

## 6. O Que Fica para Fases Futuras

| Item | Onde está | Motivo de ficar fora |
|------|-----------|----------------------|
| **Gasto parcelado no plano** | PRD legado S6 | Diferente de "compromissos fixos"; exige N registros em `budget_planning` |
| **Construtor wizard 4 etapas** | UX_PLANO_FINANCEIRO_INTEGRADO | Unifica gastos + aposentadoria; exige `base_expectativas` e cashflow engine |
| **base_expectativas** | UX doc, legado TECH_SPEC | Camada de projeção (sazonais, parcelas futuras) |
| **Budget at risk** | UX doc | Usa `base_expectativas` para prever estouro antes do mês |
| **Nudge composto por mês** | UX doc | "Esse estouro vale −R$828 na aposentadoria" |

---

## 7. Ordem de Dependências

```
01-admin ──────────────────────────────────────────┐
02-ux-fundacao ────────────────────────────────────┤
                                                    ▼
03-onboarding ← depende de 01 (trigger de init)    │
      │                                             │
      ├──────────────────────────────→ 04-upload   │
      │                                        │   │
      └──────────────────────────────→ 05-plano   │
                                               │   │
                                    04 + 05 ──→ 06-patrimonio
```

- **01 e 02** são independentes — podem ser feitos em paralelo
- **03** depende de 01 (grupos padrão ao criar conta)
- **04** pode começar após 03 (grupos existem)
- **05** pode ser feito em paralelo com 04
- **06** depende de 04 (uploads) e 05 (plano)

---

## 8. Resumo em Uma Frase

> O app conecta **extrato** (real) → **plano** (meta) → **patrimônio** (investimentos), com **renda** como âncora e **nudges** mostrando o impacto de cada desvio no longo prazo.

A fase atual implementa essa cadeia de forma incremental. Os itens fora de escopo (wizard, expectativas, gasto parcelado) já estão documentados para evoluções futuras.
