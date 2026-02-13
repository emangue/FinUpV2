# 4️⃣ Revisão - Base Genérica

**Frente:** Revisão Base Genérica  
**Status:** ✅ **CONCLUÍDA**  
**Prioridade:** 🔴 CRÍTICA  
**Responsável:** Emanuel + Copilot  
**Data Início:** 12/02/2026  
**Data Conclusão:** 12/02/2026  
**Tempo:** ~4 horas

---

## 🎯 Objetivo

Maximizar a cobertura automática de classificação para novos usuários (sem dados históricos) através da revisão e expansão da base genérica de regras (`generic_classification_rules`).

**Meta:** Aumentar cobertura de ~45% → 70%+

---

## ✅ Conquistas

### 1. Auditoria Completa
- ✅ **55 regras existentes** documentadas (keywords, prioridade, grupo/subgrupo)
- ✅ Análise de 2631 transações reais (journal_entries)
- ✅ Identificação de **gaps críticos**: Uber variações (227x), ConectCar typo (178x), etc.
- ✅ Taxa de cobertura atual medida: **~45%**

### 2. Propostas de Melhoria
- ✅ **32 melhorias identificadas** e priorizadas em 3 fases
- ✅ **Fase 1 (Críticas):** 10 melhorias → +25% cobertura (45% → 70%)
- ✅ **Fase 2 (Importantes):** 12 melhorias → +6.8% cobertura (70% → 77%)
- ✅ **Fase 3 (Opcionais):** 10 melhorias → ROI baixo (manutenção contínua)
- ✅ **SQL pronto** para implementação imediata

### 3. Script de Validação
- ✅ Ferramenta de teste criada: `scripts/testing/test_generic_classification.py`
- ✅ Processa CSVs de fatura automaticamente
- ✅ Calcula taxa de cobertura real
- ✅ Lista transações não classificadas (agrupadas + valor)
- ✅ **Sugere novas regras** baseado em padrões

### 4. Testes com Dados Reais
- ✅ Fatura dezembro 2025 (70 transações): 44.3% cobertura
- ✅ Fatura setembro 2025 (81 transações): 45.7% cobertura
- ✅ Gaps identificados e documentados

---

## 📁 Documentação Completa

### Arquivos Gerados

| Arquivo | Conteúdo | Uso |
|---------|----------|-----|
| [AUDITORIA_BASE_GENERICA.md](AUDITORIA_BASE_GENERICA.md) | Contexto geral, top gaps, plano de ação | Entender problema |
| [VALIDACAO_REGRAS_ATUAIS.md](VALIDACAO_REGRAS_ATUAIS.md) ⭐ | 55 regras detalhadas, análise por grupo | Diagnóstico completo |
| [PROPOSTAS_MELHORIAS.md](PROPOSTAS_MELHORIAS.md) ⭐⭐ | 32 melhorias + SQL pronto | Guia de implementação |
| [RELATORIO_FINAL.md](RELATORIO_FINAL.md) ⭐⭐⭐ | Consolidação, lições aprendidas, próximos passos | Referência principal |
| `../../scripts/testing/test_generic_classification.py` | Script de teste | Validação contínua |

---

## 🎯 Principais Descobertas

### 1. Uber Variações - MAIOR IMPACTO
**Problema:** 227 transações não cobertas  
**Causa:** Keywords desatualizadas (`UBER` não match com `UBER*`, `UBER *`, `UBER   *`)  
**Solução:** Adicionar variações → **+8.6% cobertura**

### 2. ConectCar Typo - 2º MAIOR IMPACTO
**Problema:** 178 transações não cobertas  
**Causa:** Typo na keyword (`CONNETCAR` com 1 N, mas transações vêm `CONECTCAR` com 2 Ns)  
**Solução:** Corrigir typo → **+6.8% cobertura**

