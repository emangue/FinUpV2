# Guia de Implementação — ProjetoFinancasV5

> **Atualizado em:** 22/02/2026
> **Objetivo:** Documentar todas as mudanças necessárias no ProjetoFinancasV5 para integrar os novos processadores produzidos neste workspace.

---

## O que vai ser integrado

| Processador | Arquivo origem | Destino no V5 | Status |
|---|---|---|---|
| Itaú Fatura PDF (com senha) | `deploy/itau/itau_fatura_pdf.py` | `raw/pdf/itau_fatura_pdf.py` | **Atualiza existente** |
| BTG Fatura PDF | `deploy/btg/btg_fatura_pdf.py` | `raw/pdf/btg_fatura_pdf.py` | **Novo** |
| BTG Fatura XLSX | `deploy/btg/btg_fatura_xlsx.py` | `raw/excel/btg_fatura_xlsx.py` | **Novo** |
| Mercado Pago Fatura PDF (OCR) | `processadores/mercadopago/mercadopago_fatura_pdf.py` | `raw/pdf/mercadopago_fatura_pdf.py` | **Novo** |

---

## Validação — Resultados dos Testes

Todos os processadores foram validados com arquivos reais antes do deploy.

### Itaú Fatura PDF

Testado com 5 faturas mensais reais. Extração de texto nativa via `pdfplumber` — sem OCR.

| Fatura | Diferença |
|---|---|
| 2025-08 | ✅ R$ 0,00 |
| 2025-09 | ✅ R$ 0,00 |
| 2025-10 | ✅ R$ 0,00 |
| 2025-11 | ✅ R$ 0,00 |
| 2025-12 | ✅ R$ 0,00 |

### BTG Fatura XLSX e PDF

Testado com faturas reais em ambos os formatos. XLSX é preferido (dados limpos, `final_cartao` por linha, datas exatas). PDF é fallback.

| Formato | Resultado |
|---|---|
| XLSX | ✅ Diferença R$ 0,00 |
| PDF | ✅ Diferença R$ 0,00 |

### Mercado Pago Fatura PDF (OCR)

Testado com 7 faturas mensais (`FaturaMercadoPago202507.pdf` a `FaturaMercadoPago202601.pdf`).

**Por que OCR?** Os PDFs do Mercado Pago usam mapeamento de glifos corrompido — a extração nativa retorna texto ilegível (ex: `êE$íóõOPó*` em vez de `MERCADOPAGO*FOXEQUIPSEG`). OCR via `easyocr` + `PyMuPDF` resolve completamente.

| Fatura | Transações | Total declarado | Soma extraída | Diferença | Obs |
|---|---|---|---|---|---|
| Jul/2025 | 9 | R$ 241,34 | R$ 241,34 | ✅ R$ 0,00 | |
| Ago/2025 | 8 | R$ 273,32 | R$ 273,32 | ✅ R$ 0,00 | |
| Set/2025 | 10 | R$ 623,45 | R$ 623,45 | ✅ R$ 0,00 | |
| Out/2025 | 15 | R$ 1.166,94 | R$ 1.166,94 | ✅ R$ 0,00 | 2 cartões: `*3517` + `*5966` |
| Nov/2025 | 18 | R$ 1.427,40 | R$ 1.427,40 | ✅ R$ 0,00 | |
| Dez/2025 | 26 | (negativo) | R$ 1.306,58 | ⚠️ esperado | Total a pagar negativo: pagamento antecipado gerou saldo positivo |
| Jan/2026 | 27 | R$ 1.521,99 | R$ 1.711,77 | ⚠️ esperado | Crédito de dez/25 abatido na capa (R$ 189,78) — transações corretas |

> **Sobre os casos "esperado" de Dez e Jan:** As transações extraídas estão 100% corretas. O `is_valid = False` é esperado — o campo "Total a pagar" da capa inclui créditos e saldos anteriores que não são transações de compra. Não é bug do processador.

---

## Estrutura de Pastas Relevante no V5

