# PRD — Patrimônio e Investimentos
> Sub-projeto 06 | Sprints 8, 9 | ~26h  
> Dependências: Sub-projeto 04 (uploads como fonte de aportes) + Sub-projeto 05 (plano financeiro com metas)

---

## 1. Problema

O usuário já registra gastos e receitas, mas seus investimentos são uma caixa-preta: não sabe se está ganhando ou perdendo, não tem posição consolidada, não calcula IR, e não consegue ver o vínculo entre o aporte que fez (no extrato) e o investimento registrado. Além disso, depende de ferramentas externas (planilha, corretora) para entender sua carteira.

---

## 2. Objetivo

Trazer visibilidade completa da carteira de investimentos dentro do app: vínculos automáticos com extratos, posição atualizada em tempo real, rentabilidade calculada (CDI, ações, indexadores), IR estimado, e saldo disponível na corretora.

---

## 3. Escopo (IN)

| ID | Feature | Sprint |
|----|---------|--------|
| S11 | Vínculo manual: aporte no extrato ↔ investimento cadastrado | 8 |
| S12 | Match automático de vínculos por valor+data±3 dias | 8 |
| S13 | Rentabilidade CDI para renda fixa | 8 |
| S14 | Posição + custo médio para ações (via brapi) | 9 |
| S15 | IR estimado (ações + FIIs + renda fixa) | 9 |
| S16 | Venda/resgate vinculado ao extrato | 9 |
| S17 | Saldo disponível na corretora | 9 |
| S18 | Indexadores alternativos (IGPM, INCC, pré-fixado, CRI/CRA) | 9 |

---

## 4. Escopo (OUT)

- Open Banking direto com corretoras (autenticação, sincronização automática)
- Importação de nota de corretagem (PDF parsing)
- Declaração de IR anual completa (IRPF)
- Criptoativos
- Fundos de investimento (cotas)

---

## 5. Dependências de Outros Sub-projetos

| Dep | Motivo |
|-----|--------|
| **04-upload-completo** (HARD) | Aportes chegam como transações de extrato; rollback de upload deve desvincular investimentos automaticamente |
| **05-plano-financeiro** (soft) | `user_financial_profile` usado para calcular IR com base na renda total |

---

## 6. User Stories

### S11 — Vínculo manual: aporte ↔ investimento

**Como** usuário,  
**Quero** vincular uma transação de extrato (ex: "TED para XP R$ 5.000") a um investimento cadastrado,  
**Para que** o app saiba que aquele dinheiro foi investido e não "saiu" do patrimônio.

**Acceptance Criteria:**
- [ ] Modal "Vincular investimento" acessível a partir de qualquer transação de débito
- [ ] Selecionar investimento existente OU criar novo na hora
- [ ] Um aporte pode ser dividido entre múltiplos investimentos (ex: R$ 5.000 → R$ 3.000 XP CDB + R$ 2.000 ITSA4)
- [ ] Transação vinculada recebe ícone diferenciado e não conta como "gasto" no dashboard
- [ ] Vínculo removível individualmente (sem apagar a transação)

### S12 — Match automático de vínculos

**Como** usuário,  
**Quero** que o sistema sugira automaticamente quais transações de extrato correspondem a aportes nos meus investimentos,  
**Para que** eu precise confirmar apenas os matches, não criar cada vínculo do zero.

**Acceptance Criteria:**
- [ ] Heurística: mesma data (±3 dias) + mesmo valor + banco reconhecido como corretora
- [ ] Sugestões exibidas como notificações ou na tela de investimentos
- [ ] "Confirmar" aceita a sugestão; "Ignorar" descarta sem registrar negativo
- [ ] Match não forçado: sempre confirmação humana antes de salvar

### S13 — Rentabilidade CDI para renda fixa

**Como** usuário com CDB/LCI/LCA,  
**Quero** ver a rentabilidade acumulada calculada com base no CDI real,  
**Para que** eu saiba se o investimento está performando conforme o prometido.

**Acceptance Criteria:**
- [ ] Job diário: busca taxa CDI do Banco Central (API BACEN séries temporais, série 4389)
- [ ] Calcula rentabilidade acumulada desde a data do aporte: `valor_atual = principal × ∏(1 + CDI_diário × percentual_CDI)`
- [ ] Exibe: valor investido, valor atual, rendimento bruto, rendimento líquido (pós IR)
- [ ] Suporta percentuais diferentes por investimento (80% CDI, 100% CDI, 120% CDI)
- [ ] Exibe variação do CDI no último mês

### S14 — Posição + custo médio para ações

**Como** usuário com ações,  
**Quero** ver minha posição atual (quantidade × preço atual) e meu custo médio,  
**Para que** eu saiba se estou no lucro ou prejuízo em cada papel.

**Acceptance Criteria:**
- [ ] Preço atual via brapi (`GET https://brapi.dev/api/quote/{tickers}`) — batch por lote de 10
- [ ] Custo médio calculado por FIFO (ou preço médio ponderado — configurável)
- [ ] Posição = quantidade atual × preço atual
- [ ] P&L (Profit & Loss) = posição - (quantidade × custo médio)
- [ ] Variação do dia (% e R$) exibida
- [ ] Atualização de preços: automática a cada 15 minutos durante horário de pregão

### S15 — IR estimado

**Como** usuário,  
**Quero** ver uma estimativa do IR que devo sobre cada tipo de investimento,  
**Para que** eu possa fazer provisão e não ser surpreendido no resgate.

