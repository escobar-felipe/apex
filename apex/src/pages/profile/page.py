from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from flask_login import current_user
from src.pages.pages_components.navbar import navbar
import dash_mantine_components as dmc
from dash_iconify import DashIconify

register_page(__name__, path='/profile', title="Meu Perfil")


def layout(**query_strings):
    if current_user.is_authenticated:
        redirect_div = html.Div(id="redirect-user-page")
        page_header = html.Div(
            [
                dmc.Title("Minha Conta", order=1, className="apex-page-title"),
                dmc.Text(
                    "Mantenha suas credenciais atualizadas para pesquisar, gerar relatórios e enviar emails pelo sistema.",
                    className="apex-page-subtitle",
                ),
            ],
            className="mt-4 mb-4",
        )
        alert = dmc.Alert(dmc.Group([dmc.Text("Para cadastrar seus dados, siga as instruções da conta.", size="md"), dcc.Link("Abrir instruções", className="fs-6 apex-link" ,href="/profile/instructions")]), title=dmc.Text(
            "Informações", weight=700), color="yellow", className="apex-alert mb-4")
        api_key_input = html.Div(
            [          
                html.Div(
                    [
                        dbc.Label("Email", html_for="email_user"),
                        dbc.Input(
                            type="email",
                            id="email_user",
                            placeholder="Seu email",
                            value=current_user.email
                        ),
                        dbc.FormText(
                            "Use o Gmail configurado para envio dos relatórios.", color="secondary"
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Label("Senha SMTP", html_for="stmp_password"),
                        dbc.Input(
                            type="password",
                            id="stmp_password",
                            placeholder="Senha SMTP cadastrada" if current_user.stmp_password else "Sua senha SMTP",
                            value=""
                        ),
                        dbc.FormText(
                            "Use uma senha de aplicativo do Google, não a senha normal da conta.", color="secondary"
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Label("Chave API", html_for="open-api-key"),
                        dbc.Input(
                            type="password",
                            id="open-api-key",
                            placeholder="Chave OpenAI cadastrada" if current_user.api_key else "Sua chave OpenAI",
                            value=""
                        ),
                        dbc.FormText(
                            "Informe sua chave da API OpenAI.", color="secondary"
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Label("Chave SerperAPI", html_for="serp-api-key"),
                        dbc.Input(
                            type="password",
                            id="serp-api-key",
                            placeholder="Chave SerperAPI cadastrada" if current_user.serpapi_key else "Sua chave SerperAPI",
                            value=""
                        ),
                        dbc.FormText(
                            "Informe sua chave SerperAPI.", color="secondary"
                        ),
                    ]
                ),
            ],
            className="apex-form-grid",
        )
        confirmation = dbc.Checklist(
            options=[
                {
                    "label": "Confirmo que desejo salvar ou sobrescrever as credenciais da minha conta.",
                    "value": "confirmed",
                }
            ],
            value=[],
            id="confirm-update-user",
            class_name="mt-3",
        )
        button = dmc.Center(
            style={"height": "auto", "width": "100%"},
            children=[
                dmc.Button(
                    "Salvar Dados",
                    leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
                    className="my-2 apex-button",
                    color="#504cab",
                    id= "btn-update-user",
                )
            ],
        )
        modal = dmc.Modal(
            title="Atualização da conta",
            id="modal-update-user",
            centered=True,
            zIndex=10000,
            opened= False,
            children=[dmc.Text("Revise os dados informados.")],
        )

        form=  dmc.LoadingOverlay(dbc.Form([api_key_input, confirmation], class_name="mt-4", id="form-user"))
        content = dbc.Container(
            [dbc.Col([page_header, alert, redirect_div, html.Div(form, className="apex-panel apex-profile-form"), button,modal])], fluid=False, class_name="apex-container")
        body = html.Div([navbar(icon=None, profile_active=True), content], className="apex-shell")
        return body
    else:
        return dcc.Location(pathname="/login", id="someid_login")
