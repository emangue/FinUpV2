# 🔍 Diagnóstico — Upload Extrato BTG Pactual (XLS Multi-Página)

**Arquivo analisado:** `Extrato_2025-12-10_a_2026-03-09_11259347605.xls`  
**Período:** 10/12/2025 a 09/03/2026 | Conta: 856710-1 | Agência: 20  
**Gerado por:** JasperReports Library 6.16.0 (exportação de PDF paginado → XLS)  
**Data da análise:** 15/03/2026  

---

## 🚨 Resultado do Upload Atual

O processador `btg_extrato.py` **extrai apenas 62 de 65 transações reais**, perdendo silenciosamente 3 transações. Não há erro/exceção visível — o upload "parece funcionar" mas os dados ficam incompletos.

---

## 📋 Problemas Identificados (por severidade)

---

### ❌ BUG CRÍTICO — P1: Filtro `str.contains('nan')` destrói "Crédito e Financiamento"

**Arquivo:** `app_dev/backend/app/domains/upload/processors/raw/excel/btg_extrato.py`  
**Linha:** ~220 (filtro de lançamentos inválidos)

#### Causa raiz

O processador tenta remover lançamentos onde o pandas converteu `NaN` em string `"nan"`. Para isso usa:

```python
(~df_trabalho['lancamento'].str.lower().str.contains('nan'))
```

**O problema:** A categoria `Crédito e Financiamento` contém o substring `"nan"`:

```
Crédito e Fina[nan]ciamento
           ↑↑↑ posições 9-11: 'n','a','n'
```

Resultado: **todas** as transações de financiamento/boleto bancário são silenciosamente descartadas.

#### Transações perdidas (comprovado em laboratório)

| Linha XLS | Data | Categoria | Descrição | Valor |
|-----------|------|-----------|-----------|-------|
| L72 (Bloco 2) | 30/01/2026 | Crédito e Financiamento | Banco Itaú | **-R$ 17.064,96** |
| L109 (Bloco 2) | 27/02/2026 | Crédito e Financiamento | Banco Itaú | **-R$ 11.348,77** |
| L117 (Bloco 2) | 06/03/2026 | Crédito e Financiamento | Mercado Crédito S.A. | **-R$ 31,31** |

**Total perdido: -R$ 28.444,04** (3 transações)

#### Rastreamento do filtro

```
L72  lancamento: 'Crédito e Financiamento - Banco Itaú'
     str.contains('nan') → True  ← FALSO POSITIVO (nan em "Fina[nan]ciamento")
     → REMOVIDA INCORRETAMENTE ❌

L109 lancamento: 'Crédito e Financiamento - Banco Itaú'
     str.contains('nan') → True  ← mesma causa
     → REMOVIDA INCORRETAMENTE ❌

L117 lancamento: 'Crédito e Financiamento - Mercado Crédito...'
     str.contains('nan') → True  ← mesma causa
     → REMOVIDA INCORRETAMENTE ❌
```

---

### ⚠️ BUG SECUNDÁRIO — P2: Estrutura multi-página (3 blocos de header)

**Impacto atual:** Baixo (filtros de data cobrem), mas frágil.

#### O que acontece

O arquivo BTG é gerado pelo JasperReports exportando um PDF paginado para XLS. Cada "página" do relatório é embutida no mesmo sheet, repetindo o cabeçalho completo:

```
Linha 00–10: Cabeçalho Bloco 1 (header: "Data e hora | Categoria | Transação | Descrição | Valor")
Linha 11–55: Transações Dec/2025 + Jan/2026 (parte 1)  → 34 transações reais
Linha 56–59: Rodapé Bloco 1 (Ouvidoria, © BTG Pactual)
Linha 60–71: Cabeçalho Bloco 2 (repetição completa: cliente, CPF, agência...)
Linha 72–120: Transações Jan/2026 (parte 2) + Fev/2026  → 30 transações reais
Linha 121–124: Rodapé Bloco 2
Linha 125–136: Cabeçalho Bloco 3
Linha 137–139: Transações Mar/2026  → 1 transação real
Linha 140–143: Rodapé Bloco 3 + marca BTG
```

#### Comportamento do processador atual

```python
# Para no PRIMEIRO header (linha 10) e lê TUDO até o fim
for idx, row in df_full.iterrows():
    if 'data e hora' in row_str:
        header_row = idx
        break  # ← para no primeiro, lê 133 linhas até o fim

df = df_full.iloc[header_row + 1:]  # linhas 11–143 = 133 linhas
```

