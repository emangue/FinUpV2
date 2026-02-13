-- ========================================
-- FASE 4: SUPERMERCADOS E SAÚDE/FARMÁCIAS
-- Data: 12/02/2026
-- Objetivo: Adicionar keywords de supermercados e farmácias
-- Impacto esperado: +3-5% cobertura
-- ========================================

-- 1. SUPERMERCADOS GRANDES (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Supermercados',
    'CARREFOUR,CARREFOUR EXPRESS,PAO DE ACUCAR,GRUPO PAO DE ACUCAR,GPA,EXTRA,EXTRA SUPER,ASSAI,ATACADAO,SAMS CLUB,SAM CLUB,ZAFFARI,SONDA',
    'Casa',
    'Mercado',
    'Despesa',
    60,
    1
);

-- 2. CONVENIÊNCIA E MERCADOS MENORES (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Conveniência',
    'DIA BRASIL,DIA%,HIROTA,ST MARCHE,OXXO,CONVENIENCIA,NATURAL DA TERRA,HORTIFRUTI',
    'Casa',
    'Mercado',
    'Despesa',
    60,
    1
);

-- 3. FARMÁCIAS GRANDES REDES (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Farmácias',
    'DROGASIL,RD DRUGSTORE,DROGA RAIA,RAIA,DROGARIA SAO PAULO,DROGARIASP,DROGARIA ONOFRE,ONOFRE,PAGUE MENOS,ULTRAFARMA,BEIRA ALTA',
    'Saúde',
    'Farmácia',
    'Despesa',
    60,
    1
);

-- 4. LABORATÓRIOS E CLÍNICAS (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Laboratórios e Clínicas',
    'LABORATORIO FLEURY,FLEURY,DELBONI,A+ MEDICINA,NOTRE DAME,PREVENT SENIOR,LABORATORIO,CLINICA',
    'Saúde',
    'Saúde Geral',
    'Despesa',
    60,
    1
);

-- 5. FARMÁCIA SELETA (Específica - pode ser local)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Farmácia Seleta',
    'FARMACIA SELETA,SELETA',
    'Saúde',
    'Farmácia',
    'Despesa',
    60,
    1
);

-- ========================================
-- RESUMO:
-- - 5 novas regras criadas
-- - ~40+ keywords adicionadas
-- - Foco: Supermercados e Saúde
-- ========================================

-- Verificar resultados:
SELECT 
    COUNT(*) as total_regras,
    SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) as ativas
FROM generic_classification_rules;

-- Ver novas regras criadas:
SELECT id, nome_regra, keywords, grupo, subgrupo, prioridade
FROM generic_classification_rules
WHERE id > 81
ORDER BY id;
