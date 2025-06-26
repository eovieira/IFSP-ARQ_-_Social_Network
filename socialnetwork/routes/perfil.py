from flask import Blueprint, render_template, redirect, url_for, flash, request, g, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Usuario, Publicacao, Seguir, Bloquear
from db import db
import os
import base64
from PIL import Image
from io import BytesIO

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/perfil/<username>')
@login_required
def perfil(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('feed.topics'))

    seguindo = user.seguindo.all()
    seguidores = user.seguidores.all()

    bloqueados_por_user = {u.id for u in user.bloqueados.all()}
    bloqueados_por_current = {u.id for u in current_user.bloqueados.all()}

    current_user_blocked = current_user.id in bloqueados_por_user
    current_user_is_blocking = user.id in bloqueados_por_current

    publicacoes = []
    if not current_user_blocked:
        for pub in user.publicacoes:
            if pub.usuario.id in bloqueados_por_current:
                continue

            comentarios_filtrados = []
            for comentario in pub.comentarios:
                if comentario.usuario.id in bloqueados_por_current:
                    continue

                respostas_filtradas = [
                    r for r in comentario.respostas
                    if r.usuario.id not in bloqueados_por_current
                ]
                comentario.respostas = respostas_filtradas
                comentarios_filtrados.append(comentario)

            pub.comentarios = comentarios_filtrados
            publicacoes.append(pub)

    return render_template('utils/perfil.html', user=user, seguindo=seguindo, seguidores=seguidores,
                           quantia_seguidores=user.quantia_seguidores,
                           quantia_seguindo=user.quantia_seguindo,
                           current_user_blocked=current_user_blocked,
                           current_user_is_blocking=current_user_is_blocking,
                           publicacoes=publicacoes)

