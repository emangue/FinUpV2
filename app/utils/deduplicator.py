"""
Deduplicador de transações contra journal_entries
"""
from app.models import JournalEntry, DuplicadoTemp, BaseParcelas, get_db_session


def deduplicate_transactions(transactions):
    """
    Deduplica transações comparando com journal_entries e base_parcelas
    
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
        
        # Busca informações de parcelas pagas
        # Mapa: id_parcela -> qtd_pagas
        parcelas_pagas = {}
        
        # Coleta IDs de parcela das transações de entrada
        ids_parcela_entrada = set(
            t.get('IdParcela') for t in transactions if t.get('IdParcela')
        )
        
        if ids_parcela_entrada:
            rows = session.query(BaseParcelas.id_parcela, BaseParcelas.qtd_pagas).filter(
                BaseParcelas.id_parcela.in_(ids_parcela_entrada)
            ).all()
            parcelas_pagas = {row[0]: row[1] for row in rows}
        
        transacoes_unicas = []
        duplicados = []
        
        for trans in transactions:
            id_transacao = trans.get('IdTransacao')
            id_parcela = trans.get('IdParcela')
            parcela_atual = trans.get('parcela_atual')
            
            is_duplicate = False
            reason = ""
            
            # 1. Checa IdTransacao (duplicata exata)
            if id_transacao in existing_ids:
                is_duplicate = True
                reason = 'IdTransacao já existe na base Journal Entries'
            
            # 2. Checa Base de Parcelas (se for parcela)
            elif id_parcela and parcela_atual and id_parcela in parcelas_pagas:
                qtd_pagas = parcelas_pagas[id_parcela]
                # Se a parcela atual for menor ou igual à quantidade já paga, é duplicata
                if parcela_atual <= qtd_pagas:
                    is_duplicate = True
                    reason = f'Parcela {parcela_atual} já processada (Base de Parcelas indica {qtd_pagas} pagas)'
            
            if is_duplicate:
                # É duplicado
                duplicados.append(trans)
                
                # Salva em duplicados_temp
                duplicado = DuplicadoTemp(
                    IdTransacao=id_transacao,
                    Data=trans.get('Data'),
                    Estabelecimento=trans.get('Estabelecimento'),
                    Valor=trans.get('Valor'),
                    origem=trans.get('origem'),
                    motivo_duplicacao=reason
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
