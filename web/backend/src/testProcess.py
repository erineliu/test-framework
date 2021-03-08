from backend.src.SSHCmd import ssh_cmd
from backend.src.SSHCmd2 import ssh_cmd2
from backend.src.readTestFlow import TestFlowReader
from backend.src.tool import buildPath
import os,sys
import math
from backend.src.mydb import mydb
import time
import datetime
import shutil

if sys.version[:1] == '2':
    import wx.lib.pubsub.setupkwargs
    from wx.lib.pubsub import pub
else:
    from pubsub import pub



import shlex
import re
import traceback
from backend.src import get_ip
from backend.src.CmdSer import cmdService
from backend.src.curlTest import sendWeb
import json
import traceback


class StageStatus(object):
    def __init__(self,name):
        self.name = name
        self.result= "PASS"
        self.errorCode = ""
        self.errorMsg = ""


    def setStartTime(self,time):
        self._startTime = time


    def setEndTime(self,time):
        self._endTime = time


    @property
    def elapsedTime(self):
        return self._endTime - self._startTime


    @property
    def startTime(self):
        return self._startTime


    @property
    def endTime(self):
        return self._endTime


    def timeFormat(self,time):
        return str(time)[:-3]



class CaseStatus(StageStatus):
      def __init__(self,name):
        StageStatus.__init__(self,name)
        self.result= ""




class DBTool(object):

    def __init__(self,TP):
        self.TP = TP


    def process_start(self):
        mydb.update(self.TP.cellid+3,"Testing","",1)



    def stage_start(self):
        
        mydb.update(self.TP.cellid+1 ,self.TP.cur_stage,"", 1)


    def stage_status(self):
        mydb.update(self.TP.cellid+1,"%s (%s/%s)"%(self.TP.cur_stage,self.TP.cur_case.seqNum,len(self.TP.unitInfo.testCaseList)), 'Testing', 1)


    def stage_result(self,result=None):
        if result == None:
            result = self.TP.stageStatus.result

        self.TP.WebUpdate.stage_result(result)
        mydb.update(self.TP.cellid+3,result,"",1)



    def case_start(self):
        self.TP.WebUpdate.case_start()
        mydb.update(self.TP.cellid+2,"%s. %s"%(self.TP.cur_case.seqNum,self.TP.cur_case.name),'Testing', 1)



    def case_result(self,result=None):
        if result == None:
            result = self.TP.caseStatus.result

        self.TP.WebUpdate.case_result()
        mydb.update(self.TP.cellid+2,"%s. %s"%(self.TP.cur_case.seqNum,self.TP.cur_case.name),result,mydb.result2flag(result))



    def unit_info(self):
        self.TP.WebUpdate.unit_info()
        mydb.unit_update(self.TP.unitid,self.TP.sn,self.TP.ip,self.TP.location)




class WebTool(object):

    def __init__(self,TP):
        self.TP = TP
        self.room = self.TP.roomID
   

    def unit_info(self):
        testMode_show={0:"DEBUG", 1:"SFCS"}
        mesg ={"update_dutInfo": \
        {"stage":self.TP.cur_stage,
         "IP":self.TP.ip, \
         "testMode":testMode_show[self.TP.debug], \
         "OPID":self.TP.FA.opid_iniConfig["opid"], \
         "state":"Testing", \
         "sn":self.TP.sn, \
         "project":self.TP.dialog_Info["project"]}}
        
        sendWeb(mesg,self.room,"sendState")



    def testItem_list(self):
        testCaseList_json = [json.dumps(testCase.__dict__) for testCase in self.TP.unitInfo.testCaseList]
        mesg ={"add_testCaseList":testCaseList_json}
        sendWeb(mesg,self.room,"sendState")



    def case_start(self):
        mesg ={"case_start":{"name":self.TP.cur_case.name,"SeqNum":self.TP.cur_case.seqNum}}
        sendWeb(mesg,self.room,"sendState")




    def case_result(self):
        mesg ={"case_result":{"name":self.TP.cur_case.name,"SeqNum":self.TP.cur_case.seqNum,"result":self.TP.caseStatus.result}}
        sendWeb(mesg,self.room,"sendState")



    def stage_result(self,result):
        mesg ={"stage_result":{"result":result}}
        sendWeb(mesg,self.room,"sendState")



    def send_mesg(self,mesg):
        sendWeb(mesg,self.room)



    def stage_initial(self):
        sendWeb("",self.room,"stageInitial")



    def test_end(self):
        sendWeb("",self.room,"testEnd",request_number=1)

   

     


