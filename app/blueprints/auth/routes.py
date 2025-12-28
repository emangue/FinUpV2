"""
Rotas de Autenticação

Versão: 2.1.0-dev
Data: 28/12/2025

Implementa:
- Login de usuários
- Logout
- Registro de novos usuários (apenas para admin criar)
- Perfil do usuário
"""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app.models import User, get_db_session
from . import auth_bp


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
    
    return render_template('list_users.html', users=users)


@auth_bp.route('/profile')
@login_required
def profile():
    """Perfil do usuário logado"""
    return render_template('profile.html', user=current_user)


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
