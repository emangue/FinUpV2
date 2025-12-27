# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.1.0] - 27/12/2025

### 🎉 Adicionado
- **Sistema de versionamento integrado**
  - Arquivo `VERSION.md` para controle de versão global
  - Campo `__version__` em `app/__init__.py`
  - Docstrings versionados em arquivos críticos
  
- **Automação de documentação de mudanças**
  - Script `scripts/version_manager.py` para gerenciar ciclo de vida das versões
  - Pasta `changes/` para documentação individual de mudanças
  - Template padronizado para documentação (`changes/TEMPLATE.md`)
  
- **Instruções persistentes para AI**
  - `.github/copilot-instructions.md` com workflow detalhado
  - `.copilot-rules.md` com resumo executivo
  - `CONTRIBUTING.md` com guia completo de contribuição
  
- **Git hooks para validação**
  - Pre-commit hook impedindo commit de versões `-dev`/`-test`
  - Validação automática de documentação obrigatória
  
- **Integração no startup do Flask**
  - Exibição de versão no console ao iniciar `run.py`
  - Avisos visuais para versões em desenvolvimento

### 🔄 Modificado
- `app/__init__.py` agora inclui `__version__ = "2.1.0"`
- `run.py` com validação e exibição de versão no startup

---

## [2.0.0] - 26/12/2025

### 🎉 Adicionado
- **Modularização completa com Flask Blueprints**
  - Blueprint `dashboard` para rotas principais
  - Blueprint `upload` para processamento de arquivos
  - Blueprint `admin` para configurações e gestão
  
- **Sistema de gestão de logos**
  - Modelo `EstabelecimentoLogo` no banco
  - Interface admin para upload e gerenciamento
  - Exibição de logos na tabela de transações
  
- **Sistema de grupos de configuração**
  - Modelo `GrupoConfig` para categorização
  - CRUD completo na interface admin
  
- **Audit Log completo**
  - Registro automático de todas operações críticas
  - Rastreabilidade de uploads, edições e exclusões

### 🐛 Corrigido
- **IdParcela não sendo salvo** (Bug #1 - 27/12/2025)
  - Campo `IdParcela` adicionado na criação de `JournalEntry`
  - Rastreamento de parcelas funcionando corretamente
  
- **BaseParcelas não atualizando** (Bug #2 - 27/12/2025)
  - Auto-sync implementado após uploads
  - Contratos órfãos limpos automaticamente
  
- **Query N+1 em faturas parceladas** (Bug #3 - 27/12/2025)
  - Substituído loop individual por bulk insert
  - Performance melhorada de ~500ms para <50ms
  
- **Colisão de hash VPD** (Bug #4 - 27/12/2025)
  - Algoritmo de hash trocado para FNV-1a 64-bit
  - Validação adicional com normalização de dados
  
- **Duplicatas de estornos não sendo detectadas** (Bug #5 - 27/12/2025)
  - Lógica ajustada para considerar valores negativos
  - Tratamento especial para transações de estorno
  
- **Erro ao fazer upload em mês vazio** (Bug #6 - 27/12/2025)
  - Verificação de segurança adicionada
  - Proteção contra SQL injection em filtros de data

### 🔄 Modificado
- Estrutura de pastas reorganizada com blueprints modulares
- `app/utils/hasher.py` com algoritmo FNV-1a 64-bit
- `app/utils/processors/fatura_cartao.py` com bulk insert otimizado
- URLs das rotas adaptadas para estrutura de blueprints

### 📚 Documentação
- `BUGS.md` atualizado com 6 bugs resolvidos e detalhes técnicos
- `STATUSPROJETO.md` marcando versão 2.0.0 como produção completa
- `MODULARIZACAO.md` documentando migração para blueprints
- `ESTRUTURA_PROJETO.md` com arquitetura modular atualizada

---

## [1.x.x] - Dezembro/2025

### Histórico Inicial
Versões iniciais com arquitetura monolítica. Para detalhes históricos, consulte:
- [BUGS.md](BUGS.md) - Histórico de bugs resolvidos
- [STATUSPROJETO.md](STATUSPROJETO.md) - Evolução do projeto

---

## 🏷️ Tipos de Mudanças

- **Adicionado** - para novas funcionalidades
- **Modificado** - para mudanças em funcionalidades existentes
- **Depreciado** - para funcionalidades que serão removidas em breve
- **Removido** - para funcionalidades removidas
- **Corrigido** - para correções de bugs
- **Segurança** - para correções de vulnerabilidades

---

## 🔗 Links de Comparação

- [2.1.0](https://github.com/seu-usuario/ProjetoFinancasV3/releases/tag/v2.1.0) - 2025-12-27
- [2.0.0](https://github.com/seu-usuario/ProjetoFinancasV3/releases/tag/v2.0.0) - 2025-12-26

---

**Nota:** Mudanças individuais em progresso são documentadas em [changes/](changes/) antes de serem agregadas aqui durante releases.