As linhas de cabeçalho dos Blocos 2 e 3 (ex: "Cliente:", "Agência:", "Data e hora" como valores) são inseridas no meio dos dados. Elas são filtradas pelo parser de data (strings como "Cliente:" não parsam como DD/MM/YYYY), **mas isso é uma coincidência feliz, não uma solução robusta**.

#### Risco

Se uma linha de cabeçalho do Bloco 2 tiver uma data acidental no campo errado, ou se o filtro de lancamento não funcionar bem, dados de metadados podem virar "transações falsas".

---

### ⚠️ PROBLEMA DE QUALIDADE — P3: Campo `lancamento` perde informação de tipo

**Impacto:** Baixo na importação, mas afeta classificação automática.

#### Estrutura real das colunas do XLS

| Pos | Nome (header) | Conteúdo (exemplo) |
|-----|--------------|-------------------|
| B (col 1) | Data e hora | `12/12/2025 21:06` |
| C (col 2) | Categoria | `Transferência` |
| D (col 3) | **Transação** | `Pix recebido` |
| E–F | (vazio) | — |
| G (col 6) | Descrição | `Emanuel Guerra Leandro` |
| K (col 10) | Valor | `180.09` |

#### Lançamento atual (incompleto)

```python
lancamento = categoria + " - " + descricao
# Resultado: "Transferência - Emanuel Guerra Leandro"
# PERDENDO: "Pix recebido" (tipo específico da operação)
```

#### Lançamento ideal (completo)

```python
lancamento = categoria + " - " + transacao + " - " + descricao
# Resultado: "Transferência - Pix recebido - Emanuel Guerra Leandro"
```

Isso melhora a classificação automática e a geração de hashes únicos de deduplicação.

---

## 📊 Resumo Quantitativo

| # | Problema | Tipo | Transações afetadas | Valor perdido |
|---|----------|------|---------------------|---------------|
| P1 | `str.contains('nan')` remove "Financiamento" | Bug crítico | **3 perdidas** | **-R$ 28.444,04** |
| P2 | Multi-página sem tratamento explícito | Frágil | 0 (por coincidência) | R$ 0 |
| P3 | Campo `transacao` ignorado no lançamento | Qualidade | 62 incompletas | R$ 0 |
| P4 | Sem processador PDF para extrato BTG | Lacuna | 65 sem suporte | R$ 0 |

**Estado atual (XLS):** 62 transações extraídas de 65 esperadas (95,4% de cobertura)  
**Estado atual (PDF):** 0% — formato sem processador registrado  
**Estado desejado:** 65/65 XLS ✅ + 65/65 PDF ✅ (dois formatos, mesmo resultado)

---

## 🛠️ Plano de Ação

### Sprint único — 3 tarefas em ordem de prioridade

---

#### ✅ Tarefa 1 — Corrigir filtro `str.contains('nan')` [CRÍTICO — 30 min]

**Arquivo:** `app_dev/backend/app/domains/upload/processors/raw/excel/btg_extrato.py`

**Fix:** substituir comparação de substring por comparação de word boundary.

**Antes (bugado):**
```python
mask_lancamento_valido = (
    (df_trabalho['lancamento'] != '') & 
    (df_trabalho['lancamento'] != '-') &
    (df_trabalho['lancamento'] != 'nan - nan') &
    (~df_trabalho['lancamento'].str.lower().str.contains('nan'))  # ← BUG
)
```

**Depois (correto):**
```python
mask_lancamento_valido = (
    (df_trabalho['lancamento'] != '') & 
    (df_trabalho['lancamento'] != '-') &
    (~df_trabalho['lancamento'].str.lower().str.match(r'^nan\s*-\s*nan$')) &
    (~df_trabalho['lancamento'].str.lower().str.contains(r'\bnan\b', regex=True))
)
```

**Por quê `\bnan\b`?**  
`\b` é word boundary — só casa "nan" como palavra isolada, não como parte de "Financiamento":
```
"crédito e financiamento - banco itaú"  →  \bnan\b não casa  → ✅ mantida
"nan - nan"                             →  \bnan\b casa      → ✅ removida
"nan - pagamento recebido"              →  \bnan\b casa      → ✅ removida
```

**Critério de sucesso:** `processar_btg_extrato_interno(arquivo)` retorna 65 transações (não 62).

---

#### ✅ Tarefa 2 — Tratar estrutura multi-página explicitamente [MÉDIO — 45 min]

**Arquivo:** `app_dev/backend/app/domains/upload/processors/raw/excel/btg_extrato.py`

