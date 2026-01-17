# 🔄 PLANO INCREMENTAL - Refatoração de Categorias

**Princípio:** Construir e validar cada etapa ANTES de prosseguir  
**Rollback:** Cada fase pode ser revertida independentemente  
**Validações:** Queries SQL + testes funcionais em cada fase

---

## 📐 ESTRATÉGIA GERAL

### Ordem de Implementação (do mais simples ao mais complexo)

```
FASE 1: Infraestrutura Base (Criar sem impactar)
   ↓
FASE 2: Helper Functions (Testar isoladamente)
   ↓
FASE 3: Migração de Dados (Journal Entries - 1 tabela por vez)
   ↓
FASE 4: Migração Budget (Menor impacto)
   ↓
FASE 5: Atualizar Classificadores (Lógica de negócio)
   ↓
FASE 6: Regenerar Bases Auxiliares (Padrões e Parcelas)
   ↓
FASE 7: Frontend Updates (UI adapta automaticamente)
```

### Princípios de Cada Fase

1. ✅ **Pode ser implementada sem quebrar o sistema atual**
2. ✅ **Tem validações específicas**
3. ✅ **Pode ser revertida facilmente**
4. ✅ **Não depende de fases futuras**

---

## 🚀 FASE 1: INFRAESTRUTURA BASE

**Objetivo:** Criar base_grupos_config SEM tocar em nenhum código existente  
**Impacto:** ZERO - tabela nova não afeta sistema atual  
**Tempo:** 30 minutos

### 1.1 Criar Tabela base_grupos_config

**Script:** `scripts/migrate_create_base_grupos_config.py`

```python
"""
Cria tabela base_grupos_config

ESTRUTURA:
- nome_grupo (PRIMARY KEY)
- tipo_gasto_padrao (5 valores possíveis)
- categoria_geral (4 valores possíveis)
"""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS base_grupos_config (
    nome_grupo TEXT PRIMARY KEY,
    tipo_gasto_padrao TEXT NOT NULL,
    categoria_geral TEXT NOT NULL,
    CHECK (tipo_gasto_padrao IN ('Fixo', 'Ajustável', 'Investimentos', 'Transferência', 'Receita')),
    CHECK (categoria_geral IN ('Receita', 'Despesa', 'Investimentos', 'Transferência'))
);
"""
```

### 1.2 Popular Seed Data (16 Grupos)

```python
SEED_DATA = [
    # Fixo (3 grupos)
    ('Moradia', 'Fixo', 'Despesa'),
    ('Educação', 'Fixo', 'Despesa'),
    ('Saúde', 'Fixo', 'Despesa'),
    
    # Ajustável (10 grupos)
    ('Casa', 'Ajustável', 'Despesa'),
    ('Delivery', 'Ajustável', 'Despesa'),
    ('Entretenimento', 'Ajustável', 'Despesa'),
    ('Uber', 'Ajustável', 'Despesa'),
    ('Viagens', 'Ajustável', 'Despesa'),
    ('Supermercado', 'Ajustável', 'Despesa'),
    ('Roupas', 'Ajustável', 'Despesa'),
    ('Presentes', 'Ajustável', 'Despesa'),
    ('Assinaturas', 'Ajustável', 'Despesa'),
    ('Carro', 'Ajustável', 'Despesa'),
    
    # Investimentos (1 grupo)
    ('Aplicações', 'Investimentos', 'Investimentos'),
    
    # Transferência (1 grupo)
    ('Movimentações', 'Transferência', 'Transferência'),
    
    # Receita (2 grupos)
    ('Salário', 'Receita', 'Receita'),
    ('Outros', 'Receita', 'Receita'),
]

for nome_grupo, tipo_gasto, categoria in SEED_DATA:
    cursor.execute("""
        INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral)
        VALUES (?, ?, ?)
    """, (nome_grupo, tipo_gasto, categoria))
```

### 1.3 Validar Criação

**Query 1:** Verificar estrutura
```sql
SELECT sql FROM sqlite_master WHERE type='table' AND name='base_grupos_config';
```

**Query 2:** Contar registros
```sql
SELECT COUNT(*) as total FROM base_grupos_config;
-- Esperado: 16
```