class TestProcess(object):
    def __init__(self,dialog_Info,factory,msgQueue):
        self.FA = factory
        self.msgQueue = msgQueue
        self.dialog_Info = dialog_Info
        self.roomID = dialog_Info["roomID"]
        self.cellid = dialog_Info["cellid"]
        self.ip = dialog_Info["ip"]
        #self.ip = ""
        self.location = ""
        self.sn = dialog_Info["sn"]
        #self.mac1 = dialog_Info["mac1"]
        #self.mac2 = dialog_Info["mac2"]
        self.debug = dialog_Info["debug"]
        self.unitid = int(math.ceil(self.cellid/4.0))
        self.name = "unit%s"%(self.unitid)
        self.cur_stage=""
        self.cur_case=""
        self.logfile = os.path.join(buildPath(self.FA.tmpPath),"%s.log"%(self.name))
        self.SFCS = self.getSFCS()
        self.logger = self.FA.getLogger(self.roomID,self.name,self.logfile,msgQueue)
        self.stageList = self.FA.getStage()
        #self.FLR = TestFlowReader(self.FA.getTestFlowFile())
        self.FLR = TestFlowReader(dialog_Info["script"])
        self.LogServer = self.FA.getLogUploader(self.name)
        self.DBUpdate = DBTool(self)
        self.WebUpdate = WebTool(self)
        self.cmdService = cmdService()


    def run(self):
        try:
            self.DBUpdate.process_start()
            
           
            for index,stage in enumerate(self.stageList):
              
                if not index == 0:
                    time.sleep(3)
                    self.WebUpdate.stage_initial()
               
                if self.checkRoute(self.sn,stage):
                    continue

                

                self.cur_stage = stage 

                #self.getUnitIP()
                #self.getLocation()

                #self.cmdService.setMSGVar("localhost",self.roomID)
                self.cmdService.setMSGVar("10.35.49.15",self.roomID)
                

                self.cmdService.setSSHVar(self.ip,self.FA.dut_iniConfig["user"],self.FA.dut_iniConfig["pwd"])


                #testInfo = 'SN:  %s\nIP:  %s\nLOC:  %s' %(self.sn,self.ip,"self.location")
                #mydb.update(self.cellid,testInfo, '', 1)

                self.initStage(stage)

                self.unitInfo = self.FLR.getDUTInfo(self.name,self.cur_stage)
                #==========
                self.WebUpdate.testItem_list()
                #==========
               
                self.unitInfo.addVar("ip",self.ip)
                ##self.unitInfo.addVar("mac1",self.maclist[0])
                #self.unitInfo.addVar("mac2",self.mac2)


                for testCase in self.unitInfo.testCaseList:
                    self.CmdH = self.cmdService.getCmdHander(testCase.cmdType)
                    self.initCase(testCase)

                    realCmd = self.replace_param(testCase.cmd)
                    for line in self.CmdH.execCmd(realCmd,testCase.timeout*60):
                        self.logger.debug(line)

                    self.parserResult()
                    self.endCase(testCase)

                    if self.caseStatus.result == "FAIL":
                        break

                self.endStage()

                try:
                    self.sendSFCS()
                finally:
                    self.saveLog()
                    self.uploadLog()


                self.DBUpdate.stage_result()

                if self.stageStatus.result == "FAIL":
                    break


            self.checkStage()
            self.WebUpdate.test_end()

        except Exception as e:
            self.WebUpdate.send_mesg("\n====== traceback message ======")
            for line in traceback.format_exc().split("\n"):
                self.WebUpdate.send_mesg(line)
           
            self.DBUpdate.stage_result("FAIL")
            #self.DBUpdate.case_result("FAIL")
            raise(e)



    def replace_param(self,cmd):

        cmd_list = shlex.split(cmd)
        try:
            for index,item in enumerate(cmd_list):
                match_var_list = re.findall("\$\{[\w]*\}|\$[\w]+",item)
                for match_var in match_var_list:
                    for reg_form in ["\$\{(.*)\}","\$([\w]+)"]:
                        if re.findall(reg_form, match_var):
                            alternate_var = re.findall(reg_form,match_var)[0]
                            item = item.replace(match_var, getattr(self.unitInfo.var, alternate_var))
                cmd_list[index] = item

            return " ".join(cmd_list)

        except Exception as error:
            raise Exception(traceback.format_exc())



    def initStage(self,stage):
        self.cur_stage = stage
        self.stageStatus = StageStatus(stage)
        self.stageStatus.setStartTime(datetime.datetime.now())
        self._printStageHeader()
        self.DBUpdate.stage_start()
        self.DBUpdate.unit_info()


    def endStage(self):
        self.stageStatus.setEndTime(datetime.datetime.now())
        self._print_printStageTail()


    def initCase(self,testCase):
        self.cur_case = testCase
        self.caseStatus = CaseStatus(self.cur_case.name)
        self.caseStatus.setStartTime(datetime.datetime.now())
        self._printCaseHeader(testCase)
        self.DBUpdate.case_start()
        self.DBUpdate.stage_status()


    def endCase(self,testCase):
        self._printCaseTail()
        self.DBUpdate.case_result()


    def parserResult(self):
        self.caseStatus.setEndTime(datetime.datetime.now())

        if self.CmdH._returncode:
            CaseResult = "FAIL"
        else:
            CaseResult = "PASS"


        self.caseStatus.result = CaseResult
        self.caseStatus.errorCode = self.CmdH._returncode


        if self.caseStatus.result == "FAIL":
            self.stageStatus.result = "FAIL"
            self.stageStatus.errorCode = self.caseStatus.errorCode


    def _showOutput(self,msg):
        for line in msg.splitlines():
            self.logger.debug(line)
            #self.msgQueue.put([line,self.name])



    def _printCaseHeader(self,testCase):
        self.logger.debug("______________________________________")
        self.logger.debug("Test Case  : %s - %s"%(testCase.seqNum, testCase.name))
        self.logger.debug("Run %s Cmd : %s" % (testCase.cmdType,testCase.cmd))
        self.logger.debug("Timeout  : %s" % testCase.timeout)
        self.logger.debug("______________________________________")



    def _printCaseTail(self):
        self.logger.debug("## time: %s" %self.caseStatus.timeFormat(self.caseStatus.elapsedTime))
        self.logger.debug("## Reuslt: %s" %self.caseStatus.result)
        self.logger.debug("----------------")
        self.logger.debug("")
        self.logger.debug("")



    def _printStageHeader(self):
        self.logger.debug("====================================================")
        self.logger.debug("Start Stage: %s" % self.cur_stage)
        self.logger.debug("Start time: %s" % self.stageStatus.timeFormat(self.stageStatus.startTime))
        self.logger.debug("====================================================")



    def _print_printStageTail(self):
        self.logger.debug("****************************")
        self.logger.debug("End Stage: %s" % self.stageStatus.name)
        self.logger.debug("End Time: %s" % self.stageStatus.timeFormat(self.stageStatus.endTime))
        self.logger.debug("Elapsed Time: %s" % self.stageStatus.timeFormat(self.stageStatus.elapsedTime))
        self.logger.debug("Result: %s" % self.stageStatus.result)
        self.logger.debug("****************************")



    def checkRoute(self,sn,stage):
        result = self.SFCS.CheckRoute(self.sn,stage)
        #if result == "OK":
        if not result == "OK":
            return 0
        return 1



    def checkStage(self):
        if self.cur_stage == "":
            raise Exception("check Route Error!")



    def saveLog(self):
        self.logger.closeFile()
        self.unitlogPath = buildPath(os.path.join(buildPath(self.FA.logPath),"WIST_%s_%s_%s_%s" % (self.sn,self.stageStatus.name ,self.stageStatus.result,self.stageStatus.endTime.strftime("%Y%m%d_T%H%M%S"))))
        shutil.copy2(self.logfile,self.unitlogPath)



    def uploadLog(self):
        self.logger.info("")
        self.logger.info("======  Upload log to Log server  ======")

        shutil.make_archive(self.unitlogPath ,'zip', self.unitlogPath)
        self.zipPath = "%s.zip"%(self.unitlogPath)
        self.logger.info("log files: %s" % self.zipPath)

        self.LogServer.connect()
        self.LogServer.upload(self.zipPath, os.path.join("Wist", os.path.basename(self.zipPath)))
        #self.LogServer.disconnect()
        self.logger.info("Upload Success")




    def sendSFCS(self):
        self.logger.info("")
        self.logger.debug("======  Upload SFCS  ======")

        resultMapping = {"PASS":True,"FAIL":False}
        sn = self.sn
        line = self.FA.sfcs_iniConfig["sfcs_line"]
        stage = self.stageStatus.name
        station = self.FA.sfcs_iniConfig["sfcs_workstation"]
        emID = self.FA.opid_iniConfig["opid"]
        result = resultMapping[self.stageStatus.result]
        if result:
            trnDatas = self.sn
        else:
            trnDatas = self.stageStatus.errorCode
        defectRemark = ""
        extendTransInfo = '{"NOFW":"NOFW"}'


        reValue = self.SFCS.CompleteWithDefectRemark_Json(sn, line, stage, station, emID, result, trnDatas, defectRemark, extendTransInfo)
        self.logger.debug(reValue)
        if not reValue == "OK":
            pass
            #raise Exception("send SFCS error!")




    def dutSNType(self):
        module_sn = self.SFCS.GetUSNItem(self.sn,"AO", "K-", 0)
        if not module_sn == "NG":
            return module_sn,"AO"
        else:
            mb_sn = self.SFCS.GetUSNItem(self.sn, "AO", "BM", 0)
            if not mb_sn == "NG":
                return self.sn,"AO" 
            else:
                return self.sn,"A0"



    def getMBMac(self,sn,stage,i=0,maclist=[]):

        csn = self.SFCS.GetUSNItem(sn,stage,"06",i)

        if csn == "NG":
            if maclist == []:
                raise Exception("get MB MAC fail")
            return
        maclist.append(csn)
        self.getMBMac(sn,stage,i+1,maclist)
        return maclist

   
    def getMBMac2(self):
        result  = self.SFCS.GetUSNInformation(self.cur_stage,self.sn,"MAC0","")
        print(self.cur_stage,self.sn)
        print(result)
        if result.GetUSNInformationResult != "OK":
            raise Exception("get MB MAC by GetUSNInformation fail")

        return result.InfoValue


    def getUnitIP(self):
        try:
            #self.ip="127.0.0.1"
            #return

            mydb.update(self.cellid+2,"Get Unit IP",'Testing', 1)
            sn,stage = self.dutSNType()
            #self.maclist = list(set(self.getMBMac(sn,stage)))
            self.maclist = [self.getMBMac2()]
            #self.maclist =["00:60:48:60:73:40"]
            print(self.maclist)
            for mac in self.maclist:
                curMac=':'.join(mac[i:i+2] for i in range(0,12,2))
                #ip = get_ip.get_ip(curMac)
                ip = get_ip.get_ip2(curMac)
                if not ip == None:
                    self.ip = ip
                    break

            if self.ip == "":
                raise Exception("get Unit IP error")

        except Exception as e:
            mydb.update(self.cellid+2,"Get Unit IP",'FAIL', 3)
            raise(e)


    def getLocation(self):

        codeMap={"00":"A","01":"B","02":"C","03":"D"}

        try:
            mydb.update(self.cellid+2,"Get location",'Testing', 1)

            ssh =ssh_cmd2(self.ip,self.FA.dut_iniConfig["user"],self.FA.dut_iniConfig["pwd"])
            ssh.connect()

            locationCmd="ipmitool raw 0x4 0x2d 0xcc"
            firstLine = list(ssh.execCmd(locationCmd))[0]
            self.logger.debug(firstLine)
            if not ssh._returncode == 0:
                raise Exception("get loaction error")

            code = firstLine.strip().split()[0]
            self.location = codeMap[code]

        except Exception as e:
            mydb.update(self.cellid+2,"Get location",'FAIL', 3)
            raise(e)


    def getSFCS(self):

        mydb.update(self.cellid+2,"Connect SFCS",'Testing', 1)

        try:
            SFCS = self.FA.getSFCSConfig(self.debug)
        except Exception as e:
            mydb.update(self.cellid+2,"Connect SFCS",'FAIL', 3)
            mydb.update(self.cellid+3,"FAIL","",1)
            raise(e)

        return SFCS


if __name__ == "__main__":

    from factory import Factory
    from multiprocessing import Process, Value, Lock , Queue


    os.environ['LaunchPath'] = os.path.dirname(os.path.realpath(sys.argv[0]))
    dialog_Info = {"cellid":1,"ip":"10.34.53.48","sn":"12345697","debug":0}
    dialog_Info1 = {"cellid":5,"ip":"10.34.53.48","sn":"56789","debug":0}

    t1 = TestProcess(dialog_Info,Factory(), Queue())
    #t1.run()

    t2 = TestProcess(dialog_Info1,Factory(),Queue())

    p1 = Process(target=t1.run)
    p2 = Process(target=t2.run)
    p2.start()
    p1.start()
    print(p1.pid,p2.pid)
    p1.join()
    p2.join()



