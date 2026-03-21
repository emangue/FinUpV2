# Validação Git – Projeto FinUp (20/02/2026)

**Plano de ação central (Git + Docker + Backup):** [PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md](PLANO_ACAO_IMPLANTACAO_GIT_DOCKER_BACKUP.md)

Objetivo: entender como o projeto está sendo versionado hoje e se algo precisa ser ajustado para funcionar bem (incluindo rollback e branches).

---

## Regra de deploy (alterações grandes)

**Em toda alteração grande: criar branch antes de subir no servidor; só depois que der certo no servidor, fazer merge na main.**

- **Antes de subir:** criar uma branch (ex.: `deploy/2026-02-20-plano-aposentadoria` ou `feature/nome-da-feature`), commitar e dar push **dessa branch**. O servidor recebe e usa **essa branch** (pull da branch no servidor).
- **Depois que validar no servidor:** aí sim fazer merge dessa branch na `main` e push da `main`. Assim a main só é atualizada quando o deploy foi validado.
- **Rollback:** se der errado no servidor, a main continua intacta; você descarta a branch ou corrige nela e faz novo deploy, sem precisar reverter a main.

O script `safe_deploy.sh` pode pedir ou criar essa branch automaticamente quando você for fazer deploy a partir da main (ver seção 4 e script).

---

## 1. Estado atual (hoje)

### Branch e remotes

| Item | Valor |
|------|--------|
| Branch local atual | `main` |
| Sua main está | **25 commits atrás** de `origin/main` (pode fazer `git pull` para atualizar) |
| Remotes | `origin` = https://github.com/emangue/FinUpV2.git ; `vps` = root@64.23.241.43:/var/repo/finup.git |
| Branch padrão no GitHub | `origin/HEAD` aponta para **`origin/dev/models-2025-12-28`** (não para `main`) |
| Outras branches (remotes) | `dev/models-2025-12-28`, `dev/models-2026-01-03`, `feature/mobile-prototypes-integration` |

### Working directory (não commitado)

- **Staged (prontos para commit):** muitas alterações (renames para `_arquivo_desktop/`, app_admin, backend, frontend, docs, scripts, etc.).
- **Unstaged:** alguns arquivos **deletados** no disco mas ainda não removidos do índice (ex.: `app_dev/backend/app/domains/dashboard/router.py`, `transactions/router.py`, vários `migrate_*.py`).
- **Untracked:** pastas inteiras (ex.: `app_dev/frontend/src/app/budget/`, `dashboard/`, `settings/`, `transactions/`, `upload/`) e `docs/deploy/PLANO_ACAO_INFRA_DOCKER_BACKUP.md`.

Ou seja: o Git está guardando **snapshots** por commit; o que você vê na pasta é a soma do último commit + alterações locais (staged + unstaged + untracked). Se você “mudar o projeto todo” e não commitar, o GitHub continua com a última versão que você deu push – por isso “não tem exatamente a última versão” no remoto: o remoto tem o que foi enviado; o que mudou depois só existe na sua máquina até você commitar e dar push.

---

## 2. O que está sendo “salvo” (versionado) de fato

- **No GitHub (origin):** apenas o que já foi commitado **e** enviado com `git push`. A `main` do servidor está 25 commits à frente da sua `main` local – ou seja, no remoto já existem 25 commits que você ainda não puxou.
- **Na sua máquina:** último commit que você tem (ex.: `178175e8 fix: migration 635e...`) + tudo que está em “Changes to be committed” + “Changes not staged” + “Untracked”. Nada disso (staged/unstaged/untracked) está “salvo” no Git até você fazer `git add` e `git commit`; e não está no GitHub até você fazer `git push`.

Resumo: o projeto “como um todo” no GitHub é exatamente o **último snapshot** que alguém commitou e deu push na branch em que você está (ou na que o servidor usa). Mudanças locais não commitadas não entram nesse snapshot.

---

## 3. Riscos e inconsistências encontrados

### 3.1 Branch padrão do GitHub ≠ main

- No remoto, `origin/HEAD` aponta para `dev/models-2025-12-28`, não para `main`.
- Quem clonar o repositório pode vir parar nessa branch em vez de `main`.
- Se a sua “produção” ou “porto seguro” é a `main`, vale deixar a branch padrão do repositório no GitHub como `main` (Settings → Repositories → Default branch) para evitar confusão e para a estratégia “main = porto seguro” fazer sentido para todos.

### 3.2 Main local 25 commits atrás

- Sua `main` local está 25 commits atrás de `origin/main`.
- Até você fazer `git pull` (ou `git pull origin main`), seu histórico local da `main` não é o “último estado” do servidor. Rollbacks e comparações devem considerar isso: o “estado atual do projeto” no remoto é o que está em `origin/main` após esses 25 commits.

