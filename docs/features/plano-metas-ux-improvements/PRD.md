# PRD — Revisão Completa do Módulo de Metas e Plano Financeiro

**Branch:** `feature/plano-metas-ux-improvements`  
**Data:** 26/02/2026  
**Status:** 🟡 Em planejamento

---

## 1. Contexto e Problema

O módulo de Metas (`/mobile/budget`) existe e funciona, mas tem uma série de bugs e lacunas conceituais que impedem que o produto cumpra sua promessa central: **ajudar a pessoa a construir um plano financeiro realista que conecta seus gastos reais ao seu futuro**.

Hoje o plano de gastos e o plano de investimentos (aposentadoria) são ilhas separadas. A pessoa consegue criar um plano de gastos completamente desconectado da realidade da sua renda, e um plano de investimentos que não considera o quanto ela precisa guardar para cumprir os gastos. Isso torna o produto intelectualmente inconsistente.

---

## 2. Escopo — O que entra nesta feature

### 2a. Bugs urgentes (UX quebrada)

| ID | Bug | Onde | Impacto |
|----|-----|------|---------|
| B1 | "Jogar plano para meses posteriores" não funciona ao editar meta existente | `/mobile/budget/edit` ou `EditGoalModal` | Alto |
| B2 | Botão Voltar do subgrupo → círculo vicioso (não volta para tela de metas) | `/mobile/budget/[goalId]` → subgrupo → router.back() → volta para goalId | Alto |
| B3 | Scroll da tela de metas não desce até o final | `/mobile/budget` | Médio |
| B4 | Tela de ajuste de metas mal formatada em mobile | `/mobile/budget/edit` | Médio |

### 2b. Feature: Plano com consciência de renda (âncora conceitual)

O maior gap do produto. O plano precisa saber quanto a pessoa ganha para que qualquer meta de gasto ou investimento faça sentido.

**Ideia central (inspirada no fluxo do plano de aposentadoria):**
1. Pede para a pessoa subir os dados dos últimos 3 meses de gastos (ou usa dados já existentes no app)
2. Com esses dados, faz perguntas:
   - Quanto você ganha em média por mês?
   - Tem meses com ganhos extraordinários? (13º, bônus, freelance...)
3. Usa os gastos já categorizados para propor um plano inicial
4. Resultado final: plano de gastos + plano de aposentadoria integrados na mesma restrição orçamentária
5. Gastos excepcionais (IPVA, IPTU, matrícula, seguro): campo específico por mês

### 2c. Feature: Gasto parcelado no plano

Hoje não tem como inserir um gasto parcelado no plano. A pessoa precisa lançar manualmente em cada mês.

- Campo "parcelado": sim/não  
- Se sim: número de parcelas, valor da parcela  
- Grupo do gasto (vincula ao grupo existente)  
- Backend: criar N registros em `budget_planning` (um por mês, marcado como parcela)

### 2d. Feature: Nudge de custo de desvio

Quando a pessoa gasta mais do que planejou (ou poupa menos), mostrar:
- Quanto um gasto adicional de R$ X acima do plano custa ao patrimônio em 10/20/30 anos
- Quanto estar sempre X% acima do plano custaria no total
- Mesmo raciocínio para savings: "se você guardasse R$ X a mais por mês, chegaria Y anos antes"
- Mostrar "meses/anos perdidos" se a pessoa travar dinheiro que estava no plano de investimentos

### 2e. Feature: Seletor de mês de início do plano

- Botão "A partir de quando seu plano começa?"
- Escolher mês/ano de início  
- Preview: resumo do que será projetado em cada mês futur (receita esperada, despesa, aporte)

### 2f. Feature: Tabela resumo do plano

Visão tabular tipo "planilha":
| Mês | Receita esperada | Despesa planejada | Aporte esperado | Saldo |
|-----|-----------------|-------------------|-----------------|-------|
| Mar/26 | R$ 15.000 | R$ 11.200 | R$ 3.800 | ✅ |

