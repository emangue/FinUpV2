# Deploy app_admin – admin.meufinup.com.br

**Data:** 16/02/2026  
**Pré-requisito:** DNS já configurado (admin → 148.230.78.91)

---

## Resumo dos passos

1. Build do app_admin localmente
2. Enviar para o servidor (git ou rsync)
3. Instalar deps e build no servidor
4. Criar serviço systemd `finup-admin`
5. Configurar Nginx para admin.meufinup.com.br
6. SSL com Certbot
7. CORS no backend
8. Variáveis de ambiente

---

## 1. Build local (opcional – ou build no servidor)

```bash
cd app_admin/frontend
npm install
npm run build
```

---

## 2. Enviar para o servidor

O app_admin está em `app_admin/` no repositório. Após `git pull` no servidor:

```bash
ssh minha-vps-hostinger
cd /var/www/finup
git pull origin main
```

---

## 3. No servidor – instalar e build

```bash
cd /var/www/finup/app_admin/frontend
npm install --production=false
npm run build
```

---

## 4. Criar serviço systemd finup-admin

```bash
sudo cat > /etc/systemd/system/finup-admin.service << 'EOF'
[Unit]
Description=FinUp Admin Frontend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/finup/app_admin/frontend
Environment="NODE_ENV=production"
Environment="PORT=3001"
Environment="NEXT_PUBLIC_BACKEND_URL=https://meufinup.com.br"
ExecStart=/usr/bin/npm start

PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable finup-admin
sudo systemctl start finup-admin
sudo systemctl status finup-admin
```

---

## 5. Nginx – adicionar server block para admin

Editar o arquivo de config do Nginx (ex: `/etc/nginx/sites-available/finup`):

```bash
sudo nano /etc/nginx/sites-available/finup
```

**Adicionar** este bloco (pode ser no mesmo arquivo, após o server do meufinup.com.br):

```nginx
# app_admin - admin.meufinup.com.br
server {
    listen 80;
    server_name admin.meufinup.com.br;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Testar e recarregar:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. SSL com Certbot

```bash
sudo certbot --nginx -d admin.meufinup.com.br --email seu-email@exemplo.com --agree-tos --no-eff-email
```

O Certbot vai ajustar o server block automaticamente para HTTPS.

---

## 7. CORS no backend

No servidor, editar o `.env` do backend:

```bash
cd /var/www/finup/app_dev/backend
nano .env
```

Adicionar ou atualizar `BACKEND_CORS_ORIGINS` para incluir o admin:

```bash
# Exemplo – manter os que já existem e adicionar admin
BACKEND_CORS_ORIGINS=https://meufinup.com.br,https://www.meufinup.com.br,https://admin.meufinup.com.br
```

Reiniciar o backend:

```bash
sudo systemctl restart finup-backend
```

---

## 8. Variáveis de ambiente do app_admin

O app_admin usa `NEXT_PUBLIC_BACKEND_URL` em build time. Se não definir, usa `http://localhost:8000`.

**Em produção:** definir antes do build:

```bash
export NEXT_PUBLIC_BACKEND_URL=https://meufinup.com.br
npm run build
```

Ou no systemd (já incluído no service acima):

```
Environment="NEXT_PUBLIC_BACKEND_URL=https://meufinup.com.br"
```

> ⚠️ Para Next.js, `NEXT_PUBLIC_*` é embutido no build. Se mudar depois, precisa rebuild.

---

## Checklist final

- [ ] `dig admin.meufinup.com.br +short` → 148.230.78.91
- [ ] `systemctl status finup-admin` → active
- [ ] `curl -s http://127.0.0.1:3001` → HTML
- [ ] `https://admin.meufinup.com.br` → carrega
- [ ] Login com admin@financas.com funciona
- [ ] CORS no backend inclui admin.meufinup.com.br

---

## Troubleshooting

**Admin não carrega:**
- `journalctl -u finup-admin -n 30`
- `curl -I http://127.0.0.1:3001`

**Login falha (CORS):**
- Verificar `BACKEND_CORS_ORIGINS` no .env do backend
- `systemctl restart finup-backend`

**Cookie não persiste:**
- Verificar se admin e API usam HTTPS
- Cookie é setado por meufinup.com.br; requests vêm de admin.meufinup.com.br – deve funcionar (mesmo domínio pai)
