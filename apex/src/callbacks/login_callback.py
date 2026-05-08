from dash_extensions.enrich import Output, Input, State, dcc, callback, no_update
from dash import ctx
from werkzeug.security import check_password_hash
from src.models import User
from flask import session
from flask_login import login_user
from src.utils.tenancy import get_current_tenant_id


@callback([
          Output('redirect-login', 'children'),
          Output("loading-form", "children"),
          Output("modal-centered", "opened"),
          Output("modal-centered", "title"),
          Output("modal-centered", "children"),
          ],
          [Input('login-button', 'n_clicks')],
          [State('username-input', 'value'), State('password-input', 'value')], prevent_initial_call=True)
def login(n_clicks, username, password):
    if not username or not password:
        return no_update, no_update, True, "Dados obrigatórios", "Informe usuário e senha para entrar."
    session.clear()
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'login-button':
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            return no_update, no_update, True, "Tenant não encontrado", "Acesse pelo domínio correto ou fale com o administrador."

        user = User.query.filter_by(username=username, tenant_id=tenant_id).first()
        if not user or not check_password_hash(user.password, password):
            return no_update, no_update, True, "Login não realizado", "Usuário ou senha inválidos."

        login_user(user)
        return dcc.Location(pathname="/", id="someid_doesnt_matter"), no_update, False, no_update, no_update
    else:
        return no_update, no_update, True, "Login não realizado", "Tente novamente."
