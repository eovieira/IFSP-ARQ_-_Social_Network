from db import db
from flask_login import UserMixin
from datetime import datetime

class Usuario(UserMixin):
    """Modelo de usuário para JSON"""
    
    def __init__(self, username=None, nome=None, senha=None, cargo=None, foto_perfil=None, email=None, id=None):
        self.id = id
        self.username = username
        self.nome = nome
        self.senha = senha
        self.cargo = cargo
        self.foto_perfil = foto_perfil
        self.email = email
    
    @staticmethod
    def create(username, email, nome, senha, cargo):
        """Cria e salva um novo usuário"""
        usuario_dict = {
            'username': username,
            'email': email,
            'nome': nome,
            'senha': senha,
            'cargo': cargo,
            'foto_perfil': None
        }
        return Usuario(**db.save_usuario(usuario_dict))
    
    @staticmethod
    def query_by_id(user_id):
        """Busca usuário por ID"""
        data = db.get_usuario_by_id(user_id)
        if data:
            return Usuario(**data)
        return None
    
    @staticmethod
    def query_by_username(username):
        """Busca usuário por username"""
        data = db.get_usuario_by_username(username)
        if data:
            return Usuario(**data)
        return None
    
    @staticmethod
    def query_all():
        """Retorna todos os usuários"""
        usuarios = db.get_all_usuarios()
        return [Usuario(**u) for u in usuarios]
    
    def save(self):
        """Salva o usuário"""
        usuario_dict = {
            'id': self.id,
            'username': self.username,
            'nome': self.nome,
            'senha': self.senha,
            'cargo': self.cargo,
            'foto_perfil': self.foto_perfil
        }
        result = db.save_usuario(usuario_dict)
        self.id = result['id']
        return self
    
    def curtiu(self, item):
        """Verifica se o usuário curtiu um item"""
        if isinstance(item, Publicacao):
            return db.get_curtida(self.id, pub_id=item.id) is not None
        elif isinstance(item, Comentario):
            return db.get_curtida(self.id, com_id=item.id) is not None
        elif isinstance(item, Resposta):
            return db.get_curtida(self.id, resp_id=item.id) is not None
        return False
    
    @property
    def seguindo(self):
        """Retorna lista de usuários que este usuário está seguindo"""
        return Seguir.query_by_seguidor(self.id)
    
    @property
    def seguidores(self):
        """Retorna lista de usuários que seguem este usuário"""
        return Seguir.query_by_seguido(self.id)
    
    @property
    def bloqueados(self):
        """Retorna lista de usuários bloqueados por este usuário"""
        return Bloquear.query_bloqueador(self.id)
    
    @property
    def bloqueado_por(self):
        """Retorna lista de usuários que bloquearam este usuário"""
        return Bloquear.query_bloqueado(self.id)
    
    @property
    def publicacoes(self):
        """Retorna publicações do usuário"""
        return Publicacao.query_by_usuario(self.id)
    
    @property
    def quantia_seguidores(self):
        """Retorna quantidade de seguidores"""
        return len(self.seguidores)
    
    @property
    def quantia_seguindo(self):
        """Retorna quantidade de pessoas que está seguindo"""
        return len(self.seguindo)


class Seguir:
    """Modelo de relacionamento de seguimento"""
    
    def __init__(self, id_seguidor=None, id_seguido=None, id=None):
        self.id = id
        self.id_seguidor = id_seguidor
        self.id_seguido = id_seguido
    
    @staticmethod
    def create(id_seguidor, id_seguido):
        """Cria e salva um novo relacionamento"""
        seguir_dict = {
            'id_seguidor': id_seguidor,
            'id_seguido': id_seguido
        }
        return Seguir(**db.save_seguir(seguir_dict))
    
    @staticmethod
    def query_by_seguidor(user_id):
        """Retorna os usuários que um usuário está seguindo"""
        return [Seguir(**s) for s in db.get_seguindo(user_id)]
    
    @staticmethod
    def query_by_seguido(user_id):
        """Retorna os seguidores de um usuário"""
        return [Seguir(**s) for s in db.get_seguidores(user_id)]
    
    @staticmethod
    def query_rel(seguidor_id, seguido_id):
        """Busca um relacionamento específico"""
        data = db.get_seguindo_rel(seguidor_id, seguido_id)
        if data:
            return Seguir(**data)
        return None
    
    def delete(self):
        """Deleta o relacionamento"""
        db.delete_seguir(self.id_seguidor, self.id_seguido)


