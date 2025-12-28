"""
Classificador automático de transações
Implementação baseada no n8n:
Base_Padroes → Journal Entries → Palavras-chave (repescagem) → Não Encontrado
"""
from app.models import BasePadrao, JournalEntry, BaseMarcacao, get_db_session
from app.models_ignorar import IgnorarEstabelecimento
from app.utils.normalizer import normalizar, tokens_validos, normalizar_estabelecimento
import re


# Regras de palavras-chave para repescagem (última tentativa)
REGRAS_CLASSIFICACAO = [
    # Prioridade 10 - Serviços específicos
    {'palavras': ['CABELEIREIRO', 'SALAO', 'BARBEARIA'], 'GRUPO': 'Serviços', 'SUBGRUPO': 'Cabeleireiro', 'TipoGasto': 'Fixo', 'prioridade': 10},
    
    # Prioridade 9 - Utilidades
    {'palavras': ['ELETROPAULO', 'ENEL', 'CPFL', 'LUZ', 'ENERGIA'], 'GRUPO': 'Casa', 'SUBGRUPO': 'Energia', 'TipoGasto': 'Fixo', 'prioridade': 9},
    {'palavras': ['SABESP', 'SANEPAR', 'AGUA'], 'GRUPO': 'Casa', 'SUBGRUPO': 'Água', 'TipoGasto': 'Fixo', 'prioridade': 9},
    {'palavras': ['CONDOMINIO'], 'GRUPO': 'Casa', 'SUBGRUPO': 'Condomínio', 'TipoGasto': 'Fixo', 'prioridade': 9},
    {'palavras': ['CLARO', 'VIVO', 'TIM', 'OI', 'TELEFONE', 'CELULAR'], 'GRUPO': 'Casa', 'SUBGRUPO': 'Celular', 'TipoGasto': 'Fixo', 'prioridade': 9},
    {'palavras': ['NET', 'INTERNET', 'FIBRA'], 'GRUPO': 'Casa', 'SUBGRUPO': 'Internet', 'TipoGasto': 'Fixo', 'prioridade': 9},
    {'palavras': ['GAS', 'COMGAS', 'ULTRAGAZ'], 'GRUPO': 'Casa', 'SUBGRUPO': 'Gás', 'TipoGasto': 'Fixo', 'prioridade': 9},
    
    # Prioridade 9 - Alimentação
    {'palavras': ['PIZZ', 'RESTAUR', 'BAR', 'PUB', 'LANCHE', 'BURGER', 'CHURRASCARIA'], 'GRUPO': 'Alimentação', 'SUBGRUPO': 'Saídas', 'TipoGasto': 'Ajustável - Saídas', 'prioridade': 9},
    
    # Prioridade 9 - Viagens
    {'palavras': ['LATAM', 'GOL', 'AZUL', 'AVIANCA'], 'GRUPO': 'Viagens', 'SUBGRUPO': 'Outros', 'TipoGasto': 'Ajustável - Viagens', 'prioridade': 9},
    {'palavras': ['HOTEL', 'POUSADA', 'AIRBNB', 'BOOKING'], 'GRUPO': 'Viagens', 'SUBGRUPO': 'Outros', 'TipoGasto': 'Ajustável - Viagens', 'prioridade': 9},
    
    # Prioridade 8 - Saúde
    {'palavras': ['FARMACIA', 'DROGARIA', 'DROGASIL', 'PACHECO'], 'GRUPO': 'Saúde', 'SUBGRUPO': 'Farmácia', 'TipoGasto': 'Fixo', 'prioridade': 8},
    {'palavras': ['DENTISTA', 'ODONTO'], 'GRUPO': 'Saúde', 'SUBGRUPO': 'Dentista', 'TipoGasto': 'Fixo', 'prioridade': 8},
    
    # Prioridade 8 - Alimentação
    {'palavras': ['IFOOD', 'UBER EATS', 'RAPPI', 'DELIVERY'], 'GRUPO': 'Alimentação', 'SUBGRUPO': 'Pedidos para casa', 'TipoGasto': 'Ajustável - Delivery', 'prioridade': 8},
    {'palavras': ['SUPERMERCADO', 'MERCADO', 'EXTRA', 'CARREFOUR', 'PAO DE ACUCAR'], 'GRUPO': 'Alimentação', 'SUBGRUPO': 'Supermercado', 'TipoGasto': 'Ajustável - Supermercado', 'prioridade': 8},
    
    # Prioridade 8 - Carro
    {'palavras': ['POSTO', 'GASOLINA', 'ALCOOL', 'ETANOL', 'SHELL', 'IPIRANGA'], 'GRUPO': 'Carro', 'SUBGRUPO': 'Abastecimento', 'TipoGasto': 'Ajustável - Carro', 'prioridade': 8},
    {'palavras': ['SEM PARAR', 'CONNECTCAR', 'PEDAGIO'], 'GRUPO': 'Carro', 'SUBGRUPO': 'Sem Parar', 'TipoGasto': 'Ajustável - Carro', 'prioridade': 8},
    {'palavras': ['IPVA', 'LICENCIAMENTO'], 'GRUPO': 'Carro', 'SUBGRUPO': 'IPVA + Licenciamento', 'TipoGasto': 'Ajustável - Carro', 'prioridade': 8},
    
    # Prioridade 8 - Transporte
    {'palavras': ['UBER', 'CABIFY', 'TAXI'], 'GRUPO': 'Transporte', 'SUBGRUPO': 'Uber', 'TipoGasto': 'Ajustável - Uber', 'prioridade': 8},
    
    # Prioridade 8 - Assinaturas
    {'palavras': ['NETFLIX', 'HBO', 'PARAMOUNT', 'GLOBOPLAY'], 'GRUPO': 'Assinaturas', 'SUBGRUPO': 'Outros', 'TipoGasto': 'Ajustável - Assinaturas', 'prioridade': 8},
    {'palavras': ['SPOTIFY'], 'GRUPO': 'Assinaturas', 'SUBGRUPO': 'Spotify', 'TipoGasto': 'Ajustável - Assinaturas', 'prioridade': 8},
    {'palavras': ['YOUTUBE'], 'GRUPO': 'Assinaturas', 'SUBGRUPO': 'Youtube', 'TipoGasto': 'Ajustável - Assinaturas', 'prioridade': 8},
    
    # Prioridade 7 - E-commerce
    {'palavras': ['MERCADO LIVRE', 'MERCADOLIVRE'], 'GRUPO': 'MeLi + Amazon', 'SUBGRUPO': 'MeLi + Amazon', 'TipoGasto': 'Ajustável', 'prioridade': 7},
    {'palavras': ['AMAZON'], 'GRUPO': 'MeLi + Amazon', 'SUBGRUPO': 'MeLi + Amazon', 'TipoGasto': 'Ajustável', 'prioridade': 7},
]


