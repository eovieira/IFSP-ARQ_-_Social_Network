from db import db
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    nome = db.Column(db.String())
    senha = db.Column(db.String())
    cargo = db.Column(db.String())
    
    seguindo = db.relationship(
        'Seguir',
        foreign_keys='Seguir.id_seguidor',
        backref='seguidor',
        lazy='dynamic'
    )

    seguidores = db.relationship(
        'Seguir',
        foreign_keys='Seguir.id_seguido',
        backref='seguido',
        lazy='dynamic'
    )

    bloqueados = db.relationship(
        'Bloquear',
        foreign_keys='Bloquear.id_bloqueador',
        backref='bloqueador',
        lazy='dynamic'
    )

    bloqueado_por = db.relationship(
        'Bloquear',
        foreign_keys='Bloquear.id_bloqueado',
        backref='bloqueado',
        lazy='dynamic'
    )
    
    def curtiu(self, item):
        if isinstance(item, Publicacao):
            return Curtida.query.filter_by(id_usuario=self.id, id_publicacao=item.id).first() is not None
        elif isinstance(item, Comentario):
            return Curtida.query.filter_by(id_usuario=self.id, id_comentario=item.id).first() is not None
        elif isinstance(item, Resposta):
            return Curtida.query.filter_by(id_usuario=self.id, id_resposta=item.id).first() is not None
        return False
    
    @property
    def quantia_seguidores(self):
        return self.seguidores.count()
    @property
    def quantia_seguindo(self):
        return self.seguindo.count()


class Seguir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_seguidor = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_seguido = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
class Bloquear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_bloqueador = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_bloqueado = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
class Publicacao(db.Model):
    __tablename__ = 'publicacao'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref='publicacoes', lazy=True)
    comentarios = db.relationship(
    'Comentario',
    backref='comentarios_publicacao',
    lazy=True,
    cascade='all, delete-orphan'
    )

    curtidas = db.relationship(
        'Curtida',
        backref='publicacao',
        lazy=True,
        cascade='all, delete-orphan'
    )
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, texto, usuario_id, data_criacao=None):
        self.texto = texto
        self.id_usuario = usuario_id
        self.data_criacao = data_criacao or datetime.utcnow()

    def listar_curtidas(self):
        return [curtida.usuario.username for curtida in self.curtidas]

    def listar_comentarios(self):
        return [(comentario.usuario.username, comentario.texto) for comentario in self.comentarios]

    def curtir(self, usuario):
        curtida = Curtida(id_usuario=usuario.id, id_publicacao=self.id)
        db.session.add(curtida)
        db.session.commit()

    def comentar(self, usuario, texto):
        comentario = Comentario(
            texto=texto,
            usuario_id=usuario.id,
            publicacao_id=self.id
        )
        db.session.add(comentario)
        db.session.commit()
        return comentario



class Comentario(db.Model):
    __tablename__ = 'comentario'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_publicacao = db.Column(db.Integer, db.ForeignKey('publicacao.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # <-- Adicionado aqui

    usuario = db.relationship('Usuario', backref='comentarios', lazy=True)
    publicacao = db.relationship('Publicacao', backref='comentarios_publicacao', lazy=True)
    curtidas = db.relationship('Curtida', backref='comentario', lazy='dynamic')
    respostas = db.relationship(
        'Resposta',
        backref='comentario_pai',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __init__(self, texto, usuario_id, publicacao_id):
        self.texto = texto
        self.id_usuario = usuario_id
        self.id_publicacao = publicacao_id
        self.data_criacao = datetime.utcnow()

    def curtir(self, usuario):
        curtida = Curtida(id_usuario=usuario.id, id_comentario=self.id)
        db.session.add(curtida)
        db.session.commit()

    def responder(self, usuario, texto):
        resposta = Resposta(texto=texto, id_usuario=usuario.id, id_comentario=self.id)
        db.session.add(resposta)
        db.session.commit()

    def listar_curtidas(self):
        return [curtida.usuario.username for curtida in self.curtidas]

    def listar_respostas(self):
        return [resposta.texto for resposta in self.respostas]

class Resposta(db.Model):
    __tablename__ = 'resposta'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)  # 🔹 Aqui está o novo campo
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_comentario = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=False)

    usuario = db.relationship('Usuario', backref='respostas', lazy=True)
    comentario = db.relationship('Comentario', backref='comentarios_resposta', lazy=True)
    
    curtidas = db.relationship('Curtida', backref='resposta', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Curtida.id_resposta')

    def __init__(self, texto, id_usuario, id_comentario):
        self.texto = texto
        self.id_usuario = id_usuario
        self.id_comentario = id_comentario
        
    def curtir(self, usuario):
        curtida = Curtida(id_usuario=usuario.id, id_resposta=self.id)
        db.session.add(curtida) 
        db.session.commit()
    
    def listar_curtidas(self):
        return [curtida.usuario.username for curtida in self.curtidas]

class Curtida(db.Model):
    __tablename__ = 'curtida'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_publicacao = db.Column(db.Integer, db.ForeignKey('publicacao.id'), nullable=True)
    id_comentario = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=True)
    id_resposta = db.Column(db.Integer, db.ForeignKey('resposta.id'), nullable=True)

    usuario = db.relationship('Usuario', backref='curtidas', lazy=True)

    def __init__(self, id_usuario, id_publicacao=None, id_comentario=None):
        self.id_usuario = id_usuario
        self.id_publicacao = id_publicacao
        self.id_comentario = id_comentario