# Plano de Implementação — Plano Financeiro Integrado

**Branch:** `feature/plano-metas-ux-improvements`  
**Data:** 27/02/2026  
**Status:** 🟡 Aguardando execução  
**Referências:** `PRD.md` · `UX_PLANO_FINANCEIRO_INTEGRADO.md` · `02-TECH_SPEC/TECH_SPEC.md`

---

## Visão geral dos sprints

| Sprint | Foco | Tipo | Estimativa |
|--------|------|------|-----------|
| **Sprint 1** | Bugs + Nav redesign + Empty states | 100% Frontend | ~10h |
| **Sprint 2** | Onboarding + Grupos padrão | Backend + Frontend | ~8h |
| **Sprint 3** | Upload inteligente (detecção automática) | Backend + Frontend | ~12h |
| **Sprint 4** | Multi-file + Classificação em lote + Import planilha | Backend + Frontend | ~10h |
| **Sprint 5** | Modo exploração (dados demo) | Backend + Frontend | ~5h |
| **Sprint 6** | Backend do Plano Financeiro (migrations + cashflow) | Backend | ~12h |
| **Sprint 7** | Frontend do Plano Financeiro (wizard + acompanhamento) | Frontend | ~16h |
| **Sprint 8** | Patrimônio — vínculos de aporte + posição + venda | Backend + Frontend | ~14h |
| **Sprint 9** | Patrimônio — cotações diárias + renda fixa + indexadores | Backend + Frontend | ~12h |

**Total estimado:** ~100h  
**Caminho crítico:** Sprint 3 → Sprint 4 → Sprint 6 → Sprint 7 → Sprint 8 → Sprint 9

---

## Sprint 1 — Bugs + Nav Redesign + Empty States

> **Princípio:** tudo independente, zero dependência de banco ou API nova. Entrega visual imediata.

**Referências PRD:** B1, B2, B3, B4, S19, S27  
**Estimativa:** ~10h

### Bugs (começar aqui — mais rápidos, mais motivadores)

- [ ] **B3** — Fix scroll da tela `/mobile/budget`
  - Localizar `overflow-hidden` ou `h-screen` no container da lista de grupos
  - Substituir por `overflow-y-auto` com altura flexível
  - Testar no emulador com 10+ grupos

- [ ] **B4** — Fix formatação mobile em `/mobile/budget/edit`
  - Revisar padding dos inputs (mínimo 44px de altura para toque)
  - Garantir que o botão Salvar não fique escondido pelo teclado virtual
  - Usar `ScrollView` ou `pb-safe` no container principal

- [ ] **B2** — Fix loop de navegação no subgrupo de `/mobile/budget/[goalId]`
  - Em `onSubgrupoClick`, substituir `router.push('/mobile/transactions?...')` por `router.push('/mobile/transactions?...&back=/mobile/budget/[goalId]?mes=...')`
  - Na tela `/mobile/transactions`, ler o param `?back=` e usar como destino do botão Voltar
  - Nunca usar `router.back()` nesse fluxo — sempre destino explícito

- [ ] **B1** — Fix propagação de plano ao editar meta existente
  - Localizar `updateGoal` em `goals-api.ts`
  - Adicionar parâmetro `replicarParaAnoTodo: boolean`
  - Se `true`: loop nos meses restantes do ano fazendo upsert (mesmo padrão do `createGoal`)
  - Retornar contagem de meses atualizados no toast de feedback

### Nav Redesign — S19

- [ ] **S19.1** — Bottom nav: renomear tab 4 de "Carteira" para "Plano", mover "Carteira" para tab 5
  - Atualizar o componente de nav (`app-sidebar.tsx` ou equivalente mobile)
  - Tab 4 → destino `/mobile/plano`
  - Tab 5 → destino `/mobile/carteira`

- [ ] **S19.2** — FAB central: trocar ícone e destino
  - De: ícone de alvo (Metas) → `/mobile/budget`
  - Para: ícone de upload (↑) → abre `UploadBottomSheet`
  - Bottom sheet: dois cards — "📄 Extrato bancário" e "💳 Fatura cartão" (por enquanto ambos vão para o fluxo atual de upload)

- [ ] **S19.3** — Perfil: remover do bottom nav, adicionar ⚙️ no header da tela Início
  - Header do `/mobile/dashboard`: adicionar ícone ⚙️ no canto superior direito → `/mobile/profile`

- [ ] **S19.4** — Badge ⚠️ no ícone da tab Carteira quando há aportes pendentes
  - Por enquanto: badge estático (implementar lógica dinâmica na Sprint 8)
  - Estrutura: wrapper com ponto vermelho condicional via prop `hasPending`

### Empty States — S27

> Componentes visuais puros — sem dados reais, sem endpoints. Só UI.

- [ ] **S27.1** — `EmptyStateDashboard`
  - Ilustração + "Seu painel financeiro está aqui"
  - Dois CTAs: [Subir primeiro extrato] (→ UploadBottomSheet) e [Ver demo] (→ `/mobile/onboarding/demo`)
  - Exibir na tela `/mobile/dashboard` quando `totalTransacoes === 0`