```
app_dev/backend/app/domains/upload/
├── router.py
├── service.py
├── models.py
├── schemas.py
└── processors/
    └── raw/
        ├── base.py                          <- RawTransaction, BalanceValidation
        ├── registry.py                      <- PROCESSORS dict + get_processor()
        ├── csv/
        │   └── itau_fatura.py
        ├── excel/
        │   ├── btg_extrato.py
        │   └── btg_fatura_xlsx.py           <- NOVO
        └── pdf/
            ├── itau_fatura_pdf.py           <- ATUALIZAR (senha)
            ├── btg_fatura_pdf.py            <- NOVO
            └── mercadopago_fatura_pdf.py    <- NOVO (OCR)
```

---

## BACKEND — Passo a Passo

### Passo 1 — Copiar os arquivos de processador

```bash
# 1. Atualizar Itaú Fatura PDF
cp deploy/itau/itau_fatura_pdf.py \
   /caminho/V5/app/domains/upload/processors/raw/pdf/itau_fatura_pdf.py

# 2. BTG Fatura PDF
cp deploy/btg/btg_fatura_pdf.py \
   /caminho/V5/app/domains/upload/processors/raw/pdf/btg_fatura_pdf.py

# 3. BTG Fatura XLSX
cp deploy/btg/btg_fatura_xlsx.py \
   /caminho/V5/app/domains/upload/processors/raw/excel/btg_fatura_xlsx.py

# 4. Mercado Pago Fatura PDF
cp processadores/mercadopago/mercadopago_fatura_pdf.py \
   /caminho/V5/app/domains/upload/processors/raw/pdf/mercadopago_fatura_pdf.py
```

---

### Passo 2 — Atualizar registry.py

**Arquivo:** `app/domains/upload/processors/raw/registry.py`

#### 2a. Adicionar imports

```python
from .pdf.itau_fatura_pdf import process_itau_fatura_pdf                    # ja existe
from .pdf.btg_fatura_pdf import process_btg_fatura_pdf                      # NOVO
from .excel.btg_fatura_xlsx import process_btg_fatura_xlsx                  # NOVO
from .pdf.mercadopago_fatura_pdf import process_mercadopago_fatura_pdf      # NOVO
```

#### 2b. Injetar senha via functools.partial

O `service.py` chama o processador com assinatura fixa:
```python
processor(file_path, nome_arquivo, nome_cartao, final_cartao)
```
Para injetar senha sem alterar o service, usa-se `functools.partial`:

```python
import os
from functools import partial

_ITAU_SENHA = os.getenv('ITAU_PDF_SENHA')   # CPF sem pontos/traço
_BTG_SENHA  = os.getenv('BTG_PDF_SENHA')    # CPF sem pontos/traço
```

#### 2c. Atualizar o dict PROCESSORS

```python
PROCESSORS: dict[Tuple[str, str, str], ProcessorFunc] = {
    # ── Itaú ──────────────────────────────────────────────────────────────────
    ('itau', 'fatura', 'csv'):    csv_itau_fatura,
    ('itau', 'extrato', 'excel'): process_itau_extrato,
    ('itau', 'extrato', 'pdf'):   _wrap_extrato_pdf(process_itau_extrato_pdf),
    # ATUALIZADO: aceita senha via partial
    ('itau', 'fatura', 'pdf'):    partial(process_itau_fatura_pdf, senha=_ITAU_SENHA)
                                  if _ITAU_SENHA else process_itau_fatura_pdf,

    # ── BTG Pactual ───────────────────────────────────────────────────────────
    ('btg', 'extrato', 'excel'):         process_btg_extrato,
    ('btg pactual', 'extrato', 'excel'): process_btg_extrato,
    ('btg-pactual', 'extrato', 'excel'): process_btg_extrato,
    # NOVOS: BTG Fatura — XLSX preferido, PDF é fallback
    ('btg', 'fatura', 'excel'):
        partial(process_btg_fatura_xlsx, senha=_BTG_SENHA) if _BTG_SENHA else process_btg_fatura_xlsx,
    ('btg pactual', 'fatura', 'excel'):
        partial(process_btg_fatura_xlsx, senha=_BTG_SENHA) if _BTG_SENHA else process_btg_fatura_xlsx,
    ('btg', 'fatura', 'pdf'):
        partial(process_btg_fatura_pdf, senha=_BTG_SENHA) if _BTG_SENHA else process_btg_fatura_pdf,
    ('btg pactual', 'fatura', 'pdf'):
        partial(process_btg_fatura_pdf, senha=_BTG_SENHA) if _BTG_SENHA else process_btg_fatura_pdf,

    # ── Mercado Pago ──────────────────────────────────────────────────────────
    ('mercado pago', 'extrato', 'excel'): process_mercadopago_extrato,
    ('mercadopago', 'extrato', 'excel'):  process_mercadopago_extrato,
    ('mercado pago', 'extrato', 'pdf'):   _wrap_extrato_pdf(process_mercadopago_extrato_pdf),
    ('mercadopago', 'extrato', 'pdf'):    _wrap_extrato_pdf(process_mercadopago_extrato_pdf),
    # NOVO: Mercado Pago Fatura PDF (OCR)
    ('mercado pago', 'fatura', 'pdf'):    process_mercadopago_fatura_pdf,
    ('mercadopago', 'fatura', 'pdf'):     process_mercadopago_fatura_pdf,
}
```

