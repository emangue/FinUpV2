"""
Deduplicador de transações contra journal_entries
"""
from models import JournalEntry, DuplicadoTemp, get_db_session


def deduplicate_transactions(transactions):
    """
    Deduplica transações comparando com journal_entries
    
    Args:
        transactions (list): Lista de dicionários de transações
        
    Returns:
        tuple: (transacoes_unicas, duplicados_removidos)
            - transacoes_unicas: Lista de transações não duplicadas
            - duplicados_removidos: Quantidade de duplicados encontrados
    """
    if not transactions:
        return [], 0
    
    session = get_db_session()
    
    try:
        # Busca todos os IdTransacao existentes na journal_entries
        existing_ids = set(
            row[0] for row in session.query(JournalEntry.IdTransacao).all()
        )
        
        transacoes_unicas = []
        duplicados = []
        
        for trans in transactions:
            id_transacao = trans.get('IdTransacao')
            
            if id_transacao in existing_ids:
                # É duplicado
                duplicados.append(trans)
                
                # Salva em duplicados_temp
                duplicado = DuplicadoTemp(
                    IdTransacao=id_transacao,
                    Data=trans.get('Data'),
                    Estabelecimento=trans.get('Estabelecimento'),
                    Valor=trans.get('Valor'),
                    origem=trans.get('origem'),
                    motivo_duplicacao='IdTransacao já existe na base Journal Entries'
                )
                session.add(duplicado)
            else:
                # É única
                transacoes_unicas.append(trans)
                # Adiciona ao set para evitar duplicatas dentro do próprio upload
                existing_ids.add(id_transacao)
        
        # Commit das duplicações
        session.commit()
        
        duplicados_count = len(duplicados)
        
        print(f"✓ Deduplicação concluída:")
        print(f"  - Transações únicas: {len(transacoes_unicas)}")
        print(f"  - Duplicados removidos: {duplicados_count}")
        
        return transacoes_unicas, duplicados_count
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro na deduplicação: {e}")
        raise
    finally:
        session.close()


def get_duplicados_temp():
    """
    Recupera todos os duplicados temporários
    
    Returns:
        list: Lista de duplicados em formato de dicionário
    """
    session = get_db_session()
    
    try:
        duplicados = session.query(DuplicadoTemp).order_by(DuplicadoTemp.created_at.desc()).all()
        return [dup.to_dict() for dup in duplicados]
    finally:
        session.close()


def clear_duplicados_temp():
    """
    Limpa tabela de duplicados temporários
    
    Returns:
        int: Quantidade de registros deletados
    """
    session = get_db_session()
    
    try:
        count = session.query(DuplicadoTemp).count()
        session.query(DuplicadoTemp).delete()
        session.commit()
        print(f"✓ {count} duplicados temporários removidos")
        return count
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao limpar duplicados: {e}")
        raise
    finally:
        session.close()


def get_duplicados_count():
    """
    Retorna quantidade de duplicados temporários
    
    Returns:
        int: Quantidade de duplicados
    """
    session = get_db_session()
    
    try:
        return session.query(DuplicadoTemp).count()
    finally:
        session.close()