- [ ] **S27.2** — `EmptyStateTransactions`
  - Ilustração + "Nenhuma transação ainda"
  - CTA: [Subir extrato]
  - Exibir em `/mobile/transactions` quando lista vazia E sem filtros ativos

- [ ] **S27.3** — `EmptyStatePlano`
  - Ilustração + "Seu plano começa com seus gastos reais"
  - Dois CTAs: [Subir extrato primeiro] e [Criar plano manualmente]
  - Exibir em `/mobile/plano` quando sem dados de plano

- [ ] **S27.4** — `EmptyStateCarteira`
  - Ilustração + "Veja seu patrimônio completo"
  - CTA: [Adicionar investimento]
  - Exibir em `/mobile/carteira` quando portfólio vazio

---

## Sprint 2 — Onboarding + Grupos Padrão

> **Princípio:** fundar a experiência do novo usuário. Backend simples (hook + migration), frontend de telas estáticas.

**Referências PRD:** S24, S25, S28, S29  
**Estimativa:** ~8h

### Backend — Grupos padrão (S25)

- [ ] **S25.1** — Migration: adicionar campo `is_padrao` (boolean, default false) em `base_grupos_config`
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_is_padrao_base_grupos_config"
  docker exec finup_backend_dev alembic upgrade head
  ```

- [ ] **S25.2** — `UserService._criar_grupos_padrao(user_id)`: inserir os 10 grupos padrão com `is_padrao=True`
  - Grupos: Alimentação (Despesa), Transporte (Despesa), Casa (Despesa), Saúde (Despesa), Lazer (Despesa), Educação (Despesa), Outros (Despesa), Investimentos (Investimento), Receita (Receita), Transferência (Transferência)
  - Chamar dentro de `UserService.create_user()` logo após commit do novo usuário

- [ ] **S25.3** — `GET /onboarding/progress` endpoint
  - Retorna `{ subiu_extrato, criou_plano, adicionou_investimento, perfil_completo, todos_completos }`
  - Consulta: `UploadHistory`, `UserFinancialProfile`, `InvestimentoPortfolio`
  - Registrar em `domains/onboarding/router.py` (criar domínio se não existir)

### Frontend — Telas de onboarding (S24)

- [ ] **S24.1** — Criar rota `/mobile/onboarding/welcome`
  - Componente `OnboardingWelcome`: valor do app em 2 frases + ilustração + botão [Vamos começar →]
  - Botão navega para `/mobile/onboarding/start`

- [ ] **S24.2** — Criar rota `/mobile/onboarding/start`
  - Componente `OnboardingChoosePath`: 3 cards selecionáveis
    - "📄 Upload extrato" → `UploadBottomSheet`
    - "📊 Import planilha" → `/mobile/onboarding/demo` (placeholder por enquanto; será `ImportPlanilhaFlow` na Sprint 4)
    - "🔍 Explorar primeiro" → `POST /onboarding/modo-demo` + redirect `/mobile/dashboard`
  - Cada card: ícone + título + subtítulo de 1 linha

- [ ] **S24.3** — Middleware de redirect
  - Se usuário logado + zero transações + nunca completou onboarding → redirecionar para `/mobile/onboarding/welcome`
  - Implementar em `middleware.ts` ou no layout de `/mobile`
  - Usar flag em `localStorage` ou campo `onboarding_completo` no perfil do usuário

### Frontend — Checklist e notificações (S28, S29)

- [ ] **S28.1** — Componente `OnboardingChecklist`
  - Busca `GET /onboarding/progress`
  - 4 itens visuais com check animado quando completo
  - Card visível no Início enquanto `todos_completos === false`
  - Ao completar todos: card desaparece (animação de saída)

- [ ] **S29.1** — Banners contextuais no Início (notificações in-app)
  - Lógica: verificar estado do progresso + timestamp do último upload
  - Sem upload após cadastro: banner "Suba seu extrato e veja para onde vai seu dinheiro" + [→ Upload]
  - Primeiro upload feito + sem plano: banner "Ótimo início! Crie seu Plano" + [→ /mobile/plano]
  - Último upload há > 30 dias: banner "Hora de atualizar! Suba o extrato de [mês anterior]" + [→ Upload]
  - 3+ aportes pendentes há > 7 dias: banner "Você tem N aportes para vincular em Carteira" + [→ /mobile/carteira]
  - Cada banner tem [X Fechar] — persistir fechamento no `localStorage` por tipo+data

---

## Sprint 3 — Upload Inteligente (Smart Detection)

> **Princípio:** inverter o fluxo de upload. Arquivo primeiro, metadados detectados. Base para tudo que vem depois.

**Referências PRD:** S20, S30  
**Estimativa:** ~12h

### Backend — Migrations

- [ ] **S20.1** — Migration: `upload_history` — adicionar campos `banco`, `tipo`, `periodo_inicio`, `periodo_fim`, `confianca_deteccao` (todos nullable)
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_detection_fields_upload_history"
  docker exec finup_backend_dev alembic upgrade head
  ```