**Fix:** encontrar TODOS os headers, unir apenas as linhas de dados de cada bloco (excluindo linhas de metadados/rodapé entre blocos).

```python
# Encontrar todas as posições de header "Data e hora"
header_rows = []
for idx, row in df_full.iterrows():
    row_str = ' '.join([str(v).lower() for v in row if pd.notna(v)])
    if 'data e hora' in row_str:
        header_rows.append(idx)

if not header_rows:
    raise ValueError("Header 'Data e hora' não encontrado no arquivo")

logger.info(f"✅ {len(header_rows)} bloco(s) encontrado(s) nas linhas {header_rows}")

# Para cada bloco, pegar apenas as linhas entre esse header e o próximo
# Uma linha é "de dados" se: tem data válida (DD/MM/YYYY), tem valor numérico
# e não é "Saldo Diário"
dfs = []
for i, hr in enumerate(header_rows):
    # Fim do bloco = próximo header (ou fim do arquivo)
    # Recuamos alguns se o bloco subsequente tem cabeçalho de página
    next_start = header_rows[i+1] if i+1 < len(header_rows) else df_full.shape[0]
    
    bloco = df_full.iloc[hr+1 : next_start].copy()
    bloco.columns = df_full.iloc[hr].values
    bloco = bloco.reset_index(drop=True)
    dfs.append(bloco)

# Concatenar todos os blocos
df = pd.concat(dfs, ignore_index=True)
```

**Critério de sucesso:** arquivo com 5+ blocos de página processa corretamente sem linhas extras de metadados.

---

#### ✅ Tarefa 3 — Incluir coluna `Transação` no lançamento [BAIXO — 15 min]

**Arquivo:** `app_dev/backend/app/domains/upload/processors/raw/excel/btg_extrato.py`

**Fix:**

```python
# Detectar coluna "Transação" (col D, posição 3)
col_transacao = None
for col in df.columns:
    if col is None:
        continue
    if 'transa' in str(col).lower() and 'ação' in str(col).lower():
        col_transacao = col
        break

# Na criação do lançamento:
if col_transacao and col_transacao in df.columns:
    df_trabalho['transacao'] = df[col_transacao].fillna('').astype(str)
    df_trabalho['lancamento'] = (
        df_trabalho['categoria'] + ' - ' +
        df_trabalho['transacao'] + ' - ' +
        df_trabalho['descricao']
    ).str.strip(' -')
else:
    # Fallback para compatibilidade com formato antigo
    df_trabalho['lancamento'] = df_trabalho['categoria'] + ' - ' + df_trabalho['descricao']
```

**⚠️ Atenção:** Mudar o formato do lançamento afeta os **hashes de deduplicação** (`IdTransacao`). Transações já importadas no histórico com o formato antigo não serão marcadas como duplicata se reimportadas com o novo formato. Avaliar se vale forçar re-hash ou apenas aplicar ao novo formato.

**Critério de sucesso:** lançamentos do tipo "Transferência - Pix recebido - Emanuel Guerra Leandro" (em vez de apenas "Transferência - Emanuel Guerra Leandro").

---

#### ✅ Tarefa 4 — Criar processador PDF para extrato BTG [MÉDIO — 60 min]

**Arquivo analisado:** `Extrato_2025-12-10_a_2026-03-09_11259347605.pdf` (mesmo período do XLS)  
**Resultado esperado:** 65 transações, saldo R$ 97,02

---

##### 4.1 — Análise Real do PDF (pdfplumber)

O PDF tem **3 páginas**. Cada página começa com cabeçalho idêntico (linhas L000–L009) e termina com rodapé (Ouvidoria + ©BTG). O `pdfplumber` extrai o texto corrido por página — as colunas **não** têm delimitadores claros.

**Estrutura do cabeçalho (todas as páginas):**
```
L000: 'Olá Emanuel!'
L001: 'Este é o extrato da sua conta corrente BTG Pactual'
L002: 'Extrato de conta corrente 09/03/2026 21h24'
L003: 'Cliente: Emanuel Guerra Leandro'
L004: 'CPF: 112.593.476-05'
L005: 'Agência: 20'
L006: 'Conta: 856710-1'
L007: 'Período do extrato: 10/12/2025 a 09/03/2026'
L008: 'Lançamentos: Saldo atual R$ 97,49'
L009: 'Data e hora Categoria Transação Descrição Valor'
```

