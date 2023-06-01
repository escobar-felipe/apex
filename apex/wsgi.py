from src.app import create_app
from src.ext.celery import  ext_celery

app = application = create_app()
celery = ext_celery.celery

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)