# Arquitetura de Componentes Compartilhados

## Princípio DRY (Don't Repeat Yourself)

Este projeto adota o princípio de **componentes reutilizáveis** para templates, garantindo:
- ✅ **Uma fonte de verdade**: Mudanças propagam para todos os lugares
- ✅ **Manutenção simplificada**: Corrigir bug uma vez corrige em todos
- ✅ **Consistência visual**: Todos os blueprints ficam iguais automaticamente
- ✅ **Testabilidade**: Testar componente isolado

---

## Estrutura de Diretórios

```
templates/
  ├── base.html                           # Layout base (navbar, footer, imports)
  │
  ├── _macros/                            # 🔧 Componentes pequenos reutilizáveis
  │   ├── transacao_filters.html          # Filtros de pesquisa
  │   ├── transacao_modal_edit.html       # Modal de edição
  │   └── (futuros componentes)
  │
  └── _partials/                          # 📦 Seções completas reutilizáveis
      └── (tabelas, cards, etc)

app/blueprints/
  ├── admin/templates/
  │   ├── admin_grupos.html               # Usa componentes compartilhados
  │   └── ...
  │
  ├── dashboard/templates/
  │   ├── dashboard.html                  # Usa componentes compartilhados
  │   ├── transacoes.html                 # Usa filtros + modal compartilhados
  │   └── ...
  │
  └── upload/templates/
      └── ...
```

---

## Componentes Existentes

### 1. `_macros/transacao_filters.html`

**Descrição:** Card completo de filtros para páginas de transações

**Uso:**
```jinja
{% include '_macros/transacao_filters.html' %}
```

**Variáveis esperadas:**
- `mes_atual` (str): Mês no formato `YYYY-MM`
- `filtro_estabelecimento` (str): Valor atual do filtro de estabelecimento
- `filtro_categoria` (str): Valor atual do filtro de categoria/grupo
- `filtro_tipo` (str): Valor atual do filtro de tipo (`despesa` ou `cartao`)
- `grupos_lista` (list): Lista de grupos para o select
- `soma_filtrada` (float, opcional): Soma total das transações filtradas

**Funcionalidades:**
- Filtro por estabelecimento (input text)
- Filtro por categoria/grupo (select)
- Filtro por tipo de transação (select)
- Botão de filtrar e limpar
- Exibição de filtros ativos com badges
- Soma total das transações filtradas (quando há filtros)

**Blueprints que usam:**
- `dashboard/transacoes.html`

**Exemplo de integração:**
```jinja
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <h1>Transações</h1>
    
    {# Inclui o componente compartilhado #}
    {% include '_macros/transacao_filters.html' %}
    
    {# Resto do conteúdo #}
    <table>...</table>
</div>
{% endblock %}
```

---

### 2. `_macros/transacao_modal_edit.html`

**Descrição:** Modal completo para edição de transações, incluindo JavaScript

**Uso:**
```jinja
{% include '_macros/transacao_modal_edit.html' %}
```

**Variáveis esperadas:**
- `grupos_lista` (list): Lista de grupos para o select de categoria

**Funcionalidades:**
- Modal Bootstrap 5
- Formulário com todos os campos editáveis
- JavaScript para carregar dados via AJAX
- JavaScript para salvar alterações via AJAX
- Feedback visual (SweetAlert2 ou alert padrão)

**Funções JavaScript incluídas:**
1. `abrirModalEditar(id)` - Carrega dados da transação e abre modal
2. `salvarEdicaoTransacao()` - Salva alterações via POST

**Blueprints que usam:**
- `dashboard/transacoes.html`

**Exemplo de integração:**
```jinja
{% extends "base.html" %}

{% block content %}
<table>
    <tr onclick="abrirModalEditar({{ trans.id }})">
        <td>{{ trans.Estabelecimento }}</td>
        <td>{{ trans.Valor }}</td>
    </tr>
</table>

{# Inclui o componente compartilhado #}
{% include '_macros/transacao_modal_edit.html' %}
{% endblock %}
```

**Requisitos backend:**
- Rota: `dashboard.api_transacao_completa` (GET com param `id`)
- Rota: `dashboard.api_atualizar_transacao` (POST com JSON body)

---

## Como Adicionar Novo Componente

### 1. Criar arquivo em `_macros/` ou `_partials/`

```bash
touch templates/_macros/meu_componente.html
```

### 2. Adicionar documentação no cabeçalho

