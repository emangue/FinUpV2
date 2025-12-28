"""
Dashboard Routes - Visualização e análise de dados permanentes
"""
from flask import render_template, request, redirect, url_for, jsonify
from sqlalchemy import func, extract, desc, or_
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from app.blueprints.dashboard import dashboard_bp
from app.models import JournalEntry, BaseMarcacao, AuditLog, GrupoConfig, get_db_session
from app.filters import get_group_color_helper


@dashboard_bp.route('/')
def index():
    """Dashboard analítico com visão geral das finanças - PÁGINA INICIAL"""
    
    db = get_db_session()
    
    try:
        # 1. Determinar meses disponíveis (para o filtro)
        meses_query = db.query(JournalEntry.DT_Fatura).distinct().order_by(desc(JournalEntry.DT_Fatura)).all()
        meses_disponiveis = []
        for m in meses_query:
            if m[0] and len(m[0]) == 6:
                try:
                    dt_obj = datetime.strptime(m[0], "%Y%m")
                    meses_disponiveis.append({
                        'value': dt_obj.strftime("%Y-%m"),
                        'label': dt_obj.strftime("%B %Y").capitalize()
                    })
                except ValueError:
                    continue
        
        # 2. Determinar mês selecionado
        mes_param = request.args.get('mes')
        
        if mes_param:
            mes_atual_db = mes_param.replace('-', '')
            mes_atual_visual = mes_param
        else:
            if meses_disponiveis:
                mes_atual_visual = meses_disponiveis[0]['value']
                mes_atual_db = mes_atual_visual.replace('-', '')
            else:
                hoje = datetime.now()
                mes_atual_visual = hoje.strftime('%Y-%m')
                mes_atual_db = hoje.strftime('%Y%m')
            
        # 3. Determinar mês anterior (para comparação)
        try:
            dt_atual = datetime.strptime(mes_atual_db, '%Y%m')
            dt_anterior = dt_atual - relativedelta(months=1)
            mes_anterior_db = dt_anterior.strftime('%Y%m')
        except:
            mes_anterior_db = None

        # === MÉTRICAS PRINCIPAIS ===
        
        # Total despesas mês atual (incluindo TODOS valores de Cartão de Crédito)
        total_despesas = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            or_(
                JournalEntry.Valor < 0,  # Despesas normais
                JournalEntry.TipoTransacao == 'Cartão de Crédito'  # Todos cartões
            ),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total despesas mês anterior  
        total_despesas_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_anterior_db,
            or_(
                JournalEntry.Valor < 0,
                JournalEntry.TipoTransacao == 'Cartão de Crédito'
            ),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total receitas mês atual (EXCLUINDO Cartão de Crédito)
        total_receitas = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor > 0,
            JournalEntry.TipoTransacao != 'Cartão de Crédito',  # Exclui cartões
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total receitas mês anterior
        total_receitas_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_anterior_db,
            JournalEntry.Valor > 0,
            JournalEntry.TipoTransacao != 'Cartão de Crédito',
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Saldo atual
        saldo = total_receitas + total_despesas
        saldo_anterior = total_receitas_anterior + total_despesas_anterior
        
        # Total de transações
        total_transacoes = db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Transações classificadas
        transacoes_classificadas = db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        perc_classificadas = (transacoes_classificadas / total_transacoes * 100) if total_transacoes > 0 else 0
        
        # Variações percentuais
        variacao_despesas = ((total_despesas / total_despesas_anterior * 100) - 100) if total_despesas_anterior != 0 else 0
        variacao_receitas = ((total_receitas / total_receitas_anterior * 100) - 100) if total_receitas_anterior != 0 else 0
        variacao_saldo = ((saldo / saldo_anterior * 100) - 100) if saldo_anterior != 0 else 0
        
        # Média diária
        try:
            ano = int(mes_atual_db[:4])
            mes = int(mes_atual_db[4:])
            _, dias_no_mes = calendar.monthrange(ano, mes)
            
            hoje = datetime.now()
            if hoje.year == ano and hoje.month == mes:
                dias_considerados = hoje.day
            else:
                dias_considerados = dias_no_mes
                
            media_diaria = total_despesas / dias_considerados if dias_considerados > 0 else 0
        except:
            media_diaria = 0
        
        # Total de estabelecimentos únicos
        total_estabelecimentos = db.query(func.count(func.distinct(JournalEntry.Estabelecimento))).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # === INFORMAÇÕES YTD (Year-to-Date até o mês selecionado) ===
        # Determinar ano do mês selecionado
        ano_atual = mes_atual_db[:4]  # '2025' de '202512'
        mes_numero = int(mes_atual_db[4:6])  # 12 de '202512'
        
        # YTD: Janeiro até mês selecionado
        ytd_inicio = f"{ano_atual}01"
        ytd_fim = mes_atual_db
        
        # 1. Receitas YTD (excluindo investimentos e cartão)
        receitas_ytd = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura >= ytd_inicio,
            JournalEntry.DT_Fatura <= ytd_fim,
            JournalEntry.Valor > 0,
            ~JournalEntry.GRUPPO.ilike('%Investimento%'),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # 2. Cartão de Crédito YTD
        cartao_ytd = abs(db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura >= ytd_inicio,
            JournalEntry.DT_Fatura <= ytd_fim,
            JournalEntry.TipoTransacao == 'Cartão de Crédito',
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0)
        
        # 3. Despesas gerais YTD (sem cartão, sem investimentos)
        despesas_ytd = abs(db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura >= ytd_inicio,
            JournalEntry.DT_Fatura <= ytd_fim,
            JournalEntry.Valor < 0,
            JournalEntry.TipoTransacao != 'Cartão de Crédito',
            ~JournalEntry.GRUPPO.ilike('%Investimento%'),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0)
        
        # 4. Investimento líquido YTD (valores negativos = investimentos)
        investimento_ytd_raw = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura >= ytd_inicio,
            JournalEntry.DT_Fatura <= ytd_fim,
            JournalEntry.GRUPPO.ilike('%Investimento%'),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        investimento_ytd = abs(investimento_ytd_raw)
        
        # Percentual de investimento em relação às receitas
        perc_investimento = (investimento_ytd / receitas_ytd * 100) if receitas_ytd > 0 else 0
        
        # Dados para o gráfico de "Informações YTD"
        ytd_labels = ['Receitas', 'Cartão de Crédito', 'Despesas Gerais', f'Investimento ({perc_investimento:.1f}%)']
        ytd_valores = [receitas_ytd, cartao_ytd, despesas_ytd, investimento_ytd]
        ytd_cores = ['#28a745', '#dc3545', '#ffc107', '#17a2b8']  # verde, vermelho, amarelo, azul
        
        # === DISTRIBUIÇÃO POR GRUPO (mantido para outras partes do dashboard) ===
        grupos_query = db.query(
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.GRUPO.isnot(None),
            JournalEntry.IgnorarDashboard.isnot(True)
        ).group_by(JournalEntry.GRUPO).order_by(func.sum(JournalEntry.Valor).asc()).limit(8).all()
        
        grupos_labels = [g[0] for g in grupos_query]
        grupos_valores = [abs(g[1]) for g in grupos_query]
        grupos_cores = [get_group_color_helper(g[0]) for g in grupos_query]
        
        # Maior aumento e maior economia
        maior_aumento = None
        maior_economia = None
        
        for grupo in grupos_labels:
            total_atual = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_atual_db,
                JournalEntry.GRUPO == grupo,
                JournalEntry.Valor < 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0
            
            total_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_anterior_db,
                JournalEntry.GRUPO == grupo,
                JournalEntry.Valor < 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0
            
            if total_anterior != 0:
                variacao = ((total_atual / total_anterior * 100) - 100)
                if variacao > 20 and (not maior_aumento or variacao > maior_aumento['variacao']):
                    maior_aumento = {'grupo': grupo, 'variacao': variacao}
                if variacao < -20 and (not maior_economia or variacao < maior_economia['variacao']):
                    maior_economia = {'grupo': grupo, 'variacao': variacao}
        
        # === TOP 10 TRANSAÇÕES ===
        top_transacoes_query = db.query(JournalEntry).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).order_by(
            JournalEntry.Valor.asc()
        ).limit(10).all()
        
        max_valor = abs(top_transacoes_query[0].Valor) if top_transacoes_query else 1
        top_estabelecimentos = [
            {
                'id': item.id,
                'data': item.Data if item.Data else 'N/A',  # Data já é string 'DD/MM/AAAA'
                'estabelecimento': item.Estabelecimento,
                'grupo': item.GRUPO,
                'subgrupo': item.SUBGRUPO,
                'total': item.Valor,
                'percentual': (abs(item.Valor) / max_valor * 100),
                'origem': item.TipoTransacao or 'N/A'
            }
            for item in top_transacoes_query
        ]
        
        # === EVOLUÇÃO MENSAL (últimos 6 meses) ===
        evolucao_meses = []
        evolucao_despesas = []
        evolucao_receitas = []
        
        # Mapeamento manual para garantir consistência (português)
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for i in range(5, -1, -1):
            dt_ref = dt_atual - relativedelta(months=i)
            mes_ref = dt_ref.strftime('%Y%m')
            
            # Formato manual: "Mês/Ano" (ex: "Jul/25")
            mes_label = f"{meses_pt[dt_ref.month - 1]}/{dt_ref.strftime('%y')}"
            evolucao_meses.append(mes_label)
            
            # Despesas incluindo TODOS cartões de crédito
            despesas_mes = abs(db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_ref,
                or_(
                    JournalEntry.Valor < 0,
                    JournalEntry.TipoTransacao == 'Cartão de Crédito'
                ),
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0)
            
            # Receitas EXCLUINDO cartões de crédito
            receitas_mes = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_ref,
                JournalEntry.Valor > 0,
                JournalEntry.TipoTransacao != 'Cartão de Crédito',
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0
            
            evolucao_despesas.append(despesas_mes)
            evolucao_receitas.append(receitas_mes)
        
        # === ÚLTIMAS 10 TRANSAÇÕES ===
        ultimas_transacoes = db.query(JournalEntry).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).order_by(
            JournalEntry.Data.desc()
        ).limit(10).all()
        
        # === BREAKDOWN DE DESPESAS - ÚLTIMOS 6 MESES ===
        breakdown_6_meses = []
        # Mapeamento inverso para conversão
        meses_para_num = {
            'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04',
            'Mai': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
            'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
        }
        
        for mes_label in evolucao_meses:
            # Converter formato "Out/25" para "202510"
            try:
                mes_nome, ano_curto = mes_label.split('/')
                mes_num = meses_para_num.get(mes_nome.strip())
                if not mes_num:
                    continue
                mes_db = f"20{ano_curto.strip()}{mes_num}"
            except:
                continue
            
            # Despesas Gerais (despesas não-cartão)
            despesas_gerais = abs(db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_db,
                JournalEntry.Valor < 0,
                JournalEntry.TipoTransacao != 'Cartão de Crédito',
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0)
            
            # Cartão de Crédito
            cartao = abs(db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_db,
                JournalEntry.TipoTransacao == 'Cartão de Crédito',
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0)
            
            # Receitas
            receitas = abs(db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_db,
                JournalEntry.Valor > 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0)
            
            # Investimentos (GRUPO contém 'Investimento' - invertido para positivo)
            investimentos_raw = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_db,
                JournalEntry.GRUPO.ilike('%Investimento%')
            ).scalar() or 0
            # Inverte o sinal: se é negativo (saída), vira positivo (investido)
            investimentos = abs(investimentos_raw)
            
            # Resultado Primário = Receitas - (Despesas Gerais + Cartão)
            resultado_primario = receitas - (despesas_gerais + cartao)
            
            breakdown_6_meses.append({
                'mes': mes_label,
                'despesas_gerais': despesas_gerais,
                'cartao_credito': cartao,
                'resultado_primario': resultado_primario,
                'investimento_liquido': investimentos
            })
        
        stats = {
            'total_despesas': total_despesas,
            'total_receitas': total_receitas,
            'saldo': saldo,
            'total_transacoes': total_transacoes,
            'perc_classificadas': round(perc_classificadas, 1),
            'variacao_despesas': variacao_despesas,
            'variacao_receitas': variacao_receitas,
            'variacao_saldo': variacao_saldo,
            'media_diaria': media_diaria,
            'total_estabelecimentos': total_estabelecimentos,
            'maior_aumento': maior_aumento,
            'maior_economia': maior_economia
        }
        
        return render_template('dashboard.html',
                             stats=stats,
                             breakdown_6_meses=breakdown_6_meses,
                             ytd_labels=ytd_labels,
                             ytd_valores=ytd_valores,
                             ytd_cores=ytd_cores,
                             grupos_labels=grupos_labels,
                             grupos_valores=grupos_valores,
                             grupos_cores=grupos_cores,
                             top_estabelecimentos=top_estabelecimentos,
                             evolucao_meses=evolucao_meses,
                             evolucao_despesas=evolucao_despesas,
                             evolucao_receitas=evolucao_receitas,
                             ultimas_transacoes=ultimas_transacoes,
                             meses_disponiveis=meses_disponiveis,
                             mes_atual=mes_atual_visual)
    
    finally:
        db.close()


