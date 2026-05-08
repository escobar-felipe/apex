from dash_extensions.enrich import Output, Input, State, callback,  no_update
from dash import ctx
import dash_mantine_components as dmc
from src.models import User
from src.ext.database import db
from flask_login import current_user
from src.utils.tenancy import get_current_tenant_id
from src.utils.send_email import is_valid_email
import time

output = [
    Output('form-user', 'children'),
    Output('modal-update-user', 'title'),
    Output('modal-update-user', 'opened'),
    Output('modal-update-user', 'children')
]

@callback(output,
          [Input('btn-update-user', 'n_clicks')],
          [State('open-api-key', 'value'),State('email_user', 'value'),State('stmp_password', 'value'),State('serp-api-key', 'value'), State('confirm-update-user', 'value')], prevent_initial_call=True)
def profile_callback(n_clicks, open_key,email , stmp_password, serpapi_key, confirmation):
    time.sleep(1)
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'btn-update-user':
        if "confirmed" not in (confirmation or []):
            return no_update, "Confirme a atualização", True, dmc.Text("Marque a confirmação antes de salvar ou sobrescrever suas credenciais.")
        if email and not is_valid_email(email):
            return no_update, "Email inválido", True, dmc.Text("Informe um email completo, como nome@dominio.com.")
        user = User.query.filter(User.username==current_user.username, User.tenant_id==get_current_tenant_id()).first()
        if not user:
            return no_update, "Erro", True, dmc.Text("Usuário não encontrado.")

        user.email = email
        if open_key:
            user.api_key = open_key
        if stmp_password:
            user.stmp_password = stmp_password
        if serpapi_key:
            user.serpapi_key = serpapi_key
        db.session.commit()
        return no_update, "Dados atualizados", True,  dmc.Text("Suas credenciais foram salvas com segurança.")
    else:
        return no_update, no_update,no_update,no_update
