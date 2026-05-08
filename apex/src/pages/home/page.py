from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from flask_login import current_user
from src.pages.pages_components.navbar import navbar
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.utils.security import mask_secret


register_page(__name__, path='/', title="Área de Pesquisa")


def get_missing_account_fields(user):
    missing_fields = []
    if not user.email:
        missing_fields.append("Email")
    if not user.stmp_password:
        missing_fields.append("Senha SMTP")
    if not user.api_key:
        missing_fields.append("Chave API OpenAI")
    if not user.serpapi_key:
        missing_fields.append("Chave SerperAPI")
    return missing_fields


def layout(**query_strings):
    if current_user.is_authenticated:
        missing_account_fields = get_missing_account_fields(current_user)
        search_disabled = len(missing_account_fields) > 0
        redirect_div = html.Div( id="redirect-home")
        missing_data_modal = dmc.Modal(
            title="Complete os dados da sua conta",
            id="modal-missing-account-data",
            centered=True,
            zIndex=10000,
            opened=search_disabled,
            children=[
                dmc.Text(
                    "Para realizar pesquisas, preencha os dados abaixo em Minha Conta.",
                    color="dimmed",
                    className="mb-3",
                ),
                dmc.List(
                    [dmc.ListItem(field) for field in missing_account_fields],
                    spacing="xs",
                    withPadding=True,
                    className="mb-3",
                ),
                dmc.Group(
                    [
                        dcc.Link(
                            dmc.Button(
                                "Ir para Minha Conta",
                                leftIcon=DashIconify(icon="mdi:user-edit", width=20),
                                className="apex-button",
                                color="#504cab",
                            ),
                            href="/profile",
                        ),
                        dcc.Link(
                            dmc.Button(
                                "Ver instruções",
                                leftIcon=DashIconify(icon="mdi:help-circle-outline", width=20),
                                className="apex-button-outline",
                                variant="outline",
                                color="#504cab",
                            ),
                            href="/profile/instructions",
                        ),
                    ],
                    position="apart",
                ),
            ],
        )
        page_header = html.Div(
            [
                dmc.Title("Área de Pesquisa", order=1, className="apex-page-title"),
                dmc.Text(
                    f"Bem-vindo, {current_user.username}. Busque artigos e conteúdos por palavra-chave, revise os resultados e gere um relatório com apoio da IA.",
                    className="apex-page-subtitle",
                ),
            ],
            className="mt-4 mb-4",
        )
        alert = dmc.Alert(
            dmc.Text(
                "Após pesquisar, os resultados aparecerão nas abas por origem. Quando a busca terminar, use a aba Relatório GPT para selecionar os textos que serão analisados.",
                size="md",
            ),
            title=dmc.Text("Fluxo de pesquisa", weight=700),
            color="yellow",
            className="apex-alert mb-4",
        )
        label_form = dmc.Text("Termo de busca", size="md", weight=700, className="mb-2")
        text_input = dmc.TextInput(placeholder="Digite uma marca, tema ou palavra-chave",icon=DashIconify(icon="ic:baseline-search", width=24),id='search-state',size="md")
        button  = dmc.Button("Pesquisar", leftIcon=DashIconify(icon="ic:baseline-content-paste-search", width=22), size="md", fullWidth=True, className="apex-button", color="#504cab", disabled=search_disabled, id="button-search")
        form_search =dmc.Grid(
                        children=[
                            dmc.Col(html.Div([label_form, text_input]), span=12, md=9),
                            dmc.Col(html.Div(button), span=12, md=3),
                        ],
                        gutter="md",
                        className="apex-search-grid",
                    )
        
        store_search = dcc.Store(id="search_value",data=None,storage_type="memory")
        store_links = dcc.Store(id="search_links",data=None,storage_type="memory")

        report_tab =[
            dmc.LoadingOverlay(dbc.Col([
            html.Div([],id='alert-div'),
            dmc.Alert("Selecione pelo menos um texto para gerar o relatório.", title="Ação necessária", color="red", hide=True, duration=5000, id="alert-multi-select",className="mt-3"),
            dmc.Title(f"Relatório GPT", order=2, className="apex-page-title mt-4"),
            dmc.Timeline(
                active=3,
                bulletSize=15,
                lineWidth=2,
                className='mt-4',
                children=[
                    dmc.TimelineItem(
                        title="Dados da sua pesquisa:",
                        children=[
                            dmc.Text(
                                color="dimmed",
                                size="sm",
                                id='search-text'
                            ),
                        ],
                    ),
                    dmc.TimelineItem(
                        title="Sua chave API",
                        children=[
                            dmc.Text(
                                [
                                    mask_secret(current_user.api_key),
                                ],
                                className="text-break",
                                color="dimmed",
                                size="sm",
                            ),
                        ],
                    ),
                    dmc.TimelineItem(
                        title="Quantidade de textos encontrados:",
                        children=[
                            dmc.Text(
                                color="dimmed",
                                size="sm",
                                id='qtd-text'
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
            [
                dbc.Label("Selecione os textos:", html_for="multiselect-text"),
            dmc.MultiSelect(
                        data=[],
                        searchable=True,
                        nothingFound="Nenhuma opção encontrada",
                        style={"width": "100%"},
                        id ="multiselect-text",
                        required=True
                    ),
                dbc.FormText(
                    "Selecione os textos para serem analisados", color="secondary"
                )]),
            dmc.Divider(label="Configuração do relatório", labelPosition="center", className="my-4"),
            html.Div(
                [
                    dmc.Select(
                        label="Tipo de relatório",
                        id="report-type",
                        value="monitoring",
                        data=[
                            {"label": "Monitoramento executivo", "value": "monitoring"},
                            {"label": "Risco de reputação", "value": "reputation"},
                            {"label": "Oportunidades de comunicação", "value": "opportunity"},
                            {"label": "Clipping analítico", "value": "clipping"},
                        ],
                    ),
                    dmc.Select(
                        label="Tom",
                        id="report-tone",
                        value="executive",
                        data=[
                            {"label": "Executivo", "value": "executive"},
                            {"label": "Consultivo", "value": "consultative"},
                            {"label": "Direto", "value": "direct"},
                        ],
                    ),
                    dmc.TextInput(
                        label="Público-alvo",
                        id="report-audience",
                        placeholder="Ex.: diretoria, cliente final, time de comunicação",
                        value="diretoria e cliente",
                    ),
                    dmc.Textarea(
                        label="Objetivo da análise",
                        id="report-objective",
                        placeholder="Ex.: avaliar riscos, oportunidades e próximos passos",
                        autosize=True,
                        minRows=2,
                        value="identificar principais achados, riscos, oportunidades e recomendações práticas",
                        className="apex-field-full",
                    ),
                ],
                className="apex-form-grid",
            ),
            dmc.Button("Gerar relatório", leftIcon=DashIconify(icon="mdi:report-box", width=22),className="p-2 my-4 apex-button" , size="md",fullWidth=True,color="#504cab",id="button-report")],class_name="col-md-12 apex-soft-panel"))
        ]
   

        tabs = dmc.LoadingOverlay(dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.Tab(dmc.Text("Google News", size="md"), icon=DashIconify(icon="dashicons:google", width=22),value="google", id="google_tittle",),
                            dmc.Tab(dmc.Text("X/Twitter", size="md"), icon=DashIconify(icon="dashicons:twitter",width=22),value="twitter", id="twitter_tittle"),
                            dmc.Tab(dmc.Text("Facebook", size="md"), icon=DashIconify(icon="dashicons:facebook",width=22), value="facebook", id="facebook_tittle"),
                            dmc.Tab(dmc.Text("Relatório GPT", size="md"), icon=DashIconify(icon="carbon:report",width=22), value="chatgpt", id="chatgpt_tittle",disabled=True),
                        ]
                    ),
                    dmc.TabsPanel(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=34),"Faça uma pesquisa para encontrar os resultados"], className="m-2 mt-5")], className="apex-empty-state"), value="google", id="google_tabs"),
                    dmc.TabsPanel(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=34),"Faça uma pesquisa para encontrar os resultados"], className="m-2 mt-5")], className="apex-empty-state"), value="twitter" ,id="twitter_tabs"),
                    dmc.TabsPanel(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=34),"Faça uma pesquisa para encontrar os resultados"], className="m-2 mt-5")], className="apex-empty-state"), value="facebook", id="facebook_tabs"),
                    dmc.TabsPanel(report_tab, value="chatgpt", id="chatgpt_tabs"),
                ],
                value="google", className="apex-tabs"
            ), loaderProps={"variant": "dots", "color": "#504cab", "size": "xl"},)
        content = dbc.Container([dbc.Col([store_search, store_links,missing_data_modal,page_header,alert,html.Div(form_search, className="apex-panel mb-4"),tabs, redirect_div])], fluid=False, class_name="apex-container")
        body = html.Div([navbar(icon=None, search_active=True),content], className="apex-shell")
        return body   
    else:
        return dcc.Location(pathname="/login", id="someid_doesnt_matter")
