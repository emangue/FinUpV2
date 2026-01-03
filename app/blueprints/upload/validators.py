"""
Transaction Data Validator
Valida dados de transações ANTES de inserir no banco

Versão: 1.0.0
Data: 03/01/2026
Autor: Sistema de Versionamento

🔒 ARQUIVO CRÍTICO - Usado em upload/routes.py
"""

import re
from datetime import datetime
from app.models import BaseMarcacao, get_db_session


def validate_date_format(date_str):
    """
    Valida formato DD/MM/AAAA
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not date_str:
        return False, "Data não pode ser vazia"
    
    # Regex para DD/MM/AAAA
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
        return False, f"Formato inválido (esperado DD/MM/AAAA): '{date_str}'"
    
    # Validar se é data real
    try:
        day, month, year = date_str.split('/')
        dt = datetime(int(year), int(month), int(day))
        
        # Validar ano razoável (1900-2100)
        if int(year) < 1900 or int(year) > 2100:
            return False, f"Ano fora do range válido: {year}"
        
        return True, None
    except ValueError as e:
        return False, f"Data inválida: {str(e)}"


def validate_dt_fatura_format(dt_fatura_str):
    """
    Valida formato AAAAMM
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not dt_fatura_str:
        return True, None  # Campo opcional
    
    if not re.match(r'^\d{6}$', dt_fatura_str):
        return False, f"Formato inválido (esperado AAAAMM): '{dt_fatura_str}'"
    
    try:
        year = int(dt_fatura_str[:4])
        month = int(dt_fatura_str[4:])
        
        if year < 1900 or year > 2100:
            return False, f"Ano inválido em DT_Fatura: {year}"
        
        if month < 1 or month > 12:
            return False, f"Mês inválido em DT_Fatura: {month}"
        
        return True, None
    except ValueError:
        return False, f"DT_Fatura inválido: '{dt_fatura_str}'"


def validate_transaction_data(trans_dict, db_session=None):
    """
    Valida transação ANTES de inserir no banco
    
    Args:
        trans_dict: Dicionário com dados da transação
        db_session: Sessão do banco (opcional, será criada se não fornecida)
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None, trans_dict_updated: dict)
        
    Validações realizadas:
    - Data em formato DD/MM/AAAA
    - Valor e ValorPositivo consistentes
    - Campos obrigatórios preenchidos
    - DT_Fatura em formato AAAAMM
    - TipoGasto presente ou preenchível via base_marcacoes
    """
    errors = []
    trans_updated = trans_dict.copy()
    
    # ==================================================
    # 1. VALIDAR DATA (formato DD/MM/AAAA)
    # ==================================================
    data = trans_dict.get('Data')
    if not data:
        errors.append("Campo 'Data' é obrigatório")
    else:
        is_valid, error_msg = validate_date_format(data)
        if not is_valid:
            errors.append(error_msg)
    
    # ==================================================
    # 2. VALIDAR VALOR E VALORPOSITIVO
    # ==================================================
    valor = trans_dict.get('Valor')
    valor_pos = trans_dict.get('ValorPositivo')
    
    if valor is None:
        errors.append("Campo 'Valor' é obrigatório")
    
    if valor_pos is None:
        # Auto-corrigir: calcular ValorPositivo
        if valor is not None:
            trans_updated['ValorPositivo'] = abs(float(valor))
    else:
        # Validar consistência
        if abs(abs(float(valor)) - float(valor_pos)) > 0.01:
            errors.append(
                f"ValorPositivo ({valor_pos}) deve ser igual a abs(Valor) ({abs(valor)})"
            )
        
        # Validar que ValorPositivo é positivo
        if float(valor_pos) < 0:
            errors.append(f"ValorPositivo não pode ser negativo: {valor_pos}")
    
    # ==================================================
    # 3. VALIDAR CAMPOS OBRIGATÓRIOS
    # ==================================================
    required_fields = {
        'IdTransacao': 'ID da Transação',
        'Estabelecimento': 'Estabelecimento',
        'origem': 'Origem'
    }
    
    for field, display_name in required_fields.items():
        if not trans_dict.get(field):
            errors.append(f"Campo '{display_name}' é obrigatório")
    
    # ==================================================
    # 4. VALIDAR DT_FATURA (formato AAAAMM)
    # ==================================================
    dt_fatura = trans_dict.get('DT_Fatura')
    if dt_fatura:
        is_valid, error_msg = validate_dt_fatura_format(dt_fatura)
        if not is_valid:
            errors.append(error_msg)
    
    # ==================================================
    # 5. VALIDAR/PREENCHER TIPOGASTO
    # ==================================================
    grupo = trans_dict.get('GRUPO')
    subgrupo = trans_dict.get('SUBGRUPO')
    tipogasto = trans_dict.get('TipoGasto')
    
    if grupo and subgrupo and not tipogasto:
        # Tentar preencher automaticamente via base_marcacoes
        if db_session is None:
            db_session = get_db_session()
        
        marcacao = db_session.query(BaseMarcacao).filter_by(
            GRUPO=grupo,
            SUBGRUPO=subgrupo
        ).first()
        
        if marcacao and marcacao.TipoGasto:
            trans_updated['TipoGasto'] = marcacao.TipoGasto
        else:
            # Aviso: não bloqueia upload, mas registra
            errors.append(
                f"⚠️ AVISO: Combinação GRUPO='{grupo}' + SUBGRUPO='{subgrupo}' "
                f"não tem TipoGasto em base_marcacoes. Transação será salva sem TipoGasto."
            )
    
    # ==================================================
    # 6. VALIDAR CONSISTÊNCIA DATA/ANO/DT_FATURA
    # ==================================================
    if data and validate_date_format(data)[0]:
        day, month, year = data.split('/')
        data_year = int(year)
        data_month = int(month)
        
        # Validar Ano
        ano = trans_dict.get('Ano')
        if ano and ano != data_year:
            # Auto-corrigir
            trans_updated['Ano'] = data_year
        
        # Validar DT_Fatura
        if dt_fatura and len(dt_fatura) == 6:
            ref_year = int(dt_fatura[:4])
            ref_month = int(dt_fatura[4:])
            
            # Avisar se diferença for > 2 meses (faturas podem ser mes anterior/posterior)
            month_diff = abs((data_year * 12 + data_month) - (ref_year * 12 + ref_month))
            if month_diff > 2:
                errors.append(
                    f"⚠️ AVISO: DT_Fatura ({dt_fatura}) difere muito da Data ({data})"
                )
    
    # ==================================================
    # RESULTADO
    # ==================================================
    if errors:
        # Separar erros críticos de avisos
        critical_errors = [e for e in errors if not e.startswith('⚠️')]
        warnings = [e for e in errors if e.startswith('⚠️')]
        
        if critical_errors:
            return False, '\n'.join(critical_errors), trans_updated
        else:
            # Apenas avisos - permitir mas registrar
            return True, '\n'.join(warnings), trans_updated
    
    return True, None, trans_updated


