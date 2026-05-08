from dash import ctx, no_update
from src.pages.home.tasks import report_media_task
import time
from dash_extensions.enrich import Output, Input, State, callback,dcc
from flask_login import current_user
from src.models import SearchResult
from src.ext.database import db
from src.utils.tenancy import get_current_tenant_id

output = [
    Output('chatgpt_tabs', 'children'),
    Output('alert-multi-select', 'hide')
]

@callback(output,
          [Input('button-report', 'n_clicks')],
          [
              State('search_value', 'data'),
              State('multiselect-text', 'value'),
              State('report-type', 'value'),
              State('report-tone', 'value'),
              State('report-audience', 'value'),
              State('report-objective', 'value'),
          ], prevent_initial_call=True)
def report_gpt_callback(n_clicks, search_value, data_select, report_type, report_tone, report_audience, report_objective):
    if not data_select:
        return no_update , False
    time.sleep(1)
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'button-report':
        report_options = {
            "title": search_value,
            "report_type": report_type or "monitoring",
            "tone": report_tone or "executive",
            "audience": report_audience or "diretoria e cliente",
            "objective": report_objective or "identificar achados, riscos, oportunidades e recomendações",
        }
        result = report_media_task.delay(articles=data_select, api_key=current_user.api_key, report_options=report_options)
        task_id = result.id

        if SearchResult.query.filter_by(result_id=task_id).first():
            raise RuntimeError(f'{task_id} ja esta cadastrada')
        search_result = SearchResult(
            title=search_value,
            user_id=current_user.id,
            tenant_id=get_current_tenant_id(),
            result_id=task_id,
            status="generating",
            report_type=report_options["report_type"],
            tone=report_options["tone"],
            audience=report_options["audience"],
            objective=report_options["objective"],
        )
        db.session.add(search_result)
        db.session.commit()
    return dcc.Location(pathname="/my_reports", id="redirec_my_reports"), no_update
