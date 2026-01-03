# 💰 Sistema de Gestão Financeira v3.0.1

<div align="center">

![Status](https://img.shields.io/badge/status-em_produção-success)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-lightgrey)
![License](https://img.shields.io/badge/license-privado-red)

**Sistema completo de gestão financeira pessoal com processamento automático de extratos e categorização inteligente**

🌐 **Produção:** https://finup.emangue.com.br

</div>

---

## ✨ Funcionalidades

### 📊 Dashboard Financeiro
- Visualização consolidada de transações
- Filtros por período, categoria, estabelecimento
- Soma automática de valores filtrados
- Gráficos e estatísticas (em desenvolvimento)

### 📤 Upload Inteligente
- **Processamento automático** de múltiplos formatos:
  - 🏦 Banco do Brasil (CSV, OFX)
  - 🏦 Itaú (CSV, XLS)
  - 🏦 XP Investimentos (XLSX)
  - 💳 Mercado Pago (XLSX)
  - 💳 Cartões de crédito (CSV, OFX)
- **Detecção de duplicatas** (hash FNV-1a de 64 bits)
- **Normalização automática** de estabelecimentos
- **Validação em 3 etapas:** Upload → Validação → Confirmação

### 🤖 Classificação Automática
- Machine learning baseado em padrões históricos
- 373 padrões pré-configurados
- Confiança alta/média/baixa
- Sugestões de grupo, subgrupo e tipo de gasto

### 👥 Multi-usuário
- Sistema completo de autenticação (Flask-Login + bcrypt)
- Isolamento total de dados por usuário (100% user_id)
- Roles: Admin e User
- Gestão de perfis e permissões

### 📦 Gestão de Parcelas
- Controle de compras parceladas
- Acompanhamento de contratos ativos/finalizados
- Vinculação automática transação ↔ parcela

### 🔍 Administração Avançada
- Gerenciamento de grupos e subgrupos
- Marcações e classificações customizadas
- Logos personalizados para estabelecimentos
- Padrões de classificação editáveis

---

## 🏗️ Arquitetura

### Stack Tecnológico

```
Frontend:  Bootstrap 5.3 + Jinja2 + JavaScript
Backend:   Flask 3.0 + SQLAlchemy 2.0 + Python 3.12
Database:  SQLite 3.45
Servidor:  Nginx + Gunicorn
Deploy:    Hostinger VPS (Ubuntu 24.04)
SSL:       Let's Encrypt (renovação automática)
```

### Estrutura de Diretórios

```
📦 ProjetoFinancasV3
 ├── 📂 app/                  # Código principal Flask
 │   ├── 📂 blueprints/       # Módulos (auth, admin, dashboard, upload)
 │   └── 📂 utils/            # Utilitários compartilhados
 ├── 📂 templates/            # Templates Jinja2
 ├── 📂 static/               # CSS, JS, logos
 ├── 📂 scripts/              # Scripts de manutenção
 ├── 📂 docs/                 # Documentação completa
 ├── 📂 deployment_scripts/   # Deploy automatizado
 ├── 📂 tests/                # Testes automatizados
 └── 📄 run.py                # Entry point
```

📖 **Documentação completa:** [docs/ESTRUTURA_ORGANIZADA.md](docs/ESTRUTURA_ORGANIZADA.md)

---

## 🚀 Quick Start

### 1. Pré-requisitos

```bash
Python 3.12+
pip (gerenciador de pacotes Python)
venv (ambiente virtual)
```

### 2. Instalação Local

```bash
# Clonar repositório (se aplicável)
git clone <repo_url>
cd ProjetoFinancasV3

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados (primeira vez)
python import_base_inicial.py
```

### 3. Executar Aplicação

```bash
# Desenvolvimento
python run.py

# Produção (via Gunicorn)
gunicorn --bind 127.0.0.1:5000 --workers 2 run:app
```

Acesse: http://localhost:5000

### 4. Login Padrão

```
Email: admin@exemplo.com (ou conforme seu banco)
Senha: (configurada no banco de dados)
```

---

## 📦 Deployment

### Novo Sistema de Deploy (Recomendado)

```bash
# 1. Validar mudanças
./deploy.sh validate

# 2. Deploy completo (com backup automático)
./deploy.sh deploy

# 3. Rollback se necessário
./deploy.sh rollback
```

**Funcionalidades:**
- ✅ Validações automáticas (syntax, imports, security)
- ✅ Comparação detalhada dev vs prod
- ✅ Backup automático antes de deploy
- ✅ Confirmação interativa
- ✅ Rollback em um comando

📖 **Guias completos:**
- [DEPLOY.md](DEPLOY.md) - Guia rápido
- [docs/WORKFLOW_DEPLOY.md](docs/WORKFLOW_DEPLOY.md) - Workflow completo
- [docs/DEPLOY_EXEMPLO.md](docs/DEPLOY_EXEMPLO.md) - Exemplos visuais
- [scripts/README.md](scripts/README.md) - Referência de scripts

### Deploy para Hostinger VPS (Legado)

```bash
# Deploy completo (primeira vez)
./deployment_scripts/deploy_hostinger.sh

# Deploy incremental (atualizações)
python deployment_scripts/deploy.py --target production \
  --vm-user root --vm-host 148.230.78.91

# Verificar antes de deployar
python deployment_scripts/deploy.py --check-only
```

### Requisitos da VM

- **OS:** Ubuntu 24.04 LTS
- **RAM:** Mínimo 2GB (recomendado 4GB+)
- **CPU:** Mínimo 1 core (recomendado 2+)
- **Disco:** Mínimo 5GB disponível

📖 **Guia completo de deployment:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🔐 Segurança

### Camadas de Proteção

✅ **Firewall (UFW):** Portas 22, 80, 443 abertas, resto bloqueado  
✅ **Fail2ban:** Proteção contra brute force (SSH + Nginx)  
✅ **SSL/TLS 1.3:** Certificado Let's Encrypt (renovação automática)  
✅ **SSH Keys:** Autenticação por chave RSA 4096 bits  
✅ **Bcrypt:** Hash de senhas com 12 rounds  
✅ **CSRF Protection:** Flask-WTF habilitado  
✅ **Headers de Segurança:** HSTS, X-Frame-Options, CSP  
✅ **Isolamento de Usuários:** 100% user_id nas transações  

### Conformidade

- ✅ LGPD: Isolamento de dados por usuário
- ✅ PCI DSS: Não armazena dados de cartão
- ✅ OWASP Top 10: Protegido contra principais vulnerabilidades

📖 **Análise completa de segurança:** [docs/SECURITY_AND_DEPLOYMENT.md](docs/SECURITY_AND_DEPLOYMENT.md)

---

## 💾 Backup e Recuperação

### Backup Automático

```bash
# Configurado via cron (diariamente às 3h AM)
0 3 * * * /opt/financial-app/backup.sh

# Retenção: 30 dias
# Compressão: gzip (77% economia)
# Localização: /backups/financial-app/
```

### Backup Manual

```bash
# Criar backup
python scripts/backup_database.py --output backups_local/manual_$(date +%Y%m%d).db.gz

# Restaurar backup
python scripts/backup_database.py restore backups_local/manual_20260102.db.gz

# Verificar integridade
python scripts/database_health_check.py
```

---

## 📊 Status do Projeto

### Versão Atual: 3.0.1 (Janeiro 2026)

- ✅ **Produção:** https://finup.emangue.com.br
- ✅ **Usuários:** 2 ativos
- ✅ **Transações:** 4,153 importadas
- ✅ **Padrões:** 373 classificações
- ✅ **Uptime:** 99.9% (monitorado)
- ✅ **Health Score:** 80/100

### Próximas Funcionalidades

- [ ] Dashboard com gráficos (Chart.js)
- [ ] Exportação de relatórios (PDF, Excel)
- [ ] API REST para integração
- [ ] App mobile (React Native)
- [ ] Notificações por email

📖 **Roadmap completo:** [docs/STATUSPROJETO.md](docs/STATUSPROJETO.md)

---

## 🧪 Testes

### Testes Automatizados

```bash
# Rodar todos os testes
python tests/deployment_health_check.py

# Health check do banco
python scripts/database_health_check.py

# Verificar mudanças
python deployment_scripts/deployment_diff.py
```

### Cobertura de Testes

- ✅ 12 testes de capabilities (100% passing)
- ✅ Verificação de integridade do BD
- ✅ Validação de estrutura de arquivos
- ✅ Testes de deployment

---

## 📚 Documentação

### Principais Documentos

- 📖 [SECURITY_AND_DEPLOYMENT.md](docs/SECURITY_AND_DEPLOYMENT.md) - **Segurança completa**
- 📖 [ESTRUTURA_ORGANIZADA.md](docs/ESTRUTURA_ORGANIZADA.md) - Estrutura do projeto
- 📖 [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guia de deployment
- 📖 [CHANGELOG.md](docs/CHANGELOG.md) - Histórico de versões
- 📖 [VERSIONAMENTO.md](docs/VERSIONAMENTO.md) - Sistema de versionamento
- 📖 [BUGS.md](docs/BUGS.md) - Issues conhecidos

### Documentação Técnica

- 📖 [ARQUITETURA_COMPONENTES.md](docs/ARQUITETURA_COMPONENTES.md) - Arquitetura detalhada
- 📖 [MODULARIZACAO.md](docs/MODULARIZACAO.md) - Histórico de refatoração
- 📖 [CONTRIBUTING.md](docs/CONTRIBUTING.md) - Guia de contribuição

---

## 🛠️ Ferramentas e Scripts

### Scripts Principais

```bash
# Backup e restauração
python scripts/backup_database.py auto|restore|list

# Health check
python scripts/database_health_check.py

# Versionamento
python scripts/version_manager.py start|finish|rollback <arquivo>

# Deployment
python deployment_scripts/deploy.py [--check-only] [--target production]

# Análise
python scripts/analisar_transacoes.py
python scripts/buscar_similares.py
```

---

## 🤝 Contribuindo

### Workflow de Desenvolvimento

1. **Criar branch** para nova feature
2. **Versionar mudanças** com `version_manager.py`
3. **Testar localmente** com `python run.py`
4. **Rodar health check** antes de commit
5. **Fazer commit** (hook pre-commit valida versionamento)
6. **Deploy para staging** (se disponível)
7. **Deploy para produção** após validação

### Padrões de Código

- **Python:** PEP 8 (autopep8, black)
- **HTML/Jinja2:** Indentação 2 espaços
- **JavaScript:** ES6+, sem jQuery
- **CSS:** BEM methodology (recomendado)

📖 **Guia completo:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 📞 Suporte e Contato

### Em caso de problemas

1. **Verificar logs:**
   ```bash
   # Logs da aplicação
   tail -f /opt/financial-app/logs/app.log
   
   # Logs do sistema
   journalctl -u financial-app -f
   ```

2. **Health check:**
   ```bash
   python scripts/database_health_check.py
   ```

3. **Consultar documentação:**
   - [docs/BUGS.md](docs/BUGS.md) - Problemas conhecidos
   - [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Troubleshooting

### Recursos

- 🌐 **Produção:** https://finup.emangue.com.br
- 📧 **Email:** emangue@emangue.com.br
- 📂 **Docs:** `/docs/` (este repositório)

---

## 📄 Licença

**Projeto Privado** - Todos os direitos reservados © 2026

Este é um projeto pessoal de gestão financeira. Código fonte não é público.

---

## 🙏 Agradecimentos

- **Flask** - Framework web robusto e flexível
- **SQLAlchemy** - ORM poderoso para Python
- **Bootstrap** - Framework CSS responsivo
- **Let's Encrypt** - SSL gratuito e confiável
- **Hostinger** - Hospedagem VPS confiável

---

<div align="center">

**Desenvolvido com ❤️ por Emanuel**

*Última atualização: Janeiro 2026*

</div>
