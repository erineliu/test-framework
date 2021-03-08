from app.model import *

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


admin = Admin()
admin.add_view(ModelView(User, db.session, name="user member"))
admin.add_view(ModelView(Locker, db.session, name="lucker"))
admin.add_view(ModelView(Role, db.session, name="Role"))

