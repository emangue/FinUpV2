# Ambiente de Desenvolvimento Local

> **Regra:** Sempre usar PostgreSQL via Docker. Alinha dev local com a VM/produção.

---

## Pré-requisitos

- **Docker Desktop** — para PostgreSQL
- **Node.js** — para o frontend
- **Python 3.9+** — para o backend (venv gerenciado pelo script)

---

## Iniciar o ambiente

```bash
# 1. Abrir Docker Desktop (se não estiver rodando)

# 2. Iniciar tudo (PostgreSQL + Backend + Frontend)
./scripts/deploy/quick_start.sh
```

O `quick_start.sh`:
- Verifica se PostgreSQL está rodando em `localhost:5432`
- Se não estiver, sobe via `docker compose up -d postgres`
- Inicia backend (porta 8000) e frontend (porta 3000)

---

## PostgreSQL — Sempre via Docker

| Comando | Descrição |
|---------|-----------|
| `docker compose up -d postgres` | Subir PostgreSQL |
| `docker ps \| grep postgres` | Verificar se está rodando |
| `docker compose stop postgres` | Parar PostgreSQL |

**Conexão:** `postgresql://finup_user:finup_password_dev_2026@localhost:5432/finup_db`

---

## URLs locais

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Parar o ambiente

```bash
./scripts/deploy/quick_stop.sh   # Para backend e frontend
docker compose stop postgres     # Para PostgreSQL (opcional)
```

---

## Troubleshooting

**"Connection refused" no login**
- PostgreSQL não está rodando. Execute: `docker compose up -d postgres`
- Verifique: `docker ps` deve listar `finup_postgres_dev`

**Docker daemon não está rodando**
- Abra o Docker Desktop e aguarde iniciar
- Depois: `docker compose up -d postgres`
