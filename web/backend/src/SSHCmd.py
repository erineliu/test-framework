#!/usr/bin/python


"""
This runs a command on a remote host using SSH. At the prompts enter hostname,
user, password and the command.
"""

import pexpect
import getpass, os


class ExceptionSsh(Exception):

    '''Exception class raised by this module.
    '''
    def __init__(self, value):
        super(ExceptionSsh, self).__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)



class ssh_cmd():

    def __init__(self,host,user,pwd):

        self.PROMPT = ['# ', '>>> ', '> ', '\$ ']
        self.reCode = -1
        self.cmdOut = ""
        self.host = host
        self.user = user
        self.pwd = pwd


    def connect(self):
        ssh_newkey = 'Are you sure you want to continue connecting'
        self.child = pexpect.spawn('ssh -l %s %s'%(self.user, self.host))
        i = self.child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])

        if i == 0: # Timeout
            print(self.child.before)
            ex = 'ERROR! could not login with SSH.'
            raise ExceptionSsh(ex)


        if i == 1: # SSH does not have the public key. Just accept it.
            self.child.sendline ('yes')
            self.child.expect ('password: ')
            i = self.child.expect([pexpect.TIMEOUT, 'password: '])
            if i == 0: # Timeout
                print(self.child.before)
                ex = 'ERROR! could not login with SSH.'
                raise ExceptionSsh(ex)

        if i == 2:
            try:
                self.child.sendline(self.pwd)
                self.child.expect(self.PROMPT)
            except:
                ex = 'ERROR! ssh password is error.'
                raise ExceptionSsh(ex)


    def execCmd(self,cmd,timeout=30):
        try:
            self.child.timeout=timeout
            self.child.sendline(cmd)
            self.child.expect(self.PROMPT)
            self.cmdOut=self.child.before.decode()
            self.getCmdReCode()

        except pexpect.TIMEOUT as e:
            print("error: cmd time out")
            self.cmdOut=self.child.before.decode()
            self.reCode=1
        except Exception as e:
            self.reCode=1
            raise e

        finally:
            self.child.close()

    def getCmdReCode(self):
        self.child.sendline("echo $?")
        self.child.expect(self.PROMPT)
        self.reCode=int(self.child.before.decode().splitlines()[1])


    def close(self):
        self.child.close()


if __name__ == '__main__':
    try:
        ssh1 = ssh_cmd("10.34.53.48","ernie","ernie321")
        ssh1.connect()
        #ssh1.execCmd("echo dfdfdfd",10)
        ssh1.execCmd("bash /home/ernie/test1",10)
        print(ssh1.cmdOut)
        print(ssh1.reCode)

    except Exception as e:
        pass
        print(str(e))
        #traceback.print_exc()
        #os._exit(1)
