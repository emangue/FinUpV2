# API Specification - Mobile Experience V1.0

**Data:** 31/01/2026  
**Versão:** 1.2 (Atualizado: budget_planning + infraestrutura)  
**Base URL:** `http://localhost:8000/api/v1` (dev) | `https://finup.srv1045889.hstgr.cloud/api/v1` (prod)

**⚠️ CHANGELOG V1.2:**
- Substituído `/budget/geral` por `/budget/planning` (usa tabela `budget_planning`)
- Adicionado documento INFRASTRUCTURE.md (dev SQLite, prod PostgreSQL)
- Corrigido campo: `categoria_geral` → `grupo`

**⚠️ CHANGELOG V1.1:**
- Atualizado endpoints reais do backend (após validação em BACKEND_VALIDATION.md)
- Dashboard: `/categories` (não `/category-expenses`), `/chart-data` (não `/monthly-trend`)
- Transactions: `/list` (não `/transactions`), `PATCH /update/` (não `PUT /`)
- Upload: Documentado fluxo 2 passos (preview → confirm)

**🌍 INFRAESTRUTURA:**
- **Dev:** SQLite (`financas_dev.db`) - Ver INFRASTRUCTURE.md
- **Prod:** PostgreSQL (`finup_db` em `64.23.241.43`) - Ver INFRASTRUCTURE.md

---

## 1. Autenticação

### 1.1 POST /auth/login

**Descrição:** Autenticar usuário e obter token JWT.

**Endpoint:** `POST /api/v1/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "nome": "Emanuel Silva",
    "email": "usuario@example.com"
  }
}
```

**Response 401 Unauthorized:**
```json
{
  "detail": "Email ou senha incorretos"
}
```

---

## 2. Dashboard

### 2.1 GET /dashboard/budget-vs-actual

**Descrição:** Obter dados de realizado vs planejado (por grupo).

**Endpoint:** `GET /api/v1/dashboard/budget-vs-actual`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `year` (obrigatório): Ano (ex: 2026)
- `month` (opcional): Mês (1-12). Se omitido, retorna YTD
- `ytd` (opcional): Boolean. Se true, agrega ano inteiro

**Exemplos:**

**Visão mensal:**
```bash
GET /api/v1/dashboard/budget-vs-actual?year=2026&month=2
```

**Visão YTD:**
```bash
GET /api/v1/dashboard/budget-vs-actual?year=2026&ytd=true
```

**Response 200 OK:**
```json
{
  "year": 2026,
  "month": 2,
  "ytd": false,
  "total_realizado": 8547.00,
  "total_planejado": 10000.00,
  "percentual": 85.47,
  "grupos": [
    {
      "grupo": "Alimentação",
      "realizado": 1850.00,
      "planejado": 2000.00,
      "percentual": 92.5,
      "cor": "#60A5FA"
    },
    {
      "grupo": "Moradia",
      "realizado": 2100.00,
      "planejado": 2500.00,
      "percentual": 84.0,
      "cor": "#9F7AEA"
    },
    {
      "grupo": "Transporte",
      "realizado": 950.00,
      "planejado": 1200.00,
      "percentual": 79.2,
      "cor": "#A8A29E"
    }
  ]
}
```

---

### 2.2 GET /dashboard/categories

**Descrição:** Despesas agrupadas por categoria.

**Endpoint:** `GET /api/v1/dashboard/categories`

**⚠️ NOTA:** Backend usa `/categories` (não `/category-expenses`)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `year` (obrigatório): Ano
- `month` (obrigatório): Mês

**Response 200 OK:**
```json
{
  "total": 8547.00,
  "top5": [
    {
      "grupo": "Moradia",
      "valor": 2100.00,
      "percentual": 24.5
    },
    {
      "grupo": "Alimentação",
      "valor": 1850.00,
      "percentual": 21.6
    },
    {
      "grupo": "Compras",
      "valor": 1210.00,
      "percentual": 14.2
    },
    {
      "grupo": "Transporte",
      "valor": 950.00,
      "percentual": 11.1
    },
    {
      "grupo": "Contas",
      "valor": 450.00,
      "percentual": 5.3
    }
  ],
  "demais": {
    "valor": 1987.00,
    "percentual": 23.3,
    "quantidade_grupos": 5,
    "grupos_inclusos": ["Saúde", "Lazer", "Educação", "Vestuário", "Outros"]
  }
}
```