- [ ] **S20.2** — Migration: `journal_entries` — adicionar campo `fonte` (string: `'upload'|'planilha'|'demo'|'manual'`, default `'upload'`) e `is_demo` (boolean, default false)
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_fonte_is_demo_journal_entries"
  docker exec finup_backend_dev alembic upgrade head
  ```

### Backend — DetectionEngine

- [ ] **S20.3** — Criar `app/domains/upload/detectors/fingerprints.py`
  - Mapear cada processador existente em `upload/processors/` para um dict com:
    - `processor_id`, `banco`, `extensoes`, `padroes_nome` (regex), `colunas_csv`, `ofx_tags`
  - Começar pelos processadores com mais usuários (Bradesco, Nubank, Itaú, BTG)
  - Adicionar os demais processadores existentes

- [ ] **S20.4** — Criar `DetectionEngine` em `app/domains/upload/detectors/engine.py`
  - Método `detect(filename: str, file_bytes: bytes) → DetectionResult`
  - Score composto: extensão (10%) + padrão no nome (20%) + colunas CSV (50%) + tags OFX (50%)
  - `DetectionResult`: `{ processor_id, banco, tipo, periodo_inicio, periodo_fim, transacoes_count, confianca: float, campos_incertos: list[str] }`
  - Testar com pelo menos 1 arquivo de cada banco mapeado

- [ ] **S20.5** — Criar `POST /upload/detect` endpoint
  - Recebe arquivo via multipart
  - Chama `DetectionEngine.detect()`
  - Verifica duplicata: consulta `upload_history` com mesmo banco + período → retorna flag `is_duplicata` com dados do upload anterior
  - Não salva nada — só análise
  - Target: retorno em < 2s

- [ ] **S30.1** — Lógica de alerta de duplicata integrada ao `/upload/detect`
  - Verificar `upload_history` por `(user_id, banco, periodo_inicio, periodo_fim)`
  - Se match: retornar `{ is_duplicata: true, upload_anterior: { data, total_transacoes } }`
  - Verificação secundária: se > 80% das transações do preview já existem no banco

### Frontend — Smart upload (S20, S30)

- [ ] **S20.6** — Componente `SmartUploadDropzone`
  - Drop zone (drag & drop + clique) que chama `POST /upload/detect` ao receber arquivo
  - Estado: "solte o arquivo" → "analisando..." → `FileDetectionCard`

- [ ] **S20.7** — Componente `FileDetectionCard`
  - Exibe resultado da detecção: banco, tipo, período, total de transações estimado, badge de confiança (🟢/🟡/🔴)
  - Confiança ≥ 85%: todos os campos em verde, botão [✓ Confirmar] proeminente
  - Confiança 50–84%: campos incertos em amarelo + editáveis inline, botão [Confirmar]
  - Confiança < 50%: abre form manual com hints dos valores detectados parcialmente

- [ ] **S30.2** — Componente `DuplicateAlert`
  - Modal: "Este arquivo parece já ter sido carregado em [data] (N transações)"
  - Dois botões: [Cancelar] e [Carregar de qualquer forma] (deduplicação garante que não duplica)

- [ ] **S20.8** — Integrar `SmartUploadDropzone` no fluxo atual de upload
  - Substituir o form pré-upload pelo novo componente em `/mobile/upload`
  - Garantir fallback: se detecção falha completamente, mostra form manual

---

## Sprint 4 — Multi-file + Classificação em Lote + Import Planilha

> **Princípio:** maximizar o valor do upload. Quem sobe 12 meses de uma vez classifica 73 estabelecimentos, não 1.247 transações.

**Referências PRD:** S21, S22, S23  
**Estimativa:** ~10h

### Backend — Multi-file (S21, S22)

- [ ] **S21.1** — `POST /upload/bulk-confirm` endpoint
  - Recebe lista de `{ arquivo_id, confirmacao_deteccao }` (cada item é o resultado confirmado do `/detect`)
  - Processa em série (não paralelo) usando o processador identificado pelo `processor_id`
  - Retorna `{ total_transacoes, estabelecimentos_unicos, aportes_pendentes }`

- [ ] **S22.1** — `POST /upload/classificar-lote` endpoint
  - Recebe `{ upload_ids: list[int], mapeamentos: [{ estabelecimento, grupo }] }`
  - Aplica cada mapeamento em todas as transações com aquele `Estabelecimento` nos `upload_ids` fornecidos
  - Salva em `base_marcacoes` para aprendizado futuro
  - Retorna contagem de transações atualizadas

### Backend — Import planilha (S23)

- [ ] **S23.1** — Criar `ImportPlanilhaService` em `app/domains/upload/services/import_planilha.py`
  - `validar(file_bytes) → ImportValidacao`: verifica colunas obrigatórias (`data`, `descricao`, `valor`), conta linhas válidas/inválidas, retorna preview das primeiras 5 linhas e lista de grupos desconhecidos
  - `confirmar(validacao_id, mapeamento_grupos) → ImportResultado`: insere transações, roda deduplicação por `IdTransacao`, popula `base_marcacoes`, dispara fase 7 se detectar `GRUPO='Investimentos'`
  - Salvar `fonte='planilha'` em todos os `journal_entries` criados por este fluxo

- [ ] **S23.2** — `POST /upload/import-planilha` endpoint
  - Recebe arquivo (CSV ou XLSX)
  - Chama `ImportPlanilhaService.validar()`
  - Retorna validação + preview; não insere nada

- [ ] **S23.3** — `POST /upload/import-planilha/confirmar` endpoint
  - Recebe `{ validacao_id, mapeamento_grupos: [{ grupo_original, grupo_destino }] }`
  - Chama `ImportPlanilhaService.confirmar()`
  - Retorna resultado com totais

### Frontend — Multi-file (S21, S22)

- [ ] **S21.2** — Atualizar `SmartUploadDropzone` para aceitar múltiplos arquivos
  - Prop `multiple=true` no input/drop
  - Cada arquivo gera um `FileDetectionCard` individual na lista
  - Botão "+ Adicionar mais arquivos" disponível até iniciar processamento
  - Estados globais: "N arquivos prontos para processar" + botão [Processar todos]

- [ ] **S21.3** — Componente `BulkUploadProgress`
  - Lista de arquivos com progresso individual (analisando / pronto / erro / duplicata / processando / concluído)
  - Processamento em série: arquivo 1 → concluído → arquivo 2 → ...

- [ ] **S21.4** — Componente `BulkUploadSummary`
  - Tela de conclusão unificada após processar todos
  - Mostra: total de transações, total de estabelecimentos para classificar, total de aportes para vincular
  - CTA: [Classificar estabelecimentos] (vai para `BatchClassificationView`)

- [ ] **S22.2** — Componente `BatchClassificationView`
  - Lista de estabelecimentos únicos ordenados por frequência decrescente
  - Cada item: nome do estabelecimento + frequência + valor total + dropdown de grupo
  - Estabelecimentos já em `base_marcacoes`: exibem grupo sugerido pré-selecionado
  - Botão [Salvar tudo]: aplica sugestões não editadas + salva edições manuais → chama `/upload/classificar-lote`

### Frontend — Import planilha (S23)

- [ ] **S23.4** — Componente `ImportPlanilhaFlow`
  - Fluxo de 4 passos inline (sem nova tela):
    1. Download do template (link para CSV de exemplo)
    2. Upload do arquivo preenchido
    3. Preview de validação (`ImportValidationPreview`)
    4. Botão Confirmar → chama `/import-planilha/confirmar`

- [ ] **S23.5** — Componente `ImportValidationPreview`
  - Tabela com as primeiras 5 linhas do arquivo
  - Estatísticas: N linhas válidas, N linhas inválidas, N grupos já existentes, N grupos novos
  - Alerta visual se há linhas inválidas (mas não bloqueia — apenas informa)

- [ ] **S23.6** — Componente `GruposDesconhecidosModal`
  - Lista de grupos do arquivo que não existem no banco
  - Para cada um: opção "Criar novo grupo" ou "Mapear para grupo existente" (dropdown)
  - Obrigatório resolver todos antes de confirmar

- [ ] **S23.7** — Atualizar `UploadBottomSheet`
  - Adicionar terceira opção: "📊 Minha planilha" → abre `ImportPlanilhaFlow`
  - Bottom sheet agora tem 3 cards: Extrato bancário / Fatura cartão / Minha planilha

---

## Sprint 5 — Modo Exploração (Dados Demo)

> **Princípio:** o usuário que quer "ver antes de colocar meus dados" precisa de uma experiência completa, não uma tela de boas-vindas.

**Referências PRD:** S26  
**Estimativa:** ~5h

### Backend

- [ ] **S26.1** — Criar dataset fictício de 6 meses (script de geração único)
  - Persona fictícia: "Ana Costa", renda R$ 8.000/mês, gastos reais distribuídos
  - ~150 transações cobrindo: Alimentação, Transporte, Saúde, Lazer, Educação, Investimentos
  - Salvar como seed em `scripts/database/seed_demo_data.py`
  - `fonte='demo'`, `is_demo=True` em todos os `journal_entries`

- [ ] **S26.2** — Criar `DemoDataService`
  - `clonar_para_usuario(user_id)`: copia o dataset demo para o usuário com `is_demo=True`
  - Garantir que budget_planning, investimentos_portfolio e expectativas também tenham dados demo

- [ ] **S26.3** — `POST /onboarding/modo-demo` endpoint
  - Verifica que usuário não tem dados reais (upload real seria contaminado)
  - Chama `DemoDataService.clonar_para_usuario()`

- [ ] **S26.4** — `DELETE /onboarding/modo-demo` endpoint
  - Remove todos os `journal_entries` com `is_demo=True` do usuário
  - Remove dados demo de budget, expectativas, investimentos

### Frontend

- [ ] **S26.5** — Componente `DemoModeBanner`
  - Banner fixo no topo de todas as telas quando `is_demo_mode === true`
  - Texto: "Modo demonstração — dados fictícios"
  - Botão: [Usar meus dados →] → chama `DELETE /onboarding/modo-demo` + redirect para `/mobile/onboarding/start`
  - Não pode ser fechado (só sai usando dados reais)

- [ ] **S26.6** — Rota `/mobile/onboarding/demo`
  - Chama `POST /onboarding/modo-demo`
  - Redireciona para `/mobile/dashboard` com banner ativo
  - Ações destrutivas (editar/excluir) em modo demo: mostrar aviso "Isso é um dado de exemplo"

---

## Sprint 6 — Backend do Plano Financeiro

> **Princípio:** construir o motor antes da interface. O cashflow engine é a peça central que une tudo.

**Referências PRD:** S5, S6, S7, S8, S9, S10 (backend)  
**Referências TECH_SPEC:** M1, M2, P1, P2, P3, C1  
**Estimativa:** ~12h

### Migrations

- [ ] **M1** — Migration `user_financial_profile`
  - Campos: `user_id` (FK unique), `renda_mensal`, `inflacao_pct` (default 5.0), `created_at`, `updated_at`
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_user_financial_profile"
  docker exec finup_backend_dev alembic upgrade head
  ```

