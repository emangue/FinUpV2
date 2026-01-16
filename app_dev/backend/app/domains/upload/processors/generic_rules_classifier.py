"""
Generic Rules Classifier
Classificador de regras genéricas hardcoded (baseado no n8n)
Independente de banco de dados, usa apenas regras em memória
"""

import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GenericRule:
    """Regra genérica de classificação"""
    keywords: List[str]
    grupo: str
    subgrupo: str
    tipo_gasto: str
    prioridade: int


class GenericRulesClassifier:
    """
    Classificador baseado em regras genéricas hardcoded
    Inspirado nas regras do n8n (Code in JavaScript)
    """
    
    # Regras ordenadas por prioridade (maior = mais específico)
    RULES = [
        # === SERVIÇOS ESPECÍFICOS (Prioridade MÁXIMA = 10) ===
        GenericRule(
            keywords=['CABELEIREIRO', 'SALAO', 'BARBEARIA', 'BARBEIRO'],
            grupo='Serviços',
            subgrupo='Cabeleireiro',
            tipo_gasto='Ajustável',
            prioridade=10
        ),
        GenericRule(
            keywords=['DIARISTA', 'FAXINA', 'LIMPEZA CASA'],
            grupo='Limpeza',
            subgrupo='Casa',
            tipo_gasto='Fixo',
            prioridade=10
        ),
        
        # === ROUPAS (Prioridade ALTA = 10) ===
        GenericRule(
            keywords=['NETSHOES'],
            grupo='Roupas',
            subgrupo='Roupas',
            tipo_gasto='Ajustável',
            prioridade=10
        ),
        
        # === ENERGIA E UTILIDADES (Prioridade ALTA = 9) ===
        GenericRule(
            keywords=['ELETROPAULO', 'ENEL', 'CPFL', 'CEMIG', 'COELBA', 'CELESC', 'ELEKTRO', 'LUZ', 'ENERGIA ELETRICA'],
            grupo='Casa',
            subgrupo='Energia',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        GenericRule(
            keywords=['SABESP', 'SANEPAR', 'CAESB', 'CEDAE', 'COPASA', 'AGUA', 'SANEAMENTO'],
            grupo='Casa',
            subgrupo='Água',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        GenericRule(
            keywords=['CONDOMINIO'],
            grupo='Casa',
            subgrupo='Condomínio',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        GenericRule(
            keywords=['CLARO', 'VIVO', 'TIM', 'OI', 'TELEFONE', 'CELULAR', 'TELEFONIA'],
            grupo='Casa',
            subgrupo='Celular',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        GenericRule(
            keywords=['NET', 'CLARO NET', 'VIVO FIBRA', 'OI FIBRA', 'INTERNET', 'BANDA LARGA', 'FIBRA OTICA'],
            grupo='Casa',
            subgrupo='Internet',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        GenericRule(
            keywords=['GAS', 'COMGAS', 'ULTRAGAZ', 'LIQUIGAS', 'SUPERGASBRASS'],
            grupo='Casa',
            subgrupo='Gás',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        
        # === ALIMENTAÇÃO - SAÍDAS (Prioridade ALTA = 9) ===
        GenericRule(
            keywords=['PIZZ', 'PIZZA', 'PIZZARIA', 'RESTAUR', 'ADEGA', 'BAR', 'PUB', 'LANCHE',
                     'HAMBURGER', 'BURGUER', 'CHURRASCARIA', 'BOTECO', 'CAFETERIA', 'FESTA',
                     'DOCERIA', 'CONFEITARIA', 'PADARIA'],
            grupo='Alimentação',
            subgrupo='Saídas',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        
        # === CARRO - IPVA/LICENCIAMENTO (Prioridade ALTA = 9) ===
        GenericRule(
            keywords=['IPVA', 'LICENCIAMENTO'],
            grupo='Carro',
            subgrupo='IPVA + Licenciamento',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        
        # === VIAGENS (Prioridade ALTA = 9) ===
        GenericRule(
            keywords=['LATAM', 'GOL', 'AZUL', 'AVIANCA', 'CIA AEREA', 'PASSAGEM AEREA', 'VOO', 'AEROPORTO'],
            grupo='Viagens',
            subgrupo='Outros',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        GenericRule(
            keywords=['HOTEL', 'POUSADA', 'AIRBNB', 'BOOKING', 'HOSPEDAGEM', 'RESORT', 'HOSTEL', 'ALBERGUE'],
            grupo='Viagens',
            subgrupo='Outros',
            tipo_gasto='Ajustável',
            prioridade=9
        ),
        
        # === SAÚDE (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['FARMACIA', 'DROGARIA', 'DROGA', 'DROGASIL', 'PACHECO', 'PANVEL', 'ULTRAFARMA', 'PAGUE MENOS'],
            grupo='Saúde',
            subgrupo='Farmácia',
            tipo_gasto='Fixo',
            prioridade=8
        ),
        GenericRule(
            keywords=['DENTISTA', 'ODONTO', 'ORTODONTIA'],
            grupo='Saúde',
            subgrupo='Dentista',
            tipo_gasto='Fixo',
            prioridade=8
        ),
        GenericRule(
            keywords=['TERAPIA', 'PSICOLOGO', 'PSIQUIATRA', 'TERAPEUTA'],
            grupo='Saúde',
            subgrupo='Terapia',
            tipo_gasto='Fixo',
            prioridade=8
        ),
        
        # === ALIMENTAÇÃO - DELIVERY (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['IFOOD', 'UBER EATS', 'RAPPI', 'DELIVERY', 'ENTREGA'],
            grupo='Alimentação',
            subgrupo='Pedidos para casa',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === ALIMENTAÇÃO - SUPERMERCADO (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['SUPERMERCADO', 'MERCADO', 'EXTRA', 'CARREFOUR', 'PAO DE ACUCAR', 
                     'PAODEACUCAR', 'WALMART', 'ATACADAO', 'ASSAI', 'MAKRO'],
            grupo='Alimentação',
            subgrupo='Supermercado',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === CARRO (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['POSTO', 'GASOLINA', 'ALCOOL', 'ETANOL', 'COMBUSTIVEL', 'SHELL', 
                     'IPIRANGA', 'BR PETROBRAS', 'ALE', 'ABASTECIMENTO'],
            grupo='Carro',
            subgrupo='Abastecimento',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['DRYWASH', 'LAVA RAPIDO', 'LAVAGEM', 'LAVA JATO', 'CAR WASH', 'ESTETICA AUTOMOTIVA'],
            grupo='Carro',
            subgrupo='Limpeza',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['SEM PARAR', 'CONNECTCAR', 'CONNETCAR', 'PEDAGIO'],
            grupo='Carro',
            subgrupo='Sem Parar',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['SEGURO CARRO', 'SEGURO AUTO', 'PORTO SEGURO AUTO'],
            grupo='Carro',
            subgrupo='Seguro',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === TRANSPORTE (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['UBER', 'CABIFY', 'TAXI'],
            grupo='Transporte',
            subgrupo='Uber',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === ASSINATURAS (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['NETFLIX', 'HBO', 'PARAMOUNT', 'GLOBOPLAY', 'STREAMING'],
            grupo='Assinaturas',
            subgrupo='Outros',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['DISNEY PLUS', 'DISNEY+'],
            grupo='Assinaturas',
            subgrupo='Outros',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['SPOTIFY'],
            grupo='Assinaturas',
            subgrupo='Spotify',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['YOUTUBE PREMIUM', 'YOUTUBE'],
            grupo='Assinaturas',
            subgrupo='Youtube',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['AMAZON PRIME', 'PRIME VIDEO'],
            grupo='Assinaturas',
            subgrupo='Amazon Prime',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['ICLOUD', 'APPLE CLOUD'],
            grupo='Assinaturas',
            subgrupo='ICloud',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['PREMIERE'],
            grupo='Assinaturas',
            subgrupo='Premiere',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        GenericRule(
            keywords=['AUDIBLE'],
            grupo='Assinaturas',
            subgrupo='Audible',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === EDUCAÇÃO (Prioridade ALTA = 8) ===
        GenericRule(
            keywords=['ESCOLA', 'FACULDADE', 'UNIVERSIDADE', 'CURSO', 'COLEGIO', 'ENSINO',
                     'MENSALIDADE', 'CERVANTES', 'PREPLY'],
            grupo='Educação',
            subgrupo='Cervantes',
            tipo_gasto='Fixo',
            prioridade=8
        ),
        
        # === VIAGENS - AGÊNCIAS (Prioridade MÉDIA-ALTA = 8) ===
        GenericRule(
            keywords=['DECOLAR', 'MAXMILHAS', 'TURISMO', 'AGENCIA', 'CVC'],
            grupo='Viagens',
            subgrupo='Outros',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === ROUPAS - GENÉRICO (Prioridade MÉDIA-ALTA = 8) ===
        GenericRule(
            keywords=['TECIDO', 'TECIDOS', 'CONFEC', 'MALHARIA', 'MODA', 'VESTUARIO', 
                     'ROUPA', 'CALCADO', 'SAPATO', 'BOUTIQUE'],
            grupo='Roupas',
            subgrupo='Roupas',
            tipo_gasto='Ajustável',
            prioridade=8
        ),
        
        # === TRANSPORTE PÚBLICO (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['BILHETE UNICO', 'METRO', 'ONIBUS', 'CPTM', 'TRANSPORTE PUBLICO'],
            grupo='Transporte',
            subgrupo='Bilhete Único',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        
        # === CARRO - ESTACIONAMENTO (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['ESTACIONAMENTO', 'PARKING', 'VAGA', 'ZONA AZUL'],
            grupo='Carro',
            subgrupo='Estacionamento',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        
        # === SAÚDE - ESPORTES (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['ACADEMIA', 'CROSSFIT', 'FUNCIONAL', 'GYMPASS'],
            grupo='Saúde',
            subgrupo='Crossfit',
            tipo_gasto='Fixo',
            prioridade=7
        ),
        GenericRule(
            keywords=['PADEL'],
            grupo='Saúde',
            subgrupo='Padel',
            tipo_gasto='Fixo',
            prioridade=7
        ),
        
        # === TECNOLOGIA (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['APPLE', 'MICROSOFT', 'GOOGLE PLAY', 'APP STORE', 'SOFTWARE'],
            grupo='Tecnologia',
            subgrupo='Outros',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        
        # === E-COMMERCE (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['MERCADO LIVRE', 'MERCADOLIVRE', 'MELI', 'ML'],
            grupo='MeLi + Amazon',
            subgrupo='MeLi + Amazon',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        GenericRule(
            keywords=['AMAZON', 'AMZN'],
            grupo='MeLi + Amazon',
            subgrupo='MeLi + Amazon',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        
        # === ALIMENTAÇÃO - CAFÉ/ALMOÇO (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['CAFE DA MANHA', 'PADARIA', 'CONFEITARIA'],
            grupo='Alimentação',
            subgrupo='Café da Manhã',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        GenericRule(
            keywords=['ALMOCO', 'REFEICAO', 'MARMITA'],
            grupo='Alimentação',
            subgrupo='Almoço',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        
        # === SERVIÇOS (Prioridade MÉDIA = 7) ===
        GenericRule(
            keywords=['LAVANDERIA', 'LAVAR ROUPA', 'LAVAGEM ROUPA'],
            grupo='Serviços',
            subgrupo='Lavanderia',
            tipo_gasto='Ajustável',
            prioridade=7
        ),
        
        # === ENTRETENIMENTO (Prioridade MÉDIA-BAIXA = 6) ===
        GenericRule(
            keywords=['CINEMA', 'CINEMARK', 'INGRESSO', 'FILME'],
            grupo='Entretenimento',
            subgrupo='Cinema',
            tipo_gasto='Ajustável',
            prioridade=6
        ),
        GenericRule(
            keywords=['SHOW', 'CONCERTO', 'APRESENTACAO'],
            grupo='Entretenimento',
            subgrupo='Shows',
            tipo_gasto='Ajustável',
            prioridade=6
        ),
        GenericRule(
            keywords=['CORRIDA', 'MARATONA', 'PROVA'],
            grupo='Entretenimento',
            subgrupo='Corrida',
            tipo_gasto='Ajustável',
            prioridade=6
        ),
        
        # === TRANSPORTE - 99 (Prioridade BAIXA = 5) ===
        GenericRule(
            keywords=['99'],
            grupo='Transporte',
            subgrupo='Uber',
            tipo_gasto='Ajustável',
            prioridade=5
        ),
        
        # === INVESTIMENTOS (Prioridade ALTA = 9) ===
        GenericRule(
            keywords=['TESOURO DIRETO', 'TESOURO SELIC', 'TESOURO IPCA', 'TESOURO PREFIXADO'],
            grupo='Investimentos',
            subgrupo='Tesouro Direto',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        GenericRule(
            keywords=['CDB', 'LCI', 'LCA', 'RENDA FIXA', 'VENCIMENTO DE LCA', 'VENCIMENTO DE LCI'],
            grupo='Investimentos',
            subgrupo='Renda Fixa',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        GenericRule(
            keywords=['FUNDO DE INVESTIMENTO', 'APLICACAO EM FUNDO', 'APLICACAO AUTOMATICA', 'REMUNERACAO APLICACAO'],
            grupo='Investimentos',
            subgrupo='Fundos',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        GenericRule(
            keywords=['BITCOIN', 'BTC', 'ETHEREUM', 'ETH', 'CRIPTO', 'MERCADO COIN', 'MCN'],
            grupo='Investimentos',
            subgrupo='Criptomoedas',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        GenericRule(
            keywords=['ACAO', 'ACOES', 'B3', 'BOVESPA', 'BOLSA DE VALORES', 'LIQUIDO DE VENCIMENTOS-RV'],
            grupo='Investimentos',
            subgrupo='Ações',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        GenericRule(
            keywords=['FII', 'FUNDO IMOBILIARIO', 'QUATA EMP'],
            grupo='Investimentos',
            subgrupo='Fundos Imobiliários',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        GenericRule(
            keywords=['CONTA INVESTIMENTO', 'TRANSFERENCIA ENVIADA PARA CONTA INVESTIMENTO'],
            grupo='Investimentos',
            subgrupo='Aplicações',
            tipo_gasto='Investimentos',
            prioridade=9
        ),
        
        # === PIX/TRANSFERÊNCIAS (Prioridade BAIXA = 3) ===
        GenericRule(
            keywords=['PIX', 'TED', 'DOC', 'TRANSFERENCIA'],
            grupo='Transferência Entre Contas',
            subgrupo='Nubank',
            tipo_gasto='Transferência',
            prioridade=3
        ),
    ]
    
    def __init__(self):
        """Inicializa o classificador genérico"""
        # Ordenar regras por prioridade (maior primeiro)
        self.rules = sorted(self.RULES, key=lambda r: r.prioridade, reverse=True)
        logger.debug(f"GenericRulesClassifier inicializado com {len(self.rules)} regras")
    
    def _normalizar(self, texto: str) -> str:
        """Normaliza texto para matching"""
        import unicodedata
        import re
        
        if not texto:
            return ""
        
        texto = str(texto).upper()
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
        texto = re.sub(r'[^A-Z0-9\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()
    
    def classify(self, estabelecimento: str) -> Optional[Dict[str, str]]:
        """
        Classifica estabelecimento usando regras genéricas
        
        Args:
            estabelecimento: Nome do estabelecimento
            
        Returns:
            Dict com grupo, subgrupo, tipo_gasto ou None
        """
        estab_norm = self._normalizar(estabelecimento)
        
        # Array para guardar matches com suas prioridades
        matches = []
        
        for regra in self.rules:
            for palavra in regra.keywords:
                palavra_norm = self._normalizar(palavra)
                
                matched = False
                
                # Para palavras curtas (<= 4 chars), usar matching exato com boundaries
                if len(palavra_norm) <= 4:
                    import re
                    regex = re.compile(r'\b' + re.escape(palavra_norm) + r'\b')
                    matched = regex.search(estab_norm) is not None
                else:
                    # Para palavras longas, matching normal
                    matched = palavra_norm in estab_norm
                
                if matched:
                    matches.append({
                        'grupo': regra.grupo,
                        'subgrupo': regra.subgrupo,
                        'tipo_gasto': regra.tipo_gasto,
                        'prioridade': regra.prioridade,
                        'palavra_encontrada': palavra
                    })
                    break  # Para de verificar outras palavras desta regra
        
        # Se encontrou matches, retorna o de maior prioridade
        if matches:
            # Já está ordenado por prioridade (regras foram ordenadas no __init__)
            return matches[0]
        
        return None
    
    def get_marcacao_ia(self, estabelecimento: str) -> Optional[str]:
        """
        Retorna string formatada para MarcacaoIA
        
        Args:
            estabelecimento: Nome do estabelecimento
            
        Returns:
            String "GRUPO > SUBGRUPO" ou None
        """
        resultado = self.classify(estabelecimento)
        if resultado:
            return f"{resultado['grupo']} > {resultado['subgrupo']}"
        return None