**Formato da linha de transação normal:**
```
'DD/MM/YYYY HHhMM Categoria Transação Descrição ±R$ X.XXX,XX'
```
Exemplos reais:
```
'12/12/2025 21h06 Transferência Pix recebido Emanuel Guerra Leandro R$ 180,09'
'15/12/2025 07h07 Salário Portabilidade de salário Pagamento recebido R$ 14.830,40'
'15/12/2025 07h23 Transferência Pix enviado Emanuel Guerra Leandro -R$ 7.000,00'
'15/12/2025 13h04 Contas Pagamento de boleto Quata Emp E P Imobiliario -R$ 2.536,90'
'19/01/2026 07h13 Contas Transferência recebida QuintoAndar R$ 352,01'
```

**Padrão de Saldo Diário (ignorar):**
```
'12/12/2025 23h59 Saldo Diário R$ 180,09'
'15/12/2025 23h59 Saldo Diário R$ 3.114,50'
```

---

##### 4.2 — Padrões de Fragmentação Identificados no PDF Real

O JasperReports quebra linhas longas. Foram encontrados **4 padrões de fragmentação**:

---

**Padrão A — "Crédito e Financiamento" simples (3 linhas)**

A categoria `Crédito e Financiamento` é dividida: "Crédito e" aparece antes da data, "Financiamento" aparece depois.

Página 2, linhas L023–L025:
```
L023: 'Crédito e'
L024: '30/01/2026 07h30 Pagamento de boleto Banco Itaú -R$ 17.064,96'
L025: 'Financiamento'
```
→ `data=30/01/2026`, `valor=-17064.96`, `lancamento="Crédito e Financiamento - Pagamento de boleto Banco Itaú"`

Página 3, linhas L027–L029:
```
L027: 'Crédito e'
L028: '27/02/2026 16h20 Pagamento de boleto Banco Itaú -R$ 11.348,77'
L029: 'Financiamento'
```
→ `data=27/02/2026`, `valor=-11348.77`, `lancamento="Crédito e Financiamento - Pagamento de boleto Banco Itaú"`

---

**Padrão B — "Crédito e Financiamento" com descrição fragmentada (3 linhas com sobra)**

A categoria E parte da descrição transbordam para as linhas ao redor.

Página 3, linhas L036–L038:
```
L036: 'Crédito e Mercado Crédito Sociedade De Crédito'
L037: '06/03/2026 14h05 Transferência enviada -R$ 31,31'
L038: 'Financiamento Financiamento E Investimento S A'
```
→ `data=06/03/2026`, `valor=-31.31`, `lancamento="Crédito e Financiamento - Transferência enviada"`  
⚠️ Descrição completa ("Mercado Crédito...") é perdida em v1 — **aceitável** pois data e valor estão corretos.

**Regra de detecção:** linha que começa com `Crédito e` mas NÃO começa com `DD/MM/YYYY` → ativa flag `credito_e_context = True`.  
**Regra de reset:** linha que começa com `Financiamento` mas NÃO começa com `DD/MM/YYYY` → reset `credito_e_context = False`, skip.

---

**Padrão C — Transação transbordou para ANTES da linha de data**

A coluna "Transação" foi longa demais e aparece na linha anterior à data.

Página 2, linhas L028–L029:
```
L028: 'Pagamento de fatura do cartão'
L029: '30/01/2026 08h05 Contas Fatura do cartão BTG Pactual -R$ 646,76'
```
→ L029 está completa (tem Categoria + Descrição + Valor). L028 é overflow ignorado.  
→ `lancamento = "Contas Fatura do cartão BTG Pactual"`

Página 3, linhas L025–L026:
```
L025: 'Pagamento de fatura do cartão'
L026: '27/02/2026 14h09 Contas Fatura do cartão BTG Pactual -R$ 2.795,29'
```
→ Mesmo comportamento.

**Regra:** linhas não-data que não começam com `Crédito e` → skip (são overflow ignorado).

---

**Padrão D — Transação transbordou para ANTES e DEPOIS (sanduíche)**

Texto da coluna "Transação" partiu em duas linhas: uma antes e uma depois da data.

Página 2, linhas L033–L035:
```
L033: 'Pix enviado via assistente virtual'
L034: '31/01/2026 16h36 Transferência Ana Beatriz Teixeira Correa De Avo -R$ 300,00'
L035: 'no WhatsApp'
```
→ L034 está completa (Categoria=Transferência, Descrição presente). L033 e L035 são overflow ignorados.  
→ `lancamento = "Transferência Ana Beatriz Teixeira Correa De Avo"`

Página 2, linhas L044–L046:
```
L044: 'Pix enviado via assistente virtual'
L045: '17/02/2026 16h27 Transferência Yescom Entretenimento, Esportes E Marketing. -R$ 84,00'
L046: 'no WhatsApp'
```
→ Mesmo comportamento.

