# 📋 Tarefas Pendentes - Sistema Multi-Usuário

**Data:** 28/12/2025  
**Versão Atual:** 2.1.1  
**Status:** Parcialmente implementado

---

## ✅ CONCLUÍDO

### 1. Infraestrutura Multi-Usuário
- ✅ Modelo User criado com autenticação
- ✅ Colunas `user_id` adicionadas em todas as tabelas relevantes
- ✅ Sistema de padrões híbridos (BasePadrao com `user_id` nullable + `shared`)
- ✅ Blueprint auth completo (login/logout/register/gerenciar)
- ✅ Flask-Login configurado
- ✅ Script de migração automática
- ✅ 2 usuários criados (admin + Ana Beatriz)
- ✅ 4.153 transações migradas para admin
- ✅ Navbar com menu de usuário

---

## ⏳ PENDENTE - Fase 2: Scoping de Dados

### 2.1. Adicionar @login_required nos Blueprints

**Dashboard (`app/blueprints/dashboard/routes.py`):**
```python
from flask_login import login_required, current_user

@dashboard_bp.route('/')
@login_required  # ← ADICIONAR
def index():
    ...
```

**Aplicar em:**
- ✅ `dashboard.index()`
- ✅ `dashboard.transacoes()`
- ✅ `dashboard.transacao_detalhes()`
- ✅ `dashboard.get_transacoes_data()`

**Upload (`app/blueprints/upload/routes.py`):**
- ✅ Todas as rotas de upload

**Admin (`app/blueprints/admin/routes.py`):**
- ✅ Todas as rotas admin
- ✅ Adicionar verificação de role:
  ```python
  if current_user.role != 'admin':
      flash('Acesso negado', 'danger')
      return redirect(url_for('dashboard.index'))
  ```

---

### 2.2. Filtrar Queries por user_id

**Dashboard:**
```python
# ANTES
transacoes = db.query(JournalEntry).filter(...).all()

# DEPOIS
transacoes = db.query(JournalEntry).filter(
    JournalEntry.user_id == current_user.id,
    ...
).all()
```

**Arquivos a modificar:**
1. `app/blueprints/dashboard/routes.py`
   - `index()` - filtrar transações do dashboard
   - `transacoes()` - filtrar lista de transações
   - `get_transacoes_data()` - filtrar JSON API

2. `app/blueprints/upload/routes.py`
   - `processar_confirmados()` - atribuir `user_id` nas novas transações
   - Deduplicação deve verificar apenas transações do usuário

3. `app/blueprints/admin/routes.py`
   - Admin pode ver todos os usuários (adicionar seletor de usuário)
   - Ou filtrar por `current_user.id` se não for admin

---

### 2.3. Atualizar Classificador Automático

**`app/utils/classifiers/auto_classifier.py`:**

Lógica de padrões híbridos:
```python
# Buscar padrões do usuário OU padrões globais
padroes = session.query(BasePadrao).filter(
    or_(
        BasePadrao.user_id == user_id,  # Padrões do usuário
        BasePadrao.user_id == None,     # Padrões globais
        and_(
            BasePadrao.user_id != user_id,
            BasePadrao.shared == True   # Padrões compartilhados por outros
        )
    ),
    BasePadrao.status == 'ativo',
    BasePadrao.confianca == 'alta'
).all()
```

**Prioridade:**
1. Padrão do próprio usuário
2. Padrão global (user_id = NULL)
3. Padrão compartilhado por outro usuário

---

### 2.4. Atualizar Pattern Generator

**`app/utils/classifiers/pattern_generator.py`:**

Gerar padrões apenas com transações do usuário:
```python
def gerar_padroes(user_id):
    transacoes = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id,
        ...
    ).all()
    ...
```

Opção de compartilhar padrão:
```python
# No admin, botão "Compartilhar Padrão"
padrao.shared = True
db.commit()
```

---

### 2.5. Visão Consolidada (Opcional - Família)

**Nova rota:** `/dashboard/consolidado`

Permite ver transações agregadas de múltiplos usuários (opt-in).

**Implementação:**
1. Criar tabela `UserRelationship`:
   ```python
   class UserRelationship(Base):
       __tablename__ = 'user_relationships'
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, ForeignKey('users.id'))
       related_user_id = Column(Integer, ForeignKey('users.id'))
       permission = Column(String(20))  # view_only, view_edit
       created_at = Column(DateTime)
   ```

