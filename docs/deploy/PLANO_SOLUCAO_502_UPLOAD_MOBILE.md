# Plano de Solução — Erros 502 na Página Mobile Upload

**Data:** 09/03/2026  
**Contexto:** Página `meufinup.com.br/mobile/upload` retornando 502 Bad Gateway em todas as chamadas de API.  
**Impacto:** Usuário não consegue carregar bancos, cartões, detectar arquivo ou fazer upload.

---

## 1. Diagnóstico dos Erros

### 1.1 Erros Observados (Console Chrome DevTools)

| Endpoint | Método | Erro | Mensagem no Frontend |
|----------|--------|------|----------------------|
| `/api/v1/upload/detect` | POST | 502 Bad Gateway | "Erro ao detectar arquivo" |
| `/api/v1/compatibility/` | GET | 502 Bad Gateway | "Erro ao buscar instituições financeiras" |
| `/api/v1/cards/` | GET | 502 Bad Gateway | "Erro ao buscar cartões de crédito" |
| `/api/v1/upload/preview` | POST | 502 Bad Gateway | "Erro ao fazer upload do arquivo" |

### 1.2 Interpretação

**502 Bad Gateway** significa que o **proxy (Nginx)** recebeu a requisição do cliente, encaminhou para o **backend (FastAPI)**, mas **não obteve resposta válida**. Possíveis causas:

1. **Backend não está rodando** — container `finup_backend_prod` parado ou crashado
2. **Backend não responde** — travado, timeout ou sobrecarga
3. **Problema de rede** — Nginx não consegue alcançar o backend na rede Docker
4. **Backend falha ao iniciar** — erro de conexão com PostgreSQL, variáveis de ambiente, migrations
5. **Backend retorna erro 5xx** — exceção não tratada que o Nginx interpreta como 502

---

## 2. Fluxo da Infraestrutura (Produção)

```
Cliente (navegador)
    ↓ HTTPS
Nginx (infra_nginx) — meufinup.com.br
    ↓ /api/* → proxy_pass
Backend (finup_backend_prod) — porta 8000
    ↓
PostgreSQL (finup_postgres_prod) + Redis (finup_redis_prod)
```

**Rede:** `finup_finup-net` (Docker network externa)

---

## 3. Plano de Solução (Ordem de Execução)

### Fase 1 — Diagnóstico Rápido (5 min)

Execute na VM para identificar a causa raiz:

```bash
# 1. Conectar na VM
ssh minha-vps-hostinger

# 2. Verificar containers em execução
docker ps -a | grep -E "finup|infra"

# 3. Verificar saúde do backend
docker exec finup_backend_prod curl -sf http://localhost:8000/api/health

# 4. Logs recentes do backend (últimas 50 linhas)
docker logs finup_backend_prod --tail=50

# 5. Verificar Nginx
docker exec infra_nginx nginx -t
docker logs infra_nginx --tail=20
```

**Interpretação:**
- `docker ps` mostra `finup_backend_prod` como `Up`? Se `Exited` ou ausente → backend parou
- `curl /api/health` retorna JSON com `"status":"ok"`? Se falhar → backend não responde
- Logs do backend mostram `ConnectionRefused`, `OperationalError`, `ModuleNotFoundError`? → causa específica

---

### Fase 2 — Correções Imediatas (conforme diagnóstico)

#### Cenário A: Backend parado ou unhealthy

```bash
cd /var/www/finup
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d backend
# Aguardar 15–30s
docker exec finup_backend_prod curl -sf http://localhost:8000/api/health
```

#### Cenário B: PostgreSQL não conecta

```bash
# Verificar se Postgres está saudável
docker exec finup_postgres_prod pg_isready -U finup_user

# Verificar DATABASE_URL no .env.prod
grep DATABASE_URL /var/www/finup/.env.prod
# Deve ser: postgresql://finup_user:PASSWORD@finup_postgres_prod:5432/finup_db
# (host = nome do container, não localhost)
```

#### Cenário C: Migration pendente

```bash
docker exec finup_backend_prod alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.prod restart backend
```

#### Cenário D: Rede Docker — Nginx não alcança backend

```bash
# Verificar se Nginx está na mesma rede
docker network inspect finup_finup-net | grep -A2 infra_nginx
docker network inspect finup_finup-net | grep -A2 finup_backend

# Se Nginx estiver em outro compose, garantir que use a rede finup_finup-net
```

#### Cenário E: Reinício completo (último recurso)

```bash
cd /var/www/finup
docker compose -f docker-compose.prod.yml --env-file .env.prod down
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
# Aguardar 1 minuto
./deploy/scripts/validate_deploy.sh  # se existir versão Docker
```

---

### Fase 3 — Validação Pós-Correção

```bash
# Health check público
curl -sf https://meufinup.com.br/api/health

# Teste com autenticação (substituir TOKEN por JWT válido)
curl -s -H "Authorization: Bearer TOKEN" https://meufinup.com.br/api/v1/compatibility/
curl -s -H "Authorization: Bearer TOKEN" https://meufinup.com.br/api/v1/cards/
```

**No navegador:**
1. Fazer login em meufinup.com.br
2. Acessar `/mobile/upload`
3. Verificar se dropdowns "Instituição Financeira" e "Cartão de Crédito" carregam
4. Selecionar arquivo e clicar em "Importar Arquivo"

---

### Fase 4 — Melhorias Preventivas (opcional)

| Ação | Objetivo |
|------|----------|
| **Health check no predeploy** | Garantir que `/api/health` responde antes de considerar deploy OK |
| **Alertas de monitoramento** | Notificar quando backend ficar unhealthy (ex: UptimeRobot, healthchecks.io) |
| **Logs centralizados** | Facilitar debug em produção (ex: Loki, CloudWatch) |
| **Timeout Nginx** | Aumentar `proxy_read_timeout` se uploads grandes estiverem causando 502 |
| **Confirm upload 502** | Fases 5/6/7 (base_parcelas, budget, padrões) movidas para background — resposta imediata ao usuário |

---

## 4. Checklist de Execução

- [ ] **1.1** Executar comandos da Fase 1 (diagnóstico)
- [ ] **1.2** Registrar resultado: backend Up? Health OK? Erro nos logs?
- [ ] **2.1** Aplicar correção do cenário identificado (A, B, C, D ou E)
- [ ] **2.2** Aguardar backend ficar healthy
- [ ] **3.1** Testar `curl https://meufinup.com.br/api/health`
- [ ] **3.2** Testar página mobile upload no navegador
- [ ] **3.3** Confirmar que dropdowns e upload funcionam

---

## 5. Referências

- **Troubleshooting 502:** `deploy/docs/TROUBLESHOOTING.md` (seção "Site retorna 502/504")
- **Deploy:** `deploy/README.md`, `scripts/deploy/deploy_docker_build_local.sh`
- **Endpoints Upload:** `app_dev/backend/app/domains/upload/router.py`
- **Frontend Upload API:** `app_dev/frontend/src/features/upload/services/upload-api.ts`

---

*Documento gerado para resolução dos erros 502 na página mobile upload.*
