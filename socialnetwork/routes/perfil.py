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

@perfil_bp.route('/perfil_json/<username>')
@login_required
def perfil_json(username):
    """Retorna dados do perfil em JSON"""
    user = Usuario.query_by_username(username)
    if not user:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    seguindo = Seguir.query_by_seguidor(user.id)
    seguidores = Seguir.query_by_seguido(user.id)
    bloqueados = Bloquear.query_bloqueador(user.id)
    
    return jsonify({
        'usuario': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'seguindo': [{'id': s.id_seguido, 'username': Usuario.query_by_id(s.id_seguido).username} for s in seguindo],
            'seguidores': [{'id': s.id_seguidor, 'username': Usuario.query_by_id(s.id_seguidor).username} for s in seguidores],
            'bloqueados': [{'id': b.id_bloqueado, 'username': Usuario.query_by_id(b.id_bloqueado).username} for b in bloqueados],
            'publicacoes': [{'id': p.id} for p in Publicacao.query_by_usuario(user.id)]
        }
    })

@perfil_bp.route('/perfil/<username>')
@login_required
def perfil(username):
    user = Usuario.query_by_username(username)
    if not user:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('feed.topics'))

    seguindo = Seguir.query_by_seguidor(user.id)
    seguidores = Seguir.query_by_seguido(user.id)

    bloqueados_por_user = {b.id_bloqueado for b in Bloquear.query_bloqueador(user.id)}
    bloqueados_por_current = {b.id_bloqueado for b in Bloquear.query_bloqueador(current_user.id)}

    current_user_blocked = current_user.id in bloqueados_por_user
    current_user_is_blocking = user.id in bloqueados_por_current

    publicacoes = []
    if not current_user_blocked:
        for pub in Publicacao.query_by_usuario(user.id):
            if pub.id_usuario in bloqueados_por_current:
                continue

            comentarios_filtrados = []
            for comentario in pub.comentarios:
                if comentario.id_usuario in bloqueados_por_current:
                    continue

                respostas_filtradas = [
                    r for r in comentario.respostas
                    if r.id_usuario not in bloqueados_por_current
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
    user = Usuario.query_by_username(username)
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('feed.topics'))

    if Seguir.query_rel(current_user.id, user.id):
        flash("Você já segue este usuário.", "info")
        return redirect(request.referrer or url_for('feed.topics'))

    if Bloquear.query_rel(current_user.id, user.id):
        flash("Você bloqueou este usuário. Desbloqueie antes de segui-lo.", "error")
        return redirect(request.referrer or url_for('feed.topics'))

    Seguir.create(current_user.id, user.id)
    flash(f"Agora você segue {username}!", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/deixar_de_seguir/<username>')
@login_required
def deixar_de_seguir(username):
    user = Usuario.query_by_username(username)
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('feed.topics'))

    seguir_register = Seguir.query_rel(current_user.id, user.id)
    if seguir_register:
        seguir_register.delete()
        flash(f"Você deixou de seguir {username}.", "info")
    else:
        flash("Você não segue este usuário.", "error")

    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/bloquear/<username>')
@login_required
def bloquear(username):
    usuario = Usuario.query_by_username(username)
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('feed.topics'))

    if Bloquear.query_rel(current_user.id, usuario.id):
        flash("Você já bloqueou este usuário.", "info")
        return redirect(request.referrer or url_for('feed.topics'))

    bloquear_registro = Bloquear.create(current_user.id, usuario.id)

    seguir_registro = Seguir.query_rel(current_user.id, usuario.id)
    if seguir_registro:
        seguir_registro.delete()
    
    seguido_por_ele = Seguir.query_rel(usuario.id, current_user.id)
    if seguido_por_ele:
        seguido_por_ele.delete()

    flash(f"Você bloqueou {username}.", "warning")
    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/desbloquear/<username>')
@login_required
def desbloquear(username):
    usuario = Usuario.query_by_username(username)
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('feed.topics'))

    bloquear_registro = Bloquear.query_rel(current_user.id, usuario.id)
    if bloquear_registro:
        bloquear_registro.delete()
        flash(f"Você desbloqueou {username}.", "success")
    else:
        flash("Este usuário não está bloqueado.", "error")

    return redirect(request.referrer or url_for('feed.topics'))

@perfil_bp.route('/remover_foto_perfil', methods=['POST'])
@login_required
def remover_foto_perfil():
    if current_user.foto_perfil:
        path = os.path.join(current_app.static_folder, 'uploads', current_user.foto_perfil)
        if os.path.exists(path):
            os.remove(path)
        current_user.foto_perfil = None
        current_user.save()

    return '', 204

@perfil_bp.route('/salvar_foto_perfil', methods=['POST'])
@login_required
def salvar_foto_perfil():
    data = request.get_json()
    imagem_base64 = data.get('imagem')
    if not imagem_base64:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400

    import re
    from PIL import Image
    from io import BytesIO

    base64_data = re.sub('^data:image/.+;base64,', '', imagem_base64)
    img_data = base64.b64decode(base64_data)
    img = Image.open(BytesIO(img_data))

    filename = f'user_{current_user.id}_perfil.png'
    path = os.path.join(current_app.static_folder, 'uploads', filename)
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)

    current_user.foto_perfil = filename
    current_user.save()

    url = url_for('static', filename='uploads/' + filename)

    return jsonify({'url': url})

@perfil_bp.route('/seguir_ajax/<username>', methods=['POST'])
@login_required
def seguir_ajax(username):
    user = Usuario.query_by_username(username)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    if Bloquear.query_rel(current_user.id, user.id):
        return jsonify({'error': 'Você bloqueou este usuário.'}), 400

    if not Seguir.query_rel(current_user.id, user.id):
        Seguir.create(current_user.id, user.id)

    return jsonify({
        'status': 'seguindo',
        'quantia_seguidores': user.quantia_seguidores,
        'quantia_seguindo': user.quantia_seguindo
    })

@perfil_bp.route('/deixar_de_seguir_ajax/<username>', methods=['POST'])
@login_required
def deixar_de_seguir_ajax(username):
    user = Usuario.query_by_username(username)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    seguir = Seguir.query_rel(current_user.id, user.id)
    if seguir:
        seguir.delete()

    return jsonify({
        'status': 'nao_seguindo',
        'quantia_seguidores': user.quantia_seguidores,
        'quantia_seguindo': user.quantia_seguindo
    })

@perfil_bp.route('/bloquear_ajax/<username>', methods=['POST'])
@login_required
def bloquear_ajax(username):
    usuario = Usuario.query_by_username(username)
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    if not Bloquear.query_rel(current_user.id, usuario.id):
        Bloquear.create(current_user.id, usuario.id)

        seguir_registro = Seguir.query_rel(current_user.id, usuario.id)
        if seguir_registro:
            seguir_registro.delete()
        
        seguido_por_ele = Seguir.query_rel(usuario.id, current_user.id)
        if seguido_por_ele:
            seguido_por_ele.delete()

    return jsonify({'status': 'bloqueado'})

@perfil_bp.route('/desbloquear_ajax/<username>', methods=['POST'])
@login_required
def desbloquear_ajax(username):
    usuario = Usuario.query_by_username(username)
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    bloquear_registro = Bloquear.query_rel(current_user.id, usuario.id)

    if bloquear_registro:
        bloquear_registro.delete()
        return jsonify({'status': 'desbloqueado'})
    else:
        return jsonify({'error': 'Usuário não está bloqueado'}), 400
