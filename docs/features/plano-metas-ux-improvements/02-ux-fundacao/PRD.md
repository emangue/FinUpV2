# PRD — UX Fundação: Bugs + Navegação + Empty States

**Sub-projeto:** 02  
**Sprint:** 1  
**Estimativa:** ~10h  
**Dependências:** nenhuma — 100% frontend, independente  

---

## Problema

Antes de construir qualquer feature nova, a experiência atual tem falhas que quebram o fluxo do usuário:
- Navegação em círculo: botão "← Voltar" em modais leva para telas erradas
- Editar lançamento em uma tela replica a alteração errada em outras telas
- Scroll na tabela mobile não funciona em alguns dispositivos
- Valores monetários aparecem sem formatação BR em algumas telas
- Navegação principal não tem acesso direto a Upload, Plano e Carteira
- Telas sem dados não orientam o usuário (o que fazer agora?)

---

## Fora do escopo

- Redesign visual completo (apenas ajustes de navegação e comportamento)
- Novos dados ou endpoints de backend
- Onboarding (será feito no sub-projeto 03)

---

## User stories

### B1 — Navegação não entra em loop
> Como usuário, quando clico em "← Voltar" dentro de qualquer modal ou tela secundária, quero ir para a tela anterior correta, não reiniciar o loop.

**Acceptance criteria:**
- `router.back()` substituído por `router.push('/mobile/[destino-explicito]')` em todos os modais de edição de transação
- Abrir modal de edição em `/mobile/transacoes` → fechar → permanecer em `/mobile/transacoes`
- Abrir modal de edição em `/mobile/inicio` → fechar → permanecer em `/mobile/inicio`
- Nenhum estado de filtro é perdido ao fechar o modal

### B2 — Edição não replica em outras telas
> Como usuário, quando edito um lançamento em qualquer tela, a mudança deve aparecer apenas no lançamento correto, sem afetar outros.

**Acceptance criteria:**
- Identificar o bug específico de replicação (qual dado é compartilhado por referência)
- Garantir que cada instância de `EditTransactionModal` usa seu próprio estado local
- Editar lançamento A → lançamento B permanece intacto em qualquer tela
- Teste: editar 2 lançamentos em sequência, ambos persistem separadamente

### B3 — Scroll funciona em tabela mobile
> Como usuário mobile, quero conseguir rolar a lista de transações com o dedo sem que a tela trave.

**Acceptance criteria:**
- `overflow-y: auto` com `webkit-overflow-scrolling: touch` no container da tabela
- Scroll funciona em iOS Safari e Chrome Android
- Cabeçalho da tabela permanece fixo durante o scroll (sticky header)

### B4 — Valores monetários formatados em BR
> Como usuário, quero ver valores sempre no formato R$ 1.234,56 em todas as telas.

**Acceptance criteria:**
- Função utilitária `formatBRL(value: number): string` centralizada em `@/lib/format`
- Todos os componentes que exibem valor monetário usam `formatBRL`
- Negativos: `R$ -1.234,56` (mantém sinal)
- Zero: `R$ 0,00`

### S19 — Redesign da navegação principal
> Como usuário, quero acessar Upload, Plano Financeiro e Carteira de Investimentos diretamente da navegação, sem precisar navegar para o Início primeiro.

**Acceptance criteria:**
- Bottom navigation (mobile) tem 5 itens: Início · Transações · Upload · Plano · Carteira
- Sidebar (desktop) expõe os mesmos 5 destinos
- Ícone de Upload é um FAB (floating action button) destacado visualmente no mobile
- Tela ativa tem indicador visual claro (ícone preenchido + label)
- Rota `/mobile/upload` já existe — apenas adicionar o link na nav

### S27 — Empty states orientadores
> Como usuário novo, quando chego em uma tela sem dados, quero entender o que fazer para começar a usá-la.

**Acceptance criteria:**
- Cada tela principal tem um empty state específico (não genérico)
- `/mobile/inicio` sem dados: "Comece subindo seu extrato" + [→ Fazer upload]
- `/mobile/transacoes` sem dados: "Nenhuma transação ainda" + [→ Fazer upload]
- `/mobile/plano` sem plano: "Crie seu Plano Financeiro" + [→ Criar plano]
- `/mobile/carteira` sem ativos: "Adicione seus investimentos" + [→ Adicionar]
- Empty state nunca aparece durante loading (skeleton primeiro)

---

## Wireframe — Nova navegação

```
Mobile (bottom nav):
┌──────────────────────────────────────────────────────┐
│                     Conteúdo                         │
│                                                      │
│              ╔══════╗                                │
│              ║  📤  ║  ← FAB Upload (destacado)     │
│              ╚══════╝                                │
├──────────────────────────────────────────────────────┤
│  🏠 Início  📋 Transações  📊 Plano  📈 Carteira    │
└──────────────────────────────────────────────────────┘
```

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| `router.back()` tem comportamento diferente no iOS Safari | Usar `router.push(destino)` explícito com mapa de destinos por origem |
| Bug de replicação pode ser em Context/store global | Auditar se há estado compartilhado por referência em `useTransactionStore` ou similar |

---

## Métricas de sucesso

- Zero relatórios de navegação em círculo
- Replicação de edição não ocorre em nenhum cenário de teste
- Empty states presentes em 100% das telas principais
