# 🔧 Configuração Git - Guia Completo

## 📋 Status Atual

### ✅ O que está CORRETO:
- **GitIgnore configurado corretamente** - todos os dados sensíveis ignorados
- **Credential helper ativo** - `credential.helper=osxkeychain` (macOS Keychain)
- **Ambos os apps no Git** - app/ e app_dev/ com código-fonte commitado
- **Recursos sensíveis ignorados** - databases, uploads, sessions, venv, node_modules

### ⚠️ O que precisa ser CONFIGURADO:
- **Nome de usuário Git** - não configurado
- **Email Git** - não configurado
- **Repositório remoto** - não configurado

---

## 🚀 Configuração Obrigatória (1 vez por máquina)

### 1. Configurar Identidade Git

```bash
# Configurar nome (global - todos os projetos)
git config --global user.name "Seu Nome Completo"

# Configurar email (global - todos os projetos)
git config --global user.email "seu.email@exemplo.com"

# OU configurar apenas para este projeto (local)
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
git config user.name "Seu Nome Completo"
git config user.email "seu.email@exemplo.com"
```

### 2. Configurar Credential Helper (Salvar Senha)

**macOS (Keychain) - JÁ CONFIGURADO ✅:**
```bash
git config --global credential.helper osxkeychain
```

**Linux:**
```bash
# Opção 1: Cache (15 minutos por padrão)
git config --global credential.helper cache

# Opção 2: Cache com timeout customizado (ex: 1 hora = 3600 segundos)
git config --global credential.helper 'cache --timeout=3600'

# Opção 3: Store (permanente - armazena em texto plano no disco)
# ⚠️ ATENÇÃO: Menos seguro, mas mais conveniente
git config --global credential.helper store
```

**Windows:**
```bash
git config --global credential.helper wincred
```

### 3. Configurar Repositório Remoto

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3

# Adicionar repositório remoto
# HTTPS (mais comum - pede senha na primeira vez)
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git

# OU SSH (requer configuração de chave SSH)
git remote add origin git@github.com:SEU-USUARIO/SEU-REPOSITORIO.git

# Verificar se foi adicionado
git remote -v
```

---

## 📤 Fazendo Push pela Primeira Vez

### Com HTTPS (Pedirá senha uma vez):

```bash
# Push inicial
git push -u origin main  # ou master, dev, etc

# O macOS Keychain salvará automaticamente as credenciais
# Próximos pushes não pedirão senha
```

### Com SSH (Requer setup de chave):

```bash
# 1. Gerar chave SSH (se não tiver)
ssh-keygen -t ed25519 -C "seu.email@exemplo.com"

# 2. Adicionar chave ao ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Copiar chave pública
cat ~/.ssh/id_ed25519.pub
# Colar no GitHub: Settings > SSH and GPG keys > New SSH key

# 4. Push
git push -u origin main
```

---

## 🔍 Verificação do GitIgnore

### O que ESTÁ no Git (código-fonte):

```
✅ app/
   ✅ __init__.py, models.py, config.py
   ✅ blueprints/
   ✅ utils/ (processadores)
   ✅ templates/
   ✅ static/ (CSS, JS, logos padrão)
   ✅ run.py, requirements.txt
   ❌ financas.db (ignorado)
   ❌ uploads_temp/ (ignorado)
   ❌ flask_session/ (ignorado)
   ❌ venv/ (ignorado)

✅ app_dev/
   ✅ backend/ (completo)
   ✅ frontend/ (React completo)
   ✅ templates/
   ✅ run.py, requirements.txt
   ❌ financas_dev.db (ignorado)
   ❌ uploads_temp/ (ignorado)
   ❌ flask_session/ (ignorado)
   ❌ venv/ (ignorado)
   ❌ frontend/node_modules/ (ignorado)
   ❌ frontend/dist/ (ignorado)

✅ scripts/ (deploy, rollback, verify)
✅ docs/ (documentação completa)
❌ backups_local/ (ignorado)
❌ data_samples/ (ignorado)
```

### Verificar arquivos ignorados:

```bash
# Ver o que o Git está ignorando
git status --ignored

# Ver o que ESTÁ no Git
git ls-files

# Verificar se algum arquivo importante está ignorado
git check-ignore -v app_dev/backend/models.py
git check-ignore -v app/config.py
```

---

## 🎯 Workflow Completo de Commit e Push

### 1. Fazer Mudanças

```bash
# Editar arquivos...
```

### 2. Verificar Mudanças

```bash
git status
git diff
```

### 3. Adicionar ao Stage

```bash
# Adicionar tudo
git add .

# OU adicionar específico
git add app/models.py app_dev/backend/config_dev.py
```

### 4. Commitar

```bash
git commit -m "feat: Descrição clara da mudança"
```

### 5. Push (Primeira vez)

```bash
# Primeira vez (cria upstream)
git push -u origin main

