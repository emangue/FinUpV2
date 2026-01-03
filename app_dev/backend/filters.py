"""
Template Filters compartilhados entre blueprints
"""
from app.models import GrupoConfig, EstabelecimentoLogo, get_db_session


# Helper functions (podem ser importadas diretamente)
def get_group_color_helper(grupo):
    """Função helper para obter cor do grupo (pode ser importada)"""
    if not grupo:
        return '#6c757d'
    
    db = get_db_session()
    try:
        config = db.query(GrupoConfig).filter_by(nome=grupo, ativo=True).first()
        if config:
            return config.cor
    finally:
        db.close()
    
    # Fallback para cores padrão
    colors = {
        'Alimentação': '#FF6384',
        'Transporte': '#36A2EB',
        'Moradia': '#FFCE56',
        'Saúde': '#4BC0C0',
        'Educação': '#9966FF',
        'Lazer': '#FF9F40',
        'Assinaturas': '#E7E9ED',
        'Vestuário': '#C9CBCF',
        'Investimentos': '#4BC0C0',
        'Impostos': '#FF6384',
        'Seguros': '#36A2EB',
        'Doações': '#9966FF'
    }
    return colors.get(grupo, '#6c757d')


def register_filters(app):
    """Registra todos os template filters globalmente"""
    
    @app.template_filter('get_group_icon')
    def get_group_icon(grupo):
        """Retorna ícone Font Awesome para cada grupo (do banco ou padrão)"""
        if not grupo:
            return 'fa-tag'
        
        db = get_db_session()
        try:
            config = db.query(GrupoConfig).filter_by(nome=grupo, ativo=True).first()
            if config:
                return config.icone
        finally:
            db.close()
        
        # Fallback para ícones padrão
        icons = {
            'Alimentação': 'fa-utensils',
            'Transporte': 'fa-car',
            'Moradia': 'fa-home',
            'Saúde': 'fa-heartbeat',
            'Educação': 'fa-graduation-cap',
            'Lazer': 'fa-gamepad',
            'Assinaturas': 'fa-file-invoice',
            'Vestuário': 'fa-tshirt',
            'Investimentos': 'fa-chart-line',
            'Impostos': 'fa-landmark',
            'Seguros': 'fa-shield-alt',
            'Doações': 'fa-hand-holding-heart'
        }
        return icons.get(grupo, 'fa-tag')

    @app.template_filter('get_group_color')
    def get_group_color(grupo):
        """Retorna cor hexadecimal para cada grupo (do banco ou padrão)"""
        return get_group_color_helper(grupo)

    @app.template_filter('format_currency')
    def format_currency(value):
        """Formata valor para moeda brasileira (R$ 1.234,56)"""
        if value is None:
            return "0,00"
        try:
            value = float(value)
            return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return "0,00"

    @app.template_filter('get_estabelecimento_logo')
    def get_estabelecimento_logo(estabelecimento):
        """Retorna caminho do logo se existir, senão None"""
        if not estabelecimento:
            return None
        
        # Normaliza o nome para busca
        estabelecimento_upper = estabelecimento.upper().strip()
        
        db = get_db_session()
        try:
            # Busca todos os logos ativos
            logos = db.query(EstabelecimentoLogo).filter(
                EstabelecimentoLogo.ativo == True
            ).all()
            
            # Procura por match em qualquer palavra de busca
            for logo in logos:
                # Separa palavras de busca por vírgula
                palavras_busca = [p.strip().upper() for p in logo.nome_busca.split(',')]
                
                # Verifica se alguma palavra está no estabelecimento
                for palavra in palavras_busca:
                    if palavra in estabelecimento_upper:
                        return f'/static/logos/{logo.arquivo_logo}'
            
        finally:
            db.close()
        
        return None
