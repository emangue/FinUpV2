# PRD — Onboarding + Grupos Padrão

**Sub-projeto:** 03  
**Sprint:** 2  
**Estimativa:** ~8h  
**Dependências:** Sub-projeto 01 (trigger de inicialização deve existir antes do onboarding funcionar)

---

## Problema

Novos usuários criados pelo admin chegam no app sem saber o que fazer. Não existe uma jornada de primeiro login. O app exibe telas vazias sem orientação. Sem grupos padrão, o primeiro upload já falha na etapa de classificação.

---

## Fora do escopo

- Tutorial interativo passo a passo (tooltip overlay)
- Vídeo de demonstração
- E-mail de boas-vindas
- Push notifications (fase futura)

---

## User stories

### S24 — Tela de boas-vindas (welcome)
> Como novo usuário, no meu primeiro login, quero ser recebido por uma tela que explique o valor do app e me ajude a escolher como começar.

**Acceptance criteria:**
- Middleware detecta: usuário logado + nunca completou onboarding → redireciona para `/mobile/onboarding/welcome`
- Tela exibe: logo + headline "Bem-vindo ao FinUp" + 3 bullets do valor do app
- Dois caminhos: "Começar com meus dados" (→ upload) e "Explorar primeiro" (→ modo demo)
- Botão "Pular" leva direto ao `/mobile/inicio` (onboarding marcado como completo)

### S25 — Grupos padrão disponíveis no primeiro login
> Como novo usuário, quero que o app já tenha categorias básicas configuradas quando faço meu primeiro upload, sem precisar criar grupos manualmente.

**Acceptance criteria:**
- Grupos padrão já existem ao criar a conta (trigger do sub-projeto 01)
- No onboarding, tela mostra preview dos grupos: "Seu app já tem categorias básicas configuradas"
- Usuário pode personalizar (renomear, mudar cor) em qualquer momento via Configurações → Grupos
- Grupos com `is_padrao=True` são diferentes de grupos criados manualmente (não somem se o usuário resetar)

### S26 — Modo exploração com dados demo
> Como novo usuário curioso, quero explorar o app com dados fictícios antes de comprometer meus dados reais.

**Acceptance criteria:**
- Dataset de demo pré-gerado com ~100 transações de 3 meses em múltiplos grupos
- Banner fixo no topo quando em modo demo: "Modo de Exploração — [Usar meus dados →]"
- Dados demo isolados por flag `fonte='demo'` em `journal_entries` — nunca misturados com dados reais
- "Usar meus dados →" limpa os dados demo e vai para o upload
- `DELETE /onboarding/modo-demo` remove apenas registros com `fonte='demo'`

### S28 — Checklist de primeiros passos
> Como novo usuário, quero ver um guia visual de progresso para saber quais passos completar para aproveitar o app completamente.

**Acceptance criteria:**
- Card "Seus primeiros passos" exibido no `/mobile/inicio` enquanto há itens pendentes
- 4 itens: ✅ Criou sua conta · ⬜ Subiu seu primeiro extrato · ⬜ Criou seu Plano · ⬜ Adicionou um investimento
- Cada item completado: check animado
- Ao completar todos os 4: card some e é substituído pelo resumo normal do mês

```
┌─────────────────────────────────────────────────────┐
│  Seus primeiros passos  · 1/4 concluídos            │
│                                                     │
│  ✅ Criou sua conta                                 │
│  ⬜ Suba seu primeiro extrato          [→ Fazer]   │
│  ⬜ Crie seu Plano Financeiro          [→ Fazer]   │
│  ⬜ Adicione um investimento           [→ Fazer]   │
└─────────────────────────────────────────────────────┘
```

### S29 — Notificações de ativação in-app
> Como usuário em processo de engajamento, quero receber nudges contextuais que me ajudem a progredir na configuração do app.

**Acceptance criteria:**
- Banners contextuais no `/mobile/inicio`, nunca intrusivos (sempre têm [X] para fechar)
- Triggers:
  - Primeiro upload feito → "Ótimo! Agora crie seu Plano para ter um orçamento real" + [→ Criar Plano]
  - Plano criado, sem investimentos → "Complete seu patrimônio! Adicione seus investimentos" + [→ Carteira]
  - Último upload há > 30 dias → "Hora de atualizar! Suba o extrato de [mês anterior]" + [→ Upload]
  - 3+ aportes aguardando vínculo há > 7 dias → "Você tem N aportes para vincular em Carteira" + [→ Carteira]
- Usuário que fecha um banner: não vê ele novamente na mesma sessão (localStorage)

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Middleware de redirect quebra deep links externos | Whitelist de paths que nunca são interceptados (ex: `/mobile/upload?source=email`) |
| Dados demo misturados com reais se flag `fonte` falhar | Seed de demo com user_id isolado ou flag dupla; `DELETE /modo-demo` usa WHERE + confirmação |
| Checklist não some quando último item completa (estado stale) | Invalidar cache do checklist via `mutate()` após cada ação relevante |

---

## Métricas de sucesso

- ≥ 60% dos novos usuários completam o primeiro upload em < 5 min após o cadastro
- Retenção D7: usuários que completam os 4 itens do checklist têm retenção 30% maior (hipótese a validar)
- 100% dos usuários novos chegam com grupos padrão (validação via query)
