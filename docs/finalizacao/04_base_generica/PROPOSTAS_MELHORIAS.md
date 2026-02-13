# 📝 Propostas de Melhorias - Base Genérica

**Data:** 12/02/2026  
**Baseado em:** Análise de 2631 transações reais (journal_entries user_id=1)  
**Objetivo:** Aumentar cobertura de 45% → 70%+

---

## 🎯 Resumo Executivo

**Total de propostas:** 32 melhorias  
**Impacto estimado:** +25 pontos percentuais de cobertura  
**Prioridade:** Focar em 10 correções críticas primeiro (80% do impacto)

---

## 🔴 CRÍTICAS - Implementar IMEDIATAMENTE (10 propostas)

### 1. Corrigir Uber - Variações com Asterisco
**Problema:** 227 transações não cobertas  
**Impacto:** +8.6% de cobertura

**Ação:** Atualizar regra #23
```sql
UPDATE generic_classification_rules
SET keywords = 'UBER,UBER*,UBER *,UBER   *,CABIFY,TAXI'
WHERE id = 23;
```

---

### 2. Corrigir ConectCar - Typo na Keyword
**Problema:** 178 transações não cobertas  
**Impacto:** +6.8% de cobertura

**Ação:** Atualizar regra #21
```sql
UPDATE generic_classification_rules
SET keywords = 'SEM PARAR,CONNECTCAR,CONECTCAR,PEDAGIO'
WHERE id = 21;
```

---

### 3. Adicionar IOF - Nova Categoria
**Problema:** 40 transações não cobertas  
**Impacto:** +1.5% de cobertura

**Ação:** Criar nova regra
```sql
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
```

---

### 4. Adicionar Apple.com/bill - Assinaturas Apple
**Problema:** 36 transações não cobertas  
**Impacto:** +1.4% de cobertura

**Ação:** Criar nova regra (prioridade ALTA para não conflitar com Tecnologia)
```sql
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
```

**⚠️ ATENÇÃO:** Baixar prioridade da regra #39 (Tecnologia - Apple) de 7 para 6
```sql
UPDATE generic_classification_rules
SET prioridade = 6
WHERE id = 39;
```

---

### 5. Adicionar Vendify/IFD* - Delivery
**Problema:** 57 transações não cobertas  
**Impacto:** +2.2% de cobertura

**Ação:** Atualizar regra #17
```sql
UPDATE generic_classification_rules
SET keywords = 'IFD,IFD*,IFOOD,IFOOD*,UBER EATS,RAPPI,DELIVERY,ENTREGA,VENDIFY,VFY COMERCIO'
WHERE id = 17;
```

---

### 6. Adicionar Atacadista - Supermercado
**Problema:** 34 transações não cobertas  
**Impacto:** +1.3% de cobertura

**Ação:** Atualizar regra #18
```sql
UPDATE generic_classification_rules
SET keywords = 'SUPERMERCADO,MERCADO,EXTRA,CARREFOUR,PAO DE ACUCAR,PAODEACUCAR,WALMART,ATACADAO,ASSAI,MAKRO,ATACADISTA'
WHERE id = 18;
```

---

### 7. Adicionar Spotify - Variações
**Problema:** 16 transações não cobertas  
**Impacto:** +0.6% de cobertura

**Ação:** Atualizar regra #26
```sql
UPDATE generic_classification_rules
SET keywords = 'SPOTIFY,EBN*SPOTIFY,SPOTIFY*'
WHERE id = 26;
```

---

### 8. Adicionar Mensagem Cartão - Nova Categoria
**Problema:** 16 transações não cobertas  
**Impacto:** +0.6% de cobertura

**Ação:** Criar nova regra
```sql
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
```

---

### 9. Adicionar Amazon Prime BR - Variação
**Problema:** 14 transações não cobertas  
**Impacto:** +0.5% de cobertura

**Ação:** Atualizar regra #28
```sql
UPDATE generic_classification_rules
SET keywords = 'AMAZON PRIME,AMAZONPRIMEBR,PRIME VIDEO'
WHERE id = 28;
```

---

### 10. Adicionar Conta Vivo - Casa
**Problema:** 45 transações não cobertas  
**Impacto:** +1.7% de cobertura

**Ação:** Atualizar regras #7 e #8
```sql
UPDATE generic_classification_rules
SET keywords = 'CLARO,VIVO,TIM,OI,TELEFONE,CELULAR,TELEFONIA,CONTA VIVO'
WHERE id = 7;

UPDATE generic_classification_rules
SET keywords = 'NET,CLARO NET,VIVO FIBRA,OI FIBRA,INTERNET,BANDA LARGA,FIBRA OTICA,CONTA VIVO'
WHERE id = 8;
```

