from dash import html, register_page, get_asset_url, dcc
from src.config.constantes.app_constants import AppConstants
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import current_user

register_page(__name__, path='/login', title="Login")

def layout(**query_strings):
        if current_user.is_authenticated:
                return dcc.Location(pathname="/", id="redirect-home-login")
        modal = dmc.Modal(
            title="Login não realizado",
            id="modal-centered",
            centered=True,
            zIndex=10000,
            opened= False,
            children=[dmc.Text("Verifique usuário e senha.")],
        )
        form = html.Div(
                className="apex-login-card",
                children=dmc.LoadingOverlay(
                        dmc.Stack(
                        id="loading-form",
                        spacing="md",
                        children=[
                                dmc.Center(
                                        html.Img(
                                                src=get_asset_url("img/thambnail.jpeg"),
                                                className="apex-login-logo my-2",
                                        )
                                ),
                                html.Div(
                                        [
                                                dmc.Title("Acesse sua conta", order=2, className="apex-page-title text-center"),
                                                dmc.Text("Entre para pesquisar conteúdos, gerar relatórios e acompanhar seus resultados.", color="dimmed", align="center", size="sm"),
                                        ],
                                        className="mb-2",
                                ),
                                dmc.TextInput(
                                label="Usuário",
                                placeholder="Digite seu nome de usuário",
                                icon=DashIconify(icon="radix-icons:person"),
                                id='username-input',
                                size="md",
                                autoComplete="username",
                                ),
                                dmc.PasswordInput(
                                label="Senha",
                                placeholder="Digite sua senha",
                                icon=DashIconify(icon="bi:shield-lock"),
                                id='password-input',
                                size="md",
                                autoComplete="current-password",
                                ),
                                dmc.Button(
                                "Entrar",  id='login-button', fullWidth=True, className="mt-2 apex-button", color="#504cab", size="md"
                                ),
                        ], 
                        )
                )
                )



        return dmc.Center([modal,form, html.Div(id="redirect-login")], style={
                "position": "fixed",
                "width": "100%",
                "height": "100%",
                "left": 0,
                "top": 0,
        } , className="apex-login-page")