- [ ] **M2** — Migration `base_expectativas`
  - Campos: `user_id`, `descricao`, `valor`, `grupo`, `tipo_lancamento`, `mes_referencia`, `is_parcela`, `parcela_seq`, `parcela_total`, `origem` (manual/recorrente/upload), `created_at`
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_base_expectativas"
  docker exec finup_backend_dev alembic upgrade head
  ```

- [ ] **M3** — Migration `budget_planning` — adicionar campos `is_parcela` (bool), `parcela_seq` (int), `parcela_total` (int) — todos nullable
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_parcela_fields_budget_planning"
  docker exec finup_backend_dev alembic upgrade head
  ```

### CRUD de Renda e Expectativas

- [ ] **P1** — `UserFinancialProfile` CRUD
  - `GET /budget/perfil` — retorna perfil ou `null` se não criado ainda
  - `POST /budget/perfil` — cria perfil (onboarding de renda)
  - `PUT /budget/perfil` — atualiza renda ou inflação
  - Ao criar perfil: buscar gastos médios dos últimos 3 meses de `journal_entries` e retornar como `proposta_por_grupo`

- [ ] **P2** — `BaseExpectativas` CRUD
  - `GET /budget/expectativas?mes=YYYY-MM` — retorna expectativas do mês
  - `POST /budget/expectativas` — cria expectativa pontual ou recorrente
  - `POST /budget/expectativas/parcelado` — cria N registros (um por mês) para gasto parcelado
  - `DELETE /budget/expectativas/{id}` — remove uma expectativa

