from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from models import Usuario
from db import db
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash(texto):
    import hashlib
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # GET - renderizar página
    if request.method == 'GET':
        device = getattr(g, 'device', 'unknown')
        return render_template('login.html', device=device)
    
    # POST - processar login
    if request.is_json:
        data = request.get_json()
        username = data.get('username', '').lower()
        password = data.get('password', '')
    else:
        username = request.form.get('usernameForm', '').lower()
        password = request.form.get('senhaForm', '')
    
    user = Usuario.query_by_username(username)
    
    if not user or user.senha != hash(password):
        if request.is_json:
            return jsonify({'erro': 'Usuário ou senha inválidos'}), 401
        device = getattr(g, 'device', 'unknown')
        return render_template('login.html', device=device, error='Usuário ou senha inválidos')
    
    login_user(user)
    
    # Retornar JSON ou redirecionar
    if request.is_json:
        return jsonify({
            'usuario': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return redirect(url_for('feed.topics'))

@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    # GET - renderizar página
    if request.method == 'GET':
        device = getattr(g, 'device', 'unknown')
        if device == 'desktop':
            return render_template('login.html', device=device)
        return render_template('registrar.html', device=device)
    
    # POST - processar registro
    if request.is_json:
        data = request.get_json()
        username = data.get('username', '').lower()
        email = data.get('email', '')
        password = data.get('password', '')
    else:
        username = request.form.get('usernameForm', '').lower()
        email = request.form.get('emailForm', '')
        password = request.form.get('senhaForm', '')
    
    if Usuario.query_by_username(username):
        if request.is_json:
            return jsonify({'erro': 'Nome de usuário em uso'}), 409
        device = getattr(g, 'device', 'unknown')
        return render_template('registrar.html', error='Nome de usuário em uso.', device=device)
    
    novo = Usuario.create(username=username, email=email, nome=username, senha=hash(password), cargo='Usuário')
    login_user(novo)
    
    if request.is_json:
        return jsonify({
            'usuario': {
                'id': novo.id,
                'username': novo.username,
                'email': novo.email
            }
        })
    
    return redirect(url_for('feed.topics'))

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    
    if request.is_json:
        return jsonify({'status': 'ok'})
    
    return redirect(url_for('feed.topics'))

@auth_bp.route('/usuario_atual_json')
def usuario_atual_json():
    """Retorna dados do usuário logado ou erro"""
    if current_user.is_authenticated:
        return jsonify({
            'usuario': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        })
    return jsonify({'erro': 'Não autenticado'}), 401