# 🧪 Passo a Passo - Testes de Upload com Aprendizado

**Data:** 13/02/2026  
**Objetivo:** Validar upload end-to-end e aprendizado progressivo de padrões e parcelas

---

## 📋 Índice

1. [Preparação do Ambiente](#1-preparação-do-ambiente)
2. [Ajuste da Journal Entries](#2-ajuste-da-journal-entries-opcional)
3. [Testes - 3 Faturas MercadoPago](#3-testes---3-faturas-mercadopago)
4. [Testes - 3 Faturas Itaú](#4-testes---3-faturas-itaú)
5. [Validações SQL](#5-validações-sql)
6. [Análise de Resultados](#6-análise-de-resultados)

---

## 1. Preparação do Ambiente

### 1.1 Verificar Servidores Rodando

```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5

# Verificar processos
ps aux | grep -E "(uvicorn|next)" | grep -v grep

# Se não estiverem rodando:
./scripts/deploy/quick_start.sh
```

**Validar:**
- ✅ Backend: http://localhost:8000/api/health
- ✅ Frontend: http://localhost:3000
- ✅ Docs API: http://localhost:8000/docs

---

### 1.2 Criar Usuário de Teste Limpo

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste_aprendizado@teste.com",
    "password": "teste123",
    "name": "Teste Aprendizado"
  }' | python3 -m json.tool
```

**Resposta esperada:**
```json
{
  "message": "Usuário criado com sucesso",
  "user": {
    "id": 5,
    "email": "teste_aprendizado@teste.com",
    "name": "Teste Aprendizado"
  }
}
```

**Anotar:** `user_id = 5` (usar nas queries SQL)

---

### 1.3 Fazer Login e Guardar Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste_aprendizado@teste.com",
    "password": "teste123"
  }' | python3 -m json.tool
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Guardar token em variável:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 1.4 Validar Estado Inicial Limpo

**SQL:**
```sql
-- Conectar ao banco
sqlite3 /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db

-- Verificar zero dados
SELECT COUNT(*) FROM journal_entries WHERE user_id = 5;
-- Esperado: 0

SELECT COUNT(*) FROM base_padroes WHERE user_id = 5;
-- Esperado: 0

SELECT COUNT(*) FROM base_parcelas WHERE user_id = 5;
-- Esperado: 0

SELECT COUNT(*) FROM upload_history WHERE user_id = 5;
-- Esperado: 0
```

---

## 2. Ajuste da Journal Entries (OPCIONAL)

### 2.1 Contexto

Campo `categoria_orcamento_id` é **legado** e não usado. Ver [ANALISE_CATEGORIA_ORCAMENTO.md](./ANALISE_CATEGORIA_ORCAMENTO.md)

**Decisão:**
- ⚠️ **Opção A:** Remover campo agora (requer recrear tabela)
- ✅ **Opção B:** Manter por enquanto, remover em cleanup futuro

### 2.2 Se Decidir Remover (SQLite)

**⚠️ FAZER BACKUP ANTES:**
```bash
cd /Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5
./scripts/deploy/backup_daily.sh
```

**SQL (Recrear tabela sem campo):**
```sql
-- 1. Parar servidores
-- ./scripts/deploy/quick_stop.sh

-- 2. Conectar ao banco
sqlite3 app_dev/backend/database/financas_dev.db

-- 3. Criar tabela temporária SEM categoria_orcamento_id
CREATE TABLE journal_entries_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    Data TEXT,
    Estabelecimento TEXT,
    EstabelecimentoBase TEXT,
    Valor REAL,
    ValorPositivo REAL,
    TipoTransacao TEXT,
    TipoGasto TEXT,
    GRUPO TEXT,
    SUBGRUPO TEXT,
    CategoriaGeral TEXT,
    IdTransacao TEXT UNIQUE,
    IdParcela TEXT,
    parcela_atual INTEGER,
    TotalParcelas INTEGER,
    arquivo_origem TEXT,
    banco_origem TEXT,
    tipodocumento TEXT,
    origem_classificacao TEXT,
    session_id TEXT,
    upload_history_id INTEGER,
    MesFatura TEXT,
    Ano INTEGER,
    Mes INTEGER,
    created_at TIMESTAMP,
    NomeCartao TEXT,
    IgnorarDashboard INTEGER DEFAULT 0,
    -- ❌ Removido: categoria_orcamento_id
    FOREIGN KEY (upload_history_id) REFERENCES upload_history(id)
);

-- 4. Copiar dados
INSERT INTO journal_entries_new 
SELECT 
    id, user_id, Data, Estabelecimento, EstabelecimentoBase,
    Valor, ValorPositivo, TipoTransacao, TipoGasto, GRUPO,
    SUBGRUPO, CategoriaGeral, IdTransacao, IdParcela,
    parcela_atual, TotalParcelas, arquivo_origem, banco_origem,
    tipodocumento, origem_classificacao, session_id,
    upload_history_id, MesFatura, Ano, Mes, created_at,
    NomeCartao, IgnorarDashboard
FROM journal_entries;

-- 5. Drop tabela antiga
DROP TABLE journal_entries;

-- 6. Renomear nova
ALTER TABLE journal_entries_new RENAME TO journal_entries;

-- 7. Recriar indexes
CREATE INDEX idx_journal_user ON journal_entries(user_id);
CREATE INDEX idx_journal_session ON journal_entries(session_id);
CREATE INDEX idx_journal_upload ON journal_entries(upload_history_id);
CREATE UNIQUE INDEX idx_journal_idtransacao ON journal_entries(IdTransacao);

-- 8. Validar
SELECT COUNT(*) FROM journal_entries;
-- Deve ter a mesma quantidade de antes

.exit
```

**9. Atualizar modelo Python:**
```python
# app_dev/backend/app/domains/transactions/models.py
# Remover linha:
# categoria_orcamento_id = Column(Integer, index=True, nullable=True)
```

**10. Reiniciar servidores:**
```bash
./scripts/deploy/quick_stop.sh && sleep 2 && ./scripts/deploy/quick_start.sh
```

---

## 3. Testes - 3 Faturas MercadoPago

### Arquivos Disponíveis
```
_arquivos_historicos/_csvs_historico/
├── MP202501.xlsx
├── MP202502.xlsx
├── MP202503.xlsx
```

---

### 3.1 Upload #1 - MercadoPago Janeiro (MP202501.xlsx)

#### Frontend - Via Browser

1. Acessar: http://localhost:3000/upload
2. Login com `teste_aprendizado@teste.com`
3. Preencher formulário:
   - Banco: MercadoPago
   - Tipo: Fatura
   - Cartão: Gold
   - Mês: 2025-01
   - Arquivo: MP202501.xlsx
4. Clicar "Processar"
5. Aguardar preview (pode demorar ~10-20s)

#### Observar Preview

**Estatísticas esperadas:**
- Total transações: ~150
- **Base Genérica:** ~145 (97%)
- **Base Padrões:** 0 (0%) ← Ainda não aprendeu!
- **Não Classificado:** ~5 (3%)

**Por quê Base Padrões = 0?**
- Fase 0 regenera padrões MAS não há journal_entries ainda
- base_padroes do usuário está vazia
- Sistema volta para Base Genérica (86 regras)

**Ações no Preview:**
1. Revisar classificações
2. Editar se necessário (opcional)
3. **Confirmar Upload**

#### Validações SQL (Após Confirmar)

```sql
-- 1. Upload registrado
SELECT * FROM upload_history WHERE user_id = 5 ORDER BY id DESC LIMIT 1;
-- Anotar: upload_history_id = ?

-- 2. Transações salvas
SELECT COUNT(*) FROM journal_entries WHERE user_id = 5;
-- Esperado: ~145 (sem duplicadas)

-- 3. Base Padrões CRIADA ✅
SELECT COUNT(*) FROM base_padroes WHERE user_id = 5;
-- Esperado: 20-40 padrões (estabelecimentos únicos com ≥2 ocorrências)

SELECT padrao_estabelecimento, contagem, confianca 
FROM base_padroes 
WHERE user_id = 5 
ORDER BY contagem DESC LIMIT 10;
-- Ver: Netflix, Spotify, Uber, etc

-- 4. Base Parcelas
SELECT COUNT(*) FROM base_parcelas WHERE user_id = 5 AND status = 'ativa';
-- Esperado: 5-15 (parcelamentos ativos)

SELECT estabelecimento_base, qtd_parcelas, qtd_pagas 
FROM base_parcelas 
WHERE user_id = 5 
ORDER BY qtd_parcelas DESC LIMIT 10;
```

**Anotar resultados:**
- ✅ Upload 1: `___ transações, ___ padrões criados, ___ parcelas ativas`

---

### 3.2 Upload #2 - MercadoPago Fevereiro (MP202502.xlsx)

#### Repetir Processo Upload

1. http://localhost:3000/upload
2. Arquivo: MP202502.xlsx
3. Mês: 2025-02
4. Processar

#### Observar Preview - APRENDIZADO! 🎯

**Estatísticas esperadas (MELHORIA!):**
- Total: ~150
- **Base Genérica:** ~120 (80%)
- **Base Padrões:** ~25 (17%) ← APRENDEU! ✨
- **Não Classificado:** ~5 (3%)

**Por quê Base Padrões aumentou?**
- Fase 0 **regenerou** padrões com dados do Upload 1
- Sistema encontrou ~20-30 padrões com alta confiança
- Estabelecimentos recorrentes agora são classificados por padrão!

**Exemplos de Padrões Aprendidos:**
- `NETFLIX` → Assinaturas, Streaming
- `UBER` → Transporte, App Transporte
- `MERCADO PAGO *IFOOD` → Alimentação, Delivery

#### Confirmar Upload

#### Validações SQL (Após Confirmar)

```sql
-- 1. Total acumulado
SELECT COUNT(*) FROM journal_entries WHERE user_id = 5;
-- Esperado: ~290 (upload 1 + upload 2)

-- 2. Base Padrões ATUALIZADA ✅
SELECT COUNT(*) FROM base_padroes WHERE user_id = 5;
-- Esperado: 35-60 padrões (mais que upload 1)

SELECT padrao_estabelecimento, contagem, confianca 
FROM base_padroes 
WHERE user_id = 5 
ORDER BY contagem DESC LIMIT 10;
-- Ver: contagem aumentou (2→3, 3→4, etc)

-- 3. Parcelas ATUALIZADAS ✅
SELECT estabelecimento_base, qtd_pagas, qtd_parcelas, status
FROM base_parcelas 
WHERE user_id = 5 
ORDER BY qtd_pagas DESC LIMIT 10;
-- Ver: qtd_pagas incrementou (1→2, 2→3)

-- 4. Parcelas finalizadas?
SELECT COUNT(*) FROM base_parcelas 
WHERE user_id = 5 AND status = 'finalizado';
-- Esperado: 0-2 (se alguma parcela 2/2 foi paga)
```

**Anotar resultados:**
- ✅ Upload 2: `___ transações, ___ padrões (___%), ___ parcelas atualizadas`

---

### 3.3 Upload #3 - MercadoPago Março (MP202503.xlsx)

#### Repetir Processo Upload

1. http://localhost:3000/upload
2. Arquivo: MP202503.xlsx
3. Mês: 2025-03
4. Processar

#### Observar Preview - CONSOLIDAÇÃO! 🎉

**Estatísticas esperadas (CONSOLIDADO!):**
- Total: ~150
- **Base Genérica:** ~105 (70%)
- **Base Padrões:** ~40 (27%) ← CONSOLIDOU! 🎯
- **Não Classificado:** ~5 (3%)

**Evolução:**
- Upload 1: Base Padrões 0%
- Upload 2: Base Padrões 17%
- Upload 3: Base Padrões **27%** ← Sistema aprendeu!

#### Confirmar Upload

#### Validações SQL (Após Confirmar)

```sql
-- 1. Total acumulado
SELECT COUNT(*) FROM journal_entries WHERE user_id = 5;
-- Esperado: ~435 (3 uploads)

-- 2. Base Padrões CONSOLIDADA ✅
SELECT COUNT(*) FROM base_padroes WHERE user_id = 5;
-- Esperado: 50-80 padrões

SELECT padrao_estabelecimento, contagem, confianca, valor_medio
FROM base_padroes 
WHERE user_id = 5 
ORDER BY contagem DESC LIMIT 15;
-- Ver: contagem 3+ (ocorreu em todos os uploads)

-- 3. Parcelas finalizadas
SELECT COUNT(*) FROM base_parcelas 
WHERE user_id = 5 AND status = 'finalizado';
-- Esperado: 3-5 (parcelas 3/3 concluídas)

SELECT estabelecimento_base, qtd_pagas, qtd_parcelas, status
FROM base_parcelas 
WHERE user_id = 5 AND status = 'finalizado';
-- Ver: parcelamentos completos
```

**Anotar resultados:**
- ✅ Upload 3: `___ transações, ___ padrões (___%), ___ parcelas finalizadas`

---

## 4. Testes - 3 Faturas Itaú

### Arquivos Disponíveis
```
_arquivos_historicos/_csvs_historico/
├── fatura_itau-202510.csv
├── fatura_itau-202511.csv
├── fatura_itau-202512.csv
```

**Nota:** Arquivos são de 2025 (outubro, novembro, dezembro)

---

### 4.1 Upload #4 - Itaú Outubro (fatura_itau-202510.csv)

#### Frontend Upload

1. http://localhost:3000/upload
2. Formulário:
   - Banco: Itaú
   - Tipo: Fatura
   - Cartão: Platinum
   - Mês: 2025-10
   - Arquivo: fatura_itau-202510.csv
3. Processar

#### Observar Preview

**Esperado:**
- Novo banco (Itaú) tem padrões diferentes de MercadoPago
- **Base Padrões:** ~15-20% (alguns estabelecimentos comuns: Netflix, Uber, etc)
- **Base Genérica:** ~75-80%

**Por quê Base Padrões funciona?**
- Estabelecimentos comuns entre bancos (Netflix, Spotify, etc)
- Sistema já aprendeu esses padrões com MercadoPago

#### Confirmar Upload

#### Validações SQL

```sql
-- 1. Total acumulado (MP + Itaú)
SELECT COUNT(*) FROM journal_entries WHERE user_id = 5;
-- Esperado: ~500-600

-- 2. Padrões POR BANCO
SELECT banco_origem, COUNT(*) 
FROM journal_entries 
WHERE user_id = 5 
GROUP BY banco_origem;
-- Ver: MercadoPago ~435, Itaú ~80

-- 3. Base Padrões atualizada com Itaú
SELECT COUNT(*) FROM base_padroes WHERE user_id = 5;
-- Esperado: 60-90 (novos estabelecimentos Itaú)
```

---

### 4.2 Upload #5 - Itaú Novembro (fatura_itau-202511.csv)

#### Repetir Upload

1. Arquivo: fatura_itau-202511.csv
2. Mês: 2025-11
3. Processar

#### Observar Aprendizado Itaú

**Esperado:**
- **Base Padrões Itaú:** ~25-30% (aprendeu do upload anterior!)
- Sistema está aprendendo padrões específicos do Itaú

#### Confirmar e Validar

```sql
-- Contagem por origem de classificação (últimos 2 uploads Itaú)
SELECT origem_classificacao, COUNT(*) 
FROM journal_entries 
WHERE user_id = 5 AND banco_origem = 'Itaú'
GROUP BY origem_classificacao;
```

---

### 4.3 Upload #6 - Itaú Dezembro (fatura_itau-202512.csv)

#### Repetir Upload

1. Arquivo: fatura_itau-202512.csv
2. Mês: 2025-12
3. Processar

#### Observar Consolidação Multi-Banco

**Esperado:**
- **Base Padrões:** ~30-35% (consolidado Itaú + MP)
- Sistema aprendeu padrões de AMBOS os bancos

#### Validações Finais

```sql
-- 1. Total final
SELECT COUNT(*) FROM journal_entries WHERE user_id = 5;
-- Esperado: ~670-750

-- 2. Distribuição por banco
SELECT banco_origem, COUNT(*), 
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
FROM journal_entries 
WHERE user_id = 5 
GROUP BY banco_origem;

-- 3. Padrões finais
SELECT COUNT(*) FROM base_padroes WHERE user_id = 5;
-- Esperado: 80-120 padrões

-- 4. Padrões mais frequentes
SELECT padrao_estabelecimento, contagem, confianca
FROM base_padroes 
WHERE user_id = 5 
ORDER BY contagem DESC LIMIT 20;
-- Ver: estabelecimentos recorrentes
```

---

## 5. Validações SQL

### 5.1 Evolução de Base Padrões

```sql
-- Ver crescimento de padrões ao longo dos uploads
SELECT 
    uh.nome_arquivo,
    uh.data_confirmacao,
    COUNT(DISTINCT bp.id) as total_padroes,
    AVG(bp.contagem) as media_contagem
FROM upload_history uh
LEFT JOIN base_padroes bp ON bp.user_id = uh.user_id
WHERE uh.user_id = 5
GROUP BY uh.id
ORDER BY uh.data_confirmacao;
```

### 5.2 Origem de Classificação por Upload

```sql
-- Estatísticas detalhadas por upload
SELECT 
    uh.nome_arquivo,
    je.origem_classificacao,
    COUNT(*) as qtd,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY uh.id), 2) as percentual
FROM upload_history uh
JOIN journal_entries je ON je.upload_history_id = uh.id
WHERE uh.user_id = 5
GROUP BY uh.id, je.origem_classificacao
ORDER BY uh.data_confirmacao, je.origem_classificacao;
```

**Resultado esperado:**
```
| Arquivo          | Origem           | Qtd | % |
|------------------|------------------|-----|---|
| MP202501.xlsx    | Base Genérica    | 145 | 97|
| MP202501.xlsx    | Não Classificado | 5   | 3 |
| MP202502.xlsx    | Base Genérica    | 120 | 80|
| MP202502.xlsx    | Base Padrões     | 25  | 17|
| MP202502.xlsx    | Não Classificado | 5   | 3 |
| MP202503.xlsx    | Base Genérica    | 105 | 70|
| MP202503.xlsx    | Base Padrões     | 40  | 27|
| MP202503.xlsx    | Não Classificado | 5   | 3 |
...
```

### 5.3 Parcelas - Evolução

```sql
-- Ver parcelas sendo pagas progressivamente
SELECT 
    estabelecimento_base,
    qtd_parcelas,
    qtd_pagas,
    status,
    ROUND(qtd_pagas * 100.0 / qtd_parcelas, 0) as percentual_pago
FROM base_parcelas
WHERE user_id = 5
ORDER BY qtd_pagas DESC, estabelecimento_base
LIMIT 20;
```

### 5.4 Padrões com Alta Confiança

```sql
-- Padrões consolidados (≥3 ocorrências)
SELECT 
    padrao_estabelecimento,
    contagem,
    confianca,
    valor_medio,
    grupo_sugerido,
    subgrupo_sugerido
FROM base_padroes
WHERE user_id = 5 AND contagem >= 3
ORDER BY contagem DESC;
```

---

## 6. Análise de Resultados

### 6.1 Planilha de Resultados

**Criar em:** `docs/finalizacao/05_teste_user_inicial/RESULTADOS_TESTES.md`

```markdown
# Resultados Testes de Upload - Aprendizado

## Upload 1 - MP202501.xlsx
- Data: __/__/2026 __:__
- Transações: ___
- Base Genérica: ___ (___%)
- Base Padrões: 0 (0%)
- Não Classificado: ___ (___%)
- Padrões criados: ___
- Parcelas ativas: ___

## Upload 2 - MP202502.xlsx
- Data: __/__/2026 __:__
- Transações: ___
- Base Genérica: ___ (___%)
- Base Padrões: ___ (___%) ← APRENDIZADO!
- Não Classificado: ___ (___%)
- Padrões atualizados: ___
- Parcelas atualizadas: ___

## Upload 3 - MP202503.xlsx
- Data: __/__/2026 __:__
- Transações: ___
- Base Genérica: ___ (___%)
- Base Padrões: ___ (___%) ← CONSOLIDAÇÃO!
- Não Classificado: ___ (___%)
- Padrões consolidados: ___
- Parcelas finalizadas: ___

## Upload 4-6 - Faturas Itaú
- (Repetir formato acima)

## Conclusões
- ✅ Base Padrões funciona? Sim/Não
- ✅ Aprendizado progressivo? Sim/Não
- ✅ Parcelas atualizadas? Sim/Não
- ⚠️ Problemas encontrados: ...
```

---

### 6.2 Screenshots

**Capturar:**
1. Preview Upload 1 (0% Base Padrões)
2. Preview Upload 2 (15-20% Base Padrões)
3. Preview Upload 3 (25-30% Base Padrões)
4. SQL: Base Padrões crescendo
5. SQL: Parcelas sendo finalizadas

**Salvar em:** `docs/finalizacao/05_teste_user_inicial/screenshots/`

---

### 6.3 Problemas Comuns

#### Fase 0 não executa

**Sintoma:** Base Padrões sempre 0%

**Verificar:**
```bash
# Logs do backend
tail -f temp/logs/backend.log | grep "Fase 0"
# Deve ver: "🔄 Fase 0: Regeneração de Base Padrões"
```

**Solução:** Ver `service.py` linha 123

---

#### Classificação não melhora

**Sintoma:** Base Padrões sempre baixo (~5%)

**Verificar:**
```sql
SELECT COUNT(*) FROM base_padroes 
WHERE user_id = 5 AND confianca = 'alta';
-- Deve ter 20+ padrões
```

**Solução:** 
- Verificar se `confianca = 'alta'` (classifier só usa alta)
- Verificar `percentual_consistencia >= 95`

---

#### Parcelas não atualizam

**Sintoma:** qtd_pagas não incrementa

**Verificar:** `service.py` linha 1008 - `_fase5_update_base_parcelas()`

---

## 7. Testes de Funcionalidades Completas

### 7.1 Dashboard - Visualizações e Filtros

#### Acessar Dashboard
```
URL: http://localhost:3000/mobile/dashboard
```

**Testes:**

1. **Visualização Inicial (Mês Atual)**
   - [ ] Dashboard carrega sem erros
   - [ ] Mostra transações dos 6 uploads
   - [ ] Cards de resumo corretos (Receitas, Despesas, Saldo)
   - [ ] Gráfico de despesas por categoria
   - [ ] Gráfico de evolução mensal

2. **Filtro de Mês**
   - [ ] Dropdown de meses funciona
   - [ ] Selecionar Janeiro/2025 → Mostra apenas transações de MP202501
   - [ ] Selecionar Fevereiro/2025 → Mostra MP202502
   - [ ] Selecionar Março/2025 → Mostra MP202503
   - [ ] Selecionar Outubro/2025 → Mostra fatura_itau-202510
   - [ ] Selecionar Novembro/2025 → Mostra fatura_itau-202511
   - [ ] Selecionar Dezembro/2025 → Mostra fatura_itau-202512
   - [ ] Valores do resumo atualizam corretamente

3. **Filtro de Categoria**
   - [ ] Clicar em categoria no gráfico → Filtra transações
   - [ ] Filtrar "Alimentação" → Mostra apenas transações dessa categoria
   - [ ] Filtrar "Transporte" → Mostra apenas Uber, transporte público, etc
   - [ ] Limpar filtro → Volta para todas as transações

4. **Filtro de Tipo (Receita/Despesa)**
   - [ ] Alternar entre Receitas/Despesas/Todos
   - [ ] Valores recalculados corretamente
   - [ ] Gráficos atualizam

**SQL de Validação:**
```sql
-- Total por mês
SELECT 
    Ano, Mes, 
    COUNT(*) as transacoes,
    SUM(CASE WHEN CategoriaGeral = 'Despesa' THEN ValorPositivo ELSE 0 END) as despesas,
    SUM(CASE WHEN CategoriaGeral = 'Receita' THEN ValorPositivo ELSE 0 END) as receitas
FROM journal_entries
WHERE user_id = 5
GROUP BY Ano, Mes
ORDER BY Ano, Mes;

-- Total por categoria
SELECT 
    GRUPO,
    COUNT(*) as transacoes,
    SUM(ValorPositivo) as total
FROM journal_entries
WHERE user_id = 5 AND CategoriaGeral = 'Despesa'
GROUP BY GRUPO
ORDER BY total DESC;
```

---

### 7.2 Metas/Budget - Criar e Editar

#### Acessar Tela de Metas
```
URL: http://localhost:3000/mobile/budget
```

**Testes:**

1. **Visualização Inicial**
   - [ ] Tela carrega sem erros
   - [ ] Mostra grupos de despesa
   - [ ] Campos de metas vazios (usuário novo)
   - [ ] Dropdown de mês funciona

2. **Criar Meta Individual**
   - [ ] Selecionar mês: Janeiro/2026
   - [ ] Clicar em "Alimentação"
   - [ ] Definir meta: R$ 1.500,00
   - [ ] Salvar
   - [ ] Valor persiste ao recarregar página
   - [ ] Dashboard mostra comparação meta vs real

3. **Criar Meta para Ano Completo**
   - [ ] Botão "Criar Metas para o Ano" visível
   - [ ] Clicar no botão
   - [ ] Modal abre com lista de grupos
   - [ ] Preencher valores:
     ```
     Alimentação: 1500
     Transporte: 500
     Casa: 2000
     Lazer: 800
     Saúde: 600
     Educação: 400
     Vestuário: 300
     Outros: 200
     ```
   - [ ] Aplicar para todos os 12 meses de 2026
   - [ ] Confirmar
   - [ ] Progresso: "Criando 96 metas..." (8 grupos × 12 meses)
   - [ ] Sucesso: Metas criadas

4. **Validar Metas Criadas**
   - [ ] Alternar entre meses (Jan, Fev, Mar...)
   - [ ] Todos têm os valores definidos
   - [ ] SQL validação:
     ```sql
     SELECT Ano, Mes, COUNT(*) as total_metas
     FROM budget_geral
     WHERE user_id = 5 AND Ano = 2026
     GROUP BY Ano, Mes;
     -- Deve retornar 12 linhas com ~8 metas cada
     ```

5. **Editar Meta Existente**
   - [ ] Selecionar Fevereiro/2026
   - [ ] Clicar em "Alimentação" (meta: 1500)
   - [ ] Alterar para: R$ 1.800,00
   - [ ] Salvar
   - [ ] Recarregar → Valor atualizado
   - [ ] SQL validação:
     ```sql
     SELECT * FROM budget_geral
     WHERE user_id = 5 AND Ano = 2026 AND Mes = 2 AND Grupo = 'Alimentação';
     -- Meta deve ser 1800
     ```

6. **Dashboard com Metas**
   - [ ] Voltar ao dashboard
   - [ ] Selecionar mês com meta (ex: Janeiro/2026)
   - [ ] Cards mostram "Meta: R$ X.XXX"
   - [ ] Indicador de progresso (% gasto da meta)
   - [ ] Cores: Verde (OK), Amarelo (90%), Vermelho (>100%)

---

### 7.3 Transações - Listar, Filtrar, Editar

#### Acessar Tela de Transações
```
URL: http://localhost:3000/mobile/transactions
```

**Testes:**

1. **Listagem Inicial**
   - [ ] Carrega lista de transações
   - [ ] Mostra ~670-750 transações (6 uploads)
   - [ ] Paginação funciona (50 por página)
   - [ ] Ordem: Mais recentes primeiro

2. **Filtro por Estabelecimento**
   - [ ] Buscar: "NETFLIX"
   - [ ] Mostra apenas transações Netflix
   - [ ] Validar: 3-6 transações (Janeiro a Dezembro)
   - [ ] Limpar filtro

3. **Filtro por Categoria**
   - [ ] Dropdown "Categoria"
   - [ ] Selecionar "Alimentação"
   - [ ] Lista filtra apenas Alimentação
   - [ ] Contador atualiza

4. **Filtro por Mês**
   - [ ] Dropdown "Mês/Ano"
   - [ ] Selecionar "Janeiro/2025"
   - [ ] Mostra apenas transações de Janeiro (upload MP202501)
   - [ ] Validar quantidade (~145 transações)

5. **Filtro por Banco/Cartão**
   - [ ] Dropdown "Banco"
   - [ ] Selecionar "MercadoPago"
   - [ ] Mostra ~435 transações (3 uploads MP)
   - [ ] Selecionar "Itaú"
   - [ ] Mostra ~235 transações (3 uploads Itaú)

6. **Filtro Combinado**
   - [ ] Mês: Outubro/2025
   - [ ] Categoria: Transporte
   - [ ] Banco: Itaú
   - [ ] Lista filtra corretamente
   - [ ] SQL esperado:
     ```sql
     SELECT COUNT(*) FROM journal_entries
     WHERE user_id = 5 
       AND Ano = 2025 AND Mes = 10
       AND GRUPO = 'Transporte'
       AND banco_origem = 'Itaú';
     ```

7. **Editar Transação**
   - [ ] Clicar em transação específica
   - [ ] Modal de edição abre
   - [ ] Campos carregam valores atuais
   - [ ] Alterar:
     - Categoria: Alimentação → Lazer
     - Subcategoria: Restaurante → Entretenimento
   - [ ] Salvar
   - [ ] Modal fecha
   - [ ] Lista atualiza (categoria mudou)
   - [ ] Recarregar página → Mudança persiste

8. **Editar Valor da Transação**
   - [ ] Abrir transação
   - [ ] Alterar valor: R$ 50,00 → R$ 55,00
   - [ ] Salvar
   - [ ] Dashboard recalcula totais automaticamente
   - [ ] SQL validação:
     ```sql
     SELECT * FROM journal_entries
     WHERE user_id = 5 AND IdTransacao = '<id_editado>';
     -- Valor deve ser 55.00
     ```

9. **Excluir Transação**
   - [ ] Abrir transação
   - [ ] Botão "Excluir" visível
   - [ ] Clicar em Excluir
   - [ ] Modal de confirmação
   - [ ] Confirmar exclusão
   - [ ] Transação removida da lista
   - [ ] SQL validação:
     ```sql
     SELECT * FROM transacoes_exclusao
     WHERE user_id = 5 AND IdTransacao = '<id_excluido>';
     -- Deve ter registro (soft delete)
     ```

---

### 7.4 Cartões - Gerenciamento

#### Acessar Tela de Cartões
```
URL: http://localhost:3000/mobile/cards
```

**Testes:**

1. **Listagem Inicial**
   - [ ] Mostra cartões usados nos uploads:
     - Gold (MercadoPago)
     - Platinum (Itaú)
   - [ ] Detalhes: Banco, últimos 4 dígitos, status

2. **Criar Novo Cartão**
   - [ ] Botão "Adicionar Cartão"
   - [ ] Modal abre
   - [ ] Preencher:
     - Nome: Visa Internacional
     - Banco: Nubank
     - Últimos 4 dígitos: 9876
     - Cor: Roxo
     - Status: Ativo
   - [ ] Salvar
   - [ ] Cartão aparece na lista

3. **Editar Cartão**
   - [ ] Clicar no cartão Gold
   - [ ] Editar nome: "Gold" → "Gold Premium"
   - [ ] Alterar cor
   - [ ] Salvar
   - [ ] Lista atualiza

4. **Desativar Cartão**
   - [ ] Clicar em cartão
   - [ ] Toggle "Ativo" → "Inativo"
   - [ ] Salvar
   - [ ] Cartão aparece como inativo
   - [ ] Não aparece no dropdown de upload

---

### 7.5 Navegação e Telas Adicionais

#### Testes de Navegação

1. **Menu Lateral (Sidebar)**
   - [ ] Dashboard → Abre dashboard
   - [ ] Transações → Abre lista
   - [ ] Upload → Abre formulário
   - [ ] Metas → Abre budget
   - [ ] Cartões → Abre gestão de cartões
   - [ ] Perfil → Abre perfil do usuário
   - [ ] Investimentos → Abre tela de investimentos (se existir)
   - [ ] Configurações → Abre settings

2. **Navegação via URL Direta**
   - [ ] /mobile/dashboard → Carrega
   - [ ] /mobile/transactions → Carrega
   - [ ] /mobile/upload → Carrega
   - [ ] /mobile/budget → Carrega
   - [ ] /mobile/cards → Carrega
   - [ ] /mobile/profile → Carrega (futura)

3. **Autenticação**
   - [ ] Logout funciona
   - [ ] Acessar rota protegida sem login → Redirect para /login
   - [ ] Login novamente funciona

---

### 7.6 Telas Admin (se usuário for admin)

**Nota:** Usuário `teste_aprendizado@teste.com` é `role=user`. Se quiser testar admin:

```bash
# Promover usuário para admin
sqlite3 app_dev/backend/database/financas_dev.db
UPDATE users SET role = 'admin' WHERE email = 'teste_aprendizado@teste.com';
.exit
```

#### Testes Admin (após promover)

1. **Acessar Tela Admin**
   - [ ] URL: http://localhost:3000/admin
   - [ ] Carrega dashboard admin
   - [ ] Mostra estatísticas globais

2. **Gerenciar Usuários**
   - [ ] URL: http://localhost:3000/admin/users
   - [ ] Lista todos os usuários
   - [ ] Pode editar usuários
   - [ ] Pode desativar/ativar

3. **Bases de Configuração**
   - [ ] URL: http://localhost:3000/admin/bases
   - [ ] Editar base_grupos_config
   - [ ] Editar base_marcacoes
   - [ ] Editar generic_classification_rules

---

### 7.7 Validações Cruzadas

#### Consistência de Dados

1. **Dashboard vs SQL**
   ```sql
   -- Totais do dashboard devem bater com SQL
   SELECT 
       SUM(CASE WHEN CategoriaGeral = 'Despesa' THEN ValorPositivo ELSE 0 END) as total_despesas,
       SUM(CASE WHEN CategoriaGeral = 'Receita' THEN ValorPositivo ELSE 0 END) as total_receitas
   FROM journal_entries
   WHERE user_id = 5 
     AND Ano = 2025 AND Mes = 1;
   ```

2. **Metas vs SQL**
   ```sql
   -- Budget salvo deve bater com tela
   SELECT Grupo, Meta
   FROM budget_geral
   WHERE user_id = 5 AND Ano = 2026 AND Mes = 1;
   ```

3. **Transações Editadas**
   ```sql
   -- Verificar audit trail (se existir)
   SELECT * FROM journal_entries_history
   WHERE user_id = 5
   ORDER BY updated_at DESC;
   ```

---

### 7.8 Performance e UX

**Testes Subjetivos:**

1. **Velocidade de Carregamento**
   - [ ] Dashboard carrega em < 2 segundos
   - [ ] Lista de transações carrega em < 1 segundo
   - [ ] Filtros aplicam em < 500ms

2. **Responsividade Mobile**
   - [ ] Abrir em mobile (Chrome DevTools)
   - [ ] Layout adapta corretamente
   - [ ] Botões clicáveis
   - [ ] Texto legível

3. **Erros e Loading States**
   - [ ] Loading spinners aparecem durante requests
   - [ ] Erros mostram mensagens amigáveis
   - [ ] Toasts de sucesso/erro funcionam

---

## 8. Checklist Final Completo

### Preparação
- [ ] ✅ Servidores rodando
- [ ] ✅ Usuário de teste criado
- [ ] ✅ Token guardado
- [ ] ✅ Estado inicial limpo (zero dados)

### Ajuste Journal Entries (Opcional)
- [ ] Decidir se remove categoria_orcamento_id
- [ ] Backup criado
- [ ] Campo removido (se aplicável)
- [ ] Servidores reiniciados

### Testes MercadoPago
- [ ] Upload 1 (MP202501) - Base Padrões criada
- [ ] Upload 2 (MP202502) - Aprendizado (15-20%)
- [ ] Upload 3 (MP202503) - Consolidação (25-30%)
- [ ] SQL validado

### Testes Itaú
- [ ] Upload 4 (fatura_itau-202510)
- [ ] Upload 5 (fatura_itau-202511)
- [ ] Upload 6 (fatura_itau-202512)
- [ ] SQL validado

### Validações
- [ ] Queries SQL executadas
- [ ] Planilha de resultados preenchida
- [ ] Screenshots capturadas
- [ ] Problemas documentados

### Testes de Funcionalidades
- [ ] Dashboard - Filtros de mês testados
- [ ] Dashboard - Filtros de categoria testados
- [ ] Metas - Criação individual testada
- [ ] Metas - Criação ano completo testada
- [ ] Metas - Edição testada
- [ ] Transações - Listagem testada
- [ ] Transações - Filtros combinados testados
- [ ] Transações - Edição testada
- [ ] Transações - Exclusão testada
- [ ] Cartões - Listagem testada
- [ ] Cartões - Criação testada
- [ ] Cartões - Edição testada
- [ ] Navegação - Todas as rotas testadas
- [ ] Performance - Carregamento aceitável
- [ ] Mobile - Layout responsivo

### Documentação
- [ ] RESULTADOS_TESTES.md criado
- [ ] Screenshots organizadas
- [ ] Bugs encontrados documentados
- [ ] Frente 5.2 atualizada como ✅ CONCLUÍDA

---

## 9. Template de Relatório de Testes

**Criar:** `docs/finalizacao/05_teste_user_inicial/RELATORIO_TESTES_COMPLETO.md`

```markdown
# Relatório de Testes - Usuário teste_aprendizado@teste.com

## Data: __/__/2026

## 1. Uploads (6 arquivos)

### Upload 1 - MP202501.xlsx
- Status: ✅ Sucesso / ❌ Erro
- Transações: ___
- Base Padrões: 0%
- Tempo: __ minutos
- Problemas: Nenhum / [Descrição]

### Upload 2 - MP202502.xlsx
- Status: ✅/❌
- Transações: ___
- Base Padrões: ___%
- Aprendizado detectado: ✅ Sim / ❌ Não
- Problemas: 

[... repetir para uploads 3-6 ...]

## 2. Dashboard

### Filtro de Mês
- ✅ Funcionou / ❌ Erro
- Problema: [se houver]

### Filtro de Categoria
- ✅ Funcionou / ❌ Erro
- Problema: 

### Gráficos
- Despesas por categoria: ✅/❌
- Evolução temporal: ✅/❌
- Budget vs Real: ✅/❌

## 3. Metas/Budget

### Criar Meta Individual
- ✅ Funcionou / ❌ Erro
- Valor persistiu: ✅/❌

### Criar Metas Ano Completo
- ✅ Sucesso / ❌ Falhou
- Tempo de processamento: __ segundos
- Total criado: __ metas
- SQL validado: ✅/❌

### Editar Meta
- ✅ Funcionou / ❌ Erro

## 4. Transações

### Listagem
- ✅ Carregou / ❌ Erro
- Quantidade correta: ✅/❌
- Performance: ✅ Rápido / ⚠️ Lento

### Filtros
- Por estabelecimento: ✅/❌
- Por categoria: ✅/❌
- Por mês: ✅/❌
- Por banco: ✅/❌
- Combinados: ✅/❌

### Edição
- Alterar categoria: ✅/❌
- Alterar valor: ✅/❌
- Dashboard atualizou: ✅/❌

### Exclusão
- Soft delete funcionou: ✅/❌
- Removeu da lista: ✅/❌

## 5. Cartões

### Listagem: ✅/❌
### Criar novo: ✅/❌
### Editar: ✅/❌
### Desativar: ✅/❌

## 6. Navegação

### Menu lateral: ✅/❌
### URLs diretas: ✅/❌
### Logout/Login: ✅/❌

## 7. Performance

- Dashboard: __ segundos
- Transações: __ segundos
- Upload: __ minutos (médio)

## 8. Responsividade Mobile

- Layout adapta: ✅/❌
- Botões clicáveis: ✅/❌
- Texto legível: ✅/❌

## 9. Bugs Encontrados

1. [Bug #1 - Descrição]
   - Gravidade: 🔴 Alta / 🟡 Média / 🟢 Baixa
   - Como reproduzir: ...
   - Esperado: ...
   - Obtido: ...

2. [Bug #2]
   ...

## 10. Sugestões de Melhoria

1. [Melhoria #1]
2. [Melhoria #2]

## 11. Conclusão

- Sistema funcional: ✅ Sim / ❌ Não
- Pronto para produção: ✅ Sim / ⚠️ Com ressalvas / ❌ Não
- Bloqueadores: Nenhum / [Lista]
- Próximos passos: [Lista]
```

---

**Tempo estimado TOTAL:** 5-7 horas (uploads + funcionalidades + análise)  
**Pré-requisito:** Servidores funcionando, arquivos CSV disponíveis  
**Resultado esperado:** 
- ✅ Upload com aprendizado validado (0% → 30% Base Padrões)
- ✅ Todas as funcionalidades principais testadas
- ✅ Bugs identificados e documentados
- ✅ Sistema aprovado ou lista de correções definida

