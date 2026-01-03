# 🏗️ Estrutura 100% Autocontida - Dev e Prod

## Nova Arquitetura: Apps Completamente Independentes

Cada aplicação agora tem **TODOS** os seus recursos em sua própria pasta.

---

## 📦 App Dev - Completamente Autocontido

```
app_dev/                                    ← TUDO do DEV aqui
├── run.py                                  ← Script de execução DEV
├── requirements.txt                        ← Dependências DEV
├── venv/                                   ← Virtual env DEV
├── financas_dev.db                         ← Banco DEV
├── uploads_temp/                           ← Uploads DEV
├── static/                                 ← Static DEV
├── flask_session/                          ← Sessions DEV
├── templates/                              ← Templates DEV
│
├── backend/                                ← Backend Flask DEV
│   ├── __init__.py
│   ├── config_dev.py
│   ├── models.py
│   ├── models_flask.py
│   ├── extensions.py                      ✅ Copiado
│   ├── filters.py                         ✅ Copiado
│   │
│   ├── utils/                             ✅ Copiado do app/
│   │   ├── __init__.py
│   │   ├── hasher.py                      ✅ Hash de transações
│   │   ├── normalizer.py                  ✅ Normalização
│   │   ├── deduplicator.py                ✅ Detecção duplicatas
│   │   └── processors/
│   │       └── preprocessors/
│   │           ├── banco_do_brasil.py     ✅ Processador BB
│   │           ├── itau.py                ✅ Processador Itaú
│   │           ├── mercado_pago.py        ✅ Processador MP
│   │           ├── xp.py                  ✅ Processador XP
│   │           └── ...                    ✅ Todos os processadores
│   │
│   ├── api/                               ← API REST
│   │   └── blueprints/
│   │       ├── auth.py
│   │       ├── dashboard_dev.py
│   │       └── transactions.py
│   │
│   └── models/                            ← Models adicionais
│
└── frontend/                              ← Frontend React
    ├── package.json
    ├── vite.config.ts
    ├── node_modules/
    └── src/
```

### ✅ Dev É 100% Autocontido
- ✅ Tem seu próprio `run.py`
- ✅ Tem seu próprio `venv/`
- ✅ Tem seu próprio `requirements.txt`
- ✅ Tem todos os `utils/` (processadores)
- ✅ Tem seu próprio banco de dados
- ✅ Tem suas próprias pastas de recursos
- ✅ Tem templates
- ✅ NÃO depende de NADA fora de `app_dev/`

---

## 📦 App Prod - Completamente Autocontido

```
app/                                        ← TUDO do PROD aqui
├── run.py                                  ← Script de execução PROD
├── requirements.txt                        ← Dependências PROD
├── venv/                                   ← Virtual env PROD (opcional)
├── financas.db                             ← Banco PROD
├── uploads_temp/                           ← Uploads PROD
├── static/                                 ← Static PROD
├── flask_session/                          ← Sessions PROD
├── templates/                              ← Templates PROD
│
├── __init__.py
├── config.py
├── models.py
├── extensions.py
├── filters.py
│
├── utils/                                  ← Utils PROD
│   ├── __init__.py
│   ├── hasher.py
│   ├── normalizer.py
│   ├── deduplicator.py
│   └── processors/
│       └── preprocessors/
│           ├── banco_do_brasil.py
│           ├── itau.py
│           └── ...
│
└── blueprints/                             ← Blueprints Flask tradicional
    ├── admin/
    ├── auth/
    ├── dashboard/
    └── upload/
```

### ✅ Prod É 100% Autocontido
- ✅ Tem seu próprio `run.py`
- ✅ Tem seu próprio `venv/` (opcional)
- ✅ Tem seu próprio `requirements.txt`
- ✅ Tem todos os `utils/` (processadores)
- ✅ Tem seu próprio banco de dados
- ✅ Tem suas próprias pastas de recursos
- ✅ Tem templates
- ✅ NÃO depende de NADA fora de `app/`

---

## 🌳 Estrutura Root (Apenas Compartilhado)

