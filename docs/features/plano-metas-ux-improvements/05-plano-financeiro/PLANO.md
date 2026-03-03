# PLANO DE IMPLEMENTAÇÃO — Plano Financeiro
> Sub-projeto 05 | Sprints 6, 7 | Estimativa: ~28h  
> **Pré-requisito:** Sub-projeto 03 (`user_financial_profile` criado no onboarding)

---

## Sprint 6 — Renda, Compromissos e Desvio (~14h)

### Backend (8h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.01 | Migrations: criar `user_financial_profile` (se não existe), `plano_metas_categoria`, `plano_compromissos` | 1h |
| A.02 | Endpoint `POST /plano/renda` — upsert renda no perfil | 0.5h |
| A.03 | Endpoints `GET /plano/compromissos`, `POST`, `DELETE /{id}` | 1.5h |
| A.04 | Endpoint `GET /plano/orcamento?ano=&mes=` — gasto real vs. meta por grupo | 2h |
| A.05 | Endpoint `POST /plano/metas/{grupo_id}` — salvar meta de um grupo | 1h |
| A.06 | Testes: renda salva corretamente, compromissos desativam (não deletam), orçamento retorna percentuais | 1h |
| A.07 | Integrar cálculo de `disponivel_real` = renda - comprometido fixo | 1h |

### Frontend (6h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.01 | Tela `/mobile/perfil/financeiro` com `RendaDeclaracaoForm` | 1.5h |
| F.02 | Componente `CompromissosFixosList` + modal de adição | 2h |
| F.03 | Componente `OrcamentoCategorias` com barras de progresso coloridas | 1.5h |
| F.04 | Widget `BudgetWidget` no dashboard (nudge se renda não declarada) | 1h |

---

## Sprint 7 — Projeção, Tabela e Impacto (~14h)

### Backend (6h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.08 | Endpoint `GET /plano/projecao?meses=12&reducao_pct=0` — média histórica + slider | 2h |
| A.09 | Endpoint `GET /plano/categorias/detalhado?ano=&mes=` — tabela com comparativo mês anterior | 2h |
| A.10 | Endpoint `GET /plano/impacto-longo-prazo` — cálculo juros compostos + dias de trabalho | 1.5h |
| A.11 | Endpoint `PUT /plano/perfil` — atualizar idade, aposentadoria, patrimônio, taxa retorno | 0.5h |

### Frontend (8h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.05 | Tela `/mobile/plano` — página principal do plano | 1h |
| F.06 | Componente `ProjecaoChart` (Recharts + slider de redução) | 2.5h |
| F.07 | Componente `TabelaDetalhadaCategorias` (ordenável, drill-down por grupo) | 2h |
| F.08 | Componente `AnosPerdidasCard` com linguagem motivacional | 1h |
| F.09 | Form de configuração: idade, aposentadoria, patrimônio, taxa | 1h |
| F.10 | Adicionar "Plano" na navegação (BottomNav do 02-ux-fundacao) | 0.5h |

---

## Validação pelo Usuário

**Sprint 6:**
1. [ ] Acessar Perfil → Financeiro → Declarar renda R$ 8.000 → salvo ✅
2. [ ] Dashboard mostra: "Renda R$ 8.000 | Gasto R$ X | Poupança Y%"
3. [ ] Adicionar compromisso fixo "Financiamento R$ 800/mês, 24 meses" → aparece na lista
4. [ ] Gasto em Alimentação ultrapassa meta → barra fica vermelha no dashboard

**Sprint 7:**
5. [ ] Tela Plano → Projeção 12 meses exibida como gráfico
6. [ ] Slider "Reduzir gastos em 10%" → linha muda em tempo real
7. [ ] Tabela de categorias ordenável por % utilizado
8. [ ] Card "Anos perdidos" aparece quando há déficit (não aparece quando dentro do plano)
9. [ ] Ajustar taxa de retorno para 10% → cálculo de impacto atualiza

---

## Ordem de Execução

```
A.01 (migrations — precisa estar pronto antes de tudo)
  ↓
A.02 + A.03 + A.05 (renda + compromissos + metas)
  ↓
A.04 (orcamento — usa metas criadas no A.05)
  ↓
F.01 → F.02 → F.03 → F.04 (Sprint 6 front)
  ↓
A.08 (projecao — usa renda + histórico)
A.09 (detalhado — usa metas do A.05)
A.10 + A.11 (impacto + perfil)
  ↓
F.05 → F.06 → F.07 → F.08 → F.09 → F.10 (Sprint 7 front)
```

---

## Commit por Sprint

```bash
# Sprint 6
git add app_dev/backend/app/domains/plano/ app_dev/backend/migrations/ app_dev/frontend/src/features/plano/
git commit -m "feat(plano): S5+S6+S7 — renda, compromissos fixos e desvio por categoria"

# Sprint 7
git add app_dev/backend/app/domains/plano/ app_dev/frontend/src/features/plano/ app_dev/frontend/src/app/mobile/plano/
git commit -m "feat(plano): S8+S9+S10 — projeção 12 meses, tabela detalhada e impacto longo prazo"
```
