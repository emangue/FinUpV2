"""
Gerador/Regenerador de padrões automáticos
Versão simplificada
"""
from models import JournalEntry, BasePadrao, get_db_session
from utils.normalizer import normalizar_estabelecimento, get_faixa_valor, arredondar_2_decimais
from utils.hasher import fnv1a_64_hash
from datetime import datetime


def regenerar_padroes():
    """
    Regenera base de padrões a partir do Journal Entries
    
    Returns:
        int: Quantidade de padrões gerados/atualizados
    """
    print("\n🔄 Regenerando padrões da base...")
    
    session = get_db_session()
    
    try:
        # Busca todas as transações com classificação completa
        transacoes = session.query(JournalEntry).filter(
            JournalEntry.GRUPO != None,
            JournalEntry.GRUPO != '',
            JournalEntry.SUBGRUPO != None,
            JournalEntry.SUBGRUPO != '',
            JournalEntry.TipoGasto != None,
            JournalEntry.TipoGasto != ''
        ).all()
        
        if not transacoes:
            print("⚠ Nenhuma transação encontrada para gerar padrões")
            return 0
        
        print(f"✓ Processando {len(transacoes)} transações...")
        
        # Agrupa por estabelecimento normalizado
        grupos = {}
        for trans in transacoes:
            estab_norm = normalizar_estabelecimento(trans.Estabelecimento)
            
            if not estab_norm:
                continue
            
            if estab_norm not in grupos:
                grupos[estab_norm] = []
            
            grupos[estab_norm].append({
                'valor': abs(trans.Valor or 0),
                'GRUPO': trans.GRUPO,
                'SUBGRUPO': trans.SUBGRUPO,
                'TipoGasto': trans.TipoGasto,
                'estabelecimento': trans.Estabelecimento
            })
        
        # Gera padrões
        padroes_novos = 0
        padroes_atualizados = 0
        
        for estab_norm, items in grupos.items():
            if len(items) < 2:  # Mínimo 2 ocorrências
                continue
            
            # Calcula estatísticas
            valores = [it['valor'] for it in items]
            valor_medio = sum(valores) / len(valores)
            valor_min = min(valores)
            valor_max = max(valores)
            
            # Conta classificações
            classificacoes = {}
            for it in items:
                chave = f"{it['GRUPO']}|{it['SUBGRUPO']}|{it['TipoGasto']}"
                classificacoes[chave] = classificacoes.get(chave, 0) + 1
            
            # Pega a mais frequente
            mais_frequente = max(classificacoes.items(), key=lambda x: x[1])
            grupo, subgrupo, tipo_gasto = mais_frequente[0].split('|')
            frequencia = mais_frequente[1]
            
            percentual = int((frequencia / len(items)) * 100)
            
            # Define confiança
            if percentual == 100:
                confianca = 'alta'
            elif percentual >= 95:
                confianca = 'alta'
            elif percentual >= 80:
                confianca = 'media'
            else:
                confianca = 'baixa'
            
            # Só mantém alta confiança
            if confianca != 'alta':
                continue
            
            # Exemplos
            exemplos = list(set([it['estabelecimento'] for it in items[:5]]))
            exemplos_str = '; '.join(exemplos[:5])
            
            # Gera hash do padrão
            padrao_num = fnv1a_64_hash(estab_norm)
            
            # Verifica se já existe
            padrao_existente = session.query(BasePadrao).filter_by(
                padrao_estabelecimento=estab_norm
            ).first()
            
            if padrao_existente:
                # Atualiza
                padrao_existente.contagem = len(items)
                padrao_existente.valor_medio = arredondar_2_decimais(valor_medio)
                padrao_existente.valor_min = arredondar_2_decimais(valor_min)
                padrao_existente.valor_max = arredondar_2_decimais(valor_max)
                padrao_existente.percentual_consistencia = percentual
                padrao_existente.confianca = confianca
                padrao_existente.grupo_sugerido = grupo
                padrao_existente.subgrupo_sugerido = subgrupo
                padrao_existente.tipo_gasto_sugerido = tipo_gasto
                padrao_existente.exemplos = exemplos_str
                padrao_existente.status = 'ativo'
                padroes_atualizados += 1
            else:
                # Insere novo
                novo_padrao = BasePadrao(
                    padrao_estabelecimento=estab_norm,
                    padrao_num=padrao_num,
                    contagem=len(items),
                    valor_medio=arredondar_2_decimais(valor_medio),
                    valor_min=arredondar_2_decimais(valor_min),
                    valor_max=arredondar_2_decimais(valor_max),
                    desvio_padrao=0,
                    coef_variacao=0,
                    percentual_consistencia=percentual,
                    confianca=confianca,
                    grupo_sugerido=grupo,
                    subgrupo_sugerido=subgrupo,
                    tipo_gasto_sugerido=tipo_gasto,
                    faixa_valor=None,
                    segmentado=False,
                    exemplos=exemplos_str,
                    data_criacao=datetime.utcnow(),
                    status='ativo'
                )
                session.add(novo_padrao)
                padroes_novos += 1
        
        session.commit()
        
        total = padroes_novos + padroes_atualizados
        print(f"✓ Padrões regenerados:")
        print(f"  - Novos: {padroes_novos}")
        print(f"  - Atualizados: {padroes_atualizados}")
        print(f"  - Total: {total}")
        
        return total
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao regenerar padrões: {e}")
        raise
    finally:
        session.close()
