import os
from app import create_app,db,celery
from app.model import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.exts import socketio


## set path enivroment ##
appPath = os.path.dirname(os.path.realpath(__file__))
os.environ['LaunchPath'] = appPath +"/backend"


app = create_app('development')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()