- [ ] **P3** — Fase 6 no `upload/service.py confirm()`
  - Após processar transações, detectar parcelas em `journal_entries` (regex no `Estabelecimento`) e popular `base_expectativas` com as parcelas futuras ainda não processadas
  - Só rodar se `base_expectativas` ainda não tiver registro para o mesmo `descricao` + `mes_referencia`

### Cashflow Engine

- [ ] **C1** — `GET /budget/cashflow?ano=YYYY` endpoint
  - Para cada mês do ano, retornar:
    ```json
    {
      "mes": "2026-03",
      "realizado": { "receita": 8200, "despesa": 6400 },
      "expectativas": { "debitos": 850, "creditos": 0 },
      "plano": { "receita_esperada": 8000, "despesa_planejada": 6000, "aporte_esperado": 2000 },
      "saldo": 800,
      "budget_at_risk": [{ "grupo": "Alimentação", "planejado": 800, "realizado": 950, "desvio_pct": 18.75 }],
      "nudge": { "anos_perdidos": 0.3, "custo_em_30_anos": 18200 }
    }
    ```
  - `realizado`: agrupa `journal_entries` por `Ano+Mes`
  - `expectativas`: agrega `base_expectativas` por `mes_referencia`
  - `plano`: soma de `budget_planning` por `mes_referencia` (com inflação aplicada)
  - `nudge`: usar parâmetros de `InvestimentoCenario` (taxa, anos) para calcular impacto composto do desvio

---

## Sprint 7 — Frontend do Plano Financeiro

> **Princípio:** a interface mais complexa da feature. Montar em ordem de dependência: Acompanhamento (consome cashflow) → Wizard etapa 1 → etapas 2, 3, 4.

**Referências PRD:** S5, S6, S7, S8, S9, S10 (frontend)  
**Referências TECH_SPEC:** F2, F3, F4, F5, F6  
**Estimativa:** ~16h

### Tela de Acompanhamento (`/mobile/plano`)

- [ ] **F2.1** — Tabela mensal de cashflow
  - Consome `GET /budget/cashflow?ano=YYYY`
  - Colunas: Mês | Receita | Despesa | Aporte | Saldo
  - Saldo verde se positivo, vermelho se negativo
  - Botão para navegar entre anos

- [ ] **F2.2** — Budget-at-risk por grupo
  - Cards expansíveis de grupos com desvio > 10%
  - Exibir planejado vs realizado vs desvio %

- [ ] **S10.1** — Banner "Anos perdidos" no Acompanhamento
  - Exibir quando total de gastos > renda declarada no mês atual
  - Texto: "Com esse nível de gasto você está perdendo N anos de aposentadoria"
  - Usar campo `nudge.anos_perdidos` do cashflow response

