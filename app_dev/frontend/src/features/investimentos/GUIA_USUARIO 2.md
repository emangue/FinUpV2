# 📊 Guia do Usuário - Módulo de Investimentos

## 🎯 Visão Geral

O módulo de Investimentos permite acompanhar e gerenciar seu portfólio de investimentos, incluindo:
- Renda Fixa, Fundos Imobiliários, Ações, Previdência Privada, etc.
- Histórico de rentabilidade mês a mês
- Análise de distribuição e diversificação
- Simulação de cenários futuros
- Exportação de relatórios

---

## 🚀 Como Começar

### 1. Acessando o Módulo
- No menu lateral, clique em **"Investimentos"**
- Você será direcionado para o dashboard principal

### 2. Primeiro Acesso (Sem Investimentos)
Se você ainda não tem investimentos cadastrados:
- Clique no botão **"+ Adicionar"** no canto superior direito
- Preencha o formulário com os dados do investimento
- Clique em **"Salvar"**

---

## 📋 Dashboard Principal

### Seção: Resumo do Portfólio

**4 Cards com métricas principais:**

1. **Total Investido** - Soma de todos os aportes realizados
2. **Valor Atual** - Patrimônio total atual (com rentabilidade)
3. **Rendimento Total** - Ganhos acumulados (Valor Atual - Total Investido)
4. **Rendimento %** - Percentual de rentabilidade sobre o investido

### Seção: Indicadores Temporais

**2 Cards com timelines:**

1. **Rendimento Mensal** - Linha do tempo mostrando ganhos mês a mês
   - Valores positivos em verde
   - Valores negativos em vermelho (perdas)

2. **Saldo dos Investimentos** - Evolução do patrimônio total
   - Crescimento acumulado ao longo dos meses

### Seção: Filtros

**Busca e filtros disponíveis:**
- **Campo de busca** - Digite nome do produto ou emissor
- **Tipo de investimento** - Filtre por Renda Fixa, FII, Ações, etc.
- **Corretora** - Filtre por instituição financeira
- **Botão "Limpar filtros"** - Remove todos os filtros ativos

💡 **Dica:** Os totais são recalculados automaticamente conforme você aplica filtros.

---

## 📊 Tabela de Investimentos

### Colunas Principais

| Coluna | Descrição |
|--------|-----------|
| **Produto** | Nome do investimento + emissor |
| **Tipo** | Classificação (Renda Fixa, FII, Ação, etc.) |
| **Corretora** | Instituição onde está aplicado |
| **Quantidade** | Número de cotas/unidades |
| **Valor Inicial** | Montante aplicado originalmente |
| **Data Aplicação** | Quando foi realizado o aporte |
| **Ações** | Botões de visualizar e editar |

### Ações Disponíveis

**👁️ Visualizar Detalhes:**
- Clique no ícone de olho para ver informações completas
- Modal exibe: histórico, rentabilidade, características do produto

**✏️ Editar:**
- Clique no ícone de lápis para modificar dados
- Pode alterar: quantidade, valores, datas, corretora, etc.
- As alterações são salvas imediatamente

---

## 📈 Gráficos e Análises

### 1. Distribuição por Tipo (Pizza)

**O que mostra:**
- Percentual de cada tipo de investimento no portfólio
- Cores diferentes para cada categoria
- Top 5 tipos com maior alocação

**Como usar:**
- Passe o mouse sobre as fatias para ver valores exatos
- Use para avaliar diversificação

### 2. Distribuição por Classe de Ativo (Barras + Tabela)

**Seção com duas visões:**

**Gráfico de Barras:**
- Mostra valor investido por tipo
- Barras coloridas por categoria
- Comparativo visual fácil

**Tabela Detalhada:**
| Tipo | Valor Investido | % do Total | Nº Produtos |
|------|----------------|------------|-------------|
| Renda Fixa | R$ 50.000 | 40% | 12 |
| FII | R$ 30.000 | 24% | 8 |
| ... | ... | ... | ... |

💡 **Insights:** Identifique rapidamente onde está concentrado seu patrimônio.

### 3. Evolução Temporal (Linha Dupla)

**2 Linhas no gráfico:**

1. **Patrimônio Real** (azul) - Dados históricos reais do seu portfólio
2. **Patrimônio Projetado** (verde tracejado) - Estimativa baseada em rendimento médio

