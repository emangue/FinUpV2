# 📋 BACKLOG DE VALIDAÇÕES - Database

**Data:** 03/01/2026  
**Status:** Aguardando validação

---

## ⏳ QUESTÃO 1: Lógica de Preenchimento do Campo `Ano`

### Contexto
O campo `Ano` não é simplesmente derivado de `Data`. A lógica é mais complexa:

### Regra Atual (a validar)
1. **Se origem = Extrato:**
   - `Ano` vem de `Data` (ano da transação)
   
2. **Se origem = Fatura:**
   - `Ano` vem de `DT_Fatura` (ano do faturamento)
   
3. **Se DT_Fatura vem do nome do arquivo:**
   - Usar `DT_Fatura` do nome do arquivo
   - Exemplo: "fatura_itau-202510.csv" → DT_Fatura = "202510", Ano = 2025
   
4. **Se não houver DT_Fatura no nome:**
   - **PROBLEMA:** Precisamos perguntar ao cliente durante o upload
   - Alternativa: Usar Data como fallback

### Problema Identificado
Atualmente temos **1.096 registros** onde Data/Ano/DT_Fatura estão inconsistentes.

Exemplos:
- ID 16: Data="16/12/2023", Ano=2024, DT_Fatura="202401"
- ID 23: Data="23/12/2023", Ano=2024, DT_Fatura="202401"

**Hipótese:** Compras de dez/2023 faturadas em jan/2024 → Ano foi preenchido com 2024 (ano da fatura)

### Questões a Validar

1. **Qual é a regra correta de preenchimento do Ano?**
   - [ ] Sempre usar ano de Data (transação)?
   - [ ] Sempre usar ano de DT_Fatura (faturamento)?
   - [ ] Depende do tipo (Extrato vs Fatura)?

2. **Para dashboards, qual ano usar?**
   - [ ] Ano da transação (quando gastou)?
   - [ ] Ano da fatura (quando pagou)?
   - [ ] Ambos (criar campo separado)?

3. **Durante upload, como definir DT_Fatura?**
   - [ ] Extrair do nome do arquivo?
   - [ ] Perguntar ao usuário?
   - [ ] Calcular a partir de Data?
   - [ ] Deixar o processador decidir?

4. **Devemos recalcular os 1.096 registros inconsistentes?**
   - [ ] Sim, usando regra X
   - [ ] Não, está correto assim
   - [ ] Criar campo adicional para não perder informação

### Ação Necessária
**ANTES de eliminar ou modificar o campo Ano:**
1. Validar lógica de preenchimento em todos os processadores
2. Verificar como é usado nos dashboards
3. Decidir se precisamos de campo adicional (AnoTransacao vs AnoFatura)
4. Documentar regra definitiva

### Arquivos a Revisar
- `app/utils/processors/*.py` - Como cada processador define Ano e DT_Fatura
- `app/blueprints/dashboard/routes.py` - Como Ano é usado em filtros
- `app/blueprints/upload/routes.py` - Lógica de upload e definição de DT_Fatura

---

## ⏳ QUESTÃO 2: Rastreabilidade do Arquivo de Origem

### Problema
Atualmente não temos coluna que armazene o **nome do arquivo original** que foi usado no upload.

**Exemplos de valores perdidos:**
- `origem = "Fatura - fatura_itau-202510.csv"` → Será padronizado para "Itaú"
- Perdemos informação de QUAL arquivo foi usado

### Proposta
Criar nova coluna `arquivo_origem` (TEXT):
```sql
ALTER TABLE journal_entries ADD COLUMN arquivo_origem TEXT;

-- Migrar dados existentes
UPDATE journal_entries SET arquivo_origem = origem 
WHERE origem LIKE '%-%' OR origem LIKE '%.%';

UPDATE journal_entries SET arquivo_origem = 'dado_historico'
WHERE arquivo_origem IS NULL;

-- Então padronizar origem
UPDATE journal_entries SET origem = 'Itaú' 
WHERE origem LIKE '%itau%' OR origem LIKE '%itaú%';
```

### Benefícios
- ✅ Rastreabilidade completa
- ✅ Facilita auditoria
- ✅ Permite reprocessamento se necessário
- ✅ Histórico de uploads

### Ação Necessária
- [ ] Aprovar criação da coluna `arquivo_origem`
- [ ] Atualizar processadores para preencher essa coluna
- [ ] Atualizar validador para verificar preenchimento

---

## ⏳ QUESTÃO 3: Coluna `tipodocumento` - Manter ou Eliminar?

### Análise Atual
- **Preenchimento:** 3.1% (129 registros)
- **Valor único:** "Extrato"
- **Proposta inicial:** ELIMINAR (redundante)

### Questão do Usuário
> "tipodocumento não é usado em nenhum processo? Nem pra definir no upload se é um cartao ou extrato? Eu gosto da var, prefiro que ajustemos e marquemos no histórico que ela vá embora"

### Ação Necessária
1. ✅ **Verificar uso no código:**
   - [ ] Upload routes - usado para determinar se é cartão/extrato?
   - [ ] Processadores - usado para lógica de processamento?
   - [ ] Dashboards - usado para filtros?

2. ✅ **Se NÃO está sendo usado:**
   - [ ] MANTER a coluna (gosto do usuário)
   - [ ] Popular valores históricos
   - [ ] Valores possíveis: "Extrato", "Fatura", "Cartão"
   - [ ] Tornar obrigatória no upload futuro

3. ✅ **Se JÁ está sendo usado:**
   - [ ] Documentar uso
   - [ ] Manter e expandir valores

---

## ⏳ QUESTÃO 4: Merge de `MarcacaoIA` + `forma_classificacao`

### Proposta Inicial
Merge das duas colunas em `origem_classificacao`.

### Questão do Usuário
> "precisamos ajustar o projeto para que não impacte nada. para o merge da forma_classificacao, quero que você me mostre onde estão sendo usadas no processo e que isso não quebra nada e que não perdemos info."

### Ação Necessária
1. ✅ **Mapear uso no código:**
   - [ ] Onde `MarcacaoIA` é lida/escrita?
   - [ ] Onde `forma_classificacao` é lida/escrita?
   - [ ] Há queries que dependem desses campos?
   - [ ] Dashboards usam essas colunas?

2. ✅ **Validar que não quebra:**
   - [ ] Testar em ambiente dev
   - [ ] Verificar se há JOIN dependente
   - [ ] Validar que queries antigas ainda funcionam

3. ✅ **Garantir que não perde info:**
   - [ ] Mapear todos os valores únicos
   - [ ] Criar tabela de migração
   - [ ] Validar que merge preserva tudo

---

## 📋 RESUMO DE PRÓXIMOS PASSOS

### Imediato
1. ✅ Verificar uso de `tipodocumento` no código
2. ✅ Verificar uso de `MarcacaoIA` e `forma_classificacao` no código
3. ✅ Mapear como `Ano` é calculado em cada processador

### Após Verificação
4. ⏳ Decidir sobre campo `arquivo_origem` (adicionar ou não)
5. ⏳ Decidir sobre `tipodocumento` (popular valores históricos)
6. ⏳ Validar merge de colunas de classificação
7. ⏳ Documentar regra definitiva de `Ano` vs `DT_Fatura`

### Antes de Aplicar Mudanças
8. ⏳ Backup completo do banco
9. ⏳ Testar em ambiente dev
10. ⏳ Atualizar models.py
11. ⏳ Atualizar processadores
12. ⏳ Executar migração

---

**Status:** Aguardando verificações técnicas