**Regra:** linhas não-data após uma linha de data (e que não começam com `Financiamento`) → skip.

---

##### 4.3 — Algoritmo de Parsing (Estado de máquina)

```
credito_e_context = False   ← flag de estado

Para cada linha:

  [SKIP] linha vazia → ignorar
  [SKIP] linha contém qualquer SKIP_KEYWORD → ignorar
  [SKIP] linha contém 'Saldo Diário' → ignorar

  [ESTADO A] linha começa com 'Crédito e' E não é linha de data:
      → credito_e_context = True
      → skip linha

  [ESTADO B] linha começa com 'Financiamento' E não é linha de data:
      → se credito_e_context == True: credito_e_context = False
      → skip linha

  [TRANSAÇÃO] linha começa com DD/MM/YYYY HHhMM (linha de data):
      → extrair data (grupo 1 do regex)
      → extrair valor do final da linha (padrão '-?R$ X.XXX,XX')
      → lancamento = tudo entre data+hora e valor
      → se credito_e_context == True:
             lancamento = "Crédito e Financiamento - " + lancamento
             (NÃO resetar context ainda — espera o "Financiamento" na linha seguinte)
      → adicionar transação

  [OVERFLOW] qualquer outra linha (não-data, não-skip, não-Crédito e):
      → ignorar (é overflow da coluna Transação, a linha de data já é completa)
```

---

##### 4.4 — Implementação Completa

**Arquivo a criar:** `app_dev/backend/app/domains/upload/processors/raw/pdf/btg_extrato_pdf.py`