---

### 2.3 GET /dashboard/chart-data

**Descrição:** Dados para gráfico de área (receitas e despesas por dia do mês).

**Endpoint:** `GET /api/v1/dashboard/chart-data`

**⚠️ NOTA:** Backend usa `/chart-data` (não `/monthly-trend`)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `months` (opcional): Número de meses (default: 12)

**Response 200 OK:**
```json
{
  "meses": [
    {
      "mes": "2025-03",
      "receitas": 12450.00,
      "despesas": 8200.00,
      "saldo": 4250.00
    },
    {
      "mes": "2025-04",
      "receitas": 12450.00,
      "despesas": 9100.00,
      "saldo": 3350.00
    },
    // ... 10 meses mais
  ]
}
```

---

## 3. Budget (Metas)

**⚠️ IMPORTANTE:** Este módulo usa a tabela `budget_planning` (não `budget_geral`).

### Diferença entre Tabelas

| Tabela | Campo Chave | Valores | Uso Mobile V1.0 |
|--------|-------------|---------|-----------------|
| `budget_planning` | `grupo` | Alimentação, Moradia, Transporte | ✅ **USAR** |
| `budget_geral` | `categoria_geral` | Casa, Cartão de Crédito, Saúde | ❌ Não usar |

**Referência:** Ver `/docs/features/mobile-v1/02-TECH_SPEC/BUDGET_STRUCTURE_ANALYSIS.md`

---

### 3.1 GET /budget/planning

**Descrição:** Listar metas por mês (tabela `budget_planning`).

**Endpoint:** `GET /api/v1/budget/planning`

**⚠️ NOTA:** Backend precisa criar este endpoint (ver EXECUTIVE_SUMMARY.md)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `mes_referencia` (obrigatório): Formato YYYY-MM (ex: 2026-02)

**Response 200 OK:**
```json
{
  "budgets": [
    {
      "id": 123,
      "grupo": "Alimentação",
      "mes_referencia": "2026-02",
      "valor_planejado": 2000.00,
      "valor_medio_3_meses": 1850.00
    },
    {
      "id": 124,
      "grupo": "Moradia",
      "mes_referencia": "2026-02",
      "valor_planejado": 2500.00,
      "valor_medio_3_meses": 2400.00
    }
  ],
  "total": 2
}
```

---

### 3.2 POST /budget/planning/bulk-upsert

**Descrição:** Criar ou atualizar uma ou múltiplas metas de uma vez.

**⚠️ NOTA:** Backend precisa criar este endpoint (ver EXECUTIVE_SUMMARY.md)

**Endpoint:** `POST /api/v1/budget/planning/bulk-upsert`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body para 1 meta:**
```json
{
  "mes_referencia": "2026-02",
  "budgets": [
    {
      "grupo": "Alimentação",
      "valor_planejado": 2200.00
    }
  ]
}
```

**Body para múltiplas metas:**
```json
{
  "mes_referencia": "2026-02",
  "budgets": [
    { "grupo": "Alimentação", "valor_planejado": 2000.00 },
    { "grupo": "Transporte", "valor_planejado": 1200.00 },
    { "grupo": "Moradia", "valor_planejado": 2500.00 }
  ]
}
```

**Response 200 OK:**
```json
[
  {
    "id": 123,
    "grupo": "Alimentação",
    "mes_referencia": "2026-02",
    "valor_planejado": 2200.00,
    "valor_medio_3_meses": 1850.00,
    "criado_em": "2026-01-31T10:30:00Z",
    "atualizado_em": "2026-01-31T10:30:00Z"
  },
  {
    "id": 124,
    "grupo": "Transporte",
    "mes_referencia": "2026-02",
    "valor_planejado": 1200.00,
    "valor_medio_3_meses": 1100.00,
    "criado_em": "2026-01-31T10:30:00Z",
    "atualizado_em": "2026-01-31T10:30:00Z"
  }
]
```

