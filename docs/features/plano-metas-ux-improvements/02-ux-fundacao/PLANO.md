# PLANO — UX Fundação: Bugs + Navegação + Empty States

**Sub-projeto:** 02 | **Sprint:** 1 | **Estimativa:** ~10h

---

## Tasks

### Bugs críticos (~4h)

- [ ] **B1.01** Mapear todos os `router.back()` em `/mobile/` e substituir por destino explícito
- [ ] **B1.02** Garantir que `onClose` é passado como prop pelos pais de `EditTransactionModal`
- [ ] **B2.01** Diagnosticar replicação: `grep useTransactionStore` → identificar estado compartilhado
- [ ] **B2.02** Isolar estado de formulário dentro do modal (useState local por instância)
- [ ] **B3.01** Aplicar `overflow-y auto` + `dvh` + sticky header na tabela de transações
- [ ] **B4.01** Criar `src/lib/format.ts` com `formatBRL()`
- [ ] **B4.02** Substituir `toFixed(2)` e `toLocaleString()` por `formatBRL()` (grep para encontrar todos)

### Navegação (~2h)

- [ ] **S19.01** Criar/atualizar `BottomNav` com 5 itens + FAB Upload destacado
- [ ] **S19.02** Atualizar sidebar desktop com mesmos 5 destinos
- [ ] **S19.03** Garantir indicador de tela ativa (ícone preenchido + cor primária)

### Empty states (~4h)

- [ ] **S27.01** Criar componente `EmptyState` reutilizável em `src/components/`
- [ ] **S27.02** `/mobile/inicio` — empty state com CTA de upload
- [ ] **S27.03** `/mobile/transacoes` — empty state com CTA de upload
- [ ] **S27.04** `/mobile/plano` — empty state com CTA de criar plano
- [ ] **S27.05** `/mobile/carteira` — empty state com CTA de adicionar investimento
- [ ] **S27.06** Garantir que skeletons aparecem durante loading (empty state só quando dados chegam vazios)

---

## Validação pelo usuário

Após `./scripts/deploy/quick_start_docker.sh`:

1. **Bug B1:** Abrir um lançamento para editar em Transações → fechar → ainda está em Transações ✅
2. **Bug B2:** Editar lançamento A, depois editar lançamento B → A ainda tem seus valores originais ✅
3. **Bug B3:** Em mobile, rolar a lista de transações com o dedo → funciona sem travar ✅
4. **Bug B4:** Verificar qualquer valor na tela → aparece como `R$ 1.234,56` ✅
5. **S19:** Bottom nav tem 5 itens; Upload é o FAB destacado; tela ativa tem ícone preenchido ✅
6. **S27:** Criar usuário novo → acessar Início, Transações, Plano, Carteira → cada um tem empty state com CTA correto ✅

---

## Ordem de execução

```
B4.01 → B4.02   (format: criar lib antes de substituir usos)
B2.01 → B2.02   (diagnosticar antes de corrigir)
B1.01 → B1.02   (mapear antes de substituir)
B3.01            (independente)
S19.01 → S19.02 → S19.03  (nav: sequencial)
S27.01 → S27.02..06        (empty states: componente antes das páginas)
```

## Commit ao finalizar

```bash
git add app_dev/frontend/src/
git commit -m "feat(ux): bugs de navegação + formatBRL + bottom nav redesign + empty states"
```
