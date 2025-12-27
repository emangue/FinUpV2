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

## 🔄 Fluxo Principal de Upload

1. **Upload** (`/upload`) - Usuário seleciona arquivo CSV/Excel
2. **Detecção** - Sistema detecta formato (fatura_cartao ou extrato_conta)
3. **Processamento** - Processador específico extrai transações
4. **Deduplicação** - Sistema identifica duplicatas
5. **Validação** - Usuário revisa e confirma transações
6. **Salvamento** - Transações salvas no banco
7. **Auto-Sync** ✨ - BaseParcelas atualiza automaticamente:
   - Conta qtd_pagas por IdParcela
   - Atualiza status (ativo/finalizado)
   - Remove contratos órfãos

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

**Última atualização:** 27 de dezembro de 2025
**Versão:** 3.0
**Commit:** aa6aac6
