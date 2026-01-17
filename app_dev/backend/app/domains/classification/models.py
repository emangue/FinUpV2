"""
Modelo para Regras Genéricas Configuráveis
Move as regras hardcoded para base de dados
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class GenericClassificationRules(Base):
    """
    Tabela de regras genéricas de classificação
    Substitui as regras hardcoded do GenericRulesClassifier
    """
    __tablename__ = "generic_classification_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação da regra
    nome_regra = Column(String(100), nullable=False, comment="Nome descritivo da regra")
    descricao = Column(Text, comment="Descrição do que a regra classifica")
    
    # Palavras-chave para matching (JSON array ou string separada por vírgula)
    keywords = Column(Text, nullable=False, comment="Palavras-chave separadas por vírgula")
    
    # Classificação resultante
    grupo = Column(String(100), nullable=False)
    subgrupo = Column(String(100), nullable=False) 
    tipo_gasto = Column(String(50), nullable=False, comment="Fixo, Ajustável, etc")
    
    # Configurações
    prioridade = Column(Integer, default=5, comment="1=menor, 10=maior prioridade")
    ativo = Column(Boolean, default=True, comment="Regra ativa/inativa")
    case_sensitive = Column(Boolean, default=False, comment="Match case sensitive")
    match_completo = Column(Boolean, default=False, comment="Deve conter palavra completa")
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), comment="Usuário que criou a regra")
    
    # Estatísticas de uso
    total_matches = Column(Integer, default=0, comment="Quantas vezes foi aplicada")
    last_match_at = Column(DateTime(timezone=True), comment="Último uso da regra")
    
    def __repr__(self):
        return f"<GenericRule({self.nome_regra}: {self.grupo}>{self.subgrupo})>"

    def to_dict(self):
        """Converte para dict para facilitar uso"""
        return {
            'id': self.id,
            'nome_regra': self.nome_regra,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'grupo': self.grupo,
            'subgrupo': self.subgrupo,
            'tipo_gasto': self.tipo_gasto,
            'prioridade': self.prioridade,
            'ativo': self.ativo,
            'case_sensitive': self.case_sensitive,
            'match_completo': self.match_completo,
        }

    def get_keywords_list(self) -> list[str]:
        """Retorna lista de keywords processadas"""
        if not self.keywords:
            return []
        
        # Split por vírgula e limpa espaços
        keywords = [kw.strip() for kw in self.keywords.split(',') if kw.strip()]
        
        # Converte para uppercase se não for case sensitive
        if not self.case_sensitive:
            keywords = [kw.upper() for kw in keywords]
        
        return keywords

    def matches(self, text: str) -> bool:
        """
        Verifica se o texto bate com esta regra
        
        Args:
            text: Texto a ser analisado (nome do estabelecimento)
            
        Returns:
            True se bate com a regra
        """
        if not self.ativo or not self.keywords:
            return False
        
        # Preparar texto
        search_text = text if self.case_sensitive else text.upper()
        
        # Verificar cada keyword
        for keyword in self.get_keywords_list():
            if self.match_completo:
                # Match palavra completa (bordas)
                import re
                pattern = r'\b' + re.escape(keyword) + r'\b'
                flags = 0 if self.case_sensitive else re.IGNORECASE
                if re.search(pattern, text, flags):
                    return True
            else:
                # Match simples (contém)
                if keyword in search_text:
                    return True
        
        return False

    def increment_usage(self):
        """Incrementa contador de uso da regra"""
        self.total_matches = (self.total_matches or 0) + 1
        self.last_match_at = func.now()