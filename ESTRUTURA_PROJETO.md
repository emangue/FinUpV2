# 📁 Estrutura do Projeto - Gestão Financeira V3

## 🎯 Visão Geral

Sistema modular de gestão financeira desenvolvido em Flask com arquitetura blueprints.

---

## 📂 Estrutura de Diretórios

```
ProjetoFinancasV3/
├── 📁 app/                          # Aplicação Flask principal
│   ├── __init__.py                  # Factory da aplicação
│   ├── config.py                    # Configurações da aplicação
│   ├── models.py                    # Modelos SQLAlchemy
│   ├── extensions.py                # Extensões Flask
│   ├── filters.py                   # Filtros Jinja2
│   │
│   ├── 📁 blueprints/               # Módulos da aplicação
│   │   ├── 📁 admin/                # Administração
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # Rotas admin (transações, parcelas, grupos, etc)
│   │   │
│   │   ├── 📁 dashboard/            # Dashboard principal
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # Visão geral, gráficos, resumos
│   │   │
│   │   └── 📁 upload/               # Sistema de upload e processamento
│   │       ├── __init__.py
│   │       ├── routes.py            # Upload, validação, deduplicação, auto-sync
│   │       │
│   │       ├── 📁 classifiers/      # Classificação automática
│   │       │   ├── __init__.py
│   │       │   ├── auto_classifier.py      # Motor de classificação
│   │       │   └── pattern_generator.py    # Gerador de padrões
│   │       │
│   │       ├── 📁 processors/       # Processadores de arquivos
│   │       │   ├── __init__.py
│   │       │   ├── fatura_cartao.py        # Processar faturas cartão (GENÉRICO)
│   │       │   ├── extrato_conta.py        # Processar extratos bancários
│   │       │   └── 📁 _deprecated/  # Processadores antigos (não usar)
│   │       │       ├── fatura_itau.py
│   │       │       ├── extrato_itau.py
│   │       │       └── mercado_pago.py
│   │       │
│   │       └── 📁 utils/            # Utilitários de upload
│   │           ├── __init__.py
│   │           └── detector.py      # Detecção de formato de arquivo
│   │
│   └── 📁 utils/                    # Utilitários globais
│       ├── __init__.py
│       ├── hasher.py                # Geração de IDs (FNV-1a, MD5)
│       ├── normalizer.py            # Normalização de estabelecimentos
│       └── deduplicator.py          # Detecção de duplicatas
│
├── 📁 scripts/                      # Scripts utilitários
│   ├── migrate_parcelas.py          # Sincronizar BaseParcelas (integrado no upload)
│   ├── cleanup_orphans.py           # Limpar contratos órfãos (integrado no upload)
│   ├── analisar_transacoes.py       # Análise de dados
│   ├── buscar_similares.py          # Buscar transações similares
│   ├── create_base_parcelas.py      # Criar tabela BaseParcelas
│   └── ...                          # Outros scripts de manutenção
│
├── 📁 templates/                    # Templates HTML (Jinja2)
│   ├── base.html                    # Template base
│   ├── dashboard.html               # Dashboard principal
│   ├── upload.html                  # Upload de arquivos
│   ├── confirmar_upload.html        # Confirmação de upload
│   ├── revisao_upload.html          # Revisão pré-salvamento
│   ├── admin_transacoes.html        # Admin de transações
│   ├── admin_parcelas.html          # Admin de parcelas
│   └── ...                          # Outros templates
│
├── 📁 static/                       # Arquivos estáticos
│   ├── 📁 css/                      # Estilos
│   │   └── style.css
│   ├── 📁 js/                       # JavaScript
│   │   └── main.js
│   └── 📁 logos/                    # Logos de estabelecimentos
│       ├── ifood_ifd.webp
│       ├── uber.svg
│       └── ...
│
├── 📁 _temp_scripts/                # Scripts temporários/debug (GIT IGNORED)
│   ├── debug_*.py
│   ├── fix_*.py
│   ├── delete_*.py
│   └── test_*.py
│
├── 📁 _csvs_historico/              # CSVs históricos (GIT IGNORED)
│   ├── fatura_itau-202510.csv
│   ├── fatura_itau-202511.csv
│   └── ...
│
├── 📁 uploads_temp/                 # Uploads temporários (GIT IGNORED)
├── 📁 flask_session/                # Sessões Flask (GIT IGNORED)
├── 📁 venv/                         # Ambiente virtual Python (GIT IGNORED)
│
├── 📄 run.py                        # Ponto de entrada da aplicação
├── 📄 requirements.txt              # Dependências Python
│
├── 📄 import_base_inicial.py        # Importar base inicial de dados
├── 📄 import_marcacoes_seguro.py    # Importar marcações de seguro
│
├── 📄 README.md                     # Documentação principal
├── 📄 BUGS.md                       # Lista de bugs conhecidos
├── 📄 MODULARIZACAO.md              # Documentação da modularização
├── 📄 PROTECAO_BASES.md             # Proteção de bases de dados
├── 📄 STATUSPROJETO.md              # Status atual do projeto
└── 📄 ESTRUTURA_PROJETO.md          # Este arquivo
```

