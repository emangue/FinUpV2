# 📋 Próximos Passos - Sistema de Budget Hierárquico

**Status:** Backend completo ✅ | Frontend parcial ⏳

**Última atualização:** 11 de janeiro de 2026

---

## ✅ Implementado

### Backend (100% completo)
- ✅ Modelo `BudgetCategoriaConfig` (categorias customizáveis)
- ✅ Modelo `BudgetGeralHistorico` (audit log de ajustes)
- ✅ Coluna `categoria_orcamento_id` em `journal_entries`
- ✅ Coluna `total_mensal` em `budget_geral`
- ✅ Migration executada com sucesso (6 categorias padrão seedadas)
- ✅ Repository completo (CRUD + reorder + tipos_gasto)
- ✅ Service com 10 métodos novos
- ✅ 7 endpoints REST implementados

### Frontend (60% completo)
- ✅ Dependências instaladas (@dnd-kit, react-colorful)
- ✅ Página de Configurações (`/budget/configuracoes`)
  - Color picker com HexColorPicker
  - Input de budget total mensal
  - Grid de categorias com metadados
- ✅ Página Meta Detalhada refatorada (`/budget/detalhada`)
  - Carregamento dinâmico de categorias
  - Drag & drop funcional com @dnd-kit
  - Reordenação persiste no backend
  - Cores e metadados visíveis
- ✅ Link "Configurações" adicionado à sidebar

---

## 📝 Pendente (3 tarefas principais)

### 1️⃣ Modificar Meta Geral (`/budget/page.tsx`) - ALTA PRIORIDADE

**Objetivo:** Adicionar controle de budget total com validação e alertas

**Implementação:**

#### Frontend - Adicionar seção de Budget Total
```tsx
// No topo da página, antes dos cards de categorias
<Card>
  <CardHeader>
    <CardTitle>Budget Total Mensal</CardTitle>
    <CardDescription>
      Defina o teto de gastos do mês. Ajustes automáticos podem ocorrer.
    </CardDescription>
  </CardHeader>
  <CardContent>
    <div className="flex items-end gap-4">
      <div className="flex-1">
        <Label>Total Mensal</Label>
        <Input
          type="number"
          value={totalMensal}
          onChange={(e) => setTotalMensal(parseFloat(e.target.value))}
          placeholder="Ex: 50000.00"
        />
      </div>
      <div className="flex-1">
        <Label>Soma das Categorias</Label>
        <div className="text-2xl font-bold">
          R$ {somaCateg.toFixed(2)}
        </div>
      </div>
      <div className="flex-1">
        <Label>Status</Label>
        {somaCateg > totalMensal ? (
          <div className="text-red-600 font-semibold">
            ⚠️ Acima em R$ {(somaCateg - totalMensal).toFixed(2)}
          </div>
        ) : (
          <div className="text-green-600 font-semibold">
            ✅ Dentro do limite
          </div>
        )}
      </div>
    </div>
  </CardContent>
</Card>
```

#### Mudar endpoint de save
```tsx
// ANTES: /api/v1/budget/geral/bulk-upsert
// DEPOIS: /api/v1/budget/geral/bulk-upsert-validado

const handleSave = async () => {
  const response = await fetch(
    `${API_CONFIG.BACKEND_URL}/api/v1/budget/geral/bulk-upsert-validado?user_id=1`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mes_referencia: mesReferencia,
        budgets: items,
        total_mensal: totalMensal,
      }),
    }
  );

  const result = await response.json();
  
  // Verificar se houve ajuste automático
  if (result.total_ajustado) {
    toast.warning(
      `⚠️ Budget total ajustado de R$ ${result.valor_anterior} para R$ ${result.novo_total} porque a soma das categorias ultrapassou o limite.`
    );
  }
};
```

