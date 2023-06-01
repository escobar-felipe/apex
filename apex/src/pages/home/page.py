from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from flask_login import current_user
from src.pages.pages_components.navbar import navbar
import dash_mantine_components as dmc
from dash_iconify import DashIconify


register_page(__name__, path='/', title="Área de Pesquisa")


def layout(**query_strings):
    if current_user.is_authenticated:
        redirect_div = html.Div( id="redirect-home")
        alert = dmc.Alert(dmc.Text(f"""Bem vindo, {current_user.username}! Na área de pesquisa você pode buscar por artigos parem analisados por nossa inteligência artificial. Após clicar no botão de pesquisa, 
                                   você verá uma lista de artigos relevantes com base nas suas palavras-chave.
                                   Uma vez que a busca for finalizada vá para aba de "Relatório GPT" após ter cadastrado sua Chave OpenAI! Nessa aba poderar selecionar os artigos para serem analisados,""", size="lg"), title= dmc.Text("Área de pesquisa!", size="xl"), color="yellow", className="mt-4")
        label_form = dmc.Text("Pesquise Aqui", size="lg" , className="mt-4 mx-2", weight=700)
        text_input = dmc.TextInput(placeholder="Digite seu texto para realizar a busca",icon=DashIconify(icon="ic:baseline-search", width=24),id='search-state',size="md",className="mt-2")
        button  = dmc.Button("Pesquisar", leftIcon=DashIconify(icon="ic:baseline-content-paste-search", width=22),className="mt-2" , size="md",fullWidth=True, id="button-search"),
        form_search =dmc.Grid(
                        children=[
                            dmc.Col(html.Div(text_input), span=10),
                            dmc.Col(html.Div(button), span="auto"),
                        ],
                        gutter="xl",
                    )
        
        store_search = dcc.Store(id="search_value",data=None,storage_type="memory")
        store_links = dcc.Store(id="search_links",data=None,storage_type="memory")

        report_tab =[
            dmc.LoadingOverlay(dbc.Col([
            html.Div([],id='alert-div'),
            dmc.Title(f"Relatório GPT", order=1, className="mt-4"),
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
                        title="Sua chaveAPI",
                        children=[
                            dmc.Text(
                                [
                                    current_user.api_key,
                                ],
                                className="text-break",
                                color="dimmed",
                                size="sm",
                            ),
                        ],
                    ),
                    dmc.TimelineItem(
                        title="Qtd. de texto encontrados:",
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
                        style={"width": "400"},
                        id ="multiselect-text",
                    ),
                dbc.FormText(
                    "Selecione os textos para serem analisados", color="secondary"
                )]),
            dmc.Button("Gerar relatório", leftIcon=DashIconify(icon="mdi:report-box", width=22),className="p-2 my-4" , size="md",fullWidth=True,id="button-report")],class_name="col-md-12"))
        ]
   

        tabs = dmc.LoadingOverlay(dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.Tab(dmc.Text("Google", size="md"), icon=DashIconify(icon="dashicons:google", width=22),value="google", id="google_tittle",),
                            dmc.Tab(dmc.Text("Twitter", size="md"), icon=DashIconify(icon="dashicons:twitter",width=22),value="twitter", id="twitter_tittle"),
                            dmc.Tab(dmc.Text("Facebook", size="md"), icon=DashIconify(icon="dashicons:facebook",width=22), value="facebook", id="facebook_tittle"),
                            dmc.Tab(dmc.Text("Relatório GPT", size="md"), icon=DashIconify(icon="carbon:report",width=22), value="chatgpt", id="chatgpt_tittle",disabled=True),
                        ]
                    ),
                    dmc.TabsPanel(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Faça uma pesquisa para encontrar os resultados"], className="m-2 mt-5")]), value="google", id="google_tabs"),
                    dmc.TabsPanel(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Faça uma pesquisa para encontrar os resultados"], className="m-2 mt-5")]), value="twitter" ,id="twitter_tabs"),
                    dmc.TabsPanel(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Faça uma pesquisa para encontrar os resultados"], className="m-2 mt-5")]), value="facebook", id="facebook_tabs"),
                    dmc.TabsPanel(report_tab, value="chatgpt", id="chatgpt_tabs"),
                ],
                value="google", className="mt-4"
            ), loaderProps={"variant": "dots", "color": "blue", "size": "xl"},)
        content = dbc.Container([dbc.Col([store_search, store_links,alert,label_form,form_search,tabs, redirect_div])], fluid=False)
        body = html.Div([navbar(icon=None, search_active=True),content]) 
        return body   
    else:
        return dcc.Location(pathname="/apex/login", id="someid_doesnt_matter")