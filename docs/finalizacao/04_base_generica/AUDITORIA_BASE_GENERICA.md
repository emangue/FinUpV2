# 🔍 Auditoria Base Genérica - generic_classification_rules

**Data:** 12/02/2026  
**Objetivo:** Maximizar cobertura automática de classificação para novos usuários

---

## 📊 Estado Atual

### Regras Existentes
- **Total:** 55 regras ativas
- **Cobertura:** Categorias básicas (Alimentação, Transporte, Assinaturas, etc.)
- **Problemas identificados:**
  1. ❌ Estabelecimentos muito frequentes sem regra
  2. ❌ Keywords muito genéricas ou muito específicas
  3. ❌ Falta regras para variações de nomes

### Top Estabelecimentos Sem Cobertura

Analisando journal_entries do usuário principal (user_id=1):

**Transporte (259 ocorrências Uber):**
- `UBER* TRIP` (138x)
- `UBER * PENDING` (45x)  
- `UBER   *UBER   *TRIP` (44x)
- `UBER* PENDING` (14x)
- `Uber *Uber *Trip` (5x)

**Alimentação (34+ ocorrências):**
- `SAO JORGE ATACADISTA` (34x) → Supermercado
- `Vendify   Cond Lodz` (31x) → Delivery
- `VFY COMERCIO LOCACAO E` (26x) → Delivery

**Assinaturas:**
- `Apple.com/bill` (36x) → Apple
- `EBN*SPOTIFY` (16x) → Spotify
- `ENVIO MENS.AUTOMATICA` (16x) → Mensagem Cartão
- `Amazonprimebr` (14x) → Amazon Prime
- `Folhadespaulo` (12x) → Folha de SP
- `APPLE.COM/BILL` (10x) → Google Photos
- `TEMBICI` (10x) → Tem Bici
- `PRODUTOS GLOBO` (7x) → Premiere

**Serviços:**
- `Ezequiel Barbearia` (10x) → Cabeleireiro
- `Iof Compra Internaciona` (40x) → IOF

**Casa:**
- `CONTA VIVO` (23x celular + 22x internet)

**Carro:**
- `Pagamento CONECTCAR` (178x + 13x)
- `R&R ESTACIONAMENTOS` (8x)

---

## 🎯 Padrões de Categorização

### Grupos/Subgrupos Mais Usados (journal_entries)

```
Investimentos|MP: 969x
Entretenimento|Saídas: 311x
Transporte|Uber: 259x
Carro|ConnectCar: 193x
Roupas|Roupas: 171x
Alimentação|Delivery: 108x
Carro|Estacionamento: 103x
Outros|Outros: 97x
Viagens|EUA: 73x
Investimentos|Itaú Person: 66x
Alimentação|Supermercado: 58x
Salário|Salário: 57x
```

### Categorias Críticas para Novo Usuário

**Essenciais (90% dos gastos):**
1. Alimentação → Supermercado, Delivery, Almoço
2. Transporte → Uber, 99, Aplicativos
3. Assinaturas → Streaming, Cloud, Outros
4. Casa → Aluguel, Condomínio, Energia, Internet
5. Carro → Combustível, Estacionamento, Aplicativos

**Importantes (5-10%):**
6. Roupas → Roupas, Calçados
7. Entretenimento → Saídas, Cinema
8. Saúde → Farmácia, Academia
9. Serviços → Cabeleireiro, Lavanderia

---

## 🔧 Melhorias Necessárias

### 1. Expandir Keywords (Variações)

**Uber:**
- Adicionar: `uber*`, `uber *`, `uber   *`, `*uber*`

**Ifood:**
- Adicionar: `ifd*`, `ifood*`, `*ifood*`

**Spotify:**
- Adicionar: `ebn*spotify`, `spotify*`

**Amazon:**
- Adicionar: `amazon*`, `amazonprimebr`, `*amazon*`

**Apple:**
- Adicionar: `apple.com/bill`, `apple*`

### 2. Novas Regras Prioritárias

