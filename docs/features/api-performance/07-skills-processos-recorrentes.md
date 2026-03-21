# Mapeamento de Skills — Processos Recorrentes do FinUpV2

> Data: Março/2026
> Objetivo: identificar workflows repetitivos que justificam a criação de skills no Claude Code para aumentar velocidade e reduzir erros.

---

## O Que É um Skill

Um skill no Claude Code é um prompt salvo em `.claude/commands/` que, ao ser ativado com `/nome-do-skill`, expande em um conjunto de instruções detalhadas para o Claude executar. É o equivalente a uma macro inteligente — elimina a necessidade de repetir contexto, padrões e regras a cada sessão.

---

## Skills Propostos

### 1. `/deploy` — Deploy na VM

**Frequência:** 3-5x por semana
**Risco:** Alto (produção, rollback automático, saúde dos containers)

#### O que o processo envolve hoje

```
1. Verificar git status (sem mudanças não commitadas)
2. git push origin <branch>
3. Verificar conectividade SSH com minha-vps-hostinger
4. Verificar se .env.prod existe na VM
5. Executar deploy_docker_build_local.sh OU deploy_docker_vm.sh
6. Aguardar health checks (12 tentativas × 5s) no backend :8000
7. Verificar que os 3 containers estão Up
8. Executar alembic upgrade head dentro do container
9. Validar com validate_deploy.sh
10. Registrar rollback commit (caso seja necessário reverter)
```

**Scripts existentes:**
- `scripts/deploy/deploy_docker_build_local.sh` — build local + SCP + deploy (workaround OOM da VM)
- `scripts/deploy/deploy_docker_vm.sh` — build na VM com rollback automático (250 linhas, 6 fases)
- `scripts/deploy/validate_deploy.sh` — health checks pós-deploy

#### O que o skill faria

- Verificar pré-condições (git limpo, SSH acessível, .env.prod existe)
- Guiar a escolha entre os dois scripts de deploy com base no contexto
- Monitorar progress e sinalizar falhas por fase
- Executar validação pós-deploy
- Documentar o rollback commit do deploy atual
- Avisar sobre necessidade de migrations pendentes

#### Boilerplate do skill

```markdown
<!-- .claude/commands/deploy.md -->
Você é um assistente de deploy para o FinUpV2.

## VM e configuração
- Host SSH: `minha-vps-hostinger`
- Path na VM: `/var/www/finup`
- Compose: `docker-compose.prod.yml`
- Containers: finup_backend_prod (:8000), finup_frontend_app_prod (:3003), finup_frontend_admin_prod (:3001)

## Pré-condições obrigatórias
1. `git status -uno` → sem mudanças não commitadas
2. `git push origin <branch-atual>`
3. `ssh minha-vps-hostinger echo ok` → SSH acessível
4. `.env.prod` existe na VM

## Fluxo de escolha de script
- VM com memória suficiente → `deploy_docker_vm.sh` (build na VM)
- VM com OOM risk → `deploy_docker_build_local.sh` (build local + SCP)

## Health checks esperados
- Backend: GET http://localhost:8000/health → 200 (máx 60s)
- Portas: 8000, 3003, 3001 Up

## Após deploy
- Rodar `validate_deploy.sh`
- Registrar commit de rollback
- Confirmar migrations com `docker exec finup_backend_prod alembic current`
```

---

### 2. `/new-processor` — Criador de Novo Processador Raw

**Frequência:** 1-2x por mês
**Risco:** Médio (parsing incorreto = dados errados para o usuário)

#### O que o processo envolve hoje

```
1. Criar arquivo em /processors/raw/{format}/{banco}_{tipo}.py
2. Implementar função process_{banco}_{tipo}(file_path, ...) → (List[RawTransaction], BalanceValidation)
3. Usar pandas (Excel), pdfplumber/PyMuPDF (PDF) ou easyocr (OCR)
4. Mapear colunas para RawTransaction (banco, tipo_documento, data, lancamento, valor, mes_fatura...)
5. Calcular BalanceValidation (saldo_inicial + soma = saldo_final, tolerância 1 centavo)
6. Registrar em registry.py: PROCESSORS[('banco_normalizado', 'tipo', 'formato')] = funcao
7. Adicionar import no registry.py
8. Atualizar .env.example se precisar de senha (ex: ITAU_PDF_SENHA=CPF)
9. Atualizar requirements.txt se tiver nova dependência
10. Atualizar tabela de compatibilidade no banco
11. Testar com arquivo real e validar balance_validation.is_valid == True
```

