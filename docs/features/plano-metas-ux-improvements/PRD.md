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

### 2i. Redesign de navegação — bottom nav e atalhos contextuais

O app evoluiu além do que o bottom nav original foi desenhado para suportar. O FAB central "Metas" não reflete mais a ação de maior valor recorrente.

**Problema atual:**
- "Metas" como FAB central → usuário não cria metas diariamente; a ação recorrente é outra
- "Perfil" ocupa uma das 5 slots preciosos → acesso raro (senha, configurações)
- Quick actions estáticas não aproveitam o contexto do estado do app (aportes pendentes, upload atrasado)

**Referência de mercado (padrão observado):**
- Kinvo: FAB = "Novo aporte" | Warren: FAB = "Investir" | Nubank: FAB = "Pix"
- Padrão: FAB central = ação transacional recorrente de maior valor para o produto

**Proposta:**
```
[Início] [Transações] [ ⬆️ ] [Plano] [Carteira]
                       ↑ FAB elevado — Upload de extrato/fatura
```

| Mudança | De | Para | Rationale |
|---------|-----|------|-----------|
| FAB central | "Metas" → `/mobile/budget` | "Upload" → bottom sheet | Upload alimenta budget, plano e investimentos |
| Tab 4 | "Carteira" na 4ª posição | "Plano" na 4ª posição | Plano é o hub cognitivo; Carteira complementa |
| Tab 5 | "Perfil" | "Carteira" | Carteira é mais acessada; Perfil vai para ⚙️ no header |
| Perfil | Tab 5 no bottom nav | ⚙️ no header de Início | Raramente acessado; não merece slot primário |

**Atalhos contextuais (badges inteligentes):**
- `Início`: badge "N aportes aguardando vínculo" → shortcut para Carteira > modal vínculo
- `Início`: badge "Último upload há N dias" (se > 30d) → shortcut para Upload
- `Transações`: ⚠️ em linhas com `GRUPO='Investimentos'` sem vínculo → modal vínculo
- `Carteira`: badge ⚠️ no ícone da tab quando há aportes pendentes

### 2j. Detecção automática de arquivo no upload (Smart Detection)

O upload hoje exige que o usuário preencha banco, tipo e período antes mesmo de escolher o arquivo. O arquivo em si já tem todas essas informações — o processo deve ser invertido.

**Novo fluxo:** usuário dropa o arquivo → backend analisa em < 2s → app exibe card de confirmação com todos os campos detectados → usuário confirma (1 clique) ou edita campos incertos.

**Signals de detecção:**
- Tags do OFX (`BANKID`, `ACCTTYPE`, `DTSTART/DTEND`)
- Padrão do nome do arquivo (`extrato-bradesco-jan-2026.csv`)
- Colunas específicas do CSV por banco (fingerprints por processador)
- Histórico do usuário (banco que ele sempre usa)

**Níveis de confiança:** 🟢 Alta (todos os campos detectados, 1 clique confirma) · 🟡 Média (campos incertos destacados) · 🔴 Baixa (form manual com hints)

**Alerta de duplicata:** se arquivo já foi processado (mesmo banco, mesmo período), avisar antes de confirmar.

### 2k. Upload de múltiplos arquivos simultâneos

O usuário pode querer subir 12 meses de extratos de uma só vez (especialmente na entrada no app). O upload precisa suportar N arquivos, de tipos e bancos diferentes, em uma única operação.

**Ganho principal:** classificação em lote por estabelecimento único. 12 meses → 1.247 transações → 73 estabelecimentos. Classificar 73 = tudo classificado.

**Comportamento esperado:**
- Drop zone aceita múltiplos arquivos
- Cada arquivo é analisado individualmente (smart detection por arquivo)
- Lista de cards com status por arquivo (analisando / pronto / erro / duplicata)
- Processamento em série (não paralelo, para evitar race conditions na DB)
- Tela de conclusão unificada: total de transações + estabelecimentos para classificar

