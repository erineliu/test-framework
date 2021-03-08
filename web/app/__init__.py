from flask import Flask,render_template

#from flask_migrate import Migrate
from config import config
from app.exts import db,socketio,login_manager,security,mail,celery
import logging
import os
from datetime import datetime
from app.extadmin.extadmin import admin
import ssl 
ssl._create_default_https_context = ssl._create_unverified_context
#from gevent import monkey
#monkey.patch_all()

cur_path = os.path.dirname(os.path.abspath(__file__))


def create_app(config_name):
    app = Flask(__name__)
    

    from .login.login import user_datastore
    security.init_app(app, user_datastore)

    mail.init_app(app)
    
    app.config.from_object(config[config_name]) 
    init_celery(app)
    

    setup_logging(app,get_log_path())

    admin.init_app(app)
    config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    #socketio.init_app(app,async_mode="threading",logger=True, engineio_logger=True, message_queue = "redis://10.35.49.15:6379") 
    #socketio.init_app(app,logger=True,async_mode="gevent_uwsgi",cors_allowed_origins='*')
    socketio.init_app(app,async_mode="threading",logger=True ,cors_allowed_origins='*')
    #migrate.init_app(app,db)

    from .login.login import login_bp
    from .main import app2_bp
    app.register_blueprint(login_bp)
    app.register_blueprint(app2_bp)
    
    return app


def init_celery(app):
    
    celery.conf.BROKER_URL = app.config['CELERY_BROKER_URL']
    celery.conf.RESULT_BACKEND = app.config['CELERY_RESULT_BACKEND']
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    



def get_log_path():

    dateTime = datetime.now().strftime("%Y%m%d_%H%M%S")
    logName = "%s_%s"%(dateTime,'app.log')
    logPath = os.path.join(cur_path,'app_journey',logName)    
  
    return logPath



def setup_logging(app,filePath):

    if not os.path.exists(os.path.dirname(filePath)):
        os.makedirs(os.path.dirname(filePath))  

    handler = logging.FileHandler(filePath)
    formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(filename)s] - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
   
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)





