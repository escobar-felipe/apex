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
from src.utils.tenancy import get_current_tenant_id
from src.ext.database import db
from src.utils.report_views import get_report_html, report_email_controls, report_review_components

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


def report_processing_content(status):
    messages = {
        "PENDING": "Relatório na fila de processamento.",
        "STARTED": "Relatório em processamento.",
        "RETRY": "Houve uma falha temporária. Uma nova tentativa será executada automaticamente.",
    }
    return [dmc.Title(messages.get(status, "Relatório em processamento."), order=3)]


def report_failure_content(result):
    message = str(result.info)
    if message.startswith("RuntimeError(") and message.endswith(")"):
        message = message[len("RuntimeError("):-1].strip("'\"")

    if message == "You exceeded your current quota, please check your plan and billing details.":
        return [dmc.Title("Você excedeu sua cota atual, verifique seu plano e detalhes de cobrança.", order=3)]
    return [dmc.Title(message, order=3)]


def sync_report_payload(search_result, payload):
    if not isinstance(payload, dict):
        return
    changed = False
    report_html = get_report_html(payload)
    if search_result.status != "ready":
        search_result.status = "ready"
        changed = True
    if payload.get("data") and not search_result.report_data:
        search_result.report_data = payload.get("data")
        changed = True
    if report_html and not search_result.report_html:
        search_result.report_html = report_html
        changed = True
    if changed:
        db.session.commit()


def report_success_content(result, modal, search_result):
    payload = result.get()
    if isinstance(payload, dict) and payload.get("error"):
        return [dmc.Center([dmc.Text([DashIconify(icon="ic:baseline-search", width=30), f"{payload['error']}"], className="m-2 mt-5")])]

    sync_report_payload(search_result, payload)
    safe_payload = get_report_html(payload)
    review = report_review_components(payload)
    return [
        modal,
        dmc.Alert(
            "Revise o relatório abaixo antes de enviar ao cliente. Ajuste assunto, mensagem e destinatário no formulário de envio.",
            title="Relatório pronto para revisão",
            color="green",
            className="apex-alert mb-3",
        ),
        review if review else html.Iframe(srcDoc=safe_payload, sandbox="", className="apex-report-frame", style={'width': '100%', 'height': '540px'}),
        dmc.Divider(label="Envio ao cliente", labelPosition="center", className="my-4"),
        report_email_controls(result.id, search_result.title),
    ]


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
        
        results_id = SearchResult.query.filter_by(user_id=current_user.id, tenant_id=get_current_tenant_id()).order_by(SearchResult.created_at.desc()).all(),
        children_accordion = []
        if len(results_id[0])> 0:
            for result_id in results_id[0]:
                result = AsyncResult(result_id.result_id)
                modal = html.Div(
                    [
                        dmc.Modal(
                            title="Envio de email",
                            id={'type': 'modal-send-email','index': result_id.result_id},
                            centered=True,
                            zIndex=10000,
                            children=[],
                        )
                    ]
                )
                if result.status == 'SUCCESS':
                    task_status_singleton.set_status(result_id.result_id, "SUCCESS")
                    icon = "icon-park-twotone:check-one"
                    color = "green"
                    content = report_success_content(result, modal, result_id)
                elif result.state in {"PENDING", "STARTED", "RETRY"}:
                    task_status_singleton.set_status(result_id.result_id, result.state)
                    icon = "line-md:downloading-loop"
                    color = "blue"
                    content = report_processing_content(result.state)
                elif result.state == 'FAILURE':
                    task_status_singleton.set_status(result_id.result_id, "FAILURE")
                    if result_id.status != "failed":
                        result_id.status = "failed"
                        db.session.commit()
                    icon = "ic:twotone-error"
                    color = "red"
                    content = report_failure_content(result)
                else:
                    task_status_singleton.set_status(result_id.result_id, result.state)
                    icon = "line-md:downloading-loop"
                    color = "blue"
                    content = report_processing_content(result.state)


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
