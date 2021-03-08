from backend.src.SSHCmd2 import ssh_cmd2
from backend.src.SubCmd import subRunCmd
from backend.src.redisCmd import redis_cmd


class cmdService():
    def __init__(self):
        self.cmdTypeList = {"SUB":subRunCmd() ,"SSH":ssh_cmd2(),"MSG":redis_cmd()}



    def getCmdHander(self,cmdType):
        return self.cmdTypeList[cmdType]



    def setSSHVar(self,host,user,pwd):
        self.cmdTypeList["SSH"].host = host
        self.cmdTypeList["SSH"].username = user
        self.cmdTypeList["SSH"].password = pwd


    def setMSGVar(self,host,room):
        self.cmdTypeList["MSG"].host = host
        self.cmdTypeList["MSG"].room = room
       




