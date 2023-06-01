from flask_celeryext import FlaskCeleryExt  #
from src.utils.celery_utils import make_celery

ext_celery = FlaskCeleryExt(create_celery_app=make_celery)  

def init_app(app):
    ext_celery.init_app(app)