import paramiko
import socket
from threading import Timer




class RunCMDTimeoutError(Exception):

    '''Exception class raised by this module.
    '''
    def __init__(self, value):
        super(ExceptionSsh, self).__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)



class ssh_cmd2:
    def __init__(self, host="", username="", password=""):
        self.host = host
        self.username = username
        self.password = password
        self._returncode = -1


    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.username, password=self.password, look_for_keys=False,timeout=10,port=60006)
        except Exception as e:
            #raise type(e)("%s\nmsg: %s"%(e.message ,"ssh connet fail"))
            raise "ssh connet fail"

    def execCmd(self,command,timeout=30):

        try:
            self.connect()
            self.timeout_timer = Timer(timeout, self.killWhenTimeout)
            stdin, stdout, stderr = self.client.exec_command(command)
            self.timeout_timer.start()

            while 1:
                line = stdout.readline().strip()
                if not line and stdout.channel.exit_status_ready():
                    break

                yield line
            self._returncode = stdout.channel.recv_exit_status()
        except RunCMDTimeoutError:
            yield "test case time out !!"


        except Exception as e:
            self._returncode = 1
            raise (e)


        finally:
            if hasattr(self,"timeout_timer"):
                self.timeout_timer.cancel()
            self.close()


    def close(self):
        self.client.close()


    def killWhenTimeout(self):
        self.client.close()
        self._returncode = 1
        raise Exception_RunCMDTimeout






if __name__ == "__main__":
    a=ssh_cmd2("10.34.53.48","ernie","ernie321")
    a.connect()
    for i in a.execCmd("ping 127.0.0.1 -c 3"):
        print(i)
    a.close()

