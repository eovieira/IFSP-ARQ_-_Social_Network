from flask import Blueprint, render_template, g
from flask_login import login_required, current_user
from models import Publicacao
from sqlalchemy import case, desc
from user_agents import parse

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/teste')
def teste():
    seguindo_ids = [rel.id_seguido for rel in current_user.seguindo]
    bloqueado_ids = [rel.id_bloqueado for rel in current_user.bloqueados]
    bloqueou_voce_ids = [rel.id_bloqueador for rel in current_user.bloqueado_por]

    prioridade_case = case(
        (Publicacao.id_usuario.in_(seguindo_ids), 0),
        else_=1
    )

    publicacoes = Publicacao.query \
        .filter(~Publicacao.id_usuario.in_(bloqueado_ids)) \
        .filter(~Publicacao.id_usuario.in_(bloqueou_voce_ids)) \
        .order_by(prioridade_case, desc(Publicacao.data_criacao)) \
        .all()

    return render_template('index.html', publicacoes=publicacoes)

@feed_bp.route('/topics')
@login_required
def topics():
    seguindo_ids = [rel.id_seguido for rel in current_user.seguindo]
    bloqueado_ids = [rel.id_bloqueado for rel in current_user.bloqueados]
    bloqueou_voce_ids = [rel.id_bloqueador for rel in current_user.bloqueado_por]

    prioridade_case = case(
        (Publicacao.id_usuario.in_(seguindo_ids), 0),
        else_=1
    )

    publicacoes = Publicacao.query \
        .filter(~Publicacao.id_usuario.in_(bloqueado_ids)) \
        .filter(~Publicacao.id_usuario.in_(bloqueou_voce_ids)) \
        .order_by(prioridade_case, desc(Publicacao.data_criacao)) \
        .all()

    return render_template('topics.html', publicacoes=publicacoes)