### 3.3 Banco de dados e .gitignore

- O arquivo **não** está versionado (confirmado: `git ls-files` não lista `*.db`).
- No `.gitignore` da raiz há a linha:
  - `!app_dev/backend/database/financas_dev.db`
  - Com o comentário “Database oficial (ÚNICO permitido - **não ignorar**)”.
- Isso **permite** que esse arquivo seja adicionado ao Git (ele deixa de ser ignorado por essa regra na raiz). Em geral não é desejável versionar `.db` (tamanho, binário, risco de dados sensíveis). O comentário pode ser lido como “não ignorar” = “trackear”, o que é arriscado.
- **Recomendação:** remover a linha `!app_dev/backend/database/financas_dev.db` e deixar o banco sempre ignorado (em todos os `.gitignore`). Se a intenção era “não commitar”, o correto é **manter** o arquivo ignorado (sem exceção).

### 3.4 Muitas mudanças em um único stage

- Há um bloco grande de alterações já em stage (staged). Se você commitar tudo de uma vez, fica um commit único com muitas mudanças; rollback seria “tudo ou nada” para esse passo.
- Estratégia mais segura (e alinhada ao que o Gemini descreveu): usar **branches** para mudanças grandes; commitar em passos menores na branch; fazer merge na `main` quando estiver estável. Assim, “rollback” = voltar para `main` e descartar a branch, sem precisar de `git reset --hard` na main.

---

## 4. O que ajustar para “funcionar bem”

### 4.1 Alinhar branch padrão e uso da main

- No GitHub: definir a branch padrão do repositório como **main** (se main for mesmo a branch de referência).
- Regra de uso: **main** = porto seguro; não desenvolver direto nela; mudanças em **branches** (ex.: `feature/nome`); quando estiver ok, fazer merge em `main` e depois `git push`.

### 4.2 Evitar que o banco entre no Git

- Remover do `.gitignore` da raiz a linha:
  - `!app_dev/backend/database/financas_dev.db`
- Garantir que em todos os `.gitignore` (raiz e `app_dev/`) o arquivo do banco continue ignorado (ex.: `*.db` ou o path explícito `app_dev/backend/database/financas_dev.db`), sem exceções que o “designorem”.

### 4.3 Antes de qualquer rollback

- Se quiser **só ver** um estado antigo: `git checkout <commit-hash>` (modo “leitura”; cuidado com detached HEAD se editar).
- Se quiser **descartar** commits locais e voltar a um commit anterior: `git reset --hard <commit-hash>` **apaga** tudo que não foi commitado; usar só quando tiver certeza.
- Estratégia mais segura: trabalhar em branch; se der errado, voltar para `main` e apagar a branch (`git checkout main` e `git branch -D nome-da-branch`); não precisa de `reset --hard` na main.

### 4.4 Sincronizar sua main com o remoto (detalhado)

**Situação:** Você tem muitas alterações locais (staged, unstaged, untracked) e a `main` local está atrás do `origin/main`. Você não quer perder o trabalho nem travar a main.

**Opção A — Guardar o trabalho em uma branch e depois alinhar a main**

1. Criar uma branch com todo o estado atual (incluindo o que está staged/unstaged/untracked):
   ```bash
   git checkout -b wip/meu-trabalho
   git add .
   git status   # conferir
   git commit -m "wip: trabalho em andamento (plano aposentadoria / ajustes)"
   ```
2. Voltar para a `main` e puxar o remoto:
   ```bash
   git checkout main
   git pull origin main
   ```
3. A partir daqui: a `main` está igual ao GitHub. O trabalho “grande” está só na branch `wip/meu-trabalho`. Você pode:
   - Continuar trabalhando nessa branch (novos commits lá).
   - Ou criar uma branch “limpa” a partir da `main` atualizada (ex.: `feature/plano-aposentadoria`) e ir migrando/cherry-pickando commits da `wip/meu-trabalho` em passos menores.

**Opção B — Descartar tudo e alinhar com o remoto (só se não precisar das mudanças)**

```bash
git checkout main
git restore --staged .
git restore .
git pull origin main
```

Os arquivos **untracked** continuam na pasta; se quiser removê-los também, apague manualmente ou use `git clean`. Não recomendado se o trabalho for importante.

---

## 5. Exemplo aplicado: projeto “Plano Aposentadoria Ajustes”

Este exemplo mostra como o **ponto 4.4** (sincronizar main + usar branches) se aplica a um projeto grande e contínuo, como o do plano em [plano_aposentadoria_ajustes_409e8d53.plan.md](.cursor/plans/plano_aposentadoria_ajustes_409e8d53.plan.md) (Sprints A a I).

