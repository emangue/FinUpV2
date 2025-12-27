import sys
import os
from collections import defaultdict

# Adiciona diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import get_db_session, JournalEntry, BaseParcelas
from app.utils.normalizer import normalizar_estabelecimento, detectar_parcela

def migrar_parcelas():
    print("🔄 Iniciando migração de parcelas para BaseParcelas...")
    
    session = get_db_session()
    
    try:
        # 1. Busca todas as transações com IdParcela (apenas Cartão de Crédito)
        transacoes = session.query(JournalEntry).filter(
            JournalEntry.IdParcela.isnot(None),
            JournalEntry.IdParcela != '',
            JournalEntry.TipoTransacao == 'Cartão de Crédito'
        ).all()
        
        print(f"✓ Encontradas {len(transacoes)} transações parceladas")
        
        # 2. Agrupa por IdParcela (Hash)
        grupos = defaultdict(list)
        for t in transacoes:
            grupos[t.IdParcela].append(t)
            
        print(f"✓ Identificados {len(grupos)} contratos únicos")
        
        novos = 0
        atualizados = 0
        
        # 3. Processa cada grupo
        for id_parcela, items in grupos.items():
            # Pega dados do contrato (usando o primeiro item como base)
            primeiro = items[0]
            
            # Tenta extrair qtd total de parcelas do estabelecimento
            info_parcela = detectar_parcela(primeiro.Estabelecimento)
            qtd_total = info_parcela['total'] if info_parcela else 0
            
            # Se não conseguiu detectar, tenta inferir pelo maior número encontrado no grupo
            if qtd_total == 0:
                max_parcela = 0
                for item in items:
                    info = detectar_parcela(item.Estabelecimento)
                    if info and info['total'] > max_parcela:
                        max_parcela = info['total']
                qtd_total = max_parcela
            
            # Se ainda assim for 0, pula (algo errado)
            if qtd_total == 0:
                print(f"⚠ Ignorando {primeiro.Estabelecimento} (não foi possível determinar total de parcelas)")
                continue
                
            # Define classificação (pega a mais comum)
            classificacoes = defaultdict(int)
            for item in items:
                if item.GRUPO and item.SUBGRUPO:
                    chave = f"{item.GRUPO}|{item.SUBGRUPO}|{item.TipoGasto}"
                    classificacoes[chave] += 1
            
            grupo = subgrupo = tipo_gasto = None
            if classificacoes:
                melhor = max(classificacoes.items(), key=lambda x: x[1])[0]
                grupo, subgrupo, tipo_gasto = melhor.split('|')
            
            # Verifica se já existe na BaseParcelas
            contrato = session.query(BaseParcelas).filter_by(id_parcela=id_parcela).first()
            
            if contrato:
                # Atualiza contagem
                contrato.qtd_pagas = len(items)
                if grupo:
                    contrato.grupo_sugerido = grupo
                    contrato.subgrupo_sugerido = subgrupo
                    contrato.tipo_gasto_sugerido = tipo_gasto
                
                if contrato.qtd_pagas >= contrato.qtd_parcelas:
                    contrato.status = 'finalizado'
                
                atualizados += 1
            else:
                # Cria novo
                novo_contrato = BaseParcelas(
                    id_parcela=id_parcela,
                    estabelecimento_base=normalizar_estabelecimento(primeiro.Estabelecimento),
                    valor_parcela=abs(primeiro.Valor),
                    qtd_parcelas=qtd_total,
                    grupo_sugerido=grupo,
                    subgrupo_sugerido=subgrupo,
                    tipo_gasto_sugerido=tipo_gasto,
                    qtd_pagas=len(items),
                    valor_total_plano=abs(primeiro.Valor) * qtd_total,
                    data_inicio=min(t.Data for t in items),
                    status='finalizado' if len(items) >= qtd_total else 'ativo'
                )
                session.add(novo_contrato)
                novos += 1
        
        session.commit()
        print(f"\n✅ Migração concluída!")
        print(f"  - Novos contratos criados: {novos}")
        print(f"  - Contratos atualizados: {atualizados}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro na migração: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrar_parcelas()