---

## 🔄 Fluxo Completo do Sistema

### 📤 1. Upload de Arquivo (`/upload`)

**Endpoint:** `POST /upload/processar`  
**Arquivo:** [app/blueprints/upload/routes.py](app/blueprints/upload/routes.py)

```
Usuário seleciona arquivo → Flask recebe → Salva em uploads_temp/
```

**Validações iniciais:**
- ✓ Extensão permitida (.csv, .xlsx, .xls)
- ✓ Tamanho máximo do arquivo
- ✓ Nome do arquivo sanitizado

---

### 🔍 2. Detecção de Formato

**Função:** `detectar_formato_arquivo()`  
**Arquivo:** [app/blueprints/upload/utils/detector.py](app/blueprints/upload/utils/detector.py)

**Ordem de detecção:**

1. **Análise de conteúdo:**
   - Lê primeiras linhas do arquivo
   - Identifica colunas presentes
   - Detecta padrões de parcelas (ex: "10/10")

2. **Decisão de processador:**
   ```python
   Se contém colunas ['Data', 'Estabelecimento', 'Valor']:
       Se tem parcelas detectadas → fatura_cartao
       Senão → extrato_conta
   ```

3. **Retorna:** Nome do processador a ser usado

---

### ⚙️ 3. Processamento do Arquivo

**Processadores disponíveis:**
- `fatura_cartao.py` - Faturas de cartão de crédito (com suporte a parcelas)
- `extrato_conta.py` - Extratos bancários (débito/transferências)

#### 3.1. Processador de Fatura de Cartão

**Arquivo:** [app/blueprints/upload/processors/fatura_cartao.py](app/blueprints/upload/processors/fatura_cartao.py)

**Fluxo detalhado:**

```
1. Leitura do CSV/Excel
   ↓
2. Para cada linha:
   ├─ Detectar se tem parcela (regex: \d{1,2}/\d{1,2})
   ├─ Se TEM parcela:
   │  ├─ Extrair parcela_atual e total_parcelas
   │  ├─ Remover " XX/YY" do estabelecimento
   │  └─ Agrupar por chave: estabelecimento + total + VALOR
   │     (IMPORTANTE: valor incluído para não misturar compras diferentes)
   │
   └─ Se NÃO TEM parcela:
      └─ Criar transação avulsa imediatamente
   ↓
3. Processar grupos de parcelas:
   Para cada grupo:
   ├─ Ordenar parcelas por número
   ├─ Gerar IdParcela (MD5 de: estabelecimento + valor + total)
   ├─ Para cada parcela do grupo:
   │  ├─ Gerar IdTransacao (FNV-1a de: data + estab + valor)
   │  ├─ Adicionar IdParcela à transação
   │  └─ Criar dict com todos os campos
   │
   └─ Validar: todas as parcelas devem ter IdParcela
   ↓
4. Retornar lista de transações processadas
```

**Campos gerados:**
- `IdTransacao` - Hash único FNV-1a 64-bit
- `IdParcela` - Hash MD5 16-char (apenas se parcelado)
- `Data`, `Estabelecimento`, `Valor`
- `DT_Fatura` - YYYYMM (ex: 202512)
- `TipoTransacao` - "Cartão de Crédito"
- `parcela_atual`, `total_parcelas` (apenas se parcelado)
- `Ano` - Ano da fatura

#### 3.2. Processador de Extrato

**Arquivo:** [app/blueprints/upload/processors/extrato_conta.py](app/blueprints/upload/processors/extrato_conta.py)

**Fluxo:**
```
1. Leitura do CSV/Excel
   ↓
2. Para cada linha:
   ├─ Gerar IdTransacao (FNV-1a)
   ├─ Classificar tipo: Débito, Transferência, Pix, etc
   └─ NÃO gera IdParcela (extratos não têm parcelas)
   ↓
3. Retornar lista de transações
```

---

### 🔍 4. Deduplicação

**Função:** `verificar_duplicatas()`  
**Arquivo:** [app/utils/deduplicator.py](app/utils/deduplicator.py)  
**Momento:** Após processamento, antes de exibir para usuário

**Ordem de verificação:**

#### 4.1. Para transações NÃO parceladas:
```
1. Buscar no banco por IdTransacao
   ↓
2. Se encontrou:
   └─ Marcar como 'duplicado'
   
3. Se não encontrou:
   └─ Marcar como 'novo'
```

#### 4.2. Para transações parceladas:
```
1. Buscar no banco por IdTransacao
   ↓
2. Se encontrou:
   └─ Marcar como 'duplicado'
   
3. Se não encontrou:
   ├─ Buscar contrato em BaseParcelas por IdParcela
   ├─ Se contrato existe:
   │  ├─ Comparar parcela_atual com qtd_pagas
   │  ├─ Se parcela_atual <= qtd_pagas:
   │  │  └─ Marcar como 'parcela_paga'
   │  └─ Senão:
   │     └─ Marcar como 'novo'
   │
   └─ Se contrato não existe:
      └─ Marcar como 'novo'
```