```
ProjetoFinancasV3/                          ← Raiz do projeto
├── app_dev/                                ✅ App dev (autocontido)
├── app/                                    ✅ App prod (autocontido)
│
├── scripts/                                📝 Scripts de deploy/manage
│   ├── deploy_dev_to_prod.py
│   ├── rollback_deployment.py
│   ├── verify_separation.py
│   └── version_manager.py
│
├── docs/                                   📚 Documentação
│   ├── SEPARACAO_DEV_PROD.md
│   ├── WORKFLOW_DEPLOY.md
│   └── ...
│
├── backups_local/                          💾 Backups locais
├── data_samples/                           📊 Dados de exemplo
├── deployment_scripts/                     🚀 Scripts VM
├── tests/                                  🧪 Testes
│
├── deploy.sh                               🔧 Script auxiliar deploy
├── DEPLOY.md                               📖 Guia rápido
├── README.md                               📖 README principal
└── .gitignore                              🚫 Ignore file
```

---

## 🔄 Como Cada App Funciona

### App Dev
```bash
cd app_dev

# Ativar venv
source venv/bin/activate

# Instalar dependências (primeira vez)
pip install -r requirements.txt

# Executar
python run.py

# Tudo roda dentro de app_dev/
# - Banco: app_dev/financas_dev.db
# - Uploads: app_dev/uploads_temp/
# - Utils: app_dev/backend/utils/
# - Templates: app_dev/templates/
```

### App Prod
```bash
cd app

# Ativar venv (se existir)
source venv/bin/activate

# Instalar dependências (primeira vez)
pip install -r requirements.txt

# Executar
python run.py

# Tudo roda dentro de app/
# - Banco: app/financas.db
# - Uploads: app/uploads_temp/
# - Utils: app/utils/
# - Templates: app/templates/
```

---

## 📝 Imports Atualizados

### No App Dev (`app_dev/backend/`)
```python
# Antes (ERRADO - dependia de app/)
from app.utils.hasher import generate_hash

# Depois (CORRETO - autocontido)
from backend.utils.hasher import generate_hash
```

### No App Prod (`app/`)
```python
# Continua igual (já era correto)
from app.utils.hasher import generate_hash
```

---

## 🚀 Deploy Atualizado

### O Que É Copiado
```bash
./deploy.sh deploy
```

**Copia de `app_dev/` para `app/`:**
- ✅ `backend/` (código, utils, API)
- ✅ `templates/` (se houver mudanças)

**NÃO copia (cada app mantém o seu):**
- ❌ `financas_dev.db` → `financas.db`
- ❌ `uploads_temp/` → `uploads_temp/`
- ❌ `static/` → `static/`
- ❌ `flask_session/` → `flask_session/`
- ❌ `venv/` → `venv/`
- ❌ `run.py` → `run.py` (cada app tem o seu)

---

## 🔍 Validação de Separação Atualizada

```bash
./deploy.sh verify
```

**Verifica:**
1. ✅ `app_dev/` tem seus próprios utils
2. ✅ `app_dev/` tem seu próprio banco
3. ✅ `app_dev/` tem suas próprias pastas de recursos
4. ✅ `app/` tem seus próprios utils
5. ✅ `app/` tem seu próprio banco
6. ✅ `app/` tem suas próprias pastas de recursos
7. ✅ Nenhuma dependência cruzada

---

## 📊 Comparação: Antes vs Depois

### ANTES ❌ (Recursos Compartilhados)
```
ProjetoFinancasV3/
├── app_dev/
│   ├── backend/  (sem utils)
│   └── frontend/
├── app/
│   └── utils/     ← COMPARTILHADO
├── financas.db    ← COMPARTILHADO
├── uploads_temp/  ← COMPARTILHADO
├── templates/     ← COMPARTILHADO
├── static/        ← COMPARTILHADO
└── run.py         ← COMPARTILHADO
```

**Problemas:**
- ❌ Dev depende de app/ para utils
- ❌ Imports cruzados
- ❌ Não é possível mover app_dev/ para outro lugar
- ❌ Deploy complicado

