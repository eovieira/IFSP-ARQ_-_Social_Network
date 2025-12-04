from flask import Blueprint, render_template, g, jsonify
from flask_login import login_required, current_user
from models import Publicacao, Seguir, Bloquear
from datetime import datetime

feed_bp = Blueprint('feed', __name__)

def _obter_publicacoes_filtradas():
    """Obtém publicações filtradas por bloqueios"""
    # Se usuário não autenticado, retorna todas as publicações
    if not current_user.is_authenticated:
        return Publicacao.query_all()
    
    seguindo_ids = [rel.id_seguido for rel in Seguir.query_by_seguidor(current_user.id)]
    bloqueado_ids = [rel.id_bloqueado for rel in Bloquear.query_bloqueador(current_user.id)]
    bloqueou_voce_ids = [rel.id_bloqueador for rel in Bloquear.query_bloqueado(current_user.id)]

    publicacoes = []
    for pub in Publicacao.query_all():
        if pub.id_usuario not in bloqueado_ids and pub.id_usuario not in bloqueou_voce_ids:
            publicacoes.append(pub)

    # Ordena com prioridade (seguindo primeiro, depois por data)
    publicacoes.sort(key=lambda p: (
        0 if p.id_usuario in seguindo_ids else 1,
        -datetime.fromisoformat(p.data_criacao).timestamp() if isinstance(p.data_criacao, str) else -p.data_criacao.timestamp()
    ))
    
    return publicacoes

def _serializar_publicacao(pub):
    """Converte publicação para dicionário JSON"""
    return {
        'id': pub.id,
        'texto': pub.texto,
        'data_criacao': pub.data_criacao,
        'usuario_id': pub.id_usuario,
        'usuario': {
            'id': pub.usuario.id,
            'username': pub.usuario.username,
            'email': pub.usuario.email
        } if pub.usuario else None,
        'comentarios': [_serializar_comentario(com) for com in pub.comentarios],
        'curtidas': len([c for c in pub.comentarios if c]) if hasattr(pub, 'comentarios') else 0
    }

def _serializar_comentario(com):
    """Converte comentário para dicionário JSON"""
    return {
        'id': com.id,
        'texto': com.texto,
        'data_criacao': com.data_criacao,
        'usuario_id': com.id_usuario,
        'usuario': {
            'id': com.usuario.id,
            'username': com.usuario.username,
            'email': com.usuario.email
        } if com.usuario else None,
        'respostas': [_serializar_resposta(res) for res in com.respostas]
    }

def _serializar_resposta(res):
    """Converte resposta para dicionário JSON"""
    return {
        'id': res.id,
        'texto': res.texto,
        'data_criacao': res.data_criacao,
        'usuario_id': res.id_usuario,
        'usuario': {
            'id': res.usuario.id,
            'username': res.usuario.username,
            'email': res.usuario.email
        } if res.usuario else None
    }

@feed_bp.route('/teste')
def teste():
    publicacoes = _obter_publicacoes_filtradas()
    return render_template('index.html', publicacoes=publicacoes)

@feed_bp.route('/topics')
@login_required
def topics():
    publicacoes = _obter_publicacoes_filtradas()
    return render_template('topics.html', publicacoes=publicacoes)

@feed_bp.route('/publicacoes_json')
def publicacoes_json():
    """Retorna lista de publicações em JSON"""
    publicacoes = _obter_publicacoes_filtradas()
    return jsonify({
        'publicacoes': [_serializar_publicacao(pub) for pub in publicacoes]
    })