**Query 3:** Ver todos os grupos
```sql
SELECT nome_grupo, tipo_gasto_padrao, categoria_geral 
FROM base_grupos_config 
ORDER BY tipo_gasto_padrao, nome_grupo;
```

### ✅ Critério de Sucesso Fase 1

- [ ] Tabela criada com 3 colunas
- [ ] 16 registros inseridos
- [ ] CHECK constraints funcionando
- [ ] Sistema continua funcionando normalmente (tabela não é usada ainda)

**Rollback:** `DROP TABLE IF EXISTS base_grupos_config;`

---

## 🛠️ FASE 2: HELPER FUNCTIONS

**Objetivo:** Criar função auxiliar e testar ISOLADAMENTE  
**Impacto:** ZERO - função nova não é chamada ainda  
**Tempo:** 1 hora

### 2.1 Criar Helper no Core

**Arquivo:** `app_dev/backend/app/core/categorias_helper.py` (novo arquivo)

```python
"""
Helper functions para determinação de TipoGasto via base_grupos_config
"""
from sqlalchemy.orm import Session
from typing import Optional

def determinar_tipo_gasto_via_config(session: Session, grupo: str) -> Optional[str]:
    """
    Busca tipo_gasto_padrao baseado no GRUPO usando base_grupos_config
    
    Args:
        session: SQLAlchemy session
        grupo: Nome do grupo (ex: 'Viagens')
    
    Returns:
        tipo_gasto_padrao (ex: 'Ajustável') ou None se não encontrado
    
    Exemplos:
        >>> determinar_tipo_gasto_via_config(db, 'Viagens')
        'Ajustável'
        
        >>> determinar_tipo_gasto_via_config(db, 'Moradia')
        'Fixo'
    """
    if not grupo:
        return None
    
    result = session.execute(
        "SELECT tipo_gasto_padrao FROM base_grupos_config WHERE nome_grupo = ?",
        (grupo,)
    ).fetchone()
    
    return result[0] if result else None


def determinar_categoria_geral_via_config(session: Session, grupo: str) -> Optional[str]:
    """
    Busca categoria_geral baseada no GRUPO usando base_grupos_config
    
    Args:
        session: SQLAlchemy session
        grupo: Nome do grupo (ex: 'Salário')
    
    Returns:
        categoria_geral (ex: 'Receita') ou None se não encontrado
    
    Exemplos:
        >>> determinar_categoria_geral_via_config(db, 'Salário')
        'Receita'
        
        >>> determinar_categoria_geral_via_config(db, 'Aplicações')
        'Investimentos'
    """
    if not grupo:
        return None
    
    result = session.execute(
        "SELECT categoria_geral FROM base_grupos_config WHERE nome_grupo = ?",
        (grupo,)
    ).fetchone()
    
    return result[0] if result else None
```

### 2.2 Criar Script de Teste Isolado

**Arquivo:** `app_dev/backend/test_categorias_helper.py`

