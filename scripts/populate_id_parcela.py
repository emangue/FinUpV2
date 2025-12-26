"""
Script de Migração: Popular IdParcela em transações históricas
Identifica compras parceladas existentes e atribui IdParcela comum
"""
import sys
import re
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import get_db_session, JournalEntry
from utils.hasher import generate_id_simples
from utils.normalizer import detectar_parcela
from sqlalchemy import func


def extrair_parcela_do_estabelecimento(estabelecimento):
    """
    Extrai informação de parcela do estabelecimento
    Suporta formatos: "LOJA (3/12)" ou "LOJA 3/12"
    
    Returns:
        dict: {'estabelecimento_base': str, 'parcela': int, 'total': int} ou None
    """
    # Tenta formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        return {
            'estabelecimento_base': match.group(1).strip(),
            'parcela': int(match.group(2)),
            'total': int(match.group(3))
        }
    
    # Tenta formato sem parênteses: "LOJA 3/12"
    match = re.search(r'^(.+?)\s+(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        return {
            'estabelecimento_base': match.group(1).strip(),
            'parcela': int(match.group(2)),
            'total': int(match.group(3))
        }
    
    return None


def gerar_id_parcela(estabelecimento_base, valor, total_parcelas):
    """
    Gera IdParcela único baseado em estabelecimento + valor + total
    Usa hash simples sem data pois queremos agrupar todas as parcelas independente da data
    """
    import hashlib
    # Cria string única: estabelecimento + valor + total
    chave = f"{estabelecimento_base}|{abs(float(valor)):.2f}|{total_parcelas}"
    # Gera hash MD5
    return hashlib.md5(chave.encode()).hexdigest()[:16]


def popular_id_parcela():
    """
    Processa todas as transações do journal_entries e popula IdParcela
    para compras parceladas
    """
    session = get_db_session()
    
    try:
        print("=" * 70)
        print("🔄 MIGRAÇÃO: Populando IdParcela em transações históricas")
        print("=" * 70)
        
        # Busca todas as transações
        total_transacoes = session.query(func.count(JournalEntry.id)).scalar()
        print(f"\n📊 Total de transações no banco: {total_transacoes}")
        
        # Busca transações que podem ter parcelas
        transacoes = session.query(JournalEntry).filter(
            JournalEntry.IdParcela.is_(None)
        ).all()
        
        print(f"🔍 Transações sem IdParcela: {len(transacoes)}")
        
        # Agrupa parcelas por estabelecimento_base + valor + total
        grupos_parcelas = {}
        transacoes_com_parcela = 0
        transacoes_sem_parcela = 0
        
        print("\n⏳ Analisando transações...")
        
        for trans in transacoes:
            estabelecimento = trans.Estabelecimento
            valor = trans.Valor
            
            # Tenta extrair informação de parcela
            info_parcela = extrair_parcela_do_estabelecimento(estabelecimento)
            
            if info_parcela:
                # Tem parcela
                transacoes_com_parcela += 1
                estab_base = info_parcela['estabelecimento_base']
                total = info_parcela['total']
                
                # Cria chave única para agrupar
                chave = f"{estab_base}|{abs(valor):.2f}|{total}"
                
                if chave not in grupos_parcelas:
                    grupos_parcelas[chave] = {
                        'estabelecimento_base': estab_base,
                        'valor': abs(valor),
                        'total': total,
                        'transacoes': []
                    }
                
                grupos_parcelas[chave]['transacoes'].append(trans)
            else:
                # Não tem parcela
                transacoes_sem_parcela += 1
        
        print(f"✅ Transações com parcela detectada: {transacoes_com_parcela}")
        print(f"📝 Transações sem parcela: {transacoes_sem_parcela}")
        print(f"📦 Grupos de parcelas encontrados: {len(grupos_parcelas)}")
        
        # Atualiza IdParcela para cada grupo
        print("\n⏳ Atualizando IdParcela...")
        
        grupos_atualizados = 0
        transacoes_atualizadas = 0
        
        for chave, grupo in grupos_parcelas.items():
            estab_base = grupo['estabelecimento_base']
            valor = grupo['valor']
            total = grupo['total']
            transacoes_grupo = grupo['transacoes']
            
            # Gera IdParcela único para este grupo
            id_parcela = gerar_id_parcela(estab_base, valor, total)
            
            # Atualiza todas as transações do grupo
            for trans in transacoes_grupo:
                trans.IdParcela = id_parcela
                transacoes_atualizadas += 1
            
            grupos_atualizados += 1
            
            # Mostra progresso a cada 10 grupos
            if grupos_atualizados % 10 == 0:
                print(f"  Processados {grupos_atualizados}/{len(grupos_parcelas)} grupos...")
        
        # Commit das mudanças
        session.commit()
        
        print("\n" + "=" * 70)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 70)
        print(f"📦 Grupos de parcelas processados: {grupos_atualizados}")
        print(f"✅ Transações atualizadas: {transacoes_atualizadas}")
        print(f"📝 Transações sem parcela: {transacoes_sem_parcela}")
        print(f"📊 Total processado: {transacoes_atualizadas + transacoes_sem_parcela}")
        print("=" * 70)
        
        # Mostra alguns exemplos
        if grupos_atualizados > 0:
            print("\n📋 Exemplos de grupos criados:")
            for i, (chave, grupo) in enumerate(list(grupos_parcelas.items())[:5]):
                estab = grupo['estabelecimento_base']
                total = grupo['total']
                qtd = len(grupo['transacoes'])
                print(f"  {i+1}. {estab} - {qtd}/{total} parcelas encontradas")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERRO durante a migração: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()


if __name__ == '__main__':
    print("\n⚠️  ATENÇÃO: Este script irá modificar o banco de dados!")
    print("Certifique-se de ter um backup antes de continuar.\n")
    
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta == 's':
        sucesso = popular_id_parcela()
        
        if sucesso:
            print("\n✅ Migração concluída! O sistema agora pode usar IdParcela para classificação.")
        else:
            print("\n❌ Migração falhou. Verifique os erros acima.")
            sys.exit(1)
    else:
        print("\n❌ Migração cancelada pelo usuário.")
        sys.exit(0)
