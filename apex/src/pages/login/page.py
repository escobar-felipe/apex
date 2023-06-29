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
            title="Falha ao realizar Login",
            id="modal-centered",
            centered=True,
            zIndex=10000,
            opened= False,
            children=[dmc.Text("Verifique seu Email e sua Senha")],
        )
        form = html.Div(
                style={"width":300},
                children=dmc.LoadingOverlay(
                        dmc.Stack(
                        id="loading-form",
                        children=[
                                html.Img(src=get_asset_url("img/thambnail.jpeg"), width=200,className="my-3 mx-auto"),
                                dmc.TextInput(
                                label="Usuário",
                                placeholder="Digite seu nome de usuário",
                                icon=DashIconify(icon="radix-icons:person"),
                                id='username-input'
                                ),
                                dmc.PasswordInput(
                                label="Senha",
                                placeholder="Digite sua senha",
                                icon=DashIconify(icon="bi:shield-lock"),
                                id='password-input'
                                ),
                                dmc.Button(
                                "Entrar",  id='login-button', variant="outline", fullWidth=True, className="mt-2" ,color="#2b2d32"
                                ),
                        ], 
                        )
                ), className="rounded bg-white p-3"
                )



        return dmc.Center([modal,form, html.Div(id="redirect-login")], style={
                "position": "fixed",
                "width": "100%",
                "height": "100%",
                "left": 0,
                "top": 0,
        } , className="col bg-fixed")