- Se a pessoa quiser colocar aporte maior do que o saldo permite → bloquear (restrição orçamentária)
- Se quiser colocar aporte menor → permitir (decisão dela)

### 2g. Feature: Alerta de anos perdidos por excesso de gastos

- Quando a pessoa está travando dinheiro de investimento por gastar acima do plano:
  > "Com esse nível de gasto, você está perdendo **3,2 anos** de aposentadoria"

### 2h. Feature: Conexão Budget ↔ Patrimônio (vínculo de aportes)

Quando o usuário faz uma TED/PIX para a corretora (ex: "TED XP INVEST R$5.000"), esse lançamento fica no `journal_entries` com `GRUPO='Investimentos'` mas **não tem conexão com o que ele realmente comprou** no patrimônio. O app não sabe se foi PETR4, CDB ou MXRF11.

**Ideia central:** após o upload, o app detecta transações de investimento e abre um modal para o usuário detalhar em qual(ais) produto(s) aquele dinheiro foi. A partir disso:
- `investimentos_transacoes` fica alimentado com a transação detalhada, vinculada ao `journal_entry_id`
- `investimentos_historico.aporte_mes` é preenchido automaticamente (corrige o cálculo de rentabilidade)
- Para ações/FIIs: guarda `codigo_ativo` + `quantidade` + `preco_unitario` → custo médio calculável
- Para renda fixa: guarda `indexador` + `taxa_pct` + `data_vencimento` → projeção via CDI do Bacen

**Match automático:** se o portfolio tem `texto_match="XP RENDA FIXA"` e o `Estabelecimento` do journal_entry contém esse texto → sugere vínculo automático sem interação do usuário.

**Job diário de cotações:**
- CDI/IPCA/SELIC: API gratuita do Banco Central (sem autenticação, sem limite)
- Ações/FIIs/ETFs: brapi.dev (plano gratuito = 15.000 req/mês, suficiente para uso pessoal)
- Cache local em `market_data_cache` — roda 1x/dia às 18h (após fechamento B3)

**IR estimado (ações):**
- Base de cálculo: `(preço_atual - custo_médio_ponderado) × posição_líquida × 15%`
- Exibido como "Patrimônio líquido estimado após IR": `total - IR_estimado`
- Renda fixa: IR já é retido na fonte — registra `ir_retido` quando vem no extrato

---

## 3. Fora do escopo (não entra nesta branch)

- Redesign completo da UI de metas
- Integração com Open Finance / importação automática de renda
- Análise preditiva de gastos por ML
- Notificações push
- Integração com API B3 em tempo real (cotações ao vivo)
- Cálculo exato de IR com deduções de custos operacionais (taxa B3, corretagem)

---

## 4. User Stories

### S1 — Propagação de plano (fix B1)
> Como usuário, quando edito o valor de uma meta existente e marco "aplicar para meses posteriores", quero que todos os meses seguintes sejam atualizados com o novo valor.

**Acceptance criteria:**
- Ao editar meta via `EditGoalModal` ou tela de edição, o checkbox "Replicar para meses posteriores" atualiza todos os meses de `mes_referencia` até dezembro do mesmo ano
- Se a meta já existe no mês destino → faz upsert (atualiza)
- Se não existe → cria
- Feedback de quantos meses foram atualizados

### S2 — Navegação sem loop (fix B2)
> Como usuário, quando estou na tela de um grupo de meta e clico em um subgrupo (vai para transações), e depois pressiono Voltar, quero retornar à tela de metas (lista), não ficar em loop entre goalId e transações.

**Acceptance criteria:**
- Clique em subgrupo → vai para `/mobile/transactions` com filtros
- Botão voltar em `/mobile/transactions` → volta para `/mobile/budget/{goalId}?mes=...`
- Botão voltar em `/mobile/budget/{goalId}` → volta para `/mobile/budget?mes=...`
- Nunca fica em loop

### S3 — Scroll funcional (fix B3)
> Como usuário, consigo rolar a tela de metas até o último item sem ela travar no meio.

