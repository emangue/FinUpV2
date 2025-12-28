# Implementação de Views Consolidadas no Dashboard

**Data:** 2025-12-28  
**Versão:** 3.0.2-dev → 3.0.3 (pendente)  
**Tipo:** MINOR (nova funcionalidade)  
**Autor:** GitHub Copilot  

## 📋 Resumo

Implementada funcionalidade de visualização consolidada no dashboard, permitindo que usuários com contas conectadas vejam dados financeiros combinados de múltiplas contas em uma única visualização.

## 🎯 Objetivo

Permitir que usuários conectados (ex: casal) possam alternar entre:
- **Modo Individual:** Ver apenas suas próprias transações e análises
- **Modo Consolidado:** Ver dados combinados de todas as contas conectadas que ativaram a flag `view_consolidated`

## 🔧 Mudanças Técnicas

### 1. Helper Function: `get_user_ids_for_view()`

**Localização:** `app/blueprints/dashboard/routes.py` (linhas ~20-48)

**Funcionalidade:**
- Recebe `current_user_id`, `db` e `view_mode` ('individual' ou 'consolidated')
- Retorna lista de user IDs a serem incluídos nas queries
- Verifica relacionamentos bidirecionais (user_id → connected_user_id E vice-versa)
- Filtra apenas relacionamentos aceitos com `view_consolidated=True`
- Remove duplicatas usando `set()`

**Código:**
```python
def get_user_ids_for_view(current_user_id, db, view_mode='individual'):
    """Determina quais user_ids devem ser incluídos nas queries baseado no modo de visualização"""
    if view_mode == 'individual':
        return [current_user_id]
    
    # Modo consolidado: incluir contas conectadas
    user_ids = [current_user_id]
    
    # Relacionamentos iniciados pelo usuário atual
    relationships_initiated = db.query(UserRelationship).filter(
        UserRelationship.user_id == current_user_id,
        UserRelationship.status == 'accepted',
        UserRelationship.view_consolidated == True
    ).all()
    for rel in relationships_initiated:
        user_ids.append(rel.connected_user_id)
    
    # Relacionamentos recebidos pelo usuário atual
    relationships_received = db.query(UserRelationship).filter(
        UserRelationship.connected_user_id == current_user_id,
        UserRelationship.status == 'accepted',
        UserRelationship.view_consolidated == True
    ).all()
    for rel in relationships_received:
        user_ids.append(rel.user_id)
    
    return list(set(user_ids))  # Remove duplicatas
```

### 2. Atualização de Queries no Dashboard

**Arquivos Modificados:**
- `app/blueprints/dashboard/routes.py` (função `index()`)
- `app/blueprints/dashboard/routes.py` (função `transacoes()`)

**Total de Queries Atualizadas:** 28 queries

**Padrão de Mudança:**
```python
# ANTES (modo individual apenas)
.filter(JournalEntry.user_id == current_user.id)

# DEPOIS (suporta ambos os modos)
user_ids = get_user_ids_for_view(current_user.id, db, view_mode)
.filter(JournalEntry.user_id.in_(user_ids))
```

**Queries Modificadas:**

**Na função `index()`:**
1. `meses_query` - Lista de meses disponíveis
2. `total_despesas` - Total de despesas do mês
3. `total_despesas_anterior` - Comparação mês anterior
4. `total_receitas` - Total de receitas do mês
5. `total_receitas_anterior` - Comparação mês anterior
6. `total_transacoes` - Contagem de transações
7. `transacoes_classificadas` - Transações com grupo
8. `total_estabelecimentos` - Estabelecimentos únicos
9. `receitas_ytd` - Receitas Year-to-Date
10. `cartao_ytd` - Cartão de crédito YTD
11. `despesas_ytd` - Despesas gerais YTD
12. `investimento_ytd_raw` - Investimentos YTD
13. `grupos_query` - Distribuição por grupo
14. `total_atual` (loop grupos) - Comparação por grupo
15. `total_anterior` (loop grupos) - Comparação anterior
16. `top_transacoes_query` - Top 10 transações
17. `ultimas_transacoes` - Últimas 10 transações
18. `despesas_mes` (loop 6 meses) - Evolução mensal
19. `receitas_mes` (loop 6 meses) - Evolução mensal
20-27. Breakdown 6 meses (despesas_gerais, cartao, receitas, investimentos) x 6 meses

**Na função `transacoes()`:**
1. Query base de transações filtradas

### 3. UI - Toggle de Visualização

**Arquivos Modificados:**
- `templates/dashboard.html`
- `templates/transacoes.html`