class Bloquear:
    """Modelo de bloqueio"""
    
    def __init__(self, id_bloqueador=None, id_bloqueado=None, id=None):
        self.id = id
        self.id_bloqueador = id_bloqueador
        self.id_bloqueado = id_bloqueado
    
    @staticmethod
    def create(id_bloqueador, id_bloqueado):
        """Cria e salva um novo bloqueio"""
        bloquear_dict = {
            'id_bloqueador': id_bloqueador,
            'id_bloqueado': id_bloqueado
        }
        return Bloquear(**db.save_bloquear(bloquear_dict))
    
    @staticmethod
    def query_bloqueador(user_id):
        """Retorna usuários bloqueados por um usuário"""
        return [Bloquear(**b) for b in db.get_bloqueados(user_id)]
    
    @staticmethod
    def query_bloqueado(user_id):
        """Retorna usuários que bloquearam um usuário"""
        return [Bloquear(**b) for b in db.get_bloqueado_por(user_id)]
    
    @staticmethod
    def query_rel(bloqueador_id, bloqueado_id):
        """Busca um relacionamento específico"""
        data = db.get_bloquear_rel(bloqueador_id, bloqueado_id)
        if data:
            return Bloquear(**data)
        return None
    
    def delete(self):
        """Deleta o bloqueio"""
        db.delete_bloquear(self.id_bloqueador, self.id_bloqueado)


class Publicacao:
    """Modelo de publicação"""
    
    def __init__(self, texto=None, id_usuario=None, data_criacao=None, id=None, usuario=None):
        self.id = id
        self.texto = texto
        self.id_usuario = id_usuario
        # Converte string ISO para datetime se necessário
        if isinstance(data_criacao, str):
            try:
                self.data_criacao = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                self.data_criacao = datetime.utcnow()
        else:
            self.data_criacao = data_criacao or datetime.utcnow()
        self._usuario = usuario
    
    @staticmethod
    def create(texto, usuario_id, data_criacao=None):
        """Cria e salva uma nova publicação"""
        publicacao_dict = {
            'texto': texto,
            'id_usuario': usuario_id,
            'data_criacao': (data_criacao or datetime.utcnow()).isoformat()
        }
        return Publicacao(**db.save_publicacao(publicacao_dict))
    
    @staticmethod
    def query_by_id(pub_id):
        """Busca publicação por ID"""
        data = db.get_publicacao_by_id(pub_id)
        if data:
            return Publicacao(**data)
        return None
    
    @staticmethod
    def query_by_usuario(user_id):
        """Busca publicações de um usuário"""
        publicacoes = db.get_publicacoes_by_usuario(user_id)
        return [Publicacao(**p) for p in publicacoes]
    
    @staticmethod
    def query_all():
        """Retorna todas as publicações"""
        publicacoes = db.get_all_publicacoes()
        return [Publicacao(**p) for p in publicacoes]
    
    @property
    def usuario(self):
        """Retorna o usuário que fez a publicação"""
        if not self._usuario:
            self._usuario = Usuario.query_by_id(self.id_usuario)
        return self._usuario
    
    @property
    def comentarios(self):
        """Retorna comentários da publicação"""
        return [Comentario(**c) for c in db.get_comentarios_by_publicacao(self.id)]
    
    @property
    def curtidas(self):
        """Retorna curtidas da publicação"""
        return [Curtida(**c) for c in db.get_curtidas_by_publicacao(self.id)]
    
    def listar_curtidas(self):
        """Retorna nomes de usuários que curtiram"""
        curtidas_list = []
        for curtida_data in db.get_curtidas_by_publicacao(self.id):
            usuario = Usuario.query_by_id(curtida_data['id_usuario'])
            if usuario:
                curtidas_list.append(usuario.username)
        return curtidas_list
    
    def listar_comentarios(self):
        """Retorna comentários em formato de tupla"""
        comentarios_list = []
        for com_data in db.get_comentarios_by_publicacao(self.id):
            usuario = Usuario.query_by_id(com_data['id_usuario'])
            if usuario:
                comentarios_list.append((usuario.username, com_data['texto']))
        return comentarios_list
    
    def curtir(self, usuario):
        """Usuário curte a publicação"""
        Curtida.create(usuario.id, pub_id=self.id)
    
    def comentar(self, usuario, texto):
        """Usuário comenta na publicação"""
        return Comentario.create(texto, usuario.id, self.id)
    
    def save(self):
        """Salva a publicação"""
        publicacao_dict = {
            'id': self.id,
            'texto': self.texto,
            'id_usuario': self.id_usuario,
            'data_criacao': self.data_criacao.isoformat() if isinstance(self.data_criacao, datetime) else self.data_criacao
        }
        result = db.save_publicacao(publicacao_dict)
        self.id = result['id']
        return self
    
    def delete(self):
        """Deleta a publicação"""
        db.delete_publicacao(self.id)


