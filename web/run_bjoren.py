from manage import app,socketio
import os,sys



## set path enivroment ##
appPath = os.path.dirname(os.path.realpath(__file__))
os.environ['LaunchPath'] = appPath +"/backend"


if __name__ == "__main__":
    import bjoern
    bjoern.run(app, "0.0.0.0", 60001)