### 3. Categorias Ausentes
**Problema:** Serviços comuns sem subgrupo  
**Exemplos:**
- IOF (40x) - sem categoria
- Mensagem Cartão (16x) - sem categoria
- Folha de SP (12x) - sem categoria
- TEM BICI (10x) - sem categoria  
**Solução:** Criar novas categorias → **+3.8% cobertura**

### 4. Conflitos de Prioridade
**Problema:** `APPLE` genérico (tecnologia, prior 7) pegando transações que deveriam ir para Assinaturas  
**Solução:** Criar `Apple.com/bill` específico (prior 9) → **+1.4% cobertura**

---

## 📊 Impacto das Melhorias (Fase 1)

```
Cobertura atual:     45.0%
+ Uber variações:    +8.6%  ← MAIOR IMPACTO
+ ConectCar fix:     +6.8%  ← 2º MAIOR IMPACTO
+ Vendify/IFD:       +2.2%
+ Conta Vivo:        +1.7%
+ IOF:               +1.5%
+ Apple.com/bill:    +1.4%
+ Atacadista:        +1.3%
+ Spotify var:       +0.6%
+ Mensagem:          +0.6%
+ Amazon Prime BR:   +0.5%
──────────────────────────
TOTAL Fase 1:        70.2%  ← META ATINGIDA!
```

---

## 🚀 Como Implementar

### 1. Executar SQL (Fase 1 - Críticas)
```bash
cd app_dev/backend
# Copiar SQL de PROPOSTAS_MELHORIAS.md (Fase 1)
sqlite3 database/financas_dev.db < fase1_melhorias.sql

# Verificar: deve ter ~60-65 regras agora
sqlite3 database/financas_dev.db "SELECT COUNT(*) FROM generic_classification_rules WHERE ativo = 1"
```

### 2. Validar com Script
```bash
python scripts/testing/test_generic_classification.py _arquivos_historicos/_csvs_historico/fatura_itau-202512.csv
```

**Esperado:**
- Antes: 31/70 (44.3%)
- Depois: ~49/70 (70%+)

### 3. Testar Múltiplas Faturas
```bash
# Testar com 3-4 faturas diferentes
python scripts/testing/test_generic_classification.py fatura_itau-202511.csv
python scripts/testing/test_generic_classification.py fatura-202509.csv
python scripts/testing/test_generic_classification.py fatura-202508.csv
```

### 4. Ajustar se Necessário
- Script mostrará gaps remanescentes
- Usar sugestões automáticas
- Criar novas regras específicas

---

## 🎓 Lições Aprendidas

### 1. Keywords Devem Ser Flexíveis
- ❌ RUIM: `UBER` (match exato)
- ✅ BOM: `UBER,UBER*,UBER *` (aceita variações)

### 2. Prioridade É Crítica
- Regras específicas devem ter prioridade > genéricas
- Exemplo: `Apple.com/bill` (9) > `APPLE` genérico (6)

### 3. Manutenção Contínua Necessária
- Estabelecimentos mudam formatos de cobrança
- Revisão trimestral recomendada
- Script de teste facilita validação

### 4. Dados Reais > Intuição
- 227 transações Uber sem match (descoberto nos dados!)
- 178 transações ConectCar sem match (typo não óbvio)
- Análise de journal_entries foi essencial

---

## ✅ Objetivo Original vs Realizado

### Objetivo Original (README.md antigo)
> "Revisar completamente a estrutura de journal_entries e dados genéricos para garantir uma excelente experiência para o primeiro usuário do sistema."

### Realizado
✅ **Foco correto identificado:** `generic_classification_rules` (não journal_entries)  
✅ **Auditoria completa:** 55 regras documentadas  
✅ **Propostas acionáveis:** 32 melhorias priorizadas com SQL  
✅ **Ferramenta de validação:** Script de teste criado  
✅ **Caminho claro:** De 45% → 70%+ cobertura