def detectar_fatura_cartao(estabelecimento):
    """Detecta se é fatura de cartão (INT VISA)"""
    estab_norm = normalizar(estabelecimento)
    
    # Padrão: INT [NOME] VISA ou VISA [NOME] INT
    regex1 = re.search(r'\bINT\s+([A-Z]+(?:\s+[A-Z]+)?)\s+VISA\b', estab_norm)
    regex2 = re.search(r'\bVISA\s+([A-Z]+(?:\s+[A-Z]+)?)\s+INT\b', estab_norm)
    
    match = regex1 or regex2
    if match:
        nome_cartao = match.group(1).strip()
        return {
            'GRUPO': 'Fatura',
            'SUBGRUPO': f'Cartão {nome_cartao}',
            'TipoGasto': 'Fatura',
            'MarcacaoIA': 'Fatura Cartão',
            'ValidarIA': ''
        }
    return None


def ignorar_titular(transacao):
    """Verifica se deve ignorar por ser nome do titular"""
    nome_titular = transacao.get('NomeTitular', '')
    estabelecimento = transacao.get('Estabelecimento', '')
    
    if not nome_titular or not estabelecimento:
        return False
    
    # Pega primeiro nome
    primeiro_nome = nome_titular.strip().split()[0] if nome_titular.strip() else ''
    
    # Normaliza
    primeiro_norm = normalizar(primeiro_nome)
    estab_norm = normalizar(estabelecimento)
    
    # Verifica se nome está no estabelecimento (mínimo 4 caracteres)
    if len(primeiro_norm) >= 4 and primeiro_norm in estab_norm:
        return True
    
    return False


def intersecao_tokens(tokens_a, tokens_b):
    """Conta quantos tokens estão em ambas as listas"""
    set_a = set(tokens_a)
    count = 0
    for token in tokens_b:
        if token in set_a:
            count += 1
    return count


def limpar_padrao_segmentado(nome_padrao):
    """Remove sufixo [RANGE] do nome do padrão para comparação"""
    if not nome_padrao:
        return ""
    return re.sub(r'\s*\[.*?\]$', '', nome_padrao)