**Tela de classificação em lote:** agrupa por estabelecimento com frequência decrescente. Cada decisão aplica para todas as ocorrências do estabelecimento (em todos os arquivos do lote).

### 2l. Import de dados históricos (planilha própria)

Usuários que já têm anos de dados organizados no Excel/Sheets não deveriam ter que reclassificar tudo. O app precisa aceitar um CSV estruturado onde o grupo já vem preenchido.

**Template CSV com colunas:**
- **Obrigatórias:** `data` (DD/MM/YYYY), `descricao`, `valor` (negativo = gasto)
- **Opcionais:** `grupo`, `conta`, `cartao`

**Diferença no processamento:**
- Pula fases de detecção e parsing (dados já estruturados)
- Valida formato e colunas → preview dos primeiros 5 registros antes de confirmar
- Se `grupo` preenchido e existe → aceita sem classificação
- Se `grupo` preenchido mas não existe → confirma criação de novo grupo com usuário
- Se `grupo` vazio → entra na classificação normal
- Roda deduplicação (IdTransacao gerado normalmente), base_marcacoes, fila de vínculo de investimentos

**UX:** guia passo a passo inline (download template → preencher → upload → validar → confirmar)

### 2m. Jornada do novo usuário (onboarding + empty states)

Um novo usuário que abre o app pela primeira vez não tem dados. A experiência precisa ser: clara (o que o app faz), rápida (como começar) e motivadora (o que ganho ao colocar dados agora).

**3 pontos de entrada:**
1. **Upload de extrato** — detectamos tudo automaticamente (recomendado)
2. **Import de planilha** — já tenho dados organizados
3. **Modo exploração** — ver como funciona com dados de exemplo (banner permanente para converter)

**Bases criadas automaticamente no primeiro login:**
- `base_grupos_config`: 10 grupos padrão (Alimentação, Transporte, Casa, Saúde, Lazer, Educação, Outros, Investimentos, Receita, Transferência)
- `user_financial_profile`: vazio, pronto para receber renda declarada

**Empty states por tela:** cada tela sem dados mostra ilustração + descrição do que aparece ali + CTA para upload ou ação relevante. Não mostrar tela vazia sem direcionamento.

**Checklist de progresso:** card no Início enquanto < 4 itens concluídos (Subiu extrato / Criou Plano / Adicionou investimento / Completou perfil).

**Notificações in-app de ativação:** gatilhos por comportamento (sem upload em 1 dia, upload feito, 30 dias sem atualização, aportes pendentes há 7 dias).

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

### S15 — IR estimado diferenciado por tipo de ativo
> Como usuário com ações e FIIs no portfólio, quero ver uma estimativa de IR que considere as regras corretas de cada tipo para ter uma visão realista do meu patrimônio líquido.

**Acceptance criteria:**
- Ações: aliquota 15% com badge "Isento" quando vendas brutas do mês ≤ R$ 20.000
- FIIs: alíquota 20%, sem possibilidade de isenção
- ETFs e BDRs: alíquota 15%, sem isenção
- Linha "IR estimado" no resumo do portfólio: soma correta por tipo
- Linha "Patrimônio líquido após IR est.": `total_ativos - ir_estimado - passivos`
- Tooltip distingue: "Ações: isento se vendas < R$20k/mês; FIIs: sempre 20%; Renda fixa: IR retido na fonte"
- Renda fixa: exibe alíquota de IR estimada pelo prazo (22,5% a 15%) como informação, não como débito

### S16 — Venda / resgate vinculado ao extrato
> Como usuário que vendeu ações ou resgatou renda fixa e subiu o extrato bancário, quero registrar essa venda no portfólio vinculando ao crédito do extrato.

**Acceptance criteria:**
- Journal_entry com `GRUPO='Investimentos'` e valor positivo (crédito) é exibido como candidato de venda
- Modal de vínculo: permite escolher `tipo_operacao = "Venda/Resgate"` além de "Aporte"
- Para venda de ações: campos quantidade e preço por cota; sistema verifica que posição não fica negativa
- Para resgate de renda fixa: campo valor resgatado + campo IR retido (opcional)
- Após confirmar: `investimentos_transacoes` recebe linha com `tipo_operacao='venda'`; posição atualizada

