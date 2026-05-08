from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
from flask_login import current_user

def navbar(icon=None, search_active=None, profile_active=None, my_search_active=None, admin_active=None):
    icon_bar = dbc.Row(
        [
            dbc.Col(
                html.A(
                    [
                        DashIconify(icon="clarity:logout-line", width=20),
                        html.Span("Sair"),
                    ],
                    className="apex-logout-link",
                    href="/logout",
                    title="Sair",
                ),
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
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Span("apex", className="apex-wordmark")
                            ),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    className="apex-brand-link",
                    href="/",
                ),
                icon_bar,
            ],
            class_name="apex-navbar-container",
            fluid=False,
        ),
        color="#2b2d32",
        dark=True,
        class_name="apex-navbar-top",
    )

    def get_icon(icon):
        return DashIconify(icon=icon, height=18, className="me-2")

    def nav_label(icon, label):
        return dmc.Text([get_icon(icon=icon), label], className="apex-nav-label")
    
    nav_links = [
        dmc.NavLink(
            label=[nav_label("bi:search", "Pesquisar")],
            className="apex-nav-link",
            active=search_active,
            href="/",
        ),
        dmc.NavLink(
            label=[nav_label("carbon:report", "Relatórios")],
            className="apex-nav-link",
            active=my_search_active,
            href="/my_reports",
        ),
        dmc.NavLink(
            label=[nav_label("mdi:account-circle-outline", "Conta")],
            className="apex-nav-link",
            active=profile_active,
            href="/profile",
        ),
    ]

    if current_user.is_authenticated and current_user.admin:
        nav_links.append(
            dmc.NavLink(
                label=[nav_label("mdi:shield-account-outline", "Admin")],
                className="apex-nav-link",
                active=admin_active,
                href="/admin",
            )
        )

    navbar_down = dbc.Navbar(
        dbc.Container(
            nav_links,
            fluid=False,
            class_name="apex-nav-wrap",
        ),
        color="light",
        dark=False,
        class_name="apex-navbar-bottom",
    )

    return html.Header([navbar_up, navbar_down])
