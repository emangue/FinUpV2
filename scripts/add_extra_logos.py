#!/usr/bin/env python3
"""
Cria logos adicionais baseados na análise das transações
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import EstabelecimentoLogo, get_db_session, init_db

init_db()

# Logos adicionais identificados nas transações
LOGOS_ADICIONAIS = [
    {
        'busca': 'apple.com',
        'exibicao': 'Apple',
        'arquivo': 'apple.svg',
        'emoji': '🍎',
        'cor': '#000000'
    },
    {
        'busca': 'vivo',
        'exibicao': 'Vivo',
        'arquivo': 'vivo.svg',
        'emoji': '📱',
        'cor': '#660099'
    },
    {
        'busca': 'conectcar',
        'exibicao': 'ConectCar',
        'arquivo': 'conectcar.svg',
        'emoji': '🚗',
        'cor': '#0066CC'
    },
    {
        'busca': 'sao jorge',
        'exibicao': 'São Jorge Atacadista',
        'arquivo': 'saogorge.svg',
        'emoji': '🛒',
        'cor': '#FF0000'
    },
]


def criar_logo_svg(filename, emoji, cor_bg='#FFFFFF'):
    """Cria SVG com emoji"""
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="48" fill="{cor_bg}" stroke="#E0E0E0" stroke-width="2"/>
  <text x="50" y="50" font-size="40" text-anchor="middle" dominant-baseline="central">{emoji}</text>
</svg>'''
    
    logos_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
    filepath = os.path.join(logos_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)


def adicionar_logos_extras():
    """Adiciona logos extras identificados"""
    
    session = get_db_session()
    
    try:
        print("🎨 Adicionando logos extras...\n")
        
        adicionados = 0
        
        for logo_data in LOGOS_ADICIONAIS:
            # Verifica se já existe
            existe = session.query(EstabelecimentoLogo).filter(
                EstabelecimentoLogo.nome_busca.ilike(logo_data['busca'])
            ).first()
            
            if existe:
                print(f"⏭️  Já existe: {logo_data['exibicao']}")
                continue
            
            # Cria SVG
            criar_logo_svg(logo_data['arquivo'], logo_data['emoji'], logo_data['cor'])
            
            # Cria registro no banco
            novo_logo = EstabelecimentoLogo(
                nome_busca=logo_data['busca'],
                nome_exibicao=logo_data['exibicao'],
                arquivo_logo=logo_data['arquivo'],
                ativo=True
            )
            
            session.add(novo_logo)
            print(f"✅ Adicionado: {logo_data['exibicao']} ({logo_data['emoji']})")
            adicionados += 1
        
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
    adicionar_logos_extras()