### S17 — Saldo na corretora como produto do portfólio
> Como usuário que vendeu ativos e deixou o dinheiro na corretora esperando oportunidades, quero ver esse saldo na tela de Carteira como parte do meu patrimônio.

**Acceptance criteria:**
- Ao registrar venda, pergunta: "Para onde foi o dinheiro?" com opções "Conta bancária" e "Ficou na corretora"
- Se "Ficou na corretora": cria produto `track='saldo_corretora'` (ex: "Caixa XP") ou incrementa saldo existente
- Produto aparece na tela de Carteira com tipo "Caixa Corretora" e valor em reais
- Não calcula rentabilidade (saldo à vista) — pode ser vinculado a futuros aportes como origem
- Badge diferente de produtos fixos/variáveis: "💵 Disponível"

### S18 — Indexadores expandidos para renda fixa
> Como usuário com CDB indexado ao IGPM ou LCA pré-fixado, quero escolher o indexador correto para que o app calcule a rentabilidade com precisão.

**Acceptance criteria:**
- Seleção de regime: toggle "Pré-fixado" / "Pós-fixado"
- Se pré-fixado: campo único "Taxa % a.a." — sem indexador
- Se pós-fixado: dropdown com CDI / SELIC / IPCA / IGPM / INCC / IPCA+X + campo taxa %
  - CDI: ex. "112% do CDI"; SELIC: ex. "100% SELIC"; IPCA+X: ex. "IPCA + 6,5% a.a."
- IGPM e INCC consultados via BCB (séries 189 e 192), armazenados em `market_data_cache`
- Cálculo: mesmo padrão de acumulação mensal que IPCA
- Produto exibe qual indexador usa e a rentabilidade % acumulada desde a aplicação

### S19 — Upload como ação primária no FAB central
> Como usuário, quero que o botão central da barra de navegação me leve diretamente ao fluxo de upload de extrato ou fatura, pois essa é a ação que mais impacta todo o app (budget, plano e carteira).

**Acceptance criteria:**
- FAB central exibe ícone de upload (↑) em vez do ícone de alvo (Metas)
- Tap no FAB → abre bottom sheet com duas opções: "📄 Extrato bancário" e "💳 Fatura cartão"
- Após upload e confirmação → retorna ao Início com toast informando resultado: `"N transações processadas · X aportes para vincular"` (se houver investimentos detectados)
- Aba "Plano" (4ª posição) substitui "Metas" → destino: `/mobile/plano` (Acompanhamento ou Construtor)
- Aba "Carteira" ocupa 5ª posição (era "Perfil")
- Perfil acessível via ⚙️ ícone no header de Início
- Badge ⚠️ no ícone da tab Carteira quando há aportes pendentes de vínculo

### S20 — Detecção automática dos metadados do arquivo
> Como usuário, quando subo um arquivo de extrato ou fatura, quero que o app detecte automaticamente o banco, o tipo de conta e o período, sem precisar preencher nada antes de escolher o arquivo.

**Acceptance criteria:**
- Endpoint `POST /upload/detect` recebe o arquivo e retorna `{ banco, tipo, periodo, confianca, transacoes_preview }` em < 2s
- Se confiança ≥ 85%: mostra card pré-preenchido com todos os campos em verde → 1 clique confirma
- Se confiança 50–84%: campos incertos ficam destacados em amarelo com opção de editar
- Se confiança < 50%: exibe form manual com hints baseados no que foi detectado parcialmente
- Se arquivo idêntico a um upload anterior (mesmo banco + período detectado): exibe alerta de duplicata antes de processar
- Detecção funciona para: OFX, CSV dos bancos suportados, XLS (Itaú)

