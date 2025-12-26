#!/usr/bin/env python3
"""
Analisa Journal Entries, identifica empresas frequentes e cria logos
"""
import sys
import os
from collections import Counter
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import JournalEntry, EstabelecimentoLogo, get_db_session, init_db

init_db()

# Mapeamento de padrões de estabelecimento para logos conhecidos
LOGOS_CONHECIDOS = {
    # Transporte
    r'uber(?!.*eats)': {'nome': 'Uber', 'emoji': '🚗', 'cor': '#000000'},
    r'99\s?(taxi|pop|moto)?': {'nome': '99', 'emoji': '🚕', 'cor': '#FFD700'},
    r'cabify': {'nome': 'Cabify', 'emoji': '🚖', 'cor': '#6C2C91'},
    
    # Food Delivery
    r'i\s?food|ifood': {'nome': 'iFood', 'emoji': '🍔', 'cor': '#EA1D2C'},
    r'rappi': {'nome': 'Rappi', 'emoji': '🛵', 'cor': '#FF441F'},
    r'uber\s?eats': {'nome': 'Uber Eats', 'emoji': '🍕', 'cor': '#06C167'},
    
    # Restaurantes
    r'z\s?deli': {'nome': 'Z Deli', 'emoji': '🥪', 'cor': '#000000'},
    r'outback': {'nome': 'Outback', 'emoji': '🥩', 'cor': '#8B4513'},
    r'mc\s?donald': {'nome': "McDonald's", 'emoji': '🍟', 'cor': '#FFC72C'},
    r'burger\s?king|bk\s': {'nome': 'Burger King', 'emoji': '👑', 'cor': '#D62300'},
    r'subway': {'nome': 'Subway', 'emoji': '🥖', 'cor': '#009639'},
    r'spoleto': {'nome': 'Spoleto', 'emoji': '🍝', 'cor': '#E30613'},
    r'giraffa': {'nome': 'Giraffas', 'emoji': '🍔', 'cor': '#FFD100'},
    
    # Streaming
    r'netflix': {'nome': 'Netflix', 'emoji': '🎬', 'cor': '#E50914'},
    r'spotify': {'nome': 'Spotify', 'emoji': '🎵', 'cor': '#1DB954'},
    r'youtube|yt premium': {'nome': 'YouTube Premium', 'emoji': '▶️', 'cor': '#FF0000'},
    r'amazon\s?prime\s?(video)?': {'nome': 'Amazon Prime', 'emoji': '📺', 'cor': '#00A8E1'},
    r'disney\s?\+?|disneyplus': {'nome': 'Disney+', 'emoji': '🏰', 'cor': '#113CCF'},
    r'hbo\s?max': {'nome': 'HBO Max', 'emoji': '🎭', 'cor': '#8B00FF'},
    r'globoplay': {'nome': 'Globoplay', 'emoji': '📺', 'cor': '#FA0000'},
    r'apple\s?(tv|music)': {'nome': 'Apple', 'emoji': '🍎', 'cor': '#000000'},
    
    # Bancos
    r'nubank|nu\s?bank': {'nome': 'Nubank', 'emoji': '💜', 'cor': '#820AD1'},
    r'banco\s?inter|inter\s?bank': {'nome': 'Banco Inter', 'emoji': '🧡', 'cor': '#FF7A00'},
    r'itau|itaú': {'nome': 'Itaú', 'emoji': '🔶', 'cor': '#EC7000'},
    r'bradesco': {'nome': 'Bradesco', 'emoji': '🔴', 'cor': '#CC092F'},
    r'santander': {'nome': 'Santander', 'emoji': '🔴', 'cor': '#EC0000'},
    r'caixa\s?economica|caixa': {'nome': 'Caixa', 'emoji': '🔵', 'cor': '#003E8A'},
    r'banco\s?do\s?brasil|bb\s': {'nome': 'Banco do Brasil', 'emoji': '💛', 'cor': '#FFDD00'},
    r'next\s?bank': {'nome': 'Next', 'emoji': '⚡', 'cor': '#00D9A5'},
    r'c6\s?bank': {'nome': 'C6 Bank', 'emoji': '⚫', 'cor': '#000000'},
    
    # E-commerce
    r'amazon(?!.*prime)': {'nome': 'Amazon', 'emoji': '📦', 'cor': '#FF9900'},
    r'mercado\s?livre|mercadolivre': {'nome': 'Mercado Livre', 'emoji': '🛒', 'cor': '#FFE600'},
    r'magazine\s?luiza|magalu': {'nome': 'Magazine Luiza', 'emoji': '🏪', 'cor': '#0086FF'},
    r'shopee': {'nome': 'Shopee', 'emoji': '🛍️', 'cor': '#EE4D2D'},
    r'americanas': {'nome': 'Americanas', 'emoji': '🛒', 'cor': '#E50914'},
    r'casas\s?bahia': {'nome': 'Casas Bahia', 'emoji': '🏠', 'cor': '#0050A0'},
    
    # Supermercados
    r'carrefour': {'nome': 'Carrefour', 'emoji': '🛒', 'cor': '#0055A4'},
    r'pao\s?de\s?acucar|p.?o\s?de\s?a.?ucar': {'nome': 'Pão de Açúcar', 'emoji': '🍞', 'cor': '#00A859'},
    r'extra\s?hipermercado|extra\s': {'nome': 'Extra', 'emoji': '🛒', 'cor': '#E2001A'},
    r'assai': {'nome': 'Assaí', 'emoji': '🛒', 'cor': '#FFD100'},
    r'atacadao|atacadão': {'nome': 'Atacadão', 'emoji': '🛒', 'cor': '#005BAA'},
    
    # Farmácias
    r'drog[ao](?:ria|rias)?|droga\s?(?:sil|raia|pacheco)': {'nome': 'Farmácia', 'emoji': '💊', 'cor': '#00A859'},
    r'pacheco': {'nome': 'Drogaria Pacheco', 'emoji': '💊', 'cor': '#009639'},
    r'sao\s?paulo|s.o\s?paulo|drogaria\s?sp': {'nome': 'Drogaria São Paulo', 'emoji': '💊', 'cor': '#E2001A'},
    
    # Combustível
    r'posto|shell|ipiranga|petrobras|br\s?distribuidora': {'nome': 'Posto de Gasolina', 'emoji': '⛽', 'cor': '#FF0000'},
    
    # Outros
    r'google\s?(play|one|storage)': {'nome': 'Google', 'emoji': '🔍', 'cor': '#4285F4'},
    r'microsoft|office\s?365': {'nome': 'Microsoft', 'emoji': '💼', 'cor': '#00A4EF'},
    r'adobe': {'nome': 'Adobe', 'emoji': '🎨', 'cor': '#FF0000'},
}