**Como usar:**
- Compare se sua rentabilidade real está acima ou abaixo da projeção
- Ajuste sua estratégia se houver desvios grandes

**Filtros do Gráfico:**
- **Período de visualização** - Selecione intervalo de meses
- **Botão "Atualizar"** - Recarrega dados com novo período

### 4. Visão por Corretora

**3 Cards informativos:**

**a) Distribuição por Corretora (Pizza)**
- Percentual do patrimônio em cada instituição
- Identifique concentração de risco

**b) Performance por Corretora (Barras)**
- Rentabilidade média de cada corretora
- Compare qual instituição teve melhor retorno

**c) Análise de Risco (Tabela)**
| Corretora | Valor Total | % Portfólio | Status Risco |
|-----------|-------------|-------------|--------------|
| XP | R$ 80.000 | 53% | ⚠️ Alto |
| BTG | R$ 40.000 | 27% | ✅ OK |
| ... | ... | ... | ... |

**Status de Risco:**
- ✅ **OK** - Menos de 40% do portfólio
- ⚠️ **Alto** - Mais de 40% do portfólio
- 🔴 **Crítico** - Mais de 60% do portfólio

💡 **Recomendação:** Mantenha diversificação entre corretoras para reduzir risco.

---

## 🧮 Simulador de Cenários

### Acessando
- Clique no botão **"🧮 Simulador"** no canto superior direito
- Nova tela dedicada será aberta

### Criando um Cenário

**Passo 1: Configurar Parâmetros Base**
- **Nome do cenário** - Ex: "Cenário Otimista 2026"
- **Patrimônio inicial** - Valor atual ou valor desejado
- **Rendimento mensal (%)** - Taxa esperada (ex: 0,8% = 0,8)
- **Aporte mensal fixo** - Quanto pretende investir todo mês
- **Período** - Quantos meses/anos simular

**Passo 2: Aportes Extraordinários (Opcional)**
- Clique em **"+ Adicionar Aporte Extraordinário"**
- Defina o mês (ex: Mês 12 = 13º salário)
- Informe o valor (ex: R$ 30.000)
- Adicione descrição (ex: "Bonus anual")

**Passo 3: Visualizar Resultados**
- Gráfico mostra 3 linhas:
  1. **Patrimônio Estimado** - Projeção do cenário
  2. **Patrimônio Real** - Dados históricos reais
  3. **Estimativa Curto Prazo** - Próximos 12 meses

**Métricas Finais:**
- **Patrimônio em X anos** - Valor projetado no fim do período
- **Independência Financeira** - Em qual mês atingirá sua meta
- **Renda Passiva Mensal** - Quanto renderá por mês (0,5% do patrimônio)

### Comparando Cenários
- Salve múltiplos cenários (conservador, moderado, otimista)
- Alterne entre eles no dropdown
- Compare visualmente no gráfico

---

## 📤 Exportação de Dados

### Como Exportar

**Passo 1:**
- Clique no botão **"📄 Exportar"** no canto superior direito

**Passo 2:**
- Escolha o formato:
  - **Excel (.xlsx)** - Recomendado para análises complexas
  - **CSV (.csv)** - Para importar em outros sistemas

**Passo 3:**
- O arquivo será baixado automaticamente
- Nome do arquivo: `investimentos_YYYY-MM-DD.xlsx`

### O que é Exportado

**Planilha 1: Investimentos**
- Todos os produtos do portfólio
- Dados completos: nome, tipo, corretora, valores, datas
- **Respeitam os filtros ativos** (se filtrou por tipo, só exporta aquele tipo)

**Planilha 2: Distribuição por Tipo**
- Tabela resumida com totais por categoria
- Percentuais calculados
- Número de produtos

**Planilha 3: Resumo**
- Métricas principais (total investido, rendimento, etc.)
- Data da exportação
- Filtros aplicados no momento da exportação

---

## 🔍 Filtros de Período

### Para Que Servem
- Permitem visualizar dados de um intervalo específico
- Útil para comparar anos diferentes
- Analise sazonalidade e tendências

### Como Usar

**Seletores de Data:**
1. **Data Início** - Mês e ano iniciais
2. **Data Fim** - Mês e ano finais

