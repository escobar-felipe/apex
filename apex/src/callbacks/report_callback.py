from dash import ctx
from src.pages.home.tasks import report_media_task
import time
from dash_extensions.enrich import Output, Input, State, callback,dcc
from flask_login import current_user
from src.models import SearchResult
from src.ext.database import db

output = [
    Output('chatgpt_tabs', 'children'),
]

@callback(output,
          [Input('button-report', 'n_clicks')],
          [State('search_value', 'data'),State('search_links', 'data')], prevent_initial_call=True)
def report_gpt_callback(n_clicks, search_value,search_links):
    time.sleep(1)
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'button-report':
        result = report_media_task.delay(articles = search_links,api_key= current_user.api_key)
        task_id = result.id

        if SearchResult.query.filter_by(result_id=task_id).first():
            raise RuntimeError(f'{task_id} ja esta cadastrada')
        search_result = SearchResult(title=search_value, user_id = current_user.id,result_id=task_id)
        db.session.add(search_result)
        db.session.commit()
    return dcc.Location(pathname="/my_reports", id="redirec_my_reports")