#### Transporte
```sql
nome_regra: "Uber - Variações"
keywords: "uber*,*uber*,uber   *"
grupo: "Transporte"
subgrupo: "Uber"
prioridade: 9
```

#### Alimentação
```sql
nome_regra: "Ifood - Variações"
keywords: "ifd*,ifood*,*ifood*,vendify"
grupo: "Alimentação"
subgrupo: "Delivery"
prioridade: 9
```

```sql
nome_regra: "Supermercado - Atacadista"
keywords: "*atacadista*,*supermercado*"
grupo: "Alimentação"
subgrupo: "Supermercado"
prioridade: 8
```

#### Assinaturas
```sql
nome_regra: "Apple - Serviços"
keywords: "apple.com/bill,apple*"
grupo: "Assinaturas"
subgrupo: "Apple"
prioridade: 9
```

```sql
nome_regra: "Spotify - Variações"
keywords: "ebn*spotify,spotify*"
grupo: "Assinaturas"
subgrupo: "Spotify"
prioridade: 9
```

```sql
nome_regra: "Amazon Prime"
keywords: "amazonprimebr,amazon prime,*prime*"
grupo: "Assinaturas"
subgrupo: "Amazon Prime"
prioridade: 9
```

```sql
nome_regra: "Mensagem Cartão"
keywords: "*mens*automatica*,envio mens*"
grupo: "Assinaturas"
subgrupo: "Outros"
prioridade: 7
```

#### Carro
```sql
nome_regra: "ConectCar"
keywords: "conectcar,conect car"
grupo: "Carro"
subgrupo: "Aplicativos"
prioridade: 9
```

```sql
nome_regra: "Estacionamento"
keywords: "*estacion*,r&r*,*parking*"
grupo: "Carro"
subgrupo: "Estacionamento"
prioridade: 8
```

#### Serviços
```sql
nome_regra: "IOF"
keywords: "iof*,*iof*"
grupo: "Serviços"
subgrupo: "IOF"
prioridade: 10
```

```sql
nome_regra: "Cabeleireiro/Barbearia"
keywords: "*barbear*,*cabeleir*,*salao*"
grupo: "Serviços"
subgrupo: "Cabeleireiro"
prioridade: 8
```

---

## 📋 Plano de Ação

### Fase 1: Análise Automática ✅
- [x] Mapear regras existentes (55 regras)
- [x] Analisar journal_entries (2631 registros)
- [x] Identificar estabelecimentos frequentes
- [x] Identificar gaps de cobertura

### Fase 2: Expansão de Regras
- [ ] Adicionar ~30 novas regras baseadas em dados reais
- [ ] Melhorar keywords das 55 regras existentes
- [ ] Ajustar prioridades baseado em frequência
- [ ] Adicionar case_sensitive onde necessário

### Fase 3: Teste com Dados Reais
- [ ] Processar CSVs históricos (_arquivos_historicos/_csvs_historico)
- [ ] Medir taxa de cobertura (% classificados)
- [ ] Identificar falsos positivos
- [ ] Ajustar regras baseado em resultados

### Fase 4: Validação
- [ ] Testar com usuário novo (zero state)
- [ ] Validar taxa de cobertura >70%
- [ ] Documentar regras finais
- [ ] Criar guia de manutenção

---

## 🎯 Meta de Cobertura

**Objetivo:** Classificar automaticamente ≥70% das transações de um novo usuário

**Benchmark atual (estimado):** ~40-50% com 55 regras

**Target após expansão:** ≥70% com ~85 regras

---

## 📁 Arquivos para Teste

Disponíveis em `_arquivos_historicos/_csvs_historico/`:
- Faturas Itaú: fatura-202508.csv até 202512.csv
- Faturas Itaú Person: fatura_itau-202510.csv até 202512.csv
- Extratos: Extrato Conta Corrente-*.xls (15+ arquivos)
- Mercado Pago: MP202501.xlsx até MP202512.xlsx

---

**Próximo passo:** Criar script de expansão automática de regras baseado em análise de journal_entries
