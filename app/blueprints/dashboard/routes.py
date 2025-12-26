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
        
        # Total despesas mês atual
        total_despesas = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total despesas mês anterior
        total_despesas_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_anterior_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total receitas mês atual
        total_receitas = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor > 0,
            JournalEntry.IgnorarDashboard.isnot(True)
        ).scalar() or 0
        
        # Total receitas mês anterior
        total_receitas_anterior = db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.DT_Fatura == mes_anterior_db,
            JournalEntry.Valor > 0,
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
        
        # === DISTRIBUIÇÃO POR GRUPO ===
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
        
        # === TOP 10 SUBGRUPOS ===
        top_subgrupos_query = db.query(
            JournalEntry.SUBGRUPO,
            JournalEntry.GRUPO,
            func.sum(JournalEntry.Valor).label('total')
        ).filter(
            JournalEntry.DT_Fatura == mes_atual_db,
            JournalEntry.Valor < 0,
            JournalEntry.IgnorarDashboard.isnot(True),
            JournalEntry.SUBGRUPO.isnot(None)
        ).group_by(
            JournalEntry.SUBGRUPO,
            JournalEntry.GRUPO
        ).order_by(
            func.sum(JournalEntry.Valor).asc()
        ).limit(10).all()
        
        max_valor = abs(top_subgrupos_query[0][2]) if top_subgrupos_query else 1
        top_estabelecimentos = [
            {
                'estabelecimento': item[0],
                'grupo': item[1],
                'total': item[2],
                'percentual': (abs(item[2]) / max_valor * 100)
            }
            for item in top_subgrupos_query
        ]
        
        # === EVOLUÇÃO MENSAL (últimos 6 meses) ===
        evolucao_meses = []
        evolucao_despesas = []
        evolucao_receitas = []
        
        for i in range(5, -1, -1):
            dt_ref = dt_atual - relativedelta(months=i)
            mes_ref = dt_ref.strftime('%Y%m')
            
            evolucao_meses.append(dt_ref.strftime('%b/%y'))
            
            despesas_mes = abs(db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_ref,
                JournalEntry.Valor < 0,
                JournalEntry.IgnorarDashboard.isnot(True)
            ).scalar() or 0)
            
            receitas_mes = db.query(func.sum(JournalEntry.Valor)).filter(
                JournalEntry.DT_Fatura == mes_ref,
                JournalEntry.Valor > 0,
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
    """Lista todas as transações de um mês específico"""
    
    mes_param = request.args.get('mes')
    if not mes_param:
        return redirect(url_for('dashboard.index'))
        
    mes_db = mes_param.replace('-', '')
    
    try:
        dt_obj = datetime.strptime(mes_db, "%Y%m")
        mes_exibicao = dt_obj.strftime("%B %Y").capitalize()
    except:
        mes_exibicao = mes_param
    
    db = get_db_session()
    try:
        transacoes = db.query(JournalEntry).filter(
            JournalEntry.DT_Fatura == mes_db
        ).order_by(JournalEntry.Data.desc()).all()
        
        # Buscar todos os grupos para o dropdown
        grupos = db.query(BaseMarcacao.GRUPO).distinct().order_by(BaseMarcacao.GRUPO).all()
        grupos_lista = [g[0] for g in grupos]
        
        return render_template('transacoes.html',
                             transacoes=transacoes,
                             mes_atual=mes_param,
                             mes_exibicao=mes_exibicao,
                             total_transacoes=len(transacoes),
                             grupos_lista=grupos_lista)
    finally:
        db.close()


@dashboard_bp.route('/api/transacao/<transacao_id>')
def api_transacao_detalhes(transacao_id):
    """API para buscar detalhes de uma transação"""
    try:
        db = get_db_session()
        transacao = db.query(JournalEntry).filter(
            JournalEntry.ID == transacao_id
        ).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        detalhes = {
            'ID': transacao.ID,
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