@perfil_bp.route('/seguir/<username>')
@login_required
def seguir(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('feed.topics'))

    if current_user.seguindo.filter_by(id_seguido=user.id).first():
        flash("Você já segue este usuário.", "info")
        return redirect(request.referrer or url_for('feed.topics'))

    if current_user.bloqueados.filter_by(id_bloqueado=user.id).first():
        flash("Você bloqueou este usuário. Desbloqueie antes de segui-lo.", "error")
        return redirect(request.referrer or url_for('feed.topics'))

    seguir_register = Seguir(id_seguidor=current_user.id, id_seguido=user.id)
    db.session.add(seguir_register)
    db.session.commit()
    flash(f"Agora você segue {username}!", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/deixar_de_seguir/<username>')
@login_required
def deixar_de_seguir(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('feed.topics'))

    seguir_register = current_user.seguindo.filter_by(id_seguido=user.id).first()
    if seguir_register:
        db.session.delete(seguir_register)
        db.session.commit()
        flash(f"Você deixou de seguir {username}.", "info")
    else:
        flash("Você não segue este usuário.", "error")

    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/bloquear/<username>')
@login_required
def bloquear(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('feed.topics'))

    if current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first():
        flash("Você já bloqueou este usuário.", "info")
        return redirect(request.referrer or url_for('feed.topics'))

    bloquear_registro = Bloquear(id_bloqueador=current_user.id, id_bloqueado=usuario.id)

    seguir_registro = current_user.seguindo.filter_by(id_seguido=usuario.id).first()
    if seguir_registro:
        db.session.delete(seguir_registro)
    seguido_por_ele = usuario.seguindo.filter_by(id_seguido=current_user.id).first()
    if seguido_por_ele:
        db.session.delete(seguido_por_ele)

    db.session.add(bloquear_registro)
    db.session.commit()
    flash(f"Você bloqueou {username}.", "warning")
    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/desbloquear/<username>')
@login_required
def desbloquear(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('feed.topics'))

    bloquear_registro = current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first()
    if bloquear_registro:
        db.session.delete(bloquear_registro)
        db.session.commit()
        flash(f"Você desbloqueou {username}.", "success")
    else:
        flash("Este usuário não está bloqueado.", "error")

    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/remover_foto_perfil', methods=['POST'])
@login_required
def remover_foto_perfil():
    # Remova o arquivo se existir
    import os

    if current_user.foto_perfil:
        path = os.path.join(current_app.static_folder, 'uploads', current_user.foto_perfil)
        if os.path.exists(path):
            os.remove(path)
        current_user.foto_perfil = None
        db.session.commit()

    return '', 204

@perfil_bp.route('/salvar_foto_perfil', methods=['POST'])
@login_required
def salvar_foto_perfil():
    data = request.get_json()
    imagem_base64 = data.get('imagem')
    if not imagem_base64:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400

    # Decodifique a imagem base64, salve em arquivo e atualize o usuário
    import base64
    import os
    from PIL import Image
    from io import BytesIO
    import re

    # Extraia dados base64 puro
    base64_data = re.sub('^data:image/.+;base64,', '', imagem_base64)
    img_data = base64.b64decode(base64_data)
    img = Image.open(BytesIO(img_data))

    # Salve a imagem (exemplo: static/uploads/user_{id}.png)
    filename = f'user_{current_user.id}_perfil.png'
    path = os.path.join(current_app.static_folder, 'uploads', filename)
    img.save(path)

    # Atualize o campo do usuário
    current_user.foto_perfil = filename
    db.session.commit()

    url = url_for('static', filename='uploads/' + filename)

    return jsonify({'url': url})

@perfil_bp.route('/seguir_ajax/<username>', methods=['POST'])
@login_required
def seguir_ajax(username):
    user = Usuario.query.filter_by(username=username).first_or_404()

    if current_user.bloqueados.filter_by(id_bloqueado=user.id).first():
        return jsonify({'error': 'Você bloqueou este usuário.'}), 400

    if not current_user.seguindo.filter_by(id_seguido=user.id).first():
        db.session.add(Seguir(id_seguidor=current_user.id, id_seguido=user.id))
        db.session.commit()

    return jsonify({
        'status': 'seguindo',
        'quantia_seguidores': user.quantia_seguidores,
        'quantia_seguindo': user.quantia_seguindo
    })

@perfil_bp.route('/deixar_de_seguir_ajax/<username>', methods=['POST'])
@login_required
def deixar_de_seguir_ajax(username):
    user = Usuario.query.filter_by(username=username).first_or_404()
    seguir = current_user.seguindo.filter_by(id_seguido=user.id).first()
    if seguir:
        db.session.delete(seguir)
        db.session.commit()

    return jsonify({
        'status': 'nao_seguindo',
        'quantia_seguidores': user.quantia_seguidores,
        'quantia_seguindo': user.quantia_seguindo
    })

@perfil_bp.route('/bloquear_ajax/<username>', methods=['POST'])
@login_required
def bloquear_ajax(username):
    usuario = Usuario.query.filter_by(username=username).first_or_404()

    if not current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first():
        bloquear_registro = Bloquear(id_bloqueador=current_user.id, id_bloqueado=usuario.id)

        seguir_registro = current_user.seguindo.filter_by(id_seguido=usuario.id).first()
        if seguir_registro:
            db.session.delete(seguir_registro)
        seguido_por_ele = usuario.seguindo.filter_by(id_seguido=current_user.id).first()
        if seguido_por_ele:
            db.session.delete(seguido_por_ele)

        db.session.add(bloquear_registro)
        db.session.commit()

    return jsonify({'status': 'bloqueado'})

@perfil_bp.route('/desbloquear_ajax/<username>', methods=['POST'])
@login_required
def desbloquear_ajax(username):
    usuario = Usuario.query.filter_by(username=username).first_or_404()
    bloquear_registro = current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first()

    if bloquear_registro:
        db.session.delete(bloquear_registro)
        db.session.commit()
        return jsonify({'status': 'desbloqueado'})
    else:
        return jsonify({'error': 'Usuário não está bloqueado'}), 400