### S21 — Upload de múltiplos arquivos em uma operação
> Como usuário, quero arrastar N arquivos de extratos e faturas de uma só vez, de bancos e tipos diferentes, e ter todos processados em sequência sem precisar repetir o processo para cada um.

**Acceptance criteria:**
- Drop zone aceita múltiplos arquivos em uma operação (drag & drop ou file picker com multi-select)
- Cada arquivo é analisado individualmente pela detecção automática (S20)
- Lista de cards por arquivo com status: analisando / pronto / erro / duplicata
- Arquivos processados em série (não paralelo)
- Tela de conclusão unificada: total de transações processadas, total de estabelecimentos para classificar, aportes para vincular
- Botão "+ Adicionar mais arquivos" disponível durante a análise (antes de processar)

### S22 — Classificação em lote por estabelecimento único
> Como usuário que subiu múltiplos arquivos com centenas de transações, quero classificar por estabelecimento único (não por transação) para que uma decisão se aplique a todas as ocorrências do mesmo estabelecimento.

**Acceptance criteria:**
- Após processar múltiplos arquivos, a tela de classificação agrupa por `Estabelecimento` com frequência e valor total
- Estabelecimentos ordenados por frequência decrescente (mais comum primeiro)
- Ao salvar um grupo para um estabelecimento, todas as transações com aquele estabelecimento recebem o mesmo grupo — inclusive em todos os arquivos do lote
- Estabelecimentos já conhecidos (`base_marcacoes`) aparecem com sugestão automática pré-selecionada (usuário só confirma)
- "Salvar tudo" aplica as sugestões automáticas para todos os estabelecimentos não editados manualmente

### S23 — Import de dados históricos via planilha
> Como usuário que já tem anos de dados organizados no Excel, quero importar meu histórico com os grupos já preenchidos para não precisar reclassificar tudo do zero.

**Acceptance criteria:**
- Novo modo de entrada: "📊 Importar minha planilha" no bottom sheet de Upload
- Template CSV para download (xlsx e csv) com colunas documentadas
- Guia passo a passo inline: baixar template → preencher → subir → validar → confirmar
- Validação pré-import: conta colunas, verifica obrigatórias, detecta linhas inválidas, exibe preview das primeiras 5 linhas
- Linha com `grupo` preenchido e existente → aceita diretamente sem classificação
- Linha com `grupo` preenchido mas inexistente → solicita confirmação de criação de novo grupo
- Linha sem `grupo` → entra na classificação normal por estabelecimento
- Processamento: mesmas fases de deduplicação e base_marcacoes do upload normal; fase 7 (fila de investimentos) aplicada se detectar `GRUPO='Investimentos'`

### S24 — Onboarding: tela de boas-vindas e escolha do ponto de partida
> Como novo usuário, quero entender o que o app faz e escolher como começar (extrato, planilha ou exploração) em no máximo 2 telas, sem ser forçado a seguir um único caminho.

**Acceptance criteria:**
- Tela 1 (Welcome): valor do app em 2 frases + ilustração + [Vamos começar →]
- Tela 2 (Escolha): 3 cards selecionáveis — "Upload extrato", "Import planilha", "Explorar primeiro"
- Cada card leva diretamente para o fluxo correspondente sem etapas extras

### S25 — Bases de grupos criadas automaticamente no primeiro login
> Como novo usuário, quero que o app já tenha grupos padrão criados (Alimentação, Transporte, etc.) quando faço meu primeiro upload, sem precisar criar cada grupo manualmente.

**Acceptance criteria:**
- `base_grupos_config` populado com 10 grupos padrão no momento da criação da conta (trigger backend)
- Os grupos padrão já aparecem disponíveis no seletor de grupo durante a classificação do primeiro upload
- Usuário pode criar grupos adicionais ou editar os nomes dos padrão a qualquer momento

### S26 — Modo exploração com dados de exemplo
> Como potencial usuário que quer entender o app antes de colocar seus dados reais, quero explorar todas as funcionalidades com dados de exemplo, sabendo claramente que são dados fictícios.

