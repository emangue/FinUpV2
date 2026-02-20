# Validação: Hashes sempre incluem user_id

**Data:** 15/02/2026  
**Objetivo:** Garantir que IdTransacao e IdParcela nunca colidam entre usuários

---

## Fórmulas (OBRIGATÓRIO manter user_id)

### IdTransacao
```
chave = f"{user_id}|{data}|{estabelecimento}|{valor}"
hash = FNV-1a 64-bit(chave)
```
**Arquivo:** `app/shared/utils/hasher.py` → `generate_id_transacao()`

### IdParcela
```
chave = f"{estabelecimento_normalizado}|{valor:.2f}|{total_parcelas}|{user_id}"
hash = MD5(chave)[:16]
```
**Arquivo:** `app/domains/upload/processors/marker.py` (linha ~317)

---

## Validação

**Testes:** `app_dev/backend/tests/test_hash_user_id.py`

```bash
cd app_dev/backend && python3 -m pytest tests/test_hash_user_id.py -v
```

**Assertion no marker:** `assert self.user_id is not None` antes de gerar IdParcela

---

## Servidor (VM)

1. **Backend reiniciado** após correção da base_parcelas
2. **Dados corrigidos** com `scripts/database/fix_id_parcela_vm.py`
3. **Código atualizado** via `git pull` (já tinha user_id no hash)
