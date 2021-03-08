import logging
import sys


class BaseLogger(object):

    def __init__(self,name,logFile):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        #formatter = logging.Formatter('[%(asctime)s] [%(threadName)s] %(message)s')

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)

        self.fh = logging.FileHandler(logFile, 'w', encoding='utf-8')
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)


    def debug(self,msg):
        self.logger.debug(msg)



    def info(self,msg):
        self.logger.info(msg)



    def warning(self,msg):
        self.logger.warning(msg)



    def error(self,msg):
        self.logger.error(msg)



    def getLogger(self):
        return self.logger




    def resetFile(self):
        self.logger.addHandler(self.fh)



    def closeFile(self):
        self.logger.removeHandler(self.fh)
        self.fh.flush()
        self.fh.close()





if __name__ == '__main__':
    import os

    logger=BaseLogger("main","123.txt")

    logger.debug("ddddddddddddddd")
    logger.debug("bbbbbbbbbbbbbbb")
    raw_input("Press enter to continue")
    logger.closeFile()
    logger.resetFile()
    logger.debug("ccccccccccccccccccc")
    print(logger.handlers)



    #logger=BaseLogger("321","168.txt").getLogger()
    #logger.debug("3038fjfkj")



