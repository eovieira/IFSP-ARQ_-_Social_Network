from flask import Blueprint, render_template, request, redirect, url_for, g
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
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form['usernameForm'].lower()
    senha = request.form['senhaForm']
    user = Usuario.query.filter_by(username=username, senha=hash(senha)).first()
    
    if not user:
        return render_template('login.html', error="Usuário ou senha incorretos.")
    
    login_user(user)
    return redirect(url_for('feed.topics'))

@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')
    
    username = request.form['usernameForm'].lower()
    nome = request.form['nomeForm']
    senha = request.form['senhaForm']
    
    if Usuario.query.filter_by(username=username).first():
        return render_template('registrar.html', error="Nome de usuário em uso.")

    cargo = 'Administrador' if username == 'superadministrador' else 'Usuário'
    novo = Usuario(username=username, nome=nome, senha=hash(senha), cargo=cargo)
    db.session.add(novo)
    db.session.commit()
    login_user(novo)
    return redirect(url_for('feed.topics'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('feed.topics'))