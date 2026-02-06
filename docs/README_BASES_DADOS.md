# 🗄️ Bases de Dados do Projeto FinUp

Este documento lista todas as bases de dados utilizadas no projeto, os campos (variáveis) de cada tabela e explica o uso de cada campo.

---

## 📍 Localização dos Bancos

- **Desenvolvimento:**
  - SQLite: `app_dev/backend/database/financas_dev.db`
- **Produção:**
  - PostgreSQL: `finup_db` (Hostinger VPS)

---

## 🏦 Tabelas Principais

### 1. journal_entries (Transações Financeiras)
| Campo              | Tipo      | Descrição/Utilização                                                                 |
|--------------------|-----------|-------------------------------------------------------------------------------------|
| id                 | String    | Identificador único da transação (IdTransacao, hash condicional)                    |
| user_id            | Integer   | ID do usuário dono da transação                                                     |
| Data               | String    | Data da transação (DD/MM/YYYY) - NÃO usar para filtros!                             |
| Ano                | Integer   | Ano da transação (usado para filtros rápidos)                                       |
| Mes                | Integer   | Mês da transação (usado para filtros rápidos)                                       |
| MesFatura          | String    | Mês/ano da fatura (YYYYMM) - para cartões                                           |
| Valor              | Float     | Valor da transação                                                                  |
| Estabelecimento    | String    | Nome do estabelecimento ou origem                                                   |
| CategoriaGeral     | String    | Categoria principal (Despesa, Receita, Investimento)                                |
| GrupoMarcacao      | String    | Grupo de marcação aplicado                                                          |
| IgnorarDashboard   | Boolean   | Se 1, transação não aparece em dashboards                                           |
| Observacao         | String    | Observações adicionais                                                              |
| created_at         | DateTime  | Data/hora de criação                                                                |
| updated_at         | DateTime  | Data/hora de última atualização                                                     |

**Uso dos campos:**
- `id`: Garante unicidade e deduplicação, gerado por hash condicional (ver regras de extrato/fatura)
- `user_id`: Permite multiusuário, isola dados por usuário
- `Ano`, `Mes`: Filtros rápidos e eficientes em queries
- `CategoriaGeral`, `GrupoMarcacao`: Usados para dashboards, relatórios e marcações
- `IgnorarDashboard`: Permite ocultar lançamentos específicos dos gráficos

---

### 2. base_marcacoes (Grupos e Marcações)
| Campo         | Tipo      | Descrição/Utilização                                         |
|---------------|-----------|-------------------------------------------------------------|
| id            | Integer   | Identificador único do grupo/marcação                        |
| nome          | String    | Nome do grupo/marcação                                       |
| categoria     | String    | Categoria associada (Despesa, Receita, Investimento)         |
| tipo          | String    | Tipo de marcação (principal, subgrupo, categoria)            |
| cor           | String    | Cor para exibição nos dashboards                             |
| ativo         | Boolean   | Se está ativo para seleção                                   |
| ordem         | Integer   | Ordem de exibição                                            |
| created_at    | DateTime  | Data/hora de criação                                         |
| updated_at    | DateTime  | Data/hora de última atualização                              |

**Uso dos campos:**
- `nome`, `categoria`, `tipo`: Definem a hierarquia de marcações
- `cor`, `ordem`: Usados para visualização e ordenação nos dashboards
- `ativo`: Permite ocultar grupos não utilizados

---

### 3. marcacoes (Marcações Aplicadas)
| Campo         | Tipo      | Descrição/Utilização                                         |
|---------------|-----------|-------------------------------------------------------------|
| id            | Integer   | Identificador único da marcação aplicada                     |
| transacao_id  | String    | ID da transação (journal_entries.id)                         |
| marcacao_id   | Integer   | ID da marcação (base_marcacoes.id)                           |
| tipo          | String    | Tipo de marcação (manual, automática)                        |
| created_at    | DateTime  | Data/hora de criação                                         |
| updated_at    | DateTime  | Data/hora de última atualização                              |

**Uso dos campos:**
- Permite múltiplas marcações por transação
- `tipo`: Diferencia marcação automática (regra) de manual (usuário)

