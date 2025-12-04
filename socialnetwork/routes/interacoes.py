from flask import Blueprint, request, redirect, url_for, flash, abort, g, render_template, jsonify
from flask_login import login_required, current_user
from models import Publicacao, Comentario, Resposta, Curtida
from db import db
from datetime import datetime
from pytz import timezone

interacoes_bp = Blueprint('interacoes', __name__, url_prefix='')

brasilia = timezone('America/Sao_Paulo')

@interacoes_bp.route('/adicionar_publicacao', methods=['POST'])
@login_required
def adicionar_publicacao():
    # Suporta tanto JSON quanto form-encoded
    if request.is_json:
        texto = request.get_json().get('texto', '')
    else:
        texto = request.form.get('texto', '')
    
    if not texto.strip():
        if request.is_json:
            return jsonify({'erro': 'Publicação não pode estar vazia'}), 400
        return redirect(request.referrer or url_for('feed.topics'))
    
    data_brasilia = datetime.now(brasilia)
    publicacao = Publicacao.create(texto=texto, usuario_id=current_user.id, data_criacao=data_brasilia)
    
    if request.is_json:
        return jsonify({'status': 'ok', 'publicacao_id': publicacao.id})
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/curtir/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def curtir_publicacao(publicacao_id):
    if not Curtida.query_by_usuario_publicacao(current_user.id, publicacao_id):
        Curtida.create(current_user.id, pub_id=publicacao_id)
    
    if request.is_json:
        return jsonify({'status': 'ok'})
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/descurtir/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def descurtir_publicacao(publicacao_id):
    curtida = Curtida.query_by_usuario_publicacao(current_user.id, publicacao_id)
    if curtida:
        curtida.delete()
    
    if request.is_json:
        return jsonify({'status': 'ok'})
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/comentar/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def comentar_publicacao(publicacao_id):
    # Suporta tanto JSON quanto form-encoded
    texto = request.get_json().get('texto') if request.is_json else request.form.get('texto')
    if not texto:
        abort(400)
    novo_comentario = Comentario.create(texto=texto, usuario_id=current_user.id, publicacao_id=publicacao_id)
    
    # Retorna JSON se foi JSON, senão redireciona
    if request.is_json:
        return {'status': 'ok', 'comentario_id': novo_comentario.id}
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/responder/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def responder_comentario(comentario_id):
    # Suporta tanto JSON quanto form-encoded
    texto = request.get_json().get('texto') if request.is_json else request.form.get('texto')
    if not texto:
        abort(400)
    resposta = Resposta.create(texto=texto, id_usuario=current_user.id, id_comentario=comentario_id)
    
    # Retorna JSON se foi JSON, senão redireciona
    if request.is_json:
        return {'status': 'ok', 'resposta_id': resposta.id}
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/responder/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def responder_resposta(resposta_id):
    # Suporta tanto JSON quanto form-encoded
    texto = request.get_json().get('texto') if request.is_json else request.form.get('texto')
    if not texto:
        abort(400)
    # Para respostas, criamos como respostas normais também (sem nested replies)
    resposta_original = Resposta.query_by_id(resposta_id)
    if resposta_original:
        nova_resposta = Resposta.create(texto=texto, id_usuario=current_user.id, id_comentario=resposta_original.id_comentario)
        if request.is_json:
            return {'status': 'ok', 'resposta_id': nova_resposta.id}
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/curtir/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def curtir_comentario(comentario_id):
    if not Curtida.query_by_usuario_comentario(current_user.id, comentario_id):
        Curtida.create(current_user.id, com_id=comentario_id)
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/descurtir/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def descurtir_comentario(comentario_id):
    curtida = Curtida.query_by_usuario_comentario(current_user.id, comentario_id)
    if curtida:
        curtida.delete()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/curtir/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def curtir_resposta(resposta_id):
    if not Curtida.query_by_usuario_resposta(current_user.id, resposta_id):
        Curtida.create(current_user.id, resp_id=resposta_id)
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/descurtir/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def descurtir_resposta(resposta_id):
    curtida = Curtida.query_by_usuario_resposta(current_user.id, resposta_id)
    if curtida:
        curtida.delete()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/deletar/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def deletar_publicacao(publicacao_id):
    publicacao = Publicacao.query_by_id(publicacao_id)
    if not publicacao:
        if request.is_json:
            return jsonify({'erro': 'Publicação não encontrada'}), 404
        flash("Publicação não encontrada.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    
    if publicacao.id_usuario != current_user.id:
        if request.is_json:
            return jsonify({'erro': 'Sem permissão'}), 403
        flash("Você não tem permissão para deletar esta publicação.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    
    publicacao.delete()
    
    if request.is_json:
        return jsonify({'status': 'ok'})
    flash("Publicação deletada com sucesso.", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/deletar/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def deletar_comentario(comentario_id):
    comentario = Comentario.query_by_id(comentario_id)
    if not comentario:
        if request.is_json:
            return jsonify({'erro': 'Comentário não encontrado'}), 404
        flash("Comentário não encontrado.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    
    if comentario.id_usuario != current_user.id:
        if request.is_json:
            return jsonify({'erro': 'Sem permissão'}), 403
        flash("Você não tem permissão para deletar este comentário.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    
    comentario.delete()
    
    if request.is_json:
        return jsonify({'status': 'ok'})
    flash("Comentário deletado com sucesso.", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/deletar/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def deletar_resposta(resposta_id):
    resposta = Resposta.query_by_id(resposta_id)
    if not resposta:
        if request.is_json:
            return jsonify({'erro': 'Resposta não encontrada'}), 404
        flash("Resposta não encontrada.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    
    if resposta.id_usuario != current_user.id:
        if request.is_json:
            return jsonify({'erro': 'Sem permissão'}), 403
        flash("Você não tem permissão para deletar esta resposta.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    
    resposta.delete()
    
    if request.is_json:
        return jsonify({'status': 'ok'})
    flash("Resposta deletada com sucesso.", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/comentarios/<int:publicacao_id>')
@login_required
def obter_comentarios(publicacao_id):
    publicacao = Publicacao.query_by_id(publicacao_id)
    if not publicacao:
        abort(404)
    return render_template('partials/comentarios_overlay.html', publicacao=publicacao)
