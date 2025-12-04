from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Publicacao, Comentario, Resposta
from datetime import datetime

comentarios_json_bp = Blueprint('comentarios_json', __name__)

@comentarios_json_bp.route('/comentarios/<int:publicacao_id>')
@login_required
def obter_comentarios(publicacao_id):
    """Retorna comentários de uma publicação em JSON"""
    publicacao = Publicacao.query_by_id(publicacao_id)
    
    if not publicacao:
        return jsonify({'erro': 'Publicação não encontrada'}), 404
    
    comentarios = []
    for com in publicacao.comentarios:
        respostas = []
        for res in com.respostas:
            respostas.append({
                'id': res.id,
                'texto': res.texto,
                'data_criacao': res.data_criacao,
                'usuario_id': res.id_usuario,
                'usuario': {
                    'id': res.usuario.id,
                    'username': res.usuario.username,
                    'email': res.usuario.email
                } if res.usuario else None
            })
        
        comentarios.append({
            'id': com.id,
            'texto': com.texto,
            'data_criacao': com.data_criacao,
            'usuario_id': com.id_usuario,
            'usuario': {
                'id': com.usuario.id,
                'username': com.usuario.username,
                'email': com.usuario.email
            } if com.usuario else None,
            'respostas': respostas
        })
    
    return jsonify({'comentarios': comentarios})

@comentarios_json_bp.route('/perfil/<username>/publicacoes_json')
@login_required
def perfil_publicacoes_json(username):
    """Retorna publicações de um perfil em JSON"""
    from models import Usuario
    
    user = Usuario.query_by_username(username)
    if not user:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    
    publicacoes = []
    for pub in Publicacao.query_by_usuario(user.id):
        comentarios = []
        for com in pub.comentarios:
            respostas = []
            for res in com.respostas:
                respostas.append({
                    'id': res.id,
                    'texto': res.texto,
                    'data_criacao': res.data_criacao,
                    'usuario_id': res.id_usuario,
                    'usuario': {
                        'id': res.usuario.id,
                        'username': res.usuario.username,
                        'email': res.usuario.email
                    } if res.usuario else None
                })
            
            comentarios.append({
                'id': com.id,
                'texto': com.texto,
                'data_criacao': com.data_criacao,
                'usuario_id': com.id_usuario,
                'usuario': {
                    'id': com.usuario.id,
                    'username': com.usuario.username,
                    'email': com.usuario.email
                } if com.usuario else None,
                'respostas': respostas
            })
        
        publicacoes.append({
            'id': pub.id,
            'texto': pub.texto,
            'data_criacao': pub.data_criacao,
            'usuario_id': pub.id_usuario,
            'usuario': {
                'id': pub.usuario.id,
                'username': pub.usuario.username,
                'email': pub.usuario.email
            } if pub.usuario else None,
            'comentarios': comentarios
        })
    
    return jsonify({'publicacoes': publicacoes})
