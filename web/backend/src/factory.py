import os
from backend.src.readConfig import IniConfig
from backend.src.sfcs import SFCS
from backend.src.testLogging import BaseLogger
from backend.src.samba import Samba
from backend.src.msgLogger import Mesg_Logger
#import threading
import multiprocessing


class Factory:
    def __init__(self,configFile):
        #self.configFile = "%s/%s"%(os.environ['LaunchPath'],"config.ini")
        self.configFile = configFile
        #print(self.configFile)

        self.tmpPath = "%s/%s"%(os.environ['LaunchPath'],"tmp")
        self.logPath = "%s/%s"%(os.environ['LaunchPath'],"log")
        #self.logger = BaseLogger(self.__class__.__name__,"%s/tmp/%s"%(os.environ['LaunchPath'],"factory.log")).getLogger()
        self.loadConfig()
        self.uploadLock = multiprocessing.Lock()


    def loadConfig(self):
        #self.logger.debug("## load ini config ##")
        self.IniConfig = IniConfig(self.configFile)
        self.sfcs_iniConfig = self.IniConfig.getSectionData("SFCS")
        self.sfcsTunnel_iniConfig = self.IniConfig.getSectionData("SFCS_TUNNEL")
        self.hugin_iniConfig = self.IniConfig.getSectionData("HUGIN")
        self.project_iniConfig = self.IniConfig.getSectionData("PROJECT")
        self.logServer_iniConfig = self.IniConfig.getSectionData("LOG_SERVER")
        self.dut_iniConfig = self.IniConfig.getSectionData("DUT")
        self.opid_iniConfig = self.IniConfig.getSectionData("OPID")


    def getSFCSConfig(self,debug_mode):
        if not debug_mode:
            return SFCS(self.sfcs_iniConfig,self.sfcsTunnel_iniConfig)
        else:
            return SFCS_Debug()



    def getLogger(self,roomID,name,logFile,msgQueue):
        #return BaseLogger(name,logFile)
        return Mesg_Logger(roomID,name,logFile,msgQueue)




    def getStage(self):
        if self.sfcs_iniConfig["sfcs_stage"].find(",") != -1:
            return [i.strip() for i in self.sfcs_iniConfig["sfcs_stage"].split(",")]
        else:
            return [self.sfcs_iniConfig["sfcs_stage"].strip()]



    def getTestFlowFile(self):
        return self.project_iniConfig["project_flow"]




    def getLogUploader(self,unitName):
        return Samba(ip=self.logServer_iniConfig["log_ip"],
                            username=self.logServer_iniConfig["log_user"],
                            password=self.logServer_iniConfig["log_pwd"],
                            remoteDir=self.logServer_iniConfig["mount_folder"],
                            mountPoint=self.logServer_iniConfig["mount_point"],
                            unitName=unitName,
                            lock =self.uploadLock)

