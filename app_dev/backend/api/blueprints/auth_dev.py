"""
Blueprint de Autenticação - API DEV
Endpoints para login, registro, refresh token
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app_dev.backend import db
from app_dev.backend.models_flask import User

bp = Blueprint('auth_dev', __name__)

@bp.route('/login', methods=['POST'])
def login():
    """
    Login de usuário
    Body: {"email": "user@email.com", "password": "senha"}
    Returns: {"access_token": "...", "refresh_token": "...", "user": {...}}
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Busca usuário
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        if not user.ativo:
            return jsonify({'error': 'Usuário inativo'}), 403
        
        # Gera tokens
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro no login: {str(e)}'}), 500


@bp.route('/register', methods=['POST'])
def register():
    """
    Registro de novo usuário
    Body: {"email": "...", "password": "...", "nome": "..."}
    """
    try:
        data = request.get_json()
        
        # Validações
        if not data or not data.get('email') or not data.get('password') or not data.get('nome'):
            return jsonify({'error': 'Email, senha e nome são obrigatórios'}), 400
        
        # Verifica se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Cria usuário
        user = User(
            email=data['email'],
            nome=data['nome'],
            role='user',
            ativo=True
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Gera tokens
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro no registro: {str(e)}'}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Renova access token usando refresh token
    Header: Authorization: Bearer <refresh_token>
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.ativo:
            return jsonify({'error': 'Usuário inválido'}), 401
        
        access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        
        return jsonify({'access_token': access_token}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao renovar token: {str(e)}'}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Retorna dados do usuário logado
    Header: Authorization: Bearer <access_token>
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuário: {str(e)}'}), 500


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout (no futuro: blacklist de token)
    """
    return jsonify({'message': 'Logout realizado com sucesso'}), 200
