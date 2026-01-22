# Processador Mercado Pago - Extrato XLSX

## 📋 Informações Gerais

**Criado em:** 18/01/2026  
**Arquivo:** `app_dev/backend/app/domains/upload/processors/raw/excel/mercadopago_extrato.py`  
**Tipo:** Extrato Bancário  
**Formato:** Excel (.xlsx)  
**Banco:** Mercado Pago

## 🎯 Propósito

Processar extratos do Mercado Pago no formato XLSX gerados pela plataforma. O processador extrai transações e valida saldos automaticamente.

## 📁 Estrutura do Arquivo

O arquivo XLSX do Mercado Pago possui a seguinte estrutura:

```
Linha 0: Headers dos totais
  [INITIAL_BALANCE, CREDITS, DEBITS, FINAL_BALANCE, Unnamed: 4]

Linha 1: Valores dos totais
  [1.852,03, 24.685,74, -25.569,57, 968,20, NaN]
  └─ Formato brasileiro: vírgula decimal, ponto milhar

Linha 2: Linha em branco

Linha 3: Headers das transações
  [RELEASE_DATE, TRANSACTION_TYPE, REFERENCE_ID, TRANSACTION_NET_AMOUNT, PARTIAL_BALANCE]

Linhas 4+: Transações
  [01-09-2025, Rendimentos, 1733144253210, 0,05, 1.852,08]
  [01-09-2025, Transferência Pix recebida..., 123877323285, 1.232,46, 3.084,54]
  ...
```

### Colunas Utilizadas

| Coluna | Nome | Descrição | Usado Como |
|--------|------|-----------|------------|
| 0 | RELEASE_DATE | Data da transação (DD-MM-YYYY) | `data` |
| 1 | TRANSACTION_TYPE | Tipo/descrição da transação | `lancamento` |
| 2 | REFERENCE_ID | ID de referência Mercado Pago | (não usado) |
| 3 | TRANSACTION_NET_AMOUNT | Valor líquido da transação | `valor` |
| 4 | PARTIAL_BALANCE | Saldo parcial após transação | (usado para validação) |

## ✅ Funcionalidades

### 1. Extração de Saldos
- **Saldo Inicial:** Extraído da linha 1, coluna 0
- **Saldo Final:** Extraído da linha 1, coluna 3
- **Validação Automática:** Verifica se `Saldo Inicial + Soma Transações = Saldo Final`

### 2. Processamento de Transações
- Remove linhas vazias
- Converte datas de `DD-MM-YYYY` para `DD/MM/YYYY`
- Converte valores brasileiros (`1.234,56` → `1234.56`)
- Remove transações com valor zero
- Limpa espaços extras nas descrições

### 3. Validação de Dados
- Valida formato de data
- Valida valores numéricos
- Remove transações inválidas
- Calcula diferença de saldo (tolerância: R$ 0,01)

## 📊 Exemplo de Uso

### Upload via Interface

1. Acesse a interface de upload
2. Selecione o arquivo `.xlsx` do Mercado Pago
3. Preencha:
   - **Banco:** "Mercado Pago" (ou "MercadoPago")
   - **Tipo:** "extrato"
   - **Formato:** Detectado automaticamente como "excel"

### Processamento Automático

```python
from app.domains.upload.processors.raw.excel.mercadopago_extrato import (
    process_mercadopago_extrato
)

# Processar arquivo
transactions, balance = process_mercadopago_extrato(
    file_path=Path("account_statement-xxx.xlsx"),
    nome_arquivo="account_statement-xxx.xlsx"
)

# Validar saldo
print(f"Transações: {len(transactions)}")
print(f"Saldo válido: {balance.is_valid}")
print(f"Diferença: R$ {balance.diferenca}")
```

## 📈 Estatísticas do Teste

Arquivo testado: `account_statement-202ffd51-0eb5-4dde-ac19-2c88c2c60896.xlsx`

```
✅ Transações processadas: 99
✅ Saldo Inicial:          R$ 1.852,03
✅ Soma Transações:        R$ -883,83
✅ Saldo Final:            R$ 968,20
✅ Diferença:              R$ 0,00
✅ Validação:              PASSOU

Créditos:  33 transações (R$ 24.685,74)
Débitos:   66 transações (R$ -25.569,57)
```