**Resultado:**
- Lista de transações com campo `status_duplicacao`
- Contadores: `novos`, `duplicados`, `parcelas_pagas`

---

### ✅ 5. Validação pelo Usuário

**Endpoint:** `GET /upload/confirmar`  
**Template:** [templates/confirmar_upload.html](templates/confirmar_upload.html)

**Exibição:**
```
┌─────────────────────────────────────────────┐
│ 📊 Resumo do Upload                         │
├─────────────────────────────────────────────┤
│ ✅ Novas: 45 transações                     │
│ ⚠️  Duplicadas: 5 transações                │
│ 🔄 Parcelas já pagas: 3 transações          │
├─────────────────────────────────────────────┤
│ [Tabela com todas as transações]            │
│ - Status de duplicação visível              │
│ - Possibilidade de desmarcar duplicatas     │
└─────────────────────────────────────────────┘
```

**Ações do usuário:**
- ✓ Revisar transações marcadas
- ✓ Desmarcar duplicatas se desejar importar mesmo assim
- ✓ Confirmar para prosseguir ou cancelar

---

### 💾 6. Salvamento no Banco de Dados

**Endpoint:** `POST /upload/salvar`  
**Arquivo:** [app/blueprints/upload/routes.py](app/blueprints/upload/routes.py) (~linhas 490-650)

**Fluxo detalhado do salvamento:**

#### 6.1. Preparação (linhas 504-510)
```python
1. Iniciar transação do banco
2. Extrair todos os IdParcela únicos das transações
3. PRÉ-CARREGAR todos os contratos de BaseParcelas em uma query:
   contratos = db_session.query(BaseParcelas)
                .filter(BaseParcelas.id_parcela.in_(ids_parcela))
                .all()
4. Criar dicionário {id_parcela: contrato} para lookup O(1)
   (Evita N+1 queries - otimização crítica!)
```

#### 6.2. Processar cada transação (linhas 512-577)
```python
Para cada transação nova (não duplicada):
    
    1. Normalizar estabelecimento
       └─ Remove espaços, converte maiúsculas, etc
    
    2. Criar JournalEntry:
       ├─ IdTransacao (PK)
       ├─ IdParcela (se parcelado)  ← FIX CRÍTICO linha 540
       ├─ Data, Estabelecimento, Valor
       ├─ DT_Fatura, TipoTransacao
       └─ parcela_atual, total_parcelas
    
    3. Adicionar à sessão
    
    4. SE é transação parcelada (tem IdParcela):
       ├─ Buscar contrato no dicionário (O(1))
       │
       ├─ Se contrato NÃO existe:
       │  └─ Criar novo em BaseParcelas:
       │     ├─ id_parcela
       │     ├─ estabelecimento
       │     ├─ valor_parcela
       │     ├─ qtd_parcelas
       │     ├─ qtd_pagas = 1
       │     ├─ status = 'ativo'
       │     └─ primeiro_vencimento, tipo_gasto, etc
       │
       └─ Se contrato EXISTE:
          └─ Incrementar qtd_pagas += 1
             ├─ Se qtd_pagas >= qtd_parcelas:
             │  └─ status = 'finalizado'
             └─ Senão:
                └─ status = 'ativo'
    
    5. Registrar em AuditLog
```

#### 6.3. Commit da transação (linha 578)
```python
db_session.commit()
```

---

### 🔄 7. Auto-Sync de BaseParcelas

**Momento:** Imediatamente após commit  
**Linhas:** ~580-610 de [routes.py](app/blueprints/upload/routes.py)  
**Introduzido em:** Commit aa6aac6

**Por que existe?**
- Antes: Usuário precisava rodar `migrate_parcelas.py` e `cleanup_orphans.py` manualmente
- Agora: Sistema sincroniza automaticamente após cada upload

**Fluxo do Auto-Sync:**

#### 7.1. Migração de Parcelas
```python
1. Buscar TODAS as transações parceladas:
   transacoes = JournalEntry.query
                .filter(IdParcela.isnot(None))
                .filter(TipoTransacao == 'Cartão de Crédito')
                .all()

2. Agrupar por IdParcela usando defaultdict:
   {
     'abc123': [transacao1, transacao2, transacao3],
     'def456': [transacao4, transacao5],
     ...
   }

3. Para cada IdParcela e suas transações:
   
   a) Contar quantas transações = qtd_pagas real
   
   b) Buscar contrato em BaseParcelas
   
   c) Atualizar ou criar:
      ├─ Se existe: atualizar qtd_pagas
      └─ Se não existe: criar novo contrato
   
   d) Atualizar status:
      ├─ Se qtd_pagas >= qtd_parcelas: 'finalizado'
      └─ Senão: 'ativo'

4. Commit das atualizações
```

