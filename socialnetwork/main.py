from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, login_remembered, logout_user, current_user
from models import Usuario, Publicacao, Curtida, Comentario, Bloquear, Seguir, Resposta
from sqlalchemy import case, desc
from db import db
import hashlib
import sqlite3
from datetime import datetime
from pytz import timezone

brasilia = timezone('America/Sao_Paulo')

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
@login_required
def home():
    if current_user.is_authenticated:
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
    else:
        publicacoes = Publicacao.query \
            .order_by(desc(Publicacao.data_criacao)) \
            .all()

    return render_template('index.html', publicacoes=publicacoes)

@app.route('/topics')
@login_required
def topics():
    if current_user.is_authenticated:
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
    else:
        publicacoes = Publicacao.query \
            .order_by(desc(Publicacao.data_criacao)) \
            .all()

    return render_template('topics.html', publicacoes=publicacoes)

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
        return redirect(request.referrer or url_for('home'))


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
    return redirect(request.referrer or url_for('home'))



@app.route('/desbloquear/<username>')
@login_required
def desbloquear(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        flash("Usuário não encontrado", "error")
        return redirect(url_for(home))

    bloquear_registro = current_user.bloqueados.filter_by(id_bloqueado=usuario.id).first()
    if bloquear_registro:
        db.session.delete(bloquear_registro)
        db.session.commit()
        flash(f"Você desbloqueou {username}.", "success")
    else:
        flash("Este usuário não está bloqueado.", "error")

    return redirect(request.referrer or url_for('home'))


@app.route('/seguir/<username>')
@login_required
def seguir(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for(home))
    if current_user.seguindo.filter_by(id_seguido=user.id).first():
        flash("Você já segue este usuário.", "info")
        return redirect(request.referrer or url_for('home'))

    if current_user.bloqueados.filter_by(id_bloqueado=user.id).first():
        flash("Você bloqueou este usuário. Desbloqueie antes de segui-lo.", "error")
        return redirect(request.referrer or url_for('home'))

    seguir_register = Seguir(id_seguidor=current_user.id, id_seguido=user.id)
    db.session.add(seguir_register)
    db.session.commit()
    flash(f"Agora você segue {username}!", "success")
    return redirect(request.referrer or url_for('home'))


@app.route('/deixar_de_seguir/<username>', methods=['GET', 'POST'])
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
    return redirect(request.referrer or url_for('home'))


@app.route('/perfil/<username>')
@login_required
def perfil(username):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        flash("Usuário não encontrado", "error")
        return redirect(url_for('home'))

    seguindo = user.seguindo.all()
    seguidores = user.seguidores.all()

    # Lista de usuários bloqueados por quem está sendo visitado
    bloqueados_por_user = {u.id for u in user.bloqueados.all()}
    # Lista de usuários que o usuário atual bloqueou
    bloqueados_por_current = {u.id for u in current_user.bloqueados.all()}

    current_user_blocked = current_user.id in bloqueados_por_user
    current_user_is_blocking = user.id in bloqueados_por_current

    publicacoes = []

    if not current_user_blocked:
        for pub in user.publicacoes:
            # Oculta publicações se o autor bloqueou o usuário atual
            if pub.usuario.id in bloqueados_por_current:
                continue

            # Cria cópias filtradas dos comentários e respostas
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

    return render_template(
        'utils/perfil.html',
        user=user,
        seguindo=seguindo,
        seguidores=seguidores,
        quantia_seguidores=user.quantia_seguidores,
        quantia_seguindo=user.quantia_seguindo,
        current_user_blocked=current_user_blocked,
        current_user_is_blocking=current_user_is_blocking,
        publicacoes=publicacoes
    )


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

@app.route('/adicionar_publicacao', methods=['POST'])
@login_required
def adicionar_publicacao():
    texto = request.form['texto']
    if texto:
        data_brasilia = datetime.now(brasilia)
        publicacao = Publicacao(texto=texto, usuario_id=current_user.id, data_criacao=data_brasilia)
        db.session.add(publicacao)
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

# Curtir publicação
@app.route('/curtir/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def curtir_publicacao(publicacao_id):
    publicacao = Publicacao.query.get_or_404(publicacao_id)
    curtida_existente = Curtida.query.filter_by(id_usuario=current_user.id, id_publicacao=publicacao_id).first()
    if not curtida_existente:
        nova_curtida = Curtida(id_usuario=current_user.id, id_publicacao=publicacao_id)
        db.session.add(nova_curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

# Descurtir publicação
@app.route('/descurtir/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def descurtir_publicacao(publicacao_id):
    curtida = Curtida.query.filter_by(id_usuario=current_user.id, id_publicacao=publicacao_id).first()
    if curtida:
        db.session.delete(curtida)
        db.session.commit()
    publicacao = Publicacao.query.get_or_404(publicacao_id)
    return redirect(request.referrer or url_for('home'))

@app.route('/deletar/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def deletar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)

    if comentario.id_usuario != current_user.id:
        flash("Você não tem permissão para deletar este comentário.", "error")
        return redirect(request.referrer or url_for('index'))

    db.session.delete(comentario)
    db.session.commit()
    flash("Comentário deletado com sucesso.", "success")
    return redirect(request.referrer or url_for('index'))

@app.route('/deletar/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def deletar_resposta(resposta_id):
    resposta = Resposta.query.get_or_404(resposta_id)

    if resposta.id_usuario != current_user.id:
        flash("Você não tem permissão para deletar esta resposta.", "error")
        return redirect(request.referrer or url_for('index'))

    db.session.delete(resposta)
    db.session.commit()
    flash("Resposta deletada com sucesso.", "success")
    return redirect(request.referrer or url_for('index'))

# Curtir comentário
@app.route('/curtir/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def curtir_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    curtida_existente = Curtida.query.filter_by(id_usuario=current_user.id, id_comentario=comentario_id).first()
    if not curtida_existente:
        nova_curtida = Curtida(id_usuario=current_user.id, id_comentario=comentario_id)
        db.session.add(nova_curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

# Descurtir comentário
@app.route('/descurtir/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def descurtir_comentario(comentario_id):
    curtida = Curtida.query.filter_by(id_usuario=current_user.id, id_comentario=comentario_id).first()
    if curtida:
        db.session.delete(curtida)
        db.session.commit()
    comentario = Comentario.query.get_or_404(comentario_id)
    return redirect(request.referrer or url_for('home'))

# Comentar publicação
@app.route('/comentar/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def comentar_publicacao(publicacao_id):
    texto = request.form.get('texto')
    if not texto:
        abort(400)
    publicacao = Publicacao.query.get_or_404(publicacao_id)
    novo_comentario = Comentario(texto=texto, usuario_id=current_user.id, publicacao_id=publicacao.id)
    db.session.add(novo_comentario)
    db.session.commit()
    return redirect(request.referrer or url_for('home'))


# Responder comentário
@app.route('/responder/comentario/<int:comentario_id>', methods=['POST'])
@login_required
def responder_comentario(comentario_id):
    texto = request.form.get('texto')
    if not texto:
        abort(400)
    comentario = Comentario.query.get_or_404(comentario_id)
    resposta = Resposta(texto=texto, id_usuario=current_user.id, id_comentario=comentario.id)
    db.session.add(resposta)
    db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/deletar/publicacao/<int:publicacao_id>', methods=['POST'])
@login_required
def deletar_publicacao(publicacao_id):
    publicacao = Publicacao.query.get_or_404(publicacao_id)
    
    if publicacao.id_usuario != current_user.id:
        flash("Você não tem permissão para deletar esta publicação.", "error")
        return redirect(request.referrer or url_for('home'))

    db.session.delete(publicacao)
    db.session.commit()
    flash("Publicação deletada com sucesso.", "success")
    return redirect(request.referrer or url_for('home'))

@app.route('/curtir/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def curtir_resposta(resposta_id):
    resposta = Resposta.query.get_or_404(resposta_id)
    curtida_existente = Curtida.query.filter_by(id_usuario=current_user.id, id_resposta=resposta_id).first()
    if not curtida_existente:
        nova_curtida = Curtida(id_usuario=current_user.id, id_resposta=resposta_id)
        db.session.add(nova_curtida)
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/descurtir/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def descurtir_resposta(resposta_id):
    curtida = Curtida.query.filter_by(id_usuario=current_user.id, id_resposta=resposta_id).first()
    if curtida:
        db.session.delete(curtida)
        db.session.commit()
    resposta = Resposta.query.get_or_404(resposta_id)
    return redirect(request.referrer or url_for('home'))

@app.route('/responder/resposta/<int:resposta_id>', methods=['POST'])
@login_required
def responder_resposta(resposta_id):
    texto = request.form.get('texto')
    if not texto:
        abort(400)  # Caso não haja texto na resposta, retorna erro 400
    resposta = Resposta.query.get_or_404(resposta_id)
    nova_resposta = Resposta(texto=texto, id_usuario=current_user.id, id_resposta=resposta.id)
    db.session.add(nova_resposta)
    db.session.commit()
    return redirect(request.referrer or url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)