class Comentario:
    """Modelo de comentário"""
    
    def __init__(self, texto=None, id_usuario=None, id_publicacao=None, data_criacao=None, id=None, usuario=None):
        self.id = id
        self.texto = texto
        self.id_usuario = id_usuario
        self.id_publicacao = id_publicacao
        # Converte string ISO para datetime se necessário
        if isinstance(data_criacao, str):
            try:
                self.data_criacao = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                self.data_criacao = datetime.utcnow()
        else:
            self.data_criacao = data_criacao or datetime.utcnow()
        self._usuario = usuario
    
    @staticmethod
    def create(texto, usuario_id, publicacao_id):
        """Cria e salva um novo comentário"""
        comentario_dict = {
            'texto': texto,
            'id_usuario': usuario_id,
            'id_publicacao': publicacao_id,
            'data_criacao': datetime.utcnow().isoformat()
        }
        return Comentario(**db.save_comentario(comentario_dict))
    
    @staticmethod
    def query_by_id(com_id):
        """Busca comentário por ID"""
        data = db.get_comentario_by_id(com_id)
        if data:
            return Comentario(**data)
        return None
    
    @staticmethod
    def query_by_publicacao(pub_id):
        """Busca comentários de uma publicação"""
        comentarios = db.get_comentarios_by_publicacao(pub_id)
        return [Comentario(**c) for c in comentarios]
    
    @property
    def usuario(self):
        """Retorna o usuário que fez o comentário"""
        if not self._usuario:
            self._usuario = Usuario.query_by_id(self.id_usuario)
        return self._usuario
    
    @property
    def publicacao(self):
        """Retorna a publicação do comentário"""
        return Publicacao.query_by_id(self.id_publicacao)
    
    @property
    def curtidas(self):
        """Retorna curtidas do comentário"""
        return [Curtida(**c) for c in db.get_curtidas_by_comentario(self.id)]
    
    @property
    def respostas(self):
        """Retorna respostas do comentário"""
        return [Resposta(**r) for r in db.get_respostas_by_comentario(self.id)]
    
    @respostas.setter
    def respostas(self, value):
        """Setter para respostas (compatibilidade)"""
        pass
    
    def curtir(self, usuario):
        """Usuário curte o comentário"""
        Curtida.create(usuario.id, com_id=self.id)
    
    def responder(self, usuario, texto):
        """Usuário responde ao comentário"""
        return Resposta.create(texto, usuario.id, self.id)
    
    def listar_curtidas(self):
        """Retorna nomes de usuários que curtiram"""
        curtidas_list = []
        for curtida_data in db.get_curtidas_by_comentario(self.id):
            usuario = Usuario.query_by_id(curtida_data['id_usuario'])
            if usuario:
                curtidas_list.append(usuario.username)
        return curtidas_list
    
    def listar_respostas(self):
        """Retorna textos das respostas"""
        respostas_list = []
        for resp_data in db.get_respostas_by_comentario(self.id):
            respostas_list.append(resp_data['texto'])
        return respostas_list
    
    def save(self):
        """Salva o comentário"""
        comentario_dict = {
            'id': self.id,
            'texto': self.texto,
            'id_usuario': self.id_usuario,
            'id_publicacao': self.id_publicacao,
            'data_criacao': self.data_criacao.isoformat() if isinstance(self.data_criacao, datetime) else self.data_criacao
        }
        result = db.save_comentario(comentario_dict)
        self.id = result['id']
        return self
    
    def delete(self):
        """Deleta o comentário"""
        db.delete_comentario(self.id)


