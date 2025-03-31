from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, login_remembered, logout_user, current_user
from models import Usuario, Seguir, Bloquear
from db import db
import hashlib
import sqlite3

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

@app.route('/usuarios')
def usuarios():
    usuarios = db.session.query(Usuario).all()
    return render_template('utils/users.html', usuarios=usuarios)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['usernameForm'].lower()
        senha = request.form['senhaForm']
        
        user = db.session.query(Usuario).filter_by(username=username, senha=hash(senha)).first()
        if not user:
            return render_template('login.html', error="Usuário ou senha incorretos, tente novamente!")
        
        login_user(user)
        return redirect(url_for('home'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')
    elif request.method == 'POST':
        username = request.form['usernameForm'].lower()
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        usuario_existente = db.session.query(Usuario).filter_by(username=username).first()
        if usuario_existente:
            return render_template('registrar.html', error="Este nome de usuário já está em uso, tente outro!")
        if username == 'superadministrador':
            novo_usuario = Usuario(username=username, nome=nome, senha=hash(senha), cargo='Administrador')
        else:
            novo_usuario = Usuario(username=username, nome=nome, senha=hash(senha), cargo='Usuário')
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
        return render_template('index.html', error='Você não tem permissão para isso!')

@app.route('/bloquear/<username>')
@login_required
def bloquear(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('index'))

    if current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first():
        flash("Você já bloqueou este usuário.", "info")
        return redirect(url_for('perfil', username=username))

    bloquear_registro = Bloquear(id_bloqueador=current_user.id, id_bloqueado=usuario.id)
    
    # Remover o follow caso exista
    seguir_registro = current_user.seguindo.filter_by(id_seguido=usuario.id).first()
    if seguir_registro:
        db.session.delete(seguir_registro)

    db.session.add(bloquear_registro)
    db.session.commit()
    flash(f"Você bloqueou {username}.", "warning")
    return redirect(url_for('perfil', username=username))


@app.route('/desbloquear/<username>')
@login_required
def desbloquear(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('index'))

    bloquear_registro = current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first()
    if bloquear_registro:
        db.session.delete(bloquear_registro)
        db.session.commit()
        flash(f"Você desbloqueou {username}.", "success")
    else:
        flash("Este usuário não está bloqueado.", "error")

    return redirect(url_for('perfil', username=username))

@app.route('/seguir/<username>')
@login_required
def seguir(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for(home))
    if current_user.seguindo.filter_by(id_seguido=user.id).first():
        flash("Você já segue este usuário.", "info")
        return redirect(url_for('perfil', username=username))
    if current_user.bloqueados.filter_by(id_bloqueado=user.id).first():
        flash("Você bloqueou este usuário. Desbloqueie antes de segui-lo.", "error")
        return redirect(url_for('perfil', username=username))
    seguir_register = Seguir(id_seguidor=current_user.id, id_seguido=user.id)
    db.session.add(seguir_register)
    db.session.commit()
    flash(f"Agora você segue {username}!", "success")
    return redirect(url_for('perfil', username=username))

@app.route('/deixar_de_seguir/<username>')
@login_required
def deixar_de_seguir(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for(home))
    seguir_register = current_user.seguindo.filter_by(id_seguido=user.id).first()
    if seguir_register:
        db.session.delete(seguir_register)
        db.session.commit()
        flash(f"Você deixou de seguir {username}.", "info")
    else:
        flash("Você não segue este usuário.", "error")
    return redirect(url_for('perfil', username=username))

@app.route('/perfil/<username>')
@login_required
def perfil(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('home'))
    seguindo = Usuario.query.join(Seguir, Seguir.id_seguido == Usuario.id).filter(Seguir.id_seguidor == user.id).all()
    
    return render_template('utils/perfil.html', user=user, seguindo=seguindo)

@app.route('/seguir/<int:id_usuario>', methods=['POST'])
@login_required
def seguir_usuario(id_usuario):
    usuario_a_seguir = Usuario.query.get(id_usuario)

    if not usuario_a_seguir:
        flash("Usuário não encontrado!", "error")
        return redirect(url_for('home'))

    ja_seguindo = Seguir.query.filter_by(id_seguidor=current_user.id, id_seguido=id_usuario).first()

    if ja_seguindo:
        db.session.delete(ja_seguindo)
        db.session.commit()
        flash(f"Você parou de seguir {usuario_a_seguir.username}.", "info")
    else:
        novo_seguimento = Seguir(id_seguidor=current_user.id, id_seguido=id_usuario)
        db.session.add(novo_seguimento)
        db.session.commit()
        flash(f"Você agora está seguindo {usuario_a_seguir.username}!", "success")

    # Alterar para usar 'username' em vez de 'id_usuario'
    return redirect(url_for('perfil', username=usuario_a_seguir.username))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)