#### 7.2. Limpeza de Órfãos
```python
1. Buscar todos os IdParcela distintos no JournalEntry:
   ids_em_uso = db_session.query(JournalEntry.IdParcela)
                 .distinct()
                 .all()

2. Buscar contratos em BaseParcelas que NÃO estão em ids_em_uso

3. Deletar contratos órfãos:
   └─ Contratos sem nenhuma transação correspondente
   
4. Commit da limpeza
```

**Resultado:**
- ✅ BaseParcelas sempre sincronizada
- ✅ Sem necessidade de scripts manuais
- ✅ qtd_pagas e status corretos
- ✅ Sem contratos órfãos

---

### 🎨 8. Classificação Automática (Opcional)

**Momento:** Após salvamento, se usuário clicar em "Classificar"  
**Arquivo:** [app/blueprints/upload/classifiers/auto_classifier.py](app/blueprints/upload/classifiers/auto_classifier.py)

**Fluxo de classificação:**

```
1. Carregar padrões existentes:
   └─ Tabela: padroes_classificacao
   
2. Para cada transação sem classificação:
   
   a) Normalizar estabelecimento
   
   b) Buscar padrão matching:
      ├─ Comparação por substring
      ├─ Comparação por similaridade (fuzzy)
      └─ Score de confiança
   
   c) Se padrão encontrado (score > threshold):
      ├─ Aplicar grupo
      ├─ Aplicar subgrupo
      ├─ Aplicar tipo de gasto
      └─ Copiar marcações
   
   d) Registrar em AuditLog

3. Retornar estatísticas:
   └─ Quantas classificadas, quantas pendentes
```

---

### 📊 9. Dashboard e Visualização

**Endpoints principais:**
- `/dashboard/` - Visão geral do mês
- `/admin/transacoes` - Administração de transações
- `/admin/parcelas` - Administração de contratos

**Ordem de carregamento do Dashboard:**

```
1. Query transações do mês atual:
   └─ Filtro por DT_Fatura

2. Agrupar por categoria/grupo:
   └─ Somar valores

3. Calcular estatísticas:
   ├─ Total gasto
   ├─ Média diária
   ├─ Comparação com mês anterior
   └─ Top estabelecimentos

4. Buscar contratos ativos:
   └─ BaseParcelas.status = 'ativo'

5. Renderizar gráficos:
   ├─ Pizza (categorias)
   ├─ Barras (evolução mensal)
   └─ Linha (tendência)

6. Exibir alertas:
   └─ Parcelas próximas de vencer
```

---

## 🔄 Ordem de Validações e Proteções

### Durante Upload:
1. ✓ Validação de extensão de arquivo
2. ✓ Validação de tamanho
3. ✓ Validação de formato CSV/Excel
4. ✓ Validação de colunas obrigatórias
5. ✓ Validação de tipos de dados (data, valor)

### Durante Processamento:
1. ✓ Normalização de estabelecimentos
2. ✓ Validação de parcelas (formato XX/YY)
3. ✓ Geração de hash IdTransacao (unicidade)
4. ✓ Geração de hash IdParcela (consistência)
5. ✓ Verificação de duplicatas

### Durante Salvamento:
1. ✓ Transação do banco (atomicidade)
2. ✓ Validação de integridade referencial
3. ✓ Registro de auditoria
4. ✓ Auto-sync de BaseParcelas
5. ✓ Limpeza de órfãos

### Proteções Implementadas:
- 🔒 **IdTransacao único** - Previne duplicatas
- 🔒 **IdParcela consistente** - Agrupa parcelas corretamente
- 🔒 **Deduplicação inteligente** - Verifica parcelas já pagas
- 🔒 **Transação atômica** - Rollback em caso de erro
- 🔒 **Audit log** - Rastreabilidade completa
- 🔒 **Auto-sync** - Dados sempre consistentes

---

## 🔑 Conceitos Importantes

### IdTransacao
- Hash FNV-1a 64-bit gerado a partir de: `data + estabelecimento + valor`
- Garante unicidade mesmo com importações duplicadas
- Sufixo `_N` adicionado se houver colisão no mesmo arquivo

### IdParcela
- Hash MD5 16-char gerado a partir de: `estabelecimento_normalizado + valor + qtd_parcelas`
- Identifica contratos de parcelamento
- Todas as parcelas da mesma compra compartilham o mesmo IdParcela

### BaseParcelas
- Tabela de contratos de parcelamento
- Campos: `id_parcela`, `estabelecimento`, `valor_parcela`, `qtd_parcelas`, `qtd_pagas`, `status`
- **Auto-atualizada** após cada upload (desde commit aa6aac6)

### Deduplicação
- Verifica IdTransacao em `journal_entries`
- Para parceladas: verifica parcela_atual vs `BaseParcelas.qtd_pagas`
- Status: `duplicado`, `parcela_paga`, `novo`

---

## 🚀 Como Executar

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python run.py

