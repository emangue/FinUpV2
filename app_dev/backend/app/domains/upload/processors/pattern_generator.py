"""
Pattern Generator - Gerador de Base Padrões
Replica lógica do n8n para criar/atualizar base_padroes

Baseado em: arquivo_teste_n8n.json (node "Code in JavaScript1")
Versão: 1.0.0
Data: 15/01/2026
"""

import re
import math
import hashlib
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session

from app.domains.transactions.models import JournalEntry
from app.domains.patterns.models import BasePadroes
from app.shared.utils import normalizar_estabelecimento


def arred2(n: float) -> float:
    """Arredonda para 2 casas decimais"""
    return round(n, 2)


def normalizar_chave_padrao(padrao: str) -> str:
    """
    Normaliza chave do padrão
    Formatos:
    - Simples: "ESTABELECIMENTO"
    - Parcelado: "ESTABELECIMENTO|valor_total_centavos|total_parcelas"

    v5: remove tudo que não é [A-Z0-9] da base do estabelecimento,
    garantindo consistência com o estab_hash gerado pelo marker.py v5.
    """
    s = str(padrao or "").strip()
    if not s:
        return ""
    
    parts = s.split("|")
    if len(parts) == 1:
        return re.sub(r'[^A-Z0-9]', '', parts[0].upper())
    
    # Parcelado
    estab = re.sub(r'[^A-Z0-9]', '', parts[0].upper())
    valor_tot_cent = re.sub(r'[^\d]', '', str(parts[1]))
    tot = str(parts[2] or "").zfill(2)
    
    return f"{estab}|{valor_tot_cent}|{tot}"


def detectar_parcela_no_final(estabelecimento: str, origem: str = "") -> Optional[Dict]:
    """
    Detecta parcela no formato XX/YY no final do estabelecimento
    VALIDAÇÃO CONTEXTUAL:
    - Extratos: XX/YY com YY <= 12 e XX <= 31 é data, não parcela
    - Faturas: XX/YY sempre é parcela
    """
    match = re.search(r'\s*(\d{1,2})/(\d{1,2})\s*$', estabelecimento or "")
    if not match:
        return None
    
    p = int(match.group(1))
    t = int(match.group(2))
    
    if not (1 <= p <= t <= 99):
        return None
    
    # Validação contextual
    eh_extrato = 'extrato' in origem.lower()
    if eh_extrato and t <= 12 and p <= 31:
        return None  # É data, não parcela
    
    return {'parcela': p, 'total': t}


def montar_padrao(estabelecimento: str, valor: float, parcela_info: Optional[Dict]) -> str:
    """
    Monta chave do padrão (FORMATO COMPATÍVEL COM CLASSIFIER)
    - Sem parcela: normaliza estabelecimento apenas
    - Com parcela: adiciona |valor_total_centavos|total_parcelas
    
    IMPORTANTE: Retorna SEM faixa de valor. 
    A segmentação por faixa é feita posteriormente com " [faixa]"

    v5: remove tudo que não é [A-Z0-9] da base (mesmo padrão do marker.py v5).
    Para parcelados, extrai a base antes de normalizar.
    """
    if parcela_info:
        # v5: extrair base sem a notação de parcela antes de normalizar
        base = re.sub(r'\s*\(?\d{1,2}/\d{1,2}\)?\s*$', '', estabelecimento).strip()
        estab = re.sub(r'[^A-Z0-9]', '', base.upper())
        tot = parcela_info['total']
        v_parc = abs(valor)
        v_tot = arred2(v_parc * tot)
        v_cent = round(v_tot * 100)
        return f"{estab}|{v_cent}|{str(tot).zfill(2)}"
    
    estab = re.sub(r'[^A-Z0-9]', '', estabelecimento.upper())
    return estab


def get_faixa_valor(valor: float) -> str:
    """Determina faixa de valor"""
    v = abs(valor)
    if v == 0:
        return "ZERO"
    if v < 50:
        return "0-50"
    if v < 100:
        return "50-100"
    if v < 200:
        return "100-200"
    if v < 500:
        return "200-500"
    if v < 1000:
        return "500-1K"
    if v < 2000:
        return "1K-2K"
    if v < 5000:
        return "2K-5K"
    return "5K+"


def get_categoria_geral_from_grupo(db: Session, grupo: str, user_id: int) -> str:
    """
    Busca CategoriaGeral correspondente ao Grupo em base_grupos_config
    
    Args:
        db: Sessão do banco
        grupo: Nome do grupo
        user_id: ID do usuário
    
    Returns:
        CategoriaGeral ou string vazia se não encontrado
    """
    if not grupo:
        return ''
    
    from sqlalchemy import text
    
    result = db.execute(
        text("SELECT categoria_geral FROM base_grupos_config WHERE nome_grupo = :grupo"),
        {"grupo": grupo}
    ).fetchone()
    
    return result[0] if result else ''


