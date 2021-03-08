from lxml import etree, objectify

class DUTInfo(object):
    def __init__(self):
        self._var = None
        self._stage = None
        self._testCaseList = []


    @property
    def var(self):
        return self._var

    @property
    def stage(self):
        return self._stage

    @property
    def testCaseList(self):
        return self._testCaseList


    def set_var(self,VarObj):
        self._var = VarObj


    def set_stage(self,StageObj):
        self._stage = StageObj


    def set_testCaseList(self,testCaseList):
        self._testCaseList = testCaseList


    def addVar(self,name,value):
        setattr(self.var,name,value)



class Var(object):
    def __init__(self):
	    pass



class TestCase(object):
    def __init__(self,seqNum,name,cmd,cmdType,errCode,timeout=5):
        self.seqNum =seqNum
        self.name = name
        self.cmd = cmd
        self.cmdType = cmdType
        self.errCode= errCode
        self.timeout = timeout



class Stage(object):
    def __init__(self):
        self.name = None




class TestFlowReader():
    def __init__(self,path):
        #self.unit = unit
        #self.stage = stage
        f = open(path, 'r')
        f.seek(0) #Ensure the file is ready for parsing
        self.root = objectify.fromstring(f.read())


    def getEnvVar(self,dut):
        varClass = Var()
        for DUT in self.root.EnvVar.getchildren():
            if DUT.tag.lower() == dut:
                for element in DUT.getchildren():
                    setattr(varClass, element.tag, element.text)
                break

        return varClass


    def getTestCase(self,stage):
        CaseList=[]
        for eachStage in self.root.TestPlan.TestStage:
            if eachStage.attrib['stage'] == stage:
                for index,eachCase in enumerate(eachStage.TestCase,1):
                    if hasattr(eachCase, 'Cmd'):
                    #if eachCase.Command.text == "Command":
                        cmdType = "SUB"
                        cmd = eachCase.Cmd.text
                    elif hasattr(eachCase, 'SSHCmd'):
                    #else eachCase.Command.text = "SSHCmd":
                        cmdType = "SSH"
                        cmd = eachCase.SSHCmd.text
                    elif hasattr(eachCase, 'MSGCmd'):
                        cmdType = "MSG"
                        cmd = eachCase.MSGCmd.text

                    CaseList.append(TestCase(index,eachCase.attrib["name"],cmd,cmdType,eachCase.ErrCode.text,int(eachCase.Timeout.text)))
                break

        return CaseList


    def getStage(self,stage):
        stageClass = Stage()
        for eachStage in self.root.TestPlan.TestStage:
            if eachStage.attrib['stage'] == stage:
                stageClass.name = eachStage.attrib['stage']
                break

        return stageClass


    def getDUTInfo(self,unit,stage):
        dutInfo = DUTInfo()
        dutInfo.set_stage(self.getStage(stage))
        dutInfo.set_testCaseList(self.getTestCase(stage))
        dutInfo.set_var(self.getEnvVar(unit))

        return dutInfo

'''
import xml.etree.ElementTree as ET

class TestFlowReader():
    def __init__(self,path):
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()


    def getEnvVar(self,dut):
        for tag in self.root.findall("EnvVar/%s"%(dut)):
            for element in tag.getchildren():
                print(element.tag,element.text)


    def TestStage(self):
        pass
'''


if __name__ == '__main__':

    FR=TestFlowReader("/PROJECT/brade_GUI/ernie/PROJECT/Infinity_MLK/Infinity_MLK_flow.xml","DUT1","TN")
    dutInfo = FR.getDUTInfo()
    print(dutInfo.var.switchIP)


