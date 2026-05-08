from flask_login import LoginManager
from src.models import Tenant, User
from src.ext.database import db
from werkzeug.security import check_password_hash, generate_password_hash
from src.config import get_settings

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



def get_or_create_tenant(slug=None, name=None, domain=None):
    settings = get_settings()
    tenant_slug = slug or settings.default_tenant_slug
    tenant = Tenant.query.filter_by(slug=tenant_slug).first()
    if tenant:
        return tenant

    tenant = Tenant(
        slug=tenant_slug,
        name=name or tenant_slug.title(),
        domain=domain,
        active=True,
    )
    db.session.add(tenant)
    db.session.commit()
    return tenant


def create_user(username, password, tenant_slug=None):
    """Registra um novo usuario caso nao esteja cadastrado"""
    tenant = get_or_create_tenant(slug=tenant_slug)
    if User.query.filter_by(username=username, tenant_id=tenant.id).first():
        raise RuntimeError(f'{username} ja esta cadastrado para o tenant {tenant.slug}')
    user = User(username=username, password=generate_password_hash(password), tenant_id=tenant.id)
    db.session.add(user)
    db.session.commit()
    return user

def init_app(app):
    login_manager.init_app(app)