**Mudança de escopo:**  
O objetivo foi **refinado** durante execução para focar na base genérica de classificação (generic_classification_rules), que é o componente crítico para experiência de novos usuários, em vez de journal_entries (que é populado pelo usuário).

---

## 🎯 Revisão do Objetivo

---

## 📋 Escopo

### Incluído
- ✅ Auditoria completa de campos em `journal_entries`
- ✅ Validação de defaults adequados
- ✅ Definição de dados iniciais obrigatórios
- ✅ Experiência zero state (usuário sem dados)
- ✅ Grupos/categorias padrão
- ✅ Validações de integridade

### Excluído
- ❌ Mudanças em outras tabelas (fora de journal_entries)
- ❌ Migração de dados existentes

---

## 🔍 Fase 1: Auditoria de journal_entries

### 1.1 Estrutura Atual

**Campos principais:**
```sql
-- Identificação
IdTransacao         TEXT PRIMARY KEY
user_id             INTEGER NOT NULL

-- Dados da Transação
Data                TEXT    -- DD/MM/YYYY
Ano                 INTEGER
Mes                 INTEGER
MesFatura           TEXT    -- YYYYMM (para faturas)

-- Valores
Lancamento          TEXT    -- Nome/descrição
Valor               REAL

-- Classificação
Grupo               TEXT
Subgrupo            TEXT
TipoGasto           TEXT
CategoriaGeral      TEXT    -- Despesa/Receita/Investimento

-- Tipo de Documento
TipoDocumento       TEXT    -- extrato/fatura

-- Controles
IgnorarDashboard    INTEGER DEFAULT 0
Observacoes         TEXT
```

### 1.2 Questões a Responder

**Campos obrigatórios vs opcionais:**
- [ ] Quais campos DEVEM ser preenchidos sempre?
- [ ] Quais campos podem ser NULL?
- [ ] Quais defaults fazem sentido?

**Validações necessárias:**
- [ ] Valor sempre positivo/negativo baseado em CategoriaGeral?
- [ ] Data sempre válida?
- [ ] Ano/Mes sempre sincronizados com Data?
- [ ] MesFatura sempre no formato YYYYMM?

**Integridade referencial:**
- [ ] Grupo deve existir em base_marcacoes?
- [ ] TipoGasto deve existir em base_grupos_config?
- [ ] user_id deve existir em users?

---

## 📊 Fase 2: Análise de Primeiro Uso

### 2.1 Cenário: Usuário Zero State

**Situação:** Usuário acabou de criar conta, sem nenhum dado

**Perguntas:**
1. O que o usuário vê no dashboard? (vazio = ruim!)
2. Consegue fazer upload? (sim, mas precisa de grupos!)
3. Consegue criar transação manual? (sim, mas precisa de categorias!)
4. Consegue criar meta? (sim, mas sem grupos não faz sentido!)

### 2.2 Dados Iniciais Necessários

**Obrigatórios para primeiro uso:**
```markdown
| Base               | Dados Iniciais | Motivo |
|--------------------|----------------|--------|
| base_marcacoes     | Grupos padrão  | Upload precisa de categorias |
| base_grupos_config | Tipos padrão   | Classificação automática |
| budget_geral       | Vazio (OK)     | Usuário cria suas metas |
| grupos_planning    | Vazio (OK)     | Gerado no primeiro upload |
| journal_entries    | Vazio (OK)     | Usuário importa/cria |
```

### 2.3 Grupos Padrão Recomendados

**Despesas:**
```
- Alimentação
  - Supermercado
  - Restaurante
  - Delivery
- Transporte
  - Combustível
  - Uber/99
  - Manutenção
- Casa
  - Aluguel/Financiamento
  - Contas (água, luz, gás)
  - Internet/TV
- Lazer
  - Viagens
  - Entretenimento
  - Hobbies
- Saúde
  - Farmácia
  - Consultas
  - Plano de Saúde
```