# Acessar no navegador
http://localhost:5001
```

---

## 📝 Arquivos Essenciais

| Arquivo | Descrição |
|---------|-----------|
| `run.py` | Ponto de entrada da aplicação Flask |
| `app/__init__.py` | Factory da aplicação (create_app) |
| `app/models.py` | Modelos SQLAlchemy (JournalEntry, BaseParcelas, etc) |
| `app/blueprints/upload/routes.py` | Lógica principal de upload e salvamento |
| `app/blueprints/upload/processors/fatura_cartao.py` | Processador de faturas (🔒 CRÍTICO) |
| `app/utils/hasher.py` | Geração de IDs únicos |
| `app/utils/deduplicator.py` | Detecção de duplicatas |

---

## ⚠️ Tratamento de Erros e Casos Especiais

### 🔴 Erros Durante Upload

#### 1. Arquivo Inválido
```python
Erro: Extensão não permitida
↓
Resposta: Mensagem flash de erro
Ação: Redireciona para /upload
```

#### 2. Formato Não Reconhecido
```python
Erro: Colunas obrigatórias ausentes
↓
Resposta: Lista as colunas esperadas
Ação: Usuário precisa ajustar o arquivo
```

#### 3. Erro de Processamento
```python
Erro: Exception durante processamento
↓
Resposta: Erro logado, mensagem genérica ao usuário
Ação: Rollback automático, arquivo descartado
Proteção: try/except no processador
```

### 🟡 Casos Especiais de Parcelas

#### 1. Parcelas com Valores Diferentes
```
Problema: Compra parcelada com entrada ou última parcela diferente
Solução: Chave de agrupamento inclui VALOR da parcela
Resultado: Cada valor gera IdParcela diferente ✓

Exemplo:
- Compra 10x de R$ 100,00 → IdParcela: abc123
- Compra 10x de R$ 90,00  → IdParcela: def456 (diferente!)
```

#### 2. Parcelas Duplicadas no Mesmo Arquivo
```
Problema: Usuário importa mesmo arquivo 2x
Solução: hash_counter incrementa sufixo em IdTransacao
Resultado: IdTransacao único mesmo com duplicata

Exemplo:
- 1ª importação: IdTransacao = abc123
- 2ª importação: IdTransacao = abc123_1 (sufixo _1)
```

#### 3. Parcelas Saltadas
```
Problema: Usuário pula meses (parcela 5 paga, parcela 6 não)
Solução: Sistema considera qtd_pagas total, não sequência
Resultado: Status correto independente da ordem

BaseParcelas.qtd_pagas = COUNT(*) de transações
Não valida se são sequenciais (5, 6, 7...)
```

#### 4. Upload Parcial de Parcelas
```
Problema: Importa apenas parte das parcelas (ex: 7 de 10)
Solução: BaseParcelas.status = 'ativo' até completar
Resultado: Dashboard mostra progresso correto

Exemplo:
- qtd_pagas = 7
- qtd_parcelas = 10
- status = 'ativo'
- Progresso: 7/10 (70%)
```

### 🟢 Casos de Sucesso

#### 1. Upload Incremental
```
Mês 1: Importa fatura-202510.csv (parcelas 1-3)
↓
BaseParcelas: qtd_pagas = 3, status = 'ativo'

Mês 2: Importa fatura-202511.csv (parcelas 4-6)
↓
Auto-sync atualiza: qtd_pagas = 6, status = 'ativo'

Mês 3: Importa fatura-202512.csv (parcelas 7-10)
↓
Auto-sync atualiza: qtd_pagas = 10, status = 'finalizado' ✓
```

#### 2. Re-upload do Mesmo Arquivo
```
Importa fatura-202512.csv
↓
Deduplicação detecta: TODAS duplicadas
↓
Confirmar upload: Usuário vê aviso de duplicatas
↓
Opções:
  [x] Importar mesmo assim (recria transações)
  [ ] Cancelar (padrão recomendado)
```

---

## 🛠️ Debugging e Troubleshooting

### Logs Importantes

#### 1. Audit Log (Banco de Dados)
```sql
SELECT * FROM audit_log 
WHERE acao IN ('insert', 'update', 'delete')
ORDER BY data_acao DESC
LIMIT 100;
```
**Campos:**
- `data_acao` - Timestamp
- `usuario` - Quem fez (sempre 'sistema' por enquanto)
- `acao` - insert/update/delete
- `tabela` - journal_entries/base_parcelas/etc
- `detalhes` - JSON com dados da operação

#### 2. Console do Flask (Terminal)
```
✅ Banco de dados inicializado: financas.db
🚀 Iniciando aplicação modularizada...
📍 Acesse: http://localhost:5001
...
127.0.0.1 - - [27/Dec/2025 00:55:10] "POST /upload/salvar HTTP/1.1" 200
```

#### 3. Validação de IdParcela
```python
# Script para verificar consistência
python _temp_scripts/debug_vpd.py
```

### Comandos Úteis

#### Verificar Transações Duplicadas
```python
from app.models import get_db_session, JournalEntry

