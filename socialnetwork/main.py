# app.py
from flask import Flask, redirect, url_for, g, request, render_template
from flask_login import LoginManager
from flask_cors import CORS
from db import db
from models import Usuario
from routes import init_app
from user_agents import parse

app = Flask(__name__)
app.secret_key = 'b1b39f3b13f4d82f957ee82b2aff10ae7d5903aa1ab6baa6c77664f667dde823'

# Habilita CORS para requisições JSON com credenciais
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type"],
         "supports_credentials": True
     }})

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@app.before_request
def detectar_dispositivo():
    user_agent = parse(request.headers.get('User-Agent', ''))
    if user_agent.is_mobile:
        g.device = 'mobile'
    elif user_agent.is_tablet:
        g.device = 'tablet'
    else:
        g.device = 'desktop'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query_by_id(int(user_id))

@app.route('/')
def home_redirect():
    return render_template('spa.html')

@app.route('/spa')
def spa():
    """Renderiza a Single Page Application"""
    return render_template('spa.html')
    return redirect(url_for('feed.topics'))

# Importa e registra todos os blueprints definidos na pasta routes/
init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
