# Fase 2 - Admin Panel: Excluir / Ignorar

**Status:** ✅ Implementado  
**Data:** 04/01/2026

---

## 📋 Resumo

Interface unificada para gerenciar regras de **Exclusão** e **Ignorar** transações durante a importação, utilizando a mesma tabela `transacoes_exclusao` com campo `acao` editável.

---

## 🎨 Interface Atualizada

### Localização
**URL:** `/settings/exclusoes`

### Mudanças Implementadas

1. **Título da Página**
   - ❌ Antes: "Exclusões"
   - ✅ Agora: "Excluir / Ignorar"
   - Descrição: "Gerencie transações que devem ser excluídas ou ignoradas durante a importação"

2. **Card Header**
   - ❌ Antes: "Transações a Excluir" (X regras de exclusão cadastradas)
   - ✅ Agora: "Transações a Excluir / Ignorar" (X regras cadastradas - Y excluir, Z ignorar)

3. **Botão Principal**
   - ❌ Antes: "Nova Exclusão"
   - ✅ Agora: "Nova Regra"

4. **Nova Coluna na Tabela**
   - **Coluna "Ação"** com dropdown editável inline
   - Valores: **EXCLUIR** (vermelho) ou **IGNORAR** (amarelo)
   - Edição instantânea: clicar no dropdown e selecionar nova ação → salva automaticamente

5. **Modal Atualizado**
   - Título: "Adicionar/Editar Regra"
   - Novo campo: **Ação** (dropdown)
     - **EXCLUIR** 🔴 - Remove da importação (não aparece no preview)
     - **IGNORAR** 🟡 - Importa mas não conta em dashboards

---

## 🔧 Estrutura da Tabela

### Colunas Exibidas

| Coluna | Descrição | Editável |
|--------|-----------|----------|
| **Nome da Transação** | Nome exato a ser buscado | Não (via modal) |
| **Banco** | Banco específico ou "Todos" | Não (via modal) |
| **Tipo** | Cartão, Extrato ou Ambos | Não (via modal) |
| **Ação** | EXCLUIR ou IGNORAR | ✅ **SIM (dropdown inline)** |
| **Descrição** | Motivo da regra | Não (via modal) |
| **Ações** | Editar / Deletar | - |

---

## 🎯 Comportamento das Ações

### 🔴 EXCLUIR (Default)
- **O que faz:** Remove a transação durante a importação
- **Onde:** Não aparece no preview de upload
- **Dashboard:** Não contabiliza (não existe no sistema)
- **Uso:** Pagamentos de fatura, ajustes técnicos, duplicatas

### 🟡 IGNORAR (Novo)
- **O que faz:** Importa a transação com `IgnorarDashboard=True`
- **Onde:** Aparece no preview de upload (com badge "Ignorar")
- **Dashboard:** Não contabiliza em métricas e gráficos
- **Uso:** TED/PIX próprios, transferências internas, tarifas que você quer registrar mas não contabilizar

---

## 💾 Backend (API)

### Endpoints Atualizados

#### `GET /api/v1/exclusoes/`
**Response:**
```json
[
  {
    "id": 1,
    "nome_transacao": "PAGAMENTO EFETUADO",
    "banco": "Itaú",
    "tipo_documento": "cartao",
    "descricao": "Pagamento fatura anterior",
    "acao": "EXCLUIR",
    "ativo": 1,
    "created_at": "2026-01-04T15:00:00"
  }
]
```

#### `POST /api/v1/exclusoes/`
**Request:**
```json
{
  "nome_transacao": "TARIFA MANUTENCAO",
  "banco": null,
  "tipo_documento": "extrato",
  "descricao": "Tarifas mensais",
  "acao": "IGNORAR"
}
```

#### `PUT /api/v1/exclusoes/{id}`
**Request (edição inline):**
```json
{
  "acao": "IGNORAR"
}
```

### Schemas Pydantic

```python
class ExclusaoCreate(BaseModel):
    nome_transacao: str
    banco: Optional[str] = None
    tipo_documento: Optional[str] = None
    descricao: Optional[str] = None
    acao: Optional[str] = 'EXCLUIR'  # ✨ NOVO

class ExclusaoUpdate(BaseModel):
    nome_transacao: Optional[str] = None
    banco: Optional[str] = None
    tipo_documento: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[int] = None
    acao: Optional[str] = None  # ✨ NOVO

class ExclusaoResponse(BaseModel):
    id: int
    nome_transacao: str
    banco: Optional[str] = None
    tipo_documento: Optional[str] = None
    descricao: Optional[str] = None
    ativo: int
    acao: str = 'EXCLUIR'  # ✨ NOVO
    created_at: Optional[datetime] = None
```

---

## 🚀 Como Usar

### 1. Adicionar Nova Regra

1. Acessar `/settings/exclusoes`
2. Clicar em **"Nova Regra"**
3. Preencher:
   - **Nome da Transação:** Ex: `TARIFA MANUTENCAO`
   - **Banco:** (opcional) Selecionar banco específico ou "Todos"
   - **Tipo:** Cartão, Extrato ou ambos
   - **Ação:** 
     - 🔴 **EXCLUIR** - Remove da importação
     - 🟡 **IGNORAR** - Importa mas não conta em dashboards
   - **Descrição:** (opcional) Motivo da regra
4. Clicar em **"Adicionar"**

### 2. Editar Ação de Regra Existente (Inline)

1. Na tabela, localizar a regra
2. Na coluna **"Ação"**, clicar no dropdown
3. Selecionar nova ação (EXCLUIR ou IGNORAR)
4. **Salva automaticamente** ✅

### 3. Editar Outros Campos

