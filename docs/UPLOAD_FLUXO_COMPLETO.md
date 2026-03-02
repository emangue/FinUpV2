# Upload — Fluxo Completo e Todos os Arquivos

> Mapa passo a passo de tudo que acontece quando o usuário faz um upload, incluindo variantes e casos de erro.

---

## Índice

1. [Todos os Arquivos do Upload](#1-todos-os-arquivos-do-upload)
2. [Visão Geral do Pipeline](#2-visão-geral-do-pipeline)
3. [Fase 0 — Detecção](#3-fase-0--detecção)
4. [Fase 1 — Processamento Bruto](#4-fase-1--processamento-bruto)
5. [Fase 2 — Marcação de IDs](#5-fase-2--marcação-de-ids)
6. [Fase 3 — Classificação (Cascata de 5 níveis)](#6-fase-3--classificação-cascata-de-5-níveis)
7. [Fase 4 — Deduplicação](#7-fase-4--deduplicação)
8. [Fase de Preview (Frontend)](#8-fase-de-preview-frontend)
9. [Fase 5 — Confirmação e Pós-Confirmação](#9-fase-5--confirmação-e-pós-confirmação)
10. [Casos Especiais e Erros](#10-casos-especiais-e-erros)
11. [Batch Upload (múltiplos arquivos)](#11-batch-upload-múltiplos-arquivos)
12. [Planilha Genérica (CSV/XLSX sem banco)](#12-planilha-genérica-csvxlsx-sem-banco)
13. [Rollback (desfazer upload)](#13-rollback-desfazer-upload)

---

## 1. Todos os Arquivos do Upload

> A coluna **`[pacote]`** é o nome do arquivo em `docs/upload-package/` — pasta flat com todos os arquivos copiados para consulta externa.

### Backend

| Arquivo original | `[pacote]` | O que faz |
|-----------------|-----------|-----------|
| `domains/upload/router.py` | `backend_upload_ENDPOINTS_router.py` | Todos os endpoints de upload (API) |
| `domains/upload/service.py` | `backend_upload_PIPELINE_service.py` | Orquestração do pipeline (fases 1–6) |
| `domains/upload/models.py` | `backend_upload_MODELO_PreviewTransacao.py` | Modelo da tabela temporária de preview |
| `domains/upload/history_models.py` | `backend_upload_MODELO_UploadHistory.py` | Modelo do histórico de uploads |
| `domains/upload/repository.py` | `backend_upload_QUERIES_repository.py` | Queries SQL isoladas |
| `domains/upload/schemas.py` | `backend_upload_SCHEMAS.py` | Schemas Pydantic de entrada/saída |
| `domains/upload/history_schemas.py` | `backend_upload_SCHEMAS_history.py` | Schemas do histórico |
| `domains/upload/fingerprints.py` | `backend_upload_FASE0_deteccao_fingerprints.py` | **Fase 0:** detecta banco, tipo e período |
| `domains/upload/content_extractor.py` | `backend_upload_content_extractor.py` | Extração de conteúdo bruto de arquivos |
| `processors/marker.py` | `backend_upload_FASE2_ids_marker.py` | **Fase 2:** geração de IDs únicos (FNV-1a, MD5) |
| `processors/classifier.py` | `backend_upload_FASE3_classificacao_classifier.py` | **Fase 3:** cascata de classificação (5 níveis) |
| `processors/generic_rules_classifier.py` | `backend_upload_FASE3_regras_genericas_classifier.py` | **Fase 3 nível 4:** regras hardcoded de texto |
| `processors/pattern_generator.py` | `backend_upload_pattern_generator.py` | Geração de padrões de classificação |
| `processors/raw/registry.py` | `backend_upload_FASE1_registry_processadores.py` | **Fase 1:** mapa (banco, tipo, formato) → processor |
| `processors/raw/base.py` | `backend_upload_FASE1_base_processor.py` | Classe base dos processors |
| `processors/raw/planilha_generica.py` | `backend_upload_FASE1_planilha_generica.py` | **Fase 1:** CSV/XLSX genérico (auto-detecta colunas) |
| `processors/raw/itau_extrato.py` | `backend_upload_FASE1_itau_extrato.py` | **Fase 1:** Itaú extrato (raiz) |
| `processors/raw/itau_fatura.py` | `backend_upload_FASE1_itau_fatura.py` | **Fase 1:** Itaú fatura (raiz) |
| `processors/raw/btg_extrato.py` | `backend_upload_FASE1_btg_extrato.py` | **Fase 1:** BTG extrato (raiz) |
| `processors/raw/csv/itau_fatura.py` | `backend_upload_FASE1_csv_itau_fatura.py` | **Fase 1:** Itaú fatura CSV |
| `processors/raw/excel/btg_extrato.py` | `backend_upload_FASE1_excel_btg_extrato.py` | **Fase 1:** BTG extrato XLSX |
| `processors/raw/excel/btg_fatura_xlsx.py` | `backend_upload_FASE1_excel_btg_fatura.py` | **Fase 1:** BTG fatura XLSX |
| `processors/raw/excel/itau_extrato.py` | `backend_upload_FASE1_excel_itau_extrato.py` | **Fase 1:** Itaú extrato XLSX |
| `processors/raw/excel/mercadopago_extrato.py` | `backend_upload_FASE1_excel_mercadopago_extrato.py` | **Fase 1:** MercadoPago extrato XLSX |
| `processors/raw/pdf/btg_fatura_pdf.py` | `backend_upload_FASE1_pdf_btg_fatura.py` | **Fase 1:** BTG fatura PDF |
| `processors/raw/pdf/itau_extrato_pdf.py` | `backend_upload_FASE1_pdf_itau_extrato.py` | **Fase 1:** Itaú extrato PDF |
| `processors/raw/pdf/itau_fatura_pdf.py` | `backend_upload_FASE1_pdf_itau_fatura.py` | **Fase 1:** Itaú fatura PDF |
| `processors/raw/pdf/mercadopago_extrato_pdf.py` | `backend_upload_FASE1_pdf_mercadopago_extrato.py` | **Fase 1:** MercadoPago extrato PDF |
| `processors/raw/pdf/mercadopago_fatura_pdf.py` | `backend_upload_FASE1_pdf_mercadopago_fatura.py` | **Fase 1:** MercadoPago fatura PDF |
| `domains/classification/router.py` | `backend_classificacao_ENDPOINTS_router.py` | Endpoints de classificação manual e regras |
| `domains/classification/service.py` | `backend_classificacao_SERVICO_regras_texto.py` | GenericClassificationService (regras por texto) |
| `domains/classification/models.py` | `backend_classificacao_MODELO.py` | Modelo GenericClassificationRules |
| `domains/classification/schemas.py` | `backend_classificacao_SCHEMAS.py` | Schemas Pydantic de classificação |
| `domains/compatibility/router.py` | `backend_compatibilidade_ENDPOINTS_router.py` | Endpoints de compatibilidade de bancos |
| `domains/compatibility/service.py` | `backend_compatibilidade_SERVICO_validacao_bancos.py` | Valida bancos e formatos suportados |
| `domains/compatibility/models.py` | `backend_compatibilidade_MODELO.py` | Modelo BankFormatCompatibility |
| `domains/compatibility/repository.py` | `backend_compatibilidade_QUERIES.py` | Queries SQL de compatibilidade |
| `domains/compatibility/schemas.py` | `backend_compatibilidade_SCHEMAS.py` | Schemas Pydantic de compatibilidade |

### Frontend

| Arquivo original | `[pacote]` | O que faz |
|-----------------|-----------|-----------|
| `app/mobile/upload/page.tsx` | `frontend_TELA_upload_page.tsx` | Tela de upload: seleciona banco, arquivo, cartão, período |
| `app/mobile/upload/batch/page.tsx` | `frontend_TELA_upload_batch_page.tsx` | Tela de upload em lote (múltiplos arquivos) |
| `features/upload/services/upload-api.ts` | `frontend_upload_API_chamadas.ts` | Todas as chamadas de API do upload (detect, preview, confirm...) |
| `features/upload/hooks/use-upload.ts` | `frontend_upload_HOOK_use-upload.ts` | Estado do upload (loading, progress, erros) |
| `features/upload/hooks/use-preview-data.ts` | `frontend_upload_HOOK_use-preview-data.ts` | Carrega dados do preview por session_id |
| `features/upload/hooks/use-banks.ts` | `frontend_upload_HOOK_use-banks.ts` | Carrega lista de bancos disponíveis |
| `features/upload/hooks/use-credit-cards.ts` | `frontend_upload_HOOK_use-credit-cards.ts` | Carrega cartões de crédito do usuário |
| `features/upload/components/bank-selector.tsx` | `frontend_upload_COMPONENTE_bank-selector.tsx` | Seletor de banco (dropdown/grid) |
| `features/upload/components/card-selector.tsx` | `frontend_upload_COMPONENTE_card-selector.tsx` | Seletor de cartão de crédito |
| `features/upload/components/format-selector.tsx` | `frontend_upload_COMPONENTE_format-selector.tsx` | Seletor de formato (CSV, XLSX, PDF) |
| `features/upload/components/file-input.tsx` | `frontend_upload_COMPONENTE_file-input.tsx` | Input de arquivo (clique ou drag) |
| `features/upload/components/drop-zone-multi.tsx` | `frontend_upload_COMPONENTE_drop-zone-multi.tsx` | Drop zone para múltiplos arquivos |
| `features/upload/components/file-detection-card.tsx` | `frontend_upload_COMPONENTE_file-detection-card.tsx` | Card com resultado da detecção automática |
| `features/upload/components/month-year-picker.tsx` | `frontend_upload_COMPONENTE_month-year-picker.tsx` | Seletor de mês e ano do extrato |
| `features/upload/components/upload-dialog.tsx` | `frontend_upload_COMPONENTE_upload-dialog.tsx` | Modal de upload |
| `features/upload/components/tab-bar.tsx` | `frontend_upload_COMPONENTE_tab-bar.tsx` | Abas fatura/extrato |
| `features/upload/components/add-group-dialog.tsx` | `frontend_upload_COMPONENTE_add-group-dialog.tsx` | Modal para adicionar grupo na classificação |
| `features/upload/types/preview.types.ts` | `frontend_upload_TIPOS_preview.ts` | Tipos TypeScript do preview |
| `features/preview/templates/PreviewLayout.tsx` | `frontend_TELA_preview_layout.tsx` | Tela completa de preview (layout principal) |
| `features/preview/molecules/ClassificationModal.tsx` | `frontend_preview_MODAL_classificacao.tsx` | Modal de edição de GRUPO/SUBGRUPO de uma transação |
| `features/preview/molecules/BatchClassifyModal.tsx` | `frontend_preview_MODAL_batch_classificacao.tsx` | Modal para classificar várias transações de uma vez |
| `features/preview/molecules/FileInfoCard.tsx` | `frontend_preview_CARD_info_arquivo.tsx` | Card com metadados do arquivo (banco, período, total) |
| `features/preview/molecules/PreviewHeader.tsx` | `frontend_preview_HEADER.tsx` | Cabeçalho do preview com resumo e filtros |
| `features/preview/molecules/TabBar.tsx` | `frontend_preview_TABS.tsx` | Abas: Todas / Classificadas / Não classificadas / Duplicatas / Excluídas |
| `features/preview/organisms/BottomActionBar.tsx` | `frontend_preview_BARRA_acoes.tsx` | Barra inferior: Confirmar / Cancelar / Excluir |
| `features/preview/organisms/TransactionList.tsx` | `frontend_preview_LISTA_transacoes.tsx` | Lista agrupada de transações do preview |
| `features/preview/organisms/TransactionCard.tsx` | `frontend_preview_CARD_transacao.tsx` | Card individual de transação com ações |
| `features/preview/lib/constants.ts` | `frontend_preview_CONSTANTES.ts` | Constantes do preview (cores, labels, etc.) |
| `features/preview/types/index.ts` | `frontend_preview_TIPOS.ts` | Tipos TypeScript do preview |
| `features/banks/services/bank-api.ts` | `frontend_banks_API.ts` | Chamadas de API de bancos e compatibilidade |
| `features/banks/hooks/use-banks.ts` | `frontend_banks_HOOK_use-banks.ts` | Hook para carregar bancos |
| `features/banks/components/banks-table.tsx` | `frontend_banks_COMPONENTE_tabela.tsx` | Tabela de bancos e formatos suportados |
| `features/banks/types/index.ts` | `frontend_banks_TIPOS.ts` | Tipos TypeScript de bancos |

### Scripts de Diagnóstico

```
scripts/diagnostic/
├── test_upload_server.sh              → Health check da API de upload
├── test_upload_pipeline_server.py     → Teste end-to-end do pipeline
└── diagnosticar_base_parcelas_upload.py → Auditoria das parcelas após upload
```

---

## 2. Visão Geral do Pipeline

```
USUÁRIO SELECIONA ARQUIVO
         ↓
[FASE 0] DETECÇÃO (fingerprints.py)
  Detecta banco, tipo, período, duplicata
         ↓
USUÁRIO CONFIRMA BANCO/CARTÃO/PERÍODO/FORMATO
         ↓
USUÁRIO CLICA "ENVIAR"
         ↓
[FASE 1] PROCESSAMENTO BRUTO (processors/raw/*.py)
  Lê CSV/XLSX/PDF → extrai data, estabelecimento, valor
  Aplica regras de exclusão
  Valida saldo (extratos)
         ↓
[FASE 2] MARCAÇÃO DE IDs (marker.py)
  Normaliza nomes de estabelecimentos
  Gera IdTransacao (hash único por transação)
  Gera IdParcela (hash por parcelamento, se houver)
  Define Tipo, Ano, Mês
         ↓
[FASE 3] CLASSIFICAÇÃO — CASCATA DE 5 NÍVEIS (classifier.py)
  1. Base Parcelas (histórico de parcelamentos)
  2. Base Padrões (padrões de classificação salvos)
  3. Histórico de Transações (journal_entries)
  4. Regras Genéricas (banco de regras + hardcoded)
  5. Não classificado (fallback)
         ↓
[FASE 4] DEDUPLICAÇÃO
  Compara IdTransacao com journal_entries existentes
  Marca is_duplicate = true para duplicatas
         ↓
SALVA em preview_transacoes (tabela temporária, session_id)
         ↓
FRONTEND: TELA DE PREVIEW
  Usuário vê transações agrupadas
  Edita classificações manualmente
  Remove transações indesejadas
  Cria regras de exclusão
         ↓
USUÁRIO CLICA "CONFIRMAR"
         ↓
[FASE 5] CONFIRMAÇÃO
  Move preview_transacoes → journal_entries
  Atualiza base_parcelas
  Sincroniza budget_planning
  Cria registro em upload_history
  Limpa preview_transacoes
```

---

## 3. Fase 0 — Detecção

**Arquivo:** `fingerprints.py`
**Endpoint:** `POST /upload/detect`

### O que acontece:

O sistema analisa o arquivo **antes** de fazer o upload completo, usando:
1. Extensão do arquivo (.csv, .xlsx, .xls, .pdf, .ofx)
2. Nome do arquivo (regex para nomes típicos dos bancos)
3. Estrutura do conteúdo (cabeçalhos, palavras-chave internas)

### Saída da detecção:

```
banco:        "nubank" | "itau" | "btg" | "mercadopago" | "bradesco" | "bb" | None
tipo:         "fatura" | "extrato" | "planilha"
confianca:    0.0 a 1.0 (quão certo o sistema está)
periodo_inicio: "01/01/2026"  (data da transação mais antiga detectada)
periodo_fim:    "31/01/2026"  (data da transação mais recente)
mes_fatura:   "202601"  (AAAAMM — usado para checar duplicatas)
arquivo_hash: SHA256 do arquivo (para auditoria)
```

### Verificação de duplicata:

Após detectar `banco + tipo + mes_fatura`, o sistema consulta `upload_history` buscando um upload anterior com:
- Mesmo banco
- Mesmo tipo_documento
- Mesmo mes_fatura
- status = 'success'

**Se encontrar:**
```
duplicata_detectada: {
  upload_id: 123,
  data_importacao: "2026-01-15",
  total_transacoes: 45
}
```

O frontend exibe um **alerta de duplicata**, mas permite que o usuário continue mesmo assim.

### No frontend (upload/page.tsx):

1. Usuário seleciona arquivo → `detectFile(file)` chama `POST /upload/detect`
2. Resultado preenche automaticamente:
   - Banco selecionado (se confiança alta)
   - Período (mês/ano)
3. Se duplicata detectada: exibe banner de aviso amarelo
4. Usuário pode confirmar ou cancelar

---

## 4. Fase 1 — Processamento Bruto

**Arquivos:** `processors/raw/*.py` + `registry.py`

### O que acontece:

O arquivo é lido pelo processor específico do banco e formato. Todos os processors retornam a mesma estrutura (`RawTransaction`), mas a lógica de extração é diferente para cada um.

### Estrutura de saída (RawTransaction):

```
banco:           "nubank"
tipo_documento:  "fatura" | "extrato"
nome_arquivo:    "nubank-fatura-jan-2026.csv"
data:            "15/01/2026"  (DD/MM/YYYY)
lancamento:      "MERCADO PINHEIROS"  (nome do estabelecimento, bruto)
valor:           -89.90  (negativo = débito, positivo = crédito)
nome_cartao:     "Nubank Platinum"  (se fatura de cartão)
final_cartao:    "1234"  (4 últimos dígitos)
mes_fatura:      "202601"  (AAAAMM, só para faturas)
data_criacao:    datetime.now()
```

### Processors por banco:

| Banco | Formatos suportados | Particularidades |
|-------|---------------------|-----------------|
| **Nubank** | CSV (fatura) | Formato simples: date, title, amount |
| **Itaú** | CSV (fatura), XLSX (extrato), PDF (fatura + extrato) | PDF tem OCR. Extrato tem saldo inicial/final |
| **BTG** | XLSX (extrato + fatura), PDF (fatura) | Fatura agrupa por cartão |
| **MercadoPago** | XLSX (extrato), PDF (fatura + extrato) | Subgrupos específicos: "Transferência", "Conta Digital" |
| **Banco do Brasil** | OFX (extrato) | Formato bancário padrão OFX/QIF |
| **Genérico** | CSV, XLSX (qualquer estrutura) | Detecção automática de colunas |

### Regras de Exclusão (aplicadas após extração):

Após extrair as transações, o processor verifica a tabela `TransacaoExclusao`:
- Cada regra tem: `nome_regra`, `banco` (opcional), `tipo_documento` (opcional)
- Se `lancamento` normalizado **contém** `nome_regra` normalizado → transação **removida**
- Escopo: se `banco` e `tipo_documento` forem null → aplica para qualquer arquivo
- Exemplo: regra "SALDO ANTERIOR" → remove linha de saldo do extrato

### Validação de Saldo (apenas extratos):

Para extratos bancários, o processor verifica:
```
saldo_inicial + soma(transações) ≈ saldo_final  (tolerância: R$ 0,01)
```
Resultado salvo em `upload_history.balance_validation` (JSON).
Não bloqueia o upload — apenas registra para auditoria.

### PDFs com senha:

Se o PDF for protegido por senha:
- Processor lança `PasswordRequiredException`
- API retorna HTTP 422 com `code = 'PASSWORD_REQUIRED'`
- Frontend exibe modal "Digite a senha do PDF"
- Usuário digita a senha e o upload é refeito com `senha=` no form data

---

## 5. Fase 2 — Marcação de IDs

**Arquivo:** `processors/marker.py` — classe `TransactionMarker`

### O que acontece:

Cada transação recebe identificadores únicos e estáveis que permitem:
- Detectar duplicatas (mesma transação importada duas vezes)
- Rastrear parcelamentos ao longo do tempo
- Isolar dados entre usuários

### Normalização do estabelecimento:

Antes de gerar IDs, o nome do estabelecimento é normalizado:
- Remove tudo exceto letras (A-Z) e dígitos (0-9)
- Converte para maiúsculas
- Exemplo: `"Mc Donald's #123 - Pinheiros"` → `"MCDONALDS123PINHEIROS"`

Isso garante que o mesmo estabelecimento seja reconhecido independente do formato (PDF vs CSV renderizam textos diferente).

### Detecção de parcelamentos:

O sistema procura padrões como:
- `"LOJA AMERICANAS (3/12)"` → parcela 3 de 12
- `"AMAZON 2/5"` → parcela 2 de 5

Se encontrado, separa:
- `EstabelecimentoBase`: `"LOJAAMERICANAS"` (sem a parte "3/12")
- `parcela_atual`: `3`
- `TotalParcelas`: `12`

### Geração de IdTransacao (FNV-1a 64-bit hash):

```
entrada: data + estabelecimento_normalizado + valor_exato + user_id + sequência

sequência: controla quando o mesmo estabelecimento aparece múltiplas vezes
           no mesmo arquivo (1ª ocorrência = seq 1, 2ª = seq 2, etc.)
```

Este ID é **determinístico**: o mesmo arquivo sempre gera os mesmos IDs. Por isso consegue detectar duplicatas: se importar o mesmo mês duas vezes, os IDs batem.

### Geração de IdParcela (MD5, só para parcelamentos):

```
entrada: estabelecimento_base + valor_parcela + total_parcelas + user_id
```

Todas as parcelas do mesmo parcelamento têm o mesmo `IdParcela`, permitindo rastrear o parcelamento inteiro.

`user_id` está no hash para garantir isolamento: parcelamentos de usuários diferentes nunca colidem.

### Outros campos definidos nesta fase:

```
TipoTransacao:  "Cartão de Crédito" (se tem nome_cartao)
                "Despesas" (se valor < 0)
                "Receitas" (se valor > 0)
Ano:            ano da data (ou do mes_fatura para faturas)
Mes:            mês da data (ou do mes_fatura para faturas)
ValorPositivo:  abs(valor)
```

---

## 6. Fase 3 — Classificação (Cascata de 5 Níveis)

**Arquivo:** `processors/classifier.py` — classe `CascadeClassifier`

### O que acontece:

Para cada transação, o sistema tenta classificar (GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral) percorrendo 5 fontes em ordem de prioridade. Para no primeiro que encontrar resultado.

**Otimização crítica:** Ao iniciar, o `CascadeClassifier` faz **4 queries** no banco e carrega tudo em memória. Depois processa todas as transações **sem novas queries**. Isso evita N+1 queries para arquivos grandes.

### Nível 1 — Base Parcelas (maior prioridade)

**O que é:** Histórico de parcelamentos confirmados anteriormente.

**Como funciona:**
- Busca `IdParcela` da transação na tabela `base_parcelas`
- Se encontrar: usa `grupo_sugerido`, `subgrupo_sugerido`, `tipo_gasto_sugerido` do parcelamento
- Confiança: máxima (o usuário já classificou esse parcelamento antes)

**Quando não usa:** Transação não é parcelada (sem `IdParcela`)

### Nível 2 — Base Padrões

**O que é:** Padrões de classificação gerados e salvos (aprendizado).

**Como funciona:**
- Busca por chave: `"estabelecimento_normalizado [faixa_de_valor]"`
  - Exemplo: `"IFOOD [0-50]"` — iFood com valor entre R$0 e R$50
- Se não encontrar com faixa, tenta só o estabelecimento: `"IFOOD"`
- Só usa padrões com `confianca = "alta"`

### Nível 3 — Histórico de Transações

**O que é:** Transações anteriores do mesmo usuário já classificadas.

**Como funciona:**
- Carrega todas as transações do usuário com classificação completa
- Para cada transação nova: procura por estabelecimentos que compartilhem **tokens** (palavras) com `EstabelecimentoBase`
- Condições adicionais:
  - Deve ter GRUPO + SUBGRUPO + TipoGasto preenchidos
  - Valor deve estar dentro de ±5 (absoluto) ou ±20% (percentual)
  - Transações PIX são ignoradas (muito genéricas)
- Usa a classificação da transação histórica **mais recente** que bater

### Nível 4 — Regras Genéricas

**O que é:** Banco de regras por palavras-chave.

Duas fontes em sequência:

**4a. Banco de dados (`generic_classification_rules`):**
- Cada regra tem: `keywords` (lista de palavras), `grupo`, `subgrupo`, `tipo_gasto`, `prioridade`
- Verifica se qualquer keyword está contida no texto do estabelecimento
- Ordenadas por prioridade (menor número = maior prioridade)

**4b. Regras hardcoded (fallback):**
- PIX → Grupo "PIX / Transferências"
- SUPERMERCADO, MERCADO → Subgrupo "Supermercado"
- COMBUSTIVEL, POSTO → Subgrupo "Combustível"
- FARMACIA, DROGARIA → Subgrupo "Farmácia"
- etc.

**Regras específicas por banco:**
- MercadoPago: "Transferência Recebida" → Subgrupo "Transferência"
- MercadoPago: "Conta Digital" → Subgrupo "Conta Digital"
- Itaú: "Poupança" → Subgrupo "Poupança"

### Nível 5 — Não Classificado (fallback final)

Se nenhum dos 4 níveis acima retornar resultado:
```
GRUPO:       None
SUBGRUPO:    None
TipoGasto:   None
CategoriaGeral: None
origem_classificacao: "Não Classificado"
```

Frontend mostra essas transações na aba "Não classificado" do preview.

### Campo `origem_classificacao` (para debug/transparência):

| Valor | Significa |
|-------|-----------|
| `"parcela"` | Veio do histórico de parcelamentos |
| `"padrao_usuario"` | Veio dos padrões salvos |
| `"historico"` | Veio de transação similar anterior |
| `"regra_generica"` | Veio das regras de texto |
| `"Não Classificado"` | Nenhum nível classificou |

---

## 7. Fase 4 — Deduplicação

**Arquivo:** `service.py` — método `_fase4_deduplication`

### O que acontece:

O sistema verifica quais transações do preview **já existem** em `journal_entries`.

### Como funciona:

1. Coleta todos os `IdTransacao` das transações em preview
2. Faz **1 única query** SQL: `WHERE id_transacao IN (...)`
3. Marca `is_duplicate = True` para os que baterem
4. Salva `duplicate_reason` com detalhes (ex: "Transação já importada em 15/01/2026")

### O que acontece com duplicatas no frontend:

- Aba "Duplicatas" no preview mostra essas transações separadas
- São excluídas automaticamente da confirmação por padrão
- Usuário pode escolher confirmar mesmo assim (caso queira reimportar)

---

## 8. Fase de Preview (Frontend)

**Arquivo:** `features/preview/templates/PreviewLayout.tsx`

### O que o usuário vê:

Tela com todas as transações da sessão de upload, organizadas para revisão.

### Abas de filtro:

| Aba | O que mostra |
|-----|-------------|
| **Todas** | Todas as transações |
| **Classificadas** | Com GRUPO e SUBGRUPO preenchidos |
| **Não classificadas** | Sem classificação |
| **Duplicatas** | `is_duplicate = true` |
| **Excluídas** | `excluir = true` (marcadas para não importar) |

### Agrupamento das transações:

As transações são agrupadas por: `descrição + GRUPO + SUBGRUPO`

Isso permite que o usuário classifique **um grupo inteiro** de uma vez em vez de transação por transação.

### Ações disponíveis:

**Por transação individual:**
- **Editar classificação** → abre `ClassificationModal` (seletor de GRUPO/SUBGRUPO)
- **Marcar para excluir** → toggle `excluir = true` (não importa essa transação)
- **Criar regra de exclusão** → salva em `TransacaoExclusao` para excluir automaticamente em uploads futuros

**Por grupo de transações (BatchClassify):**
- Selecionar todas com o mesmo estabelecimento → abre `BatchClassifyModal`
- Aplica a mesma classificação para todas de uma vez
- Opção: "Salvar como padrão" → cria entrada em `base_padroes` para uploads futuros

**Ações globais (barra inferior):**
- **Confirmar** → vai para a Fase 5
- **Cancelar** → descarta o preview (deleta `preview_transacoes` da sessão)
- **Excluir upload** → cancela e volta para a tela anterior

### Edição de classificação (PATCH):

Cada edição chama `PATCH /upload/preview/{session_id}/{preview_id}` com:
```json
{
  "GRUPO": "Alimentação",
  "SUBGRUPO": "Restaurante",
  "TipoGasto": "Variável",
  "CategoriaGeral": "Despesa",
  "excluir": false
}
```

---

## 9. Fase 5 — Confirmação e Pós-Confirmação

**Endpoint:** `POST /upload/confirm/{session_id}`

### O que acontece em sequência:

#### Passo 1 — Mover preview → journal_entries

Para cada `PreviewTransacao` da sessão onde `excluir = false` e `is_duplicate = false`:
- Cria um `JournalEntry` com todos os campos
- Salva em lote (`db.add_all`)

#### Passo 2 — Atualizar base_parcelas (Fase 5)

Para cada transação parcelada confirmada:
- Se `IdParcela` já existe em `base_parcelas`: incrementa `qtd_pagas`, atualiza status
- Se não existe: cria novo registro com os dados da transação
- Status possíveis: `"provisório"` → `"confirmado"` → `"finalizado"` (quando `qtd_pagas = qtd_parcelas`)

#### Passo 3 — Sincronizar budget_planning (Fase 6)

Para cada grupo que apareceu nas transações confirmadas:
- Verifica se existe `budget_planning` para esse grupo + mês
- Se não existir: cria com `valor_planejado = 0` (grupo sem meta definida)

#### Passo 4 — Criar upload_history

Registra o upload na tabela de histórico:
```
user_id, session_id, banco, tipo_documento, mes_fatura
total_registros: quantidade total extraída na Fase 1
transacoes_importadas: quantidade efetivamente confirmada
transacoes_duplicadas: quantas eram duplicatas
classification_stats: { "classificadas": 40, "nao_classificadas": 5, ... }
balance_validation: { ... }  (extrato só)
status: "success"
data_confirmacao: now()
```

#### Passo 5 — Limpar preview_transacoes

Deleta todas as `PreviewTransacao` da sessão (limpeza do temporário).

---

## 10. Casos Especiais e Erros

### PDF com senha
```
Trigger:    PDF protegido por senha
Erro API:   HTTP 422 { code: "PASSWORD_REQUIRED" }
Frontend:   Exibe modal "Digite a senha do PDF"
Ação:       Usuário digita senha, upload é refeito com campo senha=
```

### Arquivo com formato desconhecido
```
Trigger:    Banco não reconhecido ou formato não suportado
Detecção:   fingerprints.py retorna confianca < threshold
Frontend:   Usuário precisa selecionar banco e formato manualmente
Fallback:   Pode usar "Planilha Genérica" para CSV/XLSX
```

### Duplicata de upload
```
Trigger:    Mesmo banco + tipo + mes_fatura já importado com sucesso
Detecção:   Fase 0 (detecção) verifica upload_history
Frontend:   Banner amarelo de aviso com data do upload anterior
Ação:       Usuário pode cancelar ou continuar mesmo assim
```

### Transações duplicadas (dentro do upload)
```
Trigger:    IdTransacao já existe em journal_entries
Detecção:   Fase 4 (deduplicação)
Marcação:   is_duplicate = true + duplicate_reason
Frontend:   Aba "Duplicatas" no preview, excluídas por padrão da confirmação
```

### Arquivo vazio ou inválido
```
Trigger:    Processor não consegue extrair nenhuma transação
Erro API:   HTTP 400 com mensagem descritiva
Frontend:   Exibe mensagem de erro, usuário tenta novamente
```

### Erro de classificação
```
Trigger:    Nenhum dos 5 níveis classifica a transação
Resultado:  GRUPO = null, origem_classificacao = "Não Classificado"
Frontend:   Transação aparece na aba "Não classificadas"
            Usuário deve classificar manualmente antes de confirmar
```

### Validação de saldo com divergência (extratos)
```
Trigger:    saldo_inicial + soma != saldo_final
Resultado:  balance_validation.is_valid = false
Impacto:    Registrado em upload_history, mas NÃO bloqueia o upload
            É apenas informativo (auditoria)
```

### Erro durante confirmação
```
Trigger:    Falha em qualquer passo da Fase 5 (DB, etc.)
Resultado:  Rollback da transação de banco
            upload_history com status = "error" + error_message
            preview_transacoes permanecem (usuário pode tentar de novo)
```

---

## 11. Batch Upload (múltiplos arquivos)

**Endpoint:** `POST /upload/batch`

### Como funciona:

Permite enviar múltiplos arquivos de uma vez, que são consolidados em uma **única sessão** de preview.

### Fluxo:

```
Arquivo 1 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → salva com session_id XPTO
Arquivo 2 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → salva com MESMO session_id XPTO
...

shared_session_id = XPTO (enviado pelo frontend para todos os arquivos)
```

### Diferença do upload simples:

- Para o arquivo 2 em diante: **não limpa** o `preview_transacoes` existente da sessão (preserva os do arquivo 1)
- Deduplicação verifica tanto `journal_entries` quanto as transações já no preview da sessão
- Frontend exibe tudo junto no preview, agrupado por arquivo

### Confirmação:

Uma única chamada de `POST /upload/confirm/{session_id}` confirma tudo junto.

---

## 12. Planilha Genérica (CSV/XLSX sem banco)

**Endpoint:** `POST /upload/import-planilha`
**Processor:** `processors/raw/planilha_generica.py`

### Para que serve:

Usuário tem uma planilha de qualquer banco ou sistema (inclusive exportações de Excel pessoais) que não tem processor específico.

### Detecção automática de colunas:

O sistema tenta identificar automaticamente quais colunas correspondem a:
- **Data**: busca por "data", "data transação", "dt", "date", "data transacao"
- **Descrição**: busca por "descrição", "lancamento", "histórico", "estabelecimento", "desc"
- **Valor**: busca por "valor", "valor (r$)", "amount", "valor_reais"

A busca é feita removendo acentos e convertendo para minúsculas.

### Formatos de data suportados:

| Formato | Exemplo |
|---------|---------|
| DD/MM/YYYY | 15/01/2026 |
| DD-MM-YYYY | 15-01-2026 |
| YYYY-MM-DD | 2026-01-15 |

Todos são convertidos para DD/MM/YYYY internamente.

### Formatos de valor suportados:

| Formato | Exemplo | Conversão |
|---------|---------|-----------|
| EUA (ponto como decimal) | 49.90 | 49.90 |
| BR (vírgula como decimal) | 49,90 | 49.90 |
| BR com milhar | 1.234,56 | 1234.56 |

### Mapeamento manual (opcional):

Se a detecção automática falhar, o usuário pode passar um mapeamento explícito:
```json
{
  "Data": "coluna_data",
  "Descrição": "coluna_descricao",
  "Valor": "coluna_valor"
}
```

### Saída:

Retorna `{ sessionId, totalRegistros, preview[], colunasMapeadas }` — mesmo fluxo do upload normal a partir daí.

---

## 13. Rollback (desfazer upload)

**Endpoints:**
- `GET /upload/history/{history_id}/rollback-preview` — preview do que será deletado
- `DELETE /upload/history/{history_id}` — deleta o upload e todas as suas transações

### Fluxo de rollback:

```
1. Usuário acessa histórico de uploads
2. Clica em "Desfazer" em um upload
3. Sistema mostra preview: "Serão deletadas X transações de [banco] [mês]"
4. Usuário confirma
5. Sistema deleta:
   - Todas as journal_entries com upload_history_id = history_id
   - O registro em upload_history
6. budget_planning NÃO é revertido (seria muito complexo)
```

### Limitações do rollback:

- Não desfaz classificações aprendidas (base_padroes)
- Não desfaz atualizações em base_parcelas
- Não desfaz a sincronização de budget_planning

---

## Resumo dos Endpoints de Upload

| Endpoint | Método | Fase | O que faz |
|----------|--------|------|-----------|
| `/upload/detect` | POST | 0 | Detecta banco, tipo, período e duplicatas |
| `/upload/preview` | POST | 1-4 | Processa arquivo e salva no preview |
| `/upload/batch` | POST | 1-4 | Múltiplos arquivos em uma sessão |
| `/upload/import-planilha` | POST | 1-4 | Planilha genérica sem banco específico |
| `/upload/preview/{session_id}` | GET | — | Lista transações do preview |
| `/upload/preview/{session_id}/{id}` | PATCH | — | Edita classificação de uma transação |
| `/upload/preview/{session_id}` | DELETE | — | Cancela o preview inteiro |
| `/upload/confirm/{session_id}` | POST | 5-6 | Confirma e importa as transações |
| `/upload/history` | GET | — | Lista histórico de uploads |
| `/upload/history/{id}` | DELETE | — | Deleta upload e suas transações (rollback) |
| `/upload/history/{id}/rollback-preview` | GET | — | Preview do que o rollback vai deletar |
| `/upload/estabelecimentos/sugestoes` | GET | — | Sugestões de GRUPO por estabelecimento |

---

*Para detalhes da tela de upload no frontend, ver: `docs/TELAS_DETALHADAS.md`*
*Para visão arquitetural geral, ver: `docs/VISAO_GERAL_COMPLETA.md`*
