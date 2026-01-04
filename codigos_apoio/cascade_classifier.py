"""
Cascade Classifier - Sistema de Classificação em 6 Níveis
Versão: 1.0.0
Data: 04/01/2026

Sistema inteligente de classificação automática usando cascata de 6 níveis:
0. IdParcela - Copia de parcelas anteriores do mesmo contrato
1. Fatura Cartão - Detecta pagamentos de cartão
2. Ignorar - Lista de exclusão database-driven + matching de titular
3. Base_Padroes - Padrões aprendidos com alta confiança
4. Journal Entries - Match exato em transações históricas
5. Palavras-chave - Regras por palavras + validação em BaseMarcacao
6. Não Encontrado - Fallback quando nenhum nível funciona
"""

import sys
import os
from datetime import datetime

# Importar utilitários
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizer import normalizar, normalizar_estabelecimento, fuzzy_match_titular, get_faixa_valor


class CascadeClassifier:
    """
    Classificador em cascata com 6 níveis de prioridade
    """
    
    def __init__(self, db_session, user_id):
        """
        Inicializa classificador
        
        Args:
            db_session: Sessão do SQLAlchemy para queries
            user_id (int): ID do usuário (para filtrar padrões e exclusões)
        """
        self.db = db_session
        self.user_id = user_id
        self.stats = {
            'total': 0,
            'nivel_0_id_parcela': 0,
            'nivel_1_fatura_cartao': 0,
            'nivel_2_ignorar': 0,
            'nivel_3_base_padroes': 0,
            'nivel_4_journal_entries': 0,
            'nivel_5_palavras_chave': 0,
            'nivel_6_nao_encontrado': 0
        }
    
    def classify(self, transacao):
        """
        Classifica uma transação usando cascata de 6 níveis
        
        Args:
            transacao (dict): Transação processada pelo universal_processor
                             Deve ter: Data, Estabelecimento, ValorPositivo, IdParcela, etc.
        
        Returns:
            dict: Classificação com campos GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral, 
                  origem_classificacao, IgnorarDashboard, ValidarIA, MarcacaoIA
        """
        self.stats['total'] += 1
        
        # Nível 0: IdParcela (se tiver IdParcela, copiar de parcela anterior)
        resultado = self._nivel_0_id_parcela(transacao)
        if resultado:
            self.stats['nivel_0_id_parcela'] += 1
            return resultado
        
        # Nível 1: Fatura Cartão (detectar pagamento de cartão)
        resultado = self._nivel_1_fatura_cartao(transacao)
        if resultado:
            self.stats['nivel_1_fatura_cartao'] += 1
            return resultado
        
        # Nível 2: Ignorar (database-driven + titular matching)
        resultado = self._nivel_2_ignorar(transacao)
        if resultado:
            self.stats['nivel_2_ignorar'] += 1
            return resultado
        
        # Nível 3: Base_Padroes (padrões aprendidos com alta confiança)
        resultado = self._nivel_3_base_padroes(transacao)
        if resultado:
            self.stats['nivel_3_base_padroes'] += 1
            return resultado
        
        # Nível 4: Journal Entries (match exato em histórico)
        resultado = self._nivel_4_journal_entries(transacao)
        if resultado:
            self.stats['nivel_4_journal_entries'] += 1
            return resultado
        
        # Nível 5: Palavras-chave (regras + validação em BaseMarcacao)
        resultado = self._nivel_5_palavras_chave(transacao)
        if resultado:
            self.stats['nivel_5_palavras_chave'] += 1
            return resultado
        
        # Nível 6: Não Encontrado (fallback)
        self.stats['nivel_6_nao_encontrado'] += 1
        return self._nivel_6_nao_encontrado(transacao)
    
    def _nivel_0_id_parcela(self, transacao):
        """
        Nível 0: Copia classificação de parcelas anteriores do mesmo contrato
        
        Busca em base_parcelas pelo IdParcela e copia GRUPO, SUBGRUPO, TipoGasto
        """
        id_parcela = transacao.get('IdParcela')
        if not id_parcela:
            return None
        
        try:
            # Importar models (assume que estão disponíveis)
            try:
                from app.models import BaseParcelas
            except ImportError:
                from app_dev.backend.models import BaseParcelas
            
            # Buscar contrato de parcelamento
            contrato = self.db.query(BaseParcelas).filter(
                BaseParcelas.id_parcela == id_parcela,
                BaseParcelas.user_id == self.user_id
            ).first()
            
            if contrato:
                return {
                    'GRUPO': contrato.grupo or '',
                    'SUBGRUPO': contrato.subgrupo or '',
                    'TipoGasto': contrato.tipo_gasto or '',
                    'CategoriaGeral': contrato.categoria_geral or '',
                    'origem_classificacao': 'IdParcela',
                    'IgnorarDashboard': False,
                    'ValidarIA': '',
                    'MarcacaoIA': f"Auto (Parcela {transacao.get('ParcelaAtual')}/{transacao.get('TotalParcelas')})"
                }
        
        except Exception as e:
            print(f"⚠️  Erro nível 0 (IdParcela): {e}")
        
        return None
    
    def _nivel_1_fatura_cartao(self, transacao):
        """
        Nível 1: Detecta pagamento de fatura de cartão de crédito
        
        Keywords: FATURA, PAGTO FATURA, CARTAO, MASTERCARD, VISA, etc.
        """
        estabelecimento = transacao.get('Estabelecimento', '').upper()
        
        keywords_fatura = [
            'FATURA', 'PAGTO FATURA', 'PGTO FATURA', 'PAG FATURA',
            'CARTAO DE CREDITO', 'CARTÃO CREDITO', 'MASTERCARD', 'VISA',
            'NUBANK', 'ITAUCARD', 'BANCO DO BRASIL - CC'
        ]
        
        for keyword in keywords_fatura:
            if keyword in estabelecimento:
                return {
                    'GRUPO': 'Pagamento Cartão',
                    'SUBGRUPO': 'Fatura',
                    'TipoGasto': 'Transferência',
                    'CategoriaGeral': 'Pagamentos',
                    'origem_classificacao': 'Fatura Cartão',
                    'IgnorarDashboard': True,  # Não conta como gasto real
                    'ValidarIA': '',
                    'MarcacaoIA': 'Auto (Pagamento Fatura)'
                }
        
        return None
    
    def _nivel_2_ignorar(self, transacao):
        """
        Nível 2: Lista de exclusão database-driven + matching de titular
        
        1. Verifica se TED/PIX/TRANSF contém nome do titular (auto-ignorar)
        2. Consulta transacoes_exclusao com acao='IGNORAR'
        """
        estabelecimento = transacao.get('Estabelecimento', '').upper()
        
        try:
            # Importar models
            try:
                from app.models import User, TransacaoExclusao
            except ImportError:
                from app_dev.backend.models import User, TransacaoExclusao
            
            # 1. Buscar nome do titular
            user = self.db.query(User).filter(User.id == self.user_id).first()
            titular_nome = user.nome if user and user.nome else ''
            
            # 2. Verificar se é TED/PIX/TRANSF com nome do titular
            keywords_transferencia = ['TED', 'PIX', 'DOC', 'TRANSF', 'TRANSFERENCIA', 'SAQUE']
            
            for keyword in keywords_transferencia:
                if keyword in estabelecimento:
                    # Fazer fuzzy match com nome do titular
                    if titular_nome and fuzzy_match_titular(estabelecimento, titular_nome):
                        return {
                            'GRUPO': '',
                            'SUBGRUPO': '',
                            'TipoGasto': '',
                            'CategoriaGeral': '',
                            'origem_classificacao': 'Ignorar - Nome do Titular',
                            'IgnorarDashboard': True,
                            'ValidarIA': '',
                            'MarcacaoIA': f'Auto (Transferência própria)'
                        }
            
            # 3. Consultar lista de exclusões com acao='IGNORAR'
            exclusoes = self.db.query(TransacaoExclusao).filter(
                TransacaoExclusao.user_id == self.user_id,
                TransacaoExclusao.ativo == 1,
                TransacaoExclusao.acao == 'IGNORAR'
            ).all()
            
            estabelecimento_norm = normalizar(estabelecimento)
            
            for exclusao in exclusoes:
                nome_exc = normalizar(exclusao.nome_transacao)
                
                if nome_exc in estabelecimento_norm:
                    return {
                        'GRUPO': '',
                        'SUBGRUPO': '',
                        'TipoGasto': '',
                        'CategoriaGeral': '',
                        'origem_classificacao': 'Ignorar - Lista Admin',
                        'IgnorarDashboard': True,
                        'ValidarIA': '',
                        'MarcacaoIA': f'Auto (Excluído: {exclusao.nome_transacao})'
                    }
        
        except Exception as e:
            print(f"⚠️  Erro nível 2 (Ignorar): {e}")
        
        return None
    
    def _nivel_3_base_padroes(self, transacao):
        """
        Nível 3: Padrões aprendidos com alta confiança
        
        Busca em base_padroes por estabelecimento normalizado
        INCLUINDO padrões segmentados por faixa de valor
        """
        try:
            # ⭐ NOVA ABORDAGEM: Usar SQL direto em vez de SQLAlchemy
            import sqlite3
            
            # Path do banco de dados
            db_path = '/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV3/app_dev/backend/database/financas_dev.db'
            
            estabelecimento_base = transacao.get('EstabelecimentoBase', '')
            if not estabelecimento_base:
                estabelecimento_base = normalizar_estabelecimento(transacao.get('Estabelecimento', ''))
            
            estab_norm = normalizar(estabelecimento_base)
            
            # ⭐ NOVA LÓGICA: Gerar padrão segmentado por valor
            valor = transacao.get('Valor', 0) or 0
            faixa_valor = get_faixa_valor(valor)
            padrao_segmentado = f"{estab_norm} [{faixa_valor}]"
            
            print(f"   🔍 Buscando padrão: '{estab_norm}' (valor: {valor:.2f}, faixa: {faixa_valor})")
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # 1. PRIMEIRO: Buscar padrão segmentado exato
            cursor = conn.cursor()
            cursor.execute("""
                SELECT padrao_estabelecimento, grupo_sugerido, subgrupo_sugerido,
                       tipo_gasto_sugerido, contagem
                FROM base_padroes 
                WHERE user_id = ? 
                AND padrao_estabelecimento = ?
                AND confianca = 'alta'
                AND status = 'ativo'
            """, (self.user_id, padrao_segmentado))
            
            resultado = cursor.fetchone()
            
            if resultado:
                print(f"   ✅ Padrão SEGMENTADO encontrado: {padrao_segmentado}")
            else:
                # 2. Buscar padrão NÃO segmentado (formato antigo)
                cursor.execute("""
                    SELECT padrao_estabelecimento, grupo_sugerido, subgrupo_sugerido,
                           tipo_gasto_sugerido, contagem
                    FROM base_padroes 
                    WHERE user_id = ? 
                    AND padrao_estabelecimento = ?
                    AND confianca = 'alta'
                    AND status = 'ativo'
                """, (self.user_id, estab_norm))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    print(f"   ✅ Padrão SIMPLES encontrado: {estab_norm}")
                else:
                    # 3. Buscar por "começa com" (fallback)
                    cursor.execute("""
                        SELECT padrao_estabelecimento, grupo_sugerido, subgrupo_sugerido,
                               tipo_gasto_sugerido, contagem
                        FROM base_padroes 
                        WHERE user_id = ? 
                        AND padrao_estabelecimento LIKE ?
                        AND confianca = 'alta'
                        AND status = 'ativo'
                        LIMIT 1
                    """, (self.user_id, f'{estab_norm}%'))
                    
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        print(f"   ✅ Padrão COMEÇA COM: {estab_norm}% → {resultado['padrao_estabelecimento']}")
            
            conn.close()
            
            if resultado and resultado['grupo_sugerido']:
                return {
                    'GRUPO': resultado['grupo_sugerido'] or '',
                    'SUBGRUPO': resultado['subgrupo_sugerido'] or '',
                    'TipoGasto': resultado['tipo_gasto_sugerido'] or '',
                    'CategoriaGeral': '',
                    'origem_classificacao': 'Base_Padroes',
                    'IgnorarDashboard': False,
                    'ValidarIA': '',
                    'MarcacaoIA': f'Auto (Padrão: {resultado["contagem"]}x observado)'
                }
        
        except Exception as e:
            print(f"⚠️  Erro nível 3 (Base_Padroes): {e}")
        
        return None
    
    def _nivel_4_journal_entries(self, transacao):
        """
        Nível 4: Match exato em transações históricas
        
        Busca em journal_entries por estabelecimento normalizado
        Pega classificação mais frequente dos últimos 12 meses
        """
        try:
            try:
                from app.models import JournalEntry
            except ImportError:
                from app_dev.backend.models import JournalEntry
            from sqlalchemy import func, desc
            from datetime import datetime, timedelta
            
            estabelecimento_base = transacao.get('EstabelecimentoBase', '')
            if not estabelecimento_base:
                estabelecimento_base = normalizar_estabelecimento(transacao.get('Estabelecimento', ''))
            
            estab_norm = normalizar(estabelecimento_base)
            
            # Data limite (12 meses atrás)
            data_limite = datetime.now() - timedelta(days=365)
            
            # Buscar classificação mais frequente
            resultado = self.db.query(
                JournalEntry.GRUPO,
                JournalEntry.SUBGRUPO,
                JournalEntry.TipoGasto,
                func.count(JournalEntry.id).label('contagem')
            ).filter(
                JournalEntry.user_id == self.user_id,
                func.lower(JournalEntry.Estabelecimento).contains(estab_norm.lower()),
                JournalEntry.GRUPO != '',
                JournalEntry.GRUPO != None,
                JournalEntry.created_at >= data_limite
            ).group_by(
                JournalEntry.GRUPO,
                JournalEntry.SUBGRUPO,
                JournalEntry.TipoGasto
            ).order_by(desc('contagem')).first()
            
            if resultado and resultado.contagem >= 2:  # Mínimo 2 ocorrências
                return {
                    'GRUPO': resultado.GRUPO or '',
                    'SUBGRUPO': resultado.SUBGRUPO or '',
                    'TipoGasto': resultado.TipoGasto or '',
                    'CategoriaGeral': '',
                    'origem_classificacao': 'Journal Entries',
                    'IgnorarDashboard': False,
                    'ValidarIA': 'Revisar',
                    'MarcacaoIA': f'Auto (Histórico: {resultado.contagem}x)'
                }
        
        except Exception as e:
            print(f"⚠️  Erro nível 4 (Journal Entries): {e}")
        
        return None
    
    def _nivel_5_palavras_chave(self, transacao):
        """
        Nível 5: Regras por palavras-chave + validação em BaseMarcacao
        
        Detecta padrões comuns e valida se a combinação GRUPO+SUBGRUPO+TipoGasto
        existe na tabela base_marcacoes (combinações válidas)
        """
        try:
            try:
                from app.models import BaseMarcacao
            except ImportError:
                from app_dev.backend.models import BaseMarcacao
            
            estabelecimento = transacao.get('Estabelecimento', '').upper()
            
            # Regras de palavras-chave
            regras = [
                # Alimentação
                (['IFOOD', 'UBER EATS', 'RAPPI', 'RESTAURANTE', 'LANCHONETE'], 
                 'Alimentação', 'Delivery', 'Alimentação'),
                (['SUPERMERCADO', 'MERCADO', 'PADARIA', 'ACOUGUE'], 
                 'Alimentação', 'Supermercado', 'Alimentação'),
                
                # Transporte
                (['UBER', '99 ', 'TAXI', 'CABIFY'], 
                 'Transporte', 'Uber/99', 'Transporte'),
                (['POSTO', 'COMBUSTIVEL', 'GASOLINA', 'IPIRANGA', 'SHELL'], 
                 'Transporte', 'Combustível', 'Transporte'),
                
                # Saúde
                (['FARMACIA', 'DROGARIA', 'DROGA', 'LABORATORIO'], 
                 'Saúde', 'Farmácia', 'Saúde'),
                
                # E-commerce
                (['MERCADOLIVRE', 'MERCADO LIVRE', 'AMAZON', 'SHOPEE', 'MAGALU'], 
                 'Compras Online', 'Marketplace', 'Compras'),
                
                # Streaming
                (['NETFLIX', 'SPOTIFY', 'AMAZON PRIME', 'DISNEY'], 
                 'Assinaturas', 'Streaming', 'Entretenimento'),
            ]
            
            for keywords, grupo, subgrupo, tipo_gasto in regras:
                for keyword in keywords:
                    if keyword in estabelecimento:
                        # Validar combinação em BaseMarcacao
                        marcacao_valida = self.db.query(BaseMarcacao).filter(
                            BaseMarcacao.GRUPO == grupo,
                            BaseMarcacao.SUBGRUPO == subgrupo,
                            BaseMarcacao.TipoGasto == tipo_gasto
                        ).first()
                        
                        if marcacao_valida:
                            return {
                                'GRUPO': grupo,
                                'SUBGRUPO': subgrupo,
                                'TipoGasto': tipo_gasto,
                                'CategoriaGeral': '',
                                'origem_classificacao': 'Palavras-chave',
                                'IgnorarDashboard': False,
                                'ValidarIA': 'Revisar',
                                'MarcacaoIA': f'Auto (Palavra-chave: {keyword})'
                            }
        
        except Exception as e:
            print(f"⚠️  Erro nível 5 (Palavras-chave): {e}")
        
        return None
    
    def _nivel_6_nao_encontrado(self, transacao):
        """
        Nível 6: Fallback quando nenhum nível anterior funcionou
        
        Retorna classificação vazia com origem_classificacao='Não Encontrado'
        para que o usuário faça classificação manual
        """
        return {
            'GRUPO': '',
            'SUBGRUPO': '',
            'TipoGasto': '',
            'CategoriaGeral': '',
            'origem_classificacao': 'Não Encontrado',
            'IgnorarDashboard': False,
            'ValidarIA': 'Revisar',
            'MarcacaoIA': 'Manual (Não classificado)'
        }
    
    def classify_batch(self, transacoes):
        """
        Classifica um lote de transações
        
        Args:
            transacoes (list): Lista de transações processadas
        
        Returns:
            list: Lista de transações com classificações adicionadas
        """
        resultado = []
        
        for transacao in transacoes:
            # Classificar
            classificacao = self.classify(transacao)
            
            # Adicionar classificação à transação
            transacao_completa = {**transacao, **classificacao}
            
            resultado.append(transacao_completa)
        
        return resultado
    
    def get_stats(self):
        """
        Retorna estatísticas de classificação
        
        Returns:
            dict: Contadores por nível e percentuais
        """
        if self.stats['total'] == 0:
            return self.stats
        
        stats_com_percentual = {**self.stats}
        
        for key in self.stats:
            if key != 'total' and key.startswith('nivel_'):
                count = self.stats[key]
                percentual = (count / self.stats['total']) * 100
                stats_com_percentual[f'{key}_percentual'] = round(percentual, 1)
        
        return stats_com_percentual
    
    def print_stats(self):
        """Imprime estatísticas formatadas"""
        stats = self.get_stats()
        
        print("\n" + "="*70)
        print("ESTATÍSTICAS DE CLASSIFICAÇÃO")
        print("="*70)
        print(f"Total de transações: {stats['total']}")
        print()
        print(f"Nível 0 - IdParcela:        {stats['nivel_0_id_parcela']:4d} ({stats.get('nivel_0_id_parcela_percentual', 0):5.1f}%)")
        print(f"Nível 1 - Fatura Cartão:    {stats['nivel_1_fatura_cartao']:4d} ({stats.get('nivel_1_fatura_cartao_percentual', 0):5.1f}%)")
        print(f"Nível 2 - Ignorar:          {stats['nivel_2_ignorar']:4d} ({stats.get('nivel_2_ignorar_percentual', 0):5.1f}%)")
        print(f"Nível 3 - Base Padrões:     {stats['nivel_3_base_padroes']:4d} ({stats.get('nivel_3_base_padroes_percentual', 0):5.1f}%)")
        print(f"Nível 4 - Journal Entries:  {stats['nivel_4_journal_entries']:4d} ({stats.get('nivel_4_journal_entries_percentual', 0):5.1f}%)")
        print(f"Nível 5 - Palavras-chave:   {stats['nivel_5_palavras_chave']:4d} ({stats.get('nivel_5_palavras_chave_percentual', 0):5.1f}%)")
        print(f"Nível 6 - Não Encontrado:   {stats['nivel_6_nao_encontrado']:4d} ({stats.get('nivel_6_nao_encontrado_percentual', 0):5.1f}%)")
        print("="*70)


if __name__ == '__main__':
    print("="*70)
    print("CASCADE CLASSIFIER - Sistema de Classificação em 6 Níveis")
    print("="*70)
    print()
    print("Para usar:")
    print("  1. Processar transações com universal_processor.py")
    print("  2. Criar instância do CascadeClassifier(db_session, user_id)")
    print("  3. Chamar classify(transacao) ou classify_batch(transacoes)")
    print()
    print("Níveis de classificação (ordem de prioridade):")
    print("  0. IdParcela - Copia de parcelas anteriores")
    print("  1. Fatura Cartão - Detecta pagamentos de cartão")
    print("  2. Ignorar - Lista database-driven + titular matching")
    print("  3. Base_Padroes - Padrões aprendidos (alta confiança)")
    print("  4. Journal Entries - Match em histórico")
    print("  5. Palavras-chave - Regras + validação BaseMarcacao")
    print("  6. Não Encontrado - Fallback para classificação manual")
    print("="*70)
