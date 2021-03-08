from manage import app
import os,sys



## set path enivroment ##
appPath = os.path.dirname(os.path.realpath(__file__))
os.environ['LaunchPath'] = appPath +"/backend"
