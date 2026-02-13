# ✅ Validação - 55 Regras Genéricas Atuais

**Data:** 12/02/2026  
**Status:** Auditoria completa das regras existentes

---

## 📊 Resumo Geral

- **Total de regras ativas:** 55
- **Grupos cobertos:** 13
- **Média de keywords por regra:** 4-6
- **Prioridades:** 5-10 (quanto maior, mais prioritário)

---

## 🗂️ Regras por Grupo

### 🍽️ Alimentação (4 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 43 | Almoço | ALMOCO, REFEICAO, MARMITA | Almoço | 7 | ⚠️ Falta PRATO FEITO, PF |
| 42 | Café da Manhã | CAFE DA MANHA, PADARIA, CONFEITARIA | Café da Manhã | 7 | ✅ OK |
| 17 | Pedidos para casa | IFD, IFOOD, UBER EATS, RAPPI, DELIVERY, ENTREGA | Delivery | 8 | ⚠️ Falta IFD*, VENDIFY |
| 18 | Supermercado | SUPERMERCADO, MERCADO, EXTRA, CARREFOUR, PAO DE ACUCAR, PAODEACUCAR, WALMART, ATACADAO, ASSAI, MAKRO | Supermercado | 8 | ⚠️ Falta ATACADISTA |

**Problemas identificados:**
- ❌ Não cobre `Vendify   Cond Lodz` (31x no journal)
- ❌ Não cobre `SAO JORGE ATACADISTA` (34x no journal)
- ❌ Keywords IFOOD não pegam variação `IFD*` (26x no journal)

---

### 📱 Assinaturas (9 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 28 | Amazon Prime | AMAZON PRIME, PRIME VIDEO | Amazon Prime | 8 | ⚠️ Falta AMAZONPRIMEBR |
| 31 | Audible | AUDIBLE | Audible | 8 | ✅ OK |
| 29 | ICloud | ICLOUD, APPLE CLOUD | ICloud | 8 | ✅ OK |
| 24 | Outros | NETFLIX, HBO, PARAMOUNT, GLOBOPLAY, STREAMING | Outros | 8 | ⚠️ Falta PRODUTOS GLOBO |
| 25 | Outros | DISNEY PLUS, DISNEY+ | Outros | 8 | ✅ OK |
| 30 | Premiere | PREMIERE | Premiere | 8 | ⚠️ Falta PRODUTOS GLOBO |
| 26 | Spotify | SPOTIFY | Spotify | 8 | ⚠️ Falta EBN*SPOTIFY |
| 27 | Youtube | YOUTUBE PREMIUM, YOUTUBE | Youtube | 8 | ✅ OK |

**Problemas identificados:**
- ❌ Não cobre `Apple.com/bill` (36x no journal)
- ❌ Não cobre `EBN*SPOTIFY` (16x no journal)
- ❌ Não cobre `Amazonprimebr` (14x no journal)
- ❌ Não cobre `PRODUTOS GLOBO` (7x no journal)
- ❌ Não cobre `TEMBICI` (10x no journal)
- ❌ Não cobre `ENVIO MENS.AUTOMATICA` (16x no journal)
- ❌ Falta subgrupo "Mensagem Cartão"
- ❌ Falta subgrupo "Folha de SP" (12x no journal)

---

### 🚗 Carro (6 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 19 | Abastecimento | POSTO, GASOLINA, ALCOOL, ETANOL, COMBUSTIVEL, SHELL, IPIRANGA, BR PETROBRAS, ALE, ABASTECIMENTO | Abastecimento | 8 | ✅ OK |
| 36 | Estacionamento | ESTACIONAMENTO, PARKING, VAGA, ZONA AZUL | Estacionamento | 7 | ⚠️ Falta R&R |
| 11 | IPVA + Licenciamento | IPVA, LICENCIAMENTO | IPVA + Licenciamento | 9 | ✅ OK |
| 20 | Limpeza | DRYWASH, LAVA RAPIDO, LAVAGEM, LAVA JATO, CAR WASH, ESTETICA AUTOMOTIVA | Limpeza | 8 | ✅ OK |
| 22 | Seguro | SEGURO CARRO, SEGURO AUTO, PORTO SEGURO AUTO | Seguro | 8 | ✅ OK |
| 21 | Sem Parar | SEM PARAR, CONNECTCAR, CONNETCAR, PEDAGIO | Sem Parar | 8 | ⚠️ Typo: CONNETCAR (1 N) |

