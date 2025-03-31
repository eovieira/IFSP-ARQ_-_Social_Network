from db import db
from flask_login import UserMixin

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


class Seguir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_seguidor = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_seguido = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Bloquear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_bloqueador = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_bloqueado = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)