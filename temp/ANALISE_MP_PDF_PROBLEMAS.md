# Análise de Problemas — MP Extrato PDF Parser

**Estado atual:** 610/634 matches (96,2%) — regra inline, sem Y-map  
**Algoritmo:** ID-as-anchor + regra `inline_atual` para atribuição de frags  
**Meses testados:** MP202508, MP202509, MP202510, MP202511, MP202512

---

## Resumo dos 24 Mismatches

| Padrão | Qtd | Descrição |
|---|---|---|
| A | 6 | Dois tx seguidos com 3 frags entre eles: "Emergência" + "Pix/QR desc" + NOME |
| B | 6 | Tx com inline (`Rendimentos` ou `Pagamento`) + frag NOME vazando para o próximo tx |
| C | 1 | "Reserva por gastos" sem "Emergência" (3 frags, split errado) |
| D | 9 | Espaço duplo: PDF tem 1 espaço, XLSX tem 2 espaços em "Itaú Unibanco  S.A." |
| E | 2 | "Casar. Com" (espaço após ponto) no PDF vs "Casar.Com" no XLSX |

---

## Padrão A — 3 frags entre dois tx: "Emergência" + "tipo de Pix" + NOME

**Frequência: 6 casos (3 pares em ago/set/out)**

**O que acontece:**  
A sequência real no PDF tem 3 frags entre TX1 e TX2:
- FRAG: "Emergência"
- FRAG: "Pagamento com QR Pix" ou "Transferência Pix enviada"  ← *não tem ID, é frag*
- FRAG: NOME do destinatário

A regra `2+ frags` envia `frags[0]="Emergência"` para `desc_after[TX1]` e
`frags[1:]="Pagamento com QR Pix NOME"` para `desc_before[TX2]`. Porém o XLSX
espera a separação em: TX1=`"Dinheiro retirado Emergência"` e TX2=`"Pagamento com QR Pix NOME"`.
O atual split coloca apenas o nome no TX2, deixando "Pagamento com QR Pix" vazando para TX1.

**Exemplos reais (608 run → pares alinhados):**

```
Data        PDF desc (errado)                                   XLSX desc (correto)
----------  --------------------------------------------------  --------------------------------------------------
10/08/2025  'Dinheiro retirado Emergência Pagamento com QR Pix' 'Dinheiro retirado Emergência'
10/08/2025  'IGREJA BATISTA DE AGUA BRANCA'                     'Pagamento com QR Pix IGREJA BATISTA DE AGUA BRANCA'

14/08/2025  'Dinheiro retirado Emergência Transferência Pix enviada'  'Dinheiro retirado Emergência'
14/08/2025  'GISLEINE SANTOS ARRUDA YAMADA'                     'Transferência Pix enviada GISLEINE SANTOS ARRUDA YAMADA'

04/09/2025  'Dinheiro retirado Emergência Transferência Pix enviada'  'Dinheiro retirado Emergência'
04/09/2025  'Gisleine Santos Arruda Yamada'                     'Transferência Pix enviada Gisleine Santos Arruda Yamada'
```

**Sequência de entries no extract_text():**
```
TX:   DD-MM-YYYY  Dinheiro retirado   [ID]  R$ -XXX,XX
FRAG: Emergência
FRAG: Transferência Pix enviada              ← sem ID → frag
FRAG: GISLEINE SANTOS ARRUDA YAMADA
TX:   DD-MM-YYYY                     [ID]  R$ -XXX,XX   ← inline vazio
```

**Fix necessário:** Com 3 frags e inline_atual vazio, a divisão deveria ser:
- `desc_after[TX1]` = `frags[0]` = "Emergência"
- `desc_before[TX2]` = `frags[1]` = "Transferência Pix enviada"
- `desc_after[TX2]` = `frags[2]` = "GISLEINE SANTOS ARRUDA YAMADA"
→ Regra de 3+ frags com inline vazio = desc_after do tx atual recebe o último frag.

---

## Padrão B — Inline de Tx vaza para tx seguinte, e NOME fica sozinho

**Frequência: 6 casos (3 pares em out/nov)**

**O que acontece:**  
TX1 tem inline ("Rendimentos") e 1 frag antes (pertencente ao anterior).
TX2 tem inline ("Transferência Pix enviada/recebida") e FRAG NOME depois.
O NOME frag, entre TX2 e TX3, vai para `desc_before[TX3]` (inline_atual(TX3) vazio)
em vez de `desc_after[TX2]`.

**Exemplos reais:**
```
Data        PDF desc (errado)                                   XLSX desc (correto)
----------  --------------------------------------------------  --------------------------------------------------
02/10/2025  'Rendimentos Transferência Pix enviada'             'Rendimentos'
02/10/2025  'Gisleine Santos Arruda Yamada'                     'Transferência Pix enviada Gisleine Santos Arruda Yamada'

28/10/2025  'Rendimentos Transferência Pix recebida'            'Rendimentos'
28/10/2025  'RENAN VIEIRA DO NASCIMENTO'                        'Transferência Pix recebida RENAN VIEIRA DO NASCIMENTO'

21/11/2025  'Rendimentos Transferência Pix enviada'             'Rendimentos'
21/11/2025  'Pedro Henrique Leal de Oliveira'                   'Transferência Pix enviada Pedro Henrique Leal de Oliveira'
```

**Sequência de entries provável:**
```
TX:   DD-MM-YYYY  Rendimentos            [ID]  R$ +X,XX
FRAG: Transferência Pix enviada                        ← sem ID → frag
FRAG: NOME DO DESTINATARIO
TX:   DD-MM-YYYY                         [ID]  R$ -XXX,XX  ← inline vazio
```

