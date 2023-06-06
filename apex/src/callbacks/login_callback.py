from dash_extensions.enrich import Output, Input, State, dcc, callback, html, no_update
from dash import ctx
from werkzeug.security import check_password_hash
from src.models import User
from flask import session
from flask_login import login_user
import time


@callback([Output('redirect-login', 'children'), Output("loading-form", "children"), Output("modal-centered", "opened")],
          [Input('login-button', 'n_clicks')],
          [State('username-input', 'value'), State('password-input', 'value')], prevent_initial_call=True)
def login(n_clicks, username, password):
    time.sleep(1)
    if not username or not password:
        return no_update, no_update, True
    session.clear()
    button_id = ctx.triggered_id if not None else 'No clicks yet'
    if button_id == 'login-button':
        user = User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database
        if not user or not check_password_hash(user.password, password):
            return no_update, no_update, True

        login_user(user)
        return dcc.Location(pathname="/", id="someid_doesnt_matter"), no_update, False
    else:
        return no_update, no_update, True
