from dash import dcc, register_page
from flask_login import current_user, logout_user
from src.ext.database import db
from src.models import User

register_page(__name__, path='/logout')


def layout(**query_strings):
    if current_user.is_authenticated:
        logout_user()
    return dcc.Location(pathname="/apex/login", id="redirect-logout")