**Acceptance criteria:**
- Opção "Explorar primeiro" na tela de escolha carrega dataset de exemplo pré-gerado (persona fictícia com 6 meses de transações)
- Banner fixo em todas as telas: "Modo demonstração — dados fictícios · [Usar meus dados →]"
- Todas as telas funcionam normalmente (dashboard, transações, plano, carteira)
- Ações destrutivas (editar, excluir) mostram aviso de que é dados de exemplo
- "Usar meus dados →" vai para a tela de upload e inicia o onboarding real

### S27 — Empty states com direcionamento claro
> Como novo usuário sem dados, quero que cada tela vazia me diga o que vai aparecer ali e como colocar dados, em vez de mostrar uma tela em branco sem contexto.

**Acceptance criteria:**
- Início vazio: ilustração + "Seu painel financeiro está aqui" + [Subir primeiro extrato] + [Ver demo]
- Transações vazio: ilustração + "Nenhuma transação ainda" + [Subir extrato]
- Plano vazio: ilustração + "Seu plano começa com seus gastos reais" + [Subir extrato primeiro] + [Criar plano manualmente]
- Carteira vazia: ilustração + "Veja seu patrimônio completo" + [Adicionar investimento]
- Nenhum empty state é simplesmente uma lista vazia sem CTA

### S28 — Checklist de primeiros passos no Início
> Como novo usuário, quero ver um progresso visual dos primeiros passos no Início para saber o que falta fazer e sentir que estou avançando.

**Acceptance criteria:**
- Card "Seus primeiros passos" aparece no Início enquanto checklist não estiver 100% completo
- 4 itens: Subiu extrato / Criou Plano / Adicionou investimento / Completou perfil (renda declarada)
- Cada item concluído → check animado (confetti ou pulse)
- Ao completar todos os 4 → card desaparece, substituído pelo resumo normal do mês

### S29 — Notificações in-app de ativação por gatilho
> Como usuário, quero receber mensagens contextuais no app que me lembrem de ações importantes no momento certo (não de forma genérica ou com timing irrelevante).

**Acceptance criteria:**
- Sem upload após 1 dia do cadastro → banner no Início: "Suba seu extrato e veja para onde vai seu dinheiro"
- Primeiro upload concluído → notificação: "Ótimo início! Crie seu Plano para ter um orçamento real"
- Plano criado, sem investimento → banner no Início: "Complete seu patrimônio! Adicione seus investimentos"
- Último upload há > 30 dias → banner no Início: "Hora de atualizar! Suba o extrato de [mês anterior]"
- 3+ aportes pendentes há > 7 dias → banner no Início: "Você tem N aportes para vincular em Carteira"
- Cada banner tem [X Fechar] e [→ Ação] — nunca intrusivo

### 2n. Gestão de contas no app_admin (fonte de criação de usuários)

A criação de contas é responsabilidade exclusiva do `app_admin` — não há auto-cadastro no app principal. O admin precisa de controle total sobre o ciclo de vida de cada conta.

**O que já existe:** criar, editar, desativar (soft delete), resetar senha.

**O que precisa ser adicionado:**

- **Reativar conta:** desfazer um soft delete, restaurando login sem tocar nos dados
- **Purge total:** exclusão irreversível do usuário e de **todos** os seus dados (journal_entries, budget, grupos, investimentos, uploads, marcações, parcelas). Exige confirmação dupla na UI (digitar email do usuário) e header extra no backend
- **Stats de conta:** coluna na listagem mostrando total de transações e data do último upload — contexto essencial antes de excluir
- **Listar inativos:** toggle para exibir contas desativadas na tabela

**Trigger de inicialização:** ao criar um usuário via admin, o backend dispara automaticamente a criação de 10 grupos padrão em `base_grupos_config` e um perfil financeiro vazio em `user_financial_profile` — o usuário já chega no app com tudo pronto para o primeiro upload.

### 2o. Rastreamento de sessão de upload e rollback