> **Atenção:** `_normalize_bank_name("BTG Pactual")` retorna `"btg pactual"` (com espaço). As chaves `'btg'` são aliases para retrocompatibilidade.

---

### Passo 3 — Variáveis de ambiente

Adicionar ao `.env` do backend:

```env
# CPF sem pontos/traço do titular
ITAU_PDF_SENHA=12345678901
BTG_PDF_SENHA=12345678901
```

> **Segurança:** Nunca comitar as senhas no repositório. Usar `.env` local ou secrets do servidor.

---

### Passo 4 — Dependências Python

Adicionar ao `requirements.txt`:

```txt
# BTG XLSX
msoffcrypto-tool>=4.12.0
openpyxl>=3.1.0

# Mercado Pago Fatura PDF (OCR)
easyocr>=1.7.0      # instala PyTorch automaticamente (~600 MB de dependências)
PyMuPDF>=1.24.0     # já necessário para outros PDFs
```

Instalar:

```bash
pip install msoffcrypto-tool openpyxl easyocr
```

> Na primeira execução, os modelos OCR (~100 MB) são baixados automaticamente para `~/.EasyOCR/`. A partir daí ficam em cache local — sem download nas próximas execuções.

---

### Passo 5 — Atualizar tabela de compatibilidade no banco

```sql
-- BTG: habilitar PDF e Excel para fatura
UPDATE bank_format_compatibility
SET pdf_status = 'OK', excel_status = 'OK'
WHERE bank_name = 'BTG Pactual';

-- Mercado Pago: habilitar PDF para fatura
UPDATE bank_format_compatibility
SET pdf_status = 'OK'
WHERE bank_name = 'Mercado Pago';

-- Se os registros não existirem:
INSERT INTO bank_format_compatibility (bank_name, csv_status, excel_status, pdf_status, ofx_status)
VALUES ('BTG Pactual', 'TBD', 'OK', 'OK', 'TBD');

INSERT INTO bank_format_compatibility (bank_name, csv_status, excel_status, pdf_status, ofx_status)
VALUES ('Mercado Pago', 'TBD', 'OK', 'OK', 'TBD');
```

---

### Passo 6 — (Opcional) Passar senha dinamicamente pelo pipeline

Para permitir que o usuário informe a senha a cada upload, em vez de variável de ambiente:

```python
# router.py — adicionar campo senha
senha: Optional[str] = Form(None)

# service.py — propagar
def process_and_preview(self, ..., senha: Optional[str] = None):
    raw_transactions, balance_validation = self._fase1_raw_processing(..., senha=senha)

def _fase1_raw_processing(self, ..., senha: Optional[str] = None):
    result = processor(file_path_obj, nome_arquivo, nome_cartao, final_cartao, senha=senha)
```

> Recomendação: use a variável de ambiente (Passo 3) para simplificar. O Passo 6 só é necessário se diferentes usuários usarem CPFs diferentes.

---

## Detalhes técnicos — OCR no Mercado Pago

### Por que OCR e não extração nativa?

