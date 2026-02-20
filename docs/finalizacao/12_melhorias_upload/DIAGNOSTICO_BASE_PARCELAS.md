# Diagnóstico: Base Parcelas não marca no upload

**Data:** 15/02/2026  
**Contexto:** Upload de fatura-202601.csv – transações como "PRODUTOS GLOBO 07/12" não aparecem marcadas como "Base Parcelas"

---

## ⚠️ Mesmo arquivo, resultados diferentes (Local vs Produção)

| Ambiente | Base Parcelas | Causa |
|----------|---------------|-------|
| **Local** (localhost:3000) | 15 | `base_parcelas` populada por uploads confirmados |
| **Produção** (meufinup.com.br) | 0 | `base_parcelas` vazia ou `user_id` diferente |

**Conclusão:** A tabela `base_parcelas` é **por ambiente**. Local usa SQLite, produção usa PostgreSQL – são bancos diferentes.

---

## Resumo

O fluxo de classificação está correto. A causa mais provável é que **a base de parcelas em produção está vazia** ou **o usuário logado é diferente** do que tem parcelas cadastradas.

---

## Como funciona

1. **Fase 2 (Marker):** Extrai parcela do lançamento (ex: "PRODUTOS GLOBO 07/12" → base="PRODUTOS GLOBO", 7/12) e gera `IdParcela` com hash: `estabelecimento_normalizado|valor|total_parcelas|user_id`

2. **Fase 3 (Classifier):** Se `id_parcela` existe, busca em `base_parcelas` por `id_parcela` + `user_id`. Se encontrar → `origem_classificacao = 'Base Parcelas'`

3. **Fase 5 (após confirmar):** Popula `base_parcelas` com as parcelas do upload confirmado

---

## Causas prováveis

| Causa | Explicação |
|-------|------------|
| **a) Base vazia em produção** | `base_parcelas` só é preenchida **depois** de confirmar um upload. No primeiro upload, não há parcelas para dar match. |
| **b) user_id diferente** | O hash do `IdParcela` inclui `user_id`. Se o usuário logado for outro, o match não ocorre. |
| **c) Banco de produção** | meufinup.com.br usa PostgreSQL em produção. O banco local (SQLite) pode ter dados que produção não tem. |
| **d) Formato Excel** | Não existe processador para fatura em Excel. Use **CSV** ou **PDF**. |

---

## Validação local

No banco local, o fluxo está correto:

```
PRODUTOS GLOBO 07/12 (R$ 59,90)
→ IdParcela = cc1cc5e31675c2f7 (user_id=4) ou 9f7903660f32706a (user_id=1)
→ EXISTE em base_parcelas ✓
```

---

## O que fazer

### 1. Confirmar o primeiro upload

Se for o primeiro upload com essa fatura:

1. Faça o upload e confira o preview
2. **Confirme** o upload (botão Confirmar)
3. A Fase 5 vai popular `base_parcelas`
4. No próximo upload com a mesma parcela (ex: 08/12), ela deve aparecer como "Base Parcelas"

### 2. Conferir usuário logado

- Em produção, qual usuário está logado?
- As parcelas em `base_parcelas` estão associadas a esse `user_id`?

### 3. Conferir base em produção

No servidor de produção:

```sql
-- Quantas parcelas existem para o seu user_id?
SELECT COUNT(*) FROM base_parcelas WHERE user_id = :seu_user_id;

-- Exemplo PRODUTOS GLOBO
SELECT * FROM base_parcelas 
WHERE estabelecimento_base LIKE '%GLOBO%' 
  AND user_id = :seu_user_id;
```

### 4. Usar CSV (não Excel)

Para fatura Itaú, use **CSV** ou **PDF**. Fatura em Excel ainda não tem processador.

---

## Scripts de validação e correção

### 1. Validar base_parcelas no ambiente atual

```bash
cd app_dev && source venv/bin/activate && cd backend
python ../../scripts/diagnostic/validar_base_parcelas_local_vs_producao.py
```

Mostra quantas parcelas existem por `user_id`. Se vazio → Base Parcelas (0) no preview.

### 2. Exportar base_parcelas local para produção

Quando local tem dados e produção não:

```bash
cd app_dev/backend
python3 ../../scripts/diagnostic/exportar_base_parcelas_para_producao.py
# Gera: temp/export_base_parcelas_producao.sql
```

No servidor de produção:

```bash
scp temp/export_base_parcelas_producao.sql user@servidor:/tmp/
ssh user@servidor 'cd /var/www/finup && source .env 2>/dev/null; psql $DATABASE_URL -f /tmp/export_base_parcelas_producao.sql'
```

### 3. Diagnóstico detalhado (PRODUTOS GLOBO)

```bash
cd app_dev/backend
python3 ../../scripts/diagnostic/diagnosticar_base_parcelas_upload.py
```

---

## Referências

- `app_dev/backend/app/domains/upload/processors/marker.py` – extração de parcela e geração de IdParcela
- `app_dev/backend/app/domains/upload/processors/classifier.py` – `_classify_nivel1_parcelas`
- `app_dev/backend/app/domains/upload/service.py` – Fase 5: `_fase5_update_base_parcelas`