2. Rota consolidada:
   ```python
   @dashboard_bp.route('/consolidado')
   @login_required
   def consolidado():
       # IDs de usuários autorizados
       user_ids = [current_user.id]
       
       # Adiciona usuários relacionados
       relationships = db.query(UserRelationship).filter_by(
           user_id=current_user.id
       ).all()
       user_ids.extend([r.related_user_id for r in relationships])
       
       # Query consolidada
       transacoes = db.query(JournalEntry).filter(
           JournalEntry.user_id.in_(user_ids)
       ).all()
       
       return render_template('consolidado.html', transacoes=transacoes)
   ```

3. Interface para gerenciar relacionamentos:
   - `/auth/relationships`
   - Adicionar/remover acesso a outros usuários

---

## 🔧 Checklist de Implementação

### Prioridade ALTA (Essencial)
- [ ] Adicionar `@login_required` em todos os endpoints
- [ ] Filtrar queries do dashboard por `user_id`
- [ ] Atribuir `user_id` no upload de novas transações
- [ ] Atualizar deduplicação para verificar só transações do usuário
- [ ] Implementar lógica de padrões híbridos no classificador

### Prioridade MÉDIA (Importante)
- [ ] Adicionar controle de acesso admin nos routes
- [ ] Atualizar pattern generator para gerar padrões por usuário
- [ ] Testar isolamento completo de dados entre usuários
- [ ] Documentar sistema de padrões híbridos

### Prioridade BAIXA (Futura)
- [ ] Implementar visão consolidada (família)
- [ ] Interface para compartilhar padrões
- [ ] Gerenciar relacionamentos entre usuários
- [ ] Estatísticas multi-usuário para admin

---

## 📚 Documentação

### Arquitetura de Padrões Híbridos

**BasePadrao:** Aprendizado inteligente compartilhado

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `user_id` | NULL = global, INT = usuário específico | NULL, 1, 2 |
| `shared` | Se outro usuário compartilhou | True/False |

**Prioridade de classificação:**
1. **Padrão do usuário:** `user_id = current_user.id`
2. **Padrão global:** `user_id = NULL`
3. **Padrão compartilhado:** `user_id != current_user.id AND shared = True`

**Benefícios:**
- Novos usuários se beneficiam de padrões globais existentes
- Cada usuário pode customizar padrões específicos
- Opt-in para compartilhamento (privacidade)

---

## 🧪 Testes Necessários

### Teste 1: Isolamento de Dados
```bash
# Login como admin
curl -c cookies.txt -d "email=admin@financas.com&password=admin123" http://localhost:5001/auth/login

# Ver transações - deve mostrar 4.153
curl -b cookies.txt http://localhost:5001/dashboard/transacoes

# Login como Ana Beatriz
curl -c cookies2.txt -d "email=anabeatriz@financas.com&password=senha123" http://localhost:5001/auth/login

# Ver transações - deve mostrar 0
curl -b cookies2.txt http://localhost:5001/dashboard/transacoes
```

### Teste 2: Upload com user_id
1. Login como Ana Beatriz
2. Upload de arquivo Banco do Brasil
3. Verificar que transações têm `user_id = 2`
4. Login como admin - não deve ver essas transações

### Teste 3: Padrões Híbridos
1. Criar padrão como admin (user_id = 1)
2. Login como Ana Beatriz
3. Upload de transação similar
4. Verificar se classificou usando padrão global (user_id = NULL)

---

## 📝 Notas Importantes

1. **Segurança:** Todas as queries DEVEM filtrar por `user_id` para evitar vazamento de dados
2. **Performance:** Índices já criados em `user_id` de todas as tabelas
3. **Migração:** Backup criado em `financas.db.backup_*`
4. **Senhas Padrão:** ALTERAR após primeiro login!
5. **Padrões Globais:** 373 padrões mantidos sem `user_id` (compartilhados)

---

## 🔗 Referências

- [CONTRIBUTING.md](CONTRIBUTING.md) - Workflow de versionamento
- [changes/2025-12-28_sistema-multiusuario.md](changes/) - Documentação desta mudança
- [app/models.py](app/models.py) - Schema do banco atualizado
- [scripts/migrate_to_multiuser.py](scripts/migrate_to_multiuser.py) - Script de migração

---

**Última Atualização:** 28/12/2025  
**Responsável:** AI + Emanuel  
**Status:** Infraestrutura completa, aguardando scoping de queries
