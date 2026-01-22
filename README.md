# 💰 FinUp - Sistema de Gestão Financeira

Sistema modular de controle financeiro pessoal com frontend Next.js e backend FastAPI.

## 🚀 Quick Start

```bash
# Iniciar sistema
./scripts/deploy/quick_start.sh

# Parar sistema
./scripts/deploy/quick_stop.sh
```

## 📁 Estrutura do Projeto

```
ProjetoFinancasV5/
├── app_dev/              # Aplicação (backend + frontend)
├── docs/                 # Documentação completa
├── scripts/              # Scripts auxiliares
├── temp/                 # Logs e PIDs temporários
└── _arquivos_historicos/ # Código legado
```

## 📚 Documentação

- **[Deploy](docs/deploy/)** - Infraestrutura e deploy
- **[Arquitetura](docs/architecture/)** - Design e decisões técnicas
- **[Features](docs/features/)** - Funcionalidades específicas
- **[Planejamento](docs/planning/)** - Sprints e roadmap

## 🌐 Acesso

- **App:** https://meufinup.com.br
- **API:** https://meufinup.com.br/api/v1
- **Docs:** https://meufinup.com.br/docs

## 👨‍💻 Desenvolvimento

Ver [docs/architecture/](docs/architecture/) para detalhes técnicos.

---

**Versão:** $(cat VERSION.md 2>/dev/null || echo "5.0")
