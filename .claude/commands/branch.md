# Skill: Criação de Branch

## Workflow de fases do projeto
```
Phase 1: PRD     → docs/features/{nome}/01-PRD/PRD.md
Phase 2: TECH    → docs/features/{nome}/02-TECH_SPEC/TECH_SPEC.md
Phase 3: SPRINT  → docs/features/{nome}/03-SPRINT/SPRINTX_COMPLETE.md
Phase 4: DEPLOY  → docs/features/{nome}/04-DEPLOY/DEPLOY_CHECKLIST.md
Phase 5: POST    → docs/features/{nome}/05-POST/POST_MORTEM.md
```

## Antes de criar, pergunte
1. Nome da feature (kebab-case)
2. Fase atual (PRD / TECH / SPRINT / DEPLOY / POST)
3. Tipo de mudança: feat / fix / perf / chore / refactor

## Passos
```bash
# 1. Criar branch
git checkout -b {tipo}/{nome}

# 2. Criar estrutura de docs
mkdir -p docs/features/{nome}

# 3. Criar o arquivo da fase correspondente
```

## Convenções de nome de branch
- `feat/{nome}`     — nova funcionalidade
- `fix/{nome}`      — correção de bug
- `perf/{nome}`     — melhoria de performance
- `chore/{nome}`    — manutenção / dependências
- `refactor/{nome}` — refatoração sem mudança de comportamento

## Ao finalizar a feature
```bash
# Squash commits se necessário
git rebase -i main

# Push e abrir PR
git push origin {tipo}/{nome}
```