# ⚠️ Se pedir senha e você estiver no macOS:
# 1. Digite usuário GitHub
# 2. Digite token de acesso pessoal (não a senha da conta!)
#    Criar token em: https://github.com/settings/tokens
# 3. O Keychain salvará automaticamente
```

### 6. Pushes Seguintes

```bash
# Próximos pushes (não pedirá senha)
git push
```

---

## 🔐 Token de Acesso Pessoal (GitHub)

**⚠️ IMPORTANTE:** GitHub não aceita mais senha da conta para HTTPS!

### Criar Token:

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** > **"Generate new token (classic)"**
3. Configure:
   - **Note:** "ProjetoFinancas - Push/Pull"
   - **Expiration:** 90 days (ou No expiration)
   - **Scopes:** Marque `repo` (acesso total aos repos)
4. Clique em **"Generate token"**
5. **COPIE O TOKEN** (só aparece uma vez!)

### Usar Token no Push:

```bash
git push

# Quando pedir:
Username: seu-usuario-github
Password: cole-o-token-aqui (não a senha da conta!)
```

**O macOS Keychain salvará automaticamente!** 🎉

---

## 👥 Configuração para Múltiplos Usuários

### Usuário 1 (Você):

```bash
git config user.name "Emanuel Guerra"
git config user.email "emangue@exemplo.com"
# Push pela primeira vez → senha salva no Keychain
```

### Usuário 2 (Colaborador):

```bash
# Na máquina dele:
git clone https://github.com/SEU-USUARIO/ProjetoFinancasV3.git
cd ProjetoFinancasV3

# Configurar identidade dele
git config user.name "Nome do Colaborador"
git config user.email "colaborador@exemplo.com"

# No primeiro push, ele digita credenciais dele
# O sistema operacional dele salvará automaticamente
```

**Cada usuário terá suas próprias credenciais salvas localmente!**

---

## 🐛 Troubleshooting

### "Permission denied" ao fazer push

```bash
# Verificar se tem permissão no repo
# Adicionar colaborador no GitHub: Settings > Collaborators
```

### "Fatal: not a git repository"

```bash
# Garantir que está no diretório certo
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3
pwd
```

### Push pedindo senha toda vez

```bash
# Verificar credential helper
git config --global credential.helper

# Se vazio, configurar:
git config --global credential.helper osxkeychain  # macOS
```

### "Support for password authentication was removed"

```bash
# SOLUÇÃO: Usar token de acesso pessoal (não senha)
# Ver seção "Token de Acesso Pessoal" acima
```

### Verificar configurações atuais

```bash
# Ver todas as configs
git config --list

# Ver configs globais (todos os projetos)
git config --global --list

# Ver configs locais (só este projeto)
git config --local --list
```

---

## ✅ Checklist Final

**Antes do primeiro push:**

- [ ] Nome de usuário Git configurado
- [ ] Email Git configurado
- [ ] Credential helper configurado
- [ ] Repositório remoto adicionado
- [ ] Token de acesso pessoal gerado (se HTTPS)
- [ ] OU chave SSH configurada (se SSH)
- [ ] Verificar que gitignore está correto (`git status`)

**No primeiro push:**

- [ ] `git push -u origin main`
- [ ] Digitar usuário GitHub
- [ ] Digitar token (ou senha SSH)
- [ ] Verificar que credenciais foram salvas

**Nos próximos pushes:**

- [ ] `git push` → deve funcionar sem pedir senha! 🎉

---

## 📚 Comandos Úteis

```bash
# Ver status do repositório
git status

# Ver histórico de commits
git log --oneline -10

# Ver branches
git branch -a

# Ver remotes configurados
git remote -v

# Ver configurações de credenciais
git config --list | grep credential

# Ver arquivos ignorados
git status --ignored

# Limpar cache de credenciais (se precisar resetar)
git credential-osxkeychain erase  # macOS
```

---

## 🎯 Resumo Executivo

**Para funcionar 100% com credenciais salvas:**

1. **Configure identidade** (1 vez):
   ```bash
   git config --global user.name "Seu Nome"
   git config --global user.email "seu@email.com"
   ```

2. **Credential helper já está ativo** ✅:
   - macOS: `credential.helper=osxkeychain`

3. **Adicione repositório remoto** (1 vez):
   ```bash
   git remote add origin https://github.com/usuario/repo.git
   ```

4. **Primeiro push com token**:
   ```bash
   git push -u origin main
   # Usuario: seu-usuario-github
   # Senha: seu-token-de-acesso-pessoal
   ```

5. **Próximos pushes** → automático! 🚀

**Para outros usuários:** Mesmo processo na máquina deles!

---

## 📞 Suporte

Se continuar com problemas:
1. Verificar: `git config --list`
2. Verificar: `git remote -v`
3. Testar: `git push -v` (modo verbose)
4. Logs: `GIT_TRACE=1 git push` (debug completo)

---

**Última atualização:** 2 de Janeiro de 2026