| Abordagem | Velocidade | Memória | Precisão |
|---|---|---|---|
| pdfplumber (texto nativo) | ~0,24s / 3 págs | ~50 MB | 100% para PDFs normais |
| easyocr (OCR) | ~20-25s / fatura (Linux) | ~950 MB fixo + pico | >99% |

O PDF do Mercado Pago usa mapeamento de glifos corrompido. `pdfplumber` retorna texto ilegível onde deveria estar a descrição das compras. OCR é a única solução viável — e foi validada com 100% de acurácia nas descrições nos 7 PDFs testados.

### Performance e memória na VM (KVM4 — Ubuntu 24.04, 16 GB RAM, 4 cores)

| Métrica | Valor | Obs |
|---|---|---|
| Uso atual da VM | ~3 GB (19%) | Sem o processador MP |
| Modelo OCR em RAM (fixo) | ~950 MB | Carregado uma vez, singleton por processo |
| Pico durante inferência | ~1,5–2 GB (Linux) | Temporário por página; liberado após |
| Total pior caso | ~5,5 GB | Sobram ~10 GB livres — sem risco |
| Tempo por fatura | ~20–25s estimado | Mac: 43s; Linux com 4 cores: melhor |

O modelo fica em RAM após o primeiro uso (`_ocr_reader` singleton). Chamadas subsequentes não têm overhead de carregamento.

### Estrutura dos PDFs Mercado Pago

```
Página 1:    Capa — "Total a pagar R$ X,XX", "Vence em DD/MM/YYYY"
Páginas 2-N: Transações
               ├── [Movimentações na fatura]  <- pagamentos/créditos — IGNORAR
               ├── Cartão Visa [***5966]       <- troca o cartão corrente
               ├── DD/MM | Descrição | [Parcela X de Y |] R$ valor
               └── Total | R$ valor            <- resumo por cartão/página — IGNORAR
Última(s):   "Parcele a fatura do seu Cartão de Crédito"  <- IGNORAR completamente
```

**Casos especiais tratados:**
- Múltiplos cartões na mesma fatura (Out/2025: `*3517` + `*5966`)
- Compras internacionais: `Compra internacional em PAYPAL *GITHUB INC R$ 189,78`
- Parcelas concatenadas na descrição: `MERCADOPAGO*FOXEQUIPSEG Parcela 1 de 7`
- Linhas cambiais `BRL X = USD Y` filtradas automaticamente
- Pagamentos de fatura filtrados (são créditos, não compras)

---

## Fluxo completo — Mercado Pago Fatura PDF

```
Frontend -> POST /api/upload/preview
            banco="Mercado Pago", formato="PDF", tipoDocumento="fatura"
            |
registry   -> _normalize_bank_name("Mercado Pago") = "mercado pago"
            -> PROCESSORS[("mercado pago", "fatura", "pdf")]
            -> process_mercadopago_fatura_pdf()
            |
processador
  1. pdfplumber lê página 1 -> extrai "Total a pagar" -> BalanceValidation
  2. Para cada página de transações (2..N):
     a. fitz renderiza em 3x (~216 DPI) -> PNG em memória
     b. easyocr.readtext() -> [(bbox, texto, confiança)]
     c. Agrupa por Y (tolerância 25px) -> linhas visuais ordenadas
     d. Interpreta cada linha: cartão / transação / total / pagamento
  3. Retorna (List[RawTransaction], BalanceValidation)
            |
service.py -> isinstance(result, tuple) = True
           -> salva raw_transactions em preview_transacoes
           -> retorna UploadPreviewResponse com sessionId + balance_validation
```

---

## FRONTEND — O que mudou

### Já funciona sem nenhuma mudança

| Funcionalidade | Status |
|---|---|
| Campo de senha (PDF com senha) | ✅ `fileFormat === "PDF_PASSWORD"` |
| Envio de `senha` no FormData | ✅ `formData.append('senha', password)` |
| Seleção de banco dinâmica | ✅ `/api/compatibility` |
| Status de formato por banco | ✅ Badge OK/WIP/TBD |
| Aba Fatura vs Extrato | ✅ Tabs no UploadDialog |
| `BalanceValidation` na resposta | ✅ `UploadPreviewResponse` |

