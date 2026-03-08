# Skill: Novo Processador Raw

## Contexto
Processadores em `app_dev/backend/app/domains/upload/processors/raw/{formato}/`

## Antes de criar, pergunte
1. Nome do banco (ex: "Nubank", "C6 Bank")
2. Tipo: fatura ou extrato
3. Formato: excel (.xlsx), pdf (texto) ou pdf (OCR/imagem)

## Assinatura obrigatória
```python
def process_{banco}_{tipo}(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None,
) -> Tuple[List[RawTransaction], BalanceValidation]:
```

## Campos obrigatórios do RawTransaction
`banco`, `tipo_documento`, `nome_arquivo`, `data_criacao`, `data` (DD/MM/YYYY),
`lancamento`, `valor` (float, negativo=débito), `nome_cartao`, `final_cartao`, `mes_fatura` (AAAAMM)

## BalanceValidation
`saldo_inicial + soma_transacoes ≈ saldo_final` (tolerância 0.01)

## Após criar
1. Registrar em `registry.py`: `PROCESSORS[(_normalize_bank_name(banco), tipo, formato)] = funcao`
2. Testar com arquivo real: `balance_validation.is_valid == True`
3. Atualizar tabela de compatibilidade no banco