def fnv1a_64_to_dec(s: str) -> str:
    """
    Hash FNV-1a 64-bit (retorna string decimal sem sinal)
    Compatível com JavaScript BigInt
    """
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    
    h = FNV_OFFSET_64
    for char in s:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    
    return str(h)


def estatisticas_do_padrao(registros: List[Dict]) -> Dict:
    """
    Calcula estatísticas de um grupo de transações com mesmo padrão
    
    Retorna:
    - quantidade: total de ocorrências
    - percentual: consistência da classificação mais frequente
    - grupo, subgrupo, tipo: classificação mais frequente
    - valorMedio, valorMax, valorMin
    - desvioPadrao, coefVariacao
    - temMultiplosContextos: se tem classificações diferentes em faixas diferentes
    - porFaixa: agrupamento por faixa de valor
    - exemplos: até 5 exemplos de estabelecimentos
    """
    key_cls = lambda x: f"{x['GRUPO']}__{x['SUBGRUPO']}__{x['TipoGasto']}"
    
    cont = defaultdict(int)
    cont_detalhado = defaultdict(list)
    valores = []
    exemplos = []
    por_faixa = defaultdict(lambda: defaultdict(int))
    
    for reg in registros:
        k = key_cls(reg)
        cont[k] += 1
        
        cont_detalhado[k].append({
            'valor': abs(reg['Valor']),
            'data': reg.get('Data', ''),
            'estab': reg['Estabelecimento']
        })
        
        valores.append(abs(reg['Valor']))
        
        if len(exemplos) < 5:
            exemplos.append(reg['Estabelecimento'])
        
        faixa = get_faixa_valor(reg['Valor'])
        por_faixa[faixa][k] += 1
    
    # Classificação mais frequente (desempate por data mais recente)
    entries = sorted(cont.items(), key=lambda x: (-x[1], max((d['data'] for d in cont_detalhado[x[0]]), default='')))
    
    if not entries:
        return {
            'quantidade': 0,
            'percentual': 0,
            'grupo': '',
            'subgrupo': '',
            'tipo': '',
            'valorMedio': 0,
            'valorMax': 0,
            'valorMin': 0,
            'desvioPadrao': 0,
            'coefVariacao': 0,
            'temMultiplosContextos': False,
            'porFaixa': {},
            'exemplos': []
        }
    
    max_key, max_count = entries[0]
    grupo, subgrupo, tipo = max_key.split('__')
    quantidade = len(registros)
    
    # Percentual de consistência
    classificacoes_unicas = set(key_cls(x) for x in registros)
    todas_iguais = len(classificacoes_unicas) == 1 and grupo and subgrupo and tipo
    percentual = 100 if todas_iguais else round((max_count / quantidade) * 100)
    
    # Estatísticas de valor
    soma = sum(valores)
    valor_medio = arred2(soma / len(valores)) if valores else 0
    valor_max = arred2(max(valores)) if valores else 0
    valor_min = arred2(min(valores)) if valores else 0
    
    desvio_padrao = 0
    if len(valores) > 1:
        variancia = sum((v - valor_medio) ** 2 for v in valores) / len(valores)
        desvio_padrao = arred2(math.sqrt(variancia))
    
    coef_variacao = arred2(desvio_padrao / valor_medio) if valor_medio > 0 else 0
    
    # Múltiplos contextos: classificações diferentes em faixas diferentes
    classificacoes_por_faixa = defaultdict(list)
    for faixa, classes in por_faixa.items():
        for cls in classes.keys():
            classificacoes_por_faixa[cls].append(faixa)
    
    tem_multiplos_contextos = len(classificacoes_por_faixa) > 1 and len(por_faixa) > 1
    
    return {
        'quantidade': quantidade,
        'percentual': percentual,
        'grupo': grupo,
        'subgrupo': subgrupo,
        'tipo': tipo,
        'valorMedio': valor_medio,
        'valorMax': valor_max,
        'valorMin': valor_min,
        'desvioPadrao': desvio_padrao,
        'coefVariacao': coef_variacao,
        'temMultiplosContextos': tem_multiplos_contextos,
        'porFaixa': dict(por_faixa),
        'exemplos': exemplos
    }


