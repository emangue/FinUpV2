# 🔐 Credenciais de Acesso - Atualizado

**Data:** 01/02/2026 17:39  
**Status:** ✅ FUNCIONANDO

---

## 🔑 Credenciais Admin

### **Email:**
```
admin@financas.com
```

### **Senha:**
```
cahriZqonby8
```

### **Detalhes:**
- **User ID:** 1
- **Nome:** Emanuel Guerra
- **Role:** admin
- **Status:** Ativo ✅

---

## 🌐 URLs de Acesso

### **Frontend (Login):**
```
http://localhost:3001/login
```

### **API (Backend):**
```
http://localhost:8000/api/v1/auth/login
```

### **Swagger Docs:**
```
http://localhost:8000/docs
```

---

## 🧪 Teste via cURL

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@financas.com","password":"cahriZqonby8"}'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@financas.com",
    "nome": "Emanuel Guerra",
    "role": "admin"
  }
}
```

---

## 📊 Outros Usuários Disponíveis

1. **anabeatriz@financas.com** (ID: 2, Ativo: Sim)
2. **admin@email.com** (ID: 3, Ativo: Não - inativo)
3. **teste@email.com** (ID: 4, Ativo: Sim)

**Nota:** Senhas desses usuários não foram resetadas.

---

## 🔧 Como Resetar Senha Novamente

Se precisar resetar a senha do admin no futuro:

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend
../venv/bin/python update_admin_password.py
```

O script gera uma nova senha aleatória automaticamente.

---

## 🐛 Problemas Resolvidos

### 1. **CORS Error (Failed to fetch)**
**Causa:** Backend só aceitava requisições de `localhost:3000`, mas frontend estava em `3001`.

**Solução:** Adicionado portas 3000-3002 no CORS do backend (`.env`).

### 2. **Senha Incorreta**
**Causa:** Hash bcrypt antigo ou corrompido no banco.

**Solução:** Executado `update_admin_password.py` para gerar novo hash.

---

## ✅ Checklist de Validação

- [x] Backend rodando em `:8000`
- [x] Frontend rodando em `:3001`
- [x] CORS configurado para porta 3001
- [x] Usuário admin existe no banco
- [x] Senha resetada e testada via cURL
- [x] Login retorna access_token válido

---

**Última atualização:** 01/02/2026 17:40  
**Autor:** Assistant (Sprint 0 troubleshooting)