- [ ] **S8.1** — Seletor de mês de início
  - Botão "Começar plano a partir de..." → date picker (mês/ano)
  - Preview inline da projeção por mês após escolha

### Wizard de Construção do Plano (`/mobile/construir-plano`)

- [ ] **F3** — Etapa 1: Renda e parâmetros
  - Campo "Renda média mensal líquida"
  - Toggle "Tenho meses com ganhos extras" → expansão com campos por mês (13º, bônus, etc.)
  - Campo "Inflação esperada para correção dos gastos" (default 5% a.a.)
  - Chama `POST /budget/perfil`
  - Avança para etapa 2

- [ ] **F4** — Etapa 2: Gastos base
  - Usa `proposta_por_grupo` retornada pelo `POST /budget/perfil` (média dos últimos 3 meses)
  - Lista de grupos com valor sugerido — usuário confirma ou ajusta
  - `S7.1`: ao ajustar um valor acima do histórico, mostrar inline: "Gastar R$ X a mais por mês = R$ Y a menos em 30 anos"
  - Chama `POST /budget/planning` para cada grupo
  - Avança para etapa 3

- [ ] **F5** — Etapa 3: Gastos sazonais por mês
  - Grid de meses (Jan–Dez) com campo "gasto extra esperado"
  - Exemplos sugeridos: IPVA (Jan/Feb), IPTU (Mar), matrícula (Jan/Jul), seguro (qualquer mês)
  - Chama `POST /budget/expectativas` para cada registro
  - Avança para etapa 4

- [ ] **F6** — Etapa 4: Revisão e confirmação
  - Tabela resumo: receita, despesa, aporte disponível por mês
  - `S9.1`: se Saldo < 0 em qualquer mês → bloqueia com mensagem explicativa por mês
  - `S9.2`: se Saldo ≥ 0 → botão [Salvar Plano] (verde, proeminente)
  - Após salvar: redirect para `/mobile/plano` (Acompanhamento)

### Features adicionais

- [ ] **S6.1** — Gasto parcelado no plano (pode ser acessado pela Etapa 3 ou pelo Acompanhamento)
  - Checkbox "Parcelado" em qualquer tela de adicionar gasto
  - Se marcado: campos "Nº de parcelas" e "Valor por parcela"
  - Dropdown de grupo
  - Chama `POST /budget/expectativas/parcelado`
  - Exibe no Acompanhamento com indicador "(2/12)"

---

## Sprint 8 — Patrimônio: Vínculos de Aporte + Posição + Venda

> **Princípio:** fechar o ciclo entre upload e carteira. Uma transação de investimento no extrato deve ter rastro completo até o ativo comprado.

**Referências PRD:** S11, S12, S14, S15, S16, S17  
**Estimativa:** ~14h

### Backend — Migrations

- [ ] **Mig.inv.1** — Migration `investimentos_transacoes` — adicionar campos nullable:
  - `journal_entry_id` (FK → journal_entries.id), `codigo_ativo`, `quantidade`, `preco_unitario`, `indexador`, `taxa_pct`, `data_vencimento`, `tipo_proventos`, `ir_retido`, `tipo_operacao` (`'aporte'|'venda'|'resgate'`), `destino_resgate` (`'conta_bancaria'|'saldo_corretora'`)
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_investimento_transacoes_v2"
  docker exec finup_backend_dev alembic upgrade head
  ```

- [ ] **Mig.inv.2** — Migration `investimentos_portfolio` — adicionar campos nullable:
  - `track` (string: `'snapshot'|'fixo'|'variavel'|'saldo_corretora'`), `subtipo_ativo` (`'acao'|'fii'|'etf'|'bdr'`), `codigo_ativo`, `texto_match`
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_investimento_portfolio_track"
  docker exec finup_backend_dev alembic upgrade head
  ```

### Backend — Serviços

- [ ] **S11.1** — `InvestimentoService.get_aportes_pendentes(user_id)`
  - Busca `journal_entries` com `GRUPO='Investimentos'` sem `investimentos_transacoes.journal_entry_id` correspondente
  - Para cada um: tenta match com `portfolio.texto_match` (substring, case-insensitive)
  - Retorna lista com flag `sugestao_automatica` quando match único

- [ ] **S12.1** — `InvestimentoService.vincular_aporte(journal_entry_id, itens: list)`
  - Valida que soma dos valores dos itens == valor do journal_entry
  - Cria `investimentos_transacoes` para cada item com `tipo_operacao='aporte'`
  - Atualiza `investimentos_historico.aporte_mes` do mês correspondente

- [ ] **S11.2** — `GET /investimentos/pendentes-vinculo` endpoint

- [ ] **S11.3** — `POST /investimentos/vincular-aporte` endpoint