def gerar_padroes_segmentados(db: Session, user_id: int, padrao_str: str, registros: List[Dict], stats: Dict) -> List[Dict]:
    """
    Gera padrões (segmentados por faixa de valor ou simples)
    
    Segmenta SE:
    - Critério 1: Múltiplos contextos (classificações diferentes por faixa)
    - Critério 2: Coef. variação > 0.3 E consistência < 85%
    - Critério 3: Pelo menos 4 registros
    """
    padroes = []
    
    criterio1 = stats['temMultiplosContextos']
    criterio2 = stats['coefVariacao'] > 0.3 and stats['percentual'] < 85
    criterio3 = len(registros) >= 4
    
    deve_segmentar = (criterio1 or criterio2) and criterio3
    
    if deve_segmentar and len(registros) >= 3:
        # Segmentar por faixa
        por_faixa = defaultdict(list)
        
        for reg in registros:
            faixa = get_faixa_valor(reg['Valor'])
            por_faixa[faixa].append(reg)
        
        for faixa, items in por_faixa.items():
            faixa_unica = len(por_faixa) == 1
            if len(items) < 2 and not faixa_unica:
                continue
            
            stats_faixa = estatisticas_do_padrao(items)
            # FORMATO COMPATÍVEL COM CLASSIFIER: espaço + colchetes
            padrao_com_faixa = f"{padrao_str} [{faixa}]"
            
            is_parcelado = bool(re.search(r'\|\d+\|\d{2}$', padrao_str))
            valor_referencia = stats_faixa['valorMax'] if is_parcelado else stats_faixa['valorMedio']
            
            # Confiança
            confianca_faixa = "baixa"
            if stats_faixa['percentual'] == 100:
                confianca_faixa = "alta"
            elif stats_faixa['percentual'] >= 95:
                confianca_faixa = "alta"
            elif stats_faixa['percentual'] >= 80:
                confianca_faixa = "media"
            
            # Buscar categoria_geral
            categoria_geral = get_categoria_geral_from_grupo(db, stats_faixa['grupo'], user_id)
            
            padroes.append({
                'padrao_estabelecimento': padrao_com_faixa,
                'padrao_num': fnv1a_64_to_dec(padrao_com_faixa),
                'contagem': stats_faixa['quantidade'],
                'valor_medio': arred2(valor_referencia),
                'valor_min': stats_faixa['valorMin'],
                'valor_max': stats_faixa['valorMax'],
                'desvio_padrao': stats_faixa['desvioPadrao'],
                'coef_variacao': stats_faixa['coefVariacao'],
                'percentual_consistencia': stats_faixa['percentual'],
                'confianca': confianca_faixa,
                'grupo_sugerido': stats_faixa['grupo'] or '',
                'subgrupo_sugerido': stats_faixa['subgrupo'] or '',
                'tipo_gasto_sugerido': stats_faixa['tipo'] or '',
                'categoria_geral_sugerida': categoria_geral,
                'faixa_valor': faixa,
                'segmentado': 1,
                'exemplos': '; '.join(set(stats_faixa['exemplos'][:5])),
                'data_criacao': datetime.now(),
                'status': 'ativo'
            })
        
        return padroes
    
    # Padrão simples (não segmentado)
    is_parcelado = bool(re.search(r'\|\d+\|\d{2}$', padrao_str))
    valor_referencia = stats['valorMax'] if is_parcelado else stats['valorMedio']
    
    # Confiança
    confianca = "baixa"
    if stats['percentual'] == 100:
        confianca = "alta"
    elif stats['percentual'] >= 95:
        confianca = "alta"
    elif stats['percentual'] >= 80 and stats['coefVariacao'] < 0.5:
        confianca = "media"
    
    # Buscar categoria_geral
    categoria_geral = get_categoria_geral_from_grupo(db, stats['grupo'], user_id)
    
    return [{
        'padrao_estabelecimento': padrao_str,
        'padrao_num': fnv1a_64_to_dec(padrao_str),
        'contagem': stats['quantidade'],
        'valor_medio': arred2(valor_referencia),
        'valor_min': stats['valorMin'],
        'valor_max': stats['valorMax'],
        'desvio_padrao': stats['desvioPadrao'],
        'coef_variacao': stats['coefVariacao'],
        'percentual_consistencia': stats['percentual'],
        'confianca': confianca,
        'grupo_sugerido': stats['grupo'] or '',
        'subgrupo_sugerido': stats['subgrupo'] or '',
        'tipo_gasto_sugerido': stats['tipo'] or '',
        'categoria_geral_sugerida': categoria_geral,
        'faixa_valor': None,
        'segmentado': 0,
        'exemplos': '; '.join(set(stats['exemplos'][:5])),
        'data_criacao': datetime.now(),
        'status': 'ativo'
    }]


