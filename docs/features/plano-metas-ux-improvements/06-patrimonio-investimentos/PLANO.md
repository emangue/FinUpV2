# PLANO DE IMPLEMENTAÇÃO — Patrimônio e Investimentos
> Sub-projeto 06 | Sprints 8, 9 | Estimativa: ~26h  
> **Pré-requisitos:** Sub-projeto 04 (upload completo) + Sub-projeto 05 (plano financeiro)

---

## Sprint 8 — Vínculos + Renda Fixa + Match (~13h)

### Backend (8h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.01 | Migrations: criar `investimentos`, `investimentos_transacoes`, `investimentos_cotacoes` | 1h |
| A.02 | CRUD `investimentos`: `GET /investimentos`, `POST`, `PUT /{id}`, `DELETE /{id}` | 1.5h |
| A.03 | Endpoint `POST /investimentos/{id}/vincular` — criar InvestimentoTransacao + atualizar categoria JE | 1h |
| A.04 | Job diário BACEN: CDI (série 4389), IGPM (189), INCC (192), IPCA (433) | 1.5h |
| A.05 | Função `calcular_rentabilidade_cdi()` com tabela regressiva de IR | 1.5h |
| A.06 | Endpoint `GET /investimentos/{id}/rentabilidade` | 0.5h |
| A.07 | Endpoint `GET /investimentos/sugestoes-match` (heurística: valor ±2% + data ±3 dias + palavra corretora) | 1h |

### Frontend (5h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.01 | Tela `/mobile/carteira` com `CarteiraView` agrupado por tipo | 1h |
| F.02 | Componente `InvestimentoDetailCard` para renda fixa (principal, valor atual, rendimento, IR) | 1.5h |
| F.03 | Componente `VinculoAporteModal` acessível do detalhe de transação | 1.5h |
| F.04 | Componente `SugestoesMatchCard` na tela Carteira (lista de matches sugeridos + confirmar/ignorar) | 1h |

---

## Sprint 9 — Ações + IR + Resgate + Saldo (~13h)

### Backend (7h)

| Task | Descrição | Est. |
|------|-----------|------|
| A.08 | Job brapi: buscar preços de ações/FIIs a cada 15min (dias úteis, horário pregão) | 1.5h |
| A.09 | Função `calcular_posicao_acoes()` com custo médio ponderado + cache Redis | 2h |
| A.10 | Endpoint `GET /investimentos/ir-estimado?ano=` com regras: ações, FIIs, renda fixa | 2h |
| A.11 | Endpoint `POST /investimentos/{id}/resgatar` — registrar venda/resgate + atualizar posição | 1h |
| A.12 | Endpoint `GET /investimentos/saldo-corretora` — por banco/corretora | 0.5h |

### Frontend (6h)

| Task | Descrição | Est. |
|------|-----------|------|
| F.05 | `InvestimentoDetailCard` para ações: quantidade, custo médio, posição, P&L, variação dia | 2h |
| F.06 | Componente `VinculoResgateModal` — registrar venda/resgate com quantidade | 1.5h |
| F.07 | Componente `IREstimadoView` — tabela por investimento + total + disclaimer | 1h |
| F.08 | Componente `SaldoCorretoraCard` — saldo disponível por corretora | 0.5h |
| F.09 | Adicionar "Carteira" no BottomNav (aba dedicada) | 0.5h |
| F.10 | Configuração de `BRAPI_TOKEN` em variável de ambiente + documentar no `.env.example` | 0.5h |

---

## Validação pelo Usuário

**Sprint 8:**
1. [ ] Criar investimento "CDB XP 120% CDI" com data e valor inicial
2. [ ] Abrir transação do extrato "TED XP R$ 5.000" → vincular ao investimento criado → transação muda categoria para "Investimento"
3. [ ] Abrir tela Carteira → CDB aparece com valor atual calculado (> R$ 5.000)
4. [ ] Sugestão de match aparece para transação de corretora sem vínculo

**Sprint 9:**
5. [ ] Criar ação "ITSA4 — 200 cotas — custo R$ 2.000" → preço atual carregado da brapi
6. [ ] Ver P&L positivo ou negativo corretamente calculado
7. [ ] Ver IR estimado: ações isentas se vendas < R$ 20k, FIIs sempre 20%, renda fixa tabela regressiva
8. [ ] Registrar venda de 50 cotas ITSA4 → posição atualiza para 150 cotas
9. [ ] Saldo disponível na XP calculado corretamente

---

## Ordem de Execução

```
A.01 (migrations — base de tudo)
  ↓
A.02 (CRUD investimentos) → A.03 (vincular)
A.04 (job BACEN) → A.05 + A.06 (rentabilidade CDI)
A.07 (match automático)
  ↓
F.01 → F.02 → F.03 → F.04 (Sprint 8 front)
  ↓
A.08 (job brapi) → A.09 (posição ações)
A.10 (IR estimado) → A.11 (resgate) → A.12 (saldo)
  ↓
F.05 → F.06 → F.07 → F.08 → F.09 → F.10 (Sprint 9 front)
```

---

## Variáveis de Ambiente Novas

```bash
# Adicionar ao .env
BRAPI_TOKEN=seu_token_brapi_aqui  # https://brapi.dev/dashboard
# CDI/IGPM/IPCA: API BACEN pública — sem token necessário
```

---

## Commit por Sprint

```bash
# Sprint 8
git add app_dev/backend/app/domains/investimentos/ app_dev/backend/migrations/ app_dev/frontend/src/features/investimentos/
git commit -m "feat(investimentos): S11+S12+S13 — vínculos aportes, match automático, CDI renda fixa"

# Sprint 9
git add app_dev/backend/app/domains/investimentos/ app_dev/frontend/src/features/investimentos/ app_dev/frontend/src/app/mobile/carteira/
git commit -m "feat(investimentos): S14+S15+S16+S17+S18 — ações, IR estimado, resgate, saldo corretora, indexadores"
```
