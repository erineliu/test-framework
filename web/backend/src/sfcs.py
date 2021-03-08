#!/usr/bin/env python
# -*- coding=utf-8 -*-
#
# Create time   : 2018/09/25 12:14 AM
# File name     : sfcs.py
#
"""
Call SFCS WebService function.
Modify date:2019/01/02
    add ssh tunnel function to connect remote sfcs
"""
import subprocess, pexpect, time
from zeep import Client
from zeep.transports import Transport
import os
import json


class SFCS(object):

    def __init__(self,sfcsDict,sshTunnelDict):
        self.sfcsDict=sfcsDict
        self.sshTunnelDict=sshTunnelDict

        try:
            self.setURL(self.sfcsDict["sfcs_addr"])
            if int(self.sfcsDict["sfcs_tunnel_enable"]):
                self.openSSHClient()
            else:
                self.openClient()

        except Exception as ex:
            raise Exception(ex)

        '''
        self.__host = '192.168.13.227' # Host of the transit service
        self.__user = 'wihte' # User of the transit service
        self.__password = 'Wistron00' # Password of the transit service
        self.__sfcs = '10.38.36.81:80' # IP of remote SFCS QAS
        self.__sfcs = '10.38.30.11:80' # IP of remote SFCS PRD
        '''

    def openClient(self):
        timeout = Transport(timeout=10)
        self.__client = Client(self.__url, transport=timeout)


    def openSSHClient(self):
        # create sshtunnel to connect SFCS
        self.__ssh_tunnel()
        # zeep module, timeout default is 300 seconds.
        timeout = Transport(timeout=10)
        self.__client = Client(self.__url, transport=timeout)
        self.__client.transport.session.proxies = {'http': 'localhost:3306',}


    def setURL(self,url):
        if '?wsdl' in url.lower():
            self.__url = url
        else:
            self.__url = "%s?wsdl" % url


    def __ssh_tunnel(self):
        """ create ssh tunnel to connect sfcs server"""

        host = self.sshTunnelDict["ssh_ip"]
        user =  self.sshTunnelDict["ssh_user"]
        password = self.sshTunnelDict["ssh_password"]
        sfcs = self.sshTunnelDict["target_ip"]

        tunnel_command = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -C -N -f -L 3306:{0} {1}@{2}'.format(sfcs, user, host)
        retry = 5
        while retry:
            if not self.__check_ssh():
                try:
                    ssh_tunnel = pexpect.spawn(tunnel_command)
                    ssh_tunnel.expect('password:')
                    time.sleep(0.1)
                    ssh_tunnel.sendline(password)
                    ssh_tunnel.expect(pexpect.EOF)
                    retry -= 1
                except:
                    raise Exception("Create SSH Tunnel Failed: retry 5")
            else: break

    def __check_ssh(self):
        """Check if ssh tunnel create or not"""
        sfcs = self.sshTunnelDict["target_ip"]

        cmd = "ps aux | grep ssh | awk '{print $20}'"
        result = subprocess.Popen(cmd,
                                    shell= True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        stdout, stderr = result.communicate()
        if sfcs not in stdout.decode():
            return False
        else: return True


    def CheckRoute(self, SerialNumber, StageCode):
        return self.__client.service.CheckRoute(SerialNumber, StageCode)



    def UploadUSNInfo(self, SerialNumber, StageCode, InfoName, InfoValue):
        return self.__client.service.UploadUSNInfo(SerialNumber,
                                                   StageCode,
                                                   InfoName,
                                                   InfoValue)


    def GetUSNInformation(self,StageCode,SerialNumber ,infoName, infoValue):
        return self.__client.service.GetUSNInformation(StageCode,
                                                       SerialNumber,
                                                       infoName,
                                                       infoValue)

    def GetUSNItem(self, SerialNumber, StageCode,category,sequence):
        #category = '01'
        #sequence = 0
        return self.__client.service.GetUSNItem(SerialNumber,
                                                StageCode,
                                                category,
                                                sequence)



    def DynamicDBFunction(self,dynamicDBFun,StageCode,dynamicpara):

        '''
        dynamicpara = '{"WORKSTATION":"TEST_FCT","LOCATION":"0323418157898^1^GPU_LOWER_GPU1"}'
        dynamicDBFun = "FUN_NAOMI_UPSERTLOCATION_BATCH" or "FUN_NAOMI_UPSERTLOCATION_BATCH_USN"
        '''

        dynpara_dict = json.loads(dynamicpara)

        dparray = self.__client.get_type("ns0:ArrayOfClsDynamicParameter")()
        dp1 = self.__client.get_type("ns0:clsDynamicParameter")()
        dp2 = self.__client.get_type("ns0:clsDynamicParameter")()


        dp1.strParam="WORKSTATION"
        dp1.strValue=dynpara_dict["WORKSTATION"]

        dp2.strParam="LOCATION"
        dp2.strValue=dynpara_dict["LOCATION"]

        dparray['DynamicParameter'].append(dp1)
        dparray['DynamicParameter'].append(dp2)


        return self.__client.service.DynamicDBFunction(dynamicDBFun,
                                                       StageCode,
                                                       dparray)




    def CompleteWithDefectRemark_Json(self, sn, line, stage, station, emID, result, trnDatas, defectRemark, extendTransInfo):
        '''
        r = sfcs.CompleteWithDefectRemark_Json("0571519400173", "AD", "TP", "4R26A", "10712137", True, trnDatas, defectRemark, '{"BMC": "1.00"}')
        print(r)

        line = "AD"
        station: Physical location in factory. Ex: station = "4L19A"

        result = True
        trnDatas = Serial Number
        defectRemark = ""

        result = False
        trnDatas = Error Code
        defectRemark = Error Message

        extendTransInfo = Additional information in JSON format
        Ex: '{"IDT_RETIMER_LOWER_U93": "2.0", "IDT_RETIMER_LOWER_U96": "2.0"}'
        '''

        empthArrayPlaceholder = self.__client.get_type('ns0:ArrayOfString')
        TranDatas_list = empthArrayPlaceholder()
        TranDatas_list.TrnData.append(trnDatas)


        return self.__client.service.CompleteWithDefectRemark(sn, line, stage, station, emID, result, TranDatas_list, defectRemark, extendTransInfo)




    def Complete(self, SerialNumber, Line, StageCode, Station, OperatorID, TestResult, ErrorCode):
        empthArrayPlaceholder = self.__client.get_type('ns0:ArrayOfString')
        TranDatas = empthArrayPlaceholder()

        if TestResult:
            TranDatas.TrnData.append("")
        else:
            TranDatas.TrnData.append(ErrorCode)
        return self.__client.service.Complete(SerialNumber,
                                              Line,
                                              StageCode,
                                              Station,
                                              OperatorID,
                                              TestResult,
                                              TranDatas)






if __name__ == "__main__":

    config1={"sfcs_addr":"http://10.38.30.12/Tester.WebService/WebService.asmx","sfcs_tunnel_enable":0}
    config2={"ssh_ip":"10.38.120.227","ssh_user":"wihte","ssh_password":"Wistron00","target_ip":"10.38.30.12:80"}

    sfcsfunc = SFCS(config1,config2)
    #result = sfcsfunc.CheckRoute("1571519000008", "TN")
    #print(result)


    #result = sfcsfunc.Complete("1571519000008", "AG", "TN", "001", "10803063",1,"")
    #print(result)

    #result = sfcsfunc.CompleteWithDefectRemark_Json("1571519000008", "AG", "TN", "001", "10803063",True, "","", '{"NOFW":"NOFW"}')
    #print(result)

    result1 = sfcsfunc.GetUSNItem("WTWE2202600014", "AO", "BM", 0)
    print(result1)
    print("===============================================")
    result1 = sfcsfunc.GetUSNItem("WTWE9202600009", "AO", "K-", 0)
    result = sfcsfunc.GetUSNItem(result1, "AO", "06", 0)
    print(result)
    print("================================================")


    def getMBMac(i=0,maclist=[]):
        csn = sfcsfunc.GetUSNItem("55506901000101301A", "A0", "06", i)
        if csn == "NG":
            if maclist == []:
                raise Exception("Can't get the mac")
            return

        maclist.append(csn)
        getMBMac(i+1,maclist)
        return maclist

    # maclist = []
    #data=getMBMac()
    #print(list(set(data)))






    #result = sfcsfunc.CheckRoute("a1234568", "TP")
    #result = sfcsfunc.Complete("1", "2","3","4","5","6","7")
    #print(result)

    #sfcsfunc = SFCS("http://localhost:3306/Tester.WebService/WebService.asmx")
    #result = sfcsfunc.CheckRoute("1571519000008", "TN")
    #print(result)