**Acceptance Criteria:**
- [ ] **Ações:** Isenção se vendas < R$ 20.000/mês; 20% sobre lucro se > R$ 20.000/mês; 15% Day-trade
- [ ] **FIIs:** Sempre 20% sobre rendimentos (sem isenção)
- [ ] **Renda fixa (tabela regressiva):**
  - Até 180 dias: 22,5%
  - 181-360 dias: 20%
  - 361-720 dias: 17,5%
  - Acima de 720 dias: 15%
- [ ] IR calculado apenas sobre o lucro (valor atual - principal investido)
- [ ] Exibir: IR estimado por investimento + total IR da carteira este ano

### S16 — Venda/resgate vinculado ao extrato

**Como** usuário que fez um resgate/venda,  
**Quero** vincular a entrada no extrato ao investimento correspondente,  
**Para que** o sistema atualize minha posição e calcule o lucro realizado automaticamente.

**Acceptance Criteria:**
- [ ] Modal "Registrar resgate/venda" acessível na transação de crédito do extrato
- [ ] Selecionar investimento + quantidade resgatada/vendida
- [ ] Sistema atualiza posição, calcula lucro realizado e IR definitivo
- [ ] Histórico de resgates por investimento

### S17 — Saldo disponível na corretora

**Como** usuário,  
**Quero** ver meu saldo disponível na corretora (para novos aportes),  
**Para que** eu saiba quanto tenho para investir sem precisar acessar o app da corretora.

**Acceptance Criteria:**
- [ ] Saldo = soma de créditos da corretora - soma de débitos (aportes) vinculados a investimentos
- [ ] Exibido por corretora/banco (XP, BTG, Nubank etc.)
- [ ] Atualizado automaticamente após cada upload de extrato
- [ ] Se saldo negativo: aviso "Verifique — pode haver aportes não vinculados"

### S18 — Indexadores alternativos

**Como** usuário com CRI, CRA, Debêntures ou títulos pré-fixados,  
**Quero** ver a rentabilidade calculada com IGPM, INCC, ou taxa pré-fixada,  
**Para que** minha carteira completa tenha rentabilidade calculada, não apenas CDB.

**Acceptance Criteria:**
- [ ] IGPM: série BACEN 189
- [ ] INCC: série BACEN 192
- [ ] Pré-fixado: calculado diretamente pela taxa anual sem busca externa
- [ ] Seleção de indexador por investimento: CDI, IGPM, INCC, Pré-fixado, IPCA (série 433)

---

## 7. UX / Wireframes

### Tela Carteira (`/mobile/carteira`)

```
┌─────────────────────────────────────────────────────┐
│ 💼 Minha Carteira                          [+ Novo] │
├─────────────────────────────────────────────────────┤
│ Renda Fixa                          R$ 42.300       │
│  ├ CDB XP 120% CDI    R$ 20.000 → R$ 20.850 (+4.2%)│
│  ├ LCI Nubank 100% CDI R$ 15.000 → R$ 15.520 (+3.5%)│
│  └ CDB BTG 110% CDI   R$ 7.000 → R$  7.280 (+4.0%)│
│                                                     │
│ Ações                               R$ 18.600       │
│  ├ ITSA4  200 cotas  R$10.50  →  R$ 2.100  (+2.3%) │
│  ├ PETR4  100 cotas  R$38.20  → R$ 3.820  (-1.1%) │
│  └ MXRF11 400 cotas  R$10.45  → R$ 4.180  (+0.8%) │
│                                                     │
│ 💰 Saldo disponível: R$ 1.240 (BTG)                │
│ 🧾 IR estimado 2025: R$ 890                         │
└─────────────────────────────────────────────────────┘
```

### Modal de Vínculo de Aporte

```
┌──────────────────────────────────────────┐
│ 🔗 Vincular investimento                  │
│ TED XP R$ 5.000 — 15/11/2025            │
├──────────────────────────────────────────┤
│ [+ Dividir entre múltiplos] ←           │
│                                          │
│ Investimento: [CDB XP 120% CDI    ▼]   │
│ Valor:        [R$ 5.000,00           ]  │
│                                          │
│ ── OU ──                                │
│ [Criar novo investimento]               │
├──────────────────────────────────────────┤
│         [Cancelar] [Vincular]           │
└──────────────────────────────────────────┘
```

---

## 8. Riscos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| API brapi fora do ar / rate limit | Médio | Cache Redis 15min; fallback com último preço conhecido + timestamp |
| API BACEN indisponível | Baixo | Cache diário; se falhar, manter último CDI disponível |
| Custo médio FIFO complexo com muitas operações | Médio | Calcular apenas quando solicitado (lazy), com cache |
| IR estimado errado → decisão financeira errada | Médio | Disclaimer claro "estimativa — consulte contador para declaração oficial" |
| Match automático errado (falso positivo) | Médio | Confirmação humana obrigatória, sem auto-aceite |

---

## 9. Métricas de Sucesso

| Métrica | Meta |
|---------|------|
| % de usuários com ≥ 1 investimento vinculado | > 50% em 30 dias |
| Taxa de aceitação de matches automáticos | > 70% (indica qualidade do algoritmo) |
| Atualização diária do CDI sem falha | > 99% de uptime |
| % de usuários que consultam IR estimado antes de resgatar | > 30% |
