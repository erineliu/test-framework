import subprocess
import signal
import os

class Subp(object):

    def popen(self,cmd,**kwargs):

        if os.name == 'posix':
            kwargs.update({'preexec_fn':os.setsid})
        else:
            kwargs.update({'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP})

        return subprocess.Popen(cmd,**kwargs)


    def stop(self,pid):
        if os.name == "posix":
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
        else:
            os.kill(pid,signal.CTRL_C_EVENT)


if __name__ == '__main__':

   aa= Subp()
   aa.popen("ddd", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)