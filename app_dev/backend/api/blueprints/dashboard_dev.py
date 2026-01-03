"""
Blueprint do Dashboard - API DEV
Endpoints para métricas e dados do dashboard
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app_dev.backend import db
from app_dev.backend.models_flask import JournalEntry, GrupoConfig

bp = Blueprint('dashboard_dev', __name__)

@bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """
    Retorna métricas principais do dashboard
    Returns: {
        "total_gastos": float,
        "total_receitas": float,
        "saldo": float,
        "total_transacoes": int,
        "transacoes_mes_atual": int
    }
    """
    try:
        user_id = get_jwt_identity()
        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1)
        
        # Total de gastos (débitos)
        total_gastos = db.session.query(func.sum(JournalEntry.valororiginal))\
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.tipodocumento == 'Débito'
            ).scalar() or 0.0
        
        # Total de receitas (créditos)
        total_receitas = db.session.query(func.sum(JournalEntry.valororiginal))\
            .filter(
                JournalEntry.user_id == user_id,
                JournalEntry.tipodocumento == 'Crédito'
            ).scalar() or 0.0
        
        # Saldo
        saldo = total_receitas - abs(total_gastos)
        
        # Total de transações
        total_transacoes = JournalEntry.query.filter_by(user_id=user_id).count()
        
        # Transações do mês atual
        transacoes_mes_atual = JournalEntry.query.filter(
            JournalEntry.user_id == user_id,
            JournalEntry.data >= inicio_mes
        ).count()
        
        return jsonify({
            'total_gastos': abs(total_gastos),
            'total_receitas': total_receitas,
            'saldo': saldo,
            'total_transacoes': total_transacoes,
            'transacoes_mes_atual': transacoes_mes_atual
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar métricas: {str(e)}'}), 500


@bp.route('/chart/gastos-mes', methods=['GET'])
@jwt_required()
def get_gastos_por_mes():
    """
    Retorna gastos agregados por mês (últimos 6 meses)
    Returns: [{"mes": "2025-01", "total": 1500.50}, ...]
    """
    try:
        user_id = get_jwt_identity()
        seis_meses_atras = datetime.now() - timedelta(days=180)
        
        # Query agregada por ano/mês
        resultados = db.session.query(
            func.strftime('%Y-%m', JournalEntry.data).label('mes'),
            func.sum(func.abs(JournalEntry.valororiginal)).label('total')
        ).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.tipodocumento == 'Débito',
            JournalEntry.data >= seis_meses_atras
        ).group_by('mes').order_by('mes').all()
        
        dados = [{'mes': r.mes, 'total': float(r.total)} for r in resultados]
        
        return jsonify(dados), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar gráfico: {str(e)}'}), 500


@bp.route('/recent-transactions', methods=['GET'])
@jwt_required()
def get_recent_transactions():
    """
    Retorna últimas 10 transações
    """
    try:
        user_id = get_jwt_identity()
        
        transacoes = JournalEntry.query.filter_by(user_id=user_id)\
            .order_by(JournalEntry.data.desc())\
            .limit(10)\
            .all()
        
        dados = [{
            'id': t.id,
            'data': t.data.isoformat() if t.data else None,
            'estabelecimento': t.estabelecimento,
            'valor': float(t.valororiginal),
            'tipo': t.tipodocumento,
            'grupo': t.grupo,
            'marcacao': t.marcacao
        } for t in transacoes]
        
        return jsonify(dados), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações recentes: {str(e)}'}), 500


@bp.route('/grupos', methods=['GET'])
@jwt_required()
def get_grupos():
    """
    Retorna todos os grupos ativos
    """
    try:
        grupos = GrupoConfig.query.filter_by(ativo=True).all()
        
        dados = [{
            'id': g.id,
            'nome': g.nome,
            'icone': g.icone,
            'cor': g.cor
        } for g in grupos]
        
        return jsonify(dados), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar grupos: {str(e)}'}), 500
