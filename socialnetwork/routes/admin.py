from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from models import Usuario
from db import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.cargo == 'Administrador':
        return render_template('admin_panel.html')
    else:
        return render_template('index.html', error='Você não tem permissão para isso!')

@admin_bp.route('/usuarios')
def usuarios():
    usuarios = db.session.query(Usuario).all()
    return render_template('utils/users.html', usuarios=usuarios)

@admin_bp.route('/editar_cargo/<int:usuario_id>', methods=['POST'])
@login_required
def editar_cargo(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(request.referrer or url_for('feed.topics'))

    novo_cargo = request.form.get('cargo')
    if novo_cargo:
        usuario.cargo = novo_cargo
        db.session.commit()
        flash(f"Cargo de {usuario.username} alterado para {novo_cargo}.", "success")
    else:
        flash("Cargo não fornecido.", "error")

    return redirect(request.referrer or url_for('feed.topics'))
