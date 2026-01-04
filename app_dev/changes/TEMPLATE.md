# Template de Documentação de Mudança

**Arquivo:** `caminho/do/arquivo.py`  
**Versão:** `X.Y.Z` → `X.Y.Z+1`  
**Data:** DD/MM/AAAA HH:MM  
**Autor:** Nome do desenvolvedor

---

## 📝 Descrição

Breve descrição da mudança realizada (1-2 parágrafos).

## 📂 Arquivos Modificados

- `arquivo1.py` - Descrição da modificação
- `arquivo2.py` - Descrição da modificação
- `arquivo3.html` - Descrição da modificação

## 🔄 Mudanças Realizadas

### Adicionado
- [ ] Nova funcionalidade X
- [ ] Novo campo Y no modelo Z

### Modificado
- [ ] Função `foo()` agora aceita parâmetro adicional
- [ ] Lógica de processamento otimizada

### Corrigido
- [ ] Bug #123: Descrição do bug corrigido
- [ ] Validação de entrada melhorada

### Removido
- [ ] Código deprecated X
- [ ] Função obsoleta Y

## 🧪 Testes Realizados

- [ ] Teste unitário de `função_modificada()`
- [ ] Teste de integração com módulo X
- [ ] Teste manual no ambiente de desenvolvimento
- [ ] Validação de dados no banco
- [ ] Teste de performance (antes/depois)

### Resultados dos Testes

```bash
# Comandos executados
python -m pytest tests/test_arquivo.py -v

# Resultados
✅ Todos os testes passaram (12/12)
⏱️  Performance: -30% tempo de execução
```

## 💥 Impacto

### Breaking Changes
- [ ] **Sim** - Descrição das mudanças incompatíveis
- [x] **Não** - Mudança mantém compatibilidade

### Migração de Banco de Dados
- [ ] **Sim** - SQL/script de migração necessário
- [x] **Não** - Nenhuma mudança no schema

### Outras Funcionalidades Afetadas
- [ ] Dashboard - Descrição do impacto
- [ ] Upload - Descrição do impacto
- [ ] Admin - Descrição do impacto
- [x] Nenhuma

### Dependências
- [ ] Requer nova biblioteca: `nome-pacote>=1.0.0`
- [ ] Atualização de pacote existente
- [x] Sem mudanças em dependências

## 🔙 Rollback

### Método 1: Checkout Específico (Recomendado)

```bash
# Reverter apenas este arquivo
git checkout v{versão_anterior} -- caminho/do/arquivo.py

# Reinstalar dependências se necessário
pip install -r requirements.txt

# Restartar aplicação
python run.py
```

### Método 2: Rollback Completo

```bash
# Rollback completo para versão anterior
python scripts/version_manager.py rollback v{versão_anterior}

# Verificar status
git status
python scripts/version_manager.py status
```

### Método 3: Manual

```bash
# Ver diff da mudança
git diff v{versão_anterior}..v{versão_nova} caminho/do/arquivo.py

# Reverter manualmente as linhas necessárias
# Editar arquivo e remover mudanças problemáticas
```

## 🔗 Relacionado

### Issues
- Resolve: #123
- Parcialmente resolve: #456
- Relacionado a: #789

### Pull Requests
- PR: #42

### Documentação
- [BUGS.md](../BUGS.md) - Bug #X resolvido
- [CHANGELOG.md](../CHANGELOG.md) - Versão X.Y.Z
- [README.md](../README.md) - Atualização necessária: Sim/Não

### Outros Arquivos de Mudança
- `2025-12-27_outro-arquivo_mudanca.md` - Mudança relacionada

## 📊 Métricas (Opcional)

### Performance
- Tempo de execução: antes Xms → depois Yms (**-Z%**)
- Uso de memória: antes XMB → depois YMB
- Queries SQL: antes X → depois Y

### Código
- Linhas adicionadas: +X
- Linhas removidas: -Y
- Complexidade ciclomática: antes X → depois Y

## 🎯 Checklist de Finalização

Antes de marcar mudança como completa:

- [ ] Código revisado e testado
- [ ] Documentação inline (docstrings) atualizada
- [ ] Testes unitários passando
- [ ] README.md atualizado (se necessário)
- [ ] requirements.txt atualizado (se necessário)
- [ ] Sem warnings ou erros no console
- [ ] Validado em ambiente similar à produção
- [ ] Rollback testado e validado
- [ ] Este documento completamente preenchido

---

## 💬 Notas Adicionais

Qualquer informação adicional relevante sobre a mudança:

- Decisões de design tomadas
- Alternativas consideradas
- Contexto histórico
- Lições aprendidas
- Futuras melhorias planejadas

---

**Gerado por:** `python scripts/version_manager.py finish`  
**Última atualização:** DD/MM/AAAA HH:MM
