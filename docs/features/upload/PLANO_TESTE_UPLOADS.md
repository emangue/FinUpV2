# 🧪 Plano de Teste — Processadores de Upload

**Data:** 16/03/2026  
**Escopo:** Todos os arquivos disponíveis em `_arquivos_historicos/_csvs_historico/`  
**Objetivo:** Validar que cada processador extrai transações corretamente, sem perdas silenciosas, sem falsos positivos e com os campos obrigatórios populados.

---

## 📦 Inventário de Arquivos de Teste

### Extrato Itaú — XLS/PDF (`extrato/Itau/`)

| Arquivo | Formato | Período estimado | Observações |
|---------|---------|-----------------|-------------|
| `Extrato Conta Corrente-020320251747.xls` | XLS | Mar/2025 | — |
| `Extrato Conta Corrente-030720252048.xls` | XLS | Jul/2025 | — |
| `Extrato Conta Corrente-190520251719.xls` | XLS | Mai/2025 | — |
| `Extrato Conta Corrente-202503.xls` | XLS | Mar/2025 | Nome alternativo |
| `Extrato Conta Corrente-221220252316.xls` | XLS | Dez/2025 | — |
| `Extrato Conta Corrente-261220251037.xls` | XLS | Dez/2025 | Pode sobrepor c/ anterior |
| `Extrato Conta Corrente-300720252109.xls` | XLS | Jul/2025 | — |
| `Extrato Conta Corrente-301220242137.xls` | XLS | Dez/2024 | — |
| `Extrato Conta Corrente-310120252248.xls` | XLS | Jan/2025 | — |
| `Extrato Conta Corrente-Maio.xls` | XLS | Mai (ano?) | Nome sem ano — verificar |
| `extrato-itau-2025.xls` | XLS | 2025 | Período amplo — verificar |
| `extrato-itau-2025.pdf` | PDF | 2025 | Contraparte PDF do anterior |

**Total:** 11 XLS + 1 PDF = **12 arquivos**

---

### Extrato Mercado Pago — XLSX/PDF (`extrato/MP/`)

| Arquivo | Formato | Período | Observações |
|---------|---------|---------|-------------|
| `MP202501.xlsx` | XLSX | Jan/2025 | — |
| `MP202502.xlsx` | XLSX | Fev/2025 | — |
| `MP202503.xlsx` | XLSX | Mar/2025 | — |
| `MP202504.xlsx` | XLSX | Abr/2025 | — |
| `MP202505.xlsx` | XLSX | Mai/2025 | — |
| `MP202506.xlsx` | XLSX | Jun/2025 | — |
| `MP202507.xlsx` | XLSX | Jul/2025 | — |
| `MP202508.xlsx` | XLSX | Ago/2025 | Par do PDF |
| `MP202509.xlsx` | XLSX | Set/2025 | Par do PDF |
| `MP202510.xlsx` | XLSX | Out/2025 | Par do PDF |
| `MP202511.xlsx` | XLSX | Nov/2025 | Par do PDF |
| `MP202512.xlsx` | XLSX | Dez/2025 | Par do PDF |
| `MP202508.pdf` | PDF | Ago/2025 | — |
| `MP202509.pdf` | PDF | Set/2025 | — |
| `MP202510.pdf` | PDF | Out/2025 | — |
| `MP202511.pdf` | PDF | Nov/2025 | — |
| `MP202512.pdf` | PDF | Dez/2025 | — |
| `account_statement-202ffd51...xlsx` | XLSX | ? | Formato account_statement MP |
| `account_statement-3a5161f1...xlsx` | XLSX | ? | Formato account_statement MP |
| `account_statement-5c113ab1...xlsx` | XLSX | ? | Formato account_statement MP |

**Total:** 12 XLSX mensais + 5 PDF mensais + 3 XLSX account_statement = **20 arquivos**

---

### Extrato BTG — XLS/PDF (`extrato/btg/`)

| Arquivo | Formato | Período | Transações esperadas |
|---------|---------|---------|---------------------|
| `extrato_btg.xls` | XLS | ? | ? (formato antigo, single-page) |
| `Extrato_2025-12-10_a_2026-03-09_11259347605.xls` | XLS | 10/12/2025–09/03/2026 | **65** (verificado) |
| `Extrato_2025-12-10_a_2026-03-09_11259347605.pdf` | PDF | 10/12/2025–09/03/2026 | **65** (verificado) |

