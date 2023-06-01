

from dash_extensions.enrich import Output, Input, State, callback,  no_update
from datetime import timedelta
from dash import ctx, html, dcc, MATCH, Patch,ALL
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from src.models import SearchResult
from flask_login import current_user
import time
from dash_iconify import DashIconify
from celery.result import AsyncResult
from dash.exceptions import PreventUpdate
import bs4 as bs
from src.utils.send_email import SendEmail
from src.utils.tasks_result_utils import task_status_singleton

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

@callback(
    [Output("center-body", "children")],
    [Input("interval", "n_intervals")], prevent_initical_call = False
)
def update_status(_):
    patched_children = Patch()

    results_id = SearchResult.query.filter_by(user_id=current_user.id).order_by(SearchResult.created_at.desc()).all(),
    change =[]
    if len(results_id[0])> 0:
        for index, result_id in enumerate(results_id[0]):
            result = AsyncResult(result_id.result_id)
            if not task_status_singleton.compare_status(result_id.result_id,result.status):
                if not result.failed():                
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
                    icon = "icon-park-twotone:check-one"
                    color = "green"
                    content =  [
                        modal,
                        dmc.Group([dmc.TextInput(id={'type': 'input_email','index': result_id.result_id},placeholder="Email", style={"width": 200}),
                        dmc.LoadingOverlay(dmc.Button("Enviar Email",id={'type': 'button_send','index': result_id.result_id}, n_clicks=0), loaderProps={"variant": "oval", "color": "blue", "size": "sm"}, )], className="mb-2"),
                        html.Iframe(srcDoc=result.get(),  style={'width': '100%', 'height': '500px'})]
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
    State({'type': 'input_email', 'index': MATCH}, 'value'),
    prevent_initial_call=True,
)
def display_output(n_clicks, value):
    if value:
        print()
        if not current_user.email or not current_user.stmp_password:
            return True,[dmc.Center([DashIconify(id ='icon-modal',icon="ep:failed",color='red', width=100),
                                    dmc.Title(f"Email ou Senha SMTP não cadastradas", order=3)])] ,no_update
        if "@" in value:
            SendEmail(smtp_login=current_user.email, smtp_password= current_user.stmp_password,).send_email_to(response=AsyncResult(ctx.triggered_id.get("index", None)).get(), email=value)
            return True,[dmc.Center([DashIconify(id ='icon-modal',icon="line-md:circle-twotone-to-confirm-circle-twotone-transition",color='green', width=100)])],no_update
    return True,[dmc.Center([DashIconify(id ='icon-modal',icon="ep:failed",color='red', width=60),
                                    dmc.Title(f"Inválido, Email incompleto!", order=3)])] ,no_update