**Componente Adicionado:**
```html
{% if has_consolidated %}
<div class="btn-group shadow-sm" role="group" aria-label="Modo de Visualização">
    <a href="{{ url_for('dashboard.index', mes=mes_atual, view='individual') }}" 
       class="btn btn-sm {% if view_mode == 'individual' %}btn-primary{% else %}btn-outline-primary{% endif %}">
        <i class="fas fa-user me-1"></i>Minha Conta
    </a>
    <a href="{{ url_for('dashboard.index', mes=mes_atual, view='consolidated') }}" 
       class="btn btn-sm {% if view_mode == 'consolidated' %}btn-primary{% else %}btn-outline-primary{% endif %}">
        <i class="fas fa-users me-1"></i>Consolidado
    </a>
</div>
{% endif %}
```

**Lógica Condicional:**
- Toggle só aparece se `has_consolidated=True`
- `has_consolidated` é calculado verificando se há relacionamentos aceitos com `view_consolidated=True`
- Estado ativo visual baseado em `view_mode`

### 4. Contexto de Template

**Adicionado aos renders:**
```python
# Em index()
view_mode=view_mode,
has_consolidated=has_consolidated

# Em transacoes()
view_mode=view_mode,
has_consolidated=has_consolidated
```

### 5. Navegação - Preservação de Estado

**Modificação em `voltarDashboard()` (transacoes.html):**
```javascript
// ANTES
window.location.href = `/dashboard/?mes=${mesOriginal}`;

// DEPOIS
const viewMode = urlParams.get('view') || 'individual';
window.location.href = `/dashboard/?mes=${mesOriginal}&view=${viewMode}`;
```

**Modificação em Link "Ver Todas":**
```html
<!-- ANTES -->
<a href="{{ url_for('dashboard.transacoes', mes=mes_atual) }}">

<!-- DEPOIS -->
<a href="{{ url_for('dashboard.transacoes', mes=mes_atual, view=view_mode) }}">
```

### 6. Imports Necessários

**Adicionado:**
```python
from sqlalchemy import and_  # Para condições compostas no has_consolidated
from app.models import UserRelationship  # Para verificar relacionamentos
```

## 🔐 Segurança

**Validações Implementadas:**
1. ✅ Apenas relacionamentos com `status='accepted'` são considerados
2. ✅ Apenas relacionamentos com `view_consolidated=True` são incluídos
3. ✅ Verificação bidirecional (A→B e B→A)
4. ✅ `@login_required` mantido em todas as rotas
5. ✅ Usuário sempre vê seus próprios dados, mesmo em modo individual
6. ✅ Não é possível forçar visualização consolidada via URL se não houver relacionamentos válidos

**Fluxo de Autorização:**
```
User A solicita view=consolidated
    ↓
Sistema busca relacionamentos de A
    ↓
Filtra: status='accepted' AND view_consolidated=True
    ↓
Verifica ambas direções:
    - A conectou com B (user_id=A, connected_user_id=B)
    - B conectou com A (user_id=B, connected_user_id=A)
    ↓
Retorna: [A, B] (se ambos ativos) ou [A] (se nenhum ativo)
    ↓
Queries usam: WHERE user_id IN ([A, B])
```

## 📊 Impacto nas Métricas

**Modo Individual:**
- Comportamento idêntico à versão anterior
- Apenas dados do usuário logado

**Modo Consolidado:**
- **Total Despesas:** Soma de todos os user_ids
- **Total Receitas:** Soma de todos os user_ids
- **Saldo:** Receitas - Despesas (consolidado)
- **Top Transações:** Das maiores entre todas as contas
- **Distribuição por Grupo:** Agregado de todas as contas
- **YTD (Year-to-Date):** Acumulado de todas as contas no ano
- **Breakdown 6 Meses:** Histórico consolidado

**Métricas que permanecem individualizadas:**
- Percentual de transações classificadas (não agrega por usuário)
- Média diária (calculada sobre total consolidado)

## 🎨 UX/UI

**Localização do Toggle:**
- Dashboard: Entre seletor de mês e botão "Adicionar"
- Transações: Entre título e botão "Voltar ao Dashboard"

**Estados Visuais:**
- **Individual:** Botão azul sólido (btn-primary), ícone `fa-user`
- **Consolidado:** Botão azul sólido (btn-primary), ícone `fa-users`
- **Inativo:** Botão outline azul (btn-outline-primary)

**Comportamento:**
- Clique alterna entre modos
- URL atualiza: `?view=individual` ou `?view=consolidated`
- Estado preservado na navegação entre dashboard e transações
- Se não houver relacionamentos, toggle não aparece

## 🧪 Testes Necessários

### Cenário 1: Usuário sem Relacionamentos
- [ ] Toggle NÃO deve aparecer
- [ ] URL `?view=consolidated` deve funcionar como `individual`
- [ ] Todas as métricas devem mostrar apenas dados do usuário

### Cenário 2: Usuário com Relacionamento Pendente
- [ ] Toggle NÃO deve aparecer (status != 'accepted')
- [ ] Comportamento igual ao Cenário 1