**Total:** 2 XLS + 1 PDF = **3 arquivos**

---

### Fatura Itaú — CSV/PDF (`fatura/Itau/`)

| Arquivo | Formato | Período | Observações |
|---------|---------|---------|-------------|
| `fatura_itau-202510.csv` | CSV | Out/2025 | Nome padrão Itaú |
| `fatura_itau-202511.csv` | CSV | Nov/2025 | Nome padrão Itaú |
| `fatura_itau-202512.csv` | CSV | Dez/2025 | Nome padrão Itaú |
| `fatura-202508.csv` | CSV | Ago/2025 | ⚠️ Verificar banco (BTG ou Itaú?) |
| `fatura-202509.csv` | CSV | Set/2025 | ⚠️ Verificar banco (BTG ou Itaú?) |
| `fatura-202601.csv` | CSV | Jan/2026 | ⚠️ Verificar banco |
| `fatura-202509.pdf` | PDF | Set/2025 | — |
| `fatura-202510.pdf` | PDF | Out/2025 | — |
| `fatura-202511.pdf` | PDF | Nov/2025 | — |
| `fatura-202512.pdf` | PDF | Dez/2025 | — |

**Total:** 6 CSV + 4 PDF = **10 arquivos**

---

### Fatura Mercado Pago — PDF (`fatura/MP/`)

| Arquivo | Formato | Período |
|---------|---------|---------|
| `FATURAMP202507.pdf` | PDF | Jul/2025 |
| `FATURAMP202508.pdf` | PDF | Ago/2025 |
| `FATURAMP202509.pdf` | PDF | Set/2025 |
| `FATURAMP202510.pdf` | PDF | Out/2025 |
| `FATURAMP202511.pdf` | PDF | Nov/2025 |
| `FATURAMP202512.pdf` | PDF | Dez/2025 |
| `FATURAMP202601.pdf` | PDF | Jan/2026 |
| `FATURAMP202602.pdf` | PDF | Fev/2026 |

**Total:** **8 arquivos**

---

### Fatura BTG — PDF/XLSX (`fatura/btg/`)

| Arquivo | Formato | Período | Transações esperadas |
|---------|---------|---------|---------------------|
| `2026-02-01_Fatura_...BTG.xlsx` | XLSX | Fev/2026 | ? |
| `2026-02-01_Fatura_...BTG.pdf` | PDF | Fev/2026 | ? |
| `2026-03-01_Fatura_...BTG.xlsx` | XLSX | Mar/2026 | ? |
| `2026-03-01_Fatura_...BTG.pdf` | PDF | Mar/2026 | ? |

**Total:** 2 XLSX + 2 PDF = **4 arquivos**

---

## 📊 Matriz de Cobertura de Processadores

| Banco | Tipo | Formato | Processador registrado | Status | Arquivos de teste |
|-------|------|---------|----------------------|--------|-------------------|
| Itaú | extrato | excel | `process_itau_extrato` | ✅ OK | 11 XLS |
| Itaú | extrato | pdf | `process_itau_extrato_pdf` | ✅ OK | 1 PDF |
| Itaú | fatura | csv | `csv_itau_fatura` | ✅ OK | 3 CSV (padrão) |
| Itaú | fatura | pdf | `process_itau_fatura_pdf` | ✅ OK | 4 PDF |
| BTG | extrato | excel | `process_btg_extrato` | ⚠️ BUGS | 2 XLS |
| BTG | extrato | pdf | `process_btg_extrato_pdf` | 🆕 NOVO | 1 PDF |
| BTG | fatura | excel | `process_btg_fatura_xlsx` | ✅ OK | 2 XLSX |
| BTG | fatura | pdf | `process_btg_fatura_pdf` | ✅ OK | 2 PDF |
| Mercado Pago | extrato | excel | `process_mercadopago_extrato` | ✅ OK | 15 XLSX |
| Mercado Pago | extrato | pdf | `process_mercadopago_extrato_pdf` | ✅ OK | 5 PDF |
| Mercado Pago | fatura | pdf | `process_mercadopago_fatura_pdf` | ✅ OK | 8 PDF |
| Itaú / BTG? | fatura | csv | ❓ **SEM PROCESSADOR?** | ❌ LACUNA | 3 CSV (nome genérico) |

