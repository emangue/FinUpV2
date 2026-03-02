# Base Template de Grupos e Subgrupos

**Data:** 28/02/2026  
**Objetivo:** Definir a base canônica que é copiada para novos usuários — raramente alterada, editável no admin.

---

## 1. Conceito

- **Template** = base de grupos e subgrupos iniciais
- **Fonte:** `generic_classification_rules` (86 regras, 11+ grupos únicos) + complementos padrão
- **Uso:** Ao criar novo usuário → copiar template → `base_grupos_config` e `base_marcacoes` do usuário
- **Admin:** Pode editar o template (raramente) — tela em `/admin/grupos-base` ou similar
- **Não** usar user_id=1 como fonte — usar tabelas template explícitas

---

## 2. Tabelas template (globais, sem user_id)

### 2.1. base_grupos_template

```sql
CREATE TABLE base_grupos_template (
    id INTEGER PRIMARY KEY,
    nome_grupo VARCHAR(100) NOT NULL UNIQUE,
    tipo_gasto_padrao VARCHAR(50) NOT NULL,
    categoria_geral VARCHAR(50) NOT NULL,
    cor VARCHAR(7)
);
```

**População inicial:** 
- Extrair grupos únicos de `generic_classification_rules` (grupo → tipo_gasto do primeiro registro)
- Mapear categoria_geral: Investimentos→Investimento, demais→Despesa; adicionar Salário (Receita), Transferência Entre Contas (Transferência), Outros (Despesa)
- Ou: migrar dados atuais de `base_grupos_config` (antes de adicionar user_id)

### 2.2. base_marcacoes_template

```sql
CREATE TABLE base_marcacoes_template (
    id INTEGER PRIMARY KEY,
    GRUPO VARCHAR(100) NOT NULL,
    SUBGRUPO VARCHAR(100) NOT NULL,
    UNIQUE(GRUPO, SUBGRUPO)
);
```

**População inicial:**
- Extrair de `generic_classification_rules`: `SELECT DISTINCT grupo, subgrupo`
- Complementar com subgrupos padrão para grupos que não têm nas regras (ex.: Salário→Salário Mensal, Outros→Diversos)

---

## 3. Fluxo

```
┌─────────────────────────────────────────────────────────────────┐
│  BASE TEMPLATE (global, raramente alterada)                     │
│  base_grupos_template + base_marcacoes_template                 │
│  Fonte: generic_classification_rules + seed padrão             │
│  Admin: /admin/grupos-base (editar quando necessário)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ COPY (ao criar novo usuário)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DADOS DO USUÁRIO (por user_id)                                 │
│  base_grupos_config (user_id) + base_marcacoes (user_id)       │
│  Usuário pode adicionar grupos/subgrupos customizados           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Vantagens

1. **Fonte explícita** — não depende de user_id=1
2. **Raramente alterada** — template é estável
3. **Admin pode ajustar** — quando precisar de novo grupo padrão
4. **Reutiliza generic_classification_rules** — mesma fonte de verdade para classificação e para template
5. **Novo usuário** — sempre recebe cópia consistente do template

---

## 5. Integração com o plano

- **Migration:** Criar `base_grupos_template` e `base_marcacoes_template`
- **Seed:** Popular a partir de `generic_classification_rules` + complementos
- **A.04** `_inicializar_grupos_usuario`: copiar do **template**, não do user_id=1
- **Admin (futuro):** Tela para editar template (pode ser fase posterior)