Cada upload gera uma **sessão rastreável** (`upload_history_id` + `session_id`) que liga o registro de `upload_history` a todas as entidades criadas durante aquele processo. Se o usuário errou o arquivo, precisa conseguir desfazer o upload específico sem afetar os demais.

**Infraestrutura já existente no banco:**
- `journal_entries.upload_history_id` FK com `cascade="all, delete-orphan"` → deletar `UploadHistory` já apaga as transações em cascata ✅
- `preview_transacoes.session_id` já existe (temporário, limpo após confirmação) ✅

**O que ainda falta rastrear:**
- `base_marcacoes`: adicionar `upload_history_id` nullable → saber quais marcações foram aprendidas por aquele upload (criadas manualmente ficam com `NULL` e nunca são afetadas pelo rollback)
- `base_parcelas`: idem
- `base_expectativas` (Sprint 6): já deve nascer com `upload_history_id` para ser rastreável

**Endpoint de rollback:** `DELETE /upload/{upload_history_id}/rollback`
1. Primeiro retorna prévia do impacto: N transações, N marcações, N parcelas
2. Após confirmação: deleta `base_marcacoes` + `base_parcelas` onde `upload_history_id` = ID; depois deleta `UploadHistory` (cascade limpa `journal_entries`)
3. `UploadHistory` fica com status `revertido` para auditoria — não é removido

**Tela de histórico de uploads** (`/mobile/uploads`): lista todos os uploads com banco, período, data e total de transações. Botão "↩️ Desfazer" em cada linha.

### S30 — Alerta de duplicata de arquivo
> Como usuário, quando subo um arquivo que parece já ter sido carregado antes, quero ser avisado antes de processar para não duplicar meus dados.

**Acceptance criteria:**
- Na fase de detecção (S20), o backend verifica se já existe upload com o mesmo banco + período detectado
- Se sim: exibe modal de aviso com data do upload anterior e número de transações
- Usuário pode cancelar ou confirmar "Carregar de qualquer forma" (deduplicação por IdTransacao evita duplicatas mesmo assim)
- Aviso também aparece se mais de 80% das transações de preview forem idênticas a transações já existentes

### S31 — Desfazer um upload específico (rollback de sessão)
> Como usuário, quando percebo que subi o arquivo errado, quero desfazer aquele upload específico e remover todas as transações que ele gerou, sem afetar os demais uploads.

**Acceptance criteria:**
- Tela de histórico de uploads (`/mobile/uploads`) lista todos: banco, tipo, período, data, total de transações, status
- Botão "↩️ Desfazer" disponível para uploads com status `sucesso`
- Ao clicar: modal de pré-visualização mostra exatamente o que será removido ("N transações, N classificações aprendidas por este upload")
- Após confirmação: transações são removidas; marcações criadas exclusivamente por este upload também; demais uploads não afetados
- Se o upload tiver transações com vínculo de investimento já confirmado: aviso específico + opção de remover o vínculo junto
- `upload_history` não é deletado — fica com status `revertido` para auditoria

### SA1 — Reativar conta de usuário (admin)
> Como admin, quando um usuário foi desativado por engano ou temporariamente, quero reativá-lo sem perder nenhum dado.

**Acceptance criteria:**
- Usuários inativos visíveis ao ativar toggle "Mostrar inativos" na listagem
- Botão "Reativar" visível apenas para usuários com `ativo=0`
- Após reativar: usuário consegue fazer login normalmente; todos os dados preservados
- Sem confirmação obrigatória (operação não destrutiva)

### SA2 — Stats de conta antes de excluir (admin)
> Como admin, antes de excluir permanentemente um usuário, quero ver quantos dados ele tem para tomar uma decisão informada.

**Acceptance criteria:**
- Coluna "Dados" na tabela: `N transações · Último upload: DD/MM/AAAA` (ou "Sem dados")
- Tooltip com detalhes: total uploads, total grupos, tem plano, tem investimentos
- Stats carregadas em paralelo com a lista (não bloqueia a renderização)