session = get_db_session('financas.db')
duplicados = session.query(JournalEntry.IdTransacao, 
                           func.count(JournalEntry.IdTransacao))
                    .group_by(JournalEntry.IdTransacao)
                    .having(func.count(JournalEntry.IdTransacao) > 1)
                    .all()
```

#### Verificar BaseParcelas Inconsistente
```python
# Rodar auto-sync manualmente
python scripts/migrate_parcelas.py
python scripts/cleanup_orphans.py
```

#### Listar Contratos Ativos
```sql
SELECT id_parcela, estabelecimento, qtd_pagas, qtd_parcelas, status
FROM base_parcelas
WHERE status = 'ativo'
ORDER BY qtd_pagas DESC;
```

#### Transações Sem IdParcela (Erro!)
```sql
-- Parceladas devem TER IdParcela
SELECT COUNT(*) FROM journal_entries
WHERE IdParcela IS NULL
  AND Estabelecimento LIKE '%(%/%)'
  AND TipoTransacao = 'Cartão de Crédito';

-- Deve retornar 0!
```

### Problemas Comuns

#### 1. IdParcela NULL em Parceladas
**Sintoma:** Parcelas sem IdParcela no banco  
**Causa:** Bug no processador (corrigido em commit aa6aac6)  
**Solução:** 
```bash
# Corrigir manualmente
python _temp_scripts/fix_id_parcela_historico.py
```

#### 2. BaseParcelas Desatualizada
**Sintoma:** qtd_pagas diferente da contagem real  
**Causa:** Falta de auto-sync em versões antigas  
**Solução:**
```bash
python scripts/migrate_parcelas.py
```

#### 3. Contratos Órfãos
**Sintoma:** BaseParcelas tem registros sem transações  
**Causa:** Deleções manuais de transações  
**Solução:**
```bash
python scripts/cleanup_orphans.py
```

#### 4. Servidor Não Inicia
**Sintoma:** Erro "Port 5001 already in use"  
**Solução:**
```bash
lsof -ti:5001 | xargs kill -9
python run.py
```

---

## 📈 Performance e Otimizações

### Otimizações Implementadas

#### 1. Pré-carregamento de BaseParcelas (Crítico!)
```python
# ❌ ANTES (N+1 queries)
for trans in transacoes:
    contrato = db.query(BaseParcelas).filter_by(
        id_parcela=trans['IdParcela']
    ).first()
    # 100 transações = 100 queries!

# ✅ DEPOIS (2 queries)
ids = [t['IdParcela'] for t in transacoes if t['IdParcela']]
contratos = db.query(BaseParcelas).filter(
    BaseParcelas.id_parcela.in_(ids)
).all()
contratos_dict = {c.id_parcela: c for c in contratos}
# 1 query única + lookup O(1)
```

**Impacto:**
- 100 transações: 100 queries → 2 queries
- Redução de ~98% no tempo de salvamento

#### 2. Índices no Banco de Dados
```sql
-- Automáticos (PKs)
CREATE INDEX idx_journal_entries_id_transacao 
    ON journal_entries(IdTransacao);
CREATE INDEX idx_base_parcelas_id_parcela 
    ON base_parcelas(id_parcela);

-- Úteis para queries
CREATE INDEX idx_journal_entries_dt_fatura 
    ON journal_entries(DT_Fatura);
CREATE INDEX idx_journal_entries_id_parcela 
    ON journal_entries(IdParcela);
```

#### 3. Uso de defaultdict para Agrupamento
```python
from collections import defaultdict

# Agrupar transações por IdParcela
por_id = defaultdict(list)
for t in transacoes:
    por_id[t.IdParcela].append(t)

# Acesso O(1), agrupamento automático
```

### Métricas de Performance

**Upload típico (50 transações, 20 parceladas):**
- Processamento: ~0.5s
- Deduplicação: ~0.2s
- Salvamento: ~0.3s
- Auto-sync: ~0.1s
- **Total: ~1.1s**

**Upload grande (500 transações, 200 parceladas):**
- Processamento: ~2s
- Deduplicação: ~1s
- Salvamento: ~1.5s
- Auto-sync: ~0.5s
- **Total: ~5s**

---

## ⚠️ Não Modificar

- `app/blueprints/upload/processors/fatura_cartao.py` - Processador testado e validado
- `app/utils/hasher.py` - Lógica de hash crítica para integridade
- `app/models.py` - Alterações podem quebrar queries existentes

---

## 🔧 Manutenção

### Scripts Disponíveis

```bash
# Sincronizar BaseParcelas (agora automático no upload)
python scripts/migrate_parcelas.py

# Limpar contratos órfãos (agora automático no upload)
python scripts/cleanup_orphans.py

# Analisar transações
python scripts/analisar_transacoes.py