def gerar_base_padroes(db: Session, user_id: int) -> List[Dict]:
    """
    Gera base_padroes a partir de journal_entries
    
    Processo:
    1. Buscar todas as transações do usuário
    2. Agrupar por padrão normalizado
    3. Calcular estatísticas por grupo
    4. Gerar padrões (segmentados ou simples)
    5. Filtrar apenas alta confiança
    
    Returns:
        Lista de dicionários com padrões gerados
    """
    # 1. Buscar transações
    transacoes = db.query(JournalEntry).filter(
        JournalEntry.user_id == user_id
    ).all()
    
    if not transacoes:
        return []
    
    # 2. Agrupar por padrão
    buckets = defaultdict(list)
    
    for t in transacoes:
        estab = t.Estabelecimento or ''
        valor = t.Valor or 0
        origem = t.tipodocumento or ''
        
        parcela_info = detectar_parcela_no_final(estab, origem)
        padrao_str = normalizar_chave_padrao(montar_padrao(estab, valor, parcela_info))
        
        if not padrao_str:
            continue
        
        registro = {
            'padraoStr': padrao_str,
            'GRUPO': t.GRUPO or '',
            'SUBGRUPO': t.SUBGRUPO or '',
            'TipoGasto': t.TipoGasto or '',
            'Valor': valor,
            'Estabelecimento': estab,
            'Data': t.Data or ''
        }
        
        buckets[padrao_str].append(registro)
    
    # 3. Gerar padrões
    saida = []
    for padrao_str, registros in buckets.items():
        stats = estatisticas_do_padrao(registros)
        padroes = gerar_padroes_segmentados(db, user_id, padrao_str, registros, stats)
        saida.extend(padroes)
    
    # 4. Filtrar apenas alta confiança (>= 95% consistência e >= 2 ocorrências)
    filtrados = [
        p for p in saida 
        if p['contagem'] >= 2 and p['percentual_consistencia'] >= 95
    ]
    
    return filtrados


def atualizar_base_padroes(db: Session, user_id: int, padroes: List[Dict]) -> Tuple[int, int]:
    """
    Atualiza base_padroes no banco
    
    Estratégia:
    1. Busca por padrao_num (hash único) - mais confiável que estabelecimento
    2. Se existe: atualiza estatísticas (SEM mudar padrao_num)
    3. Se não: verifica duplicata por padrao_num antes de criar
    4. Rollback individual em caso de erro
    
    Returns:
        (criados, atualizados)
    """
    import logging
    logger = logging.getLogger(__name__)
    criados = 0
    atualizados = 0
    
    for padrao_dict in padroes:
        try:
            padrao_num = padrao_dict.get('padrao_num')
            if not padrao_num:
                logger.warning(f"Padrão sem hash: {padrao_dict.get('padrao_estabelecimento')}")
                continue
            
            # 🔍 BUSCA POR HASH (mais confiável que estabelecimento)
            padrao_existente = db.query(BasePadroes).filter(
                BasePadroes.padrao_num == padrao_num,
                BasePadroes.user_id == user_id
            ).first()
            
            if padrao_existente:
                # ✅ ATUALIZAR - Não toca em padrao_num e padrao_estabelecimento
                campos_update = ['contagem', 'valor_medio', 'valor_min', 'valor_max', 
                                'desvio_padrao', 'coef_variacao', 'percentual_consistencia',
                                'confianca', 'grupo_sugerido', 'subgrupo_sugerido', 
                                'tipo_gasto_sugerido', 'categoria_geral_sugerida',
                                'faixa_valor', 'segmentado', 'exemplos', 'status']
                
                for key in campos_update:
                    if key in padrao_dict:
                        setattr(padrao_existente, key, padrao_dict[key])
                
                padrao_existente.data_criacao = datetime.now()  # Atualiza timestamp
                atualizados += 1
            else:
                # ✅ CRIAR NOVO - Verifica duplicata antes
                duplicata = db.query(BasePadroes).filter(
                    BasePadroes.padrao_num == padrao_num
                ).first()
                
                if duplicata:
                    logger.warning(f"⚠️  Duplicata detectada (outro user?): {padrao_num}")
                    continue
                
                novo_padrao = BasePadroes(
                    user_id=user_id,
                    **padrao_dict
                )
                db.add(novo_padrao)
                criados += 1
            
            db.flush()
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar padrão {padrao_dict.get('padrao_estabelecimento', 'N/A')}: {str(e)}")
            db.rollback()
            continue
    
    try:
        db.commit()
        logger.info(f"✅ Base padrões atualizada: {criados} criados, {atualizados} atualizados")
    except Exception as e:
        logger.error(f"❌ Erro ao commitar base_padroes: {str(e)}")
        db.rollback()
    
    return criados, atualizados


def regenerar_base_padroes_completa(db: Session, user_id: int) -> Dict:
    """
    Regenera base_padroes completa do usuário
    
    Returns:
        Estatísticas da operação
    """
    # Gerar padrões
    padroes = gerar_base_padroes(db, user_id)
    
    # Atualizar banco
    criados, atualizados = atualizar_base_padroes(db, user_id, padroes)
    
    return {
        'total_padroes_gerados': len(padroes),
        'criados': criados,
        'atualizados': atualizados,
        'user_id': user_id
    }