**Exemplo:**
- Início: Janeiro/2024
- Fim: Dezembro/2024
- **Resultado:** Vê apenas dados de 2024

**Dica Rápida:**
- Botão **"🔄 Último ano"** - Preenche automaticamente últimos 12 meses
- Botão **"📅 Ano atual"** - Preenche janeiro até mês atual

---

## ✏️ Adicionar Novo Investimento

### Formulário Completo

**Campos Obrigatórios:**
- **Nome do produto** - Ex: "Tesouro Selic 2029"
- **Corretora** - Ex: "XP Investimentos"
- **Tipo de investimento** - Dropdown com opções
- **Quantidade** - Número de cotas (padrão: 1)
- **Valor unitário inicial** - Preço da cota na aplicação
- **Data de aplicação** - Quando foi investido

**Campos Opcionais:**
- **Emissor** - Ex: "Tesouro Nacional"
- **Classe de ativo** - Ativo/Passivo
- **% CDI** - Se for pós-fixado (ex: 105% do CDI)
- **Data de vencimento** - Se houver

**Cálculo Automático:**
- Ao preencher "Quantidade" e "Valor unitário"
- **Valor Total** é calculado automaticamente
- Exemplo: 100 cotas × R$ 50,00 = R$ 5.000,00

**Dicas de Preenchimento:**
- **Balance ID** é gerado automaticamente (não preencher)
- Use nomes descritivos para facilitar busca futura
- Mantenha padrão de nomenclatura (ex: sempre "BANCO + nome")

---

## 🛠️ Editar Investimento Existente

### Como Editar

**Passo 1:**
- Na tabela, clique no ícone **✏️** na coluna "Ações"

**Passo 2:**
- Modal abre com dados atuais preenchidos
- Modifique os campos desejados

**Passo 3:**
- Clique em **"Salvar alterações"**
- Aguarde confirmação (toast verde: "Investimento atualizado")

### O Que Pode Ser Editado
- ✅ Nome do produto
- ✅ Corretora
- ✅ Tipo de investimento
- ✅ Quantidade de cotas
- ✅ Valores (unitário e total)
- ✅ Datas (aplicação e vencimento)
- ❌ Balance ID (gerado pelo sistema)

### Cuidados ao Editar
- ⚠️ Alterar "Tipo" pode mudar a distribuição nos gráficos
- ⚠️ Alterar "Quantidade" ou "Valor" afeta os totais
- ⚠️ Não é possível desfazer edições (certifique-se antes de salvar)

---

## 🗑️ Excluir Investimento

### Como Excluir

**Opção 1: Via Modal de Detalhes**
- Clique em **👁️ Visualizar**
- No rodapé do modal, clique em **"🗑️ Excluir investimento"**
- Confirme a ação

**Opção 2: Via Modal de Edição**
- Clique em **✏️ Editar**
- No rodapé, clique em **"🗑️ Excluir"**
- Confirme a ação

**Confirmação de Segurança:**
- Sistema pede confirmação antes de excluir
- Exclusão é **permanente** (não há como recuperar)

💡 **Recomendação:** Se não tem certeza, edite e marque como "inativo" em vez de excluir.

---

## 📊 Entendendo as Métricas

### Total Investido
- **O que é:** Soma de todos os aportes realizados
- **Cálculo:** Σ (Valor Total Inicial de cada investimento)
- **Uso:** Saber quanto dinheiro você efetivamente colocou

### Valor Atual / Patrimônio Atual
- **O que é:** Quanto vale seu portfólio hoje
- **Cálculo:** Total Investido + Rendimentos acumulados
- **Uso:** Ver o valor real do seu patrimônio

### Rendimento Total (R$)
- **O que é:** Quanto você ganhou desde o início
- **Cálculo:** Valor Atual - Total Investido
- **Uso:** Acompanhar ganhos em valores absolutos

### Rendimento Total (%)
- **O que é:** Percentual de rentabilidade sobre o investido
- **Cálculo:** (Rendimento Total ÷ Total Investido) × 100
- **Uso:** Comparar performance do portfólio com benchmarks

**Exemplo Prático:**
- Total Investido: R$ 100.000
- Valor Atual: R$ 115.000
- Rendimento Total: R$ 15.000 (15%)

---

