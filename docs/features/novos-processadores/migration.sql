-- SQL para executar no banco do V5
-- Habilita os novos formatos no endpoint /compatibility
-- que controla quais botões ficam ativos no UploadDialog do frontend.
--
-- Executar APÓS o deploy dos processadores e reinício do backend.

-- ── BTG Pactual: habilitar PDF e Excel para fatura ───────────────────────────
UPDATE bank_format_compatibility
SET
    excel_status = 'OK',
    pdf_status   = 'OK'
WHERE bank_name = 'BTG Pactual';

-- ── Mercado Pago: habilitar PDF para fatura ───────────────────────────────────
UPDATE bank_format_compatibility
SET pdf_status = 'OK'
WHERE bank_name = 'Mercado Pago';

-- ── Fallback: INSERT caso os registros não existam ────────────────────────────
INSERT INTO bank_format_compatibility (bank_name, csv_status, excel_status, pdf_status, ofx_status)
SELECT 'BTG Pactual', 'TBD', 'OK', 'OK', 'TBD'
WHERE NOT EXISTS (
    SELECT 1 FROM bank_format_compatibility WHERE bank_name = 'BTG Pactual'
);

INSERT INTO bank_format_compatibility (bank_name, csv_status, excel_status, pdf_status, ofx_status)
SELECT 'Mercado Pago', 'TBD', 'OK', 'OK', 'TBD'
WHERE NOT EXISTS (
    SELECT 1 FROM bank_format_compatibility WHERE bank_name = 'Mercado Pago'
);

-- ── Verificar resultado ───────────────────────────────────────────────────────
SELECT bank_name, csv_status, excel_status, pdf_status, ofx_status
FROM bank_format_compatibility
WHERE bank_name IN ('BTG Pactual', 'Mercado Pago', 'Itaú')
ORDER BY bank_name;
