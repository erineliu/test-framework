import shlex
import subprocess
from backend.src.subp import Subp
from threading import Timer
import time

class subRunCmd(object):

    def __init__(self):
        self.errCode = None
        self.errMsg =[]
        self.version = 'N/A'
        self.followingActions = []
        self._returncode = -1
        self.subp = Subp()




    def execCmd(self,cmd,timeout):

        ## Run test case ##
        self.timeout_timer = Timer(timeout, self.killWhenTimeout)

        try:
            self.test_process = self.subp.popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
            self.timeout_timer.start()
            '''
            while True:
                output = self.test_process.stdout.readline().decode('utf-8','ignore').rstrip()
                if output == '' and  self.test_process.poll() is not None:
                    break
                if output:
                    yield self.StdFilterForTest(output)
            '''
            for line in iter(self.test_process.stdout.readline, b''):
                yield self.StdFilterForTest(line.decode('utf-8','ignore').rstrip())
            while self.test_process.poll() is None:
                time.sleep(0.01)

        finally:
            self.timeout_timer.cancel()

        self._returncode = self.test_process.returncode


    @property
    def returncode(self):
        return self._returncode


    def killWhenTimeout(self):
        self.stop()
        self._returncode = 1


    def stop(self):
        if not hasattr(self,"test_process"):
            return

        self.subp.stop(self.test_process.pid)


    def StdFilterForTest(self, line):
        if '[Version]' in line:
            self.version = self.StdHandler(line)
        elif '[Error Code]' in line:
            self.errCode = self.StdHandler(line)
        elif '[Error Message]' in line:
            self.errMsg.append(self.StdHandler(line))
        elif '[Following Actions]' in line:
            self.followingActions.append(self.StdHandler(line))
        else:
            return line


    def StdHandler(self, line):
        return line.split(']')[1].strip()


if __name__ == "__main__":
    p1=subRunCmd()
    for i in p1.execCmd("ipmitool 30",10):
        print(i)
    print(p1.returncode)