---

### 4. users (Usuários)
| Campo         | Tipo      | Descrição/Utilização                                         |
|---------------|-----------|-------------------------------------------------------------|
| id            | Integer   | Identificador único do usuário                               |
| email         | String    | Email do usuário (login)                                     |
| senha_hash    | String    | Hash da senha (nunca armazenar senha em texto)               |
| nome          | String    | Nome completo                                                |
| role          | String    | Papel (admin, user)                                          |
| ativo         | Boolean   | Se está ativo para login                                     |
| created_at    | DateTime  | Data/hora de criação                                         |
| updated_at    | DateTime  | Data/hora de última atualização                              |

**Uso dos campos:**
- Controle de acesso, permissões, auditoria
- `role`: Define acesso a telas e funcionalidades

---

### 5. investimentos_portfolio (Investimentos)
| Campo              | Tipo      | Descrição/Utilização                                         |
|--------------------|-----------|-------------------------------------------------------------|
| id                 | Integer   | Identificador único do investimento                          |
| user_id            | Integer   | ID do usuário dono do investimento                           |
| nome_produto       | String    | Nome do ativo/investimento                                   |
| tipo_investimento  | String    | Tipo (Renda Fixa, Ação, FII, etc)                            |
| corretora          | String    | Nome da corretora                                            |
| valor_atual        | Float     | Valor atual do investimento                                  |
| valor_investido    | Float     | Valor investido                                              |
| rendimento_total   | Float     | Rendimento acumulado                                         |
| rendimento_percentual | Float  | Rendimento em %                                              |
| created_at         | DateTime  | Data/hora de criação                                         |
| updated_at         | DateTime  | Data/hora de última atualização                              |

**Uso dos campos:**
- Dashboards de investimentos, gráficos de evolução
- Filtros por tipo, corretora, período

---

### 6. rendimentos_timeline (Rendimentos Mensais)
| Campo         | Tipo      | Descrição/Utilização                                         |
|---------------|-----------|-------------------------------------------------------------|
| id            | Integer   | Identificador único do rendimento                            |
| user_id       | Integer   | ID do usuário                                                |
| anomes        | Integer   | Ano e mês (YYYYMM)                                           |
| rendimento_mes| Float     | Valor do rendimento no mês                                   |
| created_at    | DateTime  | Data/hora de criação                                         |
| updated_at    | DateTime  | Data/hora de última atualização                              |

**Uso dos campos:**
- Gráficos de evolução temporal de investimentos
- Dashboards mensais

---

### 7. base_grupos_config (Configuração de Grupos)
| Campo         | Tipo      | Descrição/Utilização                                         |
|---------------|-----------|-------------------------------------------------------------|
| id            | Integer   | Identificador único do grupo                                 |
| nome          | String    | Nome do grupo                                                |
| tipo          | String    | Tipo (Despesa, Receita, Investimento)                        |
| ordem         | Integer   | Ordem de exibição                                            |
| ativo         | Boolean   | Se está ativo para seleção                                   |
| cor           | String    | Cor para dashboards                                          |
| created_at    | DateTime  | Data/hora de criação                                         |
| updated_at    | DateTime  | Data/hora de última atualização                              |

**Uso dos campos:**
- Configuração dinâmica de grupos para marcações e dashboards

---

## 🗄️ Outras Tabelas
- **exclusoes**: Controle de exclusões manuais/automáticas
- **uploads**: Histórico de uploads realizados
- **settings**: Configurações do sistema e do usuário

---

## ⚡ Observações Importantes
- **Filtros SQL:** SEMPRE usar campos Ano/Mes/MesFatura para performance
- **Deduplicação:** IdTransacao é gerado por hash condicional (ver regras)
- **Marcações:** Permite múltiplas por transação, hierarquia flexível
- **Segurança:** Nunca armazenar dados sensíveis em texto puro

---

Para detalhes de schema, consulte os arquivos de models e migrations em `app_dev/backend/app/domains/*/models.py` e `app_dev/backend/database/migrations/`.