## 🔧 Tipos de Transação Identificados

O Mercado Pago utiliza descrições específicas na coluna `TRANSACTION_TYPE`:

- ✅ **Rendimentos** - Rendimento da conta
- ✅ **Transferência Pix recebida [Nome]** - PIX recebido
- ✅ **Transferência Pix enviada [Nome]** - PIX enviado
- ✅ **Reserva programada [Objetivo]** - Reserva criada
- ✅ **Reserva por gastos [Categoria]** - Gasto de reserva
- ✅ **Saída de dinheiro** - Retirada genérica
- ✅ **Dinheiro retirado [Categoria]** - Retirada categorizada
- ✅ **Pagamento de assinatura** - Assinatura paga
- ✅ **Pagamento Cartão de crédito** - Pagamento de fatura
- ✅ **Pagamento [Estabelecimento]** - Pagamento genérico

## 🚨 Observações Importantes

### Formato de Valores
- O Mercado Pago usa formato **brasileiro** (vírgula decimal, ponto milhar)
- Exemplo: `1.234,56` representa mil duzentos e trinta e quatro reais e cinquenta e seis centavos
- O processador converte automaticamente para float: `1234.56`

### Formato de Data
- Arquivo original: `DD-MM-YYYY` (com hífen)
- Após processamento: `DD/MM/YYYY` (com barra)
- Compatível com o padrão do sistema

### Saldos Parciais
- A coluna `PARTIAL_BALANCE` (coluna 4) não é usada diretamente
- Ela serve para validação manual se necessário
- A validação oficial usa `Saldo Inicial + Soma Transações`

## 🔍 Troubleshooting

### Arquivo não reconhecido
**Problema:** Processador não é chamado ao fazer upload  
**Solução:** Verificar se o nome do banco está correto:
- ✅ "Mercado Pago" (com espaço)
- ✅ "MercadoPago" (sem espaço)
- ❌ "Mercadopago" (p minúsculo)
- ❌ "mercado pago" (tudo minúsculo)

### Saldo não valida
**Problema:** `balance.is_valid = False`  
**Causas possíveis:**
1. Transações futuras no arquivo (não devem existir no Mercado Pago)
2. Valores com formatação diferente
3. Linhas de cabeçalho extras

**Debug:**
```python
print(f"Saldo Inicial: {balance.saldo_inicial}")
print(f"Soma Transações: {balance.soma_transacoes}")
print(f"Saldo Final Esperado: {balance.saldo_inicial + balance.soma_transacoes}")
print(f"Saldo Final Arquivo: {balance.saldo_final}")
print(f"Diferença: {balance.diferenca}")
```

### Transações duplicadas
**Problema:** Mesma transação aparece 2x  
**Solução:** O sistema de deduplicação via `IdTransacao` detecta automaticamente
- Hash baseado em: `data | lancamento | valor | sequencia`
- Para extratos, usa `lancamento` **completo** (preserva detalhes do PIX/transferência)

## 📝 Registro no Sistema

O processador foi registrado em:
- `app_dev/backend/app/domains/upload/processors/raw/registry.py`

```python
PROCESSORS = {
    ...
    # Mercado Pago
    ('mercado pago', 'extrato', 'excel'): process_mercadopago_extrato,
    ('mercadopago', 'extrato', 'excel'): process_mercadopago_extrato,
}
```

## 🎯 Próximos Passos

- [x] Criar processador
- [x] Testar com arquivo real
- [x] Validar saldos
- [x] Registrar no sistema
- [x] Reiniciar servidores
- [x] Documentar funcionalidade
- [ ] Testar upload via interface web
- [ ] Testar classificação automática
- [ ] Validar deduplicação

## 📚 Referências

- **Arquivo de teste:** `_arquivos_historicos/_csvs_historico/account_statement-202ffd51-0eb5-4dde-ac19-2c88c2c60896.xlsx`
- **Script de teste:** `test_mercadopago_simple.py`
- **Base de código:** Baseado em `itau_extrato.py` e `btg_extrato.py`
- **Documentação de processadores:** `app_dev/backend/app/domains/upload/processors/raw/README.md` (se existir)

---

**Status:** ✅ Pronto para uso  
**Última atualização:** 18/01/2026
