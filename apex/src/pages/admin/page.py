from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import current_user
from src.pages.pages_components.navbar import navbar
from src.utils.admin_views import default_tenant_value, render_admin_data, tenant_options


register_page(__name__, path='/admin', title="Admin")


def _tenant_form():
    return html.Div(
        [
            dmc.Title("Criar Tenant", order=2, className="apex-section-title"),
            html.Div(
                [
                    dbc.Input(id="admin-tenant-slug", placeholder="slug-exemplo"),
                    dbc.Input(id="admin-tenant-name", placeholder="Nome do tenant"),
                    dbc.Input(id="admin-tenant-domain", placeholder="dominio opcional"),
                ],
                className="apex-form-grid",
            ),
            dmc.Button(
                "Criar Tenant",
                leftIcon=DashIconify(icon="mdi:domain-plus", width=20),
                id="admin-create-tenant",
                className="mt-3 apex-button",
                color="#504cab",
            ),
        ],
        className="apex-panel",
    )


def _user_form():
    return html.Div(
        [
            dmc.Title("Criar Usuário", order=2, className="apex-section-title"),
            html.Div(
                [
                    dbc.Input(id="admin-user-username", placeholder="usuário"),
                    dbc.Input(id="admin-user-password", placeholder="senha inicial", type="password"),
                    dcc.Dropdown(
                        id="admin-user-tenant",
                        options=tenant_options(),
                        value=default_tenant_value(),
                        placeholder="Selecione o tenant",
                        clearable=False,
                        className="apex-dropdown",
                    ),
                ],
                className="apex-form-grid",
            ),
            dbc.Checklist(
                options=[{"label": "Conceder acesso administrativo/root", "value": "admin"}],
                value=[],
                id="admin-user-is-admin",
                class_name="mt-3",
            ),
            dmc.Button(
                "Criar Usuário",
                leftIcon=DashIconify(icon="mdi:account-plus-outline", width=20),
                id="admin-create-user",
                className="mt-3 apex-button",
                color="#504cab",
            ),
        ],
        className="apex-panel",
    )


def layout(**query_strings):
    if not current_user.is_authenticated:
        return dcc.Location(pathname="/login", id="redirect-admin-login")

    if not current_user.admin:
        content = dbc.Container(
            [
                dmc.Alert(
                    "Sua conta não tem permissão para acessar a administração.",
                    title="Acesso restrito",
                    color="red",
                    className="apex-alert mt-4",
                )
            ],
            fluid=False,
            class_name="apex-container",
        )
        return html.Div([navbar(icon=None), content], className="apex-shell")

    page_header = html.Div(
        [
            dmc.Title("Administração", order=1, className="apex-page-title"),
            dmc.Text(
                "Gerencie tenants e usuários da aplicação.",
                className="apex-page-subtitle",
            ),
        ],
        className="mt-4 mb-4",
    )
    content = dbc.Container(
        [
            dbc.Col(
                [
                    page_header,
                    html.Div(id="admin-feedback"),
                    dcc.Store(id="admin-delete-user-id"),
                    dmc.Modal(
                        title="Confirmar exclusão de usuário",
                        id="admin-delete-user-modal",
                        centered=True,
                        zIndex=10000,
                        opened=False,
                        children=[
                            dmc.Text(id="admin-delete-user-message", className="mb-3"),
                            dmc.Group(
                                [
                                    dmc.Button(
                                        "Cancelar",
                                        id="admin-cancel-delete-user",
                                        variant="outline",
                                        color="gray",
                                        className="apex-button-outline",
                                    ),
                                    dmc.Button(
                                        "Excluir usuário",
                                        id="admin-confirm-delete-user",
                                        color="red",
                                        className="apex-button-danger",
                                        leftIcon=DashIconify(icon="mdi:trash-can-outline", width=18),
                                    ),
                                ],
                                position="right",
                            ),
                        ],
                    ),
                    html.Div([_tenant_form(), _user_form()], className="apex-admin-grid"),
                    html.Div(render_admin_data(), className="apex-panel mt-4"),
                ]
            )
        ],
        fluid=False,
        class_name="apex-container",
    )
    return html.Div([navbar(icon=None, admin_active=True), content], className="apex-shell")