---

## 🐛 Bugs Conhecidos a Reproduzir

### BTG Extrato XLS — 3 bugs documentados

> **Referência:** [docs/features/upload-btg-extrato/DIAGNOSTICO_BTG_EXTRATO_XLS.md](../upload-btg-extrato/DIAGNOSTICO_BTG_EXTRATO_XLS.md)

| ID | Severidade | Descrição | Arquivo afetado |
|----|-----------|-----------|-----------------|
| P1 | 🔴 CRÍTICO | Filtro `str.contains('nan')` descarta transações de "Crédito e Financiamento" | `Extrato_..._11259347605.xls` |
| P2 | 🟡 MÉDIO | Estrutura multi-página tratada de forma frágil (sem parse explícito por bloco) | `Extrato_..._11259347605.xls` |
| P3 | 🟢 BAIXO | Campo `Transação` (col D) ignorado no lançamento | todos XLS BTG extrato |

**Impacto P1:** 3 transações perdidas no total de -R$ 28.444,04.

---

## 🧪 Casos de Teste por Processador

### TC-01: Itaú Extrato XLS

**Processador:** `process_itau_extrato`  
**Arquivos:** todos os 11 XLS em `extrato/Itau/`

**Critérios de aceite:**
- [ ] `n_transacoes > 0` em todos os arquivos
- [ ] Nenhuma exceção/crash
- [ ] `data` no formato `DD/MM/YYYY` em todos os registros
- [ ] `valor != 0.0` em todos os registros
- [ ] `lancamento` não vazio e não contém lixo de cabeçalho (ex: "SALDO ANTERIOR", "Agência/Conta")
- [ ] Saldo final declarado no arquivo (se houver) bate com soma das transações (tolerância ±R$ 0,01)

**Sinais de problema:**
- `n_transacoes == 0` → processador não reconheceu o formato
- `lancamento` com "SALDO ANTERIOR", "SALDO", "Data" → cabeçalho vazando para dados
- `valor == None` → campo não mapeado

---

### TC-02: Itaú Extrato PDF

**Processador:** `process_itau_extrato_pdf`  
**Arquivo:** `extrato-itau-2025.pdf`

**Critérios de aceite:**
- [ ] `n_transacoes > 0`
- [ ] `BalanceValidation.is_valid == True` (saldo conferido pelo processador)
- [ ] `data` no formato `DD/MM/YYYY`
- [ ] `lancamento` não contém linhas de cabeçalho PDF ("Extrato", "Agência", "CPF")

**⚠️ Verificar:** Se `extrato-itau-2025.xls` e `extrato-itau-2025.pdf` têm o mesmo período, comparar `n_transacoes` entre os dois e soma de valores.

---

### TC-03: Itaú Fatura CSV (padrão)

**Processador:** `csv_itau_fatura`  
**Arquivos:** `fatura_itau-202510.csv`, `fatura_itau-202511.csv`, `fatura_itau-202512.csv`

**Critérios de aceite:**
- [ ] `n_transacoes > 0`
- [ ] `mes_fatura` no formato `YYYYMM` e correto para o arquivo
- [ ] `nome_cartao` e/ou `final_cartao` populados (se constam no CSV)
- [ ] Nenhuma linha de cabeçalho/totais como transação ("Total da Fatura", "Vencimento")

---

### TC-04: Itaú Fatura CSV (nome genérico — ⚠️ investigar)

**Arquivos:** `fatura-202508.csv`, `fatura-202509.csv`, `fatura-202601.csv`  
**Processador esperado:** desconhecido (depende do banco detectado)

**Ação antes do teste:**
1. Abrir cada arquivo e verificar o banco (Itaú ou BTG?)
2. Confirmar se a detecção por fingerprint (`fingerprints.py`) retorna o banco correto
3. Se for BTG fatura CSV → **não existe processador** (lacuna!)

**Critérios de aceite:**
- [ ] `DetectionEngine.detect()` retorna `confianca >= 0.8` e banco correto
- [ ] Processador processa sem erro
- [ ] `n_transacoes > 0`

---

### TC-05: Itaú Fatura PDF