**Padrão dos processadores existentes:**
- Simples: `itau_extrato.py` (108 linhas) — pandas + Excel
- Médio: `btg_fatura_xlsx.py` — Excel com múltiplas abas
- Complexo: `mercadopago_fatura_pdf.py` — OCR + PyMuPDF + agrupamento por coordenada Y (~20-25s/fatura, ~950MB RAM)

#### O que o skill faria

- Perguntar: banco, tipo (fatura/extrato), formato (excel/pdf/pdf+ocr)
- Gerar o arquivo do processador com boilerplate correto para o formato
- Gerar o patch para `registry.py` (import + PROCESSORS entry)
- Avisar sobre dependências necessárias e variáveis de ambiente
- Gerar checklist de validação com arquivo real

#### Boilerplate do skill

```markdown
<!-- .claude/commands/new-processor.md -->
Você é um assistente de criação de processadores raw para o FinUpV2.

## Antes de criar, pergunte:
1. Nome do banco (ex: "Nubank", "C6 Bank")
2. Tipo: fatura ou extrato
3. Formato: excel (.xlsx), pdf (texto), pdf (OCR/imagem)

## Estrutura obrigatória da função
Path: app_dev/backend/app/domains/upload/processors/raw/{formato}/{banco_snake}_{tipo}.py

Assinatura:
def process_{banco}_{tipo}(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> Tuple[List[RawTransaction], BalanceValidation]:

## Campos obrigatórios do RawTransaction
banco, tipo_documento, nome_arquivo, data_criacao, data (DD/MM/YYYY),
lancamento, valor (float, negativo=débito), nome_cartao, final_cartao, mes_fatura (AAAAMM)

## BalanceValidation
Validar: saldo_inicial + soma_transacoes ≈ saldo_final (tolerância 0.01)

## Registry
Arquivo: app_dev/backend/app/domains/upload/processors/registry.py
Chave: _normalize_bank_name(banco) = lowercase sem acentos

## Dependências por formato
Excel: pandas, openpyxl, (msoffcrypto-tool se criptografado)
PDF texto: pdfplumber
PDF OCR: pdfplumber + PyMuPDF (fitz) + easyocr
```

---

### 3. `/new-api-domain` — Scaffolding de Novo Domínio FastAPI

**Frequência:** 1-2x por sprint
**Risco:** Baixo (boilerplate bem definido)

#### O que o processo envolve hoje

```
1. Criar pasta app/domains/{nome_dominio}/
2. Criar __init__.py
3. Criar models.py → SQLAlchemy com user_id + campos do domínio
4. Criar schemas.py → Pydantic Create/Update/Response/ListResponse
5. Criar repository.py → get_all_by_user, get_by_id, create, update, delete
6. Criar service.py → instancia repo, contém regras de negócio
7. Criar router.py → GET /, GET /{id}, POST /, PATCH /{id}, DELETE /{id}
8. Registrar router em app/main.py (import + app.include_router)
9. Criar migration Alembic para a nova tabela
10. Testar endpoints via /docs (Swagger automático do FastAPI)
```

**Padrão dos domínios existentes (18 domínios):**
```
domain/
├── __init__.py
├── models.py        (30-80 linhas)
├── schemas.py       (100-200 linhas)
├── router.py        (50-150 linhas)
├── service.py       (150-400 linhas)
└── repository.py    (100-300 linhas)
```

#### O que o skill faria

- Perguntar: nome do domínio, campos principais, endpoints desejados
- Gerar todos os 6 arquivos com boilerplate correto
- Incluir user_id isolation (segurança padrão do projeto)
- Gerar patch para main.py
- Gerar migration Alembic
- Garantir que o padrão de dependências (`get_db`, `get_current_user_id`) seja seguido

#### Boilerplate do skill

