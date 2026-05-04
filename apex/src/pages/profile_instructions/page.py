from dash import dcc, html, register_page
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from flask_login import current_user
from src.pages.pages_components.navbar import navbar


register_page(__name__, path="/profile/instructions", title="Instruções da Conta")


def instruction_card(icon, title, description, items):
    return html.Div(
        [
            html.Div(DashIconify(icon=icon, width=26), className="apex-step-icon"),
            dmc.Title(title, order=3, className="mb-2"),
            dmc.Text(description, color="dimmed", className="mb-3"),
            dmc.List(
                [dmc.ListItem(item) for item in items],
                spacing="xs",
                size="sm",
                withPadding=True,
            ),
        ],
        className="apex-step-card",
    )


def layout(**query_strings):
    if not current_user.is_authenticated:
        return dcc.Location(pathname="/login", id="redirect-profile-instructions")

    page_header = html.Div(
        [
            dmc.Title("Como preencher Minha Conta", order=1, className="apex-page-title"),
            dmc.Text(
                "Preencha estes dados para habilitar busca, geração de relatórios e envio por email.",
                className="apex-page-subtitle",
            ),
        ],
        className="mt-4 mb-4",
    )

    instructions = html.Div(
        [
            instruction_card(
                "mdi:email-outline",
                "Email",
                "Use o email que fará o envio dos relatórios.",
                [
                    "Informe uma conta Gmail válida.",
                    "Este email será usado como remetente ao clicar em Enviar Email nos relatórios.",
                    "Confira se não há espaços antes ou depois do endereço.",
                ],
            ),
            instruction_card(
                "mdi:lock-check-outline",
                "Senha SMTP",
                "Use uma senha de aplicativo, não a senha normal da sua conta.",
                [
                    "Ative a verificação em duas etapas na conta Google.",
                    "Gere uma senha de aplicativo para email ou SMTP.",
                    "Cole a senha gerada no campo Senha SMTP.",
                ],
            ),
            instruction_card(
                "simple-icons:openai",
                "Chave API OpenAI",
                "Esta chave permite que o sistema gere os relatórios com IA.",
                [
                    "Crie ou copie uma chave no painel da OpenAI.",
                    "A chave normalmente começa com sk-.",
                    "Mantenha saldo, limite ou plano ativo para evitar erro de cota.",
                ],
            ),
            instruction_card(
                "mdi:magnify-scan",
                "Chave SerperAPI",
                "Esta chave permite buscar resultados no Google/News via Serper.",
                [
                    "Crie ou copie uma chave no painel da Serper.",
                    "Cole a chave no campo Chave SerperAPI.",
                    "Sem essa chave, a busca pode não retornar resultados.",
                ],
            ),
        ],
        className="apex-instruction-grid",
    )

    actions = dmc.Group(
        [
            dcc.Link(
                dmc.Button(
                    "Voltar para Minha Conta",
                    leftIcon=DashIconify(icon="mdi:arrow-left", width=20),
                    className="apex-button",
                    color="#504cab",
                ),
                href="/profile",
            ),
        ],
        className="mt-4",
    )

    content = dbc.Container(
        [dbc.Col([page_header, html.Div([instructions, actions], className="apex-panel")])],
        fluid=False,
        class_name="apex-container",
    )

    return html.Div([navbar(icon=None, profile_active=True), content], className="apex-shell")
