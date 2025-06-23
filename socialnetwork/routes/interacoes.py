from flask import Blueprint, request, redirect, url_for, flash, abort, g, render_template
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
    texto = request.form['texto']
    if texto:
        data_brasilia = datetime.now(brasilia)
        publicacao = Publicacao(texto=texto, usuario_id=current_user.id, data_criacao=data_brasilia)
        db.session.add(publicacao)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/curtir/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def curtir_publicacao(publicacao_id):
    if not Curtida.query.filter_by(id_usuario=current_user.id, id_publicacao=publicacao_id).first():
        nova_curtida = Curtida(id_usuario=current_user.id, id_publicacao=publicacao_id)
        db.session.add(nova_curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/descurtir/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def descurtir_publicacao(publicacao_id):
    curtida = Curtida.query.filter_by(id_usuario=current_user.id, id_publicacao=publicacao_id).first()
    if curtida:
        db.session.delete(curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/comentar/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def comentar_publicacao(publicacao_id):
    texto = request.form.get('texto')
    if not texto:
        abort(400)
    novo_comentario = Comentario(texto=texto, usuario_id=current_user.id, publicacao_id=publicacao_id)
    db.session.add(novo_comentario)
    db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/responder/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def responder_comentario(comentario_id):
    texto = request.form.get('texto')
    if not texto:
        abort(400)
    resposta = Resposta(texto=texto, id_usuario=current_user.id, id_comentario=comentario_id)
    db.session.add(resposta)
    db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/responder/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def responder_resposta(resposta_id):
    texto = request.form.get('texto')
    if not texto:
        abort(400)
    nova_resposta = Resposta(texto=texto, id_usuario=current_user.id, id_resposta=resposta_id)
    db.session.add(nova_resposta)
    db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/curtir/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def curtir_comentario(comentario_id):
    if not Curtida.query.filter_by(id_usuario=current_user.id, id_comentario=comentario_id).first():
        nova_curtida = Curtida(id_usuario=current_user.id, id_comentario=comentario_id)
        db.session.add(nova_curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/descurtir/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def descurtir_comentario(comentario_id):
    curtida = Curtida.query.filter_by(id_usuario=current_user.id, id_comentario=comentario_id).first()
    if curtida:
        db.session.delete(curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/curtir/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def curtir_resposta(resposta_id):
    if not Curtida.query.filter_by(id_usuario=current_user.id, id_resposta=resposta_id).first():
        nova_curtida = Curtida(id_usuario=current_user.id, id_resposta=resposta_id)
        db.session.add(nova_curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/descurtir/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def descurtir_resposta(resposta_id):
    curtida = Curtida.query.filter_by(id_usuario=current_user.id, id_resposta=resposta_id).first()
    if curtida:
        db.session.delete(curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/deletar/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def deletar_publicacao(publicacao_id):
    publicacao = Publicacao.query.get_or_404(publicacao_id)
    if publicacao.id_usuario != current_user.id:
        flash("Você não tem permissão para deletar esta publicação.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    db.session.delete(publicacao)
    db.session.commit()
    flash("Publicação deletada com sucesso.", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/deletar/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def deletar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    if comentario.id_usuario != current_user.id:
        flash("Você não tem permissão para deletar este comentário.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    db.session.delete(comentario)
    db.session.commit()
    flash("Comentário deletado com sucesso.", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/deletar/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def deletar_resposta(resposta_id):
    resposta = Resposta.query.get_or_404(resposta_id)
    if resposta.id_usuario != current_user.id:
        flash("Você não tem permissão para deletar esta resposta.", "error")
        return redirect(request.referrer or url_for('feed.topics'))
    db.session.delete(resposta)
    db.session.commit()
    flash("Resposta deletada com sucesso.", "success")
    return redirect(request.referrer or url_for('feed.topics'))

@interacoes_bp.route('/comentarios/<int:publicacao_id>')
@login_required
def obter_comentarios(publicacao_id):
    publicacao = Publicacao.query.get_or_404(publicacao_id)
    return render_template('partials/comentarios_overlay.html', publicacao=publicacao)
