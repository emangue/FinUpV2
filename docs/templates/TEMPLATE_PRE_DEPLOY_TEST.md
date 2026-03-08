# ✅ Checklist Pré-Deploy — FinUp

> **Como usar:** Copie este arquivo para `docs/deploy/pre-deploy-tests/TEST_PRE_DEPLOY_YYYY-MM-DD_[commit8].md`,
> preencha o cabeçalho e execute cada item antes do deploy em produção.
> Legenda: ✅ Passou | ❌ Falhou | ⚠️ Parcial | ⏭️ Pulado (justificar)

---

## 📋 Cabeçalho do Teste

| Campo              | Valor                         |
|--------------------|-------------------------------|
| **Data**           | YYYY-MM-DD                    |
| **Branch**         | nome-da-branch                |
| **Commit (HEAD)**  | `xxxxxxxx`                    |
| **Testador(a)**    | Nome                          |
| **Ambiente**       | Local Docker (dev)            |
| **Backend URL**    | http://localhost:8000         |
| **Frontend URL**   | http://localhost:3000         |
| **Tempo total**    | ~___ min                      |
| **Resultado Geral**| ✅ APROVADO / ❌ REPROVADO    |

---

## 🔴 BLOQUEANTES — Parar se qualquer item falhar

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| B1 | Docker: todos os 5 containers `Up` (`docker-compose ps`) | | |
| B2 | `GET /api/health` retorna `{"status":"healthy","database":"connected"}` | | |
| B3 | Login com `admin@financas.com` na tela `/login` funciona | | |
| B4 | Nenhum erro 500 no console do navegador após login | | |
| B5 | `git status` limpo (sem arquivos não commitados não intencionais) | | |

---

## 1. 🔑 AUTENTICAÇÃO

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 1.1 | Tela de login exibe logo, campos e botão | | |
| 1.2 | Login com credenciais inválidas exibe mensagem de erro | | |
| 1.3 | Login com credenciais válidas redireciona para dashboard | | |
| 1.4 | Logout encerra sessão e redireciona para `/login` | | |
| 1.5 | Acesso direto a rota protegida sem login redireciona para `/login` | | |

---

## 2. 📊 DASHBOARD

### 2a. Modo MÊS (mês corrente)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2a.1 | Seletor de período exibe mês atual como padrão | | |
| 2a.2 | Cards de resumo (Receitas, Despesas, Saldo) carregam sem erro | | |
| 2a.3 | Gráfico de categorias exibe barras/pizza | | |
| 2a.4 | Gráfico de evolução mensal carrega | | |
| 2a.5 | Widget Budget vs Realizado exibe dados do mês | | |
| 2a.6 | Lista de maiores gastos carrega | | |
| 2a.7 | Troca de mês (voltar/avançar) atualiza todos os cards | | |

### 2b. Modo YTD (ano até o mês atual)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2b.1 | Seletor muda para YTD corretamente | | |
| 2b.2 | Valores acumulam do Jan até o mês corrente | | |
| 2b.3 | Gráficos atualizam para visão acumulada | | |
| 2b.4 | Comparativo meses anteriores (histórico) exibe corretamente | | |

### 2c. Modo ANO COMPLETO (12 meses)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 2c.1 | Seletor muda para Ano Completo | | |
| 2c.2 | Soma cobre todos os 12 meses do ano | | |
| 2c.3 | Meses futuros exibem valores zerados ou planejados | | |
| 2c.4 | Troca de ano (2024, 2025, 2026) atualiza dados corretamente | | |

---

## 3. 💸 TRANSAÇÕES

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 3.1 | Tela `/transactions` carrega lista de transações | | |
| 3.2 | Paginação funciona (próxima página, anterior) | | |
| 3.3 | Filtro por mês/período retorna resultados corretos | | |
| 3.4 | Filtro por grupo/categoria funciona | | |
| 3.5 | Filtro por texto (estabelecimento) retorna resultados | | |
| 3.6 | Edição de transação: alterar Grupo salva corretamente | | |
| 3.7 | Edição de transação: alterar Subgrupo salva corretamente | | |
| 3.8 | Edição de transação: alterar valor salva corretamente | | |
| 3.9 | Marcar transação para ignorar dashboard funciona | | |
| 3.10 | Exclusão lógica de transação funciona | | |
| 3.11 | Ordenação por data/valor funciona | | |
| 3.12 | Somatório dos valores filtrados aparece corretamente | | |

---

## 4. 💰 ORÇAMENTO / BUDGET

### 4a. Página Principal `/budget`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 4a.1 | Tela carrega cards com grupos e valores | | |
| 4a.2 | Seletor de mês funciona | | |
| 4a.3 | Valores planejados vs realizados exibem corretamente | | |