1. Clicar no ícone **✏️ Editar** na linha da regra
2. Modal abre com todos os campos editáveis
3. Modificar conforme necessário
4. Clicar em **"Salvar"**

### 4. Deletar Regra

1. Clicar no ícone **❌** na linha da regra
2. Confirmar exclusão
3. Regra é **desativada** (soft delete: `ativo=0`)

---

## 🎨 Visual da Interface

### Dropdown de Ação (Inline)
```
┌─────────────────────┐
│ 🔴 Excluir         ▼│  ← Clicável
└─────────────────────┘

Expandido:
┌─────────────────────────────────────────┐
│ 🔴 Excluir                              │
│ Remove da importação (não aparece)      │
├─────────────────────────────────────────┤
│ 🟡 Ignorar                              │
│ Importa mas não conta em dashboards     │
└─────────────────────────────────────────┘
```

### Card Header (Contadores)
```
Transações a Excluir / Ignorar
5 regras cadastradas (3 excluir, 2 ignorar)
```

---

## 🔄 Integração com Sistema de Classificação

### Durante Import (Nível 2 - Ignorar)

**Arquivo:** `codigos_apoio/cascade_classifier.py`

```python
def _nivel_2_ignorar(self, transacao):
    # 1. Buscar regras com acao='IGNORAR'
    exclusoes = db.query(TransacaoExclusao).filter(
        TransacaoExclusao.user_id == user_id,
        TransacaoExclusao.ativo == 1,
        TransacaoExclusao.acao == 'IGNORAR'
    ).all()
    
    # 2. Se match, retornar com IgnorarDashboard=True
    for exc in exclusoes:
        if exc.nome_transacao in estabelecimento:
            return {
                'origem_classificacao': 'Ignorar - Lista Admin',
                'IgnorarDashboard': True,
                ...
            }
```

**Regras com `acao='EXCLUIR'`:**
- São filtradas **antes** do import (não chegam ao classifier)
- Implementado em: `app_dev/frontend/src/app/api/upload/preview/route.ts`

---

## 📊 Exemplo Prático

### Cenário: Tarifas Bancárias

**Objetivo:** Registrar tarifas mas não contabilizar em dashboards

**Configuração:**
```
Nome: TARIFA MANUTENCAO
Banco: Todos
Tipo: Extrato
Ação: IGNORAR 🟡
Descrição: Tarifas mensais de manutenção
```

**Resultado:**
- ✅ Transação é importada
- ✅ Aparece no preview de upload
- ✅ Fica armazenada no banco (`journal_entries`)
- ✅ Campo `IgnorarDashboard=True`
- ❌ NÃO conta em "Total de Despesas"
- ❌ NÃO aparece em gráficos de categoria
- ✅ Aparece em relatórios completos (se filtrar por "Mostrar Ignoradas")

---

## ✅ Checklist de Implementação

- [x] Adicionar coluna `acao` na tabela `transacoes_exclusao`
- [x] Atualizar modelo `TransacaoExclusao` (backend)
- [x] Atualizar schemas Pydantic (ExclusaoCreate, Update, Response)
- [x] Adicionar campo `acao` na interface TypeScript
- [x] Criar dropdown inline editável com cores
- [x] Implementar `handleAcaoChange()` para edição inline
- [x] Atualizar modal com campo Ação
- [x] Adicionar contadores no card header (X excluir, Y ignorar)
- [x] Mudar título da página para "Excluir / Ignorar"
- [x] Atualizar descrições e tooltips
- [x] Testar edição inline
- [x] Testar criação de nova regra
- [x] Testar integração com backend

---

## 🔍 Debugging

### Verificar Regras Atuais

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
source venv/bin/activate
python scripts/seed_ignore_rules.py --show
```

**Output esperado:**
```
📋 Regras atuais:
────────────────────────────────────────────────────────────────────────────────
Nome                           | Banco           | Tipo Doc             | Ação       | Status
────────────────────────────────────────────────────────────────────────────────
PAGAMENTO EFETUADO             | Itaú            | cartao               | EXCLUIR    | ✅
TARIFA MANUTENCAO              |                 | extrato              | IGNORAR    | ✅
────────────────────────────────────────────────────────────────────────────────

📊 Resumo:
   Regras EXCLUIR ativas: 1
   Regras IGNORAR ativas: 1
```

### Ver Banco de Dados Diretamente

```bash
cd app_dev/backend
sqlite3 database/financas_dev.db
```

```sql
-- Ver todas as regras
SELECT id, nome_transacao, banco, tipo_documento, acao, ativo 
FROM transacoes_exclusao;

-- Contar por ação
SELECT acao, COUNT(*) as total 
FROM transacoes_exclusao 
WHERE ativo = 1 
GROUP BY acao;
```

### Logs do Backend

```bash
tail -f /tmp/backend.log | grep -i exclus
```

---

## 🎯 Próximas Melhorias (Futuro)

1. **Filtros na Tabela**
   - Filtrar por Ação (EXCLUIR, IGNORAR, Todas)
   - Filtrar por Banco
   - Pesquisa por nome

2. **Bulk Actions**
   - Selecionar múltiplas regras
   - Mudar ação de todas de uma vez
   - Deletar múltiplas

3. **Import/Export**
   - Exportar regras para JSON
   - Importar regras de outro usuário
   - Templates de regras comuns

4. **Analytics**
   - Quantas transações foram ignoradas este mês
   - Ranking de regras mais usadas
   - Sugestões automáticas de novas regras

---

**Versão:** 1.0.0  
**Última Atualização:** 04/01/2026  
**Autor:** GitHub Copilot + Eduardo Mangue