```jinja
{# 
  Componente: Descrição do Componente
  Uso: {% include '_macros/meu_componente.html' %}
  
  Variáveis esperadas:
  - variavel1: Descrição
  - variavel2: Descrição
  
  Funcionalidades:
  - Feature 1
  - Feature 2
#}

<div class="meu-componente">
    {# Código do componente #}
</div>
```

### 3. Usar nos blueprints

```jinja
{% include '_macros/meu_componente.html' %}
```

### 4. Documentar neste arquivo

Adicionar seção com:
- Nome e descrição
- Variáveis esperadas
- Funcionalidades
- Blueprints que usam
- Exemplo de integração

---

## Workflow de Modificação

### Quando modificar componente compartilhado:

1. **Identificar impacto**
   ```bash
   # Buscar todos os arquivos que usam o componente
   grep -r "transacao_filters.html" app/blueprints/
   ```

2. **Modificar componente**
   - Editar arquivo em `templates/_macros/`
   - Atualizar documentação no cabeçalho

3. **Testar em todos os contextos**
   - Dashboard de transações
   - Admin de transações
   - Qualquer outro blueprint que use

4. **Reiniciar servidor**
   ```bash
   lsof -ti:5001 | xargs kill -9 2>/dev/null
   /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/venv/bin/python run.py
   ```

5. **Validar funcionamento**
   - Verificar filtros funcionam
   - Verificar modal abre e salva
   - Verificar JavaScript não tem erros

---

## Boas Práticas

### ✅ Fazer

1. **Sempre documentar** variáveis esperadas no cabeçalho
2. **Usar `request.path`** ao invés de `url_for()` quando aplicável (mais genérico)
3. **Incluir JavaScript** no próprio componente se for específico dele
4. **Testar isoladamente** antes de integrar
5. **Manter componentes pequenos** e focados em uma responsabilidade

### ❌ Evitar

1. ❌ Duplicar código HTML entre templates
2. ❌ Criar componente muito grande e monolítico
3. ❌ Assumir contexto específico (deve ser genérico)
4. ❌ Esquecer de documentar variáveis
5. ❌ Modificar sem testar em todos os lugares que usa

---

## Exemplos Futuros

### Componentes que podem ser criados:

1. **`_macros/card_metrica.html`**
   - Card de métrica do dashboard
   - Variáveis: `titulo`, `valor`, `icone`, `cor`

2. **`_macros/tabela_transacoes.html`**
   - Tabela completa de transações com DataTables
   - Variáveis: `transacoes`, `permite_editar`, `permite_deletar`

3. **`_macros/breadcrumb.html`**
   - Breadcrumb de navegação
   - Variáveis: `items` (lista de {texto, url})

4. **`_macros/alerta_feedback.html`**
   - Alerta de sucesso/erro consistente
   - Variáveis: `tipo`, `mensagem`, `dismissible`

---

## Versionamento de Componentes

Componentes compartilhados seguem o versionamento do projeto:

- **MAJOR**: Mudança breaking (remover variável obrigatória, mudar estrutura)
- **MINOR**: Nova funcionalidade (adicionar variável opcional, novo recurso)
- **PATCH**: Bug fix ou ajuste de estilo

**Documentar no CHANGELOG.md**:
```markdown
### [2.2.0] - 2025-12-27
#### Added
- Componente compartilhado `_macros/transacao_filters.html`
- Componente compartilhado `_macros/transacao_modal_edit.html`
```

---

## Troubleshooting

### Componente não aparece

1. Verificar caminho correto: `_macros/nome.html`
2. Verificar sintaxe: `{% include '_macros/nome.html' %}`
3. Reiniciar servidor (Flask precisa recarregar)
4. Verificar se variáveis estão sendo passadas no `render_template()`

### JavaScript do componente não funciona

1. Verificar se `<script>` está dentro do componente
2. Verificar se não há conflito de nomes de funções
3. Abrir console do navegador para ver erros
4. Verificar se URLs das rotas estão corretas

### Componente funciona em um lugar mas não em outro

1. Verificar se todas as variáveis esperadas são passadas
2. Verificar se rota backend existe no blueprint específico
3. Verificar se contexto é diferente (admin vs dashboard)

---

## Conclusão

A arquitetura de componentes compartilhados:
- 📦 **Centraliza** código comum
- 🔧 **Facilita** manutenção
- ✅ **Garante** consistência
- 🚀 **Acelera** desenvolvimento

**Sempre priorizar reutilização sobre duplicação!**
