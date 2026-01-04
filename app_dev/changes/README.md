# 📝 Pasta de Mudanças (Changes)

Esta pasta contém documentação individual de cada mudança realizada em arquivos críticos do projeto.

---

## 📂 Estrutura

```
changes/
├── TEMPLATE.md                          ← Template padrão (não deletar!)
├── README.md                            ← Este arquivo
├── 2025-12-27_models_adiciona-campo.md  ← Mudança individual
├── 2025-12-27_hasher_otimiza-hash.md    ← Mudança individual
└── _history/                            ← Histórico de releases
    ├── 2.1.0/
    │   ├── 2025-12-26_arquivo1.md
    │   └── 2025-12-26_arquivo2.md
    └── 2.2.0/
        └── ...
```

---

## 🎯 Propósito

Esta pasta serve para:

1. **Documentar mudanças em progresso** antes de serem agregadas no CHANGELOG
2. **Facilitar rollback** com instruções detalhadas
3. **Rastrear evolução** de cada arquivo crítico
4. **Revisar mudanças** antes de release

---

## 🔄 Fluxo de Vida dos Arquivos

```
1. Mudança iniciada
   → Arquivo criado automaticamente por version_manager.py finish

2. Mudança commitada
   → Arquivo permanece aqui

3. Release criado
   → Mudanças agregadas no CHANGELOG.md
   → Arquivos movidos para _history/<versao>/
```

---

## 📋 Convenção de Nomenclatura

**Formato:** `YYYY-MM-DD_nome-arquivo_descricao-curta.md`

**Exemplos:**
- `2025-12-27_models_adiciona-campo-categoria.md`
- `2025-12-27_hasher_corrige-colisao-vpd.md`
- `2025-12-28_routes_otimiza-query-parcelas.md`

---

## ✍️ Como Criar Mudança

### Automático (Recomendado):

```bash
# Ao finalizar mudança
python3 scripts/version_manager.py finish app/models.py "Descrição da mudança"

# Arquivo gerado automaticamente nesta pasta
```

### Manual (Se necessário):

```bash
# 1. Copiar template
cp changes/TEMPLATE.md changes/2025-12-27_arquivo_descricao.md

# 2. Editar arquivo preenchendo todas as seções
nano changes/2025-12-27_arquivo_descricao.md

# 3. Garantir que está completo antes de commitar
```

---

## 📝 Seções Obrigatórias

Todo arquivo de mudança deve ter:

- ✅ **Descrição** - O que foi feito e por quê
- ✅ **Arquivos Modificados** - Lista completa de arquivos
- ✅ **Mudanças Realizadas** - Detalhes técnicos (Adicionado/Modificado/Corrigido/Removido)
- ✅ **Testes Realizados** - Como validar a mudança
- ✅ **Impacto** - Breaking changes? Migração necessária?
- ✅ **Rollback** - Comandos para reverter

---

## 🔍 Revisando Mudanças

```bash
# Listar mudanças pendentes
ls -la changes/*.md | grep -v TEMPLATE

# Ver última mudança
cat changes/$(ls -t changes/*.md | grep -v TEMPLATE | head -1)

# Contar mudanças pendentes
ls changes/*.md | grep -v TEMPLATE | wc -l
```

---

## 🚀 Agregando no CHANGELOG

Quando um conjunto de mudanças está completo:

```bash
# Criar release (agrega automaticamente)
python3 scripts/version_manager.py release patch

# Resultado:
# 1. Mudanças adicionadas ao CHANGELOG.md
# 2. Arquivos movidos para _history/2.X.X/
# 3. Tag git criada
```

---

## 📦 Histórico (_history/)

Após cada release, arquivos são movidos para:

```
changes/_history/<versao>/
```

**Exemplo:**

```
_history/
├── 2.1.0/
│   ├── 2025-12-26_models_corrige-idparcela.md
│   └── 2025-12-26_routes_adiciona-autosync.md
├── 2.2.0/
│   └── 2025-12-28_hasher_adiciona-sha256.md
└── 3.0.0/
    └── 2026-01-15_models_migra-postgresql.md
```

---

## 🎯 Checklist ao Criar Mudança

Antes de commitar arquivo de mudança:

- [ ] Nome do arquivo segue convenção
- [ ] Descrição clara e completa
- [ ] Lista de arquivos modificados atualizada
- [ ] Seção de mudanças detalhada (Adicionado/Modificado/etc)
- [ ] Testes documentados com resultados
- [ ] Análise de impacto completa
- [ ] Instruções de rollback funcionais
- [ ] Links para issues/PRs relacionados
- [ ] Arquivo não é o TEMPLATE.md

---

## 💡 Dicas

1. **Seja detalhado** - Quanto mais detalhes, mais fácil o rollback
2. **Documente testes** - Inclua comandos e resultados
3. **Pense no futuro** - Alguém vai ler isso daqui 6 meses
4. **Use TEMPLATE.md** - Ele tem todas as seções necessárias
5. **Não delete histórico** - Mova para _history/ ao invés de deletar

---

## ❓ FAQ

**P: Posso deletar arquivos antigos?**  
R: Não delete. Eles são movidos automaticamente para _history/ durante releases.

**P: Preciso criar mudança para todo commit?**  
R: Não. Apenas para mudanças em **arquivos críticos** (models.py, hasher.py, etc).

**P: E se esquecer de criar mudança?**  
R: Pode criar manualmente copiando TEMPLATE.md e preenchendo.

**P: Posso editar mudança depois de criada?**  
R: Sim, até o release. Depois do release, fica em _history/ como histórico.

---

**Última atualização:** 27/12/2025  
**Versão deste README:** 1.0.0
