import os
from datetime import timedelta

#basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:  # 基本配置类
    SECRET_KEY = 'Sqsdsffqrhgh.,/1#$%^&' 
    ITEMS_PER_PAGE = 10

    @staticmethod
    def init_app(app):  # 靜態方法作為配置的統一接口，暫時為空
        pass



class DevelopmentConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ernie:zxcZXC123!@#@10.35.49.15/mydatabase"
    #SQLALCHEMY_DATABASE_URI = "mysql+pymysql://ernie:zxcZXC123!@#@localhost/mydatabase"
    SECURITY_PASSWORD_SALT = 'RTYSSJDKFLCCKOEEM'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=1)



    ## mail setting ##
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_USERNAME = "wistronspdsw"
    MAIL_PASSWORD = "ji394jo3t;4"
    MAIL_PORT = "587"
    MAIL_USE_SSL = True
    MAIL_USE_TLS =  False



    ## celery setting ##
    #CELERY_BROKER_URL = 'redis://localhost:6379'
    #CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CELERY_BROKER_URL = 'redis://10.35.49.15:6379/1'
    #CELERY_RESULT_BACKEND = 'db+mysql+pymysql://ernie:zxcZXC123!@#@localhost/mydatabase'
    CELERY_RESULT_BACKEND = 'db+mysql+pymysql://ernie:zxcZXC123!@#@10.35.49.15/mydatabase'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_RESULT_SERIALIZER = 'json'

    #CELERY_ACCEPT_CONTENT =['pickle']
    #CELERY_TASK_SERIALIZER = 'pickle'
    
    CELERY_TIMEZONE = 'Asia/Taipei'




class TestingConfig(BaseConfig):
    pass
    #TESTING = True
    #SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    #WTF_CSRF_ENABLED = False



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
