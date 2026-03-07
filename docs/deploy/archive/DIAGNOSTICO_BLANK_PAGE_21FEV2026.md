# Diagnóstico: Página em branco meufinup.com.br

**Data:** 21/02/2026  
**Sintoma:** meufinup.com.br/mobile/dashboard abre página branca.

---

## Causa raiz

**Porta 3000 está sendo usada pelo Easypanel** (painel de gerenciamento), não pelo FinUp.

| Porta | Serviço | Esperado para meufinup.com.br |
|-------|---------|------------------------------|
| 3000 | **Easypanel** (Docker) | **FinUp app_dev frontend** |
| 3001 | Ateliê frontend | - |
| 3002 | FinUp app_admin | admin.meufinup.com.br |
| 8000 | FinUp backend | /api/ |

O nginx está configurado para enviar `meufinup.com.br` → `127.0.0.1:3000`. Como a porta 3000 está com o Easypanel, o site recebe a interface do Easypanel em vez do app FinUp.

O **FinUp app_dev frontend não está rodando** em nenhuma porta.

---

## Solução

### Opção A: Mudar Easypanel para outra porta (recomendado)

1. No Easypanel ou no `docker-compose`, alterar o mapeamento de portas do Easypanel de `3000:3000` para `3004:3000` (ou outra porta livre).
2. Acessar Easypanel em `https://seu-servidor:3004` (ou o domínio que usar).
3. Iniciar o FinUp app_dev frontend na porta 3000:
   ```bash
   cd /var/www/finup/app_dev/frontend && npm run start
   # Ou via systemd/supervisor, se configurado
   ```

### Opção B: Mudar FinUp para outra porta

1. Iniciar o FinUp frontend na porta 3003:
   ```bash
   cd /var/www/finup/app_dev/frontend && npm run start -- -p 3003
   ```
2. Atualizar o nginx para usar 3003:
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:3003;
       # ... resto igual
   }
   ```
3. Recarregar o nginx: `sudo nginx -t && sudo systemctl reload nginx`

---

## Como iniciar o FinUp frontend manualmente

```bash
ssh minha-vps-hostinger
cd /var/www/finup/app_dev/frontend
sudo -u deploy npm run start
# Ou em background: nohup sudo -u deploy npm run start &
```

Se a porta 3000 estiver livre, o app sobe nela. Caso contrário, usar `-p 3003` e ajustar o nginx.

---

## Resumo

1. **Build concluído** – o código da branch está em `/var/www/finup/app_dev/frontend/.next`.
2. **Conflito de porta** – Easypanel está em 3000; o nginx espera o FinUp nessa porta.
3. **Frontend parado** – o processo do FinUp app_dev não estava em execução.

---

## Solução aplicada (21/02/2026)

- **Nginx:** `proxy_pass` alterado de `127.0.0.1:3000` para `127.0.0.1:3003`
- **FinUp frontend:** iniciado na porta 3003 com `npm run start -- -p 3003`
- **Portas atuais:** 3000=Easypanel | 3001=Ateliê | 3002=app_admin | **3003=FinUp app_dev** | 8000=backend

### Reiniciar o frontend após reboot

O frontend está rodando com `nohup` e não sobrevive a reinicialização. Para subir novamente:

```bash
ssh minha-vps-hostinger
cd /var/www/finup/app_dev/frontend
sudo -u deploy nohup npm run start -- -p 3003 > /tmp/finup-frontend.log 2>&1 &
```

Ou configurar um serviço systemd/supervisor para iniciar automaticamente.