**Processador:** `process_itau_fatura_pdf`  
**Arquivos:** `fatura-202509.pdf`, `fatura-202510.pdf`, `fatura-202511.pdf`, `fatura-202512.pdf`

**Critérios de aceite:**
- [ ] `n_transacoes > 0`
- [ ] `mes_fatura` correto para o arquivo
- [ ] `lancamento` contém nome do estabelecimento (não "Lançamento", "Valor")
- [ ] Parcelas no formato `XX/YY` detectadas corretamente no `lancamento`

---

### TC-06: BTG Extrato XLS (BUG P1 — reproduzir e corrigir)

**Processador:** `process_btg_extrato`  
**Arquivo principal:** `Extrato_2025-12-10_a_2026-03-09_11259347605.xls`

**Critérios de aceite (pós-correção P1):**
- [ ] `n_transacoes == 65` (atualmente retorna 62 — perda silenciosa)
- [ ] 3 transações com `lancamento` contendo "Crédito e Financiamento"
- [ ] Valores das 3 transações: `-17.064,96`, `-11.348,77`, `-31,31`
- [ ] Sem exceção

**Arquivo secundário:** `extrato_btg.xls`  
- [ ] `n_transacoes > 0` (formato antigo single-page)

---

### TC-07: BTG Extrato PDF (processador novo)

**Processador:** `process_btg_extrato_pdf`  
**Arquivo:** `Extrato_2025-12-10_a_2026-03-09_11259347605.pdf`

**Critérios de aceite:**
- [ ] `n_transacoes == 65`
- [ ] Saldo total = **R$ 97,02**
- [ ] 3 transações de "Crédito e Financiamento" com valores corretos
- [ ] Nenhuma linha de metadado (Cliente:, CPF:, Agência:) convertida em transação
- [ ] **Comparar com TC-06 XLS:** `n_transacoes` igual, saldo idêntico

---

### TC-08: BTG Fatura XLSX

**Processador:** `process_btg_fatura_xlsx`  
**Arquivos:** `2026-02-01_...BTG.xlsx`, `2026-03-01_...BTG.xlsx`

**Critérios de aceite:**
- [ ] `n_transacoes > 0`
- [ ] `mes_fatura` populado e correto (`202602`, `202603`)
- [ ] `nome_cartao` populado
- [ ] Nenhuma linha de totais/parcelas como transação

---

### TC-09: BTG Fatura PDF

**Processador:** `process_btg_fatura_pdf`  
**Arquivos:** `2026-02-01_...BTG.pdf`, `2026-03-01_...BTG.pdf`

**Critérios de aceite:**
- [ ] `n_transacoes > 0`
- [ ] `mes_fatura` correto
- [ ] **Comparar com TC-08 XLSX mesmo mês:** `n_transacoes` igual (mesmo dado, formatos diferentes)
- [ ] Saldo idêntico entre PDF e XLSX do mesmo mês (tolerância ±R$ 0,01)

---

### TC-10: Mercado Pago Extrato XLSX (mensal)

**Processador:** `process_mercadopago_extrato`  
**Arquivos:** `MP202501.xlsx` a `MP202512.xlsx` (12 arquivos)

**Critérios de aceite:**
- [ ] `n_transacoes > 0` em todos
- [ ] `data` no formato `DD/MM/YYYY`
- [ ] `lancamento` não contém colunas header do XLSX (`INITIAL_BALANCE`, `RELEASE_DATE`)
- [ ] Transações de saldo inicial/final filtradas (não devem aparecer como transação)
- [ ] Para meses com par PDF (Ago–Dez), comparar `n_transacoes` e saldo

---

### TC-11: Mercado Pago Extrato XLSX (account_statement)

**Processador:** `process_mercadopago_extrato`  
**Arquivos:** 3 XLSX com UUID no nome

**⚠️ Verificar:** o fingerprint detecta estes arquivos como Mercado Pago? O campo `INITIAL_BALANCE` está presente?

**Critérios de aceite:**
- [ ] `DetectionEngine.detect()` retorna `banco == 'mercadopago'`, `tipo == 'extrato'`
- [ ] `n_transacoes > 0`
- [ ] `lancamento` legível (não código interno)

---

### TC-12: Mercado Pago Extrato PDF

**Processador:** `process_mercadopago_extrato_pdf` (com `BalanceValidation`)  
**Arquivos:** `MP202508.pdf` a `MP202512.pdf` (5 arquivos)