#### Adicionar botão de histórico
```tsx
<Button
  variant="outline"
  onClick={() => setShowHistory(true)}
>
  📊 Ver Histórico de Ajustes
</Button>

{showHistory && (
  <Dialog>
    {/* Carregar /budget/geral/historico?mes_referencia=... */}
    {/* Mostrar tabela com ajustes (data, valor_anterior, valor_novo, motivo) */}
  </Dialog>
)}
```

**Arquivos afetados:**
- `app_dev/frontend/src/app/budget/page.tsx` (modificar)

**Tempo estimado:** 2-3 horas

---

### 2️⃣ Atualizar Dashboard com TOP 5 + Outros - ALTA PRIORIDADE

**Objetivo:** Dashboard mostra apenas 5 categorias principais + agregado "Outros"

**Implementação:**

#### Backend - Criar endpoint de realizado hierárquico
```python
# app_dev/backend/app/domains/budget/service.py

def calcular_realizado_hierarquico(
    self,
    user_id: int,
    mes_referencia: str
) -> List[Dict]:
    """
    Calcula valores realizados por categoria na ordem hierárquica.
    Retorna TOP 5 + "Outros".
    """
    # 1. Carregar categorias ordenadas
    categorias = self.categoria_config_repo.get_ordered_by_user(user_id, apenas_ativas=True)
    
    # 2. Para cada categoria, calcular realizado
    resultados = []
    for cat in categorias:
        # Query journal_entries filtrando por:
        # - Se fonte_dados == GRUPO: WHERE GRUPO = filtro_valor
        # - Se fonte_dados == TIPO_TRANSACAO: WHERE TipoTransacao = filtro_valor
        # - Filtrar por tipos_gasto_incluidos se especificado
        # - Somar valores WHERE Data LIKE 'mes_referencia%'
        
        valor_realizado = self._calcular_realizado_categoria(
            user_id, mes_referencia, cat
        )
        
        resultados.append({
            'categoria': cat.nome_categoria,
            'cor': cat.cor_visualizacao,
            'valor_planejado': self._get_planejado(user_id, mes_referencia, cat.nome_categoria),
            'valor_realizado': valor_realizado,
        })
    
    # 3. Ordenar por valor_planejado DESC
    resultados_ordenados = sorted(resultados, key=lambda x: x['valor_planejado'], reverse=True)
    
    # 4. TOP 5 + agregação
    top5 = resultados_ordenados[:5]
    resto = resultados_ordenados[5:]
    
    outros = {
        'categoria': 'Outros',
        'cor': '#94a3b8',
        'valor_planejado': sum(r['valor_planejado'] for r in resto),
        'valor_realizado': sum(r['valor_realizado'] for r in resto),
    }
    
    return top5 + [outros]
```

#### Backend - Adicionar endpoint
```python
# app_dev/backend/app/domains/budget/router.py

@router.get("/realizado-hierarquico")
def get_realizado_hierarquico(
    mes_referencia: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = BudgetService(db)
    return service.calcular_realizado_hierarquico(user_id, mes_referencia)
```

#### Frontend - Modificar BudgetVsActual
```tsx
// app_dev/frontend/src/features/dashboard/components/budget-vs-actual.tsx

const [categorias, setCategorias] = useState([]);

useEffect(() => {
  fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/realizado-hierarquico?mes_referencia=${mesAtual}`)
    .then(res => res.json())
    .then(data => setCategorias(data))
}, [mesAtual]);

// Renderizar apenas as categorias retornadas (TOP 5 + Outros)
{categorias.map(cat => (
  <div key={cat.categoria} className="flex items-center gap-2">
    <div
      className="w-3 h-3 rounded"
      style={{ backgroundColor: cat.cor }}
    />
    <div className="flex-1">
      <div className="flex justify-between">
        <span>{cat.categoria}</span>
        <span>R$ {cat.valor_realizado.toFixed(2)} / R$ {cat.valor_planejado.toFixed(2)}</span>
      </div>
      <Progress value={(cat.valor_realizado / cat.valor_planejado) * 100} />
    </div>
  </div>
))}

