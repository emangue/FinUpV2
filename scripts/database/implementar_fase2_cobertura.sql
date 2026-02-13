-- FASE 2 - MELHORIAS DE COBERTURA
-- Data: 12/02/2026
-- Objetivo: Cobrir mais casos sem match (+3-4% assertividade)

-- ============================================================================
-- 1. BARES E RESTAURANTES - 32 transações descobertas
-- ============================================================================

-- Atualizar regra de Entretenimento para pegar mais casos
UPDATE generic_classification_rules
SET keywords = 'BAR,PUB,BALADA,BOATE,DISCOTECA,BOULANGERIE,BURGER,EMPORIO,FRIGORIFICO,LANCHONETE,PIZZARIA,SORVETERIA,CAFE,CAFETERIA,EVENTOS'
WHERE id = 10;

-- ============================================================================
-- 2. SEGUROS DE VIAGEM - 12 transações (Allianz)
-- ============================================================================

INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Viagens - Seguros',
    'Seguros de viagem',
    'ALLIANZ TRAVEL,SEGURO VIAGEM,TRAVEL INSURANCE,ASSIST CARD',
    'Viagens',
    'Seguros',
    'Viagens',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 3. MARCAS DE ROUPA - 5 transações (Adidas, Toucan Brasil)
-- ============================================================================

-- Criar regra para marcas de roupa conhecidas
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Roupas - Marcas',
    'Marcas de roupa e calçados',
    'ADIDAS,NIKE,PUMA,ZARA,H&M,C&A,RENNER,RIACHUELO,TOUCAN BRASIL,TOLLE',
    'Roupas',
    'Roupas',
    'Ajustável',
    7,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 4. AJUSTE CRÍTICO: "Pagamento de assinatura" não está pegando
-- Verificar se prioridade da regra ConectCar está suficiente
-- ============================================================================

-- Aumentar prioridade da regra de assinatura ConectCar
UPDATE generic_classification_rules
SET prioridade = 10,
    keywords = 'PAGAMENTO DE ASSINATURA CONECT,ASSINATURA CONECT'
WHERE nome_regra = 'Assinaturas - ConectCar';

-- ============================================================================
-- 5. AMAZON BR específico (Casa > Ferramentas)
-- ============================================================================

-- Criar regra específica para Amazon.br (compras gerais)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Casa - Amazon BR',
    'Compras gerais na Amazon Brasil',
    'AMAZON BR,AMAZON.COM.BR',
    'Casa',
    'Ferramentas',
    'Ajustável',
    6,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 6. KLASS WAGEN (Aluguel de carro em viagens)
-- ============================================================================

INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Viagens - Aluguel de Carro',
    'Aluguel de carro em viagens',
    'KLASS WAGEN,LOCALIZA,MOVIDA,HERTZ,AVIS,BUDGET,RENTACAR',
    'Viagens',
    'Aluguel de Carro',
    'Viagens',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 7. RASCAL (Entretenimento > Casamento)
-- Casos muito específicos - criar regra genérica de eventos
-- ============================================================================

INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Entretenimento - Eventos',
    'Eventos e festas',
    'RASCAL,BUFFET,FESTA,EVENTO,CASAMENTO,FORMATURA',
    'Entretenimento',
    'Eventos',
    'Ajustável',
    7,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- 8. MACYS (Loja de departamento em viagens)
-- ============================================================================

INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Viagens - Compras',
    'Compras em viagens (lojas internacionais)',
    'MACYS,TARGET,WALMART,BEST BUY,COSTCO',
    'Viagens',
    'Compras',
    'Viagens',
    7,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- VALIDAÇÃO
-- ============================================================================
SELECT 'Fase 2 implementada - ' || COUNT(*) || ' regras ativas' as status
FROM generic_classification_rules
WHERE ativo = 1;