**Critérios de aceite:**
- [ ] `n_transacoes > 0`
- [ ] `BalanceValidation.is_valid == True` (ou `None` se PDF não declara saldo)
- [ ] Para meses com par XLSX: `n_transacoes` igual, saldo idêntico

---

### TC-13: Mercado Pago Fatura PDF

**Processador:** `process_mercadopago_fatura_pdf`  
**Arquivos:** `FATURAMP202507.pdf` a `FATURAMP202602.pdf` (8 arquivos)

**Critérios de aceite:**
- [ ] `n_transacoes > 0` em todos
- [ ] `mes_fatura` populado e correto
- [ ] `lancamento` contém nome do estabelecimento
- [ ] Sem linhas de totais/cabeçalho como transação

---

## 🔍 Lacunas Identificadas

### Lacuna L1 — Fatura CSV genérica (`fatura-YYYYMM.csv`)

Existem 3 arquivos CSV de fatura sem prefixo de banco no nome. Verificar manualmente o conteúdo de cada um para determinar se são Itaú ou BTG. Se forem BTG, **não existe processador para fatura BTG CSV** — será necessário criar.

**Ação:** Abrir e inspecionar cabeçalho dos 3 arquivos antes de executar os testes.

### Lacuna L2 — Mercado Pago Fatura XLSX

Não há arquivos de fatura MP em formato XLSX no diretório. Confirmar se existe/existirá este formato, e se o processador `process_mercadopago_fatura_pdf` também precisará de variante XLSX.

### Lacuna L3 — Itaú Extrato PDF (arquivo único)

Apenas 1 arquivo PDF de extrato Itaú disponível. Para testes mais robustos, idealmente seriam 3+. Considerar obter mais arquivos de exemplo.

---

## 🤖 Script de Teste Automatizado

