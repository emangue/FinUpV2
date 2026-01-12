# 🔒 HTTPS E SSL - CONFIGURAÇÃO PARA PRODUÇÃO

**Data:** 12 de Janeiro de 2026  
**⚠️ MEGA IMPORTANTE:** Sistema em produção DEVE rodar em HTTPS!

---

## 🎯 POR QUE HTTPS É OBRIGATÓRIO?

### 1. **Cookies httpOnly + Secure Flag**
```javascript
// Cookies marcados com secure=True SÓ funcionam em HTTPS
Set-Cookie: access_token=xxx; HttpOnly; Secure; SameSite=Lax
```
- Se usar HTTP em produção → **Cookies não são enviados** → Login quebra

### 2. **Segurança de Dados**
- JWT tokens trafegam pelo cookie
- Senhas enviadas no /auth/login
- Dados financeiros sensíveis
- **HTTP = Texto plano** → qualquer um na rede pode ler

### 3. **CORS com Credentials**
```python
# CORS permite cookies APENAS se origem for HTTPS
allow_credentials=True  # Requer HTTPS em produção
```

### 4. **Conformidade e SEO**
- Google penaliza sites HTTP
- Navegadores mostram "Não seguro"
- Regulamentações (LGPD) exigem criptografia

---

## 📋 CHECKLIST DE CONFIGURAÇÃO HTTPS

### ✅ **ANTES DO DEPLOY:**

- [ ] **1. Domínio configurado**
  - DNS apontando para IP da VM
  - Exemplo: `financas.seudomain.com.br` → `203.0.113.45`

- [ ] **2. Backend .env atualizado**
  ```bash
  # ⚠️ HTTPS obrigatório!
  BACKEND_CORS_ORIGINS=https://financas.seudomain.com.br
  ENVIRONMENT=production
  ```

- [ ] **3. Frontend atualizado**
  ```typescript
  // api.config.ts
  BACKEND_URL: 'https://financas.seudomain.com.br'
  ```

- [ ] **4. Nginx instalado na VM**
  ```bash
  sudo apt update
  sudo apt install nginx certbot python3-certbot-nginx
  ```

### ✅ **DURANTE O DEPLOY:**