**Receitas:**
```
- Salário
- Freelance
- Investimentos
  - Dividendos
  - Juros
- Outros
```

---

## 🛠️ Fase 3: Implementação de Defaults

### 3.1 Migration de Defaults

```python
# migrations/versions/XXXX_add_default_groups.py
def upgrade():
    """
    Adiciona grupos padrão para novos usuários
    """
    # Grupos de Despesa
    grupos_despesa = [
        ('Alimentação', 'Grupo', 'Despesa', None),
        ('Supermercado', 'Subgrupo', 'Despesa', 'Alimentação'),
        ('Restaurante', 'Subgrupo', 'Despesa', 'Alimentação'),
        # ... mais grupos
    ]
    
    # Grupos de Receita
    grupos_receita = [
        ('Salário', 'Grupo', 'Receita', None),
        ('Freelance', 'Grupo', 'Receita', None),
        # ... mais grupos
    ]
    
    # Inserir apenas se não existirem
    for nome, tipo, categoria, pai in grupos_despesa + grupos_receita:
        op.execute(f"""
            INSERT OR IGNORE INTO base_marcacoes (Marcacao, Tipo, CategoriaGeral, GrupoPai)
            VALUES ('{nome}', '{tipo}', '{categoria}', {f"'{pai}'" if pai else 'NULL'})
        """)
```

### 3.2 Função de Setup Inicial

```python
# app/domains/users/service.py
def setup_new_user(user_id: int, db: Session):
    """
    Configura dados iniciais para novo usuário
    """
    # 1. Grupos padrão já existem (migration)
    # Apenas precisamos garantir que user tem acesso
    
    # 2. Criar entrada em budget_geral (vazia mas estruturada)
    current_year = datetime.now().year
    for month in range(1, 13):
        budget = BudgetGeral(
            user_id=user_id,
            Ano=current_year,
            Mes=month,
            # Valores zerados, usuário preenche depois
        )
        db.add(budget)
    
    # 3. Criar entrada em grupos_planning (vazia)
    # Será populada no primeiro upload
    
    db.commit()
```

### 3.3 Chamar Setup no Cadastro

```python
# app/domains/auth/router.py
@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    # Criar usuário
    user = User(email=data.email, ...)
    db.add(user)
    db.commit()
    
    # Setup inicial
    setup_new_user(user.id, db)
    
    return {"message": "Usuário criado com sucesso"}
```

---

## 🎨 Fase 4: UX Zero State

### 4.1 Dashboard Vazio

**Exibição quando usuário não tem dados:**
```typescript
// src/features/dashboard/components/empty-state.tsx
function DashboardEmptyState() {
  return (
    <div className="text-center p-12">
      <h2>Bem-vindo ao FinUp! 👋</h2>
      <p>Você ainda não tem transações registradas.</p>
      
      <div className="mt-6 space-y-4">
        <Button onClick={handleUpload}>
          <Upload className="mr-2" />
          Importar Extrato/Fatura
        </Button>
        
        <Button variant="outline" onClick={handleManual}>
          <Plus className="mr-2" />
          Adicionar Transação Manual
        </Button>
        
        <Button variant="outline" onClick={handleTutorial}>
          <BookOpen className="mr-2" />
          Ver Tutorial
        </Button>
      </div>
    </div>
  )
}
```

### 4.2 Validação de Dados

**Antes de exibir dashboard:**
```typescript
function Dashboard() {
  const { data: transactions, isLoading } = useTransactions()
  
  if (isLoading) return <LoadingState />
  
  if (!transactions || transactions.length === 0) {
    return <DashboardEmptyState />
  }
  
  return <DashboardWithData data={transactions} />
}
```

---

## ✅ Checklist de Implementação

### Fase 1: Auditoria
- [ ] Documentar todos os campos de journal_entries
- [ ] Definir campos obrigatórios vs opcionais
- [ ] Definir validações necessárias
- [ ] Definir constraints de integridade

