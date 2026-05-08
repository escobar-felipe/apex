from flask import g, request
from src.config import get_settings
from src.models import Tenant


LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def normalize_host(host):
    return (host or "").split(":", 1)[0].lower().strip()


def get_tenant_slug_from_host(host=None):
    settings = get_settings()
    normalized_host = normalize_host(host or request.host)

    if not normalized_host or normalized_host in LOCAL_HOSTS:
        return settings.default_tenant_slug

    root_domain = normalize_host(settings.root_domain)
    if root_domain and normalized_host == root_domain:
        return settings.default_tenant_slug

    if root_domain and normalized_host.endswith(f".{root_domain}"):
        return normalized_host[: -(len(root_domain) + 1)]

    return settings.default_tenant_slug


def get_current_tenant():
    if hasattr(g, "tenant"):
        return g.tenant

    slug = get_tenant_slug_from_host()
    g.tenant = Tenant.query.filter_by(slug=slug, active=True).first()
    return g.tenant


def get_current_tenant_id():
    tenant = get_current_tenant()
    return tenant.id if tenant else None
