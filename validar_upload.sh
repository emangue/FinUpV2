#!/bin/bash
# Script de validação do upload

echo "========================================="
echo "VALIDAÇÃO: Extrato Conta Corrente-261220251037"
echo "========================================="
echo ""

cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database

echo "1. Resumo da Preview:"
sqlite3 financas_dev.db "
SELECT 
    'Total no preview' as metrica,
    COUNT(*) as valor
FROM preview_transacoes
UNION ALL
SELECT 
    'Duplicadas (devem ser todas)',
    COUNT(*)
FROM preview_transacoes
WHERE is_duplicate = 1
UNION ALL
SELECT 
    'Não duplicadas (devem ser 0)',
    COUNT(*)
FROM preview_transacoes
WHERE is_duplicate = 0;
"

echo ""
echo "2. Transações NÃO duplicadas (PROBLEMA SE APARECER ALGO):"
sqlite3 financas_dev.db "
SELECT 
    data,
    lancamento,
    valor,
    IdTransacao
FROM preview_transacoes
WHERE is_duplicate = 0
LIMIT 10;
"

echo ""
echo "3. Verificando se IdTransacao da preview existe no journal:"
sqlite3 financas_dev.db "
SELECT 
    p.data,
    p.lancamento,
    p.valor,
    p.IdTransacao,
    CASE 
        WHEN j.IdTransacao IS NOT NULL THEN '✅ Existe no journal'
        ELSE '❌ NÃO existe (problema!)'
    END as status
FROM preview_transacoes p
LEFT JOIN journal_entries j ON j.IdTransacao = p.IdTransacao
WHERE p.is_duplicate = 0
LIMIT 10;
"

echo ""
echo "4. Amostras de hashes para validação:"
sqlite3 financas_dev.db "
SELECT 
    data,
    lancamento,
    valor,
    IdTransacao
FROM preview_transacoes
WHERE lancamento LIKE '%PIX TRANSF EMANUEL%'
ORDER BY data
LIMIT 5;
"