```python
"""
Testa helper functions ISOLADAMENTE (sem afetar sistema)
"""
from app.core.database import SessionLocal
from app.core.categorias_helper import determinar_tipo_gasto_via_config, determinar_categoria_geral_via_config

def test_helper_functions():
    db = SessionLocal()
    
    print("🧪 TESTE 1: Grupos Ajustáveis")
    grupos_ajustaveis = ['Viagens', 'Uber', 'Delivery', 'Casa', 'Entretenimento']
    for grupo in grupos_ajustaveis:
        tipo = determinar_tipo_gasto_via_config(db, grupo)
        cat = determinar_categoria_geral_via_config(db, grupo)
        assert tipo == 'Ajustável', f"ERRO: {grupo} deveria ser Ajustável, retornou {tipo}"
        assert cat == 'Despesa', f"ERRO: {grupo} deveria ser Despesa, retornou {cat}"
        print(f"  ✅ {grupo}: {tipo} - {cat}")
    
    print("\n🧪 TESTE 2: Grupos Fixos")
    grupos_fixos = ['Moradia', 'Educação', 'Saúde']
    for grupo in grupos_fixos:
        tipo = determinar_tipo_gasto_via_config(db, grupo)
        cat = determinar_categoria_geral_via_config(db, grupo)
        assert tipo == 'Fixo', f"ERRO: {grupo} deveria ser Fixo, retornou {tipo}"
        assert cat == 'Despesa', f"ERRO: {grupo} deveria ser Despesa, retornou {cat}"
        print(f"  ✅ {grupo}: {tipo} - {cat}")
    
    print("\n🧪 TESTE 3: Receitas")
    grupos_receita = ['Salário', 'Outros']
    for grupo in grupos_receita:
        tipo = determinar_tipo_gasto_via_config(db, grupo)
        cat = determinar_categoria_geral_via_config(db, grupo)
        assert tipo == 'Receita', f"ERRO: {grupo} deveria ser Receita, retornou {tipo}"
        assert cat == 'Receita', f"ERRO: {grupo} deveria ser Receita (cat), retornou {cat}"
        print(f"  ✅ {grupo}: {tipo} - {cat}")
    
    print("\n🧪 TESTE 4: Investimentos")
    tipo = determinar_tipo_gasto_via_config(db, 'Aplicações')
    cat = determinar_categoria_geral_via_config(db, 'Aplicações')
    assert tipo == 'Investimentos', f"ERRO: Aplicações deveria ser Investimentos, retornou {tipo}"
    assert cat == 'Investimentos', f"ERRO: Aplicações deveria ser Investimentos (cat), retornou {cat}"
    print(f"  ✅ Aplicações: {tipo} - {cat}")
    
    print("\n🧪 TESTE 5: Transferência")
    tipo = determinar_tipo_gasto_via_config(db, 'Movimentações')
    cat = determinar_categoria_geral_via_config(db, 'Movimentações')
    assert tipo == 'Transferência', f"ERRO: Movimentações deveria ser Transferência, retornou {tipo}"
    assert cat == 'Transferência', f"ERRO: Movimentações deveria ser Transferência (cat), retornou {cat}"
    print(f"  ✅ Movimentações: {tipo} - {cat}")
    
    print("\n🧪 TESTE 6: Grupo Inexistente")
    tipo = determinar_tipo_gasto_via_config(db, 'GrupoQueNaoExiste')
    cat = determinar_categoria_geral_via_config(db, 'GrupoQueNaoExiste')
    assert tipo is None, f"ERRO: Grupo inexistente deveria retornar None, retornou {tipo}"
    assert cat is None, f"ERRO: Grupo inexistente deveria retornar None (cat), retornou {cat}"
    print(f"  ✅ Grupo inexistente: None - None")
    
    print("\n🎉 TODOS OS TESTES PASSARAM!\n")
    db.close()

if __name__ == "__main__":
    test_helper_functions()
```

### 2.3 Executar Testes

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend
source ../venv/bin/activate
python test_categorias_helper.py
```

### ✅ Critério de Sucesso Fase 2

- [ ] Helper criado em `app/core/categorias_helper.py`
- [ ] Todos os 6 testes passam
- [ ] 16 grupos retornam valores corretos
- [ ] Grupo inexistente retorna None
- [ ] Sistema continua funcionando (helper não é usado ainda)

**Rollback:** `rm app/core/categorias_helper.py test_categorias_helper.py`

---

## 📊 FASE 3: MIGRAÇÃO JOURNAL_ENTRIES

**Objetivo:** Migrar TipoGasto de 22→5 valores na tabela principal  
**Impacto:** MÉDIO - Altera dados mas não quebra sistema (TipoGasto continua sendo string)  
**Tempo:** 2 horas

### 3.1 Criar Backup Específico

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database
cp financas_dev.db financas_dev.db.backup_antes_migracao_journal
```

### 3.2 Script de Migração (COM PREVIEW)

**Arquivo:** `scripts/migrate_journal_entries_tipo_gasto.py`

