# PRD — Admin: Gestão Completa de Usuários

**Sub-projeto:** 01  
**Sprint:** 0  
**Estimativa:** ~6h  
**Dependências:** nenhuma — pode ser executado a qualquer momento  

---

## Problema

O `app_admin` já permite criar, editar e desativar usuários, mas faltam as operações complementares que um admin precisa no dia a dia: reativar uma conta pausada por engano, ver o volume de dados antes de excluir, excluir permanentemente com segurança e garantir que todo novo usuário chegue ao app com a configuração básica pronta.

Hoje:
- Não é possível reativar uma conta desativada sem SQL direto
- Não há visibilidade de quantos dados um usuário tem antes de excluí-lo
- Exclusão permanente (purge) não existe na UI — risco de dados órfãos
- Novo usuário criado chega no app sem grupos padrão → primeiro upload falharia na classificação

---

## Fora do escopo

- Auto-cadastro no app principal (nunca será permitido)
- Painel de analytics de uso agregado (para o futuro)
- Notificações por e-mail ao usuário ao ser reativado/excluído

---

## User stories

### SA1 — Reativar conta de usuário
> Como admin, quando um usuário foi desativado por engano ou temporariamente, quero reativá-lo sem perder nenhum dado.

**Acceptance criteria:**
- Toggle "Ver inativos" na listagem exibe usuários com `ativo=0` em linhas esmaecidas com badge "INATIVA"
- Botão "Reativar" visível apenas em linhas de inativos
- Após reativar: `ativo=1`, usuário consegue logar, todos os dados preservados
- Sem confirmação obrigatória (operação não destrutiva)

### SA2 — Stats de conta antes de excluir
> Como admin, antes de excluir permanentemente um usuário, quero ver quantos dados ele tem para tomar uma decisão informada.

**Acceptance criteria:**
- Coluna "Dados" na tabela: `N tx · últ. DD/MM/AAAA` (ou "Sem dados")
- Dados carregados em paralelo com a lista (skeleton, não bloqueia renderização)
- Tooltip completo ao hover: `N uploads · N grupos · tem plano · tem investimentos`

### SA3 — Purge total com confirmação dupla
> Como admin, quando um usuário solicita exclusão completa de conta, quero apagar permanentemente todos os dados dele de forma segura e irreversível.

**Acceptance criteria:**
- Botão "⚠ Purge" visualmente distinto de "Desativar" (vermelho sólido vs. outline)
- **Etapa 1:** resumo dos dados do usuário + aviso "ação irreversível e permanente"
- **Etapa 2:** campo para digitar e-mail exato — botão de confirmar só habilita quando coincidir
- Backend exige body `{ "confirmacao": "EXCLUIR PERMANENTEMENTE" }` além do token admin
- Após purge: zero registros em qualquer tabela com aquele `user_id`
- `user_id=1` (admin principal) **nunca** pode ser purgado
- Log imutável da operação: quem executou, quando, qual user_id

### SA4 — Trigger automático de inicialização ao criar conta
> Como admin, quando crio um novo usuário, quero que o app já esteja pronto com grupos padrão e perfil financeiro vazio.

**Acceptance criteria:**
- `POST /users/` dispara automaticamente criação de 11 grupos padrão em `base_grupos_config` com `is_padrao=True`
- Cria registro vazio em `user_financial_profile`
- Operação idempotente: se chamada duas vezes para o mesmo usuário, não duplica grupos
- Toast no admin após criar conta: "Conta criada. Grupos padrão e perfil financeiro configurados."

### SA5 — Listar usuários inativos
> Como admin, quero ver todos os usuários — ativos e inativos — em uma única tela com controle de filtro.

**Acceptance criteria:**
- Toggle "Ver inativos" no header da tabela
- Quando ligado: inativos incluídos com linha esmaecida + badge "INATIVA"
- Quando desligado (default): apenas ativos
- Contador no header atualiza: `4 ativas + 1 inativa`

---

## Wireframe de referência

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  Contas  · 4 ativas                        [+ Nova Conta]  [☐ Ver inativos]  │
├──────────────────┬───────────────────────┬───────────────────┬────────────────┤
│  Nome            │  E-mail               │  Dados            │  Ações         │
├──────────────────┼───────────────────────┼───────────────────┼────────────────┤
│  Emanuel Mangue  │  admin@financas.com   │  2.631 tx         │  [Editar]      │
│                  │                       │  últ. 15/01       │  (prot. admin) │
├──────────────────┼───────────────────────┼───────────────────┼────────────────┤
│  João Silva      │  joao@email.com       │  1.204 tx         │  [Editar]      │
│                  │                       │  últ. 03/02       │  [Desativar]   │
│                  │                       │                   │  [⚠ Purge]    │
├──────────────────┼───────────────────────┼───────────────────┼────────────────┤
│  ░░ Maria Costa  │  ░░ maria@email.com   │  45 tx            │  [Reativar]   │
│  INATIVA         │                       │  últ. 11/11       │  [⚠ Purge]    │
└──────────────────┴───────────────────────┴───────────────────┴────────────────┘
```

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Admin purga usuário errado (irreversível) | Confirmação em 2 etapas + digitar e-mail exato + user_id=1 protegido + log |
| Trigger de init falha silenciosamente | Logar erro mas não bloquear criação do usuário; admin pode re-triggar manualmente |
| Grupos padrão duplicados se trigger chamado duas vezes | Verificar `COUNT WHERE is_padrao=True AND user_id=X` antes de inserir |

---

## Métricas de sucesso

- 100% dos novos usuários criados via admin chegam com grupos padrão (zero erros no trigger SA4)
- Zero registros órfãos (`user_id` sem `users` pai) após qualquer operação de purge
- Operação de purge completa em < 3s
