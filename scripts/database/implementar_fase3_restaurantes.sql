-- ========================================
-- FASE 3: RESTAURANTES E CAFETERIAS
-- Data: 12/02/2026
-- Objetivo: Adicionar keywords de fast-food, restaurantes e cafeterias
-- Impacto esperado: +5-10% cobertura em faturas
-- ========================================

-- 1. FAST FOOD (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Fast Food',
    'MCDONALDS,MC DONALDS,ARCOS DOURADOS,BURGER KING,BK,ZAMP,SUBWAY,KFC,POPEYES,HABIB,HABIBS,GIRAFFAS,MADERO,JERONIMO,BULLGUER,CABANA BURGER,Z DELI,PAO COM CARNE',
    'Entretenimento',
    'Saídas',
    'Despesa',
    50,
    1
);

-- 2. CAFETERIAS (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Cafeterias',
    'STARBUCKS,THE COFFEE,KOPENHAGEN,BRASIL CACAU,BACIO DI LATTE,BACIO,CARLOS BAKERY,WE COFFEE,COFFEE LAB,COFFEE SHOP',
    'Entretenimento',
    'Saídas',
    'Despesa',
    50,
    1
);

-- 3. RESTAURANTES CASUAL (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Restaurantes Casual',
    'OUTBACK,APPLEBEES,APPLEBEE,OLIVE GARDEN,TGIF,PF CHANGS,COCO BAMBU,FOGO DE CHAO,NB STEAK,PARIS 6,L ENTRECOTE,ENTRECOTE',
    'Entretenimento',
    'Saídas',
    'Despesa',
    50,
    1
);

-- 4. PIZZARIAS E ITALIANOS (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Pizzarias e Italianos',
    'BRAZ PIZZARIA,SPERANZA,CAMELO,1900 PIZZARIA,FAMIGLIA MANCINI,MANCINI,SPOLETO,ABBRACCIO,BELLA PAULISTA,DONA DEOLA',
    'Entretenimento',
    'Saídas',
    'Despesa',
    50,
    1
);

-- 5. AÇAÍ E FRUTAS (Nova regra)
INSERT INTO generic_classification_rules (
    nome_regra,
    keywords,
    grupo,
    subgrupo,
    tipo_gasto,
    prioridade,
    ativo
) VALUES (
    'Açaí e Frutas',
    'OAKBERRY,OAK BERRY,FRUTARIA,FRUTARIA SP,MERCADAO,MERCADAO DE SAO PAULO,EATALY',
    'Entretenimento',
    'Saídas',
    'Despesa',
    50,
    1
);

-- ========================================
-- RESUMO:
-- - 5 novas regras criadas
-- - ~60+ keywords adicionadas
-- - Foco: Restaurantes, fast-food, cafeterias
-- ========================================

-- Verificar resultados:
SELECT 
    COUNT(*) as total_regras,
    SUM(CASE WHEN ativo = 1 THEN 1 ELSE 0 END) as ativas
FROM generic_classification_rules;

-- Ver novas regras criadas:
SELECT id, keywords, grupo, subgrupo, prioridade
FROM generic_classification_rules
WHERE grupo = 'Entretenimento' AND subgrupo = 'Saídas'
ORDER BY id DESC
LIMIT 10;