**Problemas identificados:**
- ❌ Não cobre `Pagamento CONECTCAR` (178x no journal) - typo na keyword
- ❌ Não cobre `R&R ESTACIONAMENTOS` (8x no journal)
- ⚠️ Subgrupo "Sem Parar" deveria ser "Aplicativos"?

---

### 🏠 Casa (6 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 7 | Celular | CLARO, VIVO, TIM, OI, TELEFONE, CELULAR, TELEFONIA | Celular | 9 | ⚠️ Falta CONTA VIVO |
| 6 | Condomínio | CONDOMINIO | Condomínio | 9 | ✅ OK |
| 4 | Energia | ELETROPAULO, ENEL, CPFL, CEMIG, COELBA, CELESC, ELEKTRO, LUZ, ENERGIA ELETRICA | Energia | 9 | ✅ OK |
| 9 | Gás | GAS, COMGAS, ULTRAGAZ, LIQUIGAS, SUPERGASBRASS | Gás | 9 | ✅ OK |
| 8 | Internet | NET, CLARO NET, VIVO FIBRA, OI FIBRA, INTERNET, BANDA LARGA, FIBRA OTICA | Internet | 9 | ⚠️ Falta CONTA VIVO |
| 5 | Água | SABESP, SANEPAR, CAESB, CEDAE, COPASA, AGUA, SANEAMENTO | Água | 9 | ✅ OK |

**Problemas identificados:**
- ❌ Não cobre `CONTA VIVO` (23x celular + 22x internet)

---

### 📚 Educação (1 regra)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 32 | Cervantes | ESCOLA, FACULDADE, UNIVERSIDADE, CURSO, COLEGIO, ENSINO, MENSALIDADE, CERVANTES, PREPLY | Cervantes | 8 | ⚠️ Muito genérico para Tipo "Fixo" |

**Problemas identificados:**
- ⚠️ Subgrupo "Cervantes" muito específico - deveria ser "Cursos"?
- ⚠️ Tipo "Fixo" inadequado para keywords genéricas (ESCOLA, CURSO, etc.)

---

### 🎉 Entretenimento (4 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 45 | Cinema | CINEMA, CINEMARK, INGRESSO, FILME | Cinema | 6 | ✅ OK |
| 47 | Corrida | CORRIDA, MARATONA, PROVA | Corrida | 6 | ✅ OK |
| 10 | Saídas | PIZZ, PIZZA, PIZZARIA, RESTAUR, ADEGA, BAR, PUB, LANCHE, HAMBURGER, BURGUER, CHURRASCARIA, BOTECO, CAFETERIA, FESTA, DOCERIA, CONFEITARIA, PADARIA | Saídas | 9 | ✅ Boa cobertura |
| 46 | Shows | SHOW, CONCERTO, APRESENTACAO | Shows | 6 | ✅ OK |

**Status:** ✅ Grupo bem coberto

---

### 💰 Investimentos (7 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 55 | Aplicações | CONTA INVESTIMENTO, TRANSFERENCIA ENVIADA PARA CONTA INVESTIMENTO | Aplicações | 9 | ✅ OK |
| 53 | Ações | ACAO, ACOES, B3, BOVESPA, BOLSA DE VALORES, LIQUIDO DE VENCIMENTOS-RV | Ações | 9 | ✅ OK |
| 52 | Criptomoedas | BITCOIN, BTC, ETHEREUM, ETH, CRIPTO, MERCADO COIN, MCN | Criptomoedas | 9 | ✅ OK |
| 51 | Fundos | FUNDO DE INVESTIMENTO, APLICACAO EM FUNDO, APLICACAO AUTOMATICA, REMUNERACAO APLICACAO | Fundos | 9 | ⚠️ Falta REND PAGO APLIC |
| 54 | Fundos Imobiliários | FII, FUNDO IMOBILIARIO, QUATA EMP | Fundos Imobiliários | 9 | ⚠️ Falta PAG TIT INT |
| 50 | Renda Fixa | CDB, LCI, LCA, RENDA FIXA, VENCIMENTO DE LCA, VENCIMENTO DE LCI | Renda Fixa | 9 | ✅ OK |
| 49 | Tesouro Direto | TESOURO DIRETO, TESOURO SELIC, TESOURO IPCA, TESOURO PREFIXADO | Tesouro Direto | 9 | ✅ OK |