def encontrar_por_padroes(estabelecimento, valor, padroes):
    """
    Busca na base de padrões aprendidos (Base_Padroes)
    Segue lógica do n8n: candidatosBasePadroes + selecionarPorValor
    """
    estab_norm = normalizar_estabelecimento(estabelecimento)
    tokens_estab = tokens_validos(estabelecimento)
    
    candidatos = []
    
    for padrao in padroes:
        # Só considera padrões com alta confiança
        if padrao.confianca != 'alta':
            continue
        
        # Deve ter todos os campos preenchidos
        if not padrao.grupo_sugerido or not padrao.subgrupo_sugerido or not padrao.tipo_gasto_sugerido:
            continue
        
        # Remove sufixo de segmentação para comparação (ex: "IBERIA [1K-2K]" -> "IBERIA")
        nome_limpo = limpar_padrao_segmentado(padrao.padrao_estabelecimento)
        padrao_norm = normalizar_estabelecimento(nome_limpo)
        tokens_padrao = tokens_validos(nome_limpo)
        
        score = 0
        
        # Match exato (melhor score)
        if padrao_norm == estab_norm:
            score = len(padrao_norm) + (len(tokens_padrao) * 5)
            candidatos.append({
                'padrao': padrao,
                'score': score,
                'tipo': 'exato'
            })
            continue
        
        # Contains (bom score)
        if len(tokens_padrao) < 2:
            # Palavras curtas precisam de match completo
            if re.search(r'\b' + re.escape(padrao_norm) + r'\b', estab_norm):
                score = len(padrao_norm) + 3
                candidatos.append({
                    'padrao': padrao,
                    'score': score,
                    'tipo': 'contains'
                })
                continue
        else:
            # Palavras longas podem ter match parcial
            if padrao_norm in estab_norm or estab_norm in padrao_norm:
                score = len(padrao_norm) + (len(tokens_padrao) * 5)
                candidatos.append({
                    'padrao': padrao,
                    'score': score,
                    'tipo': 'contains'
                })
                continue
        
        # Interseção de tokens (score médio)
        inter = intersecao_tokens(tokens_padrao, tokens_estab)
        limiar = 1 if min(len(tokens_padrao), len(tokens_estab)) == 1 else 2
        
        if inter >= limiar:
            score = inter * 10 + len(tokens_padrao)
            candidatos.append({
                'padrao': padrao,
                'score': score,
                'tipo': 'tokens'
            })
    
    if not candidatos:
        return None
    
    # Ordena por score
    candidatos.sort(key=lambda x: x['score'], reverse=True)
    
    # Seleciona por valor (se disponível)
    if valor is not None:
        valor_abs = abs(float(valor))
        
        # Calcula distância de valor para cada candidato
        for cand in candidatos:
            if cand['padrao'].valor_medio:
                try:
                    valor_medio = abs(float(cand['padrao'].valor_medio))
                    cand['dist_valor'] = abs(valor_abs - valor_medio)
                except:
                    cand['dist_valor'] = float('inf')
            else:
                cand['dist_valor'] = float('inf')
        
        # Reordena considerando valor
        candidatos.sort(key=lambda x: (x.get('dist_valor', float('inf')), -x['score']))
    
    # Retorna o melhor
    melhor = candidatos[0]['padrao']
    return {
        'GRUPO': melhor.grupo_sugerido,
        'SUBGRUPO': melhor.subgrupo_sugerido,
        'TipoGasto': melhor.tipo_gasto_sugerido,
        'MarcacaoIA': 'Base_Padroes',
        'ValidarIA': ''
    }


def encontrar_por_historico(estabelecimento, valor, historico):
    """
    Busca no histórico (Journal Entries)
    Segue lógica do n8n: matchHistorico
    """
    tokens_estab = tokens_validos(estabelecimento)
    valor_abs = abs(float(valor)) if valor is not None else None
    
    candidatos = []
    
    for entrada in historico:
        # Deve ter classificação completa
        if not entrada.GRUPO or not entrada.SUBGRUPO or not entrada.TipoGasto:
            continue
        
        tokens_hist = tokens_validos(entrada.Estabelecimento or '')
        
        # Calcula interseção
        inter = intersecao_tokens(tokens_hist, tokens_estab)
        
        # Verifica valor
        valor_ok = True
        if valor_abs is not None and entrada.Valor is not None:
            valor_hist = abs(float(entrada.Valor))
            diff = abs(valor_hist - valor_abs)
            diff_percent = diff / max(valor_hist, valor_abs) if max(valor_hist, valor_abs) > 0 else 0
            
            # Valor deve estar próximo (±5 ou ±20%)
            valor_ok = (diff <= 5) or (diff_percent <= 0.20)
        
        # Limiar de interseção
        limiar = 1 if min(len(tokens_hist), len(tokens_estab)) == 1 else 2
        
        if inter >= limiar and valor_ok:
            candidatos.append({
                'entrada': entrada,
                'inter': inter,
                'data': entrada.Data
            })
    
    if not candidatos:
        return None
    
    # Ordena por data (mais recente primeiro)
    candidatos.sort(key=lambda x: x['data'] if x['data'] else '', reverse=True)
    
    # Retorna o mais recente
    melhor = candidatos[0]['entrada']
    
    # Filtro PIX: se é PIX, marca para validar ao invés de usar histórico
    if re.search(r'\bPIX\b', estabelecimento, re.IGNORECASE):
        return None  # Não usa histórico para PIX
    
    return {
        'GRUPO': melhor.GRUPO,
        'SUBGRUPO': melhor.SUBGRUPO,
        'TipoGasto': melhor.TipoGasto,
        'MarcacaoIA': 'Journal Entries',
        'ValidarIA': ''
    }