```python
"""
📄 PROCESSADOR BTG PACTUAL - EXTRATO DE CONTA CORRENTE (Formato PDF)

=== FORMATO ===
PDF de 3 páginas gerado pelo JasperReports 6.16.0.
Cada página repete o cabeçalho completo (Cliente, CPF, Agência...).
Transações no formato: DD/MM/YYYY HHhMM Categoria Transação Descrição ±R$ X.XXX,XX

=== PADRÕES DE FRAGMENTAÇÃO ===
O JasperReports pode quebrar linhas longas em múltiplas linhas:

Padrão A (Crédito e Financiamento simples):
    'Crédito e'
    'DD/MM/YYYY HHhMM Transação Descrição -R$ valor'
    'Financiamento'

Padrão B (Crédito e Financiamento com descrição):
    'Crédito e [início da descrição]'
    'DD/MM/YYYY HHhMM Transação -R$ valor'
    'Financiamento [fim da descrição]'

Padrão C (Transação transborda ANTES da data):
    '[texto da coluna Transação]'
    'DD/MM/YYYY HHhMM Categoria Descrição -R$ valor'   ← linha completa

Padrão D (Transação transborda antes E depois):
    '[início da coluna Transação]'
    'DD/MM/YYYY HHhMM Categoria Descrição -R$ valor'   ← linha completa
    '[fim da coluna Transação]'

=== ESTRATÉGIA ===
- Máquina de estados com flag `credito_e_context`
- Padrões C e D: a linha de data já é completa → ignora overflow
- Padrões A e B: detecta 'Crédito e' → injeta categoria no lancamento

=== RESULTADO ESPERADO (arquivo de referência) ===
- 65 transações (mesmo período do XLS)
- Saldo R$ 97,02

=== HISTÓRICO ===
- V1 (inicial): criado após análise do PDF Extrato_2025-12-10_a_2026-03-09
"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import List

import pdfplumber

from ..base import RawTransaction

logger = logging.getLogger(__name__)

# Regex para identificar linha de transação: começa com DD/MM/YYYY HHhMM
_RE_DATE_LINE = re.compile(r'^(\d{2}/\d{2}/\d{4})\s+\d{2}h\d{2}\s+')

# Regex para extrair valor do final da linha: -R$ X.XXX,XX ou R$ X.XXX,XX
_RE_VALOR_END = re.compile(r'(-?R\$\s*[\d\.]+,\d{2})\s*$')

# Palavras-chave que identificam linhas de cabeçalho/rodapé a ignorar
_SKIP_KEYWORDS = [
    'Olá Emanuel',
    'Este é o extrato',
    'Extrato de conta',
    'Cliente:',
    'CPF:',
    'Agência:',
    'Conta:',
    'Período',
    'Lançamentos:',
    'Data e hora',
    'Ouvidoria',
    '©BTG',
]


def _parse_valor(valor_str: str) -> float:
    """
    Converte 'R$ 1.234,56' ou '-R$ 1.234,56' para float.
    Remove R$, espaços, pontos de milhar. Substitui vírgula por ponto.
    """
    limpo = re.sub(r'[R$\s]', '', valor_str)   # → "1234,56" ou "-1234,56"
    limpo = limpo.replace('.', '').replace(',', '.')  # → "1234.56" ou "-1234.56"
    return float(limpo)


def process_btg_extrato_pdf(
    file_path: Path,
    banco: str,
    tipo_documento: str,
    user_email: str,
) -> List[RawTransaction]:
    """
    Processa PDF de extrato BTG Pactual (multi-página JasperReports).

    Args:
        file_path: Caminho do arquivo .pdf
        banco: Nome do banco (ex: 'BTG Pactual')
        tipo_documento: 'extrato'
        user_email: Email do usuário

    Returns:
        Lista de RawTransaction (uma por transação real, sem Saldo Diário)
    """
    transacoes: List[RawTransaction] = []
    nome_arquivo = file_path.name
    data_criacao = datetime.now()

    with pdfplumber.open(file_path) as pdf:
        logger.info(f"📄 PDF BTG extrato: {len(pdf.pages)} página(s) — {nome_arquivo}")

        for num_pagina, page in enumerate(pdf.pages, 1):
            texto = page.extract_text()
            if not texto:
                logger.warning(f"⚠️  Página {num_pagina} sem texto extraível")
                continue

            lines = texto.splitlines()
            credito_e_context = False  # flag de estado: próxima data-line é "Crédito e Financiamento"

            for line in lines:
                line = line.strip()

                # Linha vazia
                if not line:
                    continue

                # Cabeçalho/rodapé
                if any(kw in line for kw in _SKIP_KEYWORDS):
                    continue

                # Saldo Diário (não é transação real)
                if 'Saldo Diário' in line:
                    continue

                # Padrões A e B: início de "Crédito e Financiamento"
                # Linha começa com "Crédito e" mas NÃO é uma linha de data
                if line.startswith('Crédito e') and not _RE_DATE_LINE.match(line):
                    credito_e_context = True
                    continue  # a categoria será injetada na próxima data-line

                # Padrões A e B: sufixo "Financiamento" após a data-line
                # Linha começa com "Financiamento" mas NÃO é linha de data
                if line.startswith('Financiamento') and not _RE_DATE_LINE.match(line):
                    if credito_e_context:
                        credito_e_context = False  # contexto consumido
                    continue

                # Linha de transação: começa com DD/MM/YYYY HHhMM
                m_date = _RE_DATE_LINE.match(line)
                if m_date:
                    m_valor = _RE_VALOR_END.search(line)
                    if not m_valor:
                        logger.warning(f"⚠️  Linha de data sem valor: {repr(line)}")
                        continue

                    data_str = line[:10]  # 'DD/MM/YYYY'
                    meio = line[m_date.end():m_valor.start()].strip()
                    valor = _parse_valor(m_valor.group(1))

                    # Injetar categoria se contexto ativo
                    if credito_e_context:
                        lancamento = f"Crédito e Financiamento - {meio}"
                        # NÃO resetar aqui — espera "Financiamento" suffix na linha seguinte
                    else:
                        lancamento = meio

                    if valor == 0.0:
                        continue

                    transacoes.append(RawTransaction(
                        banco=banco,
                        tipo_documento=tipo_documento,
                        nome_arquivo=nome_arquivo,
                        data_criacao=data_criacao,
                        data=data_str,
                        lancamento=lancamento,
                        valor=valor,
                        nome_cartao=None,
                        final_cartao=None,
                        mes_fatura=None,
                    ))
                    continue

                # Qualquer outra linha (overflow Padrões C e D): ignorar
                # A linha de data correspondente já é completa o suficiente.

    saldo = sum(t.valor for t in transacoes)
    logger.info(f"✅ PDF BTG extrato: {len(transacoes)} transações | saldo R$ {saldo:,.2f}")
    return transacoes
```

---

##### 4.5 — Registrar em `registry.py`

**Arquivo:** `app_dev/backend/app/domains/upload/processors/raw/registry.py`

Adicionar o import (junto aos outros imports de pdf):
```python
from .pdf.btg_extrato_pdf import process_btg_extrato_pdf
```

Adicionar as entradas no dict `PROCESSORS` (junto às entradas BTG fatura):
```python
# BTG Pactual - Extrato PDF (NOVO)
('btg', 'extrato', 'pdf'): process_btg_extrato_pdf,
('btg pactual', 'extrato', 'pdf'): process_btg_extrato_pdf,
('btg-pactual', 'extrato', 'pdf'): process_btg_extrato_pdf,
```

