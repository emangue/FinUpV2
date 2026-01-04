# 📝 Checklist de Atualização de Código - Migração Concluída

## Status: ✅ MIGRAÇÃO SQL COMPLETA

**Banco de dados atualizado com sucesso:**
- ✅ tipodocumento: 0% NULL (4,153 registros populados)
- ✅ origem_classificacao: 0% NULL (4,153 registros populados)
- ✅ arquivo_origem: 0% NULL (4,153 registros populados)
- ✅ banco_origem: Padronizado (Itaú, BTG, Mercado Pago)
- ✅ Colunas renomeadas: MesFatura, banco_origem

---

## 📋 Arquivos que Precisam de Atualização de Código

### 1. ✅ app/models.py
**Status:** Atualizado automaticamente  
**Mudanças:**
- [x] Colunas atualizadas no JournalEntry
- [x] to_dict() atualizado

---

### 2. ⏳ app/blueprints/dashboard/routes.py (2 locais)

**Linhas 731-736:**
```python
# ANTES:
if transacao.forma_classificacao and transacao.forma_classificacao.startswith('Automática-'):
    transacao.forma_classificacao = 'Semi-Automática'
elif not transacao.forma_classificacao or transacao.forma_classificacao == 'Não Classificada':
    transacao.forma_classificacao = 'Manual'

# DEPOIS:
if transacao.origem_classificacao and transacao.origem_classificacao.startswith('Automática -'):
    transacao.origem_classificacao = 'Semi-Automática'
elif not transacao.origem_classificacao or transacao.origem_classificacao == 'Não Classificada':
    transacao.origem_classificacao = 'Manual'
```

**Linhas 824-829:**
```python
# ANTES:
if transacao.forma_classificacao and transacao.forma_classificacao.startswith('Automática-'):
    transacao.forma_classificacao = 'Semi-Automática'
elif not transacao.forma_classificacao or transacao.forma_classificacao == 'Não Classificada':
    transacao.forma_classificacao = 'Manual'

# DEPOIS:
if transacao.origem_classificacao and transacao.origem_classificacao.startswith('Automática -'):
    transacao.origem_classificacao = 'Semi-Automática'
elif not transacao.origem_classificacao or transacao.origem_classificacao == 'Não Classificada':
    transacao.origem_classificacao = 'Manual'
```

---

### 3. ⏳ app/blueprints/upload/routes.py (3 locais)

**Linha 691:**
```python
# ANTES:
forma_atual = transacoes[idx].get('forma_classificacao', 'Não Classificada')

# DEPOIS:
origem_class_atual = transacoes[idx].get('origem_classificacao', 'Não Classificada')
```

**Linha 705:**
```python
# ANTES:
transacoes[idx]['forma_classificacao'] = nova_forma

# DEPOIS:
transacoes[idx]['origem_classificacao'] = nova_origem_class
```

**Linha 817:**
```python
# ANTES:
forma_classificacao=trans.get('forma_classificacao', 'Não Classificada'),

# DEPOIS:
origem_classificacao=trans.get('origem_classificacao', 'Não Classificada'),
```

---

### 4. ⏳ app/blueprints/upload/classifiers/auto_classifier.py (7 locais)

**Atualizar valores da classificação:**

```python
# Valores no NOVO formato "Tipo - Origem":
'Automática - Base Padrões'    # Era: 'Automática-BasePadrão'
'Automática - Histórico'        # Era: 'Automática-Histórico'
'Automática - Palavras-chave'   # Era: 'Automática-PalavrasChave'
'Automática - Parcela'          # Era: 'Automática-IdParcela'
'Automática - Fatura'           # Era: 'Automática-FaturaCartão'
'Manual'                        # Mantém igual
'Não Classificada'              # Mantém igual
```

**Substituições:**
- `'forma_classificacao':` → `'origem_classificacao':`
- `'Automática-BasePadrão'` → `'Automática - Base Padrões'`
- `'Automática-Histórico'` → `'Automática - Histórico'`
- `'Automática-PalavrasChave'` → `'Automática - Palavras-chave'`
- `'Automática-IdParcela'` → `'Automática - Parcela'`
- `'Automática-FaturaCartão'` → `'Automática - Fatura'`
- `'Automática-IgnorarTitular'` → `'Automática - Ignorar Titular'`
- `'Automática-IgnorarLista'` → `'Automática - Ignorar Lista'`

---

### 5. ⏳ app/blueprints/upload/processors/fatura_cartao.py

**Substituições:**
- Linha 164: `'forma_classificacao': 'Não Classificada'` → `'origem_classificacao': 'Não Classificada'`
- Linha 165: `'MarcacaoIA': None` → Remover (não precisa mais)
- Linha 243: `'forma_classificacao': 'Não Classificada'` → `'origem_classificacao': 'Não Classificada'`
- Linha 244: `'MarcacaoIA': None` → Remover

**Também atualizar:**
- `'DT_Fatura':` → `'MesFatura':`
- `'origem':` → `'banco_origem':`
- `'banco':` → Remover (obsoleto)
- `'tipodocumento':` → Já OK no código atual

---

### 6. ⏳ app/blueprints/upload/processors/extrato_conta.py

**Substituições:**
- Linha 115: `'forma_classificacao': 'Não Classificada'` → `'origem_classificacao': 'Não Classificada'`
- Linha 116: `'MarcacaoIA': None` → Remover

**Também atualizar:**
- `'DT_Fatura':` → `'MesFatura':`
- `'origem':` → `'banco_origem':`
- `'banco':` → Remover (obsoleto)

---

## 🎯 Resumo de Substituições Globais

### Nomes de colunas:
- `forma_classificacao` → `origem_classificacao`
- `DT_Fatura` → `MesFatura`
- `origem` (quando coluna) → `banco_origem`
- `MarcacaoIA` → Remover (obsoleto)

### Valores de classificação (formato novo com espaço e hífen):
- `'Automática-*'` → `'Automática - *'` (espaço antes e depois do hífen)
- Prefixo de teste: `startswith('Automática-')` → `startswith('Automática -')`

### Campos obsoletos a remover:
- `'MarcacaoIA': None`
- `'banco': <valor>` (substituir por banco_origem)
- Outros: ValidarIA, CartaoCodigo8, FinalCartao, IdOperacao, TipoLancamento, TransacaoFutura, NomeTitular, TipoTransacaoAjuste

---

## ✅ Após Atualização:

1. Testar processors com CSVs históricos
2. Validar classificação automática
3. Verificar dashboard funcionando
4. Confirmar uploads funcionando
5. Rodar `version_manager.py finish`

---

**Data:** 03/01/2026  
**Versão:** 3.0.1-dev