# Buscar transações similares
python scripts/buscar_similares.py
```

### Adicionar Novo Processador

1. Criar arquivo em `app/blueprints/upload/processors/`
2. Implementar função `processar(file_path, origem)`
3. Retornar lista de dicts com transações
4. Registrar em `app/blueprints/upload/processors/__init__.py`

---

## 📊 Banco de Dados

### Tabelas Principais

- `journal_entries` - Transações financeiras
- `base_parcelas` - Contratos de parcelamento
- `audit_log` - Log de auditoria
- `grupos` - Grupos de categorização
- `marcacoes` - Marcações/tags
- `padroes_classificacao` - Padrões de classificação automática

### Campos Importantes

**journal_entries:**
- `IdTransacao` (PK) - Hash único da transação
- `IdParcela` - Hash do contrato de parcelamento (NULL se não parcelado)
- `Data`, `Estabelecimento`, `Valor`
- `DT_Fatura` - Período da fatura (YYYYMM)
- `TipoTransacao` - Tipo (Cartão de Crédito, Débito, etc)

**base_parcelas:**
- `id_parcela` (PK) - Hash do contrato
- `qtd_parcelas` - Total de parcelas
- `qtd_pagas` - Parcelas já pagas (auto-atualizado)
- `status` - ativo/finalizado (auto-atualizado)

---

## 🎨 Frontend

- **Framework**: Bootstrap 5
- **Templates**: Jinja2
- **JavaScript**: Vanilla JS + Chart.js para gráficos
- **Estilo**: CSS customizado em `/static/css/style.css`

---

## 🔐 Segurança

- Senhas não são armazenadas (app de uso pessoal)
- Validação de entrada em todos os formulários
- Sanitização de nomes de arquivo
- Proteção contra duplicatas

---

## 📚 Documentação Adicional

- `README.md` - Instruções gerais de uso
- `BUGS.md` - Lista de bugs conhecidos e correções aplicadas
- `MODULARIZACAO.md` - Documentação da arquitetura modular
- `PROTECAO_BASES.md` - Proteção de bases de dados
- `STATUSPROJETO.md` - Status atual do desenvolvimento

---

## 🎯 Próximos Passos

- [ ] Implementar exportação de relatórios (Excel/PDF)
- [ ] Dashboard com gráficos avançados
- [ ] Sistema de metas e orçamento
- [ ] API REST para integração externa
- [ ] Notificações de vencimento

---

## 📊 Diagramas de Fluxo

### Fluxo Completo de Upload (Visão Geral)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INÍCIO: Usuário                            │
│                      Seleciona arquivo CSV                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  1. Upload de Arquivo │
                  │   (routes.py)         │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  2. Detecção Formato  │
                  │   (detector.py)       │
                  └──────────┬────────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
        ┌───────────────────┐   ┌───────────────────┐
        │ fatura_cartao.py  │   │ extrato_conta.py  │
        │   (com parcelas)  │   │  (sem parcelas)   │
        └─────────┬─────────┘   └─────────┬─────────┘
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  3. Deduplicação     │
                   │  (deduplicator.py)   │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  4. Confirmar Upload │
                   │  (template HTML)     │
                   └──────────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 │ Usuário confirma?       │
                 └────────────┬────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ SIM               │ NÃO → Cancela
                    ▼                   │
         ┌─────────────────────┐        │
         │  5. Salvar no Banco  │        │
         │   + JournalEntry     │        │
         │   + BaseParcelas     │        │
         └──────────┬───────────┘        │
                    │                    │
                    ▼                    │
         ┌─────────────────────┐         │
         │  6. Auto-Sync        │         │
         │   migrate_parcelas   │         │
         │   cleanup_orphans    │         │
         └──────────┬───────────┘         │
                    │                     │
                    ▼                     │
         ┌─────────────────────┐          │
         │  7. Classificação    │          │
         │   (opcional)         │          │
         └──────────┬───────────┘          │
                    │                      │
                    ▼                      ▼
         ┌────────────────────────────────────┐
         │     FIM: Redireciona Dashboard     │
         └────────────────────────────────────┘
```

### Fluxo de Detecção de Parcelas

```
┌──────────────────────────────────────────────────┐
│  Linha do CSV: "LOJA XYZ 10/10"  R$ 100,00      │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │  Regex: \d{1,2}/\d{1,2}  │
           │  Match: "10/10"           │
           └──────────┬───────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │  Extrair:             │
           │  parcela_atual = 10   │
           │  total_parcelas = 10  │
           └──────────┬───────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │  Remover " 10/10"     │
           │  Estabelecimento =    │
           │  "LOJA XYZ"           │
           └──────────┬───────────┘
                      │
                      ▼
           ┌──────────────────────────────┐
           │  Chave de Agrupamento:        │
           │  "LOJA XYZ_10_100.00"         │
           │  (estab + total + valor)      │
           └──────────┬───────────────┘
                      │
                      ▼
           ┌─────────────────────────────┐
           │  Gerar IdParcela (MD5):      │
           │  MD5("loja xyz|100.00|10")   │
           │  = "abc123def456..."          │
           └─────────────────────────────┘
```

### Fluxo de Deduplicação de Parcelas

