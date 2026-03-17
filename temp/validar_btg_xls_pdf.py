"""
Script de validação: BTG Extrato XLS + PDF
Executa após as 4 tarefas do DIAGNOSTICO_BTG_EXTRATO_XLS.md

Valores esperados (verificados em laboratório):
  XLS: 65 transações
  PDF: 65 transações
  Saldo XLS = Saldo PDF (exato, sem tolerância)
  PDF saldo total = R$ 97,02
  3 transações de Crédito e Financiamento: -17064.96 / -11348.77 / -31.31

Uso:
    source app_dev/venv/bin/activate
    python3 temp/validar_btg_xls_pdf.py
"""
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
        erros.append(f"XLS: valores Financiamento {valores_fin} != esperados {esperados}")
    else:
        print(f"  OK Valores Financiamento corretos: {valores_fin}")

    # Campo Transacao no lancamento (Tarefa 3)
    tem_transacao = any(
        ' - Pix ' in t['lancamento'] or
        ' - Portabilidade ' in t['lancamento'] or
        ' - Pagamento de boleto ' in t['lancamento']
        for t in xls
    )
    if not tem_transacao:
        erros.append("XLS: campo Transacao ausente no lancamento (Tarefa 3 nao aplicada?)")
    else:
        ex = next(t['lancamento'] for t in xls
                  if ' - Pix ' in t['lancamento'] or ' - Portabilidade ' in t['lancamento'])
        print(f"  OK Campo Transacao presente - ex: '{ex[:60]}'")

except Exception as e:
    erros.append(f"XLS: excecao - {e}")
    print(f"ERRO: {e}")

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
        erros.append(f"PDF: {n_pdf} transacoes (esperado 65)")
    if len(credito_pdf) != 3:
        erros.append(f"PDF: {len(credito_pdf)} transacoes de Financiamento (esperado 3)")
    if saldo_pdf != 97.02:
        erros.append(f"PDF: saldo R$ {saldo_pdf:,.2f} != esperado R$ 97,02")

    # Sem transacoes falsas de metadados
    falsas = [t for t in pdf_result if any(kw in t.lancamento
              for kw in ['Cliente:', 'Agência:', 'CPF:', 'Ouvidoria', 'CNPJ', '©'])]
    if falsas:
        erros.append(f"PDF: {len(falsas)} linha(s) de metadado viraram transacoes")
        for f in falsas[:3]:
            print(f"  FALSA: {f.lancamento}")
    else:
        print("  OK Nenhuma linha de metadado convertida indevidamente")

except Exception as e:
    erros.append(f"PDF: excecao - {e}")
    print(f"ERRO: {e}")

# ─── BLOCO 3: XLS == PDF (exato) ───────────────────────────────────────
print("\n" + "="*65)
print("🔀 XLS <-> PDF (comparação exata, sem tolerância)")
print("="*65)
try:
    print(f"Delta Transacoes: {abs(n_xls - n_pdf)}  (esperado: 0)")
    print(f"Delta Saldo:      R$ {abs(saldo_xls - saldo_pdf):.2f}  (esperado: R$ 0,00)")
    if n_xls != n_pdf:
        erros.append(f"Comparacao: XLS={n_xls} tx != PDF={n_pdf} tx")
    if saldo_xls != saldo_pdf:
        erros.append(f"Comparacao: saldo XLS R$ {saldo_xls:,.2f} != PDF R$ {saldo_pdf:,.2f}")
except Exception:
    print("AVISO: Comparacao impossivel (um dos blocos falhou)")

# ─── RESULTADO ─────────────────────────────────────────────────────────
print("\n" + "="*65)
if erros:
    print(f"FAIL — {len(erros)} problema(s):")
    for e in erros:
        print(f"  • {e}")
    sys.exit(1)
else:
    print("PASS — XLS e PDF corretos e identicos")
    print(f"   XLS: {n_xls} tx | R$ {saldo_xls:,.2f}")
    print(f"   PDF: {n_pdf} tx | R$ {saldo_pdf:,.2f}")
