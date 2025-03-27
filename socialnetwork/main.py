from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, login_remembered, logout_user, current_user
from models import Usuario
from db import db
import hashlib

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
def home():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)