### 4b. Visão Simples `/budget/simples`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 4b.1 | Tela carrega grupos simplificados | | |
| 4b.2 | Barra de progresso por grupo exibe percentual correto | | |

### 4c. Visão Detalhada `/budget/detalhada`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 4c.1 | Tela carrega por subgrupo/categoria | | |
| 4c.2 | Drill-down em grupo expande subgrupos | | |

### 4d. Planning `/budget/planning`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 4d.1 | Tela carrega metas mensais | | |
| 4d.2 | Edição de meta mensal salva corretamente | | |
| 4d.3 | Copiar mês anterior funciona | | |
| 4d.4 | Valores persistem após refresh da página | | |

### 4e. Configurações `/budget/configuracoes`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 4e.1 | Tela carrega parâmetros de orçamento | | |
| 4e.2 | Salvar configurações funciona | | |

---

## 5. 📅 HISTÓRICO

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 5.1 | Tela `/history` carrega gráfico de evolução | | |
| 5.2 | Série temporal cobre meses com dados reais | | |
| 5.3 | Troca entre grupos/categorias atualiza gráfico | | |
| 5.4 | Comparativo entre anos funciona (se disponível) | | |

---

## 6. 🏦 INVESTIMENTOS / PATRIMÔNIO

### 6a. Portfólio `/investimentos`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6a.1 | Tela carrega lista de investimentos | | |
| 6a.2 | Valor total do portfólio exibe corretamente | | |
| 6a.3 | Distribuição por tipo (FII, Renda Fixa, Ação...) aparece | | |
| 6a.4 | Histórico mensal de cada investimento carrega | | |
| 6a.5 | Adicionar novo investimento abre modal/form | | |
| 6a.6 | Editar investimento existente salva alteração | | |
| 6a.7 | Filtro por tipo/corretora funciona | | |

### 6b. Cenários — Construção

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6b.1 | Botão "Novo Cenário" abre formulário | | |
| 6b.2 | Campos: nome, patrimônio inicial, rendimento mensal, aporte, período | | |
| 6b.3 | Campos de aposentadoria: idade atual, idade alvo, renda mensal alvo | | |
| 6b.4 | Salvar cenário persiste no banco (aparece na lista) | | |
| 6b.5 | Gráfico de projeção aparece ao salvar | | |

### 6c. Cenários — Edição e Configuração

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6c.1 | Editar cenário existente carrega valores atuais | | |
| 6c.2 | Alterar aporte mensal re-calcula projeção | | |
| 6c.3 | Alterar rendimento mensal % re-calcula projeção | | |
| 6c.4 | Adicionar aporte extraordinário (ex: 13º, bônus) funciona | | |
| 6c.5 | Múltiplos aportes extraordinários somam corretamente | | |
| 6c.6 | Deletar cenário remove da lista | | |
| 6c.7 | Cenário principal (flag `principal`) destaca-se corretamente | | |

### 6d. Simulador `/investimentos/simulador`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 6d.1 | Tela do simulador carrega | | |
| 6d.2 | Parâmetros editáveis (patrimônio, aporte, rendimento, anos) | | |
| 6d.3 | Resultado atualiza em tempo real ao mudar parâmetros | | |
| 6d.4 | Gráfico de projeção exibe curva correta | | |

---

## 7. 📋 PLANO FINANCEIRO

### 7a. Wizard de Setup

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7a.1 | Acesso ao plano abre wizard se perfil incompleto | | |
| 7a.2 | Step 1: Renda mensal líquida — salva corretamente | | |
| 7a.3 | Step 2: Idade atual e aposentadoria — salva corretamente | | |
| 7a.4 | Step 3: Patrimônio atual — salva corretamente | | |
| 7a.5 | Step 4: Aporte mensal planejado — salva corretamente | | |
| 7a.6 | Conclusão do wizard redireciona para tela do plano | | |

### 7b. Visualização do Plano

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7b.1 | Card "Resumo do Plano" exibe patrimônio alvo e projeção | | |
| 7b.2 | Card "Anos Perdidos" exibe cálculo (se aplicável) | | |
| 7b.3 | Widget de orçamento no plano exibe metas | | |
| 7b.4 | Projeção de aposentadoria exibe gráfico com curva | | |

### 7c. Ajuste do Plano

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7c.1 | Botão "Ajustar Plano" abre formulário de edição | | |
| 7c.2 | Alterar renda mensal re-calcula cashflow | | |
| 7c.3 | Alterar idade de aposentadoria re-calcula projeção | | |
| 7c.4 | Alterar aporte planejado re-calcula plano | | |
| 7c.5 | Crescimento de renda (% a.a.) salva e influencia projeção | | |
| 7c.6 | Mês/ano de reajuste salva corretamente | | |