**⚠️ PROBLEMA:** Ambiguidade - `CONTA VIVO` pode ser celular ou internet  
**Solução:** Criar 2 regras mais específicas
```sql
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES 
(
    'Casa - Celular Vivo',
    'Conta de celular Vivo',
    'CONTA VIVO CEL,VIVO CELULAR',
    'Casa',
    'Celular',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
),
(
    'Casa - Internet Vivo',
    'Conta de internet Vivo',
    'CONTA VIVO INT,VIVO INTERNET,CONTA VIVO FIBRA',
    'Casa',
    'Internet',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
);
```

---

## 🟡 IMPORTANTES - Implementar em Fase 2 (12 propostas)

### 11. TEM BICI - Transporte
**Problema:** 10 transações não cobertas  
**Impacto:** +0.4% de cobertura

**Ação:** Criar nova regra
```sql
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
```

---

### 12. Folha de SP - Assinaturas
**Problema:** 12 transações não cobertas  
**Impacto:** +0.5% de cobertura

**Ação:** Criar nova regra
```sql
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - Folha de SP',
    'Assinatura jornal Folha de S.Paulo',
    'FOLHADESPAULO,FOLHA DE SP,FOLHA SP,PAG*FOLHADESPAULO',
    'Assinaturas',
    'Folha de SP',
    'Ajustável',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);
```

---

### 13. Produtos Globo - Premiere
**Problema:** 7 transações não cobertas  
**Impacto:** +0.3% de cobertura

**Ação:** Atualizar regra #30
```sql
UPDATE generic_classification_rules
SET keywords = 'PREMIERE,PRODUTOS GLOBO'
WHERE id = 30;
```

---

### 14. R&R Estacionamentos
**Problema:** 8 transações não cobertas  
**Impacto:** +0.3% de cobertura

**Ação:** Atualizar regra #36
```sql
UPDATE generic_classification_rules
SET keywords = 'ESTACIONAMENTO,PARKING,VAGA,ZONA AZUL,R&R,R & R'
WHERE id = 36;
```

---

### 15. Rendimentos Investimentos - Variações
**Problema:** 59 transações não cobertas (REND PAGO APLIC)  
**Impacto:** +2.2% de cobertura

**Ação:** Atualizar regra #51
```sql
UPDATE generic_classification_rules
SET keywords = 'FUNDO DE INVESTIMENTO,APLICACAO EM FUNDO,APLICACAO AUTOMATICA,REMUNERACAO APLICACAO,REND PAGO APLIC,RENDIMENTOS'
WHERE id = 51;
```

---

### 16. Fundos Imobiliários - Variações
**Problema:** 8 transações não cobertas (PAG TIT INT)  
**Impacto:** +0.3% de cobertura

**Ação:** Atualizar regra #54
```sql
UPDATE generic_classification_rules
SET keywords = 'FII,FUNDO IMOBILIARIO,QUATA EMP,PAG TIT INT'
WHERE id = 54;
```

---

### 17. Sodexo - Alimentação Almoço
**Problema:** 6 transações não cobertas  
**Impacto:** +0.2% de cobertura

**Ação:** Atualizar regra #43
```sql
UPDATE generic_classification_rules
SET keywords = 'ALMOCO,REFEICAO,MARMITA,SODEXO,TICKET,VR,VA'
WHERE id = 43;
```

---

### 18. Salário - TED/Pix Específico
**Problema:** Salário sem palavras-chave genéricas  
**Impacto:** +2.2% de cobertura (57 ocorrências)

**Ação:** Criar nova regra
```sql
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Salário - Recebimentos',
    'Recebimento de salário',
    'LIQUIDO DE VENCIMENTO,TED RECEBIDA SALARIO,PIX RECEBIDO SALARIO,SALARIO,VENCIMENTO SALARIO',
    'Salário',
    'Salário',
    'Salário',
    9,
    1,
    0,
    0,
    datetime('now'),
    1
);
```

---

### 19. MeLi - Pagamento Assinatura
**Problema:** 12 transações sem match específico  
**Impacto:** +0.5% de cobertura

**Ação:** Criar nova regra
```sql
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Assinaturas - MeLi+',
    'Assinatura Mercado Livre Plus',
    'PAGAMENTO DE ASSINATURA MELI,MELI+,MELI PLUS',
    'Assinaturas',
    'MeLi+',
    'Ajustável',
    8,
    1,
    0,
    0,
    datetime('now'),
    1
);
```

---

### 20. Care Plus - Reembolso Saúde
**Problema:** 6 transações sem categoria  
**Impacto:** +0.2% de cobertura

**Ação:** Criar nova regra
```sql
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES (
    'Saúde - Reembolso',
    'Reembolso plano de saúde',
    'SISPAG CARE,CARE PLUS,REEMBOLSO SAUDE,PLANO DE SAUDE',
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
```

---

### 21. Disney+ - Assinatura
**Problema:** 9 transações específicas  
**Impacto:** +0.3% de cobertura

**Ação:** Atualizar regra #25
```sql
UPDATE generic_classification_rules
SET keywords = 'DISNEY PLUS,DISNEY+,PAGAMENTO DE ASSINATURA THE WALT DISNEY'
WHERE id = 25;
```

