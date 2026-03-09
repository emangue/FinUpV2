# ✅ Checklist Pré-Deploy — FinUp

> **Gerado automaticamente por** `./scripts/deploy/predeploy.sh` em 2026-03-08 21:15:01
> Legenda: ✅ Passou (auto) | ❌ Falhou (auto) | ⬜ Requer teste manual | ⏭️ Pulado

---

## 📋 Cabeçalho do Teste

| Campo                | Valor                                                         |
|----------------------|---------------------------------------------------------------|
| **Data**             | 2026-03-08                                                        |
| **Branch**           | `perf/performance-v2-n0-n4`                                                    |
| **Commit (HEAD)**    | `3e8830c2`                                                    |
| **Descrição commit** | docs: adiciona template e checklist pré-deploy 2026-03-08 (commit 0c7e1955)                                                  |
| **Testador(a)**      | _____________                                                 |
| **Ambiente**         | Local Docker (dev)                                            |
| **Backend URL**      | http://localhost:8000                                                     |
| **Frontend URL**     | http://localhost:3000                                                    |
| **Gerado em**        | 2026-03-08 21:15:01                                                 |
| **Auto: pass/fail**  | 22 ✅ / 0 ❌ / 0 ⏭️ de 22 testes |
| **Status auto**      | ✅ OK — prosseguir com testes manuais                                                 |
| **Resultado Geral**  | ⬜ APROVADO / ⬜ REPROVADO ← *preencher ao final dos testes manuais* |

---

## 🔴 BLOQUEANTES (automatizados)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| B1 | Docker: todos os 5 containers `Up` | ✅ | 5/5 running |
| B2 | `GET /api/health` retorna `{"status":"healthy"}` | ✅ | {"status":"healthy","database":"connected"} |
| B3 | Login `admin@financas.com` retorna JWT token | ✅ | Token JWT obtido |
| B4 | `git status` limpo (sem uncommitted) | ✅ | Sem uncommitted |
| B5 | Nenhum erro 500 no console do navegador após login | ⬜ | *Manual* |

---

## 1. 🔑 AUTENTICAÇÃO (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 1.1 | Tela de login exibe logo, campos e botão | ⬜ | |
| 1.2 | Login com credenciais inválidas exibe mensagem de erro | ⬜ | |
| 1.3 | Login com credenciais válidas redireciona para dashboard | ⬜ | |
| 1.4 | Logout encerra sessão e redireciona para `/login` | ⬜ | |
| 1.5 | Acesso direto a rota protegida sem login → redireciona | ⬜ | |

---

## 2. 📊 DASHBOARD (manual)

### 2a. Modo MÊS

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2a.1 | Seletor exibe mês atual como padrão | ⬜ | |
| 2a.2 | Cards Receitas / Despesas / Saldo carregam | ⬜ | |
| 2a.3 | Gráfico de categorias exibe | ⬜ | |
| 2a.4 | Widget Budget vs Realizado exibe | ⬜ | |
| 2a.5 | Troca de mês atualiza todos os cards | ⬜ | |

### 2b. Modo YTD

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2b.1 | Seletor muda para YTD | ⬜ | |
| 2b.2 | Valores acumulam Jan → mês atual | ⬜ | |
| 2b.3 | Gráficos atualizam para visão acumulada | ⬜ | |

### 2c. Modo ANO COMPLETO

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2c.1 | Seletor muda para Ano Completo | ⬜ | |
| 2c.2 | Soma cobre 12 meses do ano | ⬜ | |
| 2c.3 | Troca de ano (2025 ↔ 2026) atualiza dados | ⬜ | |

---

## 3. 💸 TRANSAÇÕES (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 3.1 | Lista carrega com paginação | ⬜ | |
| 3.2 | Filtro por mês/período funciona | ⬜ | |
| 3.3 | Filtro por grupo/categoria funciona | ⬜ | |
| 3.4 | Filtro por texto (estabelecimento) funciona | ⬜ | |
| 3.5 | Edição: alterar Grupo e Subgrupo salva | ⬜ | |
| 3.6 | Edição: alterar valor salva | ⬜ | |
| 3.7 | Marcar IgnorarDashboard funciona | ⬜ | |
| 3.8 | Exclusão lógica funciona | ⬜ | |
| 3.9 | Somatório dos valores filtrados exibe | ⬜ | |

---

## 4. 💰 ORÇAMENTO / BUDGET (manual)