### 7d. Base Cashflow (`plano_cashflow_mes`) — Atualização

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 7d.1 | Tabela `plano_cashflow_mes` existe no Docker (`\dt plano*`) | | |
| 7d.2 | Após login, endpoint `/plano/cashflow/ano` retorna dados | | |
| 7d.3 | Após upload de transações, cashflow re-calcula automaticamente | | |
| 7d.4 | Após editar meta de orçamento, cashflow atualiza no próximo acesso | | |
| 7d.5 | Flag `invalidated` muda para `true` quando esperado | | |
| 7d.6 | Meses realizados (passado) usam dados reais (`use_realizado=true`) | | |
| 7d.7 | Meses futuros usam dados planejados (`use_realizado=false`) | | |

---

## 8. 📤 UPLOAD DE ARQUIVOS

> **Critério:** Cada upload deve: processar sem erro 500, exibir preview correto, confirmar importação e verificar transações no banco.

### 8a. Itaú — Fatura (CSV)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8a.1 | Upload de fatura Itaú `.csv` → preview exibe lançamentos | | |
| 8a.2 | Mês da fatura detectado automaticamente | | |
| 8a.3 | Confirmação importa transações para `journal_entries` | | |
| 8a.4 | Re-upload do mesmo arquivo detecta duplicatas | | |

### 8b. Itaú — Extrato (Excel .xls/.xlsx)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8b.1 | Upload de extrato Itaú Excel → preview exibe transações | | |
| 8b.2 | Tipo detectado como `extrato` | | |
| 8b.3 | Confirmação importa para `journal_entries` | | |
| 8b.4 | Re-upload detecta duplicatas | | |

### 8c. Itaú — Extrato (PDF)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8c.1 | Upload de extrato Itaú PDF → preview exibe transações | | |
| 8c.2 | Validação de saldo (início/fim) aparece no log | | |
| 8c.3 | Confirmação importa corretamente | | |

### 8d. Itaú — Fatura (PDF)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8d.1 | Upload de fatura Itaú PDF → preview exibe lançamentos | | |
| 8d.2 | Parcelas detectadas corretamente (formato `X/Y`) | | |
| 8d.3 | Confirmação importa e deduplicação de parcelas funciona | | |

### 8e. BTG Pactual — Extrato (Excel)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8e.1 | Upload de extrato BTG Excel → preview carrega | | |
| 8e.2 | Confirmação importa para `journal_entries` | | |
| 8e.3 | Re-upload detecta duplicatas | | |

### 8f. BTG Pactual — Fatura (Excel .xlsx)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8f.1 | Upload de fatura BTG Excel → preview exibe lançamentos | | |
| 8f.2 | Parcelas detectadas corretamente | | |
| 8f.3 | Confirmação importa sem duplicatas | | |

### 8g. BTG Pactual — Fatura (PDF)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8g.1 | Upload de fatura BTG PDF → preview carrega | | |
| 8g.2 | Confirmação importa corretamente | | |

### 8h. Mercado Pago — Extrato (Excel)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8h.1 | Upload de extrato Mercado Pago Excel → preview carrega | | |
| 8h.2 | Confirmação importa para `journal_entries` | | |

### 8i. Mercado Pago — Extrato (PDF)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8i.1 | Upload de extrato Mercado Pago PDF → preview carrega | | |
| 8i.2 | Validação de saldo aparece | | |
| 8i.3 | Confirmação importa corretamente | | |

### 8j. Mercado Pago — Fatura (PDF)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8j.1 | Upload de fatura Mercado Pago PDF → preview carrega | | |
| 8j.2 | Confirmação importa sem erros | | |

### 8k. Planilha Genérica

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8k.1 | Upload de planilha genérica (CSV/Excel) → preview carrega | | |
| 8k.2 | Mapeamento de colunas funciona | | |
| 8k.3 | Confirmação importa para `journal_entries` | | |

### 8l. Comportamentos Gerais do Upload

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 8l.1 | Arquivo inválido (ex: .txt) exibe mensagem de erro amigável | | |
| 8l.2 | Upload duplicado do mesmo arquivo mostra aviso de duplicata | | |
| 8l.3 | Histórico de uploads exibe arquivos enviados | | |
| 8l.4 | Cancelar na tela de preview não importa nada | | |
| 8l.5 | Classificação automática de grupos pós-upload funciona | | |

---

## 9. ⚙️ CONFIGURAÇÕES

### 9a. Perfil `/settings/profile`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9a.1 | Tela carrega dados do perfil | | |
| 9a.2 | Alterar nome salva corretamente | | |
| 9a.3 | Alterar senha funciona | | |

### 9b. Bancos `/settings/bancos`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9b.1 | Lista de bancos configurados carrega | | |
| 9b.2 | Adicionar banco funciona | | |
| 9b.3 | Editar banco funciona | | |