```markdown
<!-- .claude/commands/new-api-domain.md -->
Você é um assistente de scaffolding de domínios FastAPI para o FinUpV2.

## Antes de criar, pergunte:
1. Nome do domínio (snake_case, ex: "meu_dominio")
2. Nome da tabela (ex: "meus_itens")
3. Campos principais (nome, tipo, obrigatório?)
4. Endpoints desejados (CRUD completo ou subset?)

## Arquitetura padrão
Backend path: app_dev/backend/app/domains/{nome}/

## Regras de segurança OBRIGATÓRIAS
- Todos os models têm user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
- Todos os repositories filtram por user_id (NUNCA retornar dados de outros usuários)
- Todos os endpoints usam Depends(get_current_user_id)

## Dependencies padrão
from app.core.database import get_db
from app.shared.dependencies import get_current_user_id

## Registro em main.py
from app.domains.{nome}.router import router as {nome}_router
app.include_router({nome}_router, prefix="/api/v1")

## Após criar os arquivos
Gerar migration:
docker exec finup_backend_dev alembic revision --autogenerate -m "Add {nome} table"
```

---

### 4. `/new-feature` — Scaffolding de Nova Feature Frontend

**Frequência:** 2-3x por sprint
**Risco:** Baixo (boilerplate, sem lógica de produção)

#### O que o processo envolve hoje

```
1. Criar pasta src/features/{nome}/
2. Criar types/index.ts → interfaces TypeScript
3. Criar services/{nome}-api.ts → funções de fetch para os endpoints
4. Criar hooks/use-{nome}.ts → estado, loading, error, refetch
5. Criar components/{NomeComponent}.tsx → UI principal
6. Criar components/index.ts → barrel export
7. Criar features/{nome}/index.ts → barrel export geral
8. (Opcional) Criar src/app/mobile/{nome}/page.tsx
9. (Opcional) Criar src/app/{nome}/page.tsx (desktop)
```

**Padrão dos features existentes (14 features):**
```
features/{nome}/
├── index.ts
├── types/index.ts
├── services/{nome}-api.ts
├── hooks/use-{nome}.ts
└── components/
    ├── index.ts
    └── {NomeComponent}.tsx
```

#### O que o skill faria

- Perguntar: nome da feature, endpoints que consome, componentes necessários
- Gerar toda a estrutura de pastas e arquivos com TypeScript correto
- Gerar hook com padrão `useState + useEffect + fetchWithAuth` do projeto
- Incluir cache in-memory se a feature for lida com frequência
- Gerar barrel exports corretamente
- Perguntar se precisa de página mobile, desktop ou ambas

#### Boilerplate do skill

```markdown
<!-- .claude/commands/new-feature.md -->
Você é um assistente de scaffolding de features frontend para o FinUpV2.

## Antes de criar, pergunte:
1. Nome da feature (kebab-case, ex: "minha-feature")
2. Endpoints de backend que ela consome
3. Componentes necessários (listagem, formulário, modal?)
4. Precisa de página? (mobile / desktop / ambas / nenhuma)

## Estrutura padrão
src/features/{nome}/
├── index.ts                    # barrel export geral
├── types/index.ts              # interfaces TypeScript
├── services/{nome}-api.ts      # fetchWithAuth calls
├── hooks/use-{nome}.ts         # estado + fetch
└── components/
    ├── index.ts                # barrel export de componentes
    └── {NomeComponent}.tsx

## Padrão de hook (copiar do projeto)
- useState para dados, loading, error
- useEffect para fetch no mount
- fetchWithAuth de src/core/utils/api-client.ts
- Cache in-memory se dados são lidos com frequência (TTL 2-5min)

## Padrão de API client
- BASE_URL de src/core/config/api.config.ts
- Sempre usar fetchWithAuth (cookies httpOnly)
- Deduplicate in-flight para endpoints com cache

## Styling
- Tailwind CSS v4
- Radix UI para componentes complexos (dialogs, dropdowns)
- Seguir padrão mobile: mobileTypography, mobileDimensions de src/config/
```

---

### 5. `/branch` — Criação de Branch e Gestão de Mudança

**Frequência:** Diário
**Risco:** Médio (git sync entre local e VM é ponto de falha documentado)

#### O que o processo envolve hoje

```
1. Identificar fase: PRD / TECH_SPEC / SPRINT / DEPLOY
2. Criar branch com nome descritivo
3. Criar estrutura de docs para a feature: docs/features/{nome}/
4. (Para PRDs) Criar PRD.md com template aprovado
5. (Para TECH_SPEC) Criar TECH_SPEC.md com ≥80% completude
6. (Para SPRINT) Criar SPRINTX_COMPLETE.md
7. (Para DEPLOY) Criar DEPLOY_CHECKLIST.md (250+ itens)
8. Garantir que NUNCA editar arquivos direto na VM (regra documentada desde 22/01/2026)
```