Execute via:

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
source app_dev/venv/bin/activate
python scripts/testing/test_upload_processors.py
```

O script realiza:
1. **Detecção automática** — chama `DetectionEngine.detect()` em cada arquivo, reporta banco/tipo/confiança
2. **Processamento** — invoca o processador mapeado no registry
3. **Validações básicas** — n_transacoes > 0, campos obrigatórios, sem crash
4. **Comparação XLS×PDF** — para arquivos com par XLSX/PDF do mesmo período
5. **Relatório final** — tabela de PASS/FAIL por arquivo

---

## 📋 Checklist de Execução Manual (UI)

Após os testes automatizados, realizar testes via interface web:

### Pré-condição
- [ ] Docker em execução: `./scripts/deploy/quick_start_docker.sh`
- [ ] Login como admin: `admin@financas.com`

### Roteiro de Upload

Para cada banco/tipo, realizar ao menos 1 upload pela UI em http://localhost:3000:

- [ ] **Itaú Extrato XLS** — `Extrato Conta Corrente-202503.xls`
  - Confirmar: banco "Itaú", tipo "Extrato", período detectado correto
  - Confirmar: transações aparecem na tela de transações
  - Confirmar: re-upload do mesmo arquivo → "já importado" (deduplicação)

- [ ] **Itaú Fatura CSV** — `fatura_itau-202512.csv`
  - Confirmar: mes_fatura = 202512

- [ ] **Itaú Fatura PDF** — `fatura-202512.pdf`
  - Comparar: mesmo número de transações que o CSV de dezembro

- [ ] **BTG Extrato XLS** — `Extrato_2025-12-10_a_2026-03-09_11259347605.xls`
  - Confirmar: **65 transações** (não 62!)
  - Confirmar: 3 transações de "Crédito e Financiamento" visíveis

- [ ] **BTG Extrato PDF** — `Extrato_2025-12-10_a_2026-03-09_11259347605.pdf`
  - Após upload do XLS acima, tentar PDF do mesmo período → **deve detectar duplicatas**

- [ ] **BTG Fatura XLSX** — `2026-03-01_Fatura_...BTG.xlsx`
  - Confirmar: mes_fatura = 202603

- [ ] **BTG Fatura PDF** — `2026-03-01_Fatura_...BTG.pdf`
  - Após upload do XLSX, tentar PDF → **deve detectar duplicatas**

- [ ] **Mercado Pago Extrato XLSX** — `MP202512.xlsx`
  - Confirmar: banco "Mercado Pago", tipo "Extrato"

- [ ] **Mercado Pago Extrato PDF** — `MP202512.pdf`
  - Comparar: mesmo número de transações que MP202512.xlsx

- [ ] **Mercado Pago Fatura PDF** — `FATURAMP202512.pdf`
  - Confirmar: mes_fatura = 202512, transações visíveis

---

## 📊 Critérios Globais de Aprovação

| Critério | Meta |
|---------|------|
| Arquivos sem crash | 100% |
| Arquivos com `n_transacoes > 0` | 100% (exceto arquivos em branco) |
| Detecção de banco/tipo com confiança ≥ 0.8 | ≥ 95% |
| Pares XLS/PDF com `n_transacoes` igual | 100% |
| BTG Extrato XLS — 65 transações | ✅ obrigatório |
| BTG Extrato XLS — 3 transações Financiamento | ✅ obrigatório |
| Deduplicação funcional (re-upload detectado) | ✅ obrigatório |

---

## 🗺️ Ordem de Execução Recomendada

```
1. Inspecionar CSVs genéricos (TC-04)         → 10 min  (determinar banco)
2. Rodar script automatizado completo         → 20 min  (smoke test geral)
3. Focar bugs BTG Extrato XLS (TC-06)         → verificar P1/P2/P3
4. Focar BTG Extrato PDF (TC-07)              → validar processador novo
5. Comparar pares XLS↔PDF mesmo período      → BTG, MP Ago-Dez
6. Testes manuais pela UI (10 roteiros)       → 30 min
7. Documentar resultados na tabela abaixo     → 15 min
```

---

## 📝 Tabela de Resultados (preencher durante execução)

| TC | Arquivo | Banco detectado | n_tx | Saldo | Status | Observações |
|----|---------|----------------|------|-------|--------|-------------|
| TC-01 | `Extrato CC-202503.xls` | | | | | |
| TC-01 | `Extrato CC-310120252248.xls` | | | | | |
| TC-01 | `Extrato CC-301220242137.xls` | | | | | |
| TC-01 | `Extrato CC-221220252316.xls` | | | | | |
| TC-01 | `Extrato CC-261220251037.xls` | | | | | |
| TC-01 | `extrato-itau-2025.xls` | | | | | |
| TC-02 | `extrato-itau-2025.pdf` | | | | | |
| TC-03 | `fatura_itau-202510.csv` | | | | | |
| TC-03 | `fatura_itau-202511.csv` | | | | | |
| TC-03 | `fatura_itau-202512.csv` | | | | | |
| TC-04 | `fatura-202508.csv` | | | | | |
| TC-04 | `fatura-202509.csv` | | | | | |
| TC-04 | `fatura-202601.csv` | | | | | |
| TC-05 | `fatura-202509.pdf` | | | | | |
| TC-05 | `fatura-202510.pdf` | | | | | |
| TC-05 | `fatura-202511.pdf` | | | | | |
| TC-05 | `fatura-202512.pdf` | | | | | |
| TC-06 | `extrato_btg.xls` | | | | | |
| TC-06 | `Extrato_..._11259347605.xls` | | | | | |
| TC-07 | `Extrato_..._11259347605.pdf` | | | | | |
| TC-08 | `2026-02-01_...BTG.xlsx` | | | | | |
| TC-08 | `2026-03-01_...BTG.xlsx` | | | | | |
| TC-09 | `2026-02-01_...BTG.pdf` | | | | | |
| TC-09 | `2026-03-01_...BTG.pdf` | | | | | |
| TC-10 | `MP202501.xlsx` | | | | | |
| TC-10 | `MP202508.xlsx` | | | | | |
| TC-10 | `MP202512.xlsx` | | | | | |
| TC-11 | `account_statement-202ffd51...xlsx` | | | | | |
| TC-11 | `account_statement-3a5161f1...xlsx` | | | | | |
| TC-12 | `MP202508.pdf` | | | | | |
| TC-12 | `MP202512.pdf` | | | | | |
| TC-13 | `FATURAMP202507.pdf` | | | | | |
| TC-13 | `FATURAMP202512.pdf` | | | | | |
| TC-13 | `FATURAMP202602.pdf` | | | | | |
