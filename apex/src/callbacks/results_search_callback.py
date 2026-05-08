

from dash_extensions.enrich import Output, Input, State, callback,  no_update
from datetime import timedelta
from datetime import datetime
from dash import ctx, html, dcc, MATCH, Patch,ALL
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from src.ext.database import db
from src.models import EmailAudit, SearchResult
from flask_login import current_user
from dash_iconify import DashIconify
from celery.result import AsyncResult
from dash.exceptions import PreventUpdate
from src.utils.report_html import sanitize_report_html
from src.utils.report_views import get_report_html, report_email_controls, report_review_components
from src.utils.send_email import EmailSendError, SendEmail, is_valid_email
from src.utils.tasks_result_utils import task_status_singleton
from src.utils.tenancy import get_current_tenant_id

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
    if not search_result or not isinstance(payload, dict):
        return
    changed = False
    report_html = get_report_html(payload)
    report_data = payload.get("data")
    if search_result.status != "ready":
        search_result.status = "ready"
        changed = True
    if report_data and not search_result.report_data:
        search_result.report_data = report_data
        changed = True
    if report_html and not search_result.report_html:
        search_result.report_html = report_html
        changed = True
    if changed:
        db.session.commit()


def report_success_content(result, search_result=None):
    payload = result.get()
    sync_report_payload(search_result, payload)
    safe_payload = get_report_html(payload)
    review = report_review_components(payload)
    modal = html.Div(
        [
            dmc.Modal(
                title="Envio de email",
                id={'type': 'modal-send-email','index': result.id},
                centered=True,
                zIndex=10000,
                children=[],
            )
        ]
    )
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
        report_email_controls(result.id, search_result.title if search_result else None),
    ]


def modal_feedback(icon, color, title, message):
    return [
        dmc.Stack(
            [
                dmc.Center(DashIconify(icon=icon, color=color, width=72)),
                dmc.Title(title, order=3, align="center"),
                dmc.Text(message, align="center", color="dimmed"),
            ],
            spacing="sm",
        )
    ]


def record_email_audit(task_id, recipient, status, error_message=None):
    search_result = SearchResult.query.filter_by(
        result_id=task_id,
        user_id=current_user.id,
        tenant_id=get_current_tenant_id(),
    ).first()
    audit = EmailAudit(
        tenant_id=get_current_tenant_id(),
        user_id=current_user.id,
        search_result_id=search_result.id if search_result else None,
        celery_task_id=task_id,
        recipient=recipient or "",
        status=status,
        error_message=(error_message or "")[:512] or None,
    )
    db.session.add(audit)
    db.session.commit()

@callback(
    [Output("center-body", "children")],
    [Input("interval", "n_intervals")], prevent_initical_call = False
)
def update_status(_):
    patched_children = Patch()

    results_id = SearchResult.query.filter_by(user_id=current_user.id, tenant_id=get_current_tenant_id()).order_by(SearchResult.created_at.desc()).all(),
    change =[]
    if len(results_id[0])> 0:
        for index, result_id in enumerate(results_id[0]):
            result = AsyncResult(result_id.result_id)
            if not task_status_singleton.compare_status(result_id.result_id,result.status):
                if result.status == "SUCCESS":
                    icon = "icon-park-twotone:check-one"
                    color = "green"
                    content = report_success_content(result, result_id)
                elif result.status in {"PENDING", "STARTED", "RETRY"}:
                    icon = "line-md:downloading-loop"
                    color = "blue"
                    content = report_processing_content(result.status)
                elif result.failed():
                    task_status_singleton.set_status(result_id.result_id, "FAILURE")
                    if result_id.status != "failed":
                        result_id.status = "failed"
                        db.session.commit()
                    icon = "ic:twotone-error"
                    color = "red"
                    content = report_failure_content(result)
                else:
                    icon = "line-md:downloading-loop"
                    color = "blue"
                    content = report_processing_content(result.status)
                    
                item = dmc.AccordionItem(
                        [
                            create_accordion_label(
                                f"{result_id.title}", icon, color, f'{(result_id.created_at - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")}'
                            ),
                            create_accordion_content(content),
                        ],
                        value=f"{result_id.result_id}",)
                del patched_children[index]
                patched_children.insert(index=index, item=item)
                change.append(True)
                task_status_singleton.set_status(result_id.result_id, result.status)

        if True in change:
            change = []
            return patched_children
        else:
            return no_update
    else:
        return no_update


@callback(
    [ Output({'type': 'modal-send-email', 'index': MATCH}, 'opened'),
    Output({'type': 'modal-send-email', 'index': MATCH}, 'children'),
    Output({'type': 'button_send', 'index': MATCH}, 'children')],
    Input({'type': 'button_send', 'index': MATCH}, 'n_clicks'),
    [
        State({'type': 'input_email', 'index': MATCH}, 'value'),
        State({'type': 'input_email_subject', 'index': MATCH}, 'value'),
        State({'type': 'input_email_message', 'index': MATCH}, 'value'),
    ],
    prevent_initial_call=True,
)
def display_output(n_clicks, value, subject, message):
    if not n_clicks:
        raise PreventUpdate

    task_id = ctx.triggered_id.get("index", None)
    recipient = (value or "").strip()

    if not is_valid_email(recipient):
        record_email_audit(task_id, recipient, "invalid", "Email de destino inválido.")
        return True, modal_feedback("ep:failed", "red", "Email inválido", "Informe um email de destino completo."), "Enviar Email"

    try:
        payload = AsyncResult(task_id).get()
        report_html = get_report_html(payload)
        SendEmail(
            smtp_login=current_user.email,
            smtp_password=current_user.stmp_password,
        ).send_email_to(response=report_html, email=recipient, subject=subject, intro_message=message)
    except EmailSendError as exc:
        record_email_audit(task_id, recipient, "error", str(exc))
        return True, modal_feedback("ep:failed", "red", "Envio não realizado", str(exc)), "Tentar novamente"
    except Exception as exc:
        message = "Não foi possível preparar o relatório para envio. Tente novamente em alguns instantes."
        record_email_audit(task_id, recipient, "error", str(exc))
        return True, modal_feedback("ep:failed", "red", "Envio não realizado", message), "Tentar novamente"

    search_result = SearchResult.query.filter_by(
        result_id=task_id,
        user_id=current_user.id,
        tenant_id=get_current_tenant_id(),
    ).first()
    if search_result:
        search_result.status = "sent"
        search_result.reviewed_at = search_result.reviewed_at or datetime.utcnow()
        search_result.sent_at = datetime.utcnow()
        db.session.commit()

    record_email_audit(task_id, recipient, "success")
    return True, modal_feedback(
        "line-md:circle-twotone-to-confirm-circle-twotone-transition",
        "green",
        "Email enviado",
        f"Relatório enviado para {recipient}.",
    ), "Reenviar Email"
