# Diagnóstico: Base Parcelas (0) no preview

**Data:** 15/02/2026  
**Problema:** Upload de fatura-202601.csv mostra 0 em "Base Parcelas" no preview

---

## ✅ Marker vs base_parcelas - VERIFICADO

O IdParcela gerado pelo marker é **igual** ao id_parcela na base:

```
Marker (user 1): IdParcela=9f7903660f32706a para PRODUTOS GLOBO
base_parcelas:   id_parcela=9f7903660f32706a | R$59.9 | 12x  ← IGUAL
```

**Comando para revalidar no servidor:**
```bash
ssh minha-vps-hostinger 'cd /var/www/finup && source app_dev/backend/venv/bin/activate && python3 scripts/diagnostic/test_upload_pipeline_server.py'
```

---

## Resultado do teste no servidor

O pipeline foi testado **diretamente no servidor** e **funciona corretamente**:

```
Fase 1: 3 transações brutas ✅
Fase 2: IdParcela gerado (9f7903660f32706a para PRODUTOS GLOBO, user 1) ✅
Fase 3: 3/3 classificadas como Base Parcelas ✅
```

---

## Causa provável: user_id

| user_id | email                 | base_parcelas |
|---------|-----------------------|---------------|
| 1       | admin@financas.com    | 101           |
| 2       | anabeatriz@financas.com | **0**       |
| 3       | admin@email.com       | **0**         |
| 4       | teste@email.com       | 101           |

**Se você está logado como user 2 ou 3**, não há parcelas na base → 0 em "Base Parcelas".

**Cartão Azul** existe para:
- user 1 (admin@financas.com)
- user 4 (teste@email.com)

---

## O que fazer

### 1. Confirmar qual conta está usando
- **admin@financas.com** ou **teste@email.com** → tem parcelas ✅
- **anabeatriz@financas.com** ou **admin@email.com** → sem parcelas ❌

### 2. Se for user 2 ou 3
Opções:
- Fazer login com **admin@financas.com** ou **teste@email.com**
- Ou popular base_parcelas para o seu user (copiar de user 1 ou 4)

### 3. Popular base_parcelas para outro user
```bash
# Na VM, executar script de cópia (ajustar user destino)
python3 scripts/database/copiar_parcelas_padroes_user4.py  # ou criar para user 2/3
```

---

## Se backend OK mas preview ainda mostra 0

O marker e a classificação estão corretos. Se a interface continua com 0, verificar:

1. **Console do navegador** (F12 → Console): os logs `🔍 DEBUG - Dados recebidos do backend` mostram `origem_classificacao` nas transações?
2. **Rede** (F12 → Network): na resposta do GET `/api/v1/upload/preview/{sessionId}`, o campo `origem_classificacao` vem como `"Base Parcelas"`?
3. **Sessão correta**: o redirect após o upload leva para o mesmo `sessionId` que foi criado no POST?

---

## Scripts de teste

```bash
# Testar pipeline no servidor (marker + classifier)
ssh minha-vps-hostinger 'cd /var/www/finup && source app_dev/backend/venv/bin/activate && python3 scripts/diagnostic/test_upload_pipeline_server.py'
```
