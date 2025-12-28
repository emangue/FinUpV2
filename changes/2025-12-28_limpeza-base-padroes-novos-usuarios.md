# Feat: Base de Padrões Limpa para Novos Usuários

**Data:** 28/12/2025  
**Tipo:** Feature/Refactor  
**Impacto:** Médio - Melhoria da experiência de novos usuários  
**Versão:** 3.0.1

---

## 🎯 Objetivo

Garantir que cada novo usuário comece com uma base de padrões completamente vazia, permitindo que o sistema aprenda e construa padrões específicos para o comportamento financeiro individual de cada usuário.

---

## 🔄 Mudança Implementada

### Conceito Anterior
- Novos usuários poderiam herdar ou ver padrões globais
- Base de padrões potencialmente pré-populada
- Risco de classificações inadequadas baseadas em outros usuários

### Conceito Atual
- Cada usuário inicia com bases completamente vazias
- Padrões são construídos organicamente a partir das primeiras transações
- Aprendizado personalizado desde o início

---

## 🗄️ Bases Afetadas

### 1. BasePadrao (Padrões de Classificação)
- **Tabela:** `base_padroes`
- **Escopo:** Por usuário (`user_id`)
- **Função:** Armazena padrões aprendidos de estabelecimentos e categorias
- **Exemplo:** "Netflix → Ajustável - Assinaturas" com confiança 95%

### 2. BaseParcelas (Controle de Parcelamentos)
- **Tabela:** `base_parcelas`
- **Escopo:** Por usuário (`user_id`)
- **Função:** Controla compras parceladas e parcelas pagas
- **Exemplo:** "Amazon - 3x de R$ 50,00 → 2/3 pagas"

### 3. BaseMarcacao (Validações de Categorias)
- **Tabela:** `base_marcacoes`
- **Escopo:** Global (sem `user_id`)
- **Função:** Define combinações válidas de Grupo/Subgrupo/TipoGasto
- **Status:** Compartilhada entre todos os usuários (não limpa)

---

## 🧹 Limpeza Realizada

### Usuário: Ana Beatriz (user_id=2)

```python
from app.models import BasePadrao, BaseParcelas, get_db_session

db = get_db_session()

# Limpeza realizada
padroes_removidos = 373  # BasePadrao
parcelas_removidas = 0   # BaseParcelas (já estava vazia)

db.query(BasePadrao).filter_by(user_id=2).delete()
db.query(BaseParcelas).filter_by(user_id=2).delete()
db.commit()
```

**Resultado:**
- ✅ 373 padrões aprendidos removidos
- ✅ 0 parcelas (já estava limpo)
- ✅ Ana Beatriz agora tem base completamente vazia

---

## 📊 Comportamento Esperado

### Primeira Transação Classificada
1. Usuário importa primeira transação: "Netflix R$ 39,90"
2. Sistema não encontra padrões existentes
3. Transação vai para "Não Classificado"
4. Usuário revisa e marca: "Ajustável - Assinaturas"
5. Sistema **cria primeiro padrão** para este usuário

### Após Múltiplas Classificações
1. Netflix aparece novamente
2. Sistema encontra padrão aprendido (1/1 = 100% confiança)
3. Classifica automaticamente
4. Padrão é reforçado (2/2 = confiança mantida)

### Evolução Natural
- **0-10 transações:** Maioria não classificada, muita revisão manual
- **10-50 transações:** Padrões começam a emergir, 30-50% automático
- **50-200 transações:** Boa cobertura, 70-80% automático
- **200+ transações:** Alta precisão, 85-95% automático

---

## 🎓 Vantagens do Modelo Personalizado

### 1. Relevância
- Padrões refletem **exatamente** os gastos do usuário
- Sem ruído de comportamento de outros usuários
- Estabelecimentos e valores específicos

### 2. Privacidade
- Dados financeiros isolados por usuário
- Padrões não compartilhados
- Aprendizado independente

