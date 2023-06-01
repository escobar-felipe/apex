import dash_bootstrap_components as dbc
from dash import html, get_asset_url
from src.config.constantes.app_constants import AppConstants
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask import session

def navbar(icon = None , search_active= None,profile_active = None, my_search_active = None ):
    LOGO = get_asset_url("img/apex.png")
    icon_bar = dbc.Row(
        [
            dbc.Col(
                 html.A(DashIconify(icon="clarity:logout-line", width=30), className="link-light text-white" , href="/apex/logout"),
                width="auto",
            ),
        ],
        className="g-0",
        align="center",
    )

    navbar_up = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="https://apexconteudo.com.br/wp-content/themes/tema/img/logo-w.svg", height="40px",
                                    className="rounded")),
                            dbc.Col(dbc.NavbarBrand("",
                                    className="ms-2 text-uppercase fw-bold")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    style={"textDecoration": "none"},
                ),
                icon_bar,
            ], fluid=False
        ),
        color="#2b2d32",
        dark=True,
    )
    def get_icon(icon):
        return DashIconify(icon=icon, height=16 , className="m-1")
    
    navbar_down = dbc.Navbar(
        dbc.Container(
    [
        
        dmc.NavLink(
            label=[dmc.Text([get_icon(icon="bi:house-door-fill"),"Área de Pesquisa"])],
            className="text-center border",
            active=search_active,
            href="/apex/"
        ),        
        dmc.NavLink(
            label=[dmc.Text([get_icon(icon="material-symbols:image-search"),"Meus Relatórios"])],
            className="text-center border",
            active=my_search_active,
            href="/apex/my_reports"
        ),
        dmc.NavLink(
            label=[dmc.Text([get_icon(icon="mdi:user"),"Minha Conta"])],
            className="text-center border",
            active=profile_active,
            href="/apex/profile"
        ),

        
    ], fluid=False, class_name="text-center"
        ),
        color="light",
        dark=False,
    )

   
    return  html.Header([navbar_up, navbar_down] )