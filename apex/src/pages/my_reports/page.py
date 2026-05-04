from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from flask_login import current_user
from src.pages.pages_components.navbar import navbar
import dash_mantine_components as dmc
from src.models import SearchResult
from celery.result import AsyncResult
from dash_iconify import DashIconify
from src.utils.tasks_result_utils import task_status_singleton
from datetime import timedelta

register_page(__name__, path='/my_reports', title="Minhas Pesquisas")

def create_accordion_label(label:str, icon,color, description):
    return dmc.AccordionControl(
        dmc.Group(
            [
                DashIconify(icon=icon, color=color,width=42),
                html.Div(
                    [
                        dmc.Title(f"{label.title()}", order=4, className="mb-1"),
                        dmc.Text(f"Data do relatório: {description}", size="sm", weight=400, color="dimmed"),
                    ]
                ),
            ]
        )
    )


def create_accordion_content(content):
    return dmc.AccordionPanel(dmc.Text(content, size="sm"))


def layout(**query_strings):
    if current_user.is_authenticated:
        page_header = html.Div(
            [
                dmc.Title("Meus Relatórios", order=1, className="apex-page-title"),
                dmc.Text(
                    "Acompanhe relatórios em processamento, revise os resultados prontos e envie análises por email.",
                    className="apex-page-subtitle",
                ),
            ],
            className="mt-4 mb-4",
        )
        alert = dmc.Alert(dmc.Text(f"""Para encaminhar um relatório, preencha o campo "Email" no item desejado e clique em "Enviar Email".""", size="md",), title=dmc.Text(
            "Relatórios salvos", weight=700), color="yellow", className="apex-alert mb-4")
        
        results_id = SearchResult.query.filter_by(user_id=current_user.id).order_by(SearchResult.created_at.desc()).all(),
        children_accordion = []
        if len(results_id[0])> 0:
            for result_id in results_id[0]:
                result = AsyncResult(result_id.result_id)
                modal = html.Div(
                    [
                        dmc.Modal(
                            title="Menssagem!",
                            id={'type': 'modal-send-email','index': result_id.result_id},
                            centered=True,
                            zIndex=10000,
                            children=[dmc.Center([DashIconify(id ='icon-modal',icon="line-md:circle-twotone-to-confirm-circle-twotone-transition",color='green', width=100)])],
                        )
                    ]
                )
                if result.status == 'SUCCESS':
                    task_status_singleton.set_status(result_id.result_id, "SUCCESS")
                    icon = "icon-park-twotone:check-one"
                    color = "green"
                    if 'error' in result.get():
                        content = [dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),f"{result.get()['error']}"], className="m-2 mt-5")])]
                    content =  [
                        modal,
                        dmc.Group([dmc.TextInput(id={'type': 'input_email','index': result_id.result_id},placeholder="Email", style={"width": 260}),
                        dmc.LoadingOverlay(dmc.Button("Enviar Email",id={'type': 'button_send','index': result_id.result_id}, n_clicks=0, className="apex-button", color="#504cab"), loaderProps={"variant": "oval", "color": "#504cab", "size": "sm"}, )], className="mb-3 apex-actions-row"),
                        html.Iframe(srcDoc=result.get(),  className="apex-report-frame", style={'width': '100%', 'height': '540px'})]
                elif result.state == 'PENDING':
                    task_status_singleton.set_status(result_id.result_id, "PENDING")
                    icon = "line-md:downloading-loop"
                    color = "blue"
                    content = [dmc.Title(f"Processando seu relatório, dentro de instantes ele estará pronto.", order=3)]
                    peding = True
                elif result.state == 'FAILURE':
                    task_status_singleton.set_status(result_id.result_id, "FAILURE")
                    icon = "ic:twotone-error"
                    color = "red"
                    if str(result.info) == "You exceeded your current quota, please check your plan and billing details.":
                        content = [dmc.Title(f"Você excedeu sua cota atual, verifique seu plano e detalhes de cobrança.", order=3)]
                    else:
                        content = [dmc.Title(f"{str(result.info)}", order=3)]
                else:
                    task_status_singleton.set_status(result_id.result_id, "FAILURE")
                    icon = "ic:twotone-error"
                    color = "red"
                    if str(result.info) == "You exceeded your current quota, please check your plan and billing details.":
                        content = [dmc.Title(f"Você excedeu sua cota atual, verifique seu plano e detalhes de cobrança.", order=3)]
                    else:
                        content = [dmc.Title(f"{str(result.info)}", order=3)]


                item = dmc.AccordionItem(
                            [
                                create_accordion_label(
                                    f"{result_id.title}", icon, color, f'{(result_id.created_at - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")}'
                                ),
                                create_accordion_content(content),
                            ],
                            value=f"{result_id.result_id}",
                        )
                children_accordion.append(item)
        else:
            children_accordion.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=34),"Nenhum relatório encontrado"], className="m-2 mt-5")], className="apex-empty-state"))
                    
        list_tasks = html.Div([dmc.Accordion(
            chevronPosition="right",
            variant="contained",
            children=children_accordion,
            className="apex-panel",
            id='center-body'
        )])
        interval = dcc.Interval(id='interval', interval=5000)
    
        content = dbc.Container(
            [dbc.Col([page_header, alert,list_tasks,interval])], fluid=False, class_name="apex-container")
        body = html.Div([navbar(icon=None, my_search_active=True), content], className="apex-shell")
        return body
    else:
        return dcc.Location(pathname="/login", id="redirect_login_page")
