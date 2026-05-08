import re
from dash import no_update
from dash_extensions.enrich import Output, Input, State, callback, ALL
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from flask_login import current_user
from werkzeug.security import generate_password_hash
from src.config import get_settings
from src.ext.auth import get_or_create_tenant
from src.ext.database import db
from src.models import Tenant, User
from src.utils.admin_views import render_admin_data


SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$")


def _alert(message, title, color):
    return dmc.Alert(message, title=title, color=color, className="apex-alert mb-4")


def _require_admin():
    return current_user.is_authenticated and current_user.admin


@callback(
    [
        Output("admin-feedback", "children"),
        Output("admin-data-section", "children"),
        Output("admin-user-tenant", "options"),
    ],
    [
        Input("admin-create-tenant", "n_clicks"),
        Input("admin-create-user", "n_clicks"),
    ],
    [
        State("admin-tenant-slug", "value"),
        State("admin-tenant-name", "value"),
        State("admin-tenant-domain", "value"),
        State("admin-user-username", "value"),
        State("admin-user-password", "value"),
        State("admin-user-tenant", "value"),
        State("admin-user-is-admin", "value"),
    ],
    prevent_initial_call=True,
)
def admin_create_callback(
    tenant_clicks,
    user_clicks,
    tenant_slug,
    tenant_name,
    tenant_domain,
    username,
    password,
    user_tenant_slug,
    is_admin,
):
    from dash import ctx

    if not _require_admin():
        return _alert("Acesso negado.", "Acesso restrito", "red"), no_update, no_update

    triggered = ctx.triggered_id
    if triggered == "admin-create-tenant" and not tenant_clicks:
        raise PreventUpdate

    if triggered == "admin-create-user" and not user_clicks:
        raise PreventUpdate

    if triggered == "admin-create-tenant":
        normalized_slug = (tenant_slug or "").strip().lower()
        normalized_name = (tenant_name or "").strip()
        normalized_domain = (tenant_domain or "").strip() or None

        if not SLUG_PATTERN.match(normalized_slug):
            return (
                _alert("Use um slug com letras minúsculas, números e hifens.", "Tenant inválido", "red"),
                no_update,
                no_update,
            )

        tenant = get_or_create_tenant(
            slug=normalized_slug,
            name=normalized_name or normalized_slug.title(),
            domain=normalized_domain,
        )
        tenant.name = normalized_name or tenant.name
        tenant.domain = normalized_domain
        tenant.active = True
        db.session.commit()

        options = [{"label": f"{item.name} ({item.slug})", "value": item.slug} for item in Tenant.query.order_by(Tenant.slug.asc()).all()]
        return (
            _alert(f"Tenant {tenant.slug} pronto para uso.", "Tenant criado", "green"),
            render_admin_data().children,
            options,
        )

    if triggered == "admin-create-user":
        normalized_username = (username or "").strip()
        normalized_tenant_slug = (user_tenant_slug or get_settings().default_tenant_slug).strip()

        if not normalized_username or not password:
            return (
                _alert("Informe usuário e senha.", "Usuário inválido", "red"),
                no_update,
                no_update,
            )

        tenant = Tenant.query.filter_by(slug=normalized_tenant_slug, active=True).first()
        if not tenant:
            return _alert("Tenant selecionado não foi encontrado.", "Tenant inválido", "red"), no_update, no_update

        if User.query.filter_by(username=normalized_username, tenant_id=tenant.id).first():
            return (
                _alert("Já existe um usuário com esse nome nesse tenant.", "Usuário duplicado", "red"),
                no_update,
                no_update,
            )

        user = User(
            username=normalized_username,
            password=generate_password_hash(password),
            tenant_id=tenant.id,
            admin="admin" in (is_admin or []),
        )
        db.session.add(user)
        db.session.commit()

        return (
            _alert(f"Usuário {user.username} criado no tenant {tenant.slug}.", "Usuário criado", "green"),
            render_admin_data().children,
            no_update,
        )

    return no_update, no_update, no_update


@callback(
    [
        Output("admin-delete-user-modal", "opened"),
        Output("admin-delete-user-message", "children"),
        Output("admin-delete-user-id", "data"),
    ],
    [
        Input({"type": "admin-delete-user", "index": ALL}, "n_clicks"),
        Input("admin-cancel-delete-user", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def admin_delete_modal_callback(delete_clicks, cancel_clicks):
    from dash import ctx

    if not _require_admin():
        return False, no_update, None

    triggered = ctx.triggered_id
    if triggered == "admin-cancel-delete-user":
        return False, no_update, None

    if isinstance(triggered, dict) and triggered.get("type") == "admin-delete-user":
        if not delete_clicks or not any(clicks for clicks in delete_clicks):
            return False, no_update, None

        user = User.query.get(triggered.get("index"))
        if not user:
            return False, no_update, None

        if user.id == current_user.id:
            return True, "Você não pode excluir o próprio usuário logado.", None

        tenant_slug = user.tenant.slug if user.tenant else "-"
        message = f"Tem certeza que deseja excluir o usuário {user.username} do tenant {tenant_slug}? Essa ação não pode ser desfeita."
        return True, message, user.id

    return False, no_update, None


@callback(
    [
        Output("admin-feedback", "children", allow_duplicate=True),
        Output("admin-data-section", "children", allow_duplicate=True),
        Output("admin-delete-user-modal", "opened", allow_duplicate=True),
        Output("admin-delete-user-id", "data", allow_duplicate=True),
    ],
    [Input("admin-confirm-delete-user", "n_clicks")],
    [State("admin-delete-user-id", "data")],
    prevent_initial_call=True,
)
def admin_confirm_delete_user(n_clicks, user_id):
    if not _require_admin():
        return _alert("Acesso negado.", "Acesso restrito", "red"), no_update, False, None

    if not n_clicks:
        raise PreventUpdate

    if not user_id:
        return _alert("Nenhum usuário selecionado para exclusão.", "Exclusão não realizada", "red"), no_update, False, None

    user = User.query.get(user_id)
    if not user:
        return _alert("Usuário não encontrado.", "Exclusão não realizada", "red"), no_update, False, None

    if user.id == current_user.id:
        return _alert("Você não pode excluir o próprio usuário logado.", "Exclusão bloqueada", "red"), no_update, False, None

    username = user.username
    tenant_slug = user.tenant.slug if user.tenant else "-"
    db.session.delete(user)
    db.session.commit()

    return (
        _alert(f"Usuário {username} removido do tenant {tenant_slug}.", "Usuário excluído", "green"),
        render_admin_data().children,
        False,
        None,
    )