@dashboard_bp.route('/transacoes')
def transacoes():
    """Lista todas as transações de um mês específico com filtros"""
    
    mes_param = request.args.get('mes')
    if not mes_param:
        return redirect(url_for('dashboard.index'))
        
    mes_db = mes_param.replace('-', '')
    
    # Filtros
    filtro_estabelecimento = request.args.get('estabelecimento', '').strip()
    filtro_categoria = request.args.get('categoria', '')
    # Aceita múltiplos tipos (vem como lista do formulário)
    filtros_tipos = request.args.getlist('tipo')  # despesa, cartao, receita
    # Filtro de status dashboard: 'consideradas' ou 'todas'
    filtro_dashboard = request.args.get('dashboard', 'consideradas')
    
    try:
        dt_obj = datetime.strptime(mes_db, "%Y%m")
        mes_exibicao = dt_obj.strftime("%B %Y").capitalize()
    except:
        mes_exibicao = mes_param
    
    db = get_db_session()
    try:
        # Query base
        query = db.query(JournalEntry).filter(
            JournalEntry.DT_Fatura == mes_db
        )
        
        # Aplicar filtros
        if filtro_estabelecimento:
            query = query.filter(
                JournalEntry.Estabelecimento.ilike(f'%{filtro_estabelecimento}%')
            )
        
        if filtro_categoria:
            query = query.filter(JournalEntry.GRUPO == filtro_categoria)
        
        # Filtro de status dashboard
        if filtro_dashboard == 'consideradas':
            # Apenas transações consideradas (IgnorarDashboard = False ou NULL)
            query = query.filter(
                (JournalEntry.IgnorarDashboard == False) | (JournalEntry.IgnorarDashboard == None)
            )
        # Se 'todas', não aplica filtro (mostra incluindo ignoradas)
        
        # Filtro de tipo com múltiplas seleções
        if filtros_tipos:
            from sqlalchemy import or_, and_
            condicoes = []
            
            if 'despesa' in filtros_tipos:
                # Despesas não-cartão
                condicoes.append(
                    and_(
                        JournalEntry.Valor < 0,
                        JournalEntry.TipoTransacao != 'Cartão de Crédito'
                    )
                )
            
            if 'cartao' in filtros_tipos:
                # Cartão de crédito
                condicoes.append(
                    JournalEntry.TipoTransacao == 'Cartão de Crédito'
                )
            
            if 'receita' in filtros_tipos:
                # Receitas (valor positivo)
                condicoes.append(JournalEntry.Valor > 0)
            
            if condicoes:
                query = query.filter(or_(*condicoes))
        
        transacoes = query.order_by(JournalEntry.Data.desc()).all()
        
        # Calcular soma dos valores filtrados
        soma_filtrada = sum(t.Valor for t in transacoes)
        
        # Buscar todos os grupos para o dropdown
        grupos = db.query(BaseMarcacao.GRUPO).distinct().order_by(BaseMarcacao.GRUPO).all()
        grupos_lista = [g[0] for g in grupos if g[0]]
        
        return render_template('transacoes.html',
                             transacoes=transacoes,
                             mes_atual=mes_param,
                             mes_exibicao=mes_exibicao,
                             total_transacoes=len(transacoes),
                             soma_filtrada=soma_filtrada,
                             grupos_lista=grupos_lista,
                             filtro_estabelecimento=filtro_estabelecimento,
                             filtro_categoria=filtro_categoria,
                             filtros_tipos=filtros_tipos,
                             filtro_dashboard=filtro_dashboard)
    finally:
        db.close()


