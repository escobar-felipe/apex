from dash_extensions.enrich import Output, Input, State, callback,  no_update
from dash import ctx
import dash_mantine_components as dmc
from src.models import User
from src.ext.database import db
from flask_login import current_user
import time

output = [
    Output('form-user', 'children'),
    Output('modal-update-user', 'title'),
    Output('modal-update-user', 'opened'),
    Output('modal-update-user', 'children')
]

@callback(output,
          [Input('btn-update-user', 'n_clicks')],
          [State('open-api-key', 'value'),State('email_user', 'value'),State('stmp_password', 'value'),State('serp-api-key', 'value')], prevent_initial_call=True)
def profile_callback(n_clicks, open_key,email , stmp_password, serpapi_key):
    time.sleep(1)
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'btn-update-user':
        db.session.query(User).filter(User.username==current_user.username).update({'api_key':open_key, 'email':email, 'stmp_password':stmp_password, 'serpapi_key':serpapi_key})
        db.session.commit()
        return no_update, "Sucesso!", True,  dmc.Text("Seus dados foram atualizados!")
    else:
        return no_update, no_update,no_update,no_update