- [ ] **5. Certbot configurado (Let's Encrypt)**
  ```bash
  sudo certbot --nginx -d financas.seudomain.com.br
  ```

- [ ] **6. Nginx configurado como proxy reverso**
  ```nginx
  server {
      listen 443 ssl http2;
      server_name financas.seudomain.com.br;
      
      ssl_certificate /etc/letsencrypt/live/financas.seudomain.com.br/fullchain.pem;
      ssl_certificate_key /etc/letsencrypt/live/financas.seudomain.com.br/privkey.pem;
      
      location /api/ {
          proxy_pass http://localhost:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }
      
      location / {
          proxy_pass http://localhost:3000;  # Next.js
      }
  }
  ```

- [ ] **7. Renovação automática SSL configurada**
  ```bash
  # Cron para renovar a cada 60 dias
  0 0 1 */2 * certbot renew --quiet
  ```

### ✅ **APÓS O DEPLOY:**

- [ ] **8. Testar HTTPS**
  ```bash
  curl https://financas.seudomain.com.br/api/health
  ```

- [ ] **9. Verificar cookies secure**
  - Abrir DevTools → Application → Cookies
  - Verificar flags: `HttpOnly`, `Secure`, `SameSite`

- [ ] **10. Testar login completo**
  - Login via HTTPS
  - Verificar que cookies são salvos
  - Navegar entre páginas autenticadas

---

## 🚨 ERROS COMUNS E SOLUÇÕES

### **Erro 1: "Cookies não estão sendo salvos"**
```
Problema: Backend em HTTP mas secure=True
Solução: Mudar ENVIRONMENT=production E rodar em HTTPS
```

### **Erro 2: "CORS error: credentials not supported"**
```
Problema: BACKEND_CORS_ORIGINS está HTTP, mas acesso é HTTPS
Solução: Atualizar .env com https://...
```

### **Erro 3: "SSL certificate error"**
```
Problema: Certificado Let's Encrypt expirado
Solução: sudo certbot renew --force-renewal
```

### **Erro 4: "Mixed content blocked"**
```
Problema: Frontend HTTPS chamando backend HTTP
Solução: Backend TAMBÉM precisa estar em HTTPS via nginx
```

---

## 🔧 CONFIGURAÇÃO DETALHADA - NGINX

### **Arquivo:** `/etc/nginx/sites-available/financas`

```nginx
# Redireciona HTTP → HTTPS (obrigatório)
server {
    listen 80;
    server_name financas.seudomain.com.br;
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS principal
server {
    listen 443 ssl http2;
    server_name financas.seudomain.com.br;
    
    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/financas.seudomain.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/financas.seudomain.com.br/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/financas.seudomain.com.br/chain.pem;
    
    # SSL Settings (segurança)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (força HTTPS por 1 ano)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate Limiting Global (proteção DDoS)
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req zone=general burst=20 nodelay;
    
    # Backend API (FastAPI)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Logs
    access_log /var/log/nginx/financas-access.log;
    error_log /var/log/nginx/financas-error.log;
}
```

**Ativar configuração:**
```bash
sudo ln -s /etc/nginx/sites-available/financas /etc/nginx/sites-enabled/
sudo nginx -t  # Testar configuração
sudo systemctl restart nginx
```

---

## 🔑 OBTENDO CERTIFICADO SSL (Let's Encrypt)

### **Passo a Passo:**

```bash
# 1. Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 2. Obter certificado (automático com nginx)
sudo certbot --nginx -d financas.seudomain.com.br --email seu@email.com --agree-tos --no-eff-email

# 3. Testar renovação automática
sudo certbot renew --dry-run

# 4. Configurar cron para renovação (já vem configurado automaticamente)
# Certificados Let's Encrypt expiram em 90 dias
# Certbot renova automaticamente a cada 60 dias
```

### **Verificar Status:**
```bash
sudo certbot certificates
```

---

## 📊 VALIDAÇÃO PÓS-DEPLOY

### **1. SSL Labs Test**
- Acessar: https://www.ssllabs.com/ssltest/
- Analisar: `financas.seudomain.com.br`
- Meta: Grade **A** ou **A+**

### **2. Testar Cookies**
```bash
# Fazer login e verificar cookies
curl -v -X POST https://financas.seudomain.com.br/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@email.com","password":"admin123"}' \
  -c cookies.txt

# Verificar se cookies têm flag Secure
cat cookies.txt
```

### **3. Testar Endpoint Autenticado**
```bash
# Usar cookie do login
curl -v https://financas.seudomain.com.br/api/v1/auth/me -b cookies.txt
```

---

## 💰 CUSTO DO SSL

- **Let's Encrypt:** **GRATUITO** 🎉
- Renovação automática
- Válido por 90 dias, renovado a cada 60 dias
- Suporta wildcard (*.seudomain.com.br)

---

## 🆘 SUPORTE E TROUBLESHOOTING

### **Logs para verificar:**
```bash
# Nginx
sudo tail -f /var/log/nginx/financas-error.log

# Backend
sudo journalctl -u financas -f

# Certbot
sudo journalctl -u certbot -f
```

### **Renovação manual (se automática falhar):**
```bash
sudo certbot renew --force-renewal
sudo systemctl restart nginx
```

---

## ✅ RESUMO - CONFIGURAÇÃO FINAL

**Desenvolvimento (localhost):**
- HTTP: http://localhost:3000
- Cookies: secure=False
- CORS: http://localhost:3000

**Produção (VM):**
- HTTPS: https://financas.seudomain.com.br
- Cookies: secure=True (⚠️ obrigatório)
- CORS: https://financas.seudomain.com.br
- Nginx: proxy reverso com SSL
- Certificado: Let's Encrypt (gratuito)

---

**⚠️ LEMBRE-SE:** Sem HTTPS em produção, autenticação JWT com cookies NÃO funciona!
