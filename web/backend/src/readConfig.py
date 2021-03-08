import sys
import os
import datetime
import time

if sys.version[:1] == '2':
    import ConfigParser as configparser
else:
    import configparser 


class IniConfig:

    def __init__(self, path):
        self.path = path
        self.init()

  
    def init(self): 
        self.cf = configparser.RawConfigParser()
        self.cf.optionxform = str
        self.cf.read(self.path)


    def get(self,section, key):
        return self.cf.get(section, key)



    def getAll(self):
        return self.cf._sections

 

    def getSectionData(self,name):
        return self.cf._sections[name]



    def set(self,section, key, value):

        if not self.cf.has_section(section):
            self.cf.add_section(section)

        self.cf.set(section, key, value)
        self.cf.write(open(self.path,'w'))




if __name__ == '__main__':
    #initool=IniConfig("/PROJECT/Yama/tmp/DUT1.info")
    #initool.set("ddd","car","test")
    #dict1=initool.getAll()
    #for i,v in dict1["config"].items():
    #    print(i,v)

    config1 = IniConfig("config.ini")
    configData =config1.getAll()
    print(configData["SFCS"]["sfcs_addr"])
    print(type(configData["SFCS"]["sfcs_tunnel_enable"]))
    time.sleep(30)
    configData =config1.getAll()
    print(configData["SFCS"]["sfcs_addr"])


