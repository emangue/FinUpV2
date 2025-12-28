# Sistema de Gestão Financeira Automatizada

**Versão Atual:** 2.2.1  
**Última Atualização:** 27/12/2025

Sistema web desenvolvido em Python/Flask para processamento automatizado de extratos e faturas bancárias, com classificação inteligente de transações e interface de validação manual.

## 📋 Visão Geral

Este sistema substitui o workflow n8n anterior, oferecendo uma interface web para:
- Upload de arquivos CSV/XLSX (Faturas Itaú, Extratos Itaú, Extratos Mercado Pago)
- Processamento e extração automática de transações
- Deduplicação contra base histórica
- Classificação automática usando padrões aprendidos
- Validação manual de transações não classificadas
- Gestão de padrões de classificação

## 🏗️ Arquitetura do Sistema

### ⚙️ Modularização com Flask Blueprints

O sistema utiliza **Application Factory Pattern** com 3 blueprints independentes:

1. **Dashboard Blueprint** (`/dashboard/`)
   - Dados permanentes do banco de dados
   - Analytics, visualizações e edição de transações
   - Acessa: `JournalEntry`, `BaseMarcacao`, `GrupoConfig`, `AuditLog`

2. **Upload Blueprint** (`/upload/`)
   - Dados temporários em sessão (namespace `upload.*`)
   - Processamento de arquivos, validação e salvamento
   - Acessa: `JournalEntry` (para salvar), `BaseMarcacao` (para dropdowns)

3. **Admin Blueprint** (`/admin/`)
   - Configurações e gerenciamento de bases
   - CRUD de marcações, padrões, grupos e logos
   - Acessa: `BaseMarcacao`, `BasePadrao`, `GrupoConfig`, `EstabelecimentoLogo`

**Princípio de Modularidade:**
- ✅ **Permitido:** Importar modelos compartilhados (`models.py`) - são dados centralizados
- ✅ **Permitido:** Upload blueprint consultar `BaseMarcacao` para dropdowns de validação
- ❌ **Proibido:** Blueprints importarem rotas ou lógica de outros blueprints
- ❌ **Proibido:** Compartilhar dados entre blueprints via variáveis globais

**⚠️ GARANTIA DE MODULARIDADE:**
Qualquer alteração que possa comprometer a arquitetura modular será **SEMPRE** apresentada para aprovação antes da implementação, incluindo:
- Análise de impacto na separação de responsabilidades
- Alternativas que preservem a modularidade
- Justificativa técnica caso a quebra seja necessária
- Consequências de longo prazo para manutenibilidade

**Exemplo: Dropdown de Grupos na Validação**
- O blueprint `upload` acessa `BaseMarcacao.query.distinct(BaseMarcacao.GRUPO)`
- Isso **não quebra** modularidade pois `BaseMarcacao` é um modelo compartilhado
- A separação é mantida: dados permanentes (Dashboard) vs temporários (Upload)

### Fluxo de Processamento

```
┌─────────────────┐
│  Upload Files   │
│  (CSV/XLSX)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Identificação Automática   │
│  - fatura_itau*.csv         │
│  - Extrato Conta Corrente*  │
│  - account_statement*.xlsx  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Processamento Específico  │
│   - Extração de campos      │
│   - Detecção de parcelas    │
│   - Geração de IdTransacao  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Deduplicação              │
│   - Compara com Journal     │
│   - Move para duplicados    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Classificação Automática  │
│   1. Base Padrões           │
│   2. Histórico (Journal)    │
│   3. Regras Palavras-Chave  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Dashboard & Validação     │
│   - Resumo financeiro       │
│   - Validação manual        │
│   - Seleção de bases        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Salvar Journal Entries    │
│   - Salva bases selecionadas│
│   - Apaga duplicados_temp   │
│   - Regenera padrões        │
│   - Registra audit log      │
└─────────────────────────────┘
```

## 📁 Estrutura de Pastas

