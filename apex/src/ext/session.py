from flask_session import Session

session = Session()

def init_app(app):
    session.init_app(app)