### Fase 2: Análise
- [ ] Testar cenário zero state manualmente
- [ ] Identificar problemas de UX
- [ ] Definir dados iniciais necessários
- [ ] Criar lista de grupos padrão

### Fase 3: Implementação
- [ ] Criar migration com grupos padrão
- [ ] Implementar função setup_new_user
- [ ] Integrar setup no cadastro
- [ ] Testar criação de novo usuário

### Fase 4: UX
- [ ] Criar componente EmptyState
- [ ] Integrar em todas as telas principais
- [ ] Adicionar CTAs para primeira ação
- [ ] Testar fluxo completo de primeiro uso

---

## 🧪 Validação

### Teste Completo de Primeiro Usuário

```markdown
1. [ ] Criar novo usuário
2. [ ] Validar que grupos padrão existem
3. [ ] Validar que budget_geral foi criado (vazio)
4. [ ] Acessar dashboard → ver EmptyState
5. [ ] Fazer primeiro upload
6. [ ] Validar que transações foram salvas
7. [ ] Validar que grupos_planning foi populado
8. [ ] Voltar ao dashboard → ver dados
9. [ ] Criar primeira meta
10. [ ] Editar meta → salvar
```

---

## 📊 Métricas

### Progresso
```
Auditoria:        ░░░░░░░░░░ 0%
Análise:          ░░░░░░░░░░ 0%
Implementação:    ░░░░░░░░░░ 0%
UX:               ░░░░░░░░░░ 0%
TOTAL:            ░░░░░░░░░░ 0%
```

---

## 🚧 Riscos

1. **Alto:** Defaults podem não fazer sentido para todos os usuários
2. **Médio:** Grupos padrão podem conflitar com dados existentes
3. **Baixo:** Setup pode falhar em casos edge

### Mitigações
1. Tornar grupos padrão configuráveis
2. Usar INSERT OR IGNORE para evitar conflitos
3. Adicionar try/catch e rollback no setup

---

## � Checklist de Finalização

- [x] ✅ Validar regras atuais (55 regras documentadas)
- [x] ✅ Criar documento de propostas (32 melhorias)
- [x] ✅ Criar script de teste com fatura
- [x] ✅ Testar com faturas reais (2 testadas)
- [x] ✅ Medir cobertura atual (~45%)
- [x] ✅ Identificar gaps críticos (Uber, ConectCar, IOF, etc.)
- [x] ✅ Propor melhorias acionáveis (SQL pronto)
- [x] ✅ Documentar lições aprendidas
- [ ] ⬜ Implementar Fase 1 (10 críticas) ← PRÓXIMO PASSO
- [ ] ⬜ Validar cobertura atingiu 70%+
- [ ] ⬜ Considerar Fase 2 (12 importantes)

---

## 🚀 Próximos Passos

### Imediato (Hoje/Amanhã)
1. **Revisar propostas** com usuário/time
2. **Decidir:** Implementar Fase 1 agora ou depois?
3. **Se implementar:** Executar SQL + validar com script

### Curto Prazo (Esta Semana)
4. Testar com usuário novo (zero state) - **Frente 5**
5. Medir experiência de primeiro upload
6. Ajustar regras se necessário

### Médio Prazo (Próximo Sprint)
7. Implementar Fase 2 se gaps ainda grandes
8. Criar documentação de manutenção
9. Agendar revisão trimestral

---

## 🔗 Referências

- [PLANO_FINALIZACAO.md](../PLANO_FINALIZACAO.md)
- [Frente 5 - Teste Usuário Inicial](../05_teste_user_inicial/README.md) (próxima frente)
- Base de dados: `app_dev/backend/database/financas_dev.db`
- Modelo: `app/domains/classification/models.py`
- Service: `app/domains/classification/service.py`

---

**Última Atualização:** 12/02/2026 23:45  
**Status:** ✅ **CONCLUÍDA - Pronta para implementação**
