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
        alert = dmc.Alert(dmc.Group([dmc.Text(f"Para realizar o cadastro do seus dados, siga as instruções:", size="lg"), dcc.Link("Clique aqui!", className="fs-6" ,href="https://www.google.com/drive", style={"color":"blue"})]), title=dmc.Text(
            "Informações", size="xl"), color="yellow", className="mt-4")
        api_key_input = html.Div(
            [          
                dbc.Label("Email", html_for="email_user"),
                dbc.Input(
                    type="text",
                    id="email_user",
                    placeholder="Seu email",
                    value=current_user.api_key
                ),
                dbc.FormText(
                    "Entre com email (Gmail).", color="secondary"
                ),        
                dmc.Space(h=20),   
                dbc.Label("Senha STMP", html_for="stmp_password"),
                dbc.Input(
                    type="text",
                    id="stmp_password",
                    placeholder="Sua senha STMP",
                    value=current_user.api_key
                ), 
                dbc.FormText(
                    "Entre com sua senha STMP.", color="secondary"
                ),
                dmc.Space(h=20),
                dbc.Label("Chave API", html_for="open-api-key"),
                dbc.Input(
                    type="text",
                    id="open-api-key",
                    placeholder="Sua chave OpenAI",
                    value=current_user.api_key
                ),
                dbc.FormText(
                    "Entre com sua chave da API OpenAI.", color="secondary"
                ),
            ],
            className="mb-3",
        )
        button = dmc.Center(
            style={"height": "auto", "width": "100%"},
            children=[
                dmc.Button(
                    "Salvar Dados",
                    leftIcon=DashIconify(icon="fluent:database-plug-connected-20-filled"),
                    className="my-2",
                    id= "btn-update-user",
                )
            ],
        )
        modal = dmc.Modal(
            title="Falha ao realizar Login",
            id="modal-update-user",
            centered=True,
            zIndex=10000,
            opened= False,
            children=[dmc.Text("Verifique seu Email e sua Senha")],
        )

        form=  dmc.LoadingOverlay(dbc.Form([api_key_input], class_name="mt-4", id="form-user"))
        content = dbc.Container(
            [dbc.Col([alert, redirect_div, form, button,modal])], fluid=False)
        body = html.Div([navbar(icon=None, profile_active=True), content])
        return body
    else:
        return dcc.Location(pathname="/login", id="someid_login")