@dashboard_bp.route('/api/transacao/<transacao_id>')
def api_transacao_detalhes(transacao_id):
    """API para buscar detalhes de uma transação"""
    try:
        db = get_db_session()
        transacao = db.query(JournalEntry).filter(
            JournalEntry.id == transacao_id
        ).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        detalhes = {
            'ID': transacao.id,
            'Data': transacao.Data.strftime('%d/%m/%Y') if transacao.Data else 'N/A',
            'Estabelecimento': transacao.Estabelecimento,
            'Valor': float(transacao.Valor),
            'GRUPO': transacao.GRUPO,
            'SubGrupo': transacao.SUBGRUPO,
            'Descricao': transacao.Descricao,
            'PixChaveDestino': transacao.PixChaveDestino,
            'CategoriaTransacao': transacao.CategoriaTransacao,
            'StatusTransacao': transacao.StatusTransacao,
            'IgnorarDashboard': transacao.IgnorarDashboard
        }
        
        db.close()
        return jsonify(detalhes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/transacao_completa/<int:transacao_id>')
def api_transacao_completa(transacao_id):
    """API para buscar dados completos de uma transação para edição"""
    try:
        db = get_db_session()
        transacao = db.query(JournalEntry).filter(
            JournalEntry.id == transacao_id
        ).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        dados = {
            'id': transacao.id,
            'IdTransacao': transacao.IdTransacao,
            'Data': transacao.Data,
            'Estabelecimento': transacao.Estabelecimento,
            'Valor': float(transacao.Valor),
            'GRUPO': transacao.GRUPO,
            'SUBGRUPO': transacao.SUBGRUPO,
            'TipoTransacao': transacao.TipoTransacao,
            'IgnorarDashboard': transacao.IgnorarDashboard or False
        }
        
        db.close()
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/atualizar_transacao', methods=['POST'])
def api_atualizar_transacao():
    """API para atualizar uma transação"""
    try:
        dados = request.get_json()
        transacao_id = dados.get('id')
        
        if not transacao_id:
            return jsonify({'success': False, 'error': 'ID não fornecido'}), 400
        
        db = get_db_session()
        transacao = db.query(JournalEntry).filter(
            JournalEntry.id == transacao_id
        ).first()
        
        if not transacao:
            db.close()
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
        
        # Atualizar campos
        if 'valor' in dados:
            transacao.Valor = dados['valor']
            transacao.ValorPositivo = abs(dados['valor'])
        
        if 'estabelecimento' in dados:
            transacao.Estabelecimento = dados['estabelecimento']
        
        if 'grupo' in dados:
            transacao.GRUPO = dados['grupo']
        
        if 'subgrupo' in dados:
            transacao.SUBGRUPO = dados['subgrupo']
        
        if 'ignorar_dashboard' in dados:
            transacao.IgnorarDashboard = dados['ignorar_dashboard']
        
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'message': 'Transação atualizada com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/api/subgrupos/<grupo>')
def api_subgrupos_por_grupo(grupo):
    """API para buscar subgrupos disponíveis para um grupo específico"""
    try:
        db = get_db_session()
        
        # Busca subgrupos válidos para o grupo
        subgrupos = db.query(
            BaseMarcacao.SUBGRUPO, 
            BaseMarcacao.TipoGasto
        ).filter(
            BaseMarcacao.GRUPO == grupo
        ).distinct().order_by(BaseMarcacao.SUBGRUPO).all()
        
        # Monta lista de opções
        opcoes = [
            {
                'subgrupo': s[0],
                'tipo_gasto': s[1]
            }
            for s in subgrupos
        ]
        
        db.close()
        return jsonify({'success': True, 'subgrupos': opcoes})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/editar_transacao', methods=['POST'])