def encontrar_por_regras(estabelecimento, marcacoes_validas):
    """
    Busca por regras de palavras-chave (repescagem)
    Usado como última tentativa antes de marcar como "Não Encontrado"
    """
    estab_norm = normalizar(estabelecimento)
    
    matches = []
    for regra in REGRAS_CLASSIFICACAO:
        for palavra in regra['palavras']:
            palavra_norm = normalizar(palavra)
            
            # Match com boundaries
            regex = re.compile(r'\b' + re.escape(palavra_norm) + r'\b')
            if regex.search(estab_norm):
                # Valida contra base_marcacoes
                chave = f"{regra['GRUPO']}|{regra['SUBGRUPO']}|{regra['TipoGasto']}"
                if chave in marcacoes_validas:
                    matches.append({
                        'GRUPO': regra['GRUPO'],
                        'SUBGRUPO': regra['SUBGRUPO'],
                        'TipoGasto': regra['TipoGasto'],
                        'prioridade': regra['prioridade'],
                        'palavra_encontrada': palavra
                    })
                break
    
    # Retorna o de maior prioridade
    if matches:
        matches.sort(key=lambda x: x['prioridade'], reverse=True)
        melhor = matches[0]
        return {
            'GRUPO': melhor['GRUPO'],
            'SUBGRUPO': melhor['SUBGRUPO'],
            'TipoGasto': melhor['TipoGasto'],
            'MarcacaoIA': 'Palavras-chave',
            'ValidarIA': ''
        }
    
    return None