// Adicionar link "Ver Todas →"
<Button variant="link" asChild>
  <Link href="/budget/todas">Ver Todas as Categorias →</Link>
</Button>
```

**Arquivos afetados:**
- `app_dev/backend/app/domains/budget/service.py` (adicionar método)
- `app_dev/backend/app/domains/budget/router.py` (adicionar endpoint)
- `app_dev/frontend/src/features/dashboard/components/budget-vs-actual.tsx` (modificar)

**Tempo estimado:** 3-4 horas

---

### 3️⃣ Criar Página "Todas as Categorias" - MÉDIA PRIORIDADE

**Objetivo:** Visualização completa de todas as categorias com planejado vs realizado

**Implementação:**

#### Criar nova página
```tsx
// app_dev/frontend/src/app/budget/todas/page.tsx

export default function TodasCategoriasPage() {
  const [categorias, setCategorias] = useState([]);
  const mesAtual = '2026-01';

  useEffect(() => {
    fetch(`${API_CONFIG.BACKEND_URL}/api/v1/budget/realizado-hierarquico?mes_referencia=${mesAtual}&incluir_todas=true`)
      .then(res => res.json())
      .then(data => setCategorias(data))
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Todas as Categorias</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categorias.map(cat => (
          <Card key={cat.categoria}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: cat.cor }}
                >
                  <DollarSign className="h-6 w-6 text-white" />
                </div>
                <CardTitle>{cat.categoria}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Planejado</span>
                  <span className="font-semibold">R$ {cat.valor_planejado.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Realizado</span>
                  <span className="font-semibold">R$ {cat.valor_realizado.toFixed(2)}</span>
                </div>
                <Progress
                  value={(cat.valor_realizado / cat.valor_planejado) * 100}
                />
                {cat.valor_realizado > cat.valor_planejado && (
                  <Badge variant="destructive">
                    Acima em R$ {(cat.valor_realizado - cat.valor_planejado).toFixed(2)}
                  </Badge>
                )}
              </div>
              <div className="mt-4 pt-4 border-t">
                <Button variant="outline" size="sm" asChild className="w-full">
                  <Link href="/budget/detalhada">Editar Meta</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

#### Adicionar link na sidebar
```tsx
// app_dev/frontend/src/components/app-sidebar.tsx

{
  title: "Orçamento",
  items: [
    {title: "Meta Geral", url: "/budget"},
    {title: "Meta Detalhada", url: "/budget/detalhada"},
    {title: "Todas as Categorias", url: "/budget/todas"},  // NOVO
    {title: "Configurações", url: "/budget/configuracoes"},
  ]
}
```

**Arquivos afetados:**
- `app_dev/frontend/src/app/budget/todas/page.tsx` (criar)
- `app_dev/frontend/src/components/app-sidebar.tsx` (modificar)

**Tempo estimado:** 2 horas

---

## 🔧 Tarefas Opcionais (Melhorias)

### 4️⃣ Background Job para Popular categoria_orcamento_id

**Objetivo:** Preencher coluna calculada para performance de queries

```python
# app_dev/backend/scripts/populate_categoria_orcamento.py

"""
Para cada transação em journal_entries:
1. Carregar categorias ordenadas do user
2. Iterar categorias na ordem:
   - Se categoria.fonte_dados == GRUPO: 
       if transacao.GRUPO == categoria.filtro_valor:
           transacao.categoria_orcamento_id = categoria.id
           break
   - Se categoria.fonte_dados == TIPO_TRANSACAO:
       if transacao.TipoTransacao == categoria.filtro_valor:
           transacao.categoria_orcamento_id = categoria.id
           break
   - Verificar tipos_gasto_incluidos se especificado
3. Commit em batches de 1000
"""
```

**Benefício:** Queries do dashboard ficam 10x+ mais rápidas

**Tempo estimado:** 1-2 horas

---

### 5️⃣ Modal de Edição de tipos_gasto na Meta Detalhada

**Objetivo:** Permitir editar quais tipos_gasto pertencem a cada categoria

```tsx
// Adicionar botão "Editar Tipos" no accordion item
<Button
  size="sm"
  variant="ghost"
  onClick={() => setEditingTiposGasto(categoria.id)}
>
  ✏️ Editar Tipos de Gasto
</Button>

// Modal com lista de checkboxes
<Dialog open={editingTiposGasto === categoria.id}>
  <DialogContent>
    <DialogTitle>Tipos de Gasto - {categoria.nome_categoria}</DialogTitle>
    <div className="space-y-2">
      {todosTiposGasto.map(tipo => (
        <label key={tipo} className="flex items-center gap-2">
          <Checkbox
            checked={categoria.tipos_gasto_incluidos.includes(tipo)}
            onChange={(checked) => handleToggleTipo(categoria.id, tipo, checked)}
          />
          {tipo}
        </label>
      ))}
    </div>
    <Button onClick={handleSaveTiposGasto}>Salvar</Button>
  </DialogContent>
</Dialog>
```

**Endpoint usado:** `PATCH /budget/categorias-config/{id}/tipos-gasto`

**Tempo estimado:** 2 horas

---

### 6️⃣ Animações e Feedback Visual

**Melhorias de UX:**
- Toast notifications (react-hot-toast)
- Loading skeletons
- Animações de drag (framer-motion)
- Confirmação de deleção de categorias
- Preview de alterações antes de salvar

**Tempo estimado:** 2-3 horas

---

## 📊 Resumo de Prioridades

| Tarefa | Prioridade | Tempo | Impacto |
|--------|-----------|-------|---------|
| 1. Meta Geral com Budget Total | 🔴 Alta | 2-3h | Completa feature principal |
| 2. Dashboard TOP 5 + Outros | 🔴 Alta | 3-4h | Visualização principal |
| 3. Página Todas Categorias | 🟡 Média | 2h | Completude da interface |
| 4. Popular categoria_orcamento_id | 🟢 Baixa | 1-2h | Performance |
| 5. Modal Editar tipos_gasto | 🟢 Baixa | 2h | Flexibilidade |
| 6. Melhorias de UX | 🟢 Baixa | 2-3h | Polimento |

**Total estimado para MVP:** ~7-9 horas (tarefas 1, 2, 3)

---

## 🧪 Checklist de Testes

Após implementar as 3 tarefas principais:

- [ ] Criar nova categoria em Configurações
- [ ] Mudar cor da categoria
- [ ] Ir para Meta Detalhada e arrastar categoria
- [ ] Verificar que ordem mudou
- [ ] Editar valores de tipos_gasto na categoria
- [ ] Salvar meta detalhada
- [ ] Ir para Meta Geral
- [ ] Definir budget total menor que soma
- [ ] Salvar e verificar alerta de ajuste
- [ ] Ver histórico de ajustes
- [ ] Ir para Dashboard
- [ ] Verificar que aparecem TOP 5 + Outros
- [ ] Clicar em "Ver Todas"
- [ ] Verificar página com todas as categorias
- [ ] Validar cores corretas
- [ ] Validar cálculos de planejado vs realizado

---

## 📞 Suporte

**Arquitetura:**
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: Next.js 16 + React 19
- Drag & Drop: @dnd-kit
- Color Picker: react-colorful

**Convenções:**
- `user_id=1` hardcoded (usuário admin)
- Mês referência formato: `YYYY-MM`
- Cores em hex: `#RRGGBB`
- Ordem começa em 1

**Endpoints Backend:**
- GET `/budget/categorias-config?user_id=1&apenas_ativas=true`
- PUT `/budget/categorias-config/reordenar?user_id=1`
- POST `/budget/geral/bulk-upsert-validado?user_id=1`
- GET `/budget/realizado-hierarquico?mes_referencia=2026-01` (A CRIAR)

---

**Última revisão:** Sistema drag & drop funcional, pronto para continuar com Meta Geral.