| # | Tela / Ação | Resultado | Observação |
|---|-------------|-----------|------------|
| 4a.1 | `/budget` — cards com grupos e valores | ⬜ | |
| 4b.1 | `/budget/simples` — barras de progresso | ⬜ | |
| 4c.1 | `/budget/detalhada` — drill-down em subgrupos | ⬜ | |
| 4d.1 | `/budget/planning` — metas mensais carregam | ⬜ | |
| 4d.2 | Edição de meta mensal salva | ⬜ | |
| 4d.3 | Copiar mês anterior funciona | ⬜ | |
| 4e.1 | `/budget/configuracoes` — salva | ⬜ | |

---

## 5. 📅 HISTÓRICO (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 5.1 | `/history` carrega gráfico de evolução | ⬜ | |
| 5.2 | Troca de grupo/categoria atualiza gráfico | ⬜ | |
| 5.3 | Comparativo entre anos funciona | ⬜ | |

---

## 6. 🏦 INVESTIMENTOS / PATRIMÔNIO (manual)

### 6a. Portfólio

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6a.1 | Lista de investimentos carrega | ⬜ | |
| 6a.2 | Valor total e distribuição por tipo exibem | ⬜ | |
| 6a.3 | Adicionar / editar investimento funciona | ⬜ | |

### 6b. Cenários — Construção

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6b.1 | "Novo Cenário" abre form | ⬜ | |
| 6b.2 | Campos base (nome, patrimônio, rendimento, aporte, período) salvam | ⬜ | |
| 6b.3 | Campos aposentadoria (idades, renda alvo) salvam | ⬜ | |
| 6b.4 | Cenário aparece na lista e gráfico exibe | ⬜ | |

### 6c. Cenários — Ajuste fino

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6c.1 | Editar cenário carrega valores atuais | ⬜ | |
| 6c.2 | Alterar aporte re-calcula projeção | ⬜ | |
| 6c.3 | Adicionar aporte extraordinário funciona | ⬜ | |
| 6c.4 | Deletar cenário funciona | ⬜ | |

### 6d. Simulador `/investimentos/simulador`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6d.1 | Tela carrega | ⬜ | |
| 6d.2 | Parâmetros atualizam resultado e gráfico | ⬜ | |

---

## 7. 📋 PLANO FINANCEIRO (manual)

### 7a-b. Wizard e Visualização

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7a.1 | Wizard abre se perfil incompleto | ⬜ | |
| 7a.2 | Steps 1–4 do wizard salvam | ⬜ | |
| 7b.1 | Card Resumo do Plano exibe | ⬜ | |
| 7b.2 | ProjecaoChart exibe curva de crescimento | ⬜ | |
| 7b.3 | TabelaReciboAnual exibe | ⬜ | |

### 7c. Ajuste do Plano

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7c.1 | Form de ajuste abre | ⬜ | |
| 7c.2 | Alterar renda re-calcula cashflow | ⬜ | |
| 7c.3 | Alterar aporte planejado re-calcula | ⬜ | |
| 7c.4 | Crescimento de renda/gastos salvam | ⬜ | |

### 7d. Base Cashflow `plano_cashflow_mes` (automatizado)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7d.1 | Tabela existe no banco | ✅ | 1 registros |
| 7d.2 | `GET /api/v1/plano/cashflow?ano=2026` → 200 | ✅ | HTTP 200 |
| 7d.3 | Após upload, cashflow re-calcula no próximo request | ⬜ | *Manual* |
| 7d.4 | Meses passados usam `use_realizado=true` | ⬜ | *Manual* |

---

## 8. 📤 UPLOAD DE ARQUIVOS (manual)

> Critério: sem erro 500, preview correto, importação OK, duplicatas detectadas

| # | Banco / Formato | Resultado | Observação |
|---|-----------------|-----------|------------|
| 8a | Itaú — Fatura CSV | ⬜ | |
| 8b | Itaú — Extrato Excel | ⬜ | |
| 8c | Itaú — Extrato PDF | ⬜ | |
| 8d | Itaú — Fatura PDF | ⬜ | |
| 8e | BTG — Extrato Excel | ⬜ | |
| 8f | BTG — Fatura Excel | ⬜ | |
| 8g | BTG — Fatura PDF | ⬜ | |
| 8h | Mercado Pago — Extrato Excel | ⬜ | |
| 8i | Mercado Pago — Extrato PDF | ⬜ | |
| 8j | Mercado Pago — Fatura PDF | ⬜ | |
| 8k | Planilha Genérica | ⬜ | |
| 8l.1 | Arquivo inválido → erro amigável (não 500) | ⬜ | |
| 8l.2 | Re-upload → aviso de duplicata | ⬜ | |
| 8l.3 | Histórico de uploads exibe arquivos enviados | ⬜ | |