- [ ] **S14.1** — `calc_posicao_variavel(portfolio_id, db)`
  - Custo médio ponderado: soma (qtd × preço) de todas as compras ÷ total de cotas
  - Posição atual: cotas compradas − cotas vendidas
  - Valor atual: posição × preço_atual (de `market_data_cache`)
  - IR: despachar por `subtipo_ativo` → `calcular_ir_variavel(subtipo, lucro, vendas_mes)`
    - Ações: alíquota 15%, isenção se vendas_mes ≤ R$ 20.000
    - FIIs: alíquota 20% sempre
    - ETFs/BDRs: alíquota 15% sem isenção

- [ ] **S15.1** — `GET /investimentos/resumo-ir` endpoint
  - Soma IR estimado de todos os ativos variáveis do usuário
  - Retorna `{ total_bruto, ir_estimado, patrimonio_liquido }`

- [ ] **S16.1** — `InvestimentoService.registrar_venda(journal_entry_id, itens: list)`
  - Valida que posição não fica negativa após venda
  - Cria `investimentos_transacoes` com `tipo_operacao='venda'`
  - Se `destino_resgate='saldo_corretora'`: cria produto `track='saldo_corretora'` ou incrementa existente

- [ ] **S11.4** — Fase 7 no `upload/service.py confirm()`
  - Após processar transações, detectar journal_entries com `GRUPO='Investimentos'`
  - Chamar `get_aportes_pendentes()` para verificar matches automáticos
  - Retornar `{ pendentes_vinculo: N }` no response do confirm

### Frontend

- [ ] **S11.5** — Componente `AportesPendentesBar`
  - Badge amarelo no topo de `/mobile/carteira`: "N aportes aguardando vínculo · [Vincular]"
  - Condicional: aparece quando `pendentes > 0`

- [ ] **S12.2** — Componente `MatchAutomaticoCard`
  - Card especial para quando há sugestão automática (1 match): "Parece que é um aporte em [Produto]. Confirmar?"
  - Dois botões: [✓ Confirmar] (1 clique) e [Editar] (abre modal completo)

- [ ] **S11.6** — Componente `VincularAporteModal`
  - Modal principal de vínculo para quando não há match automático (ou após editar)
  - Lista a transação do extrato (valor, data, estabelecimento)
  - Campos para adicionar 1 ou N produtos com valor parcial cada
  - Validação: soma dos valores deve igualar o total da transação

- [ ] **S14.2** — Componente `PosicaoVariavelCard`
  - Custo médio, preço atual (com data da última atualização), posição em cotas, ganho R$ e %
  - IR estimado por subtipo com badge "Isento" quando aplicável (ações, vendas ≤ R$20k/mês)

- [ ] **S15.2** — Componente `ResumoIRPatrimonio`
  - Linha no topo de Carteira: "Patrimônio bruto: R$ X · IR estimado: R$ Y · **Líquido: R$ Z**"
  - Tooltip: explica diferença entre ações (isenção), FIIs (sempre 20%), renda fixa (retido na fonte)

- [ ] **S16.2** — Modal de venda/resgate vinculado ao extrato
  - Extensão do `VincularAporteModal`: adicionar toggle "Tipo de operação: Aporte / Venda-Resgate"
  - Se Venda: campos quantidade + preço de venda; verificação de posição
  - Se Resgate renda fixa: campo valor resgatado + IR retido
  - Se venda: pergunta "Para onde foi o dinheiro?" — [Conta bancária] ou [Ficou na corretora]

- [ ] **S17.1** — `SaldoCorretoraCard`
  - Card diferente para `track='saldo_corretora'`
  - Badge "💵 Disponível", valor em reais, nome da corretora
  - Sem cálculo de rentabilidade

- [ ] **S19.4** — Ativar badge ⚠️ na tab Carteira
  - Conectar ao `GET /investimentos/pendentes-vinculo`
  - Mostrar ponto vermelho quando `pendentes > 0`

---

## Sprint 9 — Patrimônio: Cotações Diárias + Renda Fixa + Indexadores

> **Princípio:** completar o motor de cálculo de patrimônio. Após esta sprint, a tela Carteira mostra rentabilidade real de todos os tipos de ativo.

**Referências PRD:** S13, S18  
**Estimativa:** ~12h

### Backend — Migration

- [ ] **Mig.market** — Migration `market_data_cache`
  - Campos: `codigo` (ticker ou série BCB), `data`, `valor`, `tipo` (`'acao'|'fii'|'cdi_diario'|'ipca_mensal'|'igpm_mensal'|'incc_mensal'|'selic_diario'`)
  - Constraint unique `(codigo, data)`
  ```bash
  docker exec finup_backend_dev alembic revision --autogenerate -m "add_market_data_cache"
  docker exec finup_backend_dev alembic upgrade head
  ```

### Backend — Job de cotações

- [ ] **S13.1** — Configurar APScheduler no backend
  - Job `sync_market_data` rodando às 18h30 (após fechamento B3)
  - Registrar no startup da aplicação em `main.py`

- [ ] **S13.2** — CDI e SELIC diários (BCB séries 11 e 4389)
  - Buscar série do BCB com `dataInicial` = último registro em cache
  - Inserir novos valores em `market_data_cache` com tipo `'cdi_diario'` e `'selic_diario'`
  - Usar para cálculo de renda fixa pós-fixada

