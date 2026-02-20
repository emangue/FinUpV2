# Auditoria de Segurança – 16/02/2026

## Resumo

Validação de segurança do app_dev e app_admin após deploy, com foco em:
- IPs e credenciais hardcoded
- Dados sensíveis em trânsito (front ↔ back)
- Arquivos sensíveis versionados no git

---

## 1. Correções aplicadas

### 1.1 Scripts com senha hardcoded (corrigido)

| Arquivo | Antes | Depois |
|---------|-------|--------|
| `scripts/migration/sync_investimentos_local_para_servidor.py` | `POSTGRES_DSN = "...FinUp2026SecurePass@148.230.78.91..."` | Exige `PROD_DATABASE_URL` ou `DATABASE_URL` via env |
| `scripts/deploy/sync_investimentos_para_servidor.sh` | `export PROD_DATABASE_URL='...FinUp2026SecurePass...'` | Lê de `app_dev/backend/.env` |
| `scripts/diagnostic/validar_patrimonio_no_servidor.sh` | `PGPASSWORD="${POSTGRES_PASSWORD:-FinUp2026SecurePass}"` | Lê de `.env` ou exige variável |
| `app_dev/backend/.env.example` | Comentário com senha real | Placeholder `SUA_SENHA_FORTE` |

### 1.2 Uso dos scripts após correção

**Sync investimentos (local → servidor):**
```bash
# No servidor: usa DATABASE_URL do app_dev/backend/.env automaticamente

# Local (se rodar direto): defina antes
export PROD_DATABASE_URL='postgresql://user:senha@host:5432/db'
python scripts/migration/sync_investimentos_local_para_servidor.py --yes
```

**Validação patrimônio:**
```bash
# No servidor: lê DATABASE_URL do .env
# Ou: export PGPASSWORD=... antes de rodar
```

---

## 2. Arquivos que ainda contêm referências sensíveis

Estes arquivos estão no repositório e contêm a senha antiga em documentação ou exemplos. **Não foram alterados** para evitar quebrar referências históricas, mas a senha deve ser considerada **comprometida** e trocada.

| Arquivo | Conteúdo |
|---------|----------|
| `docs/deploy/AVALIACAO_SEGURANCA_HACKER_2026.md` | Password em texto |
| `docs/deploy/DEPLOY_MEUFINUP_ATUALIZACAO_2026.md` | PGPASSWORD em exemplos |
| `docs/deploy/SSH_ACCESS.md` | Connection string |
| `docs/deploy/STATUS_DEPLOY.md` | Password em checklist |
| `docs/features/mobile-v1/02-TECH_SPEC/INFRASTRUCTURE.md` | Senha em doc técnica |
| `scripts/migration/migrate_sqlite_to_postgres.py` | POSTGRES_DSN hardcoded |
| `scripts/migration/fix_migration_v2.py` | POSTGRES_DSN hardcoded |
| `temp/execute_migration.sh`, `temp/run_migration.sh` | PGPASSWORD hardcoded (scripts em `temp/` – considerar remover do repo) |

**Recomendação:** Trocar a senha do PostgreSQL no servidor e atualizar o `.env` de produção. Os scripts de migration acima são legados; os scripts ativos (sync, validar) já usam variáveis de ambiente.

---

## 3. IPs no código

| Local | IP | Risco |
|-------|-----|-------|
| Docs (planning, deploy) | 148.230.78.91 | Baixo – IP público do servidor |
| `.cursorrules`, `.github/copilot-instructions.md` | 148.230.78.91 | Baixo – referência de infra |
| Scripts de diagnostic | 148.230.78.91 | Baixo – usado em comentários de exemplo |

O IP é público e associado ao domínio. O risco principal era a senha no mesmo contexto; com a remoção da senha dos scripts, o uso do IP em docs é aceitável.

---

## 4. Dados em trânsito (front ↔ back)

| Verificação | Status |
|-------------|--------|
| Login (email/senha) | POST JSON via HTTPS em produção |
| JWT em cookie | HttpOnly, Secure, SameSite=Strict |
| API calls | `credentials: "include"` – cookie enviado automaticamente |
| `NEXT_PUBLIC_BACKEND_URL` | `https://meufinup.com.br` em prod (embutido no build) |
| Nenhum token/senha em URL ou query params | OK |

**Conclusão:** O tráfego entre front e back está adequado para produção.

---

## 5. Arquivos versionados – verificação

| Item | Status |
|------|--------|
| `.env` | No `.gitignore` – OK |
| `financas_dev.db` | `.gitignore` tem `!app_dev/backend/database/financas_dev.db` – **revisar** se o banco deve ser versionado |
| `*.db.backup*` | 8 backups em `app_dev/backend/database/` **versionados** – podem conter dados sensíveis |
| `app_dev/backend/.env.example` | Versionado – OK (sem senhas reais) |

**Recomendação:** 
- Os `.db.backup_*` já estão no `.gitignore` mas foram commitados antes da regra. Para parar de versioná-los: `git rm --cached app_dev/backend/database/*.backup*`
- Se `financas_dev.db` for versionado intencionalmente (via `!app_dev/backend/database/financas_dev.db`), garantir que não contenha dados sensíveis de produção.

---

## 6. Checklist de ações recomendadas

- [x] Remover senha hardcoded dos scripts ativos (sync, validar)
- [x] Atualizar `.env.example` sem senha real
- [x] **Trocar senha do PostgreSQL** no servidor (feito 16/02/2026)
- [x] Atualizar `app_dev/backend/.env` no servidor com a nova senha
- [x] Remover `*.db.backup*` do versionamento (git rm --cached)
- [ ] Revisar necessidade de versionar `financas_dev.db`

---

## 7. Rotação de senha PostgreSQL (servidor)

```bash
# 1. Gerar nova senha
NEW_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
echo "Nova senha: $NEW_PASS"

# 2. No servidor
ssh minha-vps-hostinger
sudo -u postgres psql -c "ALTER USER finup_user WITH PASSWORD '$NEW_PASS';"

# 3. Atualizar .env do backend
cd /var/www/finup/app_dev/backend
# Editar .env: DATABASE_URL=postgresql://finup_user:NOVA_SENHA@localhost:5432/finup_db
sudo systemctl restart finup-backend
```
