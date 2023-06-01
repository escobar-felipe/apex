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
                DashIconify(icon=icon, color=color,width=50),
                html.Div(
                    [
                        dmc.Title(f"{label.title()}", order=4),
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
        alert = dmc.Alert(dmc.Text(f"""Aqui se encontram todos os seus relatórios, para encaminhar seu relatório complete o campo "EMAIL" no relatório desejado e clique em "ENVIAR".""", size="lg",), title=dmc.Text(
            "Relatórios", size="xl"), color="yellow", className="mt-4")
        
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
                        dmc.Group([dmc.TextInput(id={'type': 'input_email','index': result_id.result_id},placeholder="Email", style={"width": 200}),
                        dmc.LoadingOverlay(dmc.Button("Enviar Email",id={'type': 'button_send','index': result_id.result_id}, n_clicks=0), loaderProps={"variant": "oval", "color": "blue", "size": "sm"}, )], className="mb-2"),
                        html.Iframe(srcDoc=result.get(),  style={'width': '100%', 'height': '500px'})]
                elif result.state == 'PENDING':
                    task_status_singleton.set_status(result_id.result_id, "PENDING")
                    icon = "line-md:downloading-loop"
                    color = "blue"
                    content = [dmc.Title(f"Processando seu relatório, dentro de instântes ele estára pronto.", order=3)]
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
            children_accordion.append(dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30),"Nenhum relatório encontrado"], className="m-2 mt-5")]))
                    
        list_tasks = html.Div([dmc.Accordion(
            chevronPosition="right",
            variant="contained",
            children=children_accordion,
            className="mt-4",
            id='center-body'
        )])
        interval = dcc.Interval(id='interval', interval=5000)
    
        content = dbc.Container(
            [dbc.Col([alert,list_tasks,interval])], fluid=False)
        body = html.Div([navbar(icon=None, my_search_active=True), content])
        return body
    else:
        return dcc.Location(pathname="/apex/login", id="redirect_login_page")
