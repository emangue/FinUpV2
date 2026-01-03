"""
Blueprint de Teste - Para debug
"""
from flask import Blueprint, jsonify
from app_dev.backend import db
from app_dev.backend.models_flask import User, JournalEntry, GrupoConfig

bp = Blueprint('test_dev', __name__)

@bp.route('/ping', methods=['GET'])
def ping():
    """Teste simples"""
    return jsonify({'status': 'ok', 'message': 'pong'}), 200

@bp.route('/db-test', methods=['GET'])
def db_test():
    """Testa conexão com banco"""
    try:
        # Contar usuários
        user_count = User.query.count()
        
        # Contar transações
        transaction_count = JournalEntry.query.count()
        
        # Contar grupos
        group_count = GrupoConfig.query.count()
        
        return jsonify({
            'status': 'ok',
            'users': user_count,
            'transactions': transaction_count,
            'groups': group_count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'type': type(e).__name__
        }), 500

@bp.route('/user-list', methods=['GET'])
def user_list():
    """Lista usuários"""
    try:
        users = User.query.all()
        return jsonify({
            'count': len(users),
            'users': [u.to_dict() for u in users]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'type': type(e).__name__
        }), 500