### 3. Qualidade
- Alta precisão após período de aprendizado
- Menos falsos positivos
- Adaptação a mudanças de comportamento

---

## 🔧 Implementação Técnica

### Models Envolvidos

```python
class BasePadrao(Base):
    """Padrões de classificação - Separados por usuário"""
    __tablename__ = 'base_padroes'
    
    user_id = Column(Integer, ForeignKey('users.id'), 
                     nullable=False, index=True)  # ✅ Obrigatório
    padrao_estabelecimento = Column(Text, nullable=False)
    grupo_sugerido = Column(String(100))
    confianca = Column(String(10))  # alta/media/baixa
    contagem = Column(Integer)  # Número de vezes visto
    # ...

class BaseParcelas(Base):
    """Compras parceladas - Separadas por usuário"""
    __tablename__ = 'base_parcelas'
    
    user_id = Column(Integer, ForeignKey('users.id'), 
                     nullable=True, index=True)  # ✅ Nullable para migração
    id_parcela = Column(String(64), unique=True)
    estabelecimento_base = Column(Text, nullable=False)
    # ...
```

### Filtros nas Queries

```python
# Carregar padrões do usuário logado
padroes = db.query(BasePadrao).filter_by(user_id=current_user.id).all()

# Carregar parcelas do usuário logado
parcelas = db.query(BaseParcelas).filter_by(user_id=current_user.id).all()
```

---

## 📝 Procedimento para Novos Usuários

### Criação de Usuário

```python
# Script: scripts/migrate_to_multiuser.py --create-user
novo_user = User(
    nome="Novo Usuário",
    email="novo@financas.com",
    password_hash=generate_password_hash("senha")
)
db.add(novo_user)
db.commit()

# ✅ Bases automaticamente vazias:
# - BasePadrao: 0 registros (user_id=novo_user.id)
# - BaseParcelas: 0 registros (user_id=novo_user.id)
```

### Primeira Importação
1. Usuário faz login
2. Faz upload de extrato (CSV/OFX)
3. Sistema classifica com padrões **vazios**
4. Todas transações vão para revisão
5. Usuário classifica manualmente
6. Sistema **cria padrões** pela primeira vez

---

## 🧪 Validação

### Teste de Limpeza
```bash
python -c "from app.models import BasePadrao, BaseParcelas, get_db_session; \
db = get_db_session(); \
print(f'BasePadrao: {db.query(BasePadrao).filter_by(user_id=2).count()}'); \
print(f'BaseParcelas: {db.query(BaseParcelas).filter_by(user_id=2).count()}')"
```

**Esperado:** Ambos devem retornar 0

### Teste de Isolamento
```bash
# Admin (user_id=1) deve ter seus padrões preservados
python -c "from app.models import BasePadrao, get_db_session; \
db = get_db_session(); \
print(f'Admin: {db.query(BasePadrao).filter_by(user_id=1).count()}')"
```

**Esperado:** Número de padrões do Admin inalterado (746 padrões)

---

## 📋 Checklist de Novo Usuário

- [x] Usuário criado no sistema
- [x] BasePadrao vazia para user_id específico
- [x] BaseParcelas vazia para user_id específico
- [x] BaseMarcacao compartilhada (global)
- [x] Login funcional
- [x] Upload funcional
- [x] Classificação com bases vazias funcional
- [x] Salvamento de padrões funcional

---

## 🔮 Melhorias Futuras

- [ ] Dashboard de "Maturidade de Padrões" (% de transações auto-classificadas)
- [ ] Sugestão de categorias baseada em similaridade textual (sem usar padrões de outros)
- [ ] Exportação/Importação de padrões pessoais (backup)
- [ ] Opção de "reset" de padrões para recomeçar aprendizado

---

## 🔗 Relacionado

- Usuário afetado: Ana Beatriz (user_id=2)
- Feature: Sistema Multi-Usuário (v2.2.0)
- Motivação: Garantir experiência personalizada desde o início
- Impacto: Melhoria na qualidade de classificação a longo prazo
