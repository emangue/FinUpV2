# Sistema de Gestão Financeira Automatizada

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
├── templates/                      # Templates HTML (Jinja2)
│   ├── base.html                   # Template base
│   ├── upload.html                 # Página de upload/dashboard
│   ├── validar.html                # Validação manual
│   └── admin_padroes.html          # Admin de padrões
│
└── static/                         # Arquivos estáticos
    ├── css/
    │   └── style.css               # Estilos CSS
    └── js/
        └── main.js                 # JavaScript do frontend
```

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

### 2. Importação Inicial

```bash
# Importa dados do base_dados_geral.xlsx
python import_base_inicial.py
```

Isso criará:
- `financas.db` (banco SQLite)
- Popula `journal_entries`, `base_padroes`, `base_marcacoes`

### 3. Executar Aplicação

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

### Dashboard Analítico
O sistema agora conta com um dashboard completo na página inicial:
- **Filtros Temporais:** Selecione Mês/Ano para visualizar dados específicos.
- **KPIs:** Cards com Total de Despesas, Receitas e Saldo do período.
- **Gráficos Interativos:**
  - Distribuição de gastos por Grupo (Gráfico de Rosca)
  - Evolução de despesas e receitas (Gráfico de Barras)
- **Formatação Brasileira:** Valores em R$ e datas no padrão BR.
- **Botão "Ver Todas":** Acesso rápido à lista detalhada de transações do mês.

### Lista de Transações e Controle (Toggle)
Nova interface dedicada para visualização e gestão de transações mensais:
- **Listagem Detalhada:** Veja todas as transações do mês selecionado com logos, grupos e valores.
- **Toggle "Status Dashboard":** Interruptor interativo para incluir ou excluir transações dos cálculos do dashboard.
  - **Ligado (Verde):** Transação considerada nos totais e gráficos.
  - **Desligado (Cinza):** Transação ignorada (ex: investimentos, transferências internas), mas mantida no histórico.
- **Atualização em Tempo Real:** O dashboard recalcula automaticamente os totais ao alterar o status.

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

## 🔄 Atualizações Futuras

- [ ] Detector de transferências entre contas (atualmente marca para validação)
- [ ] Exportação para Excel/CSV
- [ ] Gráficos e dashboards analíticos
- [ ] API REST para integrações
- [ ] Multi-usuário com autenticação
- [ ] Backup automático do banco
- [ ] Importação de OFX/QIF

## 📄 Licença

Uso pessoal - Emanuel Guerra Leandro

---

**Versão:** 1.0.0  
**Última atualização:** 26/12/2025
