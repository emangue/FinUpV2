# /commit

Cria um commit padronizado para a branch atual do FinUp.
Segue Conventional Commits em português, com escopo obrigatório e corpo descritivo quando necessário.

## Formato do commit

```
tipo(escopo): descrição concisa em português

- detalhe 1 (se houver mais de uma mudança relevante)
- detalhe 2
```

### Tipos permitidos

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Só documentação (sem código) |
| `refactor` | Mudança interna sem alterar comportamento |
| `perf` | Melhoria de performance |
| `security` | Correção de segurança |
| `chore` | Build, dependências, config, scripts |
| `test` | Testes |

### Escopo

Usar o nome do domínio backend ou feature frontend afetado:
`plano`, `upload`, `dashboard`, `auth`, `transações`, `budget`, `investimentos`, `grupos`, `deploy`, `config`, `docs`

## O que fazer

### 1. Entender o que mudou

```bash
git status
git diff --staged    # arquivos já em stage
git diff             # arquivos modificados mas não em stage
```

Ler as mudanças para entender o contexto real — não confiar só nos nomes dos arquivos.

### 2. Nunca usar git add . ou git add -A

Mostrar ao usuário a lista de arquivos modificados e perguntar quais incluir.
Motivos para NÃO incluir automaticamente:
- `.env`, `.env.prod` — secrets
- `temp/`, `*.log` — arquivos temporários
- Arquivos não relacionados à mudança atual

```bash
# Formato da pergunta ao usuário:
# "Encontrei estes arquivos modificados:
#   backend: [lista]
#   frontend: [lista]
#   docs: [lista]
# Quais incluir no commit?"
```

### 3. Propor a mensagem de commit

Seguir o formato exato:
- Linha 1: `tipo(escopo): descrição` — sem ponto final, máximo 72 caracteres
- Linha em branco
- Corpo: bullets com detalhes (só se houver mais de uma mudança relevante)

Exemplos corretos do projeto:
```
feat(plano): wizard de 4 telas com gastos extraordinários

- implementa tela 1: Renda e modo de plano
- implementa tela 2: Gastos recorrentes com média 3 meses
- adiciona validação de recorrência mínima bimestral
```

```
fix(upload): validação de extensão e tamanho antes de leitura
```

```
security(upload): adicionar _validar_arquivo nos endpoints detect e preview
```

```
docs(dev-kit): processo canônico de deploy e cursor rules
```

### 4. Mostrar proposta e pedir confirmação

Antes de executar qualquer git add ou git commit, mostrar:

```
📋 Proposta de commit:

Arquivos: [lista dos arquivos que serão incluídos]

Mensagem:
---
feat(plano): wizard de 4 telas com gastos extraordinários

- implementa tela 1: Renda e modo de plano
- implementa tela 2: Gastos recorrentes com média 3 meses
---

Confirmar? (pode ajustar a mensagem se quiser)
```

### 5. Executar após confirmação

```bash
git add <arquivos específicos aprovados>
git commit -m "$(cat <<'EOF'
tipo(escopo): descrição

- detalhe 1
- detalhe 2
EOF
)"
```

### 6. Confirmar sucesso

Mostrar o hash do commit e os arquivos incluídos.
Opcionalmente: `git log --oneline -3` para mostrar contexto dos últimos commits.

## Regras que nunca devem ser quebradas

- **Nunca** commitar `.env`, `.env.prod`, `*.key`, arquivos de senha
- **Nunca** usar `git add .` — sempre arquivos específicos
- **Nunca** commitar sem mostrar a proposta ao usuário primeiro
- **Nunca** adicionar `--no-verify` a não ser que o usuário pedir explicitamente
- **Sempre** usar português na descrição
- **Sempre** ter escopo — `feat: algo` sem escopo não é aceito
