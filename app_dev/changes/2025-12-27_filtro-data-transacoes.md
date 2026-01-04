# Filtro de Data em Transações

**Data:** 2025-12-27  
**Tipo:** Feature  
**Versão:** 2.1.0 → 2.1.1

## 🎯 Resumo

Implementação de filtro por intervalo de datas nas páginas de transações (Admin e Dashboard), permitindo buscar transações entre duas datas específicas dentro do mesmo mês ou entre meses diferentes.

## 🔧 Problema Resolvido

### Situação Anterior
- Filtro de mês só permitia buscar transações de um mês inteiro (formato YYYYMM)
- Impossível filtrar transações entre dias específicos (ex: 07/10/2025 a 26/10/2025)
- Coluna `DT_Fatura` não possui informação de dia

### Solução Implementada
- Uso da coluna `Data` (formato DD/MM/YYYY) para filtros precisos
- Conversão de DD/MM/YYYY → YYYYMMDD usando `substr()` do SQLite
- Inputs HTML5 `type="date"` para seleção intuitiva de datas
- Filtros funcionam independentemente ou em conjunto (data início + data fim)

## 📝 Alterações Técnicas

### 1. Template: `_macros/transacao_filters.html`

**Adicionados:** Campos de data no formulário de filtros

```html
<div class="col-md-2">
    <label for="data_inicio" class="form-label">
        <i class="fas fa-calendar-alt me-1"></i>Data Início
    </label>
    <input type="date" class="form-control" id="data_inicio" 
           name="data_inicio" value="{{ filtro_data_inicio }}">
</div>
<div class="col-md-2">
    <label for="data_fim" class="form-label">
        <i class="fas fa-calendar-check me-1"></i>Data Fim
    </label>
    <input type="date" class="form-control" id="data_fim" 
           name="data_fim" value="{{ filtro_data_fim }}">
</div>
```

### 2. Backend: `admin/routes.py` e `dashboard/routes.py`

**Lógica de Conversão e Filtragem:**

```python
# Captura parâmetros da URL
filtro_data_inicio = request.args.get('data_inicio', '')  # YYYY-MM-DD
filtro_data_fim = request.args.get('data_fim', '')        # YYYY-MM-DD

# Aplicar filtro de data
if filtro_data_inicio or filtro_data_fim:
    from sqlalchemy import text
    
    if filtro_data_inicio:
        data_inicio_num = filtro_data_inicio.replace('-', '')  # YYYYMMDD
        query = query.filter(
            text(f"substr(Data, 7, 4) || substr(Data, 4, 2) || substr(Data, 1, 2) >= '{data_inicio_num}'")
        )
    
    if filtro_data_fim:
        data_fim_num = filtro_data_fim.replace('-', '')  # YYYYMMDD
        query = query.filter(
            text(f"substr(Data, 7, 4) || substr(Data, 4, 2) || substr(Data, 1, 2) <= '{data_fim_num}'")
        )
```

### 3. Lógica SQL

**Conversão de formato:**
- Entrada: `"12/10/2025"` (DD/MM/YYYY)
- `substr(Data, 7, 4)` → `"2025"` (ano)
- `substr(Data, 4, 2)` → `"10"` (mês)
- `substr(Data, 1, 2)` → `"12"` (dia)
- Concatenação: `"20251012"` (YYYYMMDD)

**Comparação:**
- Input do usuário: `"2025-10-07"` → `"20251007"`
- SQL: `WHERE substr(...) >= '20251007' AND substr(...) <= '20251026'`

## 🐛 Problemas Enfrentados e Soluções

### 1. SQLAlchemy: Operador de Concatenação

**Problema:**
```python
# ❌ ERRADO - Python interpreta + como soma matemática
data_convertida = (
    func.substr(JournalEntry.Data, 7, 4) +
    func.substr(JournalEntry.Data, 4, 2) +
    func.substr(JournalEntry.Data, 1, 2)
)
```

**Solução:**
```python
# ✅ CORRETO - SQL literal com operador || do SQLite
text(f"substr(Data, 7, 4) || substr(Data, 4, 2) || substr(Data, 1, 2) >= '{data_num}'")
```

### 2. CompileError com `.params()`

**Problema:**
```python
# ❌ ERRADO - CompileError: No literal value renderer available
text("substr(...) >= :data_inicio").params(data_inicio=data_inicio_num)
```

**Solução:**
```python
# ✅ CORRETO - f-string direta no SQL
text(f"substr(...) >= '{data_inicio_num}'")
```

## 🧪 Testes Realizados

### Teste 1: Raw SQL (Validação)
```sql
SELECT COUNT(*) FROM journal_entries 
WHERE substr(Data, 7, 4) || substr(Data, 4, 2) || substr(Data, 1, 2) >= '20250801' 
  AND substr(Data, 7, 4) || substr(Data, 4, 2) || substr(Data, 1, 2) <= '20250831';
```
**Resultado:** 83 transações encontradas ✅

### Teste 2: Aplicação Web
- **Filtro:** 01/08/2025 a 31/08/2025
- **Resultado:** 83 transações exibidas ✅
- **Validação:** Números batem com consulta SQL direta

## 📊 Impacto

### Funcionalidades Afetadas
- ✅ Admin: Página de transações
- ✅ Dashboard: Página de transações
- ✅ Filtros mantêm compatibilidade com filtros existentes (estabelecimento, categoria, tipo)

### Arquivos Modificados
1. `app/blueprints/admin/routes.py` - Lógica de filtro de data
2. `app/blueprints/dashboard/routes.py` - Lógica de filtro de data
3. `templates/_macros/transacao_filters.html` - Inputs de data
4. `templates/revisar_categoria.html` - CSS para coluna Ações sticky

### Performance
- **Impacto:** Mínimo - SQLite executa `substr()` eficientemente
- **Indexação:** Não requer índice adicional (filtros já usam DT_Fatura como base)

## ✅ Resultado Final

### Antes
- Apenas filtro de mês completo (YYYYMM)
- Não permitia buscas dentro do mesmo mês

### Depois
- Filtro preciso por intervalo de datas
- Suporte a:
  - Data início apenas (todas após data)
  - Data fim apenas (todas até data)
  - Intervalo completo (entre duas datas)
- UX intuitiva com calendário HTML5

## 🔄 Próximos Passos (Futuro)

- [ ] Adicionar atalhos rápidos ("Últimos 7 dias", "Este mês", "Mês passado")
- [ ] Exportar resultados filtrados para CSV/Excel
- [ ] Adicionar cache de consultas frequentes
- [ ] Considerar migração de coluna Data para formato YYYY-MM-DD no banco

## 📌 Notas Técnicas

- **SQLite:** Operador de concatenação é `||`, não `+`
- **SQLAlchemy:** `text()` com f-string é mais simples que construção ORM para SQL específico
- **HTML5:** `<input type="date">` gera seletor nativo do navegador
- **Formato interno:** YYYYMMDD permite comparação lexicográfica direta

## 🎨 Melhorias UX Relacionadas

- Coluna "Origem" limitada a 200px com ellipsis
- Coluna "Ações" sticky (sempre visível na rolagem horizontal)
- Validação visual removida após testes bem-sucedidos

---

**Commit:** `feat: Adiciona filtro de data por intervalo em transações`
**Tags:** #feature #filtros #datas #ux #sqlalchemy