**Problemas identificados:**
- ❌ Não cobre `REND PAGO APLIC AUT MAIS` (59x no journal)
- ❌ Não cobre `PAG TIT INT 358549389000` (8x no journal)

---

### 🧹 Limpeza (1 regra)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 2 | Casa | DIARISTA, FAXINA, LIMPEZA CASA | Casa | 10 | ✅ OK |

**Status:** ✅ Bem específico

---

### 🛒 MeLi + Amazon (2 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 40 | MeLi + Amazon | MERCADO LIVRE, MERCADOLIVRE, MELI, ML | MeLi + Amazon | 7 | ✅ OK |
| 41 | MeLi + Amazon | AMAZON, AMZN | MeLi + Amazon | 7 | ⚠️ Conflito com #28 (Amazon Prime)? |

**Problemas identificados:**
- ⚠️ Possível conflito de prioridades: Amazon genérico (7) vs Amazon Prime (8)

---

### 👕 Roupas (2 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 3 | Roupas | NETSHOES | Roupas | 10 | ⚠️ Muito específico para prior 10 |
| 34 | Roupas | TECIDO, TECIDOS, CONFEC, MALHARIA, MODA, VESTUARIO, ROUPA, CALCADO, SAPATO, BOUTIQUE | Roupas | 8 | ✅ Boa cobertura |

**Status:** ✅ OK

---

### 🏥 Saúde (6 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 37 | Crossfit | ACADEMIA, CROSSFIT, FUNCIONAL, GYMPASS | Crossfit | 7 | ⚠️ Subgrupo deveria ser "Academia"? |
| 15 | Dentista | DENTISTA, ODONTO, ORTODONTIA | Dentista | 8 | ✅ OK |
| 14 | Farmácia | FARMACIA, DROGARIA, DROGA, DROGASIL, PACHECO, PANVEL, ULTRAFARMA, PAGUE MENOS | Farmácia | 8 | ✅ OK |
| 38 | Padel | PADEL | Padel | 7 | ⚠️ Muito específico |
| 16 | Terapia | TERAPIA, PSICOLOGO, PSIQUIATRA, TERAPEUTA | Terapia | 8 | ✅ OK |

**Problemas identificados:**
- ⚠️ Subgrupo "Crossfit" e "Padel" muito específicos - deveriam ser "Academia"?

---

### 🔧 Serviços (2 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 1 | Cabeleireiro | CABELEIREIRO, SALAO, BARBEARIA, BARBEIRO | Cabeleireiro | 10 | ✅ OK |
| 44 | Lavanderia | LAVANDERIA, LAVAR ROUPA, LAVAGEM ROUPA | Lavanderia | 7 | ✅ OK |

**Problemas identificados:**
- ❌ Não cobre `Iof Compra Internaciona` (40x no journal)
- ❌ Falta subgrupo "IOF"

---

### 💻 Tecnologia (1 regra)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 39 | Outros | APPLE, MICROSOFT, GOOGLE PLAY, APP STORE, SOFTWARE | Outros | 7 | ⚠️ APPLE conflita com Assinaturas? |

**Problemas identificados:**
- ⚠️ APPLE pode causar match errado (deveria priorizar `Apple.com/bill` para Assinaturas)

---

### 🚇 Transporte (3 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 35 | Bilhete Único | BILHETE UNICO, METRO, ONIBUS, CPTM, TRANSPORTE PUBLICO | Bilhete Único | 7 | ✅ OK |
| 23 | Uber | UBER, CABIFY, TAXI | Uber | 8 | ⚠️ Não pega UBER*, UBER   * |
| 48 | Uber | 99 | Uber | 5 | ✅ OK (separado) |

