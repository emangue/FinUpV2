-- =====================================================
-- Script de Correção do Banco de Dados
-- =====================================================
-- Data: 03/01/2026
-- Versão: 1.0.0
-- Descrição: Corrige problemas críticos identificados na auditoria
--
-- IMPORTANTE: FAÇA BACKUP ANTES DE EXECUTAR!
--   cp app/financas.db app/financas.db.backup_$(date +%Y%m%d_%H%M%S)
--
-- =====================================================

-- =====================================================
-- FASE 1: CORREÇÕES CRÍTICAS
-- =====================================================

BEGIN TRANSACTION;

-- 1.1. Corrigir Formato de Data (1,220 transações)
-- De: '2024-01-01 00:00:00' Para: '01/01/2024'
-- =====================================================
UPDATE journal_entries
SET Data = 
  substr(Data, 9, 2) || '/' ||  -- Dia (posições 9-10)
  substr(Data, 6, 2) || '/' ||  -- Mês (posições 6-7)
  substr(Data, 1, 4)            -- Ano (posições 1-4)
WHERE Data LIKE '____-__-__ __:__:__';

-- Verificação
SELECT 'Datas corrigidas:', COUNT(*) 
FROM journal_entries 
WHERE Data LIKE '__/__/____';

-- 1.2. Corrigir ValorPositivo (deve ser sempre >= 0)
-- =====================================================
UPDATE journal_entries
SET ValorPositivo = ABS(Valor)
WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01
   OR ValorPositivo < 0;

-- Verificação
SELECT 'ValorPositivo corrigidos:', COUNT(*) 
FROM journal_entries 
WHERE ValorPositivo = ABS(Valor);

-- 1.3. Recalcular Ano e DT_Fatura a partir de Data
-- =====================================================
UPDATE journal_entries
SET 
  Ano = CAST(substr(Data, 7, 4) AS INTEGER),
  DT_Fatura = substr(Data, 7, 4) || substr(Data, 4, 2)
WHERE Data LIKE '__/__/____';

-- Verificação
SELECT 'Ano/DT_Fatura recalculados:', COUNT(*) 
FROM journal_entries 
WHERE Ano IS NOT NULL AND DT_Fatura IS NOT NULL;

COMMIT;

-- =====================================================
-- FASE 2: PREENCHIMENTO DE TIPOGASTO
-- =====================================================

BEGIN TRANSACTION;

-- 2.1. Corrigir Capitalização Inconsistente
-- =====================================================
UPDATE journal_entries
SET GRUPO = 'Transferência Entre Contas'
WHERE GRUPO = 'Transferência entre contas';

-- 2.2. Corrigir TipoGasto Inválidos
-- =====================================================

-- 'Ajustável - Investimentos' → 'Investimentos - Ajustável'
UPDATE journal_entries 
SET TipoGasto = 'Investimentos - Ajustável'
WHERE TipoGasto = 'Ajustável - Investimentos';

-- 'Ignorar' → NULL + IgnorarDashboard = 1
UPDATE journal_entries 
SET TipoGasto = NULL, 
    IgnorarDashboard = 1
WHERE TipoGasto = 'Ignorar';

-- 'Ajustado' → 'Ajustável' (typo)
UPDATE journal_entries 
SET TipoGasto = 'Ajustável'
WHERE TipoGasto = 'Ajustado';

-- 2.3. Adicionar Combinações Faltantes em base_marcacoes
-- =====================================================

-- Casa + TV Sala
INSERT OR IGNORE INTO base_marcacoes (GRUPO, SUBGRUPO, TipoGasto)
VALUES ('Casa', 'TV Sala', 'Fixo');

-- Adicionar outras conforme necessário após revisão manual

-- 2.4. Backfill TipoGasto via base_marcacoes
-- =====================================================
UPDATE journal_entries
SET TipoGasto = (
    SELECT TipoGasto 
    FROM base_marcacoes
    WHERE base_marcacoes.GRUPO = journal_entries.GRUPO
      AND base_marcacoes.SUBGRUPO = journal_entries.SUBGRUPO
)
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO IS NOT NULL 
  AND SUBGRUPO IS NOT NULL
  AND EXISTS (
      SELECT 1 FROM base_marcacoes
      WHERE base_marcacoes.GRUPO = journal_entries.GRUPO
        AND base_marcacoes.SUBGRUPO = journal_entries.SUBGRUPO
  );

-- Verificação
SELECT 'TipoGasto preenchidos:', COUNT(*) 
FROM journal_entries 
WHERE TipoGasto IS NOT NULL;

COMMIT;

-- =====================================================
-- VERIFICAÇÕES FINAIS
-- =====================================================

-- Total de transações
SELECT 'Total de transações:', COUNT(*) FROM journal_entries;

-- Transações sem TipoGasto (deveria ser próximo de 0)
SELECT 'Sem TipoGasto:', COUNT(*) 
FROM journal_entries 
WHERE (TipoGasto IS NULL OR TipoGasto = '')
  AND GRUPO IS NOT NULL 
  AND SUBGRUPO IS NOT NULL;

-- Datas em formato incorreto (deveria ser 0)
SELECT 'Datas com formato incorreto:', COUNT(*) 
FROM journal_entries 
WHERE Data NOT LIKE '__/__/____';

-- ValorPositivo negativos ou incorretos (deveria ser 0)
SELECT 'ValorPositivo incorretos:', COUNT(*) 
FROM journal_entries 
WHERE ValorPositivo < 0 
   OR ABS(ABS(Valor) - ValorPositivo) > 0.01;

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================

-- Para executar:
-- sqlite3 app/financas.db < scripts/fix_database_issues.sql