### 9c. Cartões `/settings/cartoes`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9c.1 | Lista de cartões carrega | | |
| 9c.2 | Adicionar cartão funciona | | |
| 9c.3 | Editar/remover cartão funciona | | |

### 9d. Grupos `/settings/grupos`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9d.1 | Lista de grupos carrega (`base_marcacoes`) | | |
| 9d.2 | Adicionar novo grupo funciona | | |
| 9d.3 | Editar grupo existente funciona | | |
| 9d.4 | Grupos aparecem nos filtros de transações | | |

### 9e. Marcações `/settings/marcacoes`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9e.1 | Lista de padrões de classificação carrega | | |
| 9e.2 | Adicionar novo padrão funciona | | |
| 9e.3 | Editar padrão existente funciona | | |

### 9f. Categorias `/settings/categorias`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9f.1 | Lista de categorias carrega | | |
| 9f.2 | Adicionar categoria funciona | | |

### 9g. Categorias Genéricas `/settings/categorias-genericas`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9g.1 | Tela carrega regras de classificação genérica | | |
| 9g.2 | Adicionar/editar regra funciona | | |

### 9h. Exclusões `/settings/exclusoes`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9h.1 | Lista de transações excluídas carrega | | |
| 9h.2 | Restaurar exclusão funciona | | |

### 9i. Visibilidade de Telas `/settings/screens`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9i.1 | Tela exibe quais seções estão ativas/inativas | | |
| 9i.2 | Desativar tela esconde do menu lateral | | |
| 9i.3 | Reativar tela restaura no menu | | |

### 9j. Backup `/settings/backup`

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 9j.1 | Opção de backup carrega | | |
| 9j.2 | Download de backup gera arquivo | | |

---

## 10. 📱 MOBILE (se aplicável)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 10.1 | Layout responsivo em viewport 375px (iPhone) | | |
| 10.2 | Menu hamburguer funciona | | |
| 10.3 | Tela `/mobile` carrega (se existir rota específica) | | |
| 10.4 | Dashboard mobile exibe corretamente | | |

---

## 11. 🧑‍💼 ADMIN (se aplicável)

| # | Teste | Resultado | Observação |
|---|-------|-----------|------------|
| 11.1 | Acesso ao painel admin (porta 3001) funciona | | |
| 11.2 | Lista de usuários carrega | | |
| 11.3 | Usuário não-admin não acessa rotas admin | | |

---

## 12. 🔌 APIs — Smoke Tests (via curl ou Swagger)

| # | Endpoint | Resultado | Observação |
|---|----------|-----------|------------|
| 12.1 | `GET /api/health` → `{"status":"healthy"}` | | |
| 12.2 | `GET /api/v1/transactions/list` (autenticado) → 200 | | |
| 12.3 | `GET /api/v1/dashboard/summary` → 200 | | |
| 12.4 | `GET /api/v1/budget/list` → 200 | | |
| 12.5 | `GET /api/v1/investimentos/portfolio` → 200 | | |
| 12.6 | `GET /api/v1/investimentos/cenarios` → 200 | | |
| 12.7 | `GET /api/v1/plano/perfil` → 200 | | |
| 12.8 | `GET /api/v1/plano/cashflow/ano` → 200 | | |
| 12.9 | `GET /api/v1/upload/history` → 200 | | |
| 12.10 | `GET /docs` (Swagger UI) carrega | | |

---

## 13. 🚀 PÓS-APROVAÇÃO — Checklist de Deploy

> Execute só após todos os itens bloqueantes e críticos estarem ✅

| # | Ação | Resultado | Observação |
|---|------|-----------|------------|
| 13.1 | `git status` limpo, tudo commitado | | |
| 13.2 | `git push origin <branch>` concluído | | |
| 13.3 | Script de deploy executado (`./scripts/deploy/deploy.sh`) | | |
| 13.4 | Health check em produção: `curl https://meufinup.com.br/api/health` | | |
| 13.5 | Login em produção funciona | | |
| 13.6 | Dashboard em produção carrega | | |

---

## 📝 Observações Gerais

```
[Escreva aqui qualquer nota relevante sobre o teste:
 - Comportamentos inesperados encontrados
 - Itens pulados e motivo
 - Bugs identificados e se foram corrigidos antes do deploy]
```

---

## 🐛 Bugs Encontrados

| ID | Descrição | Severidade | Status | Fix commit |
|----|-----------|-----------|--------|-----------|
|    |           |           |        |           |

---

*Template FinUp · Versão 1.0 · Criado em 2026-03-08*
*Copiar para `docs/deploy/pre-deploy-tests/TEST_PRE_DEPLOY_YYYY-MM-DD_[commit8].md` a cada deploy*
