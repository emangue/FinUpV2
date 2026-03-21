# Checklist Deploy - 16 Fev 2026

## Commit criado

```
feat: Dashboard mobile, Plano Aposentadoria, Orçamento, Extrato Cartão e melhorias
54 files changed, 5408 insertions(+), 152 deletions(-)
```

---

## Passos para deploy

### 1. Push para o repositório remoto

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
git push origin main
```

### 2. (Opcional) Migração de grupos - dry-run local

Se quiser validar a migração antes do deploy:

```bash
cd app_dev/backend
PROD_DATABASE_URL=postgresql://... python ../../scripts/migration/migrate_grupos_producao.py --dry-run
```

### 3. Executar deploy no servidor

```bash
./scripts/deploy/deploy_app_dev.sh
```

O script irá:
- Verificar que não há mudanças pendentes
- Verificar que local = origin/main
- Conectar via SSH na VPS
- `git pull origin main`
- `npm ci` e `npm run build` no frontend
- **Migração grupos** (Aplicações→Investimentos, Fatura→Transferência)
- Reiniciar `finup-backend` e `finup-frontend`
- Health check em `http://localhost:8000/api/health`

### 4. Validar após deploy

- [ ] https://meufinup.com.br
- [ ] https://meufinup.com.br/mobile/dashboard
- [ ] Aba **Plano** no dashboard
- [ ] Card "Construa Seu Plano" com curva e patrimônio
- [ ] Link "Criar Meu Plano" → /mobile/personalizar-plano
- [ ] Aba **Orçamento** funcionando
- [ ] Extrato do cartão (/mobile/extrato-cartao)

---

## Rollback (se necessário)

```bash
# No servidor (SSH)
cd /var/www/finup
git log -1  # ver hash anterior
git checkout <hash-anterior>
cd app_dev/frontend && npm run build
systemctl restart finup-backend finup-frontend
```

---

## Arquivos não commitados (intencional)

- `.cursorrules 2` (duplicata)
- `dashboard copy/` (backup)
- `temp/*` (dados temporários)
- `scripts/fix_cors_env.sh` (específico de ambiente)