### Mudanças recomendadas

Atualizar a tabela estática de compatibilidade em `upload/page.tsx`:

```tsx
{/* BTG Pactual — PDF: TBD -> OK */}
<Badge className="bg-green-500 ...">OK</Badge>

{/* Mercado Pago — PDF (fatura): TBD -> OK */}
<Badge className="bg-green-500 ...">OK</Badge>
```

> Esta tabela é apenas informativa. O que realmente habilita o botão de upload é o SQL do Passo 5.

---

## Checklist de Deploy

### Backend
- [ ] Copiar `deploy/itau/itau_fatura_pdf.py` -> `raw/pdf/itau_fatura_pdf.py`
- [ ] Copiar `deploy/btg/btg_fatura_pdf.py` -> `raw/pdf/btg_fatura_pdf.py`
- [ ] Copiar `deploy/btg/btg_fatura_xlsx.py` -> `raw/excel/btg_fatura_xlsx.py`
- [ ] Copiar `processadores/mercadopago/mercadopago_fatura_pdf.py` -> `raw/pdf/mercadopago_fatura_pdf.py`
- [ ] Adicionar imports no `registry.py` (btg_fatura_pdf, btg_fatura_xlsx, mercadopago_fatura_pdf)
- [ ] Adicionar `from functools import partial` e `import os` no `registry.py`
- [ ] Adicionar entradas BTG fatura e Mercado Pago fatura no dict `PROCESSORS`
- [ ] Adicionar `ITAU_PDF_SENHA` e `BTG_PDF_SENHA` no `.env`
- [ ] Atualizar `requirements.txt`: msoffcrypto-tool, openpyxl, easyocr, PyMuPDF
- [ ] Instalar: `pip install msoffcrypto-tool openpyxl easyocr`
- [ ] Executar SQL do Passo 5 (BTG e Mercado Pago pdf_status='OK')
- [ ] Reiniciar backend

### Frontend
- [ ] (Opcional) Atualizar badges na tabela estática de `upload/page.tsx`: BTG PDF e Mercado Pago PDF -> OK

### Smoke tests após deploy

```
# Logs esperados no backend:

# BTG XLSX
✅ Processador encontrado: btg pactual/fatura/excel
✅ Fatura BTG XLSX: N transações | diferença R$ 0,00

# Mercado Pago PDF (primeira execução no servidor)
Inicializando easyocr...        <- aparece UMA VEZ por vida do processo
easyocr pronto.
✅ Fatura Mercado Pago PDF: N transações
✅ Validação: total declarado R$ X | soma extraída R$ Y | diferença R$ 0,00
```

---

## Troubleshooting

| Problema | Causa provável | Solução |
|---|---|---|
| `Processador não encontrado: btg pactual/fatura/excel` | Entradas não adicionadas ao registry | Verificar Passo 2c |
| `Processador não encontrado: mercado pago/fatura/pdf` | Import/entrada faltando | Verificar Passos 2a e 2c |
| `Formato PDF não suportado para Mercado Pago` | `pdf_status='TBD'` no banco | Executar SQL do Passo 5 |
| `Falha ao descriptografar (senha errada?)` | Env var vazia ou senha errada | Verificar `.env` |
| `ModuleNotFoundError: msoffcrypto` | Não instalado | `pip install msoffcrypto-tool` |
| `ModuleNotFoundError: easyocr` | Não instalado | `pip install easyocr` |
| MP PDF: timeout no primeiro upload | Download modelos easyocr (~100 MB) | Aguardar ~2 min; próximas chamadas normais |
| MP PDF: 0 transações | Todas as páginas eram de parcelamento | Confirmar que é fatura (não extrato) |
| MP PDF: is_valid=False em Dez/Jan | Créditos na capa (comportamento esperado) | Não é bug — ver seção de validação acima |
| BTG XLSX: `Cabeçalho não encontrado` | Estrutura de aba diferente | Verificar aba 'Titular' e posição do cabeçalho (~linha 20) |
| BTG PDF: 0 transações | Regex de seção não bateu | Verificar se PDF tem seção "Lançamentos do cartão ... Final XXXX" |
