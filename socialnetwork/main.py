from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, login_remembered, logout_user, current_user
from models import Usuario
from db import db
import hashlib

app = Flask(__name__)
app.secret_key = 'b1b39f3b13f4d82f957ee82b2aff10ae7d5903aa1ab6baa6c77664f667dde823'
lm = LoginManager(app)
lm.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader
def user_loader(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not user:
            return render_template('login.html', error="Usuário ou senha incorretos, tente novamente!")
        
        login_user(user)
        return redirect(url_for('home'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        usuario_existente = db.session.query(Usuario).filter_by(nome=nome).first()
        if usuario_existente:
            return render_template('registrar.html', error="Este nome de usuário já está em uso, tente outro!")
        if nome == 'SuperAdministrador':
            novo_usuario = Usuario(nome=nome, senha=hash(senha), cargo='Administrador')
        else:
            novo_usuario = Usuario(nome=nome, senha=hash(senha), cargo='Usuário')
        db.session.add(novo_usuario)
        db.session.commit()
        
        login_user(novo_usuario)
        
        return redirect(url_for('home'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
    
@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.cargo == 'Administrador':
        return render_template('admin_panel.html')
    else:
        return render_template('home.html', error='Você não tem permissão para isso!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)