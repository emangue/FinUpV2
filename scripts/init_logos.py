#!/usr/bin/env python3
"""
Script para popular logos iniciais de estabelecimentos comuns
"""
import sys
import os

# Adiciona o diretório pai ao path para importar models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import EstabelecimentoLogo, get_db_session, init_db

# Inicializa o banco de dados
init_db()

# Lista de logos a serem criados
LOGOS_INICIAIS = [
    # Transporte
    {
        'nome_busca': 'uber',
        'nome_exibicao': 'Uber',
        'arquivo_logo': 'uber.svg',
        'emoji': '🚗'
    },
    {
        'nome_busca': '99',
        'nome_exibicao': '99',
        'arquivo_logo': '99.svg',
        'emoji': '🚕'
    },
    
    # Food Delivery
    {
        'nome_busca': 'ifood',
        'nome_exibicao': 'iFood',
        'arquivo_logo': 'ifood.svg',
        'emoji': '🍔'
    },
    {
        'nome_busca': 'rappi',
        'nome_exibicao': 'Rappi',
        'arquivo_logo': 'rappi.svg',
        'emoji': '🛵'
    },
    {
        'nome_busca': 'uber eats',
        'nome_exibicao': 'Uber Eats',
        'arquivo_logo': 'ubereats.svg',
        'emoji': '🍕'
    },
    
    # Restaurantes
    {
        'nome_busca': 'z deli',
        'nome_exibicao': 'Z Deli',
        'arquivo_logo': 'zdeli.svg',
        'emoji': '🥪'
    },
    {
        'nome_busca': 'outback',
        'nome_exibicao': 'Outback',
        'arquivo_logo': 'outback.svg',
        'emoji': '🥩'
    },
    {
        'nome_busca': 'mcdonalds',
        'nome_exibicao': "McDonald's",
        'arquivo_logo': 'mcdonalds.svg',
        'emoji': '🍟'
    },
    {
        'nome_busca': 'burger king',
        'nome_exibicao': 'Burger King',
        'arquivo_logo': 'burgerking.svg',
        'emoji': '👑'
    },
    
    # Streaming
    {
        'nome_busca': 'netflix',
        'nome_exibicao': 'Netflix',
        'arquivo_logo': 'netflix.svg',
        'emoji': '🎬'
    },
    {
        'nome_busca': 'spotify',
        'nome_exibicao': 'Spotify',
        'arquivo_logo': 'spotify.svg',
        'emoji': '🎵'
    },
    {
        'nome_busca': 'youtube',
        'nome_exibicao': 'YouTube Premium',
        'arquivo_logo': 'youtube.svg',
        'emoji': '▶️'
    },
    {
        'nome_busca': 'amazon prime',
        'nome_exibicao': 'Amazon Prime',
        'arquivo_logo': 'prime.svg',
        'emoji': '📺'
    },
    {
        'nome_busca': 'disney',
        'nome_exibicao': 'Disney+',
        'arquivo_logo': 'disney.svg',
        'emoji': '🏰'
    },
    
    # Bancos
    {
        'nome_busca': 'nubank',
        'nome_exibicao': 'Nubank',
        'arquivo_logo': 'nubank.svg',
        'emoji': '💜'
    },
    {
        'nome_busca': 'inter',
        'nome_exibicao': 'Banco Inter',
        'arquivo_logo': 'inter.svg',
        'emoji': '🧡'
    },
    {
        'nome_busca': 'itau',
        'nome_exibicao': 'Itaú',
        'arquivo_logo': 'itau.svg',
        'emoji': '🔶'
    },
    {
        'nome_busca': 'bradesco',
        'nome_exibicao': 'Bradesco',
        'arquivo_logo': 'bradesco.svg',
        'emoji': '🔴'
    },
    
    # E-commerce
    {
        'nome_busca': 'amazon',
        'nome_exibicao': 'Amazon',
        'arquivo_logo': 'amazon.svg',
        'emoji': '📦'
    },
    {
        'nome_busca': 'mercado livre',
        'nome_exibicao': 'Mercado Livre',
        'arquivo_logo': 'mercadolivre.svg',
        'emoji': '🛒'
    },
    {
        'nome_busca': 'magazine luiza',
        'nome_exibicao': 'Magazine Luiza',
        'arquivo_logo': 'magalu.svg',
        'emoji': '🏪'
    },
    {
        'nome_busca': 'shopee',
        'nome_exibicao': 'Shopee',
        'arquivo_logo': 'shopee.svg',
        'emoji': '🛍️'
    },
    
    # Utilidades
    {
        'nome_busca': 'carrefour',
        'nome_exibicao': 'Carrefour',
        'arquivo_logo': 'carrefour.svg',
        'emoji': '🛒'
    },
    {
        'nome_busca': 'pao de acucar',
        'nome_exibicao': 'Pão de Açúcar',
        'arquivo_logo': 'paodeacucar.svg',
        'emoji': '🍞'
    },
    {
        'nome_busca': 'farmacia',
        'nome_exibicao': 'Farmácia',
        'arquivo_logo': 'farmacia.svg',
        'emoji': '💊'
    },
    {
        'nome_busca': 'posto',
        'nome_exibicao': 'Posto de Gasolina',
        'arquivo_logo': 'posto.svg',
        'emoji': '⛽'
    },
]


def criar_logo_svg(filename, emoji, cor_bg='#FFFFFF', cor_texto='#000000'):
    """Cria um SVG simples com emoji"""
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="48" fill="{cor_bg}" stroke="#E0E0E0" stroke-width="2"/>
  <text x="50" y="50" font-size="40" text-anchor="middle" dominant-baseline="central">{emoji}</text>
</svg>'''
    
    logos_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
    os.makedirs(logos_dir, exist_ok=True)
    
    filepath = os.path.join(logos_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✓ Logo criado: {filename}")


def popular_logos():
    """Popula o banco com logos iniciais e cria os arquivos SVG"""
    
    session = get_db_session()
    
    try:
        print("🎨 Populando logos iniciais...\n")
        
        for logo_data in LOGOS_INICIAIS:
            # Verifica se já existe
            existe = session.query(EstabelecimentoLogo).filter(
                EstabelecimentoLogo.nome_busca.ilike(logo_data['nome_busca'])
            ).first()
            
            if existe:
                print(f"⏭️  Já existe: {logo_data['nome_exibicao']}")
                continue
            
            # Cria arquivo SVG
            criar_logo_svg(
                filename=logo_data['arquivo_logo'],
                emoji=logo_data['emoji']
            )
            
            # Cria registro no banco
            novo_logo = EstabelecimentoLogo(
                nome_busca=logo_data['nome_busca'],
                nome_exibicao=logo_data['nome_exibicao'],
                arquivo_logo=logo_data['arquivo_logo'],
                ativo=True
            )
            
            session.add(novo_logo)
            print(f"✅ Adicionado: {logo_data['nome_exibicao']} ({logo_data['emoji']})")
        
        session.commit()
        
        total = session.query(EstabelecimentoLogo).count()
        print(f"\n🎉 Concluído! Total de logos: {total}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    popular_logos()
