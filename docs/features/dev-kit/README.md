# Dev Kit — FinUp

Documentação completa do kit de ferramentas de desenvolvimento: regras para o modelo, skills para o desenvolvedor, pendências de código e processo de deploy.

---

## Filosofia: Dois Layers de Qualidade

```
WRITE TIME  →  Cursor rules   →  modelo já sabe as convenções ao escrever
                                  previne antes de acontecer, zero fricção

REVIEW TIME →  Claude skills  →  você invoca para auditar, scaffoldar, analisar
                                  mais poderoso, lê múltiplos arquivos, roda bash
```

Cada skill tem um "irmão passivo" em Cursor rule e vice-versa. A rule previne, a skill audita o que passou.

---

## Arquivos desta pasta

| Arquivo | Conteúdo |
|---------|----------|
| `CURSOR-RULES.md` | Conteúdo completo de cada `.mdc` — pronto para criar em `.cursor/rules/` |
| `CLAUDE-SKILLS.md` | Spec completa de cada slash command — pronto para criar em `.claude/commands/` |
| `PENDENCIAS.md` | Todas as alterações de código pendentes: segurança, performance, dev experience |
| `DEPLOY.md` | Processo canônico de deploy + rollback + mapa de portas |

---

## Checklist de implementação

### Cursor Rules — criar em `.cursor/rules/`

- [ ] `security-backend.mdc` — padrões de segurança para `.py`
- [ ] `security-frontend.mdc` — padrões de segurança para `.ts/.tsx`
- [ ] `perf-backend.mdc` — performance e queries para `.py`
- [ ] `perf-frontend.mdc` — performance React/Next.js para `.ts/.tsx`
- [ ] `new-domain.mdc` — convenções ao criar domínio backend
- [ ] `new-feature.mdc` — convenções ao criar feature frontend
- [ ] `migration.mdc` — boas práticas ao escrever migrations Alembic
- [ ] `deploy.mdc` — mapa de portas e sequência de deploy

### Claude Code Skills — criar em `.claude/commands/`

- [x] `commit.md` — ✅ criado e funcional (`/commit`)
- [ ] `new-domain.md` — scaffolda domínio backend completo
- [ ] `new-feature.md` — scaffolda feature frontend completa
- [ ] `security-check.md` — auditoria de segurança completa (OWASP + padrões do projeto)
- [ ] `perf-check.md` — auditoria de performance completa
- [ ] `api-review.md` — lista endpoints de um domínio em tabela
- [ ] `feature-status.md` — estado atual da sessão de trabalho
- [ ] `migration.md` — cria migration Alembic com boas práticas
- [ ] `deploy.md` — executa processo canônico de deploy

### Código pendente

Ver `PENDENCIAS.md` para lista completa com arquivo, linha e o que fazer.

---

## Mapa de relação skill ↔ rule

| Tema | Cursor Rule | Claude Skill |
|------|-------------|-------------|
| Segurança backend | `security-backend.mdc` | `/security-check` |
| Segurança frontend | `security-frontend.mdc` | `/security-check` |
| Performance backend | `perf-backend.mdc` | `/perf-check` |
| Performance frontend | `perf-frontend.mdc` | `/perf-check` |
| Novo domínio | `new-domain.mdc` | `/new-domain` |
| Nova feature | `new-feature.mdc` | `/new-feature` |
| Migrations | `migration.mdc` | `/migration` |
| Deploy | `deploy.mdc` | `/deploy` |
| API review | — | `/api-review` |
| Status da sessão | — | `/feature-status` |
