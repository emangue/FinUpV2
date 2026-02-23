# feature: novos processadores PDF/XLSX

**Data:** 22/02/2026  
**Desenvolvido em:** workspace `NovoProcesadorPDF`

---

## O que essa feature entrega

Suporte a 4 novos formatos de importação no sistema:

| Banco | Tipo | Formato | Arquivo |
|---|---|---|---|
| Itaú | Fatura | PDF (com senha) | `pdf/itau_fatura_pdf.py` |
| BTG Pactual | Fatura | XLSX | `excel/btg_fatura_xlsx.py` |
| BTG Pactual | Fatura | PDF | `pdf/btg_fatura_pdf.py` |
| Mercado Pago | Fatura | PDF (OCR) | `pdf/mercadopago_fatura_pdf.py` |

---

## Conteúdo desta pasta

```
feature_novos_processadores_pdf/
├── README.md                    <- este arquivo
├── GUIA_IMPLEMENTACAO_V5.md     <- guia completo com contexto, decisões e troubleshooting
├── registry_delta.py            <- imports e entradas prontos para colar no registry.py
├── requirements_delta.txt       <- dependências a adicionar no requirements.txt
├── migration.sql                <- SQL para habilitar formatos no banco
├── pdf/
│   ├── itau_fatura_pdf.py       <- destino: raw/pdf/itau_fatura_pdf.py  (SUBSTITUI)
│   ├── btg_fatura_pdf.py        <- destino: raw/pdf/btg_fatura_pdf.py   (NOVO)
│   └── mercadopago_fatura_pdf.py <- destino: raw/pdf/mercadopago_fatura_pdf.py (NOVO)
└── excel/
    └── btg_fatura_xlsx.py       <- destino: raw/excel/btg_fatura_xlsx.py (NOVO)
```

---

## Deploy em 5 passos

**1. Copiar os processadores**
```bash
cp pdf/itau_fatura_pdf.py        /caminho/V5/.../processors/raw/pdf/
cp pdf/btg_fatura_pdf.py         /caminho/V5/.../processors/raw/pdf/
cp pdf/mercadopago_fatura_pdf.py /caminho/V5/.../processors/raw/pdf/
cp excel/btg_fatura_xlsx.py      /caminho/V5/.../processors/raw/excel/
```

**2. Atualizar registry.py**  
Usar `registry_delta.py` como referência — adicionar os imports e as entradas no dict `PROCESSORS`.

**3. Instalar dependências**
```bash
pip install -r requirements_delta.txt
```

**4. Adicionar variáveis de ambiente**
```env
ITAU_PDF_SENHA=<CPF sem pontos/traço>
BTG_PDF_SENHA=<CPF sem pontos/traço>
```

**5. Executar migration.sql** no banco de dados do V5.

---

## Validação (testes rodados com arquivos reais)

| Processador | Arquivos testados | Resultado |
|---|---|---|
| Itaú Fatura PDF | 5 faturas (ago–dez/25) | ✅ diferença R$ 0,00 em todas |
| BTG Fatura XLSX | faturas reais | ✅ diferença R$ 0,00 |
| BTG Fatura PDF | faturas reais | ✅ diferença R$ 0,00 |
| Mercado Pago Fatura PDF | 7 faturas (jul/25–jan/26) | ✅ 5/7 R$ 0,00 · 2/7 esperado* |

*Os 2 casos "esperado" (Dez/25 e Jan/26) têm as transações 100% corretas. O `is_valid = False` reflete créditos de pagamento na capa que não são transações de compra — comportamento esperado e documentado.

---

## Observação importante — Mercado Pago PDF

O processador usa **OCR** (easyocr + PyMuPDF) porque os PDFs do Mercado Pago têm fonte com mapeamento corrompido. O easyocr carrega ~950 MB de modelo em RAM na primeira chamada (singleton), mantendo-o em cache para as próximas. A VM atual (16 GB RAM) comporta isso com folga.

Ver `GUIA_IMPLEMENTACAO_V5.md` para detalhes completos.
