#!/usr/bin/env python
import requests
import json
import socketio

# standard Python
#sio = socketio.Client()
#sio = socketio.AsyncClient()
#sio.connect('http://localhost:5000')

def sendWeb(mesg,room,sendType="add_mesg",request_number=0):
    
    headers = {'Content-type': 'application/json',}
    data =json.dumps({"mesg":mesg})
    #response = requests.post('http://127.0.0.1:60001/%s/%s'%(sendType,room), headers=headers, data=data)
    
    if request_number == 2 or request_number == 0:
        #requests.post('http://127.0.0.1:60002/%s/%s'%(sendType,"test123"), headers=headers, data=data)
        requests.post('http://10.34.53.212:60002/%s/%s'%(sendType,"test123"), headers=headers, data=data)
    if request_number == 1 or request_number == 0:
        #response = requests.post('http://127.0.0.1:60001/%s/%s'%(sendType,room), headers=headers, data=data)
        response = requests.post('http://10.34.53.212:60001/%s/%s'%(sendType,room), headers=headers, data=data)


    print(response)
    return response





if __name__ == "__main__":
   headers = {'Content-type': 'application/json',}
   #response = requests.post('http://127.0.0.1:60001/%s/%s'%("send","123"), headers=headers, data='{"username":"xyz","password":"xyz"}')
   response = requests.post('http://127.0.0.1:5000/%s/%s'%("sendState","Test123"), headers=headers, data='{"username":"xyz","password":"xyz"}')