### DEPOIS ✅ (100% Autocontido)
```
ProjetoFinancasV3/
├── app_dev/               ← Tudo do dev aqui
│   ├── backend/
│   │   └── utils/        ✅ Próprios
│   ├── frontend/
│   ├── financas_dev.db   ✅ Próprio
│   ├── uploads_temp/     ✅ Próprio
│   ├── templates/        ✅ Próprios
│   ├── static/           ✅ Próprio
│   ├── venv/             ✅ Próprio
│   └── run.py            ✅ Próprio
│
└── app/                   ← Tudo do prod aqui
    ├── utils/            ✅ Próprios
    ├── financas.db       ✅ Próprio
    ├── uploads_temp/     ✅ Próprio
    ├── templates/        ✅ Próprios
    ├── static/           ✅ Próprio
    └── run.py            ✅ Próprio
```

**Benefícios:**
- ✅ Dev 100% independente
- ✅ Prod 100% independente
- ✅ Pode mover qualquer pasta para outro servidor
- ✅ Deploy simples e seguro
- ✅ Zero dependências cruzadas

---

## 🎯 Como Usar

### Desenvolvimento
```bash
cd app_dev
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Produção
```bash
cd app
source venv/bin/activate  # ou usar venv global
pip install -r requirements.txt
python run.py
```

### Deploy
```bash
# Na raiz do projeto
./deploy.sh verify      # Verificar separação
./deploy.sh validate    # Validar código
./deploy.sh deploy      # Deploy
```

---

## 🔧 Configurações Atualizadas

### `app_dev/backend/config_dev.py`
```python
import os
from pathlib import Path

# Base path é app_dev/
BASE_DIR = Path(__file__).parent.parent

# Banco dentro de app_dev/
SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'financas_dev.db'}"

# Uploads dentro de app_dev/
UPLOAD_FOLDER = str(BASE_DIR / 'uploads_temp')

# Static dentro de app_dev/
STATIC_FOLDER = str(BASE_DIR / 'static')

# Sessions dentro de app_dev/
SESSION_FOLDER = str(BASE_DIR / 'flask_session')

# Templates dentro de app_dev/
TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
```

### `app/config.py`
```python
import os
from pathlib import Path

# Base path é app/
BASE_DIR = Path(__file__).parent

# Banco dentro de app/
SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'financas.db'}"

# Uploads dentro de app/
UPLOAD_FOLDER = str(BASE_DIR / 'uploads_temp')

# Static dentro de app/
STATIC_FOLDER = str(BASE_DIR / 'static')

# Sessions dentro de app/
SESSION_FOLDER = str(BASE_DIR / 'flask_session')

# Templates dentro de app/
TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
```

---

## ✅ Checklist de Separação Completa

### App Dev
- [x] Tem `backend/utils/` completo
- [x] Tem `financas_dev.db`
- [x] Tem `uploads_temp/`
- [x] Tem `static/`
- [x] Tem `flask_session/`
- [x] Tem `templates/`
- [x] Tem `venv/`
- [x] Tem `run.py`
- [x] Tem `requirements.txt`
- [x] Config usa paths relativos a `app_dev/`

### App Prod
- [x] Tem `utils/` completo
- [x] Tem `financas.db`
- [x] Tem `uploads_temp/`
- [x] Tem `static/`
- [x] Tem `flask_session/`
- [x] Tem `templates/`
- [x] Tem `run.py`
- [x] Tem `requirements.txt`
- [x] Config usa paths relativos a `app/`

### Validação
- [x] Nenhum import de `app_dev/` para fora
- [x] Nenhum import de `app/` para fora
- [x] Nenhum path absoluto para raiz
- [x] Cada app roda independentemente

---

## 🎉 Resultado Final

**Agora você pode:**
- ✅ Mover `app_dev/` para qualquer lugar
- ✅ Mover `app/` para qualquer lugar
- ✅ Cada app funciona isoladamente
- ✅ Deploy copia apenas código necessário
- ✅ Zero dependências entre apps
- ✅ Zero recursos compartilhados (exceto scripts de deploy)

**Separação física e lógica 100% completa!** 🚀

