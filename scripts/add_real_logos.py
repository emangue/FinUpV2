#!/usr/bin/env python3
"""
Script para adicionar logos reais de empresas
Coloque as imagens PNG/JPG na pasta static/logos/ e execute este script
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import EstabelecimentoLogo, get_db_session, init_db

init_db()

# Mapeamento de arquivos de logo para nomes de busca
LOGOS_REAIS = {
    # Transporte
    'uber.png': {'busca': 'uber', 'exibicao': 'Uber'},
    'uber_logo.png': {'busca': 'uber', 'exibicao': 'Uber'},
    '99.png': {'busca': '99', 'exibicao': '99'},
    '99pop.png': {'busca': '99', 'exibicao': '99'},
    
    # Food Delivery
    'ifood.png': {'busca': 'ifood', 'exibicao': 'iFood'},
    'ifood_logo.png': {'busca': 'ifood', 'exibicao': 'iFood'},
    'rappi.png': {'busca': 'rappi', 'exibicao': 'Rappi'},
    'ubereats.png': {'busca': 'uber eats', 'exibicao': 'Uber Eats'},
    
    # Restaurantes
    'zdeli.png': {'busca': 'z deli', 'exibicao': 'Z Deli'},
    'zdeli_logo.png': {'busca': 'z deli', 'exibicao': 'Z Deli'},
    'outback.png': {'busca': 'outback', 'exibicao': 'Outback'},
    'mcdonalds.png': {'busca': 'mcdonalds', 'exibicao': "McDonald's"},
    'burgerking.png': {'busca': 'burger king', 'exibicao': 'Burger King'},
    
    # Streaming
    'netflix.png': {'busca': 'netflix', 'exibicao': 'Netflix'},
    'spotify.png': {'busca': 'spotify', 'exibicao': 'Spotify'},
    'youtube.png': {'busca': 'youtube', 'exibicao': 'YouTube Premium'},
    'prime.png': {'busca': 'amazon prime', 'exibicao': 'Amazon Prime'},
    'disney.png': {'busca': 'disney', 'exibicao': 'Disney+'},
    'disneyplus.png': {'busca': 'disney', 'exibicao': 'Disney+'},
    
    # Bancos
    'nubank.png': {'busca': 'nubank', 'exibicao': 'Nubank'},
    'inter.png': {'busca': 'inter', 'exibicao': 'Banco Inter'},
    'itau.png': {'busca': 'itau', 'exibicao': 'Itaú'},
    'bradesco.png': {'busca': 'bradesco', 'exibicao': 'Bradesco'},
    
    # E-commerce
    'amazon.png': {'busca': 'amazon', 'exibicao': 'Amazon'},
    'mercadolivre.png': {'busca': 'mercado livre', 'exibicao': 'Mercado Livre'},
    'magalu.png': {'busca': 'magazine luiza', 'exibicao': 'Magazine Luiza'},
    'shopee.png': {'busca': 'shopee', 'exibicao': 'Shopee'},
    
    # Supermercados
    'carrefour.png': {'busca': 'carrefour', 'exibicao': 'Carrefour'},
    'paodeacucar.png': {'busca': 'pao de acucar', 'exibicao': 'Pão de Açúcar'},
}


def adicionar_logos_reais():
    """Adiciona logos reais ao banco de dados"""
    
    session = get_db_session()
    logos_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'logos')
    
    try:
        print("🎨 Adicionando logos reais...\n")
        
        # Lista arquivos na pasta logos
        arquivos_existentes = [f for f in os.listdir(logos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        adicionados = 0
        atualizados = 0
        
        for arquivo in arquivos_existentes:
            if arquivo in LOGOS_REAIS:
                config = LOGOS_REAIS[arquivo]
                
                # Verifica se já existe
                logo_existente = session.query(EstabelecimentoLogo).filter(
                    EstabelecimentoLogo.nome_busca.ilike(config['busca'])
                ).first()
                
                if logo_existente:
                    # Atualiza para usar o logo real
                    logo_existente.arquivo_logo = arquivo
                    logo_existente.nome_exibicao = config['exibicao']
                    print(f"✏️  Atualizado: {config['exibicao']} → {arquivo}")
                    atualizados += 1
                else:
                    # Cria novo
                    novo_logo = EstabelecimentoLogo(
                        nome_busca=config['busca'],
                        nome_exibicao=config['exibicao'],
                        arquivo_logo=arquivo,
                        ativo=True
                    )
                    session.add(novo_logo)
                    print(f"✅ Adicionado: {config['exibicao']} → {arquivo}")
                    adicionados += 1
        
        session.commit()
        
        print(f"\n🎉 Concluído!")
        print(f"   Adicionados: {adicionados}")
        print(f"   Atualizados: {atualizados}")
        print(f"\n💡 Dica: Coloque mais imagens PNG/JPG na pasta static/logos/")
        print(f"   e execute este script novamente!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    adicionar_logos_reais()