**Critério de sucesso:** `process_btg_extrato_pdf(arquivo_pdf, ...)` retorna exatamente **65 transações** com soma **R$ 97,02**.

---

## 📁 Arquivos a Modificar

```
app_dev/backend/app/domains/upload/processors/raw/
├── excel/
│   └── btg_extrato.py          ← Tarefas 1, 2 e 3 (fix XLS)
├── pdf/
│   └── btg_extrato_pdf.py      ← Tarefa 4 (NOVO — processador PDF)
└── registry.py                 ← Tarefa 4 (adicionar entradas PDF)
```

Não há mudança em schema, migrations ou outros domínios.

---

## 🧪 Script de Validação (XLS + PDF)

Após implementar todas as correções (Tarefas 1–4), rodar:

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
source app_dev/venv/bin/activate
python3 temp/validar_btg_xls_pdf.py
```

> **Valores esperados (verificados por análise direta do PDF):**  
> XLS: **65** transações | PDF: **65** transações  
> Saldo XLS = Saldo PDF = **exato** (mesmo dado, formatos diferentes)  
> PDF saldo total = **R$ 97,02** (calculado e verificado em laboratório)  
> 3 transações de "Crédito e Financiamento": **-R$ 17.064,96 / -11.348,77 / -31,31**

**Criar `temp/validar_btg_xls_pdf.py`:**

```python
import sys, os
from pathlib import Path

sys.path.insert(0, 'app_dev/backend')
os.environ.setdefault('DATABASE_URL', 'postgresql://x:x@localhost/x')
os.environ.setdefault('JWT_SECRET_KEY', 'test')

from app.domains.upload.processors.raw.excel.btg_extrato import processar_btg_extrato_interno
from app.domains.upload.processors.raw.pdf.btg_extrato_pdf import process_btg_extrato_pdf

BASE  = Path('_arquivos_historicos/_csvs_historico/extrato/btg')
F_XLS = BASE / 'Extrato_2025-12-10_a_2026-03-09_11259347605.xls'
F_PDF = BASE / 'Extrato_2025-12-10_a_2026-03-09_11259347605.pdf'

erros = []

# ─── BLOCO 1: XLS ──────────────────────────────────────────────────────
print("\n" + "="*65)
print("📄 XLS")
print("="*65)
try:
    xls = processar_btg_extrato_interno(F_XLS, user_id=1)
    n_xls     = len(xls)
    saldo_xls = round(sum(t['valor'] for t in xls), 2)
    credito_xls = [t for t in xls if 'Financiamento' in t['lancamento']]

    print(f"Transações:              {n_xls:>4}  (esperado: 65)")
    print(f"Crédito e Financiamento: {len(credito_xls):>4}  (esperado:  3)")
    print(f"Saldo total:      R$ {saldo_xls:>10,.2f}")

    if n_xls != 65:
        erros.append(f"XLS: {n_xls} transações (esperado 65)")
    if len(credito_xls) != 3:
        erros.append(f"XLS: {len(credito_xls)} transações de Financiamento (esperado 3)")

    # Valores individuais exatos das 3 transações de Financiamento
    valores_fin = sorted([round(t['valor'], 2) for t in credito_xls])
    esperados   = sorted([-17064.96, -11348.77, -31.31])
    if valores_fin != esperados:
        erros.append(f"XLS: valores Financiamento {valores_fin} ≠ esperados {esperados}")
    else:
        print(f"  ✅ Valores Financiamento corretos: {valores_fin}")

    # Campo Transação no lançamento (Tarefa 3)
    tem_transacao = any(
        ' - Pix ' in t['lancamento'] or
        ' - Portabilidade ' in t['lancamento'] or
        ' - Pagamento de boleto ' in t['lancamento']
        for t in xls
    )
    if not tem_transacao:
        erros.append("XLS: campo Transação ausente no lançamento (Tarefa 3 não aplicada?)")
    else:
        ex = next(t['lancamento'] for t in xls
                  if ' - Pix ' in t['lancamento'] or ' - Portabilidade ' in t['lancamento'])
        print(f"  ✅ Campo Transação presente — ex: '{ex[:60]}'")

except Exception as e:
    erros.append(f"XLS: exceção — {e}")
    print(f"❌ {e}")

