-- =====================================================
-- Script de Correção - FASE 1 (Pontos 1 e 2)
-- =====================================================
-- Data: 03/01/2026
-- Descrição: Corrige formato de Data e ValorPositivo
--
-- IMPORTANTE: FAÇA BACKUP ANTES DE EXECUTAR!
--
-- =====================================================

BEGIN TRANSACTION;

-- =====================================================
-- PONTO 1: Corrigir Formato de Data (1,220 transações)
-- De: '2024-01-01 00:00:00' Para: '01/01/2024'
-- =====================================================

-- Contar antes
SELECT '=== ANTES DA CORREÇÃO ===' as status;
SELECT 'Datas com formato incorreto:', COUNT(*) 
FROM journal_entries 
WHERE Data LIKE '____-__-__ __:__:__';

-- Aplicar correção
UPDATE journal_entries
SET Data = 
  substr(Data, 9, 2) || '/' ||  -- Dia (posições 9-10)
  substr(Data, 6, 2) || '/' ||  -- Mês (posições 6-7)
  substr(Data, 1, 4)            -- Ano (posições 1-4)
WHERE Data LIKE '____-__-__ __:__:__';

-- Contar depois
SELECT '=== APÓS CORREÇÃO ===' as status;
SELECT 'Datas em formato correto (DD/MM/AAAA):', COUNT(*) 
FROM journal_entries 
WHERE Data LIKE '__/__/____';

SELECT 'Datas ainda incorretas:', COUNT(*) 
FROM journal_entries 
WHERE Data NOT LIKE '__/__/____';

-- =====================================================
-- PONTO 2: Corrigir ValorPositivo (7 transações)
-- =====================================================

-- Contar antes
SELECT '=== ANTES DA CORREÇÃO ===' as status;
SELECT 'ValorPositivo incorretos:', COUNT(*) 
FROM journal_entries 
WHERE ValorPositivo < 0 
   OR ABS(ABS(Valor) - ValorPositivo) > 0.01;

-- Mostrar exemplos antes
SELECT 'Exemplos de inconsistências:' as status;
SELECT id, Valor, ValorPositivo, 
       ABS(Valor) as 'ValorAbsoluto',
       ABS(ABS(Valor) - ValorPositivo) as 'Diferenca'
FROM journal_entries 
WHERE ValorPositivo < 0 
   OR ABS(ABS(Valor) - ValorPositivo) > 0.01
LIMIT 5;

-- Aplicar correção
UPDATE journal_entries
SET ValorPositivo = ABS(Valor)
WHERE ValorPositivo < 0 
   OR ABS(ABS(Valor) - ValorPositivo) > 0.01;

-- Contar depois
SELECT '=== APÓS CORREÇÃO ===' as status;
SELECT 'ValorPositivo corretos:', COUNT(*) 
FROM journal_entries 
WHERE ValorPositivo = ABS(Valor);

SELECT 'ValorPositivo ainda incorretos:', COUNT(*) 
FROM journal_entries 
WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01;

-- =====================================================
-- RESUMO FINAL
-- =====================================================

SELECT '=== RESUMO FINAL ===' as status;

SELECT 'Total de transações:' as metrica, COUNT(*) as valor
FROM journal_entries
UNION ALL
SELECT 'Datas corretas (DD/MM/AAAA):', COUNT(*)
FROM journal_entries WHERE Data LIKE '__/__/____'
UNION ALL
SELECT 'Datas incorretas:', COUNT(*)
FROM journal_entries WHERE Data NOT LIKE '__/__/____'
UNION ALL
SELECT 'ValorPositivo corretos:', COUNT(*)
FROM journal_entries WHERE ValorPositivo = ABS(Valor)
UNION ALL
SELECT 'ValorPositivo incorretos:', COUNT(*)
FROM journal_entries WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01;

COMMIT;

SELECT '✅ Correções aplicadas com sucesso!' as status;

-- Para executar:
-- sqlite3 app/financas.db < scripts/fix_fase1_data_valor.sql