```python
"""
Migra TipoGasto de journal_entries: 22 valores → 5 valores
"""

# MAPEAMENTO: TipoGasto antigo → Novo
MAPEAMENTO = {
    # Ajustável - * → Ajustável
    'Ajustável - Viagens': 'Ajustável',
    'Ajustável - Casa': 'Ajustável',
    'Ajustável - Delivery': 'Ajustável',
    'Ajustável - Saídas': 'Ajustável',
    'Ajustável - Uber': 'Ajustável',
    'Ajustável - Supermercado': 'Ajustável',
    'Ajustável - Roupas': 'Ajustável',
    'Ajustável - Presentes': 'Ajustável',
    'Ajustável - Assinaturas': 'Ajustável',
    'Ajustável - Carro': 'Ajustável',
    'Ajustável - Doações': 'Ajustável',
    'Ajustável - Esportes': 'Ajustável',
    'Ajustável - Tech': 'Ajustável',
    'Ajustável': 'Ajustável',
    
    # Fixo → Fixo
    'Fixo': 'Fixo',
    
    # Receita → Receita
    'Receita': 'Receita',
    'Receita - Salário': 'Receita',
    
    # Débito → Transferência
    'Débito': 'Transferência',
    
    # Investimentos → Investimentos
    'Investimentos': 'Investimentos',
    
    # Outros/Especiais
    'Outros': 'Ajustável',  # Maioria é despesa ajustável
}

def preview_migration(conn):
    """Mostra O QUE SERÁ ALTERADO sem modificar dados"""
    print("\n🔍 PREVIEW DA MIGRAÇÃO\n")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TipoGasto, COUNT(*) as qtd
        FROM journal_entries
        WHERE TipoGasto IS NOT NULL
        GROUP BY TipoGasto
        ORDER BY TipoGasto
    """)
    
    print(f"{'TipoGasto Atual':<30} {'Qtd':<10} {'→ Novo':<15}")
    print("-" * 60)
    
    total_afetado = 0
    for row in cursor.fetchall():
        tipo_atual, qtd = row
        tipo_novo = MAPEAMENTO.get(tipo_atual, '⚠️ SEM MAPEAMENTO')
        print(f"{tipo_atual:<30} {qtd:<10} → {tipo_novo:<15}")
        if tipo_novo != '⚠️ SEM MAPEAMENTO':
            total_afetado += qtd
    
    print("-" * 60)
    print(f"Total de registros afetados: {total_afetado}")
    print()
    
    return total_afetado

def execute_migration(conn):
    """Executa migração após confirmação"""
    cursor = conn.cursor()
    
    for tipo_antigo, tipo_novo in MAPEAMENTO.items():
        cursor.execute("""
            UPDATE journal_entries
            SET TipoGasto = ?
            WHERE TipoGasto = ?
        """, (tipo_novo, tipo_antigo))
        
        affected = cursor.rowcount
        if affected > 0:
            print(f"  ✅ {tipo_antigo:<30} → {tipo_novo:<15} ({affected} registros)")
    
    conn.commit()
    print("\n✅ Migração concluída!")

def validate_migration(conn):
    """Valida que migração funcionou"""
    cursor = conn.cursor()
    
    print("\n🔍 VALIDAÇÃO PÓS-MIGRAÇÃO\n")
    
    cursor.execute("""
        SELECT TipoGasto, COUNT(*) as qtd
        FROM journal_entries
        WHERE TipoGasto IS NOT NULL
        GROUP BY TipoGasto
        ORDER BY TipoGasto
    """)
    
    tipos_encontrados = set()
    for row in cursor.fetchall():
        tipo, qtd = row
        tipos_encontrados.add(tipo)
        print(f"  {tipo:<20} {qtd:>6} registros")
    
    print()
    
    # Verificar se há apenas os 5 valores esperados
    esperados = {'Fixo', 'Ajustável', 'Investimentos', 'Transferência', 'Receita'}
    tipos_invalidos = tipos_encontrados - esperados
    
    if tipos_invalidos:
        print(f"⚠️ ERRO: Tipos inválidos encontrados: {tipos_invalidos}")
        return False
    
    if not tipos_encontrados.issubset(esperados):
        print(f"⚠️ ERRO: Tipos esperados: {esperados}, encontrados: {tipos_encontrados}")
        return False
    
    print("✅ Validação bem-sucedida! Apenas 5 valores presentes.")
    return True

if __name__ == "__main__":
    import sqlite3
    
    conn = sqlite3.connect('/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db')
    
    # 1. Preview
    total = preview_migration(conn)
    
    # 2. Confirmar
    resposta = input(f"\n⚠️ Isso irá alterar {total} registros. Continuar? (sim/não): ")
    if resposta.lower() != 'sim':
        print("❌ Migração cancelada.")
        conn.close()
        exit(0)
    
    # 3. Executar
    execute_migration(conn)
    
    # 4. Validar
    if validate_migration(conn):
        print("\n🎉 Migração da journal_entries concluída com sucesso!")
    else:
        print("\n⚠️ Validação falhou. Verifique os dados.")
        print("💡 Para reverter: restaure o backup financas_dev.db.backup_antes_migracao_journal")
    
    conn.close()
```

