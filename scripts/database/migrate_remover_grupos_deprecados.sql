-- ============================================================================
-- MIGRAÇÃO: Remover/deprecar grupos Aplicações, Fatura, Movimentações
-- ============================================================================
-- Aplicações → Investimentos
-- Fatura → Transferência Entre Contas
-- Movimentações → DELETE (não usado)
-- ============================================================================

-- 1. journal_entries: Aplicações → Investimentos
UPDATE journal_entries 
SET GRUPO = 'Investimentos', CategoriaGeral = 'Investimentos' 
WHERE GRUPO = 'Aplicações';

-- 2. journal_entries: Fatura → Transferência Entre Contas
UPDATE journal_entries 
SET GRUPO = 'Transferência Entre Contas', CategoriaGeral = 'Transferência' 
WHERE GRUPO = 'Fatura';

-- 3. base_marcacoes: Fatura → Transferência Entre Contas
UPDATE base_marcacoes 
SET "GRUPO" = 'Transferência Entre Contas' 
WHERE "GRUPO" = 'Fatura';

-- 4. generic_classification_rules: Aplicações → Investimentos (grupo)
UPDATE generic_classification_rules 
SET grupo = 'Investimentos' 
WHERE grupo = 'Aplicações';

-- 5. generic_classification_rules: Fatura → Transferência Entre Contas
UPDATE generic_classification_rules 
SET grupo = 'Transferência Entre Contas' 
WHERE grupo = 'Fatura';

-- 6. budget_planning: Fatura → Transferência Entre Contas
UPDATE budget_planning 
SET grupo = 'Transferência Entre Contas' 
WHERE grupo = 'Fatura';

-- 7. budget_planning: Aplicações → Investimentos
UPDATE budget_planning 
SET grupo = 'Investimentos' 
WHERE grupo = 'Aplicações';

-- 8. DELETE grupos deprecados de base_grupos_config
DELETE FROM base_grupos_config WHERE nome_grupo = 'Movimentações';
DELETE FROM base_grupos_config WHERE nome_grupo = 'Aplicações';
DELETE FROM base_grupos_config WHERE nome_grupo = 'Fatura';

-- Validação
SELECT 'Migração concluída' as status;
SELECT COUNT(*) as grupos_restantes FROM base_grupos_config;