def editar_transacao():
    """Edita uma transação permanente no dashboard"""
    try:
        data = request.get_json()
        id_transacao = data.get('id')
        grupo = data.get('grupo')
        subgrupo = data.get('subgrupo')
        
        if not all([id_transacao, grupo, subgrupo]):
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        db = get_db_session()
        
        # Buscar transação
        transacao = db.query(JournalEntry).filter_by(id=id_transacao).first()
        if not transacao:
            db.close()
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
        
        # Validar combinação em BaseMarcacao e obter TipoGasto
        marcacao = db.query(BaseMarcacao).filter_by(
            GRUPO=grupo,
            SUBGRUPO=subgrupo
        ).first()
        
        if not marcacao:
            db.close()
            return jsonify({'success': False, 'error': 'Combinação GRUPO/SUBGRUPO inválida'}), 400
        
        # Salvar estado anterior para auditoria
        estado_anterior = {
            'GRUPO': transacao.GRUPO,
            'SUBGRUPO': transacao.SUBGRUPO,
            'TipoGasto': transacao.TipoGasto
        }
        
        # Atualizar transação
        transacao.GRUPO = grupo
        transacao.SUBGRUPO = subgrupo
        transacao.TipoGasto = marcacao.TipoGasto  # Preenche automaticamente
        
        # Registrar em AuditLog
        audit = AuditLog(
            action='UPDATE',
            table_name='journal_entries',
            record_id=transacao.id,
            before_data=str(estado_anterior),
            after_data=str({
                'GRUPO': grupo,
                'SUBGRUPO': subgrupo,
                'TipoGasto': marcacao.TipoGasto
            }),
            ip_address=request.remote_addr,
            session_id=request.cookies.get('session', 'unknown')
        )
        db.add(audit)
        
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'tipo_gasto': marcacao.TipoGasto
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/toggle_dashboard/<string:id_transacao>', methods=['POST'])
def toggle_dashboard_status(id_transacao):
    """Alterna o status de IgnorarDashboard de uma transação"""
    try:
        print(f"🔄 Toggle Dashboard solicitado para ID: {id_transacao}")
        data = request.get_json()
        ignorar = data.get('ignorar', True)
        
        print(f"📝 Novo status IgnorarDashboard: {ignorar}")
        
        db = get_db_session()
        transacao = db.query(JournalEntry).filter_by(IdTransacao=id_transacao).first()
        
        if not transacao:
            print(f"❌ Transação {id_transacao} não encontrada")
            db.close()
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
            
        transacao.IgnorarDashboard = bool(ignorar)
        db.commit()
        print(f"✅ Transação {id_transacao} atualizada com sucesso")
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Erro no toggle: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