# ─── BLOCO 2: PDF ──────────────────────────────────────────────────────
print("\n" + "="*65)
print("📄 PDF")
print("="*65)
try:
    pdf_result = process_btg_extrato_pdf(
        F_PDF, banco='BTG Pactual', tipo_documento='extrato', user_email='test@test.com'
    )
    n_pdf     = len(pdf_result)
    saldo_pdf = round(sum(t.valor for t in pdf_result), 2)
    credito_pdf = [t for t in pdf_result if 'Financiamento' in t.lancamento]

    print(f"Transações:              {n_pdf:>4}  (esperado: 65)")
    print(f"Crédito e Financiamento: {len(credito_pdf):>4}  (esperado:  3)")
    print(f"Saldo total:      R$ {saldo_pdf:>10,.2f}  (esperado: R$ 97,02)")

    if n_pdf != 65:
        erros.append(f"PDF: {n_pdf} transações (esperado 65)")
    if len(credito_pdf) != 3:
        erros.append(f"PDF: {len(credito_pdf)} transações de Financiamento (esperado 3)")
    if saldo_pdf != 97.02:
        erros.append(f"PDF: saldo R$ {saldo_pdf:,.2f} ≠ esperado R$ 97,02")

    # Sem transações falsas de metadados
    falsas = [t for t in pdf_result if any(kw in t.lancamento
              for kw in ['Cliente:', 'Agência:', 'CPF:', 'Ouvidoria', 'CNPJ', '©'])]
    if falsas:
        erros.append(f"PDF: {len(falsas)} linha(s) de metadado viraram transações")
        for f in falsas[:3]:
            print(f"  ⚠️  {f.lancamento}")
    else:
        print("  ✅ Nenhuma linha de metadado convertida indevidamente")

except Exception as e:
    erros.append(f"PDF: exceção — {e}")
    print(f"❌ {e}")

# ─── BLOCO 3: XLS == PDF (exato) ───────────────────────────────────────
print("\n" + "="*65)
print("🔀 XLS ↔ PDF (comparação exata, sem tolerância)")
print("="*65)
try:
    print(f"Δ Transações: {abs(n_xls - n_pdf)}  (esperado: 0)")
    print(f"Δ Saldo:      R$ {abs(saldo_xls - saldo_pdf):.2f}  (esperado: R$ 0,00)")
    if n_xls != n_pdf:
        erros.append(f"Comparação: XLS={n_xls} tx ≠ PDF={n_pdf} tx")
    if saldo_xls != saldo_pdf:
        erros.append(f"Comparação: saldo XLS R$ {saldo_xls:,.2f} ≠ PDF R$ {saldo_pdf:,.2f}")
except Exception:
    print("⚠️  Comparação impossível (um dos blocos falhou)")

# ─── RESULTADO ─────────────────────────────────────────────────────────
print("\n" + "="*65)
if erros:
    print(f"❌ FAIL — {len(erros)} problema(s):")
    for e in erros: print(f"  • {e}")
    sys.exit(1)
else:
    print("✅ PASS — XLS e PDF corretos e idênticos")
    print(f"   XLS: {n_xls} tx | R$ {saldo_xls:,.2f}")
    print(f"   PDF: {n_pdf} tx | R$ {saldo_pdf:,.2f}")
```

---

## 📅 Ordem de Execução Recomendada

```
1. Tarefa 1 (fix filtro nan)         → 30 min   → Resolve os -R$ 28.444,04
2. Tarefa 2 (multi-página explícito) → 45 min   → Robustez para arquivos multi-página
3. Tarefa 3 (campo Transação)        → 15 min   → Qualidade de classificação
4. Tarefa 4 (processador PDF)        → 60 min   → Suporte ao formato PDF BTG extrato
5. Script de validação (XLS + PDF)   → 5 min    → Confirmar 65/65 em ambos os formatos
6. Deploy + teste real de upload     → 15 min   → Upload XLS e PDF na UI, confirmar produção
```

**Tempo total estimado: ~3h (incluindo testes e deploy)**

---

## 🔎 Contexto Técnico

- **Gerador do arquivo:** JasperReports 6.16.0 (BTG exporta PDF paginado → XLS via JasperReports, cada "página" do relatório vira um bloco repetido no mesmo sheet)
- **Formato:** Composite Document File V2 (formato `.xls` legado, lido via `xlrd`)
- **Arquivo de referência antigo:** `_arquivos_historicos/_csvs_historico/extrato/btg/extrato_btg.xls` (formato single-page, 1 bloco — processador foi desenvolvido para esse)
- **Arquivo novo:** multi-página (3 blocos) — comportamento diferente porque o período exportado é maior (3 meses em vez de 1)