### SA3 — Excluir usuário com purge total (admin)
> Como admin, quando um usuário solicita exclusão completa de conta, quero apagar permanentemente todos os dados dele de forma segura e irreversível.

**Acceptance criteria:**
- Botão de exclusão total visualmente distinto do de desativação (vermelho sólido, ícone diferente)
- Etapa 1: exibe resumo de dados do usuário + aviso "ação irreversível e permanente"
- Etapa 2: campo para digitar email exato do usuário — botão só habilita se coincidir
- Backend exige body `{ "confirmacao": "EXCLUIR PERMANENTEMENTE" }` além do token admin
- Após purge: nenhuma tabela do banco contém registros daquele `user_id`
- `user_id=1` nunca pode ser purgado
- Log da operação: quem executou, quando, qual user_id foi purgado

### SA4 — Trigger automático de inicialização ao criar conta
> Como admin, quando crio um novo usuário, quero que o app já esteja pronto para recebê-lo com grupos padrão e perfil vazio.

**Acceptance criteria:**
- `POST /users/` dispara automaticamente criação de 10 grupos padrão em `base_grupos_config` com `is_padrao=True`
- Cria registro vazio em `user_financial_profile`
- Idempotente: se chamado novamente para o mesmo usuário, não duplica
- Novo usuário que faz login cai no onboarding (S24), com grupos já disponíveis para o primeiro upload

### SA5 — Listar usuários inativos no admin
> Como admin, quero ver todos os usuários — ativos e inativos — em uma única tela com controle de filtro.

**Acceptance criteria:**
- Toggle "Mostrar inativos" no header da tabela de contas
- Quando ligado: lista inclui inativos com linha esmaecida e badge "Inativo"
- Quando desligado (default): apenas ativos
- Contagem no header atualiza conforme o filtro

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
S15 (IR estimado diferenciado)            → depende de S14
S16 (venda/resgate vinculado ao extrato)  → depende de S11 + S14 (posição)
S17 (saldo na corretora)                  → depende de S16 (fluxo de venda)
S18 (indexadores IGPM/INCC/pré-fixado)    → depende de S11 + market_data_cache (BCB)

S19 (nav redesign: Upload FAB + Plano + Carteira + ⚙️ Perfil) → independente, pode ir primeiro (só frontend/routing)

S20 (detect endpoint: fingerprints por processador)  → base de S21, S23, S30
S21 (multi-file drop zone + análise por arquivo)      → depende de S20
S22 (classificação em lote por estabelecimento)       → depende de S21 (funciona também com upload simples)
S23 (import planilha: validação + processamento)      → depende de S20 parcialmente (endpoint separado)
S24 (onboarding: welcome + escolha ponto de entrada)  → independente (só frontend)
S25 (grupos padrão no primeiro login)                 → depende de S24 (trigger no create_user)
S26 (modo exploração com dados demo)                  → depende de S24; dados demo pré-gerados
S27 (empty states com CTA)                            → independente (só frontend)
S28 (checklist de primeiros passos)                   → depende de S25 + S27
S29 (notificações in-app por gatilho)                 → depende de S28 (precisa de estado de progresso)
S30 (alerta de duplicata)                             → depende de S20 (detecção já carrega dados do arquivo)
S31 (rollback upload)                                 → depende de migration base_marcacoes.upload_history_id + base_parcelas.upload_history_id