**Problemas identificados:**
- ❌ Não cobre `UBER* TRIP` (138x no journal)
- ❌ Não cobre `UBER * PENDING` (45x no journal)
- ❌ Não cobre `UBER   *UBER   *TRIP` (44x no journal)

---

### ✈️ Viagens (3 regras)

| ID | Nome | Keywords | Subgrupo | Prior | Observações |
|----|------|----------|----------|-------|-------------|
| 12 | Outros | LATAM, GOL, AZUL, AVIANCA, CIA AEREA, PASSAGEM AEREA, VOO, AEROPORTO | Outros | 9 | ✅ OK |
| 13 | Outros | HOTEL, POUSADA, AIRBNB, BOOKING, HOSPEDAGEM, RESORT, HOSTEL, ALBERGUE | Outros | 9 | ✅ OK |
| 33 | Outros | DECOLAR, MAXMILHAS, TURISMO, AGENCIA, CVC | Outros | 8 | ✅ OK |

**Status:** ✅ Boa cobertura

---

## 📊 Análise de Problemas

### 🔴 Críticos (Bloqueantes - Alta frequência)

1. **Uber com asterisco** - 227x sem cobertura
   - `UBER* TRIP` (138x), `UBER * PENDING` (45x), `UBER   *` (44x)
   
2. **ConectCar com typo** - 178x sem cobertura
   - `Pagamento CONECTCAR` não match com `CONNETCAR` (1 N)

3. **Apple.com/bill** - 36x sem cobertura
   - Não match com `APPLE` (conflita com Tecnologia)

4. **Vendify/IFD*** - 57x sem cobertura
   - `Vendify   Cond Lodz` (31x), `VFY COMERCIO` (26x)

5. **Atacadista** - 34x sem cobertura
   - `SAO JORGE ATACADISTA` não match com keywords atuais

### 🟡 Importantes (Médio impacto)

6. **Conta Vivo** - 45x sem cobertura
   - Não match com keywords atuais (VIVO genérico)

7. **IOF** - 40x sem cobertura
   - Categoria inexistente

8. **Spotify variações** - 16x sem cobertura
   - `EBN*SPOTIFY` não match

9. **Mensagem Cartão** - 16x sem cobertura
   - Subgrupo inexistente

10. **Amazon Prime BR** - 14x sem cobertura
    - `Amazonprimebr` não match

### 🟢 Menores (Baixo impacto mas fáceis de resolver)

11. **Estacionamento R&R** - 8x
12. **Produtos Globo** - 7x
13. **TEM BICI** - 10x
14. **Folha de SP variações** - 12x

---

## 📈 Taxa de Cobertura Estimada

**Baseado em top 100 estabelecimentos (5+ ocorrências):**

- ✅ **Cobertos:** ~1200 transações (45%)
- ❌ **Não cobertos:** ~1450 transações (55%)

**Problemas que causam maioria dos gaps:**
1. Uber variações (227x)
2. ConectCar typo (178x)
3. Investimentos/Transferências (muito específicos)
4. Vendify/IFD* (57x)
5. Apple.com/bill (36x)

**Com correções prioritárias:** Taxa esperada sobe para **~70-75%**

---

## ✅ Pontos Fortes da Base Atual

1. ✅ **Entretenimento** - Excelente cobertura de restaurantes
2. ✅ **Casa** - Boa cobertura de contas fixas
3. ✅ **Investimentos** - Bem estruturado
4. ✅ **Viagens** - Boa cobertura de serviços
5. ✅ **Saúde** - Farmácias bem cobertas

---

## 🎯 Próximos Passos

1. ✅ Validação completa
2. 📝 Criar documento de propostas (30+ melhorias)
3. 🧪 Script de teste com fatura real
4. 📊 Medir impacto das melhorias

---

**Conclusão:** Base atual tem boa fundação mas precisa de ~30 ajustes/adições para atingir >70% de cobertura.