### Premissas

- **main** = porto seguro; não desenvolver direto nela.
- O “projeto” = conjunto de entregas (Plano Aposentadoria: cenários, gráfico, Central de Cenários, integração orçamento, redesign transações, upload, etc.).

### Fluxo recomendado

| Passo | Ação | Comando / decisão |
|-------|------|-------------------|
| 1 | Garantir que a main local está alinhada ao remoto | `git checkout main` e `git pull origin main` (se ainda tiver trabalho local, usar 4.4 Opção A antes). |
| 2 | Criar branch do projeto (ou por fase grande) | `git checkout -b feature/plano-aposentadoria-ajustes` |
| 3 | Desenvolver por Sprint | Cada Sprint (A, B, C…) = um ou mais commits **nessa branch**. Ex.: “feat(plano): Sprint A – remove mensagem Ver Todas” e “feat(plano): Sprint B – highlight Despesas vs Plano”. |
| 4 | Manter main estável | Não fazer merge na main até uma etapa estar validada (ex.: fim de um Sprint ou conjunto de Sprints). |
| 5 | Integrar na main quando estável | `git checkout main`, `git pull origin main`, `git merge feature/plano-aposentadoria-ajustes`, resolver conflitos se houver, `git push origin main`. |
| 6 | Continuar o projeto | Voltar para a branch: `git checkout feature/plano-aposentadoria-ajustes`, puxar a main para atualizar a branch: `git merge main` (ou `git rebase main`), seguir nos Sprints seguintes. |
| 7 | Rollback (deu errado em algo grande) | Não usar `git reset --hard` na main. Voltar para main e descartar a branch: `git checkout main`, `git branch -D feature/plano-aposentadoria-ajustes`. O projeto “como um todo” desse plano some; a main continua intacta. Se já tiver feito merge na main, a reversão é outro merge (revert) ou novo branch que desfaz partes específicas. |

### Como ficaria “todo o projeto” no Git

- **Um repositório, uma main:** a “última versão estável” do app está na `main` (no remoto, após `git push`).
- **Um branch de feature para o plano:** `feature/plano-aposentadoria-ajustes` contém **todos** os commits do projeto (Sprints A → I). Cada commit = um passo lógico (ex.: “Sprint B – highlight”, “Sprint H – backend cenários aposentadoria”).
- **Snapshots:** cada commit é um snapshot do projeto. O “projeto completo” do plano = o estado da branch após o último commit dessa feature. A main = snapshot da última versão que você considerou estável e fez merge.
- **Sincronizar main (4.4) no meio do projeto:** se no meio dos Sprints a main no GitHub avançar (outras pessoas ou você em outra máquina), você atualiza a branch assim: `git checkout feature/plano-aposentadoria-ajustes`, `git fetch origin`, `git merge origin/main` (ou `git rebase origin/main`). Assim a branch do plano continua a partir da main mais recente, sem perder seus commits.

### Resumo do exemplo

- **Onde o ponto 3 (4.4) está detalhado:** na seção **4.4** deste documento (Sincronizar sua main com o remoto).
- **Como fica o projeto “Plano Aposentadoria Ajustes”:** em uma branch (`feature/plano-aposentadoria-ajustes`); commits por Sprint ou por grupo lógico; main só recebe merge quando estável; rollback = voltar para main e apagar a branch (ou reverter merges já feitos). Assim o Git guarda o projeto em snapshots (commits) e a “última versão” no remoto é exatamente o que foi commitado e enviado na main (e, na branch, o estado da feature).

---

## 6. Resumo

| Aspecto | Situação | Ação sugerida |
|--------|----------|----------------|
| Como o Git salva | Snapshots por commit; alterações locais não estão “salvas” até commit + push | Entender que “última versão no GitHub” = último push na branch; local = último commit + working dir |
| Branch padrão GitHub | `dev/models-2025-12-28` | Definir `main` como default se for o porto seguro |
| Main local vs remoto | 25 commits atrás | Usar 4.4: criar branch com seu trabalho, commitar lá; depois `git checkout main` e `git pull` |
| Banco no Git | Não está trackeado; há regra que **permite** trackear | Remover `!app_dev/backend/database/financas_dev.db` do .gitignore da raiz |
| Rollback | Confuso se feito com checkout/reset sem regra clara | Usar branches; rollback = voltar para main e deletar a branch (ver exemplo seção 5) |

Com esses ajustes, o repositório fica consistente com a ideia de “main = última versão estável” e “rollback = abandonar a branch e voltar para main”, sem depender de cópia manual da pasta para “voltar”.
