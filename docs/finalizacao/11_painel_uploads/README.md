# 1️⃣1️⃣ Painel de Uploads - /mobile/profile

**Status:** 🟢 Parcialmente Implementado  
**Prioridade:** 🟡 MÉDIA  
**Criado em:** 13/02/2026  
**Ordem Recomendada:** A definir (após Feature s Core)

---

## ✅ Implementado (14/02/2026)

### Painel de Últimos 10 Uploads
- **Componente:** `app_dev/frontend/src/app/mobile/profile/components/uploads-panel.tsx`
- **Integração:** Incluído em `app_dev/frontend/src/app/mobile/profile/page.tsx`
- **Dados exibidos por upload:**
  - Nome do arquivo, banco, cartão, mês fatura
  - Data do upload
  - Total processado (`total_registros`)
  - Salvas na base (`transacoes_importadas`)
  - Duplicadas ignoradas (`transacoes_duplicadas`)
  - Status (Confirmado/Erro/Processando)

### Botão "Revisar" - Reabrir Preview
- **Endpoint:** `POST /api/v1/upload/history/{history_id}/recreate-preview`
- **Fluxo:**
  1. Lê `journal_entries` do upload original
  2. Cria `PreviewTransacao` para cada entrada
  3. Cria sessão `rev-{id}-{uuid}` e redireciona para `/mobile/preview/{session_id}`
  4. Usuário edita no preview e clica "Salvar e Importar Dados"
  5. `confirm_upload` detecta sessão de revisão:
     - Remove transações antigas do upload original
     - Insere novas transações com `upload_history_id` original
     - Remove histórico temporário de revisão

---

## 🎯 Objetivo

Criar painel completo de gerenciamento de uploads em `/mobile/profile` que permita ao usuário:
- Visualizar histórico de uploads
- Estatísticas por upload
- Editar transações de upload específico
- Deletar upload completo

---

## 📋 Especificação da Tela

### URL
```
http://localhost:3000/mobile/profile
```

### Layout
```
┌─────────────────────────────────────┐
│  📁 Histórico de Uploads            │
├─────────────────────────────────────┤
│  🔍 Filtros: Banco | Mês | Status   │
├─────────────────────────────────────┤
│                                     │
│  📊 Upload #1 - MercadoPago         │
│  ├─ 📅 15/01/2025 14:30            │
│  ├─ ✅ Status: Confirmado          │
│  ├─ 📈 150 transações importadas   │
│  ├─ 🏷️ Origem Classificação:       │
│  │   • Base Genérica: 120 (80%)   │
│  │   • Base Padrões: 25 (17%)     │
│  │   • Não Classificado: 5 (3%)   │
│  ├─ 🗑️ 10 duplicadas              │
│  └─ 🛠️ [Editar] [Deletar]         │
│                                     │
│  📊 Upload #2 - Itaú Cartão        │
│  ├─ ...                            │
│                                     │
│  [Carregar mais...]                │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔧 Funcionalidades

### 1. Listagem de Uploads (Últimos 10)

**Endpoint:** `GET /api/v1/upload/history?limit=10&offset=0`

**Dados exibidos por upload:**
- `session_id` - Identificador único
- `banco` - Ex: "MercadoPago", "Itaú"
- `tipo_documento` - "extrato" ou "fatura"
- `nome_arquivo` - Arquivo original
- `nome_cartao` - Se fatura (opcional)
- `data_upload` - Data/hora do upload
- `data_confirmacao` - Data/hora da confirmação
- `status` - "processing" | "success" | "error"
- `total_registros` - Quantidade total
- `transacoes_importadas` - Não-duplicadas salvas
- `transacoes_duplicadas` - Ignoradas

**Estatísticas de Origem (calcular via query):**
```sql
SELECT 
    origem_classificacao,
    COUNT(*) as qtd