def validate_transaction_batch(transactions_list, db_session=None):
    """
    Valida um lote de transações
    
    Args:
        transactions_list: Lista de dicionários com transações
        db_session: Sessão do banco (opcional)
    
    Returns:
        tuple: (valid_transactions, invalid_transactions, warnings)
        
    Examples:
        >>> valid, invalid, warnings = validate_transaction_batch(transactions)
        >>> print(f"Válidas: {len(valid)}, Inválidas: {len(invalid)}")
    """
    valid = []
    invalid = []
    warnings = []
    
    for trans in transactions_list:
        is_valid, error_msg, trans_updated = validate_transaction_data(trans, db_session)
        
        if is_valid:
            valid.append(trans_updated)
            if error_msg:  # Tem avisos
                warnings.append({
                    'IdTransacao': trans.get('IdTransacao'),
                    'warning': error_msg
                })
        else:
            invalid.append({
                'transaction': trans,
                'error': error_msg
            })
    
    return valid, invalid, warnings


# ==================================================
# EXEMPLO DE USO
# ==================================================
if __name__ == '__main__':
    # Teste 1: Transação válida
    trans1 = {
        'IdTransacao': 'abc123',
        'Data': '01/01/2024',
        'Estabelecimento': 'TESTE LTDA',
        'Valor': -100.50,
        'ValorPositivo': 100.50,
        'origem': 'Teste',
        'DT_Fatura': '202401',
        'Ano': 2024,
        'GRUPO': 'Alimentação',
        'SUBGRUPO': 'Supermercado',
        'TipoGasto': 'Ajustável'
    }
    
    # Teste 2: Transação com erro
    trans2 = {
        'IdTransacao': 'def456',
        'Data': '2024-01-01 00:00:00',  # Formato errado
        'Estabelecimento': 'TESTE 2',
        'Valor': -50.00,
        'ValorPositivo': -50.00,  # Negativo!
        'origem': '',  # Faltando
        'DT_Fatura': '20240',  # Formato errado
    }
    
    print("Teste 1 (válida):")
    is_valid, error, updated = validate_transaction_data(trans1)
    print(f"  Válida: {is_valid}")
    print(f"  Erro: {error}")
    print()
    
    print("Teste 2 (inválida):")
    is_valid, error, updated = validate_transaction_data(trans2)
    print(f"  Válida: {is_valid}")
    print(f"  Erro: {error}")
