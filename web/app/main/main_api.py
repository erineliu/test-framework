from flask import Flask,render_template,request,redirect,Blueprint,url_for,jsonify,current_app
from flask_socketio import SocketIO, emit, join_room, leave_room,rooms
from app.exts import db,socketio
from . import app2_bp
import redis
import shlex
from backend.src.controller import Controller
import threading
import json
import logging


test_controller = Controller()
client_room_dict={}


#LOG = logging.getLogger(__name__)


class Listener(threading.Thread):

    def __init__(self, r, channel):
        threading.Thread.__init__(self)
        self.redis = r
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channel)


    def run(self):
        for m in self.pubsub.listen():
            if 'message' != m['type']:
                continue
            
            try:
                data=json.loads(m['data'])
                cmd = shlex.split(data['cmd'])
           
                if cmd[0] == "showMessageDlg":
                    socketio.emit('mesg_box', {'text':cmd[1],'image':cmd[2]}, namespace='/cmd', room=data["room"] )

                if cmd[0] == "closeMessageDlg":
                    socketio.emit('mesg_box_close', {}, namespace='/cmd', room=data["room"] )
                 
                #print('[{}]: {}'.format(m['channel'], m['data']))
            except Exception as e:
                print("eeeeeeeeeeeeeeee",str(e))


#pool = redis.ConnectionPool(host='127.0.0.1',port=6379, db=0,decode_responses=True)
pool = redis.ConnectionPool(host='10.35.49.15',port=6379, db=0,decode_responses=True)
rcon = redis.StrictRedis(connection_pool=pool)
client = Listener(rcon,"message_box_server")
client.start()






@app2_bp.route('/add_numbers',methods=['GET'])
def add_numbers():    
    data = test_controller.getProjList()
    current_app.logger.info("%s => %s"%("/add_numbers",str(data)))
   
   
    return jsonify(results=data)
    





@app2_bp.route('/run_test',methods=['POST'])
def run_test():

    try:
        data = request.get_json()
        #t = threading.Thread(target = test_controller.runTest,args = (data,))
        #t.start()
        test_controller.runTest(data)
        print(test_controller.TP_member_dict)

       
        current_app.logger.info("%s => %s"%("/run_test",str(data)))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
 
 
    except Exception as e:
        current_app.logger.error("%s => %s"%("/run_test",str(e)))
        return json.dumps({'error':str(e)}), 400, {'ContentType':'application/json'}

       
   





@app2_bp.route('/stop_test',methods=['POST'])
def stop_test():

    try:
        data = request.get_json()
        test_controller.stopTest(data)

        current_app.logger.info("%s => %s"%("/stop_test",str(data)))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    except Exception as e:
        return json.dumps({'error':str(e)}), 400, {'ContentType':'application/json'} 






@app2_bp.route('/save_lock', methods=['POST'])
def save_lock():

    data = request.get_json()
   
    sql_cmd = """
              INSERT INTO Locker (room,name) VALUES ('%s', '%s')
              ON DUPLICATE KEY UPDATE name='%s';
              """%(data["roomID"],data["name"],data["name"])
   
    query_data = db.engine.execute(sql_cmd)

    return "ok"








@app2_bp.route('/release_lock', methods=['POST'])
def release_lock():

    data = request.get_json()
   
    sql_cmd = """
              INSERT INTO Locker (room,name) VALUES ('%s', '%s')
              ON DUPLICATE KEY UPDATE name='%s';
              """%(data["roomID"],"","")
   
    query_data = db.engine.execute(sql_cmd)

    return "ok"







@app2_bp.route('/add_mesg/<room>',methods=['POST'])
def send(room):
    
    if request.headers['Content-Type'] == 'application/json':
      
        #data = json.loads(request.get_json())['mesg']
        data = request.get_json()['mesg']
        #print("ttttttttttttttttttttt",type(data),data)
       
        socketio.emit('mesg_output', {'output':data}, namespace='/cmd', room=room )
        current_app.logger.info("%s => %s"%("/send/"+room,str(data)))
       
        #q.put([room,request.get_json()['mesg']])
        #print(list(q.queue))
       
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 





@app2_bp.route('/sendState/<room>',methods=['POST'])
def sendState(room):
    if request.headers['Content-Type'] == 'application/json':
        socketio.emit('state_update', request.get_json()['mesg'], namespace='/cmd', room=room )

        current_app.logger.info("%s => %s"%("/sendState/"+room,str(request.get_json()['mesg'])))
 
        return "i got it\n"




@app2_bp.route('/stageInitial/<room>',methods=['POST'])
def stageInitial(room):
    if request.headers['Content-Type'] == 'application/json':
        socketio.emit('stage_Initial', request.get_json()['mesg'], namespace='/cmd', room=room )

        current_app.logger.info("%s => %s"%("/stage_Initial/"+room,str(request.get_json()['mesg'])))
 
        return "i got it\n"




@app2_bp.route('/testEnd/<room>',methods=['POST'])
def testEnd(room):
    if request.headers['Content-Type'] == 'application/json':
        socketio.emit('test_end', request.get_json()['mesg'], namespace='/cmd', room=room )

        current_app.logger.info("%s => %s"%("/stage_Initial/"+room,str(request.get_json()['mesg'])))
 
        return "i got it\n"





@socketio.on('connect_event', namespace='/cmd')
def connected_msg(msg):  

    #print(msg)   
    join_room(msg["roomID"])

    #print("[clinet] %s join room: %s"%(msg["clientID"],msg["roomID"]))

    if msg["roomID"] in client_room_dict:
         client_room_dict[msg["roomID"]].append(msg["clientID"])
    else:
        client_room_dict.update({msg["roomID"]:[msg["clientID"]]})


    current_app.logger.info("%s => %s"%("connect_event",str(client_room_dict)))
   
    print(client_room_dict)



@socketio.on('disconnect_event', namespace='/cmd')
def disconnect(msg):
    client_room_dict[msg["roomID"]].remove(msg["clientID"])

    current_app.logger.info("%s => %s"%("disconnect_event",str(client_room_dict)))
    #print('disconnect')





@socketio.on('mesg_box_return', namespace='/cmd')
def connected_msg(msg):
    #rcon.publish("message_box_client",'{"room":"%s","cmd":"result","data":"%s"}'%(request.sid,msg["data"]))
    try:
        print("jjjjjjjjjjjjjjjjj",rooms())
        rcon.publish("message_box_client",'{"room":"%s","cmd":"result","data":"%s"}'%(msg["roomID"],msg["data"]))
    except Exception as e:
        print(e)



@socketio.on('manualChange', namespace='/cmd')
def manualChange(msg):
    print(msg)
    current_app.logger.info("%s => %s"%("manualChange",str(msg)))
    socketio.emit('manual_update',msg,namespace='/cmd',room=msg["roomID"], include_self=False )










          
 

