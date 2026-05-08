from flask import Flask 
from src.dash import dash_app
import redis
from src.ext import configuration
from src.config import get_settings
from src.utils.tenancy import get_current_tenant
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

def create_flask_app():

    settings = get_settings()
    server = Flask(__name__)
    server.config.update(
        ENV=settings.environment,
        SECRET_KEY=settings.secret_session,
        PREFERRED_URL_SCHEME="https" if settings.is_production_like else "http",
    )
    server.config['SESSION_TYPE'] = "redis"  #redis
    server.config['SESSION_REDIS'] = redis.from_url(f'{settings.redis_db}/1')
    server.config['SESSION_PERMANENT'] = False
    server.config['SESSION_USE_SIGNER'] = True
    server.config['SESSION_COOKIE_HTTPONLY'] = True
    server.config['SESSION_COOKIE_SAMESITE'] = "Lax"
    server.config['SESSION_COOKIE_SECURE'] = settings.use_secure_cookies
    server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    server.config['CACHE_TYPE'] = 'redis'
    server.config['CACHE_REDIS_URL'] = f'{settings.redis_db}/10'
    server.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url or 'sqlite:///' + os.path.join(basedir, 'database.db')
    server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    server.config['CELERY_BROKER_URL']= f"{settings.redis_db}/3"
    server.config['result_backend'] =  f"{settings.redis_db}/4"
    server.config['CELERY_RESULT_EXPIRES'] = settings.celery_result_expires_seconds
    server.config['CELERY_TASK_TRACK_STARTED'] = True
    server.config['CELERY_TASK_TIME_LIMIT'] = settings.celery_task_time_limit_seconds
    server.config['CELERY_TASK_SOFT_TIME_LIMIT'] = settings.celery_task_soft_time_limit_seconds

    server.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    @server.before_request
    def load_current_tenant():
        get_current_tenant()
    
    return server
    
def create_app():
    app = create_flask_app()

    configuration.load_extensions(app)
    dash_app.init_app(app)

    import src.pages.home.tasks

    if __name__ == '__main__':

        with  app.app_context() as ctx:
            dash_app.run(debug=True)

    return app