### Cenário 3: Relacionamento Aceito mas view_consolidated=False
- [ ] Toggle NÃO deve aparecer
- [ ] Comportamento igual ao Cenário 1

### Cenário 4: Relacionamento Aceito e view_consolidated=True
- [ ] Toggle DEVE aparecer
- [ ] Modo individual: ver apenas dados próprios
- [ ] Modo consolidado: ver soma de ambas as contas
- [ ] Alternar entre modos funciona corretamente
- [ ] Navegação preserva estado do modo
- [ ] Top transações incluem ambas as contas
- [ ] Gráficos refletem dados combinados

### Cenário 5: Relacionamento Bidirecional
- [ ] Usuário A vê dados de B quando view_consolidated=True
- [ ] Usuário B vê dados de A quando view_consolidated=True
- [ ] Se A desativa consolidado, A para de ver B (mas B ainda vê A se ativo)

### Cenário 6: Múltiplos Relacionamentos
- [ ] Usuário A conectado com B e C
- [ ] Modo consolidado mostra: dados de A + B + C
- [ ] Dedupplicação funciona (sem contar duplicado)

## 📈 Performance

**Impacto esperado:**
- **Individual:** Nenhum (queries idênticas à versão anterior)
- **Consolidado:** Leve aumento (IN clause com 2-3 user_ids)
- **Otimização:** Índice em `journal_entry.user_id` já existe

**Queries adicionais:**
- +2 queries por page load (verificar `has_consolidated`)
- Complexidade: O(1) para 99% dos casos (1-2 relacionamentos)

## 🔄 Compatibilidade

**Versões Anteriores:**
- ✅ Dados existentes continuam funcionando
- ✅ Usuários sem relacionamentos não veem diferença
- ✅ URLs antigas (`?mes=2025-12`) continuam funcionando
- ✅ Padrão é `view=individual` se não especificado

**Breaking Changes:**
- ❌ Nenhum

## 📝 Documentação para Usuário

**Como usar Views Consolidadas:**

1. **Conectar Contas:**
   - Ir em Perfil
   - Clicar em "Conectar Conta"
   - Inserir email do outro usuário
   - Aguardar aceitação

2. **Ativar Visualização Consolidada:**
   - Após aceitação, toggle "Ver Consolidado" aparece no Perfil
   - Ativar toggle para ambos os usuários

3. **Usar Dashboard Consolidado:**
   - Toggle "Minha Conta" / "Consolidado" aparece no topo
   - Clicar para alternar entre visualizações
   - Todas as métricas refletem soma das contas conectadas

4. **Desativar:**
   - Perfil → Desligar toggle "Ver Consolidado"
   - Toggle some automaticamente do dashboard

## ✅ Checklist de Implementação

- [x] Criar helper function `get_user_ids_for_view()`
- [x] Atualizar 28 queries em `index()`
- [x] Atualizar query em `transacoes()`
- [x] Adicionar `view_mode` ao contexto de templates
- [x] Implementar toggle UI em dashboard.html
- [x] Implementar toggle UI em transacoes.html
- [x] Preservar estado em navegação (voltarDashboard)
- [x] Preservar estado em links ("Ver Todas")
- [x] Importar `and_` do SQLAlchemy
- [x] Validar `has_consolidated` em ambas rotas
- [x] Documentar mudanças
- [ ] Testar todos os cenários
- [ ] Criar testes unitários
- [ ] Atualizar VERSION.md
- [ ] Commitar mudanças

## 🐛 Possíveis Bugs a Monitorar

1. **Query Performance:** Monitorar tempo de execução com múltiplas contas
2. **Dedupplicação:** Verificar se há transações duplicadas em queries específicas
3. **Estado de Navegação:** Confirmar que modo é preservado em todos os fluxos
4. **Edge Case:** Usuário com relacionamento aceito mas dados zerados

## 🔮 Melhorias Futuras

1. **Breakdown por Usuário:** No modo consolidado, mostrar subtotais por conta
2. **Filtro de Usuário:** Permitir filtrar dados de usuário específico no consolidado
3. **Indicador Visual:** Badge ou cor diferente para transações de outras contas
4. **Gráfico Comparativo:** Lado a lado de gastos individuais
5. **Export Consolidado:** Permitir exportar dados combinados
6. **Notificação:** Alertar quando outro usuário ativa/desativa consolidado
7. **Permissões Granulares:** Escolher quais métricas compartilhar (ex: apenas gastos, não receitas)

## 📚 Referências

- **User Story:** #MultiUser-ConsolidatedView
- **Related Issues:** #UserRelationship, #DataIsolation
- **Previous Version:** v3.0.2-dev (user_id filters)
- **Next Version:** v3.0.3 (após testes)