Com 2 frags e inline_atual vazio, a regra atual coloca:
- `desc_after[Rendimentos_tx]` = "Transferência Pix enviada" ❌ (deveria ir para desc_before de outro tx)
- `desc_before[prox_tx]` = "NOME" ❌

**Fix necessário:** Idem Padrão A — precisa de regra específica para 2+ frags quando inline_atual é vazio.

---

## Padrão C — "Reserva por gastos" sem "Emergência" (3 frags, split errado)

**Frequência: 1 caso (out)**

**Exemplos reais:**
```
Data        PDF desc (errado)                   XLSX desc (correto)
----------  ----------------------------------  --------------------------------
18/10/2025  'Pagamento CONECTCAR Reserva por gastos'   'Pagamento CONECTCAR'
18/10/2025  'Emergência'                               'Reserva por gastos Emergência'
```

**Sequência de entries provável:**
```
TX:   DD-MM-YYYY  Pagamento CONECTCAR  [ID]  R$ -XX,XX
FRAG: Reserva por gastos
FRAG: Emergência
TX:   DD-MM-YYYY                       [ID]  R$ -XXX,XX   ← inline vazio
```

Com 2 frags entre TX1 e TX2 (inline_atual vazio):
- Regra atual (2+ frags): `desc_after[TX1]="Reserva por gastos"`, `desc_before[TX2]="Emergência"` ❌
- Correto: `desc_before[TX2]="Reserva por gastos"`, `desc_after[TX2]="Emergência"` ← ambos pertencem ao TX2

**Atenção:** Este padrão confirma que a regra de 2+ frags com inline_atual vazio precisa
atribuir **todos** os frags ao tx2 (desc_before + desc_after), não dividir entre TX1 e TX2.

---

## Padrão D — Espaço duplo: "Itaú Unibanco  S.A."

**Frequência: 9 casos (2 em ago, 1 em set, 4 em out, 1 em nov, 1 em dez)**

**Exemplos reais:**
```
Data        PDF desc (errado)                               XLSX desc (correto)
----------  ------------------------------------------      ------------------------------------------
20/08/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
22/08/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
26/09/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
12/10/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
24/10/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
27/10/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
31/10/2025  'Pagamento de contas Itaú Unibanco S.A.'        'Pagamento de contas Itaú Unibanco  S.A.'
30/11/2025  'Pagamento de conta Itaú Unibanco S.A.'         'Pagamento de conta Itaú Unibanco  S.A.'
28/12/2025  'Pagamento de conta Itaú Unibanco S.A.'         'Pagamento de conta Itaú Unibanco  S.A.'
```

**Causa raiz:**  
O XLSX original do MP registra "Itaú Unibanco  S.A." com 2 espaços (provavelmente
2 células concatenadas ou espaço de formatação). O `extract_text()` do pdfplumber
produz apenas 1 espaço.

**Fix:** Normalizar espaços múltiplos em **ambos** os processadores ao gerar o `lancamento`
para hash. `' '.join(desc.split())` em ambos — XLSX e PDF — resolve sem alterar exibição.

---

## Padrão E — "Casar. Com" (espaço após ponto no PDF)

**Frequência: 2 casos (ago)**

**Exemplos reais:**
```
Data        PDF desc (errado)                                              XLSX desc (correto)
----------  -----------------------------------------------------------------  -----------------------------------------------------------------
16/08/2025  'Pagamento com QR Pix Casar. Com Site de Casamento e Eventos S.A.'  'Pagamento com QR Pix Casar.Com Site de Casamento e Eventos S.A.'
```

**Causa raiz:**  
O `extract_text()` do pdfplumber insere espaço após o ponto em "Casar.Com" devido
ao kerning/espaçamento da fonte. O XLSX não tem esse espaço.

**Fix:** Post-processamento pontual com regex `re.sub(r'\.\s+([A-Z])', r'.\1', desc)`.
Risco baixo de falsos positivos — "Itaú Unibanco. S.A." não existe nos dados.
Alternativa: normalizar só para fins de hash (não altera exibição).

---

## Plano de Ação para Próxima Sessão

| Prioridade | Padrão | Fix | Impacto |
|---|---|---|---|
| 🔴 P0 | A + B + C | Regra especial: 2+frags + inline_atual vazio → todos frags ficam no tx atual (desc_before=frags[0..n-1], desc_after=frags[n]) | +13 matches |
| 🟡 P1 | D | `' '.join(desc.split())` em ambos processadores na hora do hash | +9 matches |
| 🟢 P2 | E | `re.sub(r'\.\s+([A-Z])', r'.\1', desc)` no processador PDF | +2 matches |

**Meta:** 610 → 634 (100%) após P0+P1+P2.

---

## Comandos de Diagnóstico

```bash
# Ver sequência de entries para um caso específico (ex: 10/08/2025)
python -c "
import pdfplumber, re
_TX_RE = re.compile(r'(\d{2}-\d{2}-\d{4})\s*(.*?)\s*(\d{10,})\s+R\\\$\s*(-?[\d.]+,\d{2})')
with pdfplumber.open('_arquivos_historicos/_csvs_historico/extrato/MP/MP202508.pdf') as pdf:
    texto = '\n'.join(p.extract_text() or '' for p in pdf.pages)
for i, line in enumerate(texto.split('\n')):
    l = line.strip()
    if not l: continue
    m = _TX_RE.search(l)
    tag = 'TX  ' if m else 'FRAG'
    info = (f\"{m.group(1)} inline='{m.group(2)}' val={m.group(4)}\" if m else repr(l[:70]))
    print(f'{i:3}: {tag} | {info}')
" 2>/dev/null | grep -A5 -B3 "10-08-2025"
```

```bash
# Rodar teste completo
source app_dev/venv/bin/activate && python temp/test_mp_pdf_words.py 2>/dev/null | tail -5
```