### 3.3 Executar Migração

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend
source ../venv/bin/activate
python scripts/migrate_journal_entries_tipo_gasto.py
```

### 3.4 Validação Pós-Migração

**Query 1:** Verificar apenas 5 valores existem
```sql
SELECT DISTINCT TipoGasto 
FROM journal_entries 
WHERE TipoGasto IS NOT NULL 
ORDER BY TipoGasto;

-- Esperado: Ajustável, Fixo, Investimentos, Receita, Transferência
```

**Query 2:** Contar por novo TipoGasto
```sql
SELECT TipoGasto, COUNT(*) as qtd
FROM journal_entries
WHERE TipoGasto IS NOT NULL
GROUP BY TipoGasto
ORDER BY qtd DESC;
```

**Query 3:** Verificar se algum registro ficou sem TipoGasto
```sql
SELECT COUNT(*) as sem_tipo_gasto
FROM journal_entries
WHERE TipoGasto IS NULL;
```

### ✅ Critério de Sucesso Fase 3

- [ ] Preview mostra mapeamento correto
- [ ] Migração executa sem erros
- [ ] Apenas 5 valores existem na tabela
- [ ] Nenhum registro ficou com TipoGasto NULL (exceto os que já eram)
- [ ] Backup criado antes da migração
- [ ] Sistema continua funcionando (valores simplificados são válidos)

**Rollback:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database
cp financas_dev.db.backup_antes_migracao_journal financas_dev.db
```

---

## 💰 FASE 4: MIGRAÇÃO BUDGET_PLANNING

**Objetivo:** Migrar tipo_gasto de budget_planning  
**Impacto:** BAIXO - Tabela pequena, fácil reverter  
**Tempo:** 30 minutos

### 4.1 Criar Backup

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database
sqlite3 financas_dev.db ".backup financas_dev.db.backup_antes_budget"
```

### 4.2 Script de Migração

**Arquivo:** `scripts/migrate_budget_planning_tipo_gasto.py`

```python
"""
Migra tipo_gasto de budget_planning: 22 valores → 5 valores
"""
# Usa mesmo MAPEAMENTO da Fase 3