---

### 22. Condomínio - Pagamento Itaú
**Problema:** 6 transações específicas  
**Impacto:** +0.2% de cobertura

**Ação:** Atualizar regra #6
```sql
UPDATE generic_classification_rules
SET keywords = 'CONDOMINIO,PAGAMENTO DE CONTAS ITAU CONDOMINIO'
WHERE id = 6;
```

---

## 🟢 OPCIONAIS - Implementar se Sobrar Tempo (10 propostas)

### 23-32. Estabelecimentos Específicos

Criar regras para estabelecimentos muito específicos do usuário (menor ROI para base genérica):

- Ezequiel Barbearia (10x) - já coberto por regra genérica
- Fatz Burger, Osnir, Outback, Le Jazz (restaurantes específicos)
- Lejazzboulangerie (padaria específica)
- YID (loja de roupas específica)

**Decisão:** ❌ NÃO incluir na base genérica (muito específicos)

---

## 📊 Impacto Total Estimado

### Fase 1 - Críticas (10 propostas)
```
Cobertura atual:     45%
+ Uber variações:    +8.6%
+ ConectCar fix:     +6.8%
+ Vendify/IFD:       +2.2%
+ Conta Vivo:        +1.7%
+ IOF:               +1.5%
+ Apple.com/bill:    +1.4%
+ Atacadista:        +1.3%
+ Spotify var:       +0.6%
+ Mensagem:          +0.6%
+ Amazon Prime BR:   +0.5%
──────────────────────────
Subtotal Fase 1:     70.2%
```

### Fase 2 - Importantes (12 propostas)
```
Cobertura Fase 1:    70.2%
+ Rendimentos:       +2.2%
+ Salário:           +2.2%
+ Outros (10):       +2.4%
──────────────────────────
TOTAL Fase 2:        76.8%
```

---

## 🎯 Plano de Implementação

### Sprint 1 (1-2 horas)
1. ✅ Implementar 10 correções críticas
2. ✅ Testar com script de validação
3. ✅ Medir cobertura real

### Sprint 2 (2-3 horas)
4. ✅ Implementar 12 melhorias importantes
5. ✅ Refinar keywords baseado em testes
6. ✅ Validar com múltiplas faturas

### Sprint 3 (1 hora)
7. ✅ Ajustes finos de prioridades
8. ✅ Documentação final
9. ✅ Deploy em produção

---

## 📝 Script SQL Completo - Fase 1

```sql
-- 1. Uber variações
UPDATE generic_classification_rules
SET keywords = 'UBER,UBER*,UBER *,UBER   *,CABIFY,TAXI'
WHERE id = 23;

-- 2. ConectCar fix typo
UPDATE generic_classification_rules
SET keywords = 'SEM PARAR,CONNECTCAR,CONECTCAR,PEDAGIO'
WHERE id = 21;

-- 3. IOF
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

-- 4. Apple.com/bill (alta prioridade)
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

-- 5. Vendify/IFD*
UPDATE generic_classification_rules
SET keywords = 'IFD,IFD*,IFOOD,IFOOD*,UBER EATS,RAPPI,DELIVERY,ENTREGA,VENDIFY,VFY COMERCIO'
WHERE id = 17;

-- 6. Atacadista
UPDATE generic_classification_rules
SET keywords = 'SUPERMERCADO,MERCADO,EXTRA,CARREFOUR,PAO DE ACUCAR,PAODEACUCAR,WALMART,ATACADAO,ASSAI,MAKRO,ATACADISTA'
WHERE id = 18;

-- 7. Spotify variações
UPDATE generic_classification_rules
SET keywords = 'SPOTIFY,EBN*SPOTIFY,SPOTIFY*'
WHERE id = 26;

-- 8. Mensagem Cartão
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

-- 9. Amazon Prime BR
UPDATE generic_classification_rules
SET keywords = 'AMAZON PRIME,AMAZONPRIMEBR,PRIME VIDEO'
WHERE id = 28;

-- 10. Conta Vivo (específicas)
INSERT INTO generic_classification_rules (
    nome_regra, descricao, keywords,
    grupo, subgrupo, tipo_gasto,
    prioridade, ativo, case_sensitive, match_completo,
    created_at, created_by
) VALUES 
(
    'Casa - Celular Vivo',
    'Conta de celular Vivo',
    'CONTA VIVO CEL,VIVO CELULAR',
    'Casa',
    'Celular',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
),
(
    'Casa - Internet Vivo',
    'Conta de internet Vivo',
    'CONTA VIVO INT,VIVO INTERNET,CONTA VIVO FIBRA',
    'Casa',
    'Internet',
    'Ajustável',
    10,
    1,
    0,
    0,
    datetime('now'),
    1
);

-- Verificar impacto
SELECT 'Fase 1 implementada - 10 melhorias críticas' as status;
```

---

**Próximo passo:** Criar script de teste para validar impacto real das melhorias
