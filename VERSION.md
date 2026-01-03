# 🔢 Versão do Projeto

**Versão Atual:** `3.0.1`  
**Status:** `stable` 🟢  
**Data da Última Atualização:** 28/12/2025

---

## 📋 Informações da Versão

| Campo | Valor |
|-------|-------|
| **Versão Major** | 3 |
| **Versão Minor** | 0 |
| **Versão Patch** | 1 |
| **Status** | stable |
| **Nome do Release** | "Multi-Usuário e Preprocessadores" |

---

## 🎯 O que está incluído nesta versão

- ✅ Arquitetura modularizada com Flask Blueprints
- ✅ Sistema de deduplicação com hash FNV-1a 64-bit
- ✅ Auto-sync de parcelas integrado
- ✅ Sistema de audit log completo
- ✅ Interface admin para grupos e logos
- ✅ Sistema de versionamento e documentação de mudanças
- ✅ **Sistema multi-usuário com autenticação**
- ✅ **Preprocessadores modulares (BB, BTG, Mercado Pago)**
- ✅ **Base de padrões personalizada por usuário**

---

## 📖 Versionamento Semântico

Este projeto segue [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes - mudanças incompatíveis na API/banco
- **MINOR** (x.Y.0): Novas funcionalidades mantendo compatibilidade
- **PATCH** (x.y.Z): Correções de bugs e melhorias

---

## 🔄 Estados de Versão

| Estado | Descrição | Pode ser commitado? |
|--------|-----------|---------------------|
| `X.Y.Z` | **Estável** - Versão testada e aprovada | ✅ Sim |
| `X.Y.Z-dev` | **Desenvolvimento** - Mudanças em progresso | ❌ Não |
| `X.Y.Z-test` | **Teste** - Mudanças prontas para validação | ❌ Não |

---

## 📚 Histórico de Versões

| Versão | Data | Descrição |
|--------|------|-----------|
| **3.0.1** | 28/12/2025 | **Fix:** Preprocessador BB CSV corrigido + Base limpa para novos usuários |
| **3.0.0** | 27/12/2025 | **Major:** Arquitetura unificada de preprocessadores (BB, BTG, Mercado Pago) |
| **2.2.0** | 28/12/2025 | Sistema multi-usuário com Flask-Login + relacionamentos |
| **2.1.0** | 27/12/2025 | Sistema de versionamento e documentação implementado |
| **2.0.0** | 26/12/2025 | Modularização completa com Blueprints, produção estável |
| **1.x.x** | Dez/2025 | Versões iniciais monolíticas (ver BUGS.md para histórico) |

---

## 🔗 Ver Mais

- **Changelog completo:** [CHANGELOG.md](CHANGELOG.md)
- **Mudanças pendentes:** [changes/](changes/)
- **Contribuir:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Status do projeto:** [STATUSPROJETO.md](STATUSPROJETO.md)

---

## 🛠️ Gerenciar Versão

```bash
# Ver versão atual
python scripts/version_manager.py status

# Criar novo release
python scripts/version_manager.py release [major|minor|patch]

# Ver histórico git
git tag -l "v*" --sort=-version:refname
```

---

**Última verificação:** 28/12/2025 às 14:00 BRT
