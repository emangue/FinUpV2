-- FASE 1B - AJUSTES CRÍTICOS DE ASSERTIVIDADE
-- Data: 12/02/2026
-- Objetivo: Aumentar assertividade de 35.5% → 60%+

-- ============================================================================
-- CRÍTICO 1: Separar ConectCar de "Sem Parar" (+20% assertividade)
-- Problema: 178 transações classificadas errado (ConnectCar → Sem Parar)
-- ============================================================================

-- Remover CONECTCAR/CONNECTCAR da regra "Sem Parar"
UPDATE generic_classification_rules
SET keywords = 'SEM PARAR,PEDAGIO'
WHERE id = 21;

-- Criar regra específica para ConnectCar (prioridade ALTA)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Carro - ConnectCar',
    'Aplicativo de pedágio ConnectCar',
    'CONECTCAR,CONNECTCAR,CONECT CAR',
    'Carro',
    'ConnectCar',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- CRÍTICO 2: Priorizar assinaturas específicas sobre genéricas (+5%)
-- Problema: MeLi+, Disney+, ConectCar pegam em categorias erradas
-- ============================================================================

-- 2.1: MeLi+ específico (prior 9 > MeLi genérico prior 7)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - MeLi Plus',
    'Assinatura Mercado Livre Plus',
    'PAGAMENTO DE ASSINATURA MELI,MELI+,MELI PLUS',
    'Assinaturas',
    'MeLi+',
    'Ajustável',
    9,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- 2.2: Disney+ específico (atualizar para pegar variações)
UPDATE generic_classification_rules
SET keywords = 'DISNEY PLUS,DISNEY+,PAGAMENTO DE ASSINATURA THE WALT DISNEY,WALT DISNEY',
    prioridade = 9
WHERE id = 25;

-- 2.3: ConectCar assinatura (diferente do pagamento de pedágio)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - ConectCar',
    'Mensalidade do app ConnectCar',
    'PAGAMENTO DE ASSINATURA CONECT',
    'Assinaturas',
    'ConectCar',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- 2.4: Amazon específico (prior 9 > Amazon genérico prior 7)
-- Já existe #41 com prior 7, aumentar para 8
UPDATE generic_classification_rules
SET prioridade = 8,
    keywords = 'AMAZON SERVICOS,AMZN,AMAZON.COM'
WHERE id = 41;

-- ============================================================================
-- CRÍTICO 3: Adicionar keywords específicas (+8%)
-- Problema: Transações comuns sem match
-- ============================================================================

-- 3.1: Seguro Cartão (11 transações)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - Seguro Cartão',
    'Seguro do cartão de crédito',
    'SEGURO CARTAO,SEGURO TC,SEGURO CREDIT',
    'Assinaturas',
    'Seguro TC',
    'Ajustável',
    9,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- 3.2: Sodexo (6 transações)
UPDATE generic_classification_rules
SET keywords = 'ALMOCO,REFEICAO,MARMITA,SODEXO,TICKET,VR,VA'
WHERE id = 43;

-- 3.3: Care Plus / Reembolso (6 transações)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Saúde - Reembolso',
    'Reembolso plano de saúde',
    'SISPAG CARE,CARE PLUS,REEMBOLSO SAUDE,PLANO DE SAUDE,REEMBOLSO',
    'Saúde',
    'Reembolso',
    'Fixo',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- 3.4: Pagamento de contas Itaú (condomínio, aluguel, energia)
-- Melhorar regras existentes para pegar "Pagamento de contas"
UPDATE generic_classification_rules
SET keywords = 'CONDOMINIO,PAGAMENTO DE CONTAS'
WHERE id = 6;

-- Energia
UPDATE generic_classification_rules
SET keywords = 'ELETROPAULO,ENEL,CPFL,CEMIG,COELBA,CELESC,ELEKTRO,LUZ,ENERGIA ELETRICA,PAGAMENTO DE CONTAS ITAU ENERGIA'
WHERE id = 4;

-- 3.5: Anuidade (estorno/diferenciado)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - Anuidade',
    'Anuidade de cartão de crédito',
    'ANUIDADE,ESTORNO DE ANUIDADE,ANUIDADE DIFERENC',
    'Assinaturas',
    'Anuidade',
    'Ajustável',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- 3.6: Pagamento genérico (ultrapasse, pendentes)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Carro - Aplicativos',
    'Pagamentos de apps de carro (ultrapasse, conectcar)',
    'PAGAMENTOS PENDENTES,ULTRAPASSE',
    'Carro',
    'Aplicativos',
    'Ajustável',
    7,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- 3.7: Transferências e dinheiro reservado (muitos casos)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Investimentos - Transferências',
    'Transferências para investimento',
    'DINHEIRO RETIRADO,DINHEIRO RESERVADO,RESERVA PROGRAMADA',
    'Investimentos',
    'Aplicações',
    'Investimentos',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- ============================================================================
-- VALIDAÇÃO
-- ============================================================================
SELECT 'Fase 1B implementada - ' || COUNT(*) || ' regras ativas' as status
FROM generic_classification_rules
WHERE ativo = 1;