- [ ] **S18.1** — IPCA mensal (BCB série 433)
  - Buscar e inserir mensalmente em `market_data_cache` com tipo `'ipca_mensal'`

- [ ] **S18.2** — IGPM mensal (BCB série 189) e INCC mensal (BCB série 192)
  - Inserir como `'igpm_mensal'` e `'incc_mensal'`
  - Nota: FGV publica com atraso — exibir "Dado referente a MM/AAAA" no card

- [ ] **S14.3** — Ações e FIIs via brapi
  - Buscar `DISTINCT codigo_ativo` de todos os portfólios ativos (sem `user_id` — 1 chamada por ticker)
  - Enviar em chunks de `BRAPI_BATCH_SIZE` (1 no plano free, 10 no Startup)
  - Configurar `BRAPI_TOKEN` no `.env` local e no servidor
  - Inserir preços em `market_data_cache` com tipo `'acao'` ou `'fii'`

### Backend — Cálculos de renda fixa

- [ ] **S13.3** — `calc_valor_fixo(portfolio_id, db)` — track `'fixo'`
  - Regimes suportados:
    - **CDI:** `capital × Π(1 + cdi_dia × taxa_pct/100)` para cada dia desde aplicação
    - **SELIC:** mesmo padrão com série SELIC
    - **IPCA:** `capital × Π(1 + ipca_mes/100)` para cada mês + taxa real
    - **Pré-fixado:** `capital × (1 + taxa_anual/100)^(dias/252)`
  - Retorna: `{ capital, valor_atual, rentabilidade_pct, dias_corridos, aliquota_ir_estimada }`

- [ ] **S18.3** — Suporte a IGPM e INCC no `calc_valor_fixo()`
  - Mesmo padrão de acumulação mensal do IPCA
  - Adicionar ao dropdown de seleção de indexador

- [ ] **S13.4** — `GET /investimentos/posicao/{portfolio_id}` endpoint
  - Despacha por `track`: `calc_posicao_variavel()` (Sprint 8) ou `calc_valor_fixo()` (Sprint 9)
  - Retorna payload unificado com campos opcionais por track

### Frontend

- [ ] **S18.4** — Formulário de produto de renda fixa (sub-form no `VincularAporteModal`)
  - Toggle "Regime": Pré-fixado / Pós-fixado
  - Se Pré-fixado: campo único "Taxa % a.a."
  - Se Pós-fixado: dropdown indexador (CDI / SELIC / IPCA / IGPM / INCC / IPCA+X) + campo "Taxa %"
  - IPCA+X: dois campos (indexador + spread a.a.)
  - Campo "Vencimento" (opcional, data picker — deixar em branco = liquidez diária)

- [ ] **S13.5** — Componente `PosicaoFixoCard`
  - Exibe: regime (pré/pós), indexador, capital aplicado, valor atual estimado
  - Alíquota IR estimada pelo prazo (tabela regressiva: >720d = 15%, 361–720d = 17,5%, 181–360d = 20%, ≤180d = 22,5%)
  - Data da última atualização do indexador

- [ ] **S14.4** — Atualizar `PosicaoVariavelCard` com preço do dia
  - Conectar ao `market_data_cache` via endpoint `/investimentos/posicao/{id}`
  - Exibir "Atualizado em HH:MM de DD/MM"

---

## Checklist de encerramento da feature

### Testes mínimos obrigatórios antes do PR

- [ ] B1-B4: Navegar pelos fluxos de budget sem encontrar nenhum dos 4 bugs
- [ ] S19: Bottom nav com 5 tabs corretas, FAB abre bottom sheet, ⚙️ no header leva para Perfil
- [ ] S20: Subir 1 arquivo OFX e 1 CSV → detecção retorna banco + período corretos
- [ ] S21: Subir 3 arquivos de uma vez → processados em série, sem erros
- [ ] S22: Classificar 2 estabelecimentos em lote → ambas as transações atualizadas
- [ ] S23: Import de CSV com template → preview aparece, confirmar insere transações
- [ ] S24-S25: Novo usuário vê welcome → escolhe upload → grupos padrão já estão disponíveis
- [ ] S26: Ativar modo demo → banner aparece em todas as telas → "Usar meus dados" limpa tudo
- [ ] S27: Cada tela sem dados exibe seu empty state com CTA funcional
- [ ] S28: Checklist no Início atualiza em tempo real ao completar cada item
- [ ] S11-S12: Upload com transação de investimento → badge aparece em Carteira → vínculo criado
- [ ] S13: Produto CDI com 90 dias → valor atual > capital (rentabilidade positiva)
- [ ] S15: Portfólio com FII → IR 20% calculado corretamente no resumo
- [ ] C1: Cashflow de mês passado mostra realizado correto + desvios

### Deploy

- [ ] Todas as migrations aplicadas em produção via `docker exec finup_backend_dev alembic upgrade head`
- [ ] `BRAPI_TOKEN` configurado no servidor
- [ ] Job de cotações ativo (verificar log do APScheduler às 18h30)
- [ ] Smoke test em produção: health check + 1 upload + 1 visualização de carteira