**Acceptance criteria:**
- Scroll chega até o último card mesmo com muitos grupos
- Sem overflow oculto cortando o conteúdo

### S4 — Mobile formatado (fix B4)
> Como usuário mobile, a tela de ajuste de metas está bem formatada e não tem campos cortados ou sobrepostos.

**Acceptance criteria:**
- Inputs com tamanho adequado para toque
- Sem texto vazando do container
- Keyboard não esconde o botão de salvar

### S5 — Plano com consciência de renda
> Como usuário, quero informar quanto ganho por mês para que o app me ajude a construir um plano realista que conecta gastos e investimentos dentro da minha renda.

**Acceptance criteria:**
- Onboarding de plano pergunta renda média mensal
- Pergunta se há ganhos extraordinários em meses específicos
- Usa gastos dos últimos 3 meses (já no banco) como proposta inicial
- Mostra saldo disponível para investimento = renda - gastos planejados
- Permite declarar gastos excepcionais por mês (campo "gastos sazonais")

### S6 — Gasto parcelado no plano
> Como usuário, quero inserir uma compra parcelada no plano para que o sistema distribua automaticamente o valor em cada mês.

**Acceptance criteria:**
- Checkbox "parcelado" na criação de meta/gasto
- Se marcado: campos "nº de parcelas" e "valor por parcela"
- Seleção do grupo da compra
- Backend cria N registros em `budget_planning`, um por mês, com flag `is_parcela=true` e `parcela_seq`
- Na tela de metas, parcelas são exibidas agrupadas com indicador "(2/12)"

### S7 — Nudge de custo de desvio
> Como usuário, quero saber o quanto gastar R$ 500 a mais por mês custaria no longo prazo para decidir se vale a pena.

**Acceptance criteria:**
- Ao criar/editar meta acima da renda ou do histórico:
  > "Gastar R$ 500 a mais por mês = R$ 180.000 a menos no patrimônio em 30 anos (a juros de 10% a.a.)"
- Nudge de savings: "Guardar R$ 200 a mais por mês = aposentadoria 2,1 anos antes"
- Cálculo usa os parâmetros do plano de aposentadoria já configurado pelo usuário

### S8 — Seletor de mês de início + preview
> Como usuário, quero escolher a partir de qual mês meu plano começa e ver um resumo do que será colocado em cada mês.

**Acceptance criteria:**
- Botão "Começar plano a partir de..." abre date picker (mês/ano)
- Após escolha: tabela de preview com receita, despesa e aporte por mês
- Botão "Confirmar e criar plano" aplica todos os registros

### S9 — Tabela de plano com restrição orçamentária
> Como usuário, quero ver meu plano numa tabela mensal com receita, despesa e aporte esperados, e ser impedido de planejar aportes maiores do que o saldo disponível.

**Acceptance criteria:**
- Tabela: Mês | Receita | Despesa | Aporte | Saldo
- Saldo = Receita - Despesa - Aporte
- Se Saldo < 0 ao tentar salvar → bloqueia com mensagem explicativa
- Aportes menores que o possível → permitido

### S10 — Anos perdidos por excesso de gastos
> Como usuário, quando estou gastando mais do que o plano permite, quero ver quantos anos de aposentadoria estou perdendo.

**Acceptance criteria:**
- Quando total de gastos planejados > renda declarada:
  > "Você está perdendo 3,2 anos de aposentadoria gastando acima do plano"
- Cálculo integrado com parâmetros do plano de aposentadoria

### S11 — Vínculo de transação de investimento ao produto
> Como usuário, quando faço uma transferência para a corretora e subo o extrato, quero poder detalhar em qual(ais) produto(s) aquele dinheiro foi aplicado.

