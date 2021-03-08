import os
import subprocess
from shutil import copyfile
import logging


class Samba:

    def __init__(self, ip, username, password, remoteDir, mountPoint,unitName,lock):
        self.ip = ip
        self.username = username
        self.password = password
        self.remoteDir = remoteDir
        self.mountPoint = mountPoint
        self.logger = logging.getLogger(unitName)
        self.lock = lock

    def connect(self):
        self.mount()


    def mount(self):

        self.lock.acquire()

        # Check if path is exist
        if not os.path.exists(self.mountPoint):
            os.mkdir(self.mountPoint)

        # Check if path is mounted
        if not os.path.ismount(self.mountPoint):
            mountCmd = "mount -t cifs -o username=%s,password=%s //%s/%s %s" % \
                (self.username, self.password, self.ip, self.remoteDir, self.mountPoint)

            self.logger.debug("mount command: %s" % mountCmd)
            subprocess.call(mountCmd, shell=True, stdout=subprocess.PIPE)

        self.lock.release()


    def disconnect(self):
        self.umount()


    def umount(self):
        umountCmd1 = " fuser -ck %s" % self.mountPoint
        umountCmd2 = "umount %s" % self.mountPoint

        #subprocess.call(umountCmd1,shell=True, stdout=subprocess.PIPE)
        subprocess.call(umountCmd2,shell=True, stdout=subprocess.PIPE)


    def upload(self, src, dst):

        mdst = os.path.join(self.mountPoint, dst)

        if not os.path.isdir(os.path.dirname(mdst)):
            os.makedirs(os.path.dirname(mdst))

        self.logger.debug("upload %s to %s" % (src,mdst))
        copyfile(src, mdst)





class WinSamba:

    def __init__(self, ip, username, password, remoteDir, mountPoint,dut):
        self.ip = ip
        self.username = username
        self.password = password
        self.remoteDir = remoteDir
        self.mountPoint = mountPoint
        self.logger = dut.factory.createLogger(self.__class__.__name__, dut.dutid)

    def connect(self):
        self.mount()

    def mount(self):
        if not os.path.exists("z:\\"):
            mountCmd = "net use z: \\\\%s\\%s /user:%s %s" % \
                (self.ip,self.remoteDir,self.username,self.password)

            self.logger.debug("mount command: %s" % mountCmd)
            subprocess.call(mountCmd, shell=True, stdout=subprocess.PIPE)


    def disconnect(self):
        self.umount()


    def umount(self):
        umountCmd = "net use z: /delete"
        subprocess.call(umountCmd, shell=True, stdout=subprocess.PIPE)


    def upload(self, src, dst):
        mpath = "z:"
        self.logger.debug("upload %s to %s" % (src,os.path.join(mpath, dst)))
        copyfile(src, os.path.join(mpath,dst))



class Samba_Debug:

    def __init__(self, ip, username, password, remoteDir, mountPoint,dut):
        self.ip = ip
        self.username = username
        self.password = password
        self.remoteDir = remoteDir
        self.mountPoint = mountPoint
        #self.logger = BaseLogger(self.__class__.__name__)
        self.logger = dut.factory.createLogger(self.__class__.__name__, dut.dutid)

    def connect(self):
        self.mount()

    def mount(self):
        mountCmd = "mount -t cifs -o username=%s,password=%s //%s/%s %s" % \
            (self.username, self.password, self.ip, self.remoteDir, self.mountPoint)
        self.logger.debug("mount command: %s" % mountCmd)

    def disconnect(self):
        self.umount()

    def umount(self):
        umountCmd = "umount %s" % self.mountPoint
        self.logger.debug("umount command: %s" % umountCmd)

    def upload(self, src, dst):
        self.logger.debug("No upload in debug mode")
        self.logger.debug("upload source file: %s" % src)
        self.logger.debug("upload destination: %s" % os.path.join(self.mountPoint, dst))



class WinSamba_Debug:

    def __init__(self, ip, username, password, remoteDir, mountPoint,dut):
        self.ip = ip
        self.username = username
        self.password = password
        self.remoteDir = remoteDir
        self.mountPoint = mountPoint
        self.logger = dut.factory.createLogger(self.__class__.__name__, dut.dutid)

    def connect(self):
        self.mount()

    def mount(self):
        mountCmd = "net use z: \\\\%s\\%s" % \
            (self.ip,self.remoteDir)
        self.logger.debug("mount command: %s" % mountCmd)

    def disconnect(self):
        self.umount()

    def umount(self):
        umountCmd = "net use z: /delete"
        self.logger.debug("umount command: %s" % umountCmd)

    def upload(self, src, dst):
        self.logger.debug("No upload in debug mode")
        self.logger.debug("upload source file: %s" % src)
        self.logger.debug("upload destination: %s" % os.path.join(self.mountPoint, dst))
