from flask import Flask,render_template,request,redirect,Blueprint,url_for
from app.model import User
from app.exts import login_manager
from . import app2_bp




@app2_bp.route('/')
def index():
    if not request.script_root:
        # this assumes that the 'index' view function handles the path '/'
        request.script_root = url_for('app2.index', _external=True)    
    
    return render_template('index.html')
    


@app2_bp.route('/framework/<room>')
def runFramework(room):
    return render_template('framework.html')



@app2_bp.route('/board')
def board():
    return render_template('board.html')

    

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)

    return None



