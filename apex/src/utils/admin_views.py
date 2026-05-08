from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import current_user
from src.config import get_settings
from src.models import Tenant, User


def tenant_options():
    tenants = Tenant.query.filter_by(active=True).order_by(Tenant.slug.asc()).all()
    return [{"label": f"{tenant.name} ({tenant.slug})", "value": tenant.slug} for tenant in tenants]


def default_tenant_value():
    settings = get_settings()
    default_tenant = Tenant.query.filter_by(slug=settings.default_tenant_slug, active=True).first()
    if default_tenant:
        return default_tenant.slug

    first_tenant = Tenant.query.filter_by(active=True).order_by(Tenant.slug.asc()).first()
    return first_tenant.slug if first_tenant else None


def render_admin_data():
    tenants = Tenant.query.order_by(Tenant.slug.asc()).all()
    users = (
        User.query.join(Tenant, User.tenant_id == Tenant.id)
        .order_by(Tenant.slug.asc(), User.username.asc())
        .all()
    )

    tenant_rows = [
        html.Tr(
            [
                html.Td(tenant.slug),
                html.Td(tenant.name),
                html.Td(tenant.domain or "-"),
                html.Td("Ativo" if tenant.active else "Inativo"),
            ]
        )
        for tenant in tenants
    ]
    user_rows = [
        html.Tr(
            [
                html.Td(user.username),
                html.Td(user.tenant.slug if user.tenant else "-"),
                html.Td("Admin" if user.admin else "Usuário"),
                html.Td(user.email or "-"),
                html.Td(
                    dmc.Button(
                        "Excluir",
                        leftIcon=DashIconify(icon="mdi:trash-can-outline", width=18),
                        id={"type": "admin-delete-user", "index": user.id},
                        color="red",
                        variant="outline",
                        compact=True,
                        className="apex-button-danger-outline",
                        disabled=current_user.is_authenticated and user.id == current_user.id,
                    )
                ),
            ]
        )
        for user in users
    ]

    return html.Div(
        [
            dmc.Title("Tenants", order=2, className="apex-section-title"),
            dbc.Table(
                [
                    html.Thead(html.Tr([html.Th("Slug"), html.Th("Nome"), html.Th("Dominio"), html.Th("Status")])),
                    html.Tbody(tenant_rows or [html.Tr(html.Td("Nenhum tenant encontrado.", colSpan=4))]),
                ],
                bordered=False,
                hover=True,
                responsive=True,
                class_name="apex-admin-table",
            ),
            dmc.Title("Usuários", order=2, className="apex-section-title mt-4"),
            dbc.Table(
                [
                    html.Thead(html.Tr([html.Th("Usuário"), html.Th("Tenant"), html.Th("Perfil"), html.Th("Email"), html.Th("Ações")])),
                    html.Tbody(user_rows or [html.Tr(html.Td("Nenhum usuário encontrado.", colSpan=5))]),
                ],
                bordered=False,
                hover=True,
                responsive=True,
                class_name="apex-admin-table",
            ),
        ],
        id="admin-data-section",
    )
