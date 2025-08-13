from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import Usuario, Pedido, db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re
import requests
import json
from urllib.parse import urlencode

usuarios_bp = Blueprint('usuarios', __name__)

def login_required(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Salvar a URL atual na sessão para redirecionamento após login
            session['redirect_after_login'] = request.url
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de usuário"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        telefone = request.form.get('telefone', '').strip()
        endereco = request.form.get('endereco', '').strip()
        
        # Validações
        if not nome or len(nome) < 2:
            flash('Nome deve ter pelo menos 2 caracteres.', 'error')
            return render_template('usuarios/registro.html')
        
        if not email or '@' not in email:
            flash('Email inválido.', 'error')
            return render_template('usuarios/registro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return render_template('usuarios/registro.html')
        
        if len(senha) < 6:
            flash('Senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('usuarios/registro.html')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('usuarios/registro.html')
        
        # Criar usuário
        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            telefone=telefone,
            endereco=endereco
        )
        
        try:
            db.session.add(usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            
            # Salvar a URL de redirecionamento se existir na sessão
            redirect_url = session.get('redirect_after_login')
            if redirect_url:
                return redirect(url_for('usuarios.login'))
            return redirect(url_for('usuarios.login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
            return render_template('usuarios/registro.html')
    
    return render_template('usuarios/registro.html')

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login de usuário"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Preencha todos os campos.', 'error')
            return render_template('usuarios/login.html')
        
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        
        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['user_id'] = usuario.id
            session['user_nome'] = usuario.nome
            session['user_email'] = usuario.email
            
            # Atualizar último login
            from datetime import datetime
            usuario.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Bem-vindo(a) de volta, {usuario.nome}!', 'success')
            
            # Verificar se há uma URL salva na sessão para redirecionamento
            redirect_url = session.pop('redirect_after_login', None)
            if redirect_url:
                return redirect(redirect_url)
            
            # Redirecionar para a página que o usuário estava tentando acessar (fallback)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('loja.index'))
        else:
            flash('Email ou senha incorretos.', 'error')
            return render_template('usuarios/login.html')
    
    return render_template('usuarios/login.html')

@usuarios_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('user_id', None)
    session.pop('user_nome', None)
    session.pop('user_email', None)
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('loja.index'))

@usuarios_bp.route('/minha-conta')
@login_required
def minha_conta():
    """Página da área do cliente"""
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('usuarios.login'))
    
    # Buscar pedidos do usuário
    pedidos = Pedido.query.filter_by(usuario_id=usuario.id).order_by(Pedido.data_pedido.desc()).all()
    
    return render_template('usuarios/minha_conta.html', usuario=usuario, pedidos=pedidos)

@usuarios_bp.route('/meus-pedidos')
@login_required
def meus_pedidos():
    """Página com histórico de pedidos"""
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('usuarios.login'))
    
    pedidos = Pedido.query.filter_by(usuario_id=usuario.id).order_by(Pedido.data_pedido.desc()).all()
    
    return render_template('usuarios/meus_pedidos.html', usuario=usuario, pedidos=pedidos)

@usuarios_bp.route('/pedido/<int:pedido_id>')
@login_required
def detalhes_pedido(pedido_id):
    """Página com detalhes de um pedido específico"""
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('usuarios.login'))
    
    pedido = Pedido.query.filter_by(id=pedido_id, usuario_id=usuario.id).first()
    if not pedido:
        flash('Pedido não encontrado.', 'error')
        return redirect(url_for('usuarios.meus_pedidos'))
    
    return render_template('usuarios/detalhes_pedido.html', usuario=usuario, pedido=pedido)

@usuarios_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Página para editar dados do perfil"""
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('usuarios.login'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone = request.form.get('telefone', '').strip()
        endereco = request.form.get('endereco', '').strip()
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        # Validações
        if not nome or len(nome) < 2:
            flash('Nome deve ter pelo menos 2 caracteres.', 'error')
            return render_template('usuarios/editar_perfil.html', usuario=usuario)
        
        # Atualizar dados básicos
        usuario.nome = nome
        usuario.telefone = telefone
        usuario.endereco = endereco
        
        # Se forneceu senha atual, verificar e atualizar senha
        if senha_atual:
            if not check_password_hash(usuario.senha_hash, senha_atual):
                flash('Senha atual incorreta.', 'error')
                return render_template('usuarios/editar_perfil.html', usuario=usuario)
            
            if len(nova_senha) < 6:
                flash('Nova senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('usuarios/editar_perfil.html', usuario=usuario)
            
            if nova_senha != confirmar_senha:
                flash('As senhas não coincidem.', 'error')
                return render_template('usuarios/editar_perfil.html', usuario=usuario)
            
            usuario.senha_hash = generate_password_hash(nova_senha)
        
        try:
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('usuarios.minha_conta'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar perfil. Tente novamente.', 'error')
            return render_template('usuarios/editar_perfil.html', usuario=usuario)
    
    return render_template('usuarios/editar_perfil.html', usuario=usuario)

@usuarios_bp.route('/pedido/<int:pedido_id>/cancelar', methods=['POST'])
@login_required
def cancelar_pedido(pedido_id):
    """Cancelar um pedido específico"""
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        session.clear()
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('usuarios.login'))
    
    # Buscar o pedido e verificar se pertence ao usuário
    pedido = Pedido.query.filter_by(id=pedido_id, usuario_id=usuario.id).first()
    if not pedido:
        flash('Pedido não encontrado.', 'error')
        return redirect(url_for('usuarios.meus_pedidos'))
    
    # Verificar se o pedido pode ser cancelado (apenas pendente)
    if pedido.status != 'pendente':
        flash('Este pedido não pode ser cancelado. Apenas pedidos pendentes podem ser cancelados.', 'error')
        return redirect(url_for('usuarios.detalhes_pedido', pedido_id=pedido_id))
    
    try:
        # Cancelar o pedido
        pedido.status = 'cancelado'
        db.session.commit()
        
        flash('Pedido cancelado com sucesso!', 'success')
        return redirect(url_for('usuarios.meus_pedidos'))
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao cancelar pedido. Tente novamente.', 'error')
        return redirect(url_for('usuarios.detalhes_pedido', pedido_id=pedido_id))

# ===== AUTENTICAÇÃO SOCIAL =====

@usuarios_bp.route('/google-login')
def google_login():
    """Iniciar login com Google"""
    # Configurações do Google OAuth
    google_client_id = current_app.config.get('GOOGLE_CLIENT_ID', '')
    redirect_uri = url_for('usuarios.google_callback', _external=True)
    
    if not google_client_id:
        flash('Login com Google não está configurado.', 'error')
        return redirect(url_for('usuarios.login'))
    
    # Parâmetros para autorização do Google
    params = {
        'client_id': google_client_id,
        'redirect_uri': redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return redirect(auth_url)

@usuarios_bp.route('/google-callback')
def google_callback():
    """Callback do Google OAuth"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash('Erro na autenticação com Google.', 'error')
        return redirect(url_for('usuarios.login'))
    
    if not code:
        flash('Código de autorização não recebido.', 'error')
        return redirect(url_for('usuarios.login'))
    
    try:
        # Trocar código por token de acesso
        google_client_id = current_app.config.get('GOOGLE_CLIENT_ID', '')
        google_client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET', '')
        redirect_uri = url_for('usuarios.google_callback', _external=True)
        
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        
        # Obter informações do usuário
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Processar informações do usuário
        email = user_info.get('email')
        nome = user_info.get('name', '')
        google_id = user_info.get('id')
        avatar_url = user_info.get('picture')
        
        if not email:
            flash('Email não fornecido pelo Google.', 'error')
            return redirect(url_for('usuarios.login'))
        
        # Verificar se usuário já existe
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario:
            # Criar novo usuário
            usuario = Usuario(
                nome=nome,
                email=email,
                provider='google',
                provider_id=google_id,
                avatar_url=avatar_url,
                ativo=True
            )
            db.session.add(usuario)
            db.session.commit()
            flash('Conta criada com sucesso usando Google!', 'success')
        else:
            # Atualizar informações do usuário existente
            if not usuario.provider:
                usuario.provider = 'google'
                usuario.provider_id = google_id
                usuario.avatar_url = avatar_url
                db.session.commit()
        
        # Fazer login
        session['user_id'] = usuario.id
        session['user_nome'] = usuario.nome
        session['user_email'] = usuario.email
        
        # Atualizar último login
        from datetime import datetime
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        # Redirecionar
        redirect_url = session.get('redirect_after_login', url_for('loja.index'))
        session.pop('redirect_after_login', None)
        return redirect(redirect_url)
        
    except Exception as e:
        current_app.logger.error(f'Erro no callback do Google: {str(e)}')
        flash('Erro na autenticação com Google. Tente novamente.', 'error')
        return redirect(url_for('usuarios.login'))


