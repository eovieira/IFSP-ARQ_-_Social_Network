from .feed import feed_bp
from .perfil import perfil_bp
from .admin import admin_bp
from .interacoes import interacoes_bp
from .auth import auth_bp
from .comentarios_json import comentarios_json_bp

def init_app(app):
    app.register_blueprint(feed_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(interacoes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(comentarios_json_bp)