def classificar_transacoes(transacoes):
    """
    Classifica lista de transações automaticamente
    LÓGICA DO N8N:
    0. IdParcela (busca exata por compra parcelada - MÁXIMA PRIORIDADE)
    1. Fatura de cartão (prioridade máxima)
    2. Ignorar titular
    3. Base_Padroes (confiança='alta')
    4. Journal Entries (histórico)
    5. Palavras-chave (repescagem)
    6. Não Encontrado
    
    Args:
        transacoes (list): Lista de transações
        
    Returns:
        list: Transações classificadas
    """
    print(f"\n🤖 Classificando {len(transacoes)} transações...")
    
    session = get_db_session()
    
    try:
        # Carrega padrões (alta confiança)
        padroes = session.query(BasePadrao).filter(
            BasePadrao.status == 'ativo',
            BasePadrao.confianca == 'alta'
        ).all()
        print(f"✓ Carregados {len(padroes)} padrões (alta confiança)")
        
        # Carrega histórico (Journal Entries)
        historico = session.query(JournalEntry).all()
        print(f"✓ Carregadas {len(historico)} entradas históricas")
        
        # Carrega marcações válidas (para validar regras)
        marcacoes = session.query(BaseMarcacao).all()
        marcacoes_validas = set(
            f"{m.GRUPO}|{m.SUBGRUPO}|{m.TipoGasto}"
            for m in marcacoes
        )
        print(f"✓ Carregadas {len(marcacoes_validas)} marcações válidas")
        
        classificadas = 0
        nao_encontradas = 0
        ignoradas = 0
        por_tipo = {
            'IdParcela': 0,
            'Fatura Cartão': 0,
            'Ignorar - Nome do Titular': 0,
            'Base_Padroes': 0,
            'Journal Entries': 0,
            'Palavras-chave': 0,
            'Não Encontrado': 0
        }
        
        for trans in transacoes:
            estabelecimento = trans.get('Estabelecimento', '')
            valor = trans.get('Valor')
            id_parcela = trans.get('IdParcela')
            
            # 0. IdParcela (busca exata por compra parcelada - MÁXIMA PRIORIDADE)
            if id_parcela:
                # Busca outra parcela da mesma compra que já tenha classificação
                parcela_existente = session.query(JournalEntry).filter(
                    JournalEntry.IdParcela == id_parcela,
                    JournalEntry.GRUPO.isnot(None),
                    JournalEntry.GRUPO != ''
                ).first()
                
                if parcela_existente:
                    trans.update({
                        'GRUPO': parcela_existente.GRUPO,
                        'SUBGRUPO': parcela_existente.SUBGRUPO,
                        'TipoGasto': parcela_existente.TipoGasto,
                        'MarcacaoIA': 'IdParcela',
                        'ValidarIA': ''
                    })
                    por_tipo['IdParcela'] += 1
                    classificadas += 1
                    continue
            
            # 1. Fatura de cartão (prioridade máxima)
            fatura = detectar_fatura_cartao(estabelecimento)
            if fatura:
                trans.update(fatura)
                por_tipo['Fatura Cartão'] += 1
                classificadas += 1
                continue
            
            # 2. Ignorar titular
            if ignorar_titular(trans):
                trans.update({
                    'GRUPO': '',
                    'SUBGRUPO': '',
                    'TipoGasto': '',
                    'MarcacaoIA': 'Ignorar - Nome do Titular',
                    'ValidarIA': '',
                    'Ignorar': 'SIM'
                })
                por_tipo['Ignorar - Nome do Titular'] += 1
                ignoradas += 1
                continue
            
            # 2.1 Ignorar estabelecimentos da lista do admin
            origem = trans.get('origem', '')
            tipo_arquivo = 'cartao' if 'Fatura' in origem else 'extrato' if 'Extrato' in origem else 'ambos'
            estabelecimentos_ignorar = session.query(IgnorarEstabelecimento).filter(
                (IgnorarEstabelecimento.tipo == 'ambos') | (IgnorarEstabelecimento.tipo == tipo_arquivo)
            ).all()
            
            deve_ignorar = False
            for ig in estabelecimentos_ignorar:
                if ig.nome.lower() in estabelecimento.lower():
                    deve_ignorar = True
                    break
            
            if deve_ignorar:
                trans.update({
                    'GRUPO': '',
                    'SUBGRUPO': '',
                    'TipoGasto': '',
                    'MarcacaoIA': 'Ignorar - Lista Admin',
                    'ValidarIA': '',
                    'Ignorar': 'SIM'
                })
                por_tipo['Ignorar - Nome do Titular'] += 1
                ignoradas += 1
                continue
            
            # 3. Base_Padroes (confiança='alta')
            padrao = encontrar_por_padroes(estabelecimento, valor, padroes)
            if padrao:
                trans.update(padrao)
                por_tipo['Base_Padroes'] += 1
                classificadas += 1
                continue
            
            # 4. Journal Entries (histórico)
            historico_match = encontrar_por_historico(estabelecimento, valor, historico)
            if historico_match:
                trans.update(historico_match)
                por_tipo['Journal Entries'] += 1
                classificadas += 1
                continue
            
            # 5. Palavras-chave (repescagem)
            regra = encontrar_por_regras(estabelecimento, marcacoes_validas)
            if regra:
                trans.update(regra)
                por_tipo['Palavras-chave'] += 1
                classificadas += 1
                continue
            
            # 6. Não Encontrado
            trans.update({
                'GRUPO': '',
                'SUBGRUPO': '',
                'TipoGasto': '',
                'MarcacaoIA': 'Não Encontrado',
                'ValidarIA': 'VALIDAR',
                'Ignorar': 'NÃO'
            })
            por_tipo['Não Encontrado'] += 1
            nao_encontradas += 1
        
        # Inicializar campo Ignorar para todas as transações que não foram marcadas
        for trans in transacoes:
            if 'Ignorar' not in trans:
                trans['Ignorar'] = 'NÃO'
        
        print(f"\n📊 Resultado da classificação:")
        print(f"  IdParcela: {por_tipo['IdParcela']}")
        print(f"  Fatura Cartão: {por_tipo['Fatura Cartão']}")
        print(f"  Ignorar - Titular: {por_tipo['Ignorar - Nome do Titular']}")
        print(f"  Base_Padroes: {por_tipo['Base_Padroes']}")
        print(f"  Journal Entries: {por_tipo['Journal Entries']}")
        print(f"  Palavras-chave: {por_tipo['Palavras-chave']}")
        print(f"  Não Encontrado: {por_tipo['Não Encontrado']}")
        print(f"\n✓ Total classificadas: {classificadas}")
        print(f"⚠ Precisam validação: {nao_encontradas}")
        print(f"ℹ Ignoradas: {ignoradas}")
        
        return transacoes
        
    finally:
        session.close()

