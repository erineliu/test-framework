from flask import Flask, redirect, url_for, request, flash, render_template,Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user,UserMixin,current_user
from datetime import timedelta

from app.model import *
from app.exts import socketio,db,mail,celery

from flask_security import SQLAlchemyUserDatastore

from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message
import time

## use blueprint ##
login_bp = Blueprint('login',__name__ ,url_prefix='/view' )


s = URLSafeTimedSerializer('Thisisaseret')
user_datastore = SQLAlchemyUserDatastore(db,User,Role)



@login_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        print(request.url)
        print(request.form)
        user_id = request.form.get('username')
        user_db = User.query.filter_by(username=user_id).first()
        
        #print(user_db.username,user_db.password)
        #print(user_db.roles[0].name)

        if user_db and user_db.password == request.form['password']:         
 
            next = request.args.get('next')
            ## login remember me ##
            login_user(user_db,remember=True)

            return redirect(next or url_for('app2.index'))
           

        flash('Wrong username or password!')


    # GET 請求
    #return render_template('login.html')
    return redirect(url_for('app2.index'))



@celery.task
def add(x, y):
    return x + y



@celery.task(bind=True)
def send_async_email(self,mesg_dict):
    """Background task to send an email with Flask-Mail."""    
    msg = Message(mesg_dict['title'],sender=mesg_dict['sender'],recipients=mesg_dict['recipients']) 
    msg.body = mesg_dict['body']
 
    try:
        mail.send(msg)
    except:
        return 1

    return 0

    #return "hello ha ha"
  




@login_bp.route('/status/<task_id>') 
def cheek_task_result(task_id):
    task = send_async_email.AsyncResult(task_id)
    print(task.result)
    return task.result





@login_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        ## create role to data base ##
        role_admin = user_datastore.find_or_create_role(name='admin')
        role_user = user_datastore.find_or_create_role(name='user')

        cur_user = user_datastore.create_user(username=request.form.get('username'), password=request.form.get("password"),email=request.form.get("email"))
        user_datastore.add_role_to_user(cur_user,role_user)
        db.session.commit()

        email = request.form.get("email")
        token = s.dumps(email, salt = 'email-confirm')
        link = url_for('login.confirm_email',token = token, _external = True )

        msg_title = 'Hello It is Flask-Mail'
        msg_recipients = [email]
        msg_sender = 'wistronspdsw@gmail.com'        
        msg_body = 'Your link is {}'.format(link)
 
        mesg_dict = {"title": msg_title,"recipients":msg_recipients,"sender":msg_sender,"body":msg_body }

        

        ## If you’d like to store additional metadata about the task in the result backend ## 
        ## set the result_extended setting to True.                                        ##
        
        task = send_async_email.apply_async( args=[mesg_dict], countdown=30, result_extended=True )
        
        print("skdfsofjmdodmdodfdkfdofkdfpkspoko")
        print(task.id)
         
        add.delay(3,8)

        '''
        msg = Message(msg_title,sender=msg_sender,recipients=msg_recipients) 
        link = url_for('login.confirm_email',token = token, _external = True )
        msg.body = 'Your link is {}'.format(link)
        #mail.send(msg)
        send_async_email.delay(msg)
        '''

        flash('Please check your mail to enable account','info')

        next = request.args.get('next')
        return redirect(next or url_for('app2.index'))

    return redirect(url_for('app2.index'))





@login_bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:

       ##  expired time in second => max_age ## 
       email = s.loads(token, salt = 'email-confirm', max_age=60)
    except SignatureExpired:
       return '<h1> The token is expired!</h1>'
 
    return "<h1>The token works</h1>"






@login_bp.route('/logout')
@login_required
def logout():
   
    #Locker_db = Locker.query.filter_by(name=current_user.username)
    Locker_db = Locker.query.filter_by(name=current_user.username).all()
   
    if Locker_db != None:
        for eachLocker in Locker_db:
            msg={"action":"unLock"}
            socketio.emit('manual_update',msg,namespace='/cmd',room=eachLocker.room )
  
    logout_user()
    return 'Logged out successfully!'



if __name__ == "__main__":
    app.run(debug=True)
