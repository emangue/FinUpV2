"""
Blueprint de Transações - API DEV
Endpoints para listar, criar, editar, deletar transações
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app_dev.backend import db
from app_dev.backend.models_flask import JournalEntry

bp = Blueprint('transactions_dev', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def list_transactions():
    """
    Lista transações com filtros e paginação
    Query params:
        - page: int (padrão 1)
        - per_page: int (padrão 20)
        - grupo: string (opcional)
        - marcacao: string (opcional)
        - estabelecimento: string (opcional)
        - data_inicio: YYYY-MM-DD (opcional)
        - data_fim: YYYY-MM-DD (opcional)
    """
    try:
        user_id = get_jwt_identity()
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtros
        query = JournalEntry.query.filter_by(user_id=user_id)
        
        if grupo := request.args.get('grupo'):
            query = query.filter_by(grupo=grupo)
        
        if marcacao := request.args.get('marcacao'):
            query = query.filter_by(marcacao=marcacao)
        
        if estabelecimento := request.args.get('estabelecimento'):
            query = query.filter(JournalEntry.estabelecimento.ilike(f'%{estabelecimento}%'))
        
        if data_inicio := request.args.get('data_inicio'):
            query = query.filter(JournalEntry.data >= datetime.fromisoformat(data_inicio))
        
        if data_fim := request.args.get('data_fim'):
            query = query.filter(JournalEntry.data <= datetime.fromisoformat(data_fim))
        
        # Ordena por data decrescente
        query = query.order_by(JournalEntry.data.desc())
        
        # Paginação
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        transacoes = [{
            'id': t.id,
            'id_transacao': t.id_transacao,
            'data': t.data.isoformat() if t.data else None,
            'estabelecimento': t.estabelecimento,
            'valor': float(t.valororiginal),
            'tipo': t.tipodocumento,
            'grupo': t.grupo,
            'marcacao': t.marcacao,
            'banco': t.banco,
            'observacoes': t.observacoes,
            'id_parcela': t.id_parcela,
            'numero_parcela': t.numero_parcela,
            'total_parcelas': t.total_parcelas
        } for t in pagination.items]
        
        return jsonify({
            'data': transacoes,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar transações: {str(e)}'}), 500


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    """Busca transação específica"""
    try:
        user_id = get_jwt_identity()
        transacao = JournalEntry.query.filter_by(id=id, user_id=user_id).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        dados = {
            'id': transacao.id,
            'id_transacao': transacao.id_transacao,
            'data': transacao.data.isoformat() if transacao.data else None,
            'estabelecimento': transacao.estabelecimento,
            'valor': float(transacao.valororiginal),
            'tipo': transacao.tipodocumento,
            'grupo': transacao.grupo,
            'marcacao': transacao.marcacao,
            'banco': transacao.banco,
            'observacoes': transacao.observacoes,
            'id_parcela': transacao.id_parcela,
            'numero_parcela': transacao.numero_parcela,
            'total_parcelas': transacao.total_parcelas
        }
        
        return jsonify(dados), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transação: {str(e)}'}), 500


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    """
    Atualiza transação
    Body: {"grupo": "...", "marcacao": "...", "observacoes": "..."}
    """
    try:
        user_id = get_jwt_identity()
        transacao = JournalEntry.query.filter_by(id=id, user_id=user_id).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        data = request.get_json()
        
        # Atualiza campos permitidos
        if 'grupo' in data:
            transacao.grupo = data['grupo']
        if 'marcacao' in data:
            transacao.marcacao = data['marcacao']
        if 'observacoes' in data:
            transacao.observacoes = data['observacoes']
        
        db.session.commit()
        
        return jsonify({'message': 'Transação atualizada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar transação: {str(e)}'}), 500


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    """Deleta transação"""
    try:
        user_id = get_jwt_identity()
        transacao = JournalEntry.query.filter_by(id=id, user_id=user_id).first()
        
        if not transacao:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        db.session.delete(transacao)
        db.session.commit()
        
        return jsonify({'message': 'Transação deletada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar transação: {str(e)}'}), 500