**Acceptance criteria:**
- Após upload, transações com `GRUPO='Investimentos'` geram um badge na tela de Patrimônio: "N aportes aguardando vínculo"
- Modal de vínculo: exibe a transação (valor, data, estabelecimento) e permite adicionar 1 ou mais produtos com valor parcial
- Soma dos produtos vinculados deve igualar o valor total da transação para confirmar
- Ao confirmar: cria `investimentos_transacoes` com `journal_entry_id` linkado
- `investimentos_historico.aporte_mes` do mês é atualizado automaticamente

### S12 — Match automático de produto único
> Como usuário, quando a corretora que recebi o dinheiro corresponde exatamente a um produto do meu portfólio, quero que o vínculo seja sugerido automaticamente.

**Acceptance criteria:**
- Se `portfolio.texto_match` está contido no `Estabelecimento` do journal_entry → exibe sugestão "Parece que é um aporte em [produto]. Confirmar?"
- Um clique confirma; caso contrário, abre o modal completo
- Match case-insensitive e parcial (substring)

### S13 — Rentabilidade real de renda fixa com CDI
> Como usuário com CDB no portfólio, quero ver quanto meu investimento rendeu comparado ao CDI contratado.

**Acceptance criteria:**
- Para produtos `track='fixo'` com `indexador='CDI'` e `taxa_pct`: o app calcula o valor atual usando CDI acumulado real (API Bacen)
- Exibe: valor aplicado, valor atual estimado, rentabilidade % e quanto % do CDI isso representa
- Para liquidez diária (`data_vencimento` NULL): sempre mostra valor atualizado
- Para produtos com vencimento: mostra projeção até o vencimento

### S14 — Posição e custo médio de ações
> Como usuário com ações no portfólio, quero ver minha posição atual, custo médio e rentabilidade.

**Acceptance criteria:**
- Para produtos `track='variavel'`: custo médio ponderado é calculado a partir de todas as transações de compra
- Posição atual = quantidade comprada − quantidade vendida
- Valor atual = posição × preço do dia (atualizado 1x/dia via brapi)
- Exibe: posição, custo médio, valor atual, ganho/perda R$ e %

### S15 — IR estimado no patrimônio
> Como usuário com ações, quero ver uma estimativa do IR sobre ganho de capital para ter uma visão realista do meu patrimônio líquido.

**Acceptance criteria:**
- Linha "IR estimado (ganho de capital)" no resumo do portfólio: `ganho × 15%`
- Linha "Patrimônio líquido após IR estimado": `total_ativos - ir_estimado - passivos`
- Tooltip explicando que é estimativa (não considera isenção de R$20k/mês, day trade, etc.)
- Renda fixa: IR já retido na fonte — não entra no cálculo de IR estimado

---

## 5. Análise Técnica Preliminar

### Bugs (baixo risco)

**B1 — Replicação ao editar:**  
`updateGoal` em `goals-api.ts` não tem o parâmetro `replicarParaAnoTodo`. Precisa replicar a mesma lógica de `createGoal` (loop de meses) mas usando `PUT` / `bulk-upsert` com o ID da meta existente.

**B2 — Círculo vicioso de navegação:**  
`onSubgrupoClick` em `/mobile/budget/[goalId]/page.tsx` faz `router.push('/mobile/transactions?...')`. O botão Voltar em transactions faz `router.back()` → volta para goalId → que mostra o subgrupo novamente. Solução: ao navegar para transactions via subgrupo, passar `?back=/mobile/budget/{goalId}?mes=...` como param e o botão voltar usar esse param em vez de `router.back()`.

**B3 — Scroll:**  
Provável `overflow-hidden` ou `h-screen` no container da lista. Revisão de CSS.

**B4 — Formatação mobile:**  
Revisão de padding/input size na tela `/mobile/budget/edit`.

### Feature: Budget ↔ Patrimônio (mudanças de modelo)