class Resposta:
    """Modelo de resposta"""
    
    def __init__(self, texto=None, id_usuario=None, id_comentario=None, data_criacao=None, id=None, usuario=None):
        self.id = id
        self.texto = texto
        self.id_usuario = id_usuario
        self.id_comentario = id_comentario
        # Converte string ISO para datetime se necessário
        if isinstance(data_criacao, str):
            try:
                self.data_criacao = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                self.data_criacao = datetime.utcnow()
        else:
            self.data_criacao = data_criacao or datetime.utcnow()
        self._usuario = usuario
    
    @staticmethod
    def create(texto, id_usuario, id_comentario):
        """Cria e salva uma nova resposta"""
        resposta_dict = {
            'texto': texto,
            'id_usuario': id_usuario,
            'id_comentario': id_comentario,
            'data_criacao': datetime.utcnow().isoformat()
        }
        return Resposta(**db.save_resposta(resposta_dict))
    
    @staticmethod
    def query_by_id(resp_id):
        """Busca resposta por ID"""
        data = db.get_resposta_by_id(resp_id)
        if data:
            return Resposta(**data)
        return None
    
    @staticmethod
    def query_by_comentario(com_id):
        """Busca respostas de um comentário"""
        respostas = db.get_respostas_by_comentario(com_id)
        return [Resposta(**r) for r in respostas]
    
    @property
    def usuario(self):
        """Retorna o usuário que fez a resposta"""
        if not self._usuario:
            self._usuario = Usuario.query_by_id(self.id_usuario)
        return self._usuario
    
    @property
    def comentario_pai(self):
        """Retorna o comentário pai"""
        return Comentario.query_by_id(self.id_comentario)
    
    @property
    def curtidas(self):
        """Retorna curtidas da resposta"""
        return [Curtida(**c) for c in db.get_curtidas_by_resposta(self.id)]
    
    def curtir(self, usuario):
        """Usuário curte a resposta"""
        Curtida.create(usuario.id, resp_id=self.id)
    
    def listar_curtidas(self):
        """Retorna nomes de usuários que curtiram"""
        curtidas_list = []
        for curtida_data in db.get_curtidas_by_resposta(self.id):
            usuario = Usuario.query_by_id(curtida_data['id_usuario'])
            if usuario:
                curtidas_list.append(usuario.username)
        return curtidas_list
    
    def save(self):
        """Salva a resposta"""
        resposta_dict = {
            'id': self.id,
            'texto': self.texto,
            'id_usuario': self.id_usuario,
            'id_comentario': self.id_comentario,
            'data_criacao': self.data_criacao.isoformat() if isinstance(self.data_criacao, datetime) else self.data_criacao
        }
        result = db.save_resposta(resposta_dict)
        self.id = result['id']
        return self
    
    def delete(self):
        """Deleta a resposta"""
        db.delete_resposta(self.id)


class Curtida:
    """Modelo de curtida"""
    
    def __init__(self, id_usuario=None, id_publicacao=None, id_comentario=None, id_resposta=None, id=None, usuario=None):
        self.id = id
        self.id_usuario = id_usuario
        self.id_publicacao = id_publicacao
        self.id_comentario = id_comentario
        self.id_resposta = id_resposta
        self._usuario = usuario
    
    @staticmethod
    def create(id_usuario, pub_id=None, com_id=None, resp_id=None):
        """Cria e salva uma nova curtida"""
        curtida_dict = {
            'id_usuario': id_usuario,
            'id_publicacao': pub_id,
            'id_comentario': com_id,
            'id_resposta': resp_id
        }
        return Curtida(**db.save_curtida(curtida_dict))
    
    @staticmethod
    def query_by_usuario_publicacao(user_id, pub_id):
        """Busca curtida específica em publicação"""
        data = db.get_curtida(user_id, pub_id=pub_id)
        if data:
            return Curtida(**data)
        return None
    
    @staticmethod
    def query_by_usuario_comentario(user_id, com_id):
        """Busca curtida específica em comentário"""
        data = db.get_curtida(user_id, com_id=com_id)
        if data:
            return Curtida(**data)
        return None
    
    @staticmethod
    def query_by_usuario_resposta(user_id, resp_id):
        """Busca curtida específica em resposta"""
        data = db.get_curtida(user_id, resp_id=resp_id)
        if data:
            return Curtida(**data)
        return None
    
    @property
    def usuario(self):
        """Retorna o usuário que curtiu"""
        if not self._usuario:
            self._usuario = Usuario.query_by_id(self.id_usuario)
        return self._usuario
    
    @property
    def publicacao(self):
        """Retorna a publicação curtida"""
        if self.id_publicacao:
            return Publicacao.query_by_id(self.id_publicacao)
        return None
    
    @property
    def comentario(self):
        """Retorna o comentário curtido"""
        if self.id_comentario:
            return Comentario.query_by_id(self.id_comentario)
        return None
    
    @property
    def resposta(self):
        """Retorna a resposta curtida"""
        if self.id_resposta:
            return Resposta.query_by_id(self.id_resposta)
        return None
    
    def save(self):
        """Salva a curtida"""
        curtida_dict = {
            'id': self.id,
            'id_usuario': self.id_usuario,
            'id_publicacao': self.id_publicacao,
            'id_comentario': self.id_comentario,
            'id_resposta': self.id_resposta
        }
        result = db.save_curtida(curtida_dict)
        self.id = result['id']
        return self
    
    def delete(self):
        """Deleta a curtida"""
        if self.id:
            db.delete_curtida(self.id)
        resposta = Resposta(texto=texto, id_usuario=usuario.id, id_comentario=self.id)
        db.session.add(resposta)
        db.session.commit()

    def listar_curtidas(self):
        return [curtida.usuario.username for curtida in self.curtidas]

    def listar_respostas(self):
        return [resposta.texto for resposta in self.respostas]