**Workflow de 5 fases documentado em `.github/copilot-instructions.md`:**
```
Phase 1: PRD     → docs/features/{nome}/01-PRD/PRD.md
Phase 2: TECH    → docs/features/{nome}/02-TECH_SPEC/TECH_SPEC.md
Phase 3: SPRINT  → SPRINTX_COMPLETE.md
Phase 4: DEPLOY  → docs/features/{nome}/03-DEPLOY/DEPLOY_CHECKLIST.md
Phase 5: POST    → POST_MORTEM.md
```

#### O que o skill faria

- Perguntar: nome da feature, fase atual
- Criar branch com nome padronizado
- Criar estrutura de docs para a fase
- Popular template correto (PRD, TECH_SPEC, SPRINT, DEPLOY, POST_MORTEM)
- Lembrar regras críticas (nunca editar na VM, sempre push antes de pull na VM)

---

### 6. `/migration` — Geração e Aplicação de Migration Alembic

**Frequência:** 1-2x por sprint
**Risco:** Alto (banco de produção, dados reais)

#### O que o processo envolve hoje

```
1. Modificar models.py com novos campos/tabelas
2. Gerar migration dentro do container dev:
   docker exec finup_backend_dev alembic revision --autogenerate -m "Descrição"
3. Revisar o arquivo gerado em migrations/versions/
4. Testar em dev: docker exec finup_backend_dev alembic upgrade head
5. Verificar que o guard (PostgreSQL only) está ativo em env.py
6. No deploy de prod: migration roda automaticamente via script de deploy
7. Em caso de erro: alembic downgrade -1
```

**Guard importante em `migrations/env.py`:**
- Bloqueia execução fora do PostgreSQL (previne rodar em SQLite acidentalmente)

#### O que o skill faria

- Perguntar: descrição da mudança, tabelas/campos afetados
- Verificar que models.py foi atualizado antes de gerar a migration
- Executar o comando correto dentro do container
- Revisar o arquivo gerado automaticamente
- Alertar sobre campos NOT NULL sem default em tabelas existentes (risco de falha em prod)
- Documentar o downgrade correspondente

---

## Tabela Resumo por Prioridade

| # | Skill | Frequência | Esforço de Criar | Valor |
|---|-------|-----------|-----------------|-------|
| 1 | `/deploy` | 3-5x/semana | Alto | Alto |
| 2 | `/new-processor` | 1-2x/mês | Médio | Alto |
| 3 | `/new-api-domain` | 1-2x/sprint | Médio | Alto |
| 4 | `/new-feature` | 2-3x/sprint | Baixo | Alto |
| 5 | `/branch` | Diário | Baixo | Médio |
| 6 | `/migration` | 1-2x/sprint | Médio | Alto |

---

## Como Criar um Skill

Os skills vivem em `.claude/commands/` na raiz do projeto:

```
.claude/
└── commands/
    ├── deploy.md
    ├── new-processor.md
    ├── new-api-domain.md
    ├── new-feature.md
    ├── branch.md
    └── migration.md
```

Cada arquivo é um prompt Markdown. Quando o usuário digita `/deploy`, o Claude Code carrega o conteúdo e executa com o contexto atual do projeto.

**Estrutura recomendada para cada arquivo:**
```markdown
# Nome do Skill

## Contexto do projeto
[Detalhes específicos do FinUpV2: paths, padrões, regras]

## Antes de executar, pergunte
[Variáveis que o Claude precisa coletar]

## Passos
[Sequência de ações, com paths exatos e comandos]

## Regras e armadilhas
[O que NÃO fazer, casos de borda, validações]

## Checklist de conclusão
[Como saber que o skill terminou corretamente]
```

---

## Próximos Passos

- [ ] Criar `.claude/commands/deploy.md` (maior valor imediato — risco real de erros)
- [ ] Criar `.claude/commands/new-processor.md` (processo mais complexo documentado)
- [ ] Criar `.claude/commands/new-api-domain.md` (boilerplate mais repetitivo)
- [ ] Criar `.claude/commands/new-feature.md` (mais frequente no dia a dia)
- [ ] Criar `.claude/commands/migration.md` (maior risco se feito errado)
- [ ] Criar `.claude/commands/branch.md` (baixo esforço, elimina esquecimentos)