**`investimentos_transacoes` — novos campos (nullable, sem quebrar prod):**
```python
journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
codigo_ativo     = Column(String(20))       # "PETR4" (track variavel)
quantidade       = Column(Numeric(15, 6))   # cotas
preco_unitario   = Column(Numeric(15, 6))   # preço por cota
indexador        = Column(String(20))       # "CDI" | "IPCA" | "SELIC" | "PREFIXADO"
taxa_pct         = Column(Numeric(8, 4))    # 112.0 = 112% CDI
data_vencimento  = Column(Date, nullable=True)  # NULL = liquidez diária
tipo_proventos   = Column(String(30))       # "dividendo" | "jcp" | "rendimento_fii"
ir_retido        = Column(Numeric(15, 2))   # IR retido na fonte (renda fixa)
```

**`investimentos_portfolio` — novos campos:**
```python
track       = Column(String(10), default="snapshot")  # "snapshot" | "fixo" | "variavel"
codigo_ativo = Column(String(20))   # "PETR4" — para match e cotação diária
texto_match  = Column(String(200))  # "XP RENDA FIXA" — detecta no Estabelecimento
```

**Nova tabela `market_data_cache`:**  
Cache de cotações diárias (ações via brapi + CDI/IPCA via BCB). Job roda 1x/dia.

---

## 6. DAG — Ordem de implementação sugerida

```
B3 (scroll)          → independente, 30min
B4 (mobile format)   → independente, 1h
B2 (navegação loop)  → independente, 1-2h
B1 (replicação edit) → independente, 1-2h

S5 (renda: model+API)     → base de S9, S10
S5 (renda: UI onboarding) → depois do model
S6 (parcelas: model+API)  → independente dos outros
S6 (parcelas: UI)         → depois do model
S8 (seletor início + preview) → depois de S5
S9 (tabela + restrição)       → depois de S5
S7 (nudge custo desvio)       → depois de S5
S10 (anos perdidos)           → depois de S5 + integração plano aposentadoria

S11 (vínculo: migration + modal backend)  → depende de migration investimentos_transacoes
S12 (match automático)                    → depende de S11
S13 (CDI renda fixa: job + cálculo)       → depende de S11 + market_data_cache
S14 (posição + custo médio ações)         → depende de S11 + market_data_cache (brapi)
S15 (IR estimado)                         → depende de S14
```

---

## 7. Riscos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Migration de `BudgetPlanning` com campo novo quebra prod | Média | Sempre `nullable=True` em novos campos; migration via alembic no container |
| Cálculo de anos perdidos divergir do plano de aposentadoria | Alta | Extrair lógica de cálculo para lib compartilhada (`features/plano-financeiro/lib/calculator.ts`) |
| Usuário sem dados dos últimos 3 meses | Baixa | Fallback: onboarding manual sem dados históricos |
| `router.back()` em iOS Safari se comporta diferente | Média | Usar `router.push()` com destino explícito em vez de `back()` |
| brapi gratuita (15k req/mês) insuficiente com muitos usuários | Baixa (uso pessoal) | Upgrade para plano Startup R$50/mês se necessário; ou agrupar todos os tickers numa req no plano pago |
| CDI histórico: Bacen limita consultas a 10 anos e exige filtro de datas | Baixa | Sempre buscar com `dataInicial` e `dataFinal`; cache local evita requerimentos repetidos |
| Cotação de ação fora do horário B3 (final de semana) | Baixa | Cache usa último valor disponível; exibe data da última atualização |
| Custo médio incorreto por falta de histórico pré-app | Média | Permitir lançamento manual de transações históricas de compra (tipo='aporte', fonte='manual') |

---

## 8. Métricas de sucesso

- [ ] 0 relatórios de bug de navegação em círculo
- [ ] Replicação de plano funciona em 100% dos testes
- [ ] Taxa de ativação do fluxo de renda ≥ 60% dos novos usuários que criam plano
- [ ] Usuários que usam o nudge têm desvio de plano 20% menor (medir em 60 dias)
- [ ] ≥ 80% dos lançamentos de investimento (GRUPO='Investimentos') têm vínculo criado pelo usuário em até 7 dias
- [ ] Rentabilidade de renda fixa: valor calculado diverge < 0,5% do extrato da corretora (validar manualmente em 3 produtos)