---

## 9. ⚙️ CONFIGURAÇÕES (manual)

| # | Tela | Resultado | Observação |
|---|------|-----------|------------|
| 9a | `/settings/profile` — salva alterações | ⬜ | |
| 9b | `/settings/bancos` — CRUD funciona | ⬜ | |
| 9c | `/settings/cartoes` — CRUD funciona | ⬜ | |
| 9d | `/settings/grupos` — CRUD + aparece em filtros | ⬜ | |
| 9e | `/settings/marcacoes` — CRUD funciona | ⬜ | |
| 9f | `/settings/categorias` — CRUD funciona | ⬜ | |
| 9g | `/settings/categorias-genericas` — CRUD funciona | ⬜ | |
| 9h | `/settings/exclusoes` — restaurar funciona | ⬜ | |
| 9i | `/settings/screens` — toggle ativa/desativa telas | ⬜ | |
| 9j | `/settings/backup` — download funciona | ⬜ | |

---

## 10. 📱 MOBILE (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 10.1 | Layout responsivo 375px (DevTools) | ⬜ | |
| 10.2 | Menu hamburguer abre/fecha | ⬜ | |
| 10.3 | Dashboard mobile exibe cards | ⬜ | |

---

## 11. 🧑‍💼 ADMIN — porta 3001 (manual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 11.1 | http://localhost:3001 abre | ⬜ | |
| 11.2 | Lista de usuários carrega | ⬜ | |
| 11.3 | Não-admin recebe 403 em rotas admin | ⬜ | |

---

## 12. 🔌 API — Smoke Tests (automatizados)

| # | Endpoint | Resultado | Observação |
|---|----------|-----------|------------|
| 12.1  | `GET /api/health`                           | ✅  | HTTP 200  |
| 12.2  | `GET /api/v1/dashboard/last-month-with-data`| ✅  | HTTP 200  |
| 12.3  | `GET /api/v1/dashboard/metrics`             | ✅  | HTTP 200  |
| 12.4  | `GET /api/v1/budget`                        | ✅  | HTTP 200  |
| 12.5  | `GET /api/v1/investimentos/`                | ✅  | HTTP 200  |
| 12.6  | `GET /api/v1/investimentos/cenarios`        | ✅  | HTTP 200  |
| 12.7  | `GET /api/v1/plano/perfil`                  | ✅  | HTTP 200  |
| 12.8  | `GET /api/v1/plano/cashflow?ano=2026`     | ✅  | HTTP 200  |
| 12.9  | `GET /api/v1/upload/history`                | ✅  | HTTP 200  |
| 12.10 | `GET /api/v1/grupos/`                       | ✅ | HTTP 200 |
| 12.11 | `GET /docs` (Swagger UI)                    | ✅ | HTTP 200 |

---

## 🗄️ Banco de Dados (automatizado)

| Tabela | Status | Registros |
|--------|--------|-----------|
| `journal_entries`          | ✅ | 8096 registros |
| `investimentos_portfolio`  | ✅ | 94 registros |
| `investimentos_cenarios`   | ✅ | 6 registros |
| `plano_cashflow_mes`       | ✅ | 1 registros |
| `budget_planning`          | ✅ | 1250 registros |
| `base_marcacoes`           | ✅ | 956 registros |
| `users`                    | ✅ | 7 registros |

---

## 13. 🚀 PÓS-APROVAÇÃO — Deploy (preencher ao executar)

| # | Ação | Resultado | Observação |
|---|------|-----------|------------|
| 13.1 | `git push origin perf/performance-v2-n0-n4` concluído | ⬜ | |
| 13.2 | `./scripts/deploy/deploy.sh` executado | ⬜ | |
| 13.3 | Health produção: `curl https://meufinup.com.br/api/health` | ⬜ | |
| 13.4 | Login em produção funciona | ⬜ | |
| 13.5 | Dashboard em produção carrega sem erros | ⬜ | |

---

## 📝 Observações Gerais

```
[Escreva aqui qualquer nota durante ou após os testes manuais]
```

---

## 🐛 Bugs Encontrados

| ID | Descrição | Severidade | Status | Fix commit |
|----|-----------|-----------|--------|------------|
|    |           |           |        |            |

---

*FinUp · Gerado por `predeploy.sh` · Branch: perf/performance-v2-n0-n4 · Commit: 3e8830c2 · 2026-03-08 21:15:01*