SA1 (reativar conta)         → independente (toggle ativo no backend + frontend)
SA2 (stats de conta)         → independente (query count + max upload_date por user_id)
SA3 (purge total)            → independente; respeitar ordem de FKs no backend
SA4 (trigger inicialização)  → depende de migration is_padrao em base_grupos_config (Sprint 2)
SA5 (listar inativos)        → independente (parâmetro apenas_ativos=false na query)
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
| BCB IGPM/INCC com atraso de publicação (FGV publica no mês seguinte) | Baixa | Cache exibe último valor disponível; nota "Dado referente a MM/AAAA" no card |
| Isenção R$20k: usuário opera em múltiplas corretoras não rastreadas | Média | Tooltip explica limitação: "Estimativa baseada apenas em vendas registradas no app" |
| Saldo na corretora não sincroniza com venda de outro ativo na mesma corretora | Média | Feature de fase 2: link entre saldo_corretora e próximo aporte para fechar o ciclo || brapi: N usuários com os mesmos tickers geram N chamadas repetidas | ✅ Resolvido | Job usa `DISTINCT codigo_ativo` sem `user_id` — 1 chamada por ticker único global; `BRAPI_BATCH_SIZE` controla chunks (1=free, 10=startup, 20=pro) |
| Detecção automática falha para banco não mapeado | Média | Fallback gracioso: exibe form manual com hints; banco desconhecido adiciona fingerprint ao backlog |
| Upload de múltiplos arquivos com arquivo corrompido no lote | Baixa | Arquivo com erro é sinalizado no card individual; resto do lote continua |
| Import de planilha com encoding diferente (Latin-1 vs UTF-8) | Média | Tentar auto-detect de encoding; fallback com mensagem "selecione o encoding" |
| Grupos do import não mapeiam para grupos existentes | Baixa | Exibir preview de grupos desconhecidos com opção "criar" ou "mapear" antes de confirmar |
| Modo demo contamina dados reais (usuário confunde) | Baixa | Dataset de demo isolado por flag `is_demo=True` em journal_entries; import real sempre cria registros novos sem flag |
| Checklist de primeiros passos nunca some (bug de estado) | Baixa | Marcar item como completo via backend + cache invalidation no frontend |
| Admin purga usuário errado (ação irreversível) | Média | Confirmação em 2 etapas: (1) resumo de dados do usuário, (2) digitar email exato; `user_id=1` protegido contra purge; log imutável da operação (quem, quando, qual user_id) |
| Rollback apaga marcação criada manualmente (não pelo upload) | Baixa | `base_marcacoes.upload_history_id IS NULL` = criada manualmente → nunca afetada pelo rollback; preview mostra apenas marcações com FK preenchida |
| Rollback após vínculo de investimento já confirmado | Baixa | Preview detecta vínculos ativos (`investimentos_transacoes` referenciando `journal_entry`); modal avisa explicitamente e oferece "remover vínculo junto" ou "cancelar rollback" |
---

## 8. Métricas de sucesso

- [ ] 0 relatórios de bug de navegação em círculo
- [ ] Replicação de plano funciona em 100% dos testes
- [ ] Taxa de ativação do fluxo de renda ≥ 60% dos novos usuários que criam plano
- [ ] Usuários que usam o nudge têm desvio de plano 20% menor (medir em 60 dias)
- [ ] ≥ 80% dos lançamentos de investimento (GRUPO='Investimentos') têm vínculo criado pelo usuário em até 7 dias
- [ ] Rentabilidade de renda fixa: valor calculado diverge < 0,5% do extrato da corretora (validar manualmente em 3 produtos)
- [ ] Detecção automática: ≥ 80% dos uploads têm confiança Alta (usuário confirma com 1 clique) sem editar campos
- [ ] Multi-file: P90 do tempo de análise de 5 arquivos simultâneos < 10s
- [ ] Import planilha: ≥ 90% das linhas com `grupo` preenchido aceitas sem reclassificação (grupos mapeiam corretamente)
- [ ] Onboarding: ≥ 60% dos novos usuários completam o primeiro upload em < 5 minutos após o cadastro
- [ ] Retenção D7: usuários que completam o checklist de 4 itens têm retenção 30% maior que os que não completam (hipótese a validar)
- [ ] 100% dos usuários criados via admin chegam com grupos padrão e perfil financeiro (zero erros no trigger SA4)
- [ ] Rollback de upload concluído em ≤ 3 cliques com ≤ 5s de processamento
- [ ] Zero registros órfãos (`user_id` referenciado sem `users` pai) após qualquer operação de purge — validar via query de auditoria
