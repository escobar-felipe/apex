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


def official_link(label, description, href, icon, tag):
    return html.A(
        [
            html.Div(DashIconify(icon=icon, width=24), className="apex-official-link-icon"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(label, className="apex-official-link-title"),
                            html.Span(tag, className="apex-official-link-tag"),
                        ],
                        className="apex-official-link-heading",
                    ),
                    html.Span(description, className="apex-official-link-description"),
                ],
                className="apex-official-link-copy",
            ),
            DashIconify(icon="mdi:open-in-new", width=18, className="apex-official-link-external"),
        ],
        href=href,
        target="_blank",
        rel="noreferrer",
        className="apex-official-link",
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

    official_links = html.Div(
        [
            dmc.Title("Links oficiais", order=2, className="apex-section-title"),
            dmc.Text(
                "Use somente páginas oficiais para criar chaves, revisar acesso e resolver erros de credenciais.",
                color="dimmed",
                className="mb-3",
            ),
            html.Div(
                [
                    official_link(
                        "Conta Google",
                        "Revise login, segurança e verificação em duas etapas da conta remetente.",
                        "https://myaccount.google.com/",
                        "simple-icons:google",
                        "Email",
                    ),
                    official_link(
                        "Senhas de aplicativo Google",
                        "Gere a senha usada no campo Senha SMTP para envio de relatórios.",
                        "https://myaccount.google.com/apppasswords",
                        "mdi:lock-check-outline",
                        "SMTP",
                    ),
                    official_link(
                        "OpenAI API Keys",
                        "Crie ou revogue a chave usada para gerar relatórios com IA.",
                        "https://platform.openai.com/api-keys",
                        "simple-icons:openai",
                        "IA",
                    ),
                    official_link(
                        "OpenAI Billing",
                        "Verifique saldo, limites e cobrança quando houver erro de cota.",
                        "https://platform.openai.com/settings/organization/billing/overview",
                        "mdi:credit-card-check-outline",
                        "Cota",
                    ),
                    official_link(
                        "Serper API Key",
                        "Copie a chave usada para buscar resultados externos.",
                        "https://serper.dev/api-key",
                        "mdi:magnify-scan",
                        "Busca",
                    ),
                    official_link(
                        "Serper Dashboard",
                        "Acompanhe consumo, plano e limites da integração de busca.",
                        "https://serper.dev/dashboard",
                        "mdi:view-dashboard-outline",
                        "Limites",
                    ),
                ],
                className="apex-official-links",
            ),
        ],
        className="apex-soft-panel mt-4",
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
        [dbc.Col([page_header, html.Div([instructions, official_links, actions], className="apex-panel")])],
        fluid=False,
        class_name="apex-container",
    )

    return html.Div([navbar(icon=None, profile_active=True), content], className="apex-shell")
