# 📚 Índice de Documentação

**Última atualização:** 23/01/2026

Este é o índice completo da documentação do projeto.

---

## 🔴 Regras Críticas

Leia PRIMEIRO antes de modificar qualquer código:

- [CRITICAL.md](rules/CRITICAL.md) - Regras invioláveis (Git Sync, Database, Filtros)
- [security.md](rules/security.md) - Segurança (JWT, Secrets, Rate Limiting)
- [architecture.md](rules/architecture.md) - Arquitetura (Domains, Features, Isolamento)

---

## 🚀 Guias Práticos

Passo-a-passo para tarefas comuns:

- [quick-start.md](guides/quick-start.md) - Iniciar projeto do zero
- [deploy.md](guides/deploy.md) - Deploy em produção
- [troubleshooting.md](guides/troubleshooting.md) - Resolver problemas comuns
- [testing.md](guides/testing.md) - Testar isolamento e autenticação

---

## 📖 Referência Técnica

Consulta rápida:

- [api-endpoints.md](reference/api-endpoints.md) - Lista completa de APIs
- [database-schema.md](reference/database-schema.md) - Schema do banco
- [accounts.md](reference/accounts.md) - Contas de teste
- [environment.md](reference/environment.md) - Variáveis de ambiente

---

## 🔍 Busca Rápida

**Tenho um problema com...**

- **Autenticação/Login** → [security.md](rules/security.md)
- **Deploy** → [deploy.md](guides/deploy.md)
- **Backend não inicia** → [troubleshooting.md](guides/troubleshooting.md)
- **Estrutura de domínios** → [architecture.md](rules/architecture.md)
- **Sincronização git** → [CRITICAL.md](rules/CRITICAL.md#git-sync)
- **Database** → [CRITICAL.md](rules/CRITICAL.md#database)

---

## 📋 Workflow Completo

1. Ler requisição do usuário
2. Identificar categoria (feature, bug, deploy)
3. Consultar documento correspondente
4. Implementar seguindo padrões
5. Testar isoladamente
6. Commitar e fazer deploy se necessário

---

**Ver também:** [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Resumo CORE
