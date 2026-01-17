"""
Regenerar IdTransacao com algoritmo v4.2.3 (uppercase + normalização de parcela)

Este script regenera TODOS os IdTransacao na base usando o novo algoritmo que:
1. Normaliza espaços múltiplos
2. Converte para UPPERCASE
3. Normaliza formato de parcela para faturas

CRÍTICO: Resolve duplicatas não detectadas por diferença de case e espaços
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from datetime import datetime
from collections import defaultdict

from app.shared.utils import generate_id_transacao
from app.domains.upload.processors.marker import normalizar_espacos, normalizar_formato_parcela


def is_fatura(tipo_documento: str) -> bool:
    """Verifica se é fatura (para normalizar parcela)"""
    if not tipo_documento:
        return False
    tipo_lower = tipo_documento.lower()
    return 'fatura' in tipo_lower or 'cartao' in tipo_lower or 'cartão' in tipo_lower


def processar_estabelecimento(estabelecimento: str, tipo_documento: str) -> str:
    """
    Processa estabelecimento conforme algoritmo v4.2.3
    
    Args:
        estabelecimento: Nome original
        tipo_documento: Tipo do documento (fatura/extrato)
        
    Returns:
        Estabelecimento normalizado
    """
    # 1. Normalizar espaços
    norm = normalizar_espacos(estabelecimento)
    
    # 2. Uppercase
    norm = norm.upper().strip()
    
    # 3. Se fatura, normalizar parcela
    if is_fatura(tipo_documento):
        norm = normalizar_formato_parcela(norm)
    
    return norm


def regenerate_all():
    """Regenera todos os IdTransacao do banco"""
    
    db_path = Path(__file__).parent.parent / 'database' / 'financas_dev.db'
    
    if not db_path.exists():
        print(f'❌ Banco não encontrado: {db_path}')
        return
    
    print(f'🔄 Regenerando IdTransacao com algoritmo v4.2.3')
    print(f'📁 Banco: {db_path}')
    print(f'⏰ Início: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Buscar todas as transações (ordem determinística com id no final)
        cursor.execute('''
            SELECT id, user_id, Data, Estabelecimento, Valor, tipodocumento
            FROM journal_entries
            ORDER BY user_id, Data, Estabelecimento, id
        ''')
        
        transacoes = cursor.fetchall()
        total = len(transacoes)
        print(f'📊 Total de transações: {total}')
        print()
        
        # 2. Agrupar por (user_id, data, estabelecimento_normalizado, valor) para sequência
        seen_transactions = defaultdict(int)
        updates = []
        
        for row in transacoes:
            id_entry, user_id, data, estabelecimento, valor, tipo_doc = row
            
            # Processar estabelecimento conforme v4.2.3
            estab_normalizado = processar_estabelecimento(estabelecimento, tipo_doc)
            
            # Chave para detectar duplicatas
            chave = f"{data}|{estab_normalizado}|{valor:.2f}"
            
            # Incrementar sequência
            if chave in seen_transactions:
                seen_transactions[chave] += 1
            else:
                seen_transactions[chave] = 1
            
            sequencia = seen_transactions[chave]
            
            # Gerar novo IdTransacao
            novo_id = generate_id_transacao(
                data=data,
                estabelecimento=estab_normalizado,
                valor=valor,
                user_id=user_id,
                sequencia=sequencia
            )
            
            updates.append((novo_id, id_entry))
        
        # 3. Aplicar atualizações diretamente (IdTransacao é NOT NULL, então update direto)
        print(f'🔄 Aplicando {len(updates)} atualizações de IdTransacao...')
        
        contador = 0
        for novo_id, id_entry in updates:
            cursor.execute('''
                UPDATE journal_entries
                SET IdTransacao = ?
                WHERE id = ?
            ''', (novo_id, id_entry))
            
            contador += 1
            if contador % 500 == 0:
                print(f'  ✅ {contador}/{len(updates)} processados...')
                conn.commit()  # Commit parcial
        
        conn.commit()
        
        print(f'✅ Regeneração concluída!')
        print(f'📊 {len(updates)} IdTransacao atualizados')
        print()
        
        # 4. Verificar duplicatas detectadas (sequencia > 1)
        duplicatas = sum(1 for seq in seen_transactions.values() if seq > 1)
        print(f'🔍 Duplicatas detectadas: {duplicatas} grupos')
        print()
        
        # 5. Exemplos de mudanças
        print('📋 Exemplos de IdTransacao atualizados:')
        cursor.execute('''
            SELECT IdTransacao, Data, Estabelecimento, Valor
            FROM journal_entries
            WHERE Estabelecimento LIKE '%VPD TRAVEL%'
            AND Data = '14/03/2025'
            ORDER BY Valor DESC
            LIMIT 5
        ''')
        
        for row in cursor.fetchall():
            print(f'  {row[0]} | {row[1]} | {row[2]} | R$ {row[3]}')
        
    except Exception as e:
        conn.rollback()
        print(f'❌ Erro: {e}')
        raise
    
    finally:
        conn.close()
    
    print()
    print(f'⏰ Fim: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    print('🎯 Próximo passo: Fazer novo upload para validar detecção de duplicatas')


if __name__ == '__main__':
    print()
    print('=' * 70)
    print(' REGENERAÇÃO DE IdTransacao - v4.2.3')
    print('=' * 70)
    print()
    
    resposta = input('⚠️  Isso irá REGENERAR todos os IdTransacao. Continuar? (s/N): ')
    
    if resposta.lower() == 's':
        print()
        regenerate_all()
    else:
        print('❌ Cancelado pelo usuário')
