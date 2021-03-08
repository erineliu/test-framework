from backend.src.factory import Factory
from backend.src.testProcess import TestProcess
from backend.src.readProj import getProjList
from multiprocessing import Process, Value, Lock, Queue
import os
import signal


class Controller:

    def __init__(self):
        self.TP_member_dict={}


    def runTest(self,dut_Info):
        dialog_Info = {"script":os.path.join(os.environ['LaunchPath'],dut_Info["script"]), \
                       "roomID":dut_Info["roomID"],"cellid":1,"ip":"10.34.53.48","sn":dut_Info["SN"],"debug":0,"project":dut_Info["project"]}

        print(dialog_Info)
        configFile = os.path.join(os.environ['LaunchPath'],os.path.dirname(dut_Info["script"]), "config.ini")
       
        tp = TestProcess(dialog_Info,Factory(configFile),Queue())
        p1 = Process(target=tp.run)
        self.TP_member_dict.update({dut_Info["roomID"]:p1})
              
        p1.start()
       
 

    def stopTest(self,dut_Info):
       
        if not dut_Info["roomID"] in self.TP_member_dict:
            return

        print("kill process %s"%(self.TP_member_dict[dut_Info["roomID"]].pid))
        os.kill(self.TP_member_dict[dut_Info["roomID"]].pid, signal.SIGKILL)
        del self.TP_member_dict[dut_Info["roomID"]]




    def getProjList(self):
        return getProjList(os.path.join(os.environ['LaunchPath'],"project_table.csv"))




     