```
ProjetoFinancasV3/
├── app.py                          # Servidor Flask principal
├── config.py                       # Configurações da aplicação
├── models.py                       # Models SQLAlchemy (DB)
├── requirements.txt                # Dependências Python
├── import_base_inicial.py          # Script de importação inicial
├── README.md                       # Documentação (este arquivo)
├── STATUSPROJETO.md               # Status do projeto
│
├── utils/                          # Utilitários gerais
│   ├── __init__.py
│   ├── hasher.py                   # Hash FNV-1a 64-bit
│   ├── normalizer.py               # Normalização de texto
│   └── deduplicator.py             # Deduplicação contra Journal
│
├── processors/                     # Processadores de arquivos
│   ├── __init__.py
│   ├── fatura_itau.py              # Processa CSV de faturas
│   ├── extrato_itau.py             # Processa XLS de extratos
│   └── mercado_pago.py             # Processa XLSX Mercado Pago
│
├── classifiers/                    # Sistema de classificação
│   ├── __init__.py
│   ├── auto_classifier.py          # Classificador automático
│   └── pattern_generator.py        # Geração/regeneração de padrões
│
├── scripts/                        # Scripts utilitários
│   ├── COMO_ADICIONAR_LOGOS.py     # Guia para adicionar logos
│   └── check_groups.py             # Verificação de grupos
│
├── templates/                      # Templates HTML (Jinja2)
│   ├── base.html                   # Template base com Chart.js
│   ├── dashboard.html              # Dashboard analítico principal
│   ├── upload.html                 # Upload e processamento de arquivos
│   ├── transacoes.html             # Lista de transações com toggle
│   ├── validar.html                # Validação manual de transações
│   ├── duplicados.html             # Visualização de duplicados
│   ├── admin_padroes.html          # Admin de padrões de classificação
│   ├── admin_logos.html            # Admin de logos de estabelecimentos
│   └── admin_grupos.html           # Admin de grupos e categorias
│
└── static/                         # Arquivos estáticos
    ├── css/
    │   └── style.css               # Estilos CSS com Bootstrap 5
    ├── js/
    │   └── main.js                 # JavaScript frontend
    └── logos/                      # Logos de estabelecimentos
        ├── README.md               # Documentação dos logos
        └── *.{png,svg,webp,jpg}    # Arquivos de logo
```

## � PROTEÇÃO DE BASES DE DADOS

### ⚠️ ATENÇÃO: VALIDAÇÃO OBRIGATÓRIA

**TODAS as operações que alterem as bases de dados requerem validação manual:**

- ❌ **NUNCA** execute scripts de importação sem revisar o que será alterado
- ✅ **SEMPRE** use os scripts com confirmação interativa
- 🎯 **PRIORIDADE**: Base `BaseMarcacoesGastos` (essencial para dropdowns)
- ⚡ **VALIDAÇÃO**: Outras bases (`Journal Entries`, `Base_Padroes`) podem ser validadas mas só alteradas com aprovação

### Scripts Disponíveis

- `import_marcacoes_seguro.py` - **RECOMENDADO**: Importa apenas BaseMarcacoesGastos com confirmação
- `import_base_inicial.py` - **CUIDADO**: Importa todas as bases (use apenas se necessário)

## 🚀 Instalação e Uso

### 1. Instalação

```bash
# Clone ou navegue até o diretório
cd ProjetoFinancasV3

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Instale dependências
pip install -r requirements.txt
```

### 2. Importação Inicial (SEGURA)

```bash
# RECOMENDADO: Importa apenas BaseMarcacoesGastos com validação
python import_marcacoes_seguro.py
```

### 3. Importação Completa (SOMENTE SE NECESSÁRIO)

```bash
# CUIDADO: Importa todas as bases - confirme antes de usar
python import_base_inicial.py
```

Isso criará:
- `financas.db` (banco SQLite)
- Popula principalmente `base_marcacoes` (necessário para funcionalidade)
- Opcionalmente `journal_entries`, `base_padroes` (com confirmação)

### 4. Executar Aplicação

```bash
python app.py
```

Acesse: `http://localhost:5000`

### 4. Uso Típico

1. **Dashboard Analítico (Home)**
   - Acesse `http://localhost:5000`
   - Visualize KPIs (Total Gasto, Receita, Saldo)
   - Gráficos de despesas por categoria e evolução mensal
   - Filtre por mês/ano (baseado na data da fatura)

2. **Upload de Arquivos**
   - Clique em "Upload de Arquivos" no menu
   - Arraste arquivos CSV/XLSX ou clique em "Escolher Arquivos"
   - Clique em "Processar Arquivos"

3. **Revisar Processamento**
   - Veja resumo de transações por origem (Fatura Itaú, Extrato Itaú, Mercado Pago)
   - Verifique valores de faturas/extratos
   - **Selecione quais bases deseja salvar** (checkbox por origem)
   - Clique em "Ver Duplicados" se houver

4. **Validar Pendentes** (se houver)
   - Clique em "Validar Marcações Pendentes"
   - Classifique transação por transação
   - Salve ao finalizar

5. **Salvar na Base**
   - Selecione as origens desejadas (ou marque "Selecionar Todas")
   - Clique em "Salvar Selecionadas na Journal Entries"
   - Aguarde processamento
   - Padrões são regenerados automaticamente

6. **Gerenciar Padrões e Logos** (opcional)
   - Acesse `/admin/padroes` para regras de classificação
   - Acesse `/admin/logos` para gerenciar logos de estabelecimentos (Criar/Editar)

## 📊 Funcionalidades Principais

### Dashboard Analítico Completo
Sistema de dashboard avançado com visualizações interativas:
- **Filtros Temporais:** Seletor de Mês/Ano para análise temporal
- **KPIs Financeiros:** Cards com Total de Despesas, Receitas e Saldo
- **Gráficos Interativos (Chart.js 4.4.0):**
  - Gráfico de barras com evolução mensal dos últimos 6 meses (valores em milhares)
  - Gráfico de pizza com insights das principais categorias de gastos
  - Top 10 SubGrupos de gastos (em vez de estabelecimentos individuais)
