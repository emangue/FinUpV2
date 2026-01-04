# Fix: Preprocessador Extrato BB CSV - Alinhamento de Colunas

**Data:** 28/12/2025  
**Tipo:** Bug Fix  
**Impacto:** Alto - Upload de extratos BB estava quebrado  
**Versão:** 3.0.0 → 3.0.1

---

## 🐛 Problema Identificado

O preprocessador de extratos BB CSV estava criando colunas incompatíveis com o processador de extrato de conta, causando múltiplos KeyErrors durante o upload:

1. **Erro 1:** `KeyError: 'mensagem'` - validação sem campo mensagem
2. **Erro 2:** `KeyError: 'lançamento'` - preprocessador criando 'descricao_original' 
3. **Erro 3:** `KeyError: 'data'` - problema de normalização (falso positivo)
4. **Erro 4:** `KeyError: 'valor'` - validação usando 'valor' em vez de 'valor (R$)'

**Arquivo testado:** `extrato_ana_beatriz_BB.csv` (66 transações)

---

## ✅ Solução Implementada

### 1. Correção de Nomes de Colunas

**Arquivo:** `app/utils/processors/preprocessors/extrato_bb_csv.py`

```python
# ANTES (incorreto):
df = df.rename(columns={
    'Data': 'data',
    'Valor': 'valor',
    'Historico': 'descricao_original'
})

# DEPOIS (correto):
df = df.rename(columns={
    'Data': 'data',
    'Valor': 'valor (R$)',  # ✅ Formato esperado pelo processador
    'Historico': 'lançamento'  # ✅ Nome correto da coluna
})
df['descricao_original'] = df['lançamento'].copy()  # ✅ Mantém backup
```

### 2. Adição de Campo 'mensagem' na Validação

```python
# ANTES (incompleto):
validacao = {
    'saldo_anterior': saldo_anterior,
    'saldo_final': saldo_final,
    'soma_transacoes': soma_transacoes,
    'valido': valido,
    'diferenca': diferenca
}

# DEPOIS (completo):
mensagem = f"✅ Validação OK - Diferença: R$ {abs(diferenca):.2f}" if valido else f"❌ Validação FALHOU"
validacao = {
    'saldo_anterior': saldo_anterior,
    'saldo_final': saldo_final,
    'soma_transacoes': soma_transacoes,
    'valido': valido,
    'diferenca': diferenca,
    'mensagem': mensagem  # ✅ Campo obrigatório para UI
}
```

### 3. Correção do Cálculo de Validação

```python
# ANTES (KeyError):
soma_transacoes = df_final['valor'].sum()

# DEPOIS (correto):
soma_transacoes = df_final['valor (R$)'].sum()  # ✅ Usa nome correto
```

---

## 🧪 Validação

### Teste Standalone
```bash
python -c "from app.utils.processors.preprocessors.extrato_bb_csv import processar_extrato_bb_csv; resultado = processar_extrato_bb_csv('extrato_ana_beatriz_BB.csv'); print(list(resultado['df'].columns)); print(resultado['validacao'])"
```

**Resultado:**
- ✅ Colunas: `['data', 'lançamento', 'valor (R$)', 'descricao_original']`
- ✅ 66 transações processadas
- ✅ Validação: `{'valido': True, 'mensagem': '✅ Validação OK - Diferença: R$ 0.00'}`
- ✅ Saldo anterior: R$ 0,00
- ✅ Saldo final: R$ 0,00
- ✅ Diferença de validação: -4.66e-12 (tolerância aceitável)

---

## 📋 Arquivos Modificados

1. **`app/utils/processors/preprocessors/extrato_bb_csv.py`** (v3.0.0 → v3.0.1)
   - Linhas ~210: Correção de renomeação de colunas
   - Linhas ~218: Correção de cálculo de validação
   - Linhas ~225: Adição de campo 'mensagem'

2. **`app/blueprints/upload/routes.py`** (anteriormente)
   - Já estava correto - passa filepath para preprocessador

3. **`app/blueprints/upload/processors/extrato_conta.py`** (sem mudanças)
   - Espera colunas: `['data', 'lançamento', 'valor (R$)']`
   - Funcionando conforme esperado

---

## 🎯 Impacto

### Antes da Correção
- ❌ Upload de extratos BB completamente quebrado
- ❌ 4 erros consecutivos durante processamento
- ❌ Usuários não conseguiam importar extratos BB

### Depois da Correção
- ✅ Upload de extratos BB funcional
- ✅ Validação de saldo funcionando corretamente
- ✅ Interface exibindo mensagens de validação
- ✅ 66 transações processadas sem erros

---

## 📝 Lições Aprendidas

1. **Consistência de Nomenclatura:** Preprocessadores devem retornar **exatamente** os nomes de colunas esperados pelos processadores
2. **Caracteres Especiais:** Nomes como `'valor (R$)'` requerem correspondência exata, incluindo parênteses e símbolos
3. **Validação Completa:** Estruturas de validação devem incluir **todos** os campos esperados pela UI
4. **Teste Standalone:** Sempre testar preprocessadores isoladamente antes de integração completa

---

## 🔮 Próximos Passos

- [ ] Adicionar testes unitários para preprocessador BB
- [ ] Documentar formato esperado de colunas em cada preprocessador
- [ ] Criar guia de troubleshooting para erros de coluna
- [ ] Considerar validação automática de estrutura de retorno

---

## 🔗 Relacionado

- Issue: Upload BB CSV não funcionando (28/12/2025)
- User: Ana Beatriz
- Arquivo: `extrato_ana_beatriz_BB.csv`
- Branch: `main`
