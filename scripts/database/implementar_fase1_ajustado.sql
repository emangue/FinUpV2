-- FASE 1 - MELHORIAS CRÍTICAS (AJUSTADO baseado em feedback)
-- Data: 12/02/2026
-- Objetivo: Aumentar cobertura de 45% → 70%+

-- ============================================================================
-- 1. Uber - SIMPLIFICADO (já usa CONTAINS)
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'UBER,CABIFY,TAXI,99'
WHERE id = 23;

-- ============================================================================
-- 2. ConectCar - Corrigir typo + ambas variações
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'SEM PARAR,CONNECTCAR,CONECTCAR,CONECT CAR,PEDAGIO'
WHERE id = 21;

-- ============================================================================
-- 3. IOF - Nova categoria
-- ============================================================================
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords, 
    grupo, subgrupo, tipo_gasto, 
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Serviços - IOF',
    'Taxa IOF em compras internacionais',
    'IOF,IOF COMPRA,IOF INTERNAC',
    'Serviços',
    'IOF',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 4. Apple.com/bill - Assinaturas Apple (prioridade alta)
-- ============================================================================
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - Apple Serviços',
    'Cobranças Apple (iCloud, Music, etc)',
    'APPLE.COM/BILL,APPLE.COM',
    'Assinaturas',
    'Apple',
    'Ajustável',
    9,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- Baixar prioridade Apple Tecnologia
UPDATE generic_classification_rules
SET prioridade = 6
WHERE id = 39;

-- ============================================================================
-- 5. Vendify/IFD* - Delivery
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'IFD,IFOOD,UBER EATS,RAPPI,DELIVERY,ENTREGA,VENDIFY,VFY'
WHERE id = 17;

-- ============================================================================
-- 6. Atacadista - Supermercado
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'SUPERMERCADO,MERCADO,EXTRA,CARREFOUR,PAO DE ACUCAR,PAODEACUCAR,WALMART,ATACADAO,ASSAI,MAKRO,ATACADISTA'
WHERE id = 18;

-- ============================================================================
-- 7. Spotify - SIMPLIFICADO
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'SPOTIFY,EBN'
WHERE id = 26;

-- ============================================================================
-- 8. Mensagem Cartão - Nova categoria
-- ============================================================================
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - Mensagem Cartão',
    'Taxa de envio de mensagens automáticas do cartão',
    'ENVIO MENS,MENS AUTOMATICA,MENSAGEM AUTOMATICA,MENSAGEM CARTAO',
    'Assinaturas',
    'Mensagem Cartão',
    'Ajustável',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 9. Amazon Prime BR - SIMPLIFICADO
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'AMAZON PRIME,AMAZONPRIME,PRIME VIDEO'
WHERE id = 28;

-- ============================================================================
-- 10. Conta Vivo - Casa (ambiguidade celular/internet)
-- ============================================================================
-- Atualizar ambas as regras existentes para incluir "CONTA VIVO"
UPDATE generic_classification_rules
SET keywords = 'CLARO,VIVO,TIM,OI,TELEFONE,CELULAR,TELEFONIA,CONTA VIVO'
WHERE id = 7;

UPDATE generic_classification_rules
SET keywords = 'NET,CLARO NET,VIVO FIBRA,OI FIBRA,INTERNET,BANDA LARGA,FIBRA OTICA,CONTA VIVO'
WHERE id = 8;

-- ============================================================================
-- 11. Revistas e Jornais - Categoria genérica (NOVA - sugestão do usuário)
-- ============================================================================
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - Revistas e Jornais',
    'Assinaturas de jornais e revistas',
    'FOLHADESPAULO,FOLHA DE SP,FOLHA SP,PAG*FOLHADESPAULO,VALOR ECONOMICO,VEJA,TIME,EPOCA,EXAME,ESTADAO,ESTADO DE SP,GLOBO,O GLOBO',
    'Assinaturas',
    'Revistas e Jornais',
    'Ajustável',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 12. GloboPlay - Atualizar (sugestão do usuário)
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'PREMIERE,PRODUTOS GLOBO,GLOBOPLAY'
WHERE id = 30;

-- ============================================================================
-- 13. TEM BICI - Transporte
-- ============================================================================
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Transporte - Bike',
    'Serviços de bike compartilhada',
    'TEMBICI,TEM BICI,BIKE ITAU,BIKE COMPARTILHADA',
    'Transporte',
    'Bike',
    'Ajustável',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 14. R&R Estacionamentos
-- ============================================================================
UPDATE generic_classification_rules
SET keywords = 'ESTACIONAMENTO,PARKING,VAGA,ZONA AZUL,R&R,R & R'
WHERE id = 36;

-- ============================================================================
-- VALIDAÇÃO
-- ============================================================================
SELECT 'Fase 1 implementada - ' || COUNT(*) || ' regras ativas' as status
FROM generic_classification_rules
WHERE ativo = 1;