def preview_budget_migration(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo_gasto, COUNT(*) as qtd
        FROM budget_planning
        GROUP BY tipo_gasto
        ORDER BY tipo_gasto
    """)
    
    print("\n🔍 PREVIEW - Budget Planning\n")
    print(f"{'Tipo Atual':<30} {'Qtd':<10} {'→ Novo':<15}")
    print("-" * 60)
    
    for row in cursor.fetchall():
        tipo_atual, qtd = row
        tipo_novo = MAPEAMENTO.get(tipo_atual, '⚠️ SEM MAPEAMENTO')
        print(f"{tipo_atual:<30} {qtd:<10} → {tipo_novo:<15}")
    
    print()

def migrate_budget(conn):
    cursor = conn.cursor()
    
    for tipo_antigo, tipo_novo in MAPEAMENTO.items():
        cursor.execute("""
            UPDATE budget_planning
            SET tipo_gasto = ?
            WHERE tipo_gasto = ?
        """, (tipo_novo, tipo_antigo))
        
        if cursor.rowcount > 0:
            print(f"  ✅ {tipo_antigo} → {tipo_novo} ({cursor.rowcount} registros)")
    
    conn.commit()

# ... (similar à Fase 3)
```

### 4.3 Validação

```sql
SELECT DISTINCT tipo_gasto 
FROM budget_planning 
ORDER BY tipo_gasto;

-- Esperado: Ajustável, Fixo, Investimentos, Receita, Transferência
```

### ✅ Critério de Sucesso Fase 4

- [ ] Preview OK
- [ ] Migração executada
- [ ] Apenas 5 valores em budget_planning
- [ ] Backup criado

**Rollback:** Restaurar backup

---

## 🎯 FASE 5: ATUALIZAR CLASSIFICADORES

**Objetivo:** Atualizar generic_rules_classifier.py com novos valores  
**Impacto:** MÉDIO - Afeta classificação de novos uploads  
**Tempo:** 1 hora

### 5.1 Atualizar 39 Regras

**Arquivo:** `app/domains/upload/processors/generic_rules_classifier.py`

**ANTES:**
```python
ClassificationRule(
    pattern=r'netflix|spotify',
    grupo='Assinaturas',
    subgrupo='Streaming',
    tipo_gasto='Ajustável - Assinaturas',  # ❌ Antigo
    prioridade=100
)
```

**DEPOIS:**
```python
ClassificationRule(
    pattern=r'netflix|spotify',
    grupo='Assinaturas',
    subgrupo='Streaming',
    tipo_gasto='Ajustável',  # ✅ Novo
    prioridade=100
)
```

### 5.2 Mapeamento Completo das 39 Regras

**Substituições:**
- `'Ajustável - Viagens'` → `'Ajustável'` (3 ocorrências)
- `'Ajustável - Roupas'` → `'Ajustável'` (2 ocorrências)
- `'Ajustável - Saídas'` → `'Ajustável'` (1 ocorrência)
- `'Ajustável - Carro'` → `'Ajustável'` (5 ocorrências)
- `'Ajustável - Delivery'` → `'Ajustável'` (1 ocorrência)
- `'Ajustável - Supermercado'` → `'Ajustável'` (1 ocorrência)
- `'Ajustável - Uber'` → `'Ajustável'` (2 ocorrências)
- `'Ajustável - Assinaturas'` → `'Ajustável'` (8 ocorrências)
- `'Ajustável - Esportes'` → `'Ajustável'` (2 ocorrências)
- `'Ajustável - Tech'` → `'Ajustável'` (1 ocorrência)
- `'Ajustável'` → `'Ajustável'` (6 ocorrências - manter)
- `'Fixo'` → `'Fixo'` (9 ocorrências - manter)
- `'Débito'` → `'Transferência'` (1 ocorrência)

**Total:** 42 linhas alteradas

### 5.3 Teste de Classificação

**Script:** `test_generic_rules_updated.py`

```python
"""
Testa se regras genéricas retornam novos valores (5 apenas)
"""
from app.domains.upload.processors.generic_rules_classifier import GenericRulesClassifier

def test_rules():
    classifier = GenericRulesClassifier()
    
    test_cases = [
        ("NETFLIX", "Ajustável"),
        ("SPOTIFY", "Ajustável"),
        ("UBER *VIAGEM", "Ajustável"),
        ("RENT PAYMENT", "Fixo"),
        ("ZARA", "Ajustável"),
    ]
    
    for lancamento, tipo_esperado in test_cases:
        result = classifier.classify(lancamento, 100.0)
        if result:
            tipo = result['tipo_gasto']
            assert tipo == tipo_esperado, f"ERRO: {lancamento} retornou {tipo}, esperado {tipo_esperado}"
            print(f"  ✅ {lancamento}: {tipo}")
        else:
            print(f"  ⚠️ {lancamento}: Sem classificação")
    
    print("\n✅ Todas as regras retornam valores simplificados!")

if __name__ == "__main__":
    test_rules()
```

### ✅ Critério de Sucesso Fase 5

- [ ] 39 regras atualizadas
- [ ] Nenhuma referência a "Ajustável - *" permanece
- [ ] Teste de classificação passa
- [ ] Upload funciona normalmente

**Rollback:** Git revert do arquivo

---

## 🔄 FASE 6: REGENERAR BASES AUXILIARES

**Objetivo:** Regenerar base_padroes e base_parcelas com novos valores  
**Impacto:** ALTO - Mas apenas cria dados novos, não altera existentes  
**Tempo:** 2 horas

### 6.1 Criar Script de Regeneração de Padrões

**⚠️ DESCOBERTA:** base_padroes **NÃO tem gerador ativo** em app_dev!
- `pattern_generator.py` existe APENAS em `_arquivos_historicos/`
- NÃO é usado atualmente (sem referências em app_dev)
- base_padroes é APENAS **LIDA** pelo classifier

**OPÇÕES:**

**Opção A: Criar novo script em app_dev/backend/scripts/**
```bash
# scripts/regenerate_base_padroes.py
```

**Opção B: Adaptar script histórico**
- Copiar `_arquivos_historicos/codigos_apoio/pattern_generator.py` para `scripts/`
- Atualizar imports (app.models → app.domains.*)
- Adicionar helper `determinar_tipo_gasto_via_config()`
- Remover TipoGasto da chave de classificação (linha 68-77)

### 6.2 Entender regenerate_sql.py

**⚠️ DESCOBERTA:** `regenerate_sql.py` (raiz) **APENAS regenera hashes IdTransacao**
- NÃO popula base_padroes
- NÃO mexe em TipoGasto
- Função: Recalcular IdTransacao usando lógica de deduplicação

**✅ NENHUMA mudança necessária em regenerate_sql.py**

### 6.3 Backup e Regeneração

```bash
# Backup das bases
sqlite3 financas_dev.db "SELECT * FROM base_padroes" > base_padroes_backup.csv
sqlite3 financas_dev.db "SELECT * FROM base_parcelas" > base_parcelas_backup.csv

# Limpar bases
sqlite3 financas_dev.db "DELETE FROM base_padroes"
sqlite3 financas_dev.db "DELETE FROM base_parcelas"

# Regenerar
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
python regenerate_sql.py
```

### 6.4 Validação

**Query 1:** Verificar valores em base_padroes
```sql
SELECT DISTINCT tipo_gasto_sugerido 
FROM base_padroes 
ORDER BY tipo_gasto_sugerido;

-- Esperado: Ajustável, Fixo, Investimentos, Receita, Transferência
```

**Query 2:** Verificar valores em base_parcelas
```sql
SELECT DISTINCT tipo_gasto_sugerido 
FROM base_parcelas 
WHERE tipo_gasto_sugerido IS NOT NULL
ORDER BY tipo_gasto_sugerido;

-- Esperado: Ajustável, Fixo, Investimentos, Receita, Transferência
```

### ✅ Critério de Sucesso Fase 6

- [ ] base_padroes regenerada com 5 valores
- [ ] base_parcelas regenerada com 5 valores
- [ ] Nenhum valor antigo ("Ajustável - *") permanece
- [ ] Backups criados
- [ ] Classificação de novos uploads funciona

**Rollback:** Restaurar CSVs de backup

---

## 🎨 FASE 7: FRONTEND UPDATES

**Objetivo:** Atualizar filtros e inputs para mostrar apenas 5 valores  
**Impacto:** BAIXO - UI adaptativa, não quebra  
**Tempo:** 1 hora

### 7.1 Atualizar Filtro de Transações

**Arquivo:** `frontend/src/features/transactions/components/transaction-filters.tsx`

**ANTES:**
```typescript
<Select
  value={filters.tipoGasto || ''}
  onValueChange={(value) => setFilters({ ...filters, tipoGasto: value || undefined })}
>
  <SelectTrigger>
    <SelectValue placeholder="Todos" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="">Todos</SelectItem>
    {/* Options carregadas dinamicamente */}
  </SelectContent>
</Select>
```

**DEPOIS:**
```typescript
const TIPOS_GASTO_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'Fixo', label: 'Fixo' },
  { value: 'Ajustável', label: 'Ajustável' },
  { value: 'Investimentos', label: 'Investimentos' },
  { value: 'Transferência', label: 'Transferência' },
  { value: 'Receita', label: 'Receita' },
]

<Select
  value={filters.tipoGasto || ''}
  onValueChange={(value) => setFilters({ ...filters, tipoGasto: value || undefined })}
>
  <SelectTrigger>
    <SelectValue placeholder="Todos" />
  </SelectTrigger>
  <SelectContent>
    {TIPOS_GASTO_OPTIONS.map(opt => (
      <SelectItem key={opt.value} value={opt.value}>
        {opt.label}
      </SelectItem>
    ))}
  </SelectContent>
</Select>
```

### 7.2 Atualizar Inputs de Upload

**Arquivos:**
- `app/upload/confirm-ai/page.tsx` (linhas 667-671)
- `app/upload/confirm/page.tsx` (linhas 548-552)

**Mesma lógica:** Substituir input livre por select com 5 opções.

### 7.3 Atualizar Settings

**Arquivo:** `app/settings/categorias/page.tsx`

- Carregar grupos de base_grupos_config (endpoint novo)
- Form de edição usa select fixo com 5 valores

### ✅ Critério de Sucesso Fase 7

- [ ] Filtros mostram apenas 5 opções
- [ ] Upload permite selecionar apenas 5 valores
- [ ] Settings carrega de base_grupos_config
- [ ] UI responsiva e funcional
- [ ] Nenhum erro de console

**Rollback:** Git revert dos arquivos

---

## 📋 CHECKLIST GERAL DE EXECUÇÃO

### Antes de Começar
- [ ] Backup diário executado (`./backup_daily.sh`)
- [ ] Servidores parados (`./quick_stop.sh`)
- [ ] Branch git criada (`git checkout -b refactor/categorias-v2`)

### Durante Execução
- [ ] Fase 1 concluída e validada
- [ ] Fase 2 concluída e validada
- [ ] Fase 3 concluída e validada
- [ ] Fase 4 concluída e validada
- [ ] Fase 5 concluída e validada
- [ ] Fase 6 concluída e validada
- [ ] Fase 7 concluída e validada

### Pós-Implementação
- [ ] Servidores reiniciados (`./quick_start.sh`)
- [ ] Testes funcionais executados
- [ ] Commit e push da branch
- [ ] Merge request criado
- [ ] Documentação atualizada

---

## 🚨 PROCEDIMENTO DE ROLLBACK POR FASE

| Fase | Rollback | Impacto |
|------|----------|---------|
| Fase 1 | `DROP TABLE base_grupos_config` | Zero |
| Fase 2 | `rm categorias_helper.py test_categorias_helper.py` | Zero |
| Fase 3 | Restaurar `financas_dev.db.backup_antes_migracao_journal` | Médio |
| Fase 4 | Restaurar `financas_dev.db.backup_antes_budget` | Baixo |
| Fase 5 | `git checkout generic_rules_classifier.py` | Baixo |
| Fase 6 | Restaurar CSVs + reprocessar | Alto |
| Fase 7 | `git checkout frontend/...` | Zero |

---

## ⏱️ CRONOGRAMA ESTIMADO

| Fase | Tempo | Acumulado | Pode Fazer em Separado? |
|------|-------|-----------|-------------------------|
| Fase 1 | 30min | 0:30 | ✅ Sim |
| Fase 2 | 1h | 1:30 | ✅ Sim (após Fase 1) |
| Fase 3 | 2h | 3:30 | ⚠️ Requer pausa no sistema |
| Fase 4 | 30min | 4:00 | ✅ Pode fazer junto com Fase 3 |
| Fase 5 | 1h | 5:00 | ✅ Sim |
| Fase 6 | 2h | 7:00 | ⚠️ Requer pausa no sistema |
| Fase 7 | 1h | 8:00 | ✅ Sim |

**Total:** 8 horas  
**Tempo crítico (sistema parado):** 2h30min (Fases 3, 4, 6)

---

## 🎯 PRÓXIMAS AÇÕES SUGERIDAS

1. **Começar pela Fase 1** - Criar base_grupos_config (30min, zero risco)
2. **Fazer Fase 2 no mesmo dia** - Testar helpers (1h, zero risco)
3. **Agendar janela de manutenção** para Fases 3-4-6 (2h30min)
4. **Fases 5 e 7 podem ser feitas antes ou depois** das migrações

---

**Documento criado em:** 14/01/2026  
**Baseado em:** ANALISE_IMPACTO_COMPLETA.md  
**Próximo passo:** Executar Fase 1 ✅
