from flask_admin import Admin
from flask_admin.base import AdminIndexView
from flask_admin.contrib import sqla
from flask_login import login_required
from werkzeug.security import generate_password_hash
from src.ext.database import db
from src.models import  User
from flask_login import current_user

# Proteger o admin com login via Monkey Patch
AdminIndexView._handle_view = login_required(AdminIndexView._handle_view)
sqla.ModelView._handle_view = login_required(sqla.ModelView._handle_view)
admin = Admin()


class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

class UserAdmin(sqla.ModelView):
    column_list = ['username']
    can_edit = False

    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)


def init_app(app):
    admin.name = "APEX"
    admin.template_mode = "bootstrap3"
    admin.init_app(app)
    admin.add_view(UserAdmin(User, db.session))