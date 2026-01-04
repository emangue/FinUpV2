"""
Rotas de Autenticação

Versão: 3.0.0-dev
Data: 28/12/2025

Implementa:
- Login de usuários
- Logout
- Registro de novos usuários (apenas para admin criar)
- Perfil do usuário
- Troca de senha
- Gestão de contas conectadas (relacionamentos)
- Visão consolidada entre contas
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime
from app.models import User, UserRelationship, get_db_session
from . import auth_bp


@auth_bp.app_context_processor
def inject_notifications():
    """Injeta contagem de notificações em todos os templates"""
    if current_user.is_authenticated:
        db = get_db_session()
        pending_count = db.query(UserRelationship).filter(
            UserRelationship.connected_user_id == current_user.id,
            UserRelationship.status == 'pending'
        ).count()
        return {'pending_requests_count': pending_count}
    return {'pending_requests_count': 0}


@auth_bp.app_context_processor
def inject_notifications():
    """Injeta contagem de notificações em todos os templates"""
    if current_user.is_authenticated:
        db = get_db_session()
        pending_count = db.query(UserRelationship).filter(
            UserRelationship.connected_user_id == current_user.id,
            UserRelationship.status == 'pending'
        ).count()
        return {'pending_requests_count': pending_count}
    return {'pending_requests_count': 0}


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        db = get_db_session()
        user = db.query(User).filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            flash('Email ou senha inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.ativo:
            flash('Sua conta está desativada. Entre em contato com o administrador.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        
        # Redirect para página requisitada originalmente
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você saiu da sua conta com sucesso', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Registro de novo usuário (apenas admin)"""
    if current_user.role != 'admin':
        flash('Apenas administradores podem criar novos usuários', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        role = request.form.get('role', 'user')
        
        # Validações
        if not nome or not email or not password:
            flash('Todos os campos são obrigatórios', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != password2:
            flash('As senhas não conferem', 'danger')
            return redirect(url_for('auth.register'))
        
        db = get_db_session()
        
        # Verifica se email já existe
        if db.query(User).filter_by(email=email).first():
            flash('Este email já está cadastrado', 'danger')
            return redirect(url_for('auth.register'))
        
        # Cria novo usuário
        user = User(
            nome=nome,
            email=email,
            role=role,
            ativo=True
        )
        user.set_password(password)
        
        db.add(user)
        db.commit()
        
        flash(f'Usuário {nome} criado com sucesso!', 'success')
        return redirect(url_for('auth.list_users'))
    
    return render_template('register.html')


@auth_bp.route('/users')
@login_required
def list_users():
    """Lista todos os usuários (apenas admin)"""
    if current_user.role != 'admin':
        flash('Acesso negado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    db = get_db_session()
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    # Para cada usuário, buscar contas conectadas
    users_with_connections = []
    for user in users:
        # Buscar relacionamentos aceitos
        connections = db.query(UserRelationship).filter(
            ((UserRelationship.user_id == user.id) | 
             (UserRelationship.connected_user_id == user.id)),
            UserRelationship.status == 'accepted'
        ).all()
        
        # Obter nomes dos usuários conectados
        connected_users = []
        for rel in connections:
            if rel.user_id == user.id:
                connected_user = db.query(User).get(rel.connected_user_id)
            else:
                connected_user = db.query(User).get(rel.user_id)
            
            if connected_user:
                status = '🔗 Consolidado' if rel.view_consolidated else '🔓 Separado'
                connected_users.append({
                    'nome': connected_user.nome,
                    'email': connected_user.email,
                    'status': status
                })
        
        users_with_connections.append({
            'user': user,
            'connections': connected_users
        })
    
    return render_template('list_users.html', users_data=users_with_connections)


@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário logado"""
    db = get_db_session()
    
    # Buscar relacionamentos ativos
    relacionamentos = db.query(UserRelationship).filter(
        ((UserRelationship.user_id == current_user.id) | 
         (UserRelationship.connected_user_id == current_user.id)) &
        (UserRelationship.status == 'accepted')
    ).all()
    
    # Buscar convites pendentes
    convites_pendentes = db.query(UserRelationship).filter(
        (UserRelationship.connected_user_id == current_user.id) &
        (UserRelationship.status == 'pending')
    ).all()
    
    return render_template('profile.html', 
                         user=current_user, 
                         relacionamentos=relacionamentos,
                         convites_pendentes=convites_pendentes)


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Troca de senha do usuário logado"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validações
    if not current_password or not new_password or not confirm_password:
        flash('Todos os campos são obrigatórios', 'danger')
        return redirect(url_for('auth.profile'))
    
    if not current_user.check_password(current_password):
        flash('Senha atual incorreta', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('A nova senha e a confirmação não conferem', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres', 'warning')
        return redirect(url_for('auth.profile'))
    
    # Atualiza senha
    db = get_db_session()
    current_user.set_password(new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/connect-account', methods=['POST'])
@login_required
def connect_account():
    """Solicita conexão com outra conta"""
    email_to_connect = request.form.get('email')
    
    if not email_to_connect:
        flash('Email é obrigatório', 'danger')
        return redirect(url_for('auth.profile'))
    
    db = get_db_session()
    
    # Buscar usuário para conectar
    user_to_connect = db.query(User).filter_by(email=email_to_connect).first()
    
    if not user_to_connect:
        flash('Usuário não encontrado', 'danger')
        return redirect(url_for('auth.profile'))
    
    if user_to_connect.id == current_user.id:
        flash('Você não pode conectar com sua própria conta', 'warning')
        return redirect(url_for('auth.profile'))
    
    # Verificar se já existe relacionamento
    relacionamento_existente = db.query(UserRelationship).filter(
        ((UserRelationship.user_id == current_user.id) & 
         (UserRelationship.connected_user_id == user_to_connect.id)) |
        ((UserRelationship.user_id == user_to_connect.id) & 
         (UserRelationship.connected_user_id == current_user.id))
    ).first()
    
    if relacionamento_existente:
        if relacionamento_existente.status == 'accepted':
            flash('Você já está conectado com esta conta', 'info')
        elif relacionamento_existente.status == 'pending':
            flash('Já existe uma solicitação pendente com esta conta', 'info')
        else:
            flash('Conexão foi rejeitada anteriormente', 'warning')
        return redirect(url_for('auth.profile'))
    
    # Criar novo relacionamento
    relacionamento = UserRelationship(
        user_id=current_user.id,
        connected_user_id=user_to_connect.id,
        status='pending',
        view_consolidated=False
    )
    db.add(relacionamento)
    db.commit()
    
    flash(f'Solicitação de conexão enviada para {user_to_connect.nome}', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/relationship/<int:relationship_id>/accept', methods=['POST'])
@login_required
def accept_relationship(relationship_id):
    """Aceita uma solicitação de conexão"""
    db = get_db_session()
    relacionamento = db.query(UserRelationship).get(relationship_id)
    
    if not relacionamento:
        flash('Solicitação não encontrada', 'danger')
        return redirect(url_for('auth.profile'))
    
    if relacionamento.connected_user_id != current_user.id:
        flash('Você não pode aceitar esta solicitação', 'danger')
        return redirect(url_for('auth.profile'))
    
    if relacionamento.status != 'pending':
        flash('Esta solicitação não está pendente', 'warning')
        return redirect(url_for('auth.profile'))
    
    relacionamento.status = 'accepted'
    relacionamento.accepted_at = datetime.utcnow()
    db.commit()
    
    flash('Conexão aceita com sucesso!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/relationship/<int:relationship_id>/reject', methods=['POST'])
@login_required
def reject_relationship(relationship_id):
    """Rejeita uma solicitação de conexão"""
    db = get_db_session()
    relacionamento = db.query(UserRelationship).get(relationship_id)
    
    if not relacionamento:
        flash('Solicitação não encontrada', 'danger')
        return redirect(url_for('auth.profile'))
    
    if relacionamento.connected_user_id != current_user.id:
        flash('Você não pode rejeitar esta solicitação', 'danger')
        return redirect(url_for('auth.profile'))
    
    relacionamento.status = 'rejected'
    db.commit()
    
    flash('Solicitação rejeitada', 'info')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/relationship/<int:relationship_id>/toggle-consolidated', methods=['POST'])
@login_required
def toggle_consolidated_view(relationship_id):
    """Ativa/desativa visão consolidada"""
    db = get_db_session()
    relacionamento = db.query(UserRelationship).get(relationship_id)
    
    if not relacionamento:
        flash('Relacionamento não encontrado', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Verificar se usuário pode modificar
    if relacionamento.user_id != current_user.id and relacionamento.connected_user_id != current_user.id:
        flash('Você não pode modificar este relacionamento', 'danger')
        return redirect(url_for('auth.profile'))
    
    if relacionamento.status != 'accepted':
        flash('Relacionamento não está ativo', 'warning')
        return redirect(url_for('auth.profile'))
    
    relacionamento.view_consolidated = not relacionamento.view_consolidated
    db.commit()
    
    status = "ativada" if relacionamento.view_consolidated else "desativada"
    flash(f'Visão consolidada {status}', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/relationship/<int:relationship_id>/disconnect', methods=['POST'])
@login_required
def disconnect_account(relationship_id):
    """Desconecta contas"""
    db = get_db_session()
    relacionamento = db.query(UserRelationship).get(relationship_id)
    
    if not relacionamento:
        flash('Relacionamento não encontrado', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Verificar se usuário pode remover
    if relacionamento.user_id != current_user.id and relacionamento.connected_user_id != current_user.id:
        flash('Você não pode remover este relacionamento', 'danger')
        return redirect(url_for('auth.profile'))
    
    db.delete(relacionamento)
    db.commit()
    
    flash('Contas desconectadas com sucesso', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    """Ativa/desativa um usuário (apenas admin)"""
    if current_user.role != 'admin':
        flash('Acesso negado', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if current_user.id == user_id:
        flash('Você não pode desativar sua própria conta', 'warning')
        return redirect(url_for('auth.list_users'))
    
    db = get_db_session()
    user = db.query(User).get(user_id)
    
    if not user:
        flash('Usuário não encontrado', 'danger')
        return redirect(url_for('auth.list_users'))
    
    user.ativo = not user.ativo
    db.commit()
    
    status = "ativado" if user.ativo else "desativado"
    flash(f'Usuário {user.nome} {status} com sucesso', 'success')
    
    return redirect(url_for('auth.list_users'))