## 💡 Dicas e Boas Práticas

### Cadastro de Investimentos
✅ **Mantenha atualizado**
- Cadastre novos aportes assim que realizar
- Atualize valores de resgate imediatamente

✅ **Use nomes consistentes**
- Padrão: "CORRETORA - Tipo - Nome do produto"
- Exemplo: "XP - FII - HGLG11"

✅ **Categorize corretamente**
- Tipo correto facilita análises
- Use categorias padrão sempre que possível

### Acompanhamento
✅ **Revise mensalmente**
- Compare projeções vs. real
- Ajuste estratégia se necessário

✅ **Diversifique**
- Evite concentração em uma única corretora (> 40%)
- Distribua entre tipos de investimento

✅ **Use o simulador**
- Teste cenários antes de mudar estratégia
- Planeje aportes extraordinários

### Exportação e Backup
✅ **Exporte periodicamente**
- Gere backup mensal dos dados
- Armazene em local seguro (drive, nuvem)

✅ **Use para IR**
- Exporte ao fim do ano para declaração
- Excel facilita cálculos de imposto

---

## ❓ Perguntas Frequentes (FAQ)

### 1. Posso importar dados de um arquivo Excel?
Atualmente não há importação via interface. Use a API ou contate o administrador.

### 2. Como atualizar o valor atual dos investimentos?
O sistema calcula automaticamente com base no histórico. Para forçar atualização, edite o investimento.

### 3. Por que alguns gráficos não aparecem?
Se não houver dados suficientes (ex: menos de 2 meses), gráficos não são exibidos.

### 4. Posso adicionar investimentos no exterior?
Sim, use o campo "Corretora" para indicar instituição estrangeira.

### 5. Como funciona a projeção de patrimônio?
Usa rendimento médio histórico + aportes configurados. É uma estimativa, não garantia.

### 6. Posso excluir múltiplos investimentos de uma vez?
Não. Cada investimento deve ser excluído individualmente por segurança.

### 7. O que é "Balance ID"?
Identificador único do investimento. Gerado automaticamente, não precisa preencher.

### 8. Como ver investimentos inativos/resgatados?
Atualmente, só investimentos ativos são exibidos. Funcionalidade de histórico em desenvolvimento.

---

## 🆘 Suporte e Problemas

### Problemas Comuns

**1. Página não carrega / Erro ao buscar dados**
- **Causa:** Servidor backend offline ou problema de rede
- **Solução:** 
  - Verifique se está conectado à internet
  - Tente recarregar a página (Ctrl+R ou Cmd+R)
  - Clique em "Tentar novamente" no erro

**2. Não consigo adicionar investimento**
- **Causa:** Campos obrigatórios não preenchidos
- **Solução:**
  - Certifique-se de preencher: nome, corretora, tipo, quantidade, valor
  - Verifique se valores numéricos estão corretos (sem letras)

**3. Gráficos não atualizam após adicionar/editar**
- **Causa:** Cache do navegador
- **Solução:**
  - Recarregue a página (F5)
  - Limpe cache do navegador se persistir

**4. Exportação não funciona**
- **Causa:** Bloqueador de pop-ups ou extensão do navegador
- **Solução:**
  - Desabilite bloqueadores temporariamente
  - Verifique configurações de download do navegador

### Como Reportar um Bug

**Informações Necessárias:**
1. Descrição do problema
2. Passos para reproduzir
3. Navegador e versão (ex: Chrome 120)
4. Captura de tela (se aplicável)
5. Mensagem de erro (se houver)

**Onde Reportar:**
- Entre em contato com o administrador do sistema
- Abra um ticket no suporte interno

---

## 🔄 Atualizações Futuras

**Funcionalidades Planejadas:**
- [ ] Importação de extratos de corretoras (PDF/Excel)
- [ ] Integração com API de cotações (atualização automática de valores)
- [ ] Histórico de investimentos inativos/resgatados
- [ ] Alertas de vencimentos e metas
- [ ] Comparativo com benchmarks (CDI, IPCA, Ibovespa)
- [ ] App mobile (iOS/Android)

---

**📅 Última atualização:** 17 de Janeiro de 2026  
**📋 Versão do módulo:** 1.0.0  
**👤 Suporte:** Sistema de Finanças Pessoais
