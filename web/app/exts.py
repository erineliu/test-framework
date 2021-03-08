from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_security import Security
from flask_mail import Mail
from celery import Celery, platforms
platforms.C_FORCE_ROOT = True   

socketio = SocketIO()
db = SQLAlchemy()
login_manager = LoginManager()
security = Security()
mail = Mail()
celery = Celery()