- **Modal de Detalhes:** Sistema de modais para visualizar detalhes completos de transações
- **Formatação Brasileira:** Valores em R$ com separadores de milhares
- **Seção de Categorias:** Área dedicada para futuras análises categóricas

### Sistema de Toggle para Controle de Dashboard
Interface avançada para gestão granular de transações:
- **Listagem Detalhada:** Visualização completa com logos, grupos e valores formatados
- **Toggle "Status Dashboard":** Interruptor visual para controle de inclusão nos cálculos
  - **Ativo (Verde):** Transação considerada nos totais e gráficos do dashboard
  - **Inativo (Cinza):** Transação mantida no histórico mas excluída dos cálculos
  - **Casos de uso:** Investimentos, transferências internas, transações especiais
- **Atualização em Tempo Real:** Dashboard recalcula automaticamente via AJAX
- **Persistência:** Status salvo no banco de dados para manter estado entre sessões

### Gestão de Logos
Sistema inteligente para associar logos aos estabelecimentos:
- **Upload de Logos:** Associe imagens a estabelecimentos normalizados.
- **Edição vs Criação:** Interface distingue entre adicionar novo logo ou atualizar existente.
- **Visualização:** Logos aparecem nas listagens de transações para fácil identificação.

### Seleção de Bases para Salvamento

O sistema permite duas formas de salvar transações:

1. **Salvar Todas**: Checkbox "Selecionar Todas" marca todas as origens
2. **Salvar Selecionadas**: Escolha individualmente quais origens salvar:
   - ☑️ Fatura Itaú (3 arquivos - out/nov/dez 2025)
   - ☑️ Extrato Itaú Person
   - ☑️ Mercado Pago (3 arquivos)

Apenas as transações das origens selecionadas serão salvas no `journal_entries`.

### Dashboard por Origem

O dashboard exibe estatísticas separadas por origem:

**Para Faturas:**
- Valor total da fatura
- Breakdown por TipoGasto (Fixo, Ajustável, etc.)
- Quantidade de transações

**Para Extratos:**
- Soma total de despesas
- Soma total de receitas
- Saldo líquido
- Quantidade de transações

## 🔒 Segurança e Boas Práticas

- **Sessões:** Uso de Flask sessions para armazenar uploads temporários
- **Validação:** WTForms para validação de formulários
- **SQL Injection:** SQLAlchemy ORM previne ataques
- **File Upload:** Validação de extensões e tamanho máximo
- **Audit Log:** Rastreamento de todas as modificações
- **Backup:** Sempre faça backup do `financas.db` antes de mudanças grandes

## 📝 Logs e Debug

### Habilitar modo debug
Em `app.py`:
```python
app.run(debug=True)
```

### Logs de classificação
O classificador imprime logs durante o processamento:
```
✓ Carregadas 150 marcações válidas da base
Múltiplos matches para "SUPERMERCADO EXTRA": ['SUPERMERCADO', 'EXTRA']
🔗 Transferências marcadas: 5
```

## 🔄 Funcionalidades Implementadas

- [x] **Dashboard Analítico Completo:** KPIs, gráficos interativos com Chart.js 4.4.0
- [x] **Sistema de Upload Multi-formato:** CSV (Itaú), XLS (Extrato), XLSX (Mercado Pago)  
- [x] **Classificação Automática Inteligente:** Base de padrões + histórico + palavras-chave
- [x] **Sistema de Toggle para Dashboard:** Controle granular de inclusão de transações
- [x] **Gestão de Logos:** Upload e associação de imagens aos estabelecimentos
- [x] **Deduplicação Automática:** Prevenção de duplicatas contra base histórica
- [x] **Interface de Validação Manual:** Para transações não classificadas automaticamente
- [x] **API REST:** Endpoints para dados de transações e detalhes
- [x] **Audit Log Completo:** Rastreamento de todas as operações do sistema
- [x] **Formatação Brasileira:** Valores, datas e separadores no padrão nacional

## 🔄 Roadmap Futuro

- [ ] Detector inteligente de transferências entre contas
- [ ] Exportação avançada para Excel/CSV com formatação
- [ ] Dashboard de tendências e previsões financeiras  
- [ ] API REST completa para integrações externas
- [ ] Sistema multi-usuário com autenticação e permissões
- [ ] Backup automático e versionamento do banco de dados
- [ ] Importação de formatos OFX/QIF de outros bancos
- [ ] Notificações e alertas de gastos por categoria
- [ ] Análise de padrões e sugestões de economia

## 📄 Licença

Uso pessoal - Emanuel Guerra Leandro

---

**Versão:** 2.0.0  
**Última atualização:** 26/12/2025  
**Status:** Produção ✅ - Sistema completo e funcional
