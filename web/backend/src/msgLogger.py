from backend.src.testLogging import BaseLogger
from backend.src.curlTest import sendWeb



class VMesg_Decorator(object):

    def __getattribute__(self,Name):
        attr = object.__getattribute__(self, Name)
        if hasattr(attr, '__call__'):
            def newfunc(*args,**kwargs):
                if Name in ["debug","info","error","warning"]:
                   if self.__dict__["msgQueue"]:
                        self.__dict__["msgQueue"].put([args[0],self.__dict__["name"]])
                        sendWeb(args[0],self.__dict__["roomID"])
                        

                result = attr(*args, **kwargs)
                return result
            return newfunc
        else:
            return attr


class Mesg_Logger(BaseLogger,VMesg_Decorator):
    def __init__(self,roomID,name,logFile,msgQueue):
        self.msgQueue = msgQueue
        self.name = name
        self.roomID = roomID
        BaseLogger.__init__(self,name,logFile)





if __name__ == "__main__":

    #from multiprocessing import Process, Value, Lock, Queue
    from Queue import Queue

    q1 =Queue()
    logger=Mesg_Logger("main","123.txt",q1)
    logger.debug("sss")
    print(list(q1.queue))