```
                  ┌────────────────────────┐
                  │  Transação Parcelada   │
                  │  IdTransacao: xyz789   │
                  │  IdParcela: abc123     │
                  │  parcela_atual: 5      │
                  └───────────┬────────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │  Buscar IdTransacao    │
                 │  no banco?             │
                 └────────┬───────────────┘
                          │
              ┌───────────┴───────────┐
              │ ENCONTROU             │ NÃO ENCONTROU
              ▼                       ▼
    ┌─────────────────┐    ┌─────────────────────┐
    │ STATUS:         │    │ Buscar IdParcela    │
    │ 'duplicado'     │    │ em BaseParcelas?    │
    └─────────────────┘    └──────────┬──────────┘
                                       │
                           ┌───────────┴───────────┐
                           │ ENCONTROU             │ NÃO ENCONTROU
                           ▼                       ▼
               ┌─────────────────────┐  ┌─────────────────┐
               │ Comparar:           │  │ STATUS:         │
               │ parcela_atual (5)   │  │ 'novo'          │
               │ vs                  │  │                 │
               │ qtd_pagas (3)       │  └─────────────────┘
               └──────────┬──────────┘
                          │
              ┌───────────┴───────────┐
              │ 5 <= 3?               │ 5 > 3?
              ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐
    │ STATUS:         │    │ STATUS:         │
    │ 'parcela_paga'  │    │ 'novo'          │
    └─────────────────┘    └─────────────────┘
```

### Estrutura de Dados - Relacionamentos

```
┌──────────────────────────────────────────────────────┐
│              JournalEntry (Transações)               │
├──────────────────────────────────────────────────────┤
│ PK: IdTransacao (FNV-1a 64-bit)                      │
│ FK: IdParcela → BaseParcelas.id_parcela (NULLABLE)   │
│     Data, Estabelecimento, Valor                     │
│     DT_Fatura (YYYYMM), TipoTransacao                │
│     parcela_atual, total_parcelas                    │
└──────────────────┬───────────────────────────────────┘
                   │
                   │ N:1 (muitas transações → 1 contrato)
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│            BaseParcelas (Contratos)                  │
├──────────────────────────────────────────────────────┤
│ PK: id_parcela (MD5 16-char)                         │
│     estabelecimento, valor_parcela                   │
│     qtd_parcelas (total planejado)                   │
│     qtd_pagas (contagem real) ← Auto-atualizado      │
│     status ('ativo'/'finalizado') ← Auto-atualizado  │
└──────────────────────────────────────────────────────┘

Exemplo:
┌─────────────────────────────────────────────────┐
│ BaseParcelas                                    │
│ id_parcela: "abc123"                            │
│ estabelecimento: "LOJA XYZ"                     │
│ valor_parcela: 100.00                           │
│ qtd_parcelas: 10                                │
│ qtd_pagas: 7 ← Calculado por COUNT(*)          │
│ status: 'ativo' ← (7 < 10)                     │
└─────────────────────────────────────────────────┘
              ▲
              │
    ┌─────────┼─────────────────┐
    │         │                 │
┌───┴───┐ ┌───┴───┐  ...  ┌────┴────┐
│ Trans │ │ Trans │        │ Trans   │
│ 1/10  │ │ 2/10  │        │ 7/10    │
│abc123 │ │abc123 │        │ abc123  │
└───────┘ └───────┘        └─────────┘
  (7 transações com IdParcela = "abc123")
```

### Auto-Sync - Lógica de Atualização

```
┌────────────────────────────────────────────────────┐
│          TRIGGER: Upload concluído                 │
│          db_session.commit() executado             │
└───────────────────────┬────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  PASSO 1: Buscar Transações   │
        │  SELECT * FROM journal_entries│
        │  WHERE IdParcela IS NOT NULL  │
        │  AND TipoTransacao = 'CC'     │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  PASSO 2: Agrupar por IdParcela│
        │  {                             │
        │   'abc123': [t1, t2, t3],     │
        │   'def456': [t4, t5],         │
        │   ...                          │
        │  }                             │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────────┐
        │  PASSO 3: Para cada IdParcela     │
        │                                   │
        │  qtd_pagas = len(transacoes)      │
        │                                   │
        │  Buscar em BaseParcelas           │
        │  ├─ Se existe: UPDATE             │
        │  └─ Se não: INSERT                │
        │                                   │
        │  Atualizar status:                │
        │  IF qtd_pagas >= qtd_parcelas:    │
        │     status = 'finalizado'         │
        │  ELSE:                            │
        │     status = 'ativo'              │
        └──────────────┬────────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  PASSO 4: Cleanup Órfãos      │
        │                               │
        │  ids_em_uso = SELECT DISTINCT │
        │    IdParcela FROM journal     │
        │                               │
        │  DELETE FROM base_parcelas    │
        │  WHERE id_parcela NOT IN      │
        │    (ids_em_uso)               │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  PASSO 5: Commit Final        │
        │  db_session.commit()          │
        └───────────────────────────────┘
```

---

**Última atualização:** 27 de dezembro de 2025
**Versão:** 3.0
**Commit:** aa6aac6