**Response 400 Bad Request:**
```json
{
  "detail": "Valor planejado deve ser maior que zero"
}
```

---

### 3.4 POST /budget/geral/copy-to-year 🆕 NOVO

**Descrição:** Copiar metas de um mês para todos os meses de um ano.

**Endpoint:** `POST /api/v1/budget/geral/copy-to-year`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "mes_origem": "2026-02",
  "ano_destino": 2026,
  "substituir_existentes": true
}
```

**Parâmetros:**
- `mes_origem`: Mês de referência no formato YYYY-MM
- `ano_destino`: Ano para copiar (ex: 2026)
- `substituir_existentes`:
  - `true`: Sobrescrever metas existentes
  - `false`: Copiar apenas para meses vazios

**Response 200 OK:**
```json
{
  "sucesso": true,
  "meses_criados": 11,
  "metas_copiadas": 55,
  "mensagem": "Metas copiadas de 2026-02 para 11 meses de 2026"
}
```

**Response 400 Bad Request:**
```json
{
  "detail": "Nenhuma meta encontrada para o mês de origem 2026-02"
}
```

**Exemplo de uso:**
```typescript
// Frontend
const copyToYear = async () => {
  const response = await fetch('/api/v1/budget/geral/copy-to-year', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      mes_origem: '2026-02',
      ano_destino: 2026,
      substituir_existentes: true,
    }),
  });
  
  const result = await response.json();
  console.log(result.mensagem); // "Metas copiadas de 2026-02 para 11 meses de 2026"
};
```

---

### 3.5 GET /budget/geral/media-3-meses

**Descrição:** Calcular média das metas dos últimos 3 meses (para sugestão).

**Endpoint:** `GET /api/v1/budget/geral/media-3-meses`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `mes_referencia` (obrigatório): Mês base (ex: 2026-02)

**Response 200 OK:**
```json
{
  "mes_referencia": "2026-02",
  "meses_considerados": ["2025-11", "2025-12", "2026-01"],
  "sugestoes": [
    {
      "grupo": "Alimentação",
      "media": 1950.00
    },
    {
      "grupo": "Transporte",
      "media": 1150.00
    }
  ]
}
```

---

## 4. Transactions

### 4.1 GET /transactions/list

**Descrição:** Listar transações com filtros e paginação.

**Endpoint:** `GET /api/v1/transactions/list`

**⚠️ NOTA:** Backend usa `/transactions/list` (não `/transactions` direto)

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `page` (opcional): Página (default: 1)
- `limit` (opcional): Itens por página (default: 10)
- `year` (opcional): Ano
- `month` (opcional): Mês
- `tipo` (opcional): "receita" ou "despesa"
- `grupo` (opcional): Nome do grupo
- `subgrupo` (opcional): Nome do subgrupo
- `estabelecimento` (opcional): Nome do estabelecimento
- `cartao` (opcional): Nome do cartão
- `search` (opcional): Busca livre

**Exemplo:**
```bash
GET /api/v1/transactions/list?year=2026&month=2&tipo=despesa&grupo=Alimentação&limit=20&page=1
```

**Response 200 OK:**
```json
{
  "transactions": [
    {
      "IdTransacao": "1001",
      "Data": "2026-02-15",
      "Estabelecimento": "Mercado São José",
      "GRUPO": "Alimentação",
      "SUBGRUPO": "Supermercado",
      "Valor": 185.40,
      "TipoTransacao": "despesa",
      "NomeCartao": "Nubank"
    },
    {
      "IdTransacao": "1002",
      "Data": "2026-02-14",
      "Estabelecimento": "Posto Shell",
      "GRUPO": "Transporte",
      "SUBGRUPO": "Combustível",
      "Valor": 250.00,
      "TipoTransacao": "despesa",
      "NomeCartao": "Itaú"
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

---

### 4.2 PATCH /transactions/update/{id}

**Descrição:** Atualizar uma transação.

**Endpoint:** `PATCH /api/v1/transactions/update/{transaction_id}`

**⚠️ NOTA:** Backend usa `PATCH /transactions/update/{id}` (não `PUT /transactions/{id}`)

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body (todos opcionais):**
```json
{
  "GRUPO": "Alimentação",
  "SUBGRUPO": "Restaurante",
  "Valor": 190.00,
  "Estabelecimento": "Mercado São José",
  "IgnorarDashboard": false
}
```

**Response 200 OK:**
```json
{
  "IdTransacao": "1001",
  "Data": "2026-02-15",
  "Estabelecimento": "Mercado São José",
  "GRUPO": "Alimentação",
  "SUBGRUPO": "Restaurante",
  "Valor": 190.00,
  "TipoTransacao": "despesa",
  "NomeCartao": "Nubank"
}
```

---

### 4.3 DELETE /transactions/{id}

**Descrição:** Deletar uma transação.

**Endpoint:** `DELETE /api/v1/transactions/{transaction_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response 204 No Content**

---

### 4.4 GET /transactions/grupo-breakdown 🆕 NOVO

**Descrição:** Listar subgrupos de um grupo com valores agregados (drill-down).

**Endpoint:** `GET /api/v1/transactions/grupo-breakdown`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Params:**
- `grupo` (obrigatório): Nome do grupo (ex: "Cartão de Crédito")
- `year` (obrigatório): Ano
- `month` (obrigatório): Mês

**Exemplo:**
```bash
GET /api/v1/transactions/grupo-breakdown?grupo=Cartão%20de%20Crédito&year=2026&month=2
```

**Response 200 OK:**
```json
{
  "grupo": "Cartão de Crédito",
  "total": 3200.00,
  "subgrupos": [
    {
      "subgrupo": "iFood",
      "valor": 850.20,
      "percentual": 26.6,
      "quantidade_transacoes": 12
    },
    {
      "subgrupo": "Uber",
      "valor": 420.00,
      "percentual": 13.1,
      "quantidade_transacoes": 8
    },
    {
      "subgrupo": "Netflix",
      "valor": 55.90,
      "percentual": 1.7,
      "quantidade_transacoes": 1
    },
    {
      "subgrupo": "Spotify",
      "valor": 34.90,
      "percentual": 1.1,
      "quantidade_transacoes": 1
    },
    {
      "subgrupo": "Outros",
      "valor": 1839.00,
      "percentual": 57.5,
      "quantidade_transacoes": 23
    }
  ]
}
```

**Response 404 Not Found:**
```json
{
  "detail": "Grupo 'Cartão de Crédito' não encontrado no período 2026-02"
}
```

**Exemplo de uso:**
```typescript
// Frontend - GrupoBreakdownBottomSheet
const fetchSubgrupos = async (grupo: string, year: number, month: number) => {
  const response = await fetch(
    `/api/v1/transactions/grupo-breakdown?grupo=${encodeURIComponent(grupo)}&year=${year}&month=${month}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  const data = await response.json();
  return data.subgrupos;
};
```

---

## 5. Upload

**⚠️ IMPORTANTE:** Backend usa fluxo em **2 passos** (Preview → Confirm)

### 5.1 POST /upload/preview (Passo 1)

**Descrição:** Upload de arquivo + preview das transações detectadas.

**Endpoint:** `POST /api/v1/upload/preview`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Arquivo (PDF, CSV, XLSX)
- `banco`: String ("itau", "btg", "nubank", etc)
- `cartao`: String (opcional, nome do cartão)
- `final_cartao`: String (opcional, últimos 4 dígitos)
- `mesFatura`: String (formato YYYY-MM)
- `tipoDocumento`: String (default: "fatura", opções: "fatura" ou "extrato")
- `formato`: String (default: "csv")

**Response 200 OK:**
```json
{
  "session_id": "abc123def456",
  "transacoes_preview": [
    {
      "id": 1,
      "data": "2026-02-15",
      "estabelecimento": "Mercado São José",
      "valor": 185.40,
      "grupo_sugerido": "Alimentação",
      "subgrupo_sugerido": "Supermercado"
    },
    {
      "id": 2,
      "data": "2026-02-14",
      "estabelecimento": "Posto Shell",
      "valor": 250.00,
      "grupo_sugerido": "Transporte",
      "subgrupo_sugerido": "Combustível"
    }
  ],
  "total_transacoes": 45,
  "duplicadas_detectadas": 3
}
```

**Response 400 Bad Request:**
```json
{
  "detail": "Formato de arquivo não suportado"
}
```

---

### 5.2 GET /upload/preview/{session_id}

**Descrição:** Listar dados de preview de uma sessão.

**Endpoint:** `GET /api/v1/upload/preview/{session_id}`

**Response 200 OK:**
```json
{
  "session_id": "abc123def456",
  "transacoes_preview": [...],
  "total_transacoes": 45
}
```

---

### 5.3 PATCH /upload/preview/{session_id}/{preview_id}

**Descrição:** Atualizar classificação ou marcar exclusão de um registro de preview.

**Endpoint:** `PATCH /api/v1/upload/preview/{session_id}/{preview_id}`

**Query Params:**
- `grupo` (opcional): Novo grupo
- `subgrupo` (opcional): Novo subgrupo
- `excluir` (opcional): 1 para marcar como excluído

**Response 200 OK:**
```json
{
  "id": 1,
  "grupo": "Alimentação",
  "subgrupo": "Restaurante",
  "excluir": false
}
```

---

### 5.4 POST /upload/confirm/{session_id} (Passo 2)

**Descrição:** Confirmar upload e salvar transações na tabela principal.

**Endpoint:** `POST /api/v1/upload/confirm/{session_id}`

**Response 200 OK:**
```json
{
  "sucesso": true,
  "transacoes_importadas": 42,
  "transacoes_duplicadas": 3,
  "mensagem": "Importação concluída com sucesso"
}
```

---

### 5.5 DELETE /upload/preview/{session_id}

**Descrição:** Cancelar upload e remover dados de preview.

**Endpoint:** `DELETE /api/v1/upload/preview/{session_id}`

**Response 200 OK:**
```json
{
  "mensagem": "Preview removido com sucesso"
}
```

---

### 5.6 GET /upload/history

**Descrição:** Listar histórico de uploads do usuário.

**Endpoint:** `GET /api/v1/upload/history`

**Query Params:**
- `limit` (opcional): Número de resultados (default: 50)
- `offset` (opcional): Paginação (default: 0)

**Response 200 OK:**
```json
{
  "uploads": [
    {
      "id": 1,
      "arquivo": "extrato_itau_fev2026.pdf",
      "banco": "itau",
      "data_upload": "2026-02-01T10:30:00Z",
      "transacoes_importadas": 45,
      "status": "concluído"
    }
  ],
  "total": 10
}
```

---

## 6. Profile

### 6.1 GET /auth/profile

**Descrição:** Obter dados do perfil do usuário.

**Endpoint:** `GET /api/v1/auth/profile`

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200 OK:**
```json
{
  "id": 1,
  "nome": "Emanuel Silva",
  "email": "usuario@example.com",
  "criado_em": "2025-01-15T08:00:00Z"
}
```

---

### 6.2 PUT /auth/profile

**Descrição:** Atualizar dados do perfil.

**Endpoint:** `PUT /api/v1/auth/profile`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "nome": "Emanuel Silva Santos",
  "email": "novo_email@example.com"
}
```

**Response 200 OK:**
```json
{
  "id": 1,
  "nome": "Emanuel Silva Santos",
  "email": "novo_email@example.com",
  "atualizado_em": "2026-01-31T12:00:00Z"
}
```

---

### 6.3 PUT /auth/change-password

**Descrição:** Alterar senha do usuário.

**Endpoint:** `PUT /api/v1/auth/change-password`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "current_password": "senha_antiga",
  "new_password": "senha_nova_123"
}
```

**Response 200 OK:**
```json
{
  "mensagem": "Senha alterada com sucesso"
}
```

**Response 400 Bad Request:**
```json
{
  "detail": "Senha atual incorreta"
}
```

---

## 7. Códigos de Status HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 OK | Sucesso | GET, PUT bem-sucedidos |
| 201 Created | Criado | POST bem-sucedido (criação) |
| 204 No Content | Sem conteúdo | DELETE bem-sucedido |
| 400 Bad Request | Requisição inválida | Validação falhou, parâmetros incorretos |
| 401 Unauthorized | Não autorizado | Token inválido ou expirado |
| 403 Forbidden | Proibido | Usuário sem permissão |
| 404 Not Found | Não encontrado | Recurso não existe |
| 422 Unprocessable Entity | Entidade não processável | Validação semântica falhou |
| 500 Internal Server Error | Erro interno | Erro no servidor |

---

## 8. Rate Limiting

**Limite:** 100 requisições por minuto por usuário

**Headers de resposta:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1706699400
```

**Response 429 Too Many Requests:**
```json
{
  "detail": "Rate limit excedido. Tente novamente em 30 segundos."
}
```

---

## 9. Versionamento

**Estratégia:** Versionamento por URL

**Formato:** `/api/v{version}/`

**Versões disponíveis:**
- `v1`: Versão atual (mobile V1.0)

**Deprecation:** Versões antigas mantidas por 6 meses após lançamento de nova versão

---

## 10. Exemplos de Integração

### 10.1 Fluxo Completo: Editar Meta

```typescript
// 1. Listar metas de fevereiro
const response1 = await fetch('/api/v1/budget/planning?mes_referencia=2026-02', {
  headers: { 'Authorization': `Bearer ${token}` },
});
const { budgets } = await response1.json();

// 2. Atualizar meta de "Alimentação" (usar bulk-upsert com 1 item)
const response2 = await fetch('/api/v1/budget/planning/bulk-upsert', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    mes_referencia: '2026-02',
    budgets: [
      {
        grupo: 'Alimentação',
        valor_planejado: 2200.00,
      }
    ],
  }),
});

const resultado = await response2.json();
console.log(resultado); // [{ id: 123, grupo: "Alimentação", ... }]
```

---

### 10.2 Fluxo Completo: Drill-down Subgrupos

```typescript
// 1. Listar budget vs actual (grupos)
const response1 = await fetch('/api/v1/dashboard/budget-vs-actual?year=2026&month=2', {
  headers: { 'Authorization': `Bearer ${token}` },
});
const dashboard = await response1.json();

// 2. Usuário toca em "Cartão de Crédito"
const grupo = 'Cartão de Crédito';

// 3. Buscar subgrupos (endpoint a criar - ver BACKEND_VALIDATION.md)
const response2 = await fetch(
  `/api/v1/transactions/grupo-breakdown?grupo=${encodeURIComponent(grupo)}&year=2026&month=2`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const breakdown = await response2.json();

console.log(breakdown.subgrupos); // [ { subgrupo: "Netflix", valor: 55.90, ... }, ... ]
```

---

### 10.3 Fluxo Completo: Upload de Arquivo (2 passos)

```typescript
// Passo 1: Upload e preview
const formData = new FormData();
formData.append('file', file);
formData.append('banco', 'itau');
formData.append('mesFatura', '2026-02');
formData.append('tipoDocumento', 'fatura');

const response1 = await fetch('/api/v1/upload/preview', {
  method: 'POST',
  body: formData,
  headers: { 'Authorization': `Bearer ${token}` }
});

const { session_id, transacoes_preview } = await response1.json();

// Passo 2: Usuário valida preview, pode editar classificações
// ...

// Passo 3: Confirmar importação
const response2 = await fetch(`/api/v1/upload/confirm/${session_id}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

const { transacoes_importadas, transacoes_duplicadas } = await response2.json();
console.log(`Importadas: ${transacoes_importadas}, Duplicadas: ${transacoes_duplicadas}`);
```

---

**Fim da API Specification**

**Data:** 31/01/2026  
**Versão:** 1.0