FROM journal_entries
WHERE upload_history_id = ?
GROUP BY origem_classificacao
```

**Resultado:**
```json
{
  "Base Genérica": 120,
  "Base Padrões": 25,
  "Não Classificado": 5
}
```

---

### 2. Filtros

**Opções:**
- **Banco:** Dropdown (MercadoPago, Itaú, BTG, Todos)
- **Mês:** Seletor de mês/ano
- **Status:** success | error | processing | Todos

**Query params:**
```
GET /api/v1/upload/history?banco=MercadoPago&mes=2025-01&status=success
```

---

### 3. Editar Transações do Upload

**Ação:** Redireciona para tela de transações filtradas por upload

**URL de redirecionamento:**
```
/mobile/transactions?upload_id={upload_history_id}
```

**Backend:** Adicionar filtro `upload_history_id` no endpoint de listagem
```python
# app/domains/transactions/router.py
@router.get("/transactions/list")
def list_transactions(
    upload_id: Optional[int] = Query(None),
    # ... outros filtros
):
    if upload_id:
        filters.append(JournalEntry.upload_history_id == upload_id)
```

**Frontend:** Tela de transações mostra banner indicando filtro ativo:
```
⚠️ Exibindo apenas transações do upload "MP202501.xlsx" (15/01/2025)
[Remover filtro]
```

---

### 4. Deletar Upload Completo

**Endpoint:** `DELETE /api/v1/upload/history/{history_id}`

**Lógica (Backend):**
```python
# app/domains/upload/router.py
@router.delete("/upload/history/{history_id}")
def delete_upload_history(
    history_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Deleta upload e TODAS suas transações
    
    1. Verificar se upload pertence ao usuário
    2. Deletar transações (journal_entries com upload_history_id)
    3. Deletar registro de histórico
    4. Retornar quantidade deletada
    """
    service = UploadService(db)
    resultado = service.delete_upload_history(history_id, user_id)
    return {
        "message": "Upload deletado com sucesso",
        "transacoes_deletadas": resultado["transacoes_deletadas"],
        "upload_id": history_id
    }
```

**Confirmação (Frontend):**
```tsx
<AlertDialog>
  <AlertDialogTitle>Deletar Upload?</AlertDialogTitle>
  <AlertDialogDescription>
    Isso vai deletar permanentemente:
    • {upload.transacoes_importadas} transações
    • Histórico de upload "{upload.nome_arquivo}"
    
    ⚠️ Esta ação não pode ser desfeita!
  </AlertDialogDescription>
  <AlertDialogAction onClick={handleDelete}>
    Deletar
  </AlertDialogAction>
</AlertDialog>
```

---

## 🗄️ Backend - Endpoints Necessários

### Existentes (Validar)
- ✅ `GET /api/v1/upload/history` - Listar histórico (já existe)

### A Criar
- ✅ `POST /api/v1/upload/history/{history_id}/recreate-preview` - Recriar preview para revisão
- ❌ `DELETE /api/v1/upload/history/{history_id}` - Deletar upload
- ❌ `GET /api/v1/upload/history/{history_id}/stats` - Estatísticas detalhadas (opcional)

### A Ajustar
- ⚠️ `GET /api/v1/transactions/list` - Adicionar filtro `upload_history_id`

---

## 🎨 Frontend - Componentes

### Estrutura de Arquivos
```
app_dev/frontend/src/app/mobile/profile/
├── page.tsx                    # Página principal
├── components/
│   ├── upload-list-item.tsx   # Card de upload individual
│   ├── upload-filters.tsx     # Filtros de busca
│   └── delete-upload-dialog.tsx # Modal de confirmação
└── hooks/
    ├── use-upload-history.ts  # Hook para buscar uploads
    └── use-delete-upload.ts   # Hook para deletar
```

### Interfaces TypeScript
```typescript
interface UploadHistory {
  id: number;
  session_id: string;
  banco: string;
  tipo_documento: 'extrato' | 'fatura';
  nome_arquivo: string;
  nome_cartao?: string;
  final_cartao?: string;
  mes_fatura?: string;
  data_upload: string;
  data_confirmacao?: string;
  status: 'processing' | 'success' | 'error';
  total_registros: number;
  transacoes_importadas: number;
  transacoes_duplicadas: number;
}

interface UploadStats {
  origem_classificacao: {
    'Base Genérica': number;
    'Base Padrões': number;
    'Não Classificado': number;
  };
}
```

---

## 📊 Queries SQL Úteis

### Estatísticas de Origem por Upload
```sql
SELECT 
    origem_classificacao,
    COUNT(*) as qtd,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
FROM journal_entries
WHERE upload_history_id = :history_id
GROUP BY origem_classificacao;
```

### Uploads com Contadores
```sql
SELECT 
    uh.*,
    COUNT(je.id) as total_transacoes_salvas,
    SUM(CASE WHEN je.origem_classificacao = 'Base Genérica' THEN 1 ELSE 0 END) as qtd_base_generica,
    SUM(CASE WHEN je.origem_classificacao = 'Base Padrões' THEN 1 ELSE 0 END) as qtd_base_padroes,
    SUM(CASE WHEN je.origem_classificacao = 'Não Classificado' THEN 1 ELSE 0 END) as qtd_nao_classificado
FROM upload_history uh
LEFT JOIN journal_entries je ON je.upload_history_id = uh.id
WHERE uh.user_id = :user_id
GROUP BY uh.id
ORDER BY uh.data_upload DESC
LIMIT 10;
```

---

## 🧪 Casos de Teste

### CT1: Visualizar Histórico
- **Ação:** Acessar `/mobile/profile`
- **Esperado:** Lista últimos 10 uploads com estatísticas

### CT2: Filtrar por Banco
- **Ação:** Selecionar "MercadoPago" no filtro
- **Esperado:** Apenas uploads MercadoPago exibidos

### CT3: Editar Transações
- **Ação:** Clicar "Editar" em upload #1
- **Esperado:** Redireciona para `/mobile/transactions?upload_id=1`

### CT4: Deletar Upload
- **Ação:** Clicar "Deletar" → Confirmar
- **Esperado:** 
  - Upload removido da lista
  - Transações deletadas do journal_entries
  - Toast: "Upload deletado com sucesso"

### CT5: Carregar Mais
- **Ação:** Scroll até fim da lista → Clicar "Carregar mais"
- **Esperado:** Próximos 10 uploads carregados

---

## 📝 Checklist de Implementação

### Backend (2-3h)
- [ ] Criar endpoint `DELETE /api/v1/upload/history/{id}`
  - [ ] Validar ownership (user_id)
  - [ ] Deletar transações (journal_entries)
  - [ ] Deletar histórico (upload_history)
  - [ ] Retornar contador
- [ ] Adicionar filtro `upload_history_id` em `/transactions/list`
- [ ] Endpoint de estatísticas (opcional)
- [ ] Testes unitários

### Frontend (4-5h)
- [ ] Criar pasta `/app/mobile/profile/`
- [ ] Página principal `page.tsx`
- [ ] Componente `upload-list-item.tsx`
- [ ] Componente `upload-filters.tsx`
- [ ] Modal `delete-upload-dialog.tsx`
- [ ] Hook `use-upload-history.ts`
- [ ] Hook `use-delete-upload.ts`
- [ ] Integração com API
- [ ] Loading states
- [ ] Error handling
- [ ] Responsividade mobile

### Validação (1h)
- [ ] Testar todos os casos de teste
- [ ] Validar performance (lista grande)
- [ ] Validar deletar cascata funciona
- [ ] Validar filtros funcionam

---

## 🎯 Priorização

**Recomendação:** Implementar após Frente 5 (Teste Upload End-to-End)

**Por quê:**
- Depende de uploads reais funcionando
- Feature secundária (não bloqueia uso)
- Útil para gerenciar uploads após testes

**Ordem proposta:** Entre 7º e 8º lugar

---

## 📚 Referências

- **Backend:** `app_dev/backend/app/domains/upload/router.py`
- **Models:** `app_dev/backend/app/domains/upload/history_models.py`
- **Frontend upload:** `app_dev/frontend/src/app/upload/` (referência de integração)

---

**Criado em:** 13/02/2026  
**Por:** Planejamento de feature solicitada pelo usuário
