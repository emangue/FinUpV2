# app_admin – Segurança e Configuração Hostinger

**Data:** 16/02/2026

---

## 1. Visão Geral de Segurança do app_admin

### 1.1 O que o app_admin usa (mesmo do BAU)

| Camada | Implementação | Fonte |
|--------|---------------|-------|
| **Autenticação** | JWT via cookie `auth_token` | Backend `auth/router.py` |
| **Cookie** | HttpOnly, Secure (prod), SameSite=Strict | Backend `auth/router.py` |
| **Rate limiting** | 5 tentativas/minuto no login | Backend `auth/router.py` |
| **Autorização** | `require_admin` em todos os endpoints admin | Backend `users/router.py` |
| **CORS** | Origens explícitas (não `*`) | Backend `config.py` |
| **API calls** | `credentials: "include"` (envia cookies) | `api-client.ts`, `AuthContext.tsx` |
| **Validação role** | Login só aceita `role === "admin"` | `login/page.tsx` |
| **Proteção de rotas** | `RequireAdmin` redireciona não-admin para /login | `RequireAdmin.tsx` |

### 1.2 Fluxo de segurança atual

```
1. Usuário acessa admin.meufinup.com.br
2. RequireAdmin verifica: user?.role === "admin"
3. Se não logado → redirect /login
4. Login: POST /api/v1/auth/login (email, password)
5. Backend valida, retorna JWT em cookie auth_token (HttpOnly)
6. Requisições subsequentes: credentials: "include" → cookie enviado
7. Endpoints /users/* exigem require_admin → 403 se não admin
```

### 1.3 Pontos fortes (herdados do BAU)

- JWT com secret forte (variável de ambiente)
- Cookie HttpOnly (proteção XSS)
- Cookie Secure em produção (apenas HTTPS)
- SameSite=Strict (proteção CSRF)
- Rate limiting no login (anti brute-force)
- CORS restrito (sem `*`)
- Backend valida role em todos os endpoints admin

### 1.4 Ideias de melhoria para o app_admin

| Melhoria | Prioridade | Descrição |
|----------|------------|-----------|
| **Cookie domain** | Alta | Se admin.meufinup.com.br e API em meufinup.com.br: cookie precisa `domain=.meufinup.com.br` para funcionar cross-subdomain. Verificar se já funciona ou ajustar no backend. |
| **2FA para admin** | Média | Autenticação em dois fatores para contas admin (TOTP, email) |
| **Audit log** | Média | Registrar ações admin (criar usuário, alterar senha, etc.) |
| **Session timeout** | Baixa | Reduzir tempo de sessão para admin (ex: 30 min vs 1h) |
| **IP allowlist** | Baixa | Restringir acesso admin a IPs conhecidos (opcional) |
| **Content-Security-Policy** | Baixa | Headers CSP no Next.js para mitigar XSS |
| **HSTS** | Baixa | Header Strict-Transport-Security (geralmente no Nginx) |

### 1.5 Checklist de segurança em produção

- [ ] CORS inclui `https://admin.meufinup.com.br`
- [ ] Cookie auth_token funciona cross-subdomain (domain correto)
- [ ] HTTPS ativo em admin.meufinup.com.br
- [ ] JWT_SECRET_KEY forte no backend
- [ ] Rate limiting ativo no login
- [ ] Nenhum log expondo tokens ou senhas

---

## 2. Hostinger – Criar subdomínio admin.meufinup.com.br

### 2.1 Cenário: VPS Hostinger (seu caso)

Você usa **VPS** (IP 148.230.78.91), não hospedagem compartilhada. O subdomínio é configurado via **DNS**, não pelo painel de subdomínios da hospedagem.

### 2.2 O que configurar

#### Opção A: DNS na Hostinger (hPanel)

1. Acesse **hPanel** da Hostinger
2. Vá em **Domínios** → **meufinup.com.br** → **DNS / Nameservers**
3. Adicione um **Registro A**:

| Campo | Valor |
|-------|-------|
| **Tipo** | A |
| **Nome** | admin |
| **Aponta para** | 148.230.78.91 |
| **TTL** | 14400 (ou padrão) |

Resultado: `admin.meufinup.com.br` → 148.230.78.91

#### Opção B: DNS em outro provedor (Cloudflare, etc.)

Se o domínio usa nameservers externos, adicione o mesmo registro A no painel DNS do provedor.

### 2.3 Resumo – O que colocar no Hostinger

| Onde | O quê |
|------|-------|
| **hPanel** → Domínios → meufinup.com.br → **DNS** | Novo registro: **Tipo A**, **Nome: admin**, **Valor: 148.230.78.91** |

### 2.4 Após o DNS

Guia completo: **`docs/deploy/DEPLOY_APP_ADMIN.md`**

1. **Propagação:** Pode levar até 24h (geralmente 15–60 min)
2. **Nginx:** Configurar `admin.meufinup.com.br` para proxy no app_admin (porta 3001)
3. **SSL:** Certbot para `admin.meufinup.com.br`
4. **CORS:** Adicionar `https://admin.meufinup.com.br` no backend (.env)
5. **systemd:** Serviço `finup-admin` rodando o Next.js

### 2.5 Verificar propagação DNS

```bash
# Após criar o registro, testar:
dig admin.meufinup.com.br +short
# Deve retornar: 148.230.78.91
```

---

## Referências

- Contrato API: `docs/planning/APP_ADMIN_CONTRATO_API.md`
- Deploy BAU: `docs/deploy/DEPLOY_MEUFINUP_ATUALIZACAO_2026.md`
- SSH: `docs/deploy/SSH_ACCESS.md`
- Hostinger subdomínios: https://support.hostinger.com/pt/articles/1583405-como-criar-e-excluir-subdominios