def criar_logo_svg(filename, emoji, cor_bg='#FFFFFF', nome=''):
    """Cria SVG com emoji e cor de fundo"""
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="48" fill="{cor_bg}" stroke="#E0E0E0" stroke-width="2"/>
  <text x="50" y="50" font-size="40" text-anchor="middle" dominant-baseline="central">{emoji}</text>
</svg>'''
    
    logos_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
    filepath = os.path.join(logos_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return filepath


def analisar_estabelecimentos():
    """Analisa Journal Entries e identifica estabelecimentos mais frequentes"""
    
    session = get_db_session()
    
    try:
        # Busca todos os estabelecimentos únicos
        entries = session.query(JournalEntry).filter(
            JournalEntry.Estabelecimento.isnot(None),
            JournalEntry.Estabelecimento != ''
        ).all()
        
        # Conta frequências
        estabelecimentos = Counter([e.Estabelecimento.upper().strip() for e in entries])
        
        print(f"📊 Analisando {len(entries)} transações...")
        print(f"📍 Encontrados {len(estabelecimentos)} estabelecimentos únicos\n")
        
        # Identifica matches com logos conhecidos
        matches = []
        logos_criados = 0
        logos_atualizados = 0
        
        for estabelecimento, count in estabelecimentos.most_common(100):
            for pattern, config in LOGOS_CONHECIDOS.items():
                if re.search(pattern, estabelecimento, re.IGNORECASE):
                    nome_arquivo = f"{config['nome'].lower().replace(' ', '_').replace(chr(39), '')}.svg"
                    
                    # Verifica se já existe no banco
                    logo_existente = session.query(EstabelecimentoLogo).filter(
                        EstabelecimentoLogo.nome_exibicao == config['nome']
                    ).first()
                    
                    if logo_existente:
                        print(f"⏭️  Já existe: {config['nome']} (usado {count}x)")
                        logos_atualizados += 1
                    else:
                        # Cria SVG
                        criar_logo_svg(nome_arquivo, config['emoji'], config['cor'], config['nome'])
                        
                        # Cria registro no banco
                        novo_logo = EstabelecimentoLogo(
                            nome_busca=pattern.replace(r'\s?', ' ').replace('\\', '').strip(),
                            nome_exibicao=config['nome'],
                            arquivo_logo=nome_arquivo,
                            ativo=True
                        )
                        session.add(novo_logo)
                        
                        matches.append({
                            'estabelecimento': estabelecimento,
                            'nome': config['nome'],
                            'count': count,
                            'pattern': pattern
                        })
                        
                        print(f"✅ {config['nome']} ({config['emoji']}) - usado {count}x em '{estabelecimento[:40]}'")
                        logos_criados += 1
                    
                    break  # Encontrou match, pula para próximo estabelecimento
        
        session.commit()
        
        print(f"\n🎉 Concluído!")
        print(f"   Logos criados: {logos_criados}")
        print(f"   Logos já existentes: {logos_atualizados}")
        
        # Mostra estabelecimentos sem logo (top 20)
        print(f"\n📋 Top 20 estabelecimentos SEM logo ainda:")
        sem_logo = []
        for estabelecimento, count in estabelecimentos.most_common(50):
            tem_logo = False
            for pattern in LOGOS_CONHECIDOS.keys():
                if re.search(pattern, estabelecimento, re.IGNORECASE):
                    tem_logo = True
                    break
            
            if not tem_logo:
                sem_logo.append((estabelecimento, count))
        
        for i, (est, count) in enumerate(sem_logo[:20], 1):
            print(f"   {i}. {est[:50]} ({count}x)")
        
        print(f"\n💡 Dica: Adicione logos manualmente em /admin/logos para esses estabelecimentos!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    analisar_estabelecimentos()
