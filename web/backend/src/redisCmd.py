import redis
import time
from threading import Timer
import json

'''
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
sub = r.pubsub()
sub.psubscribe('message_box_*')
r.publish("message_box_client",'kill')
'''


'''
while True:
    message = sub.get_message()
    if message:
        print(message)
    time.sleep(0.001)
'''


class RunCMDTimeoutError(Exception):

    '''Exception class raised by this module.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class redis_cmd():

    def __init__(self,host="",user="",pwd="",room=""):
        #self.cmdOut = ""
        self.host = host
        self.user = user
        self.pwd = pwd
        self.room = room
        self._returncode = -1
        self.timeOutFlag = False


    def connect(self):
        try:
            self.r = redis.Redis(host=self.host, port=6379, db=0, decode_responses=True)
            self.sub = self.r.pubsub()
            #self.sub.subscribe('message_box')
            self.sub.psubscribe('message_box_*')
        except Exception as e:
            raise type(e)("%s\nmsg: %s"%(str(e),"redis connet fail"))


    def execCmd(self,cmd,timeout=30):

        self.timeout_timer = Timer(timeout, self.killWhenTimeout)

        try:
            self.connect()
           
            self.timeout_timer.start()
            #print("message_box_server",'{"room":"%s","cmd":"%s"}'%(self.room,cmd))
            self.r.publish("message_box_server",'{"room":"%s","cmd":"%s"}'%(self.room,cmd))
            

            for line in self.sub.listen():
                #print(line)
                #yield str(line)
                 
                if line["channel"] == "message_box_client" and line["type"] == "pmessage":
                    data = json.loads(line["data"])
                    print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
                    print(data)
                    if data["room"] != self.room:continue
                    
                    if data["cmd"] == "result":
                        if data["data"] == "True":
                            self._returncode = 0
                        break

                    if data["cmd"] == "kill":
                        break

            if self.timeOutFlag:
                raise RunCMDTimeoutError("test case time out")

        except RunCMDTimeoutError as e:
            yield str(e)
            #yield "test case time out !!"

        except Exception as e:
            raise e

        finally:
            self.timeout_timer.cancel()
            self.close()



    def killWhenTimeout(self):
        self.r.publish("message_box_server",'{"room":"%s","cmd":"%s"}'%(self.room,"closeMessageDlg"))
        self.r.publish("message_box_client",'{"room":"%s","cmd":"%s"}'%(self.room,"kill"))
        self._returncode = 1
        self.timeOutFlag = True


    @property
    def getCmdReCode(self):
        return self._returncode


    def close(self):
        self.sub.close()
        pass


if __name__ == "__main__":

    r1 = redis_cmd('localhost',"","","12")
    r1.connect()
   
    #r1.r.publish("message_box_client",'{"room":"%s","cmd":"%s"}'%("dddwer","kill"))
    #for i in r1.execCmd("this is  a book"):
    #    print(i)
    r1.execCmd("showMessageDlg 'Please check led is light' static/image/flower.jpg")
















#for message in sub.listen():
#    print('Got message', message)
#sub.close()

    #if (
    #    isinstance(message.get('data'), bytes) and
    #    message['data'].decode() == 'GREETING'
    #):
    #    print('Hello')
