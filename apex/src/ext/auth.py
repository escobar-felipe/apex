from flask_login import LoginManager
from src.models import User
from src.ext.database import db
from werkzeug.security import check_password_hash, generate_password_hash

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def create_user(username, password):
    """Registra um novo usuario caso nao esteja cadastrado"""
    if User.query.filter_by(username=username).first():
        raise RuntimeError(f'{username} ja esta cadastrado')
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user

def init_app(app):
    login_manager.init_app(app)