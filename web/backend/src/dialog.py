#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import os
    import sys
    import re
    import math
    import wx
    import wx.grid
    from ctypes import *
    import threading
    from threading import Timer
    import time

    if sys.version[:1] == '2':
        import wx.lib.pubsub.setupkwargs
        from wx.lib.pubsub import pub
    else:
        from pubsub import pub

    #from wx.lib.pubsub import Publisher

    import datetime
    from multiprocessing import Process, Value, Lock, Queue
    import traceback
    import signal

    # created module
    #import mydb
    from src.mydb import mydb
    from src.testProcess import TestProcess
    from src.factory import Factory
    from src.logViewer import logView
    import atexit



except ImportError as e:
    print("")
    print("\33[31;1mImportError: %s.\33[0m" % e)
    print("")
    exit(1)



msgQueue = Queue()
StatusQueue = Queue()

# global variable
#os.environ['LaunchPath'] = os.path.dirname(os.path.realpath(sys.argv[0]))
VERSION = '''V1.00.12'''
global CELLS_START_STATUS
CELLS_STATUS = [] # each item contain CellID, CellStatus, SN......
LOG = "errorTest.log"
CELLS_START_STATUS = {0:"default"}
LOCK = Lock()
mydb.create_db()
factory=Factory()


def exit_handler():
    #pass
    factory.getLogUploader(None).disconnect()

atexit.register(exit_handler)



# write log
def write_log(filename, type, buff):
    fp = open(filename, type)
    fp.write(buff)
    fp.close()




def call_run(cellid,sn,msgQueue):

    try:
        global Test
        unitid = int(math.ceil(cellid/4.0))
        dialog_Info = {"cellid":cellid,"ip":"10.34.53.48","sn":sn,"debug":0}
        #tp = TestProcess(dialog_Info,Factory(),msgQueue)
        tp = TestProcess(dialog_Info,factory,msgQueue)
        tp.run()
        testStatus = mydb.result2flag(tp.stageStatus.result)
        StatusQueue.put({"name":"CELLS_STATUS","data":{"_UnitInfo__testStatus":testStatus},"unitid":unitid})

    except:
        buff = "%s" % traceback.format_exc()
        write_log(LOG, "a", buff)

        Test = 1
        testStatus = 5
        StatusQueue.put({"name":"CELLS_STATUS","data":{"_UnitInfo__testStatus":testStatus},"unitid":unitid})
        msgQueue.put([buff,"unit%s"%(unitid)])

        buff = "Error: Run Unit %d Failed." % int(math.ceil(cellid/4.0))


        with LOCK:
            CELLS_START_STATUS.update({cellid:buff})
        #   CELLS_START_STATUS

        #exit(-1)

    finally:
        StatusQueue.put({"name":"CELLS_STATUS","data":{"_UnitInfo__startStatus":0},"unitid":unitid})
        msg = "Unit %s:Test %s --> End Time: %s\n" % (unitid,mydb.flag2result(testStatus),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        StatusQueue.put({"name":"TCTRL_SHOW_MSG","data":msg,"unitid":unitid})



class CellInfo(Structure):
    def __init__(self):
        self.__uutId = 0
        self.__cellId = 0
        self.__cellTestStatus = 0


class UnitInfo(Structure):
    def __init__(self):
        self.__SerialNumber = ""
        self.__MAC = ""
        self.__type = ""
        #self.__operatorId = ""
        self.__startTime = "00:00:00"
        self.__testStatus = 0   # unstart:0  testing: 1  pass: 2  fail: 3  Unknow: 4  start failed: 5
        self.__startStatus = 0
        self.__inputStatus = 0
        self.__process = 0
        self.__processID = -1
        self.__cyberSwitchIP = ""
        self.__unitInfo = []
        i=0
        for i in range(0, 4):
            cellInfo = CellInfo()
            cellInfo.__uutId = 0
            cellInfo.__cellId = 0
            cellInfo.__cellTestStatus = 0

            self.__unitInfo.append(cellInfo)


#read the selection cell test log
class ShowLog(threading.Thread):
    def __init__(self, logname):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.__stop = threading.Event() # for stop thread
        self.__stop.set()   # set its value to True
        self.__startpos = 0
        self.pos = 0
        self.__testlog = logname


    def run(self):
        '''
        while self.__stop.isSet():
            if self.__stop == False:
                print "Have stoped."
            self.readlog()
            #self.readlog_line()
            time.sleep(0.01)
            pass
        '''
        #while self.__stop.isSet():
        self.readlog_line()
        pass

    def stop(self):
        self.__stop.clear()
        pass

    def show_all(self):
        try:
            fp = open(self.__testlog, 'r')
        except IOError:
            return
        fp.seek(os.SEEK_END)
        lenght = fp.tell()
        fp.close()
        if lenght == self.__startpos:
            return 0
        else:
            return 1


    def readlog(self):
        self.pos = self.__startpos
        fp = None
        try:
            fp = open(self.__testlog, 'r')
        except IOError:
            return
        fp.seek(self.__startpos, 0)
        try:
            while True:
                check = fp.read(1024)
                #if not check:
                #    break
                length = len(check)
                self.pos += length
                #if self.__startpos <= self.pos:
                if length == 0:
                    pass
                else:
                    wx.CallAfter(pub.sendMessage, "ShowTestLog", msg=check)
                pass
            self.__startpos = self.pos
        finally:
            fp.close()
        pass

    def readlog_line(self):
        fp = None
        try:
            fp = open(self.__testlog, 'r')
        except IOError:
            return

        try:
            while True:
                line = fp.readline()
                if not line:
                    break
                wx.CallAfter(pub.sendMessage, "ShowTestLog", msg=line)
                time.sleep(0.000001)
        finally:
            fp.close()
            size = "Saved %d bytes to %s." % (os.stat(self.__testlog).st_size, self.__testlog)
            wx.CallAfter(pub.sendMessage, "SendLogSize",data=size)
            #self.__stop.clear()


#open a window to show the selection cell test log
class LogDialog(wx.Frame):
    def __init__(self, title, logname):
        wx.Frame.__init__(self, None, -1, "View Test Log", size=(640, 480))
        self.panel = wx.Panel(self, -1)
        self.SetTitle(title)

        self.__log = logname

        self.log = ShowLog(self.__log)

        pub.subscribe(self.update_log, "ShowTestLog")
        pub.subscribe(self.get_log_size, "SendLogSize")
        self.log.start()

        self.add_menu()
        self.draw_ui()
        self.check_log()

        self.count = 0

        self.Bind(wx.EVT_MENU, self.exit,self.menuFileExit)
        self.Bind(wx.EVT_MENU, self.reload_log, self.menuViewReload)

    def add_menu(self):
        menu = wx.MenuBar()

        self.menuFile = wx.Menu()
        self.menuFileExit = wx.MenuItem(self.menuFile, 100, "Exit")
        self.menuFile.AppendItem(self.menuFileExit)
        menu.Append(self.menuFile, '&File')

        self.menuView = wx.Menu()
        self.menuViewReload = wx.MenuItem(self.menuView, 101, "&Reload\tF5")
        self.menuView.AppendItem(self.menuViewReload)
        menu.Append(self.menuView, '&View')

        self.SetMenuBar(menu)

    def check_log(self):
        ret = os.path.exists(self.__log)
        if ret == False:
            tmp = "Cannot access %s: No such file or directory." % (self.__log)
            self.label.SetLabel(tmp)
        pass

    def draw_ui(self):
        self.box = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(self.panel, -1, "")
        self.logCtrl = wx.TextCtrl(self.panel, -1, size=(100, 100), style=wx.TE_MULTILINE)
        self.logCtrl.SetEditable(False)

        self.box.Add(self.label, 0, wx.EXPAND)
        self.box.Add(self.logCtrl, 2, wx.EXPAND)

        self.panel.SetSizer(self.box)
        self.Show()
        self.Maximize()

    def exit(self, event):
        self.Close()

    def reload_log(self, event):
        self.logCtrl.Clear()
        self.log = ShowLog(self.__log)
        self.log.start()

    def get_log_size(self, data):
        size = data.data
        self.label.SetLabel(size)

    def update_log(self, msg):
        buff = msg.data
        self.count += 1
        try:
            self.logCtrl.AppendText(buff)
        except:
            #self.log.AppendText(buff)
            #print self.count, chardet.detect(buff)
            tmp = buff.decode("utf-8", 'ignore')
            self.logCtrl.AppendText(tmp)




class UpdateProcessMsg(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.__stop = threading.Event()
        self.__stop.set()


    def run(self):
        while self.__stop.isSet():
            time.sleep(0.01)
            if not msgQueue.empty():
                data = msgQueue.get()
                wx.CallAfter(pub.sendMessage,"process_log",msg=data[0],unitName=data[1])


    def stop(self):
        self.__stop.clear()
        pass



class UpdateProcessStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.__stop = threading.Event()
        self.__stop.set()


    def run(self):
        while self.__stop.isSet():
            time.sleep(0.01)
            if not StatusQueue.empty():
                data = StatusQueue.get()
                wx.CallAfter(pub.sendMessage,data["name"],data=data["data"],unitid=data["unitid"])

    def stop(self):
        self.__stop.clear()
        pass




class UpdateWindow(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.__stop = threading.Event()
        self.__stop.set()

    def run(self):
        while self.__stop.isSet():

            time.sleep(1)
            try:
                db = mydb.fetchall()
            except:
                #buff = "%s\n" % traceback.format_exc()
                buff = "%s\n" % (traceback.format_exc())
                write_log(LOG, 'a', buff)

            wx.CallAfter(pub.sendMessage, "UpdateCells", data=db)
        pass
        print("\33[32mComplete to test.\33[0m")
        write_log(LOG, 'a', "Complete to test.\n")

    def stop(self):
        self.__stop.clear()
        pass
    pass


class MainWindow(wx.App):
    def __init__(self):
        wx.App.__init__(self)
        title = "Wistron Test App {}".format(VERSION)
        self.__frame = wx.Frame(parent=None,
                                title=title)
        self.__panel = wx.Panel(self.__frame, -1)
        self.__frame.Maximize() # show max window
        self.__frame.SetMinSize((800, 600))

        global CELLS_STATUS
        global LOG
        global CELLS_START_STATUS
        global LOCK
        Test = 0

        curr_time = "%s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp = "\n\n\n\n\n" + \
              "-" * 72 + \
              "\nStart Time: %s\n\n" % curr_time
        write_log(LOG, 'a', tmp)

        self.global_variable()

        # initialize global variable
        self.init_logViewer()
        self.draw_ui()
        self.init_global_variable()
        self.define_left_menu()

        #main dialog close event
        self.__frame.Bind(wx.EVT_CLOSE, self.OnClose)


        self.__frame.Bind(wx.EVT_MENU, self.file_exit, self.__menu_file_exit)
        self.__frame.Bind(wx.EVT_MENU, self.help, self.__menu_help_about)

        self.__frame.Bind(wx.EVT_BUTTON, self.start_button, self.__start_button)

        self.__frame.Bind(wx.EVT_TEXT_ENTER, self.enter_info, self.__input_line) # input info event

        # update all cells
        pub.subscribe(self.update_win, "UpdateCells")
        pub.subscribe(self.unit_run_error, "UnitRunError")
        pub.subscribe(self.receive_process_log, "process_log")
        pub.subscribe(self.update_cells_status, "CELLS_STATUS")
        pub.subscribe(self.show_main_msg,"TCTRL_SHOW_MSG")



    def init_logViewer(self):
        self.unitLogView_dict={}
        for i in range(self.__unitCount):
            self.unitLogView_dict.update({"unit%s"%(i+1):logView(self.__frame,"unit%s"%(i+1))})




    def __del__(self):
        if self.__update_win.isAlive():
            self.__update_win.stop()
            self.__update_win.join()
        print("Exit APP.")
        pass

    def global_variable(self):
        self.__resw, self.__resh = wx.DisplaySize()

        self.count = 0

        if self.__resw<1024 or self.__resh<768:
            self.__resw = 1024
            self.__resh = 768

        self.__lineCells = 8
        self.__unitCount = 8
        self.__unitCells = 4
        self.__nextStep = 0

        #define Enter item status.
        self.curEnterStep = 0
        self.__inputStatus = 1000
        self.__inputSNStatus = 1001
        self.__inputMacStatus1 = 1002
        self.__inputMacStatus2 = 1003
        self.__inputTypeStatus = 1004
        self.__inputOperatorID = 1005
        self.__inputTestTimeStatus = 1006
        self.__pressEnterStatus = 1007
        self.__inputCyberSwitchIPStatus = 1008

        self.__startButtonStatus = 1999

        self.curRow = -1
        self.curCol = -1

        # create a thread to update cells
        self.__update_win = UpdateWindow()
        self.__update_win.setDaemon(True)
        self.__update_win.start()
        #print "\33[31mUpdate\33[0m"

        self.__update_processMsg = UpdateProcessMsg()
        self.__update_processMsg.setDaemon(True)
        self.__update_processMsg.start()


        self.__update_processStatus = UpdateProcessStatus()
        self.__update_processStatus.setDaemon(True)
        self.__update_processStatus.start()

        pass

    def define_left_menu(self):
        self.MENU_CELL_ID = 999
        self.MENU_START_ID = 1000
        self.MENU_VIEW_ID = 1001
        self.MENU_CLEAN_ID = 1002
        self.MENU_DEBUG_ID = 1003
        self.MENU_ABORT_ID = 1004

        self.__left_menu = wx.Menu()

        # right menu ID
        self.menu_cell =  "Cell options"
        self.menu_start = "Start Unit Test"
        self.menu_view = "View"
        self.menu_clean = "Clean"
        self.menu_debug = "Debug"
        self.menu_Abort = "Abort"


        self.__left_menu.Append(self.MENU_CELL_ID, self.menu_cell)
        self.__left_menu.AppendSeparator()
        start = self.__left_menu.Append(self.MENU_START_ID, self.menu_start)
        view = self.__left_menu.Append(self.MENU_VIEW_ID, self.menu_view)
        self.__left_menu.AppendSeparator()
        clean = self.__left_menu.Append(self.MENU_CLEAN_ID, self.menu_clean)
        self.__left_menu.AppendSeparator()
        debug = self.__left_menu.Append(self.MENU_DEBUG_ID, self.menu_debug)
        self.__left_menu.AppendSeparator()
        abort = self.__left_menu.Append(self.MENU_ABORT_ID, self.menu_Abort)

        '''
        self.__left_menu.Append(wx.MenuItem(id=self.MENU_CELL_ID,text=self.menu_cell))
        self.__left_menu.AppendSeparator()
        start = self.__left_menu.Append(wx.MenuItem(id=self.MENU_START_ID, text=self.menu_start))
        view = self.__left_menu.Append(wx.MenuItem(id=self.MENU_VIEW_ID, text=self.menu_view))
        self.__left_menu.AppendSeparator()
        clean = self.__left_menu.Append(wx.MenuItem(id=self.MENU_CLEAN_ID, text=self.menu_clean))
        self.__left_menu.AppendSeparator()
        debug = self.__left_menu.Append(wx.MenuItem(id=self.MENU_DEBUG_ID, text=self.menu_debug))
        self.__left_menu.AppendSeparator()
        abort = self.__left_menu.Append(wx.MenuItem(id=self.MENU_ABORT_ID, text=self.menu_Abort))
        '''


        #define menu event
        self.__frame.Bind(wx.EVT_MENU, self.left_menu_start, start)
        self.__frame.Bind(wx.EVT_MENU, self.left_menu_view, view)
        self.__frame.Bind(wx.EVT_MENU, self.left_menu_clean, clean)
        self.__frame.Bind(wx.EVT_MENU, self.left_menu_debug, debug)
        self.__frame.Bind(wx.EVT_MENU, self.left_menu_abort, abort)
        pass

    def init_global_variable(self):
        i = 0
        global CELLS_STATUS
        CELLS_STATUS = [] # empty list
        for i in range(self.__unitCount):
            item = UnitInfo()
            CELLS_STATUS.append(item)
            pass
        pass

    def test_unit_array(self):
        print("\33[32;1mEvery Unit initialization value:")
        print("Test Start Time: ", CELLS_STATUS[0]._UnitInfo__startTime, "\33[0m")
        pass

    def draw_ui(self):
        self.__menu = wx.MenuBar()
        self.__menu_file = wx.Menu()
        self.__menu_file_exit = wx.MenuItem(self.__menu_file, 1, "&Quit\tCtrl+Q")
        self.__menu_file.AppendSeparator()

        if sys.version[:1] == '2':
            self.__menu_file.AppendItem(self.__menu_file_exit)
        else:
            self.__menu_file.Append(self.__menu_file_exit)


        #self.__menu_file_spe = wx.MenuItem(self.__menu_file, 2, "")
        self.__menu.Append(self.__menu_file, "&File")

        self.__menu_help = wx.Menu()
        self.__menu_help_about = wx.MenuItem(self.__menu_help, 10, "&About\tF1")

        if sys.version[:1] == '2':
            self.__menu_help.AppendItem(self.__menu_help_about)
        else:
            self.__menu_help.Append(self.__menu_help_about)

        self.__menu.Append(self.__menu_help, "&Help")

        self.__frame.SetMenuBar(self.__menu)

        # show message text control
        self.__show_msg = wx.TextCtrl(self.__panel, -1, size=(30, 120), style=wx.TE_MULTILINE)
        self.__show_msg.SetEditable(False)
        self.__show_msg_box = wx.BoxSizer(wx.HORIZONTAL)    #level extend
        self.__show_msg_box.Add(self.__show_msg, proportion=1, flag=wx.RIGHT)

        # for enter info
        self.__enterLineWidth = 40
        string = ""
        self.__label = wx.StaticText(self.__panel, -1, string, size=(-1, self.__enterLineWidth), style=wx.ALIGN_CENTER | wx.TEXT_ALIGNMENT_CENTER)
        label_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.__label.SetFont(label_font)
        w, h = self.__label.GetTextExtent(string)
        self.__label.SetSize(wx.Size(w, self.__enterLineWidth))

        #self.__input_line = wx.TextCtrl(self.__panel, 200, size=(30, self.__enterLineWidth), style=wx.TE_LINEWRAP | wx.PROCESS_ENTER)
        self.__input_line = wx.TextCtrl(self.__panel, 200, size=(30, self.__enterLineWidth), style=wx.TE_PROCESS_ENTER)
        line_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.__input_line.SetFont(line_font)
        self.__input_line.Hide()

        self.__start_button = wx.Button(self.__panel, 100, "Start", size=(152, self.__enterLineWidth))
        start_font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.__start_button.SetFont(start_font)
        self.__start_button.Hide()

        self.__box_input = wx.BoxSizer(wx.HORIZONTAL)
        self.__box_input.Add(self.__label, proportion=0, flag=wx.RIGHT | wx.CENTER, border=10)
        self.__box_input.Add(self.__input_line, proportion=2, flag=wx.RIGHT)
        self.__box_input.Add(self.__start_button, proportion=0, flag=wx.RIGHT, border=5)

        self.__cells = wx.grid.Grid(self.__panel) #create grid
        self.__cells.CreateGrid(self.__unitCount/2, 8)
        self.init_cells_table()

        self.__main_box = wx.BoxSizer(wx.VERTICAL)
        #self.__main_box.AddSizer(self.__show_msg_box, flag=wx.EXPAND)
        #self.__main_box.AddSizer(self.__box_input, flag=wx.EXPAND)
        self.__main_box.Add(self.__show_msg_box, flag=wx.EXPAND)
        self.__main_box.Add(self.__box_input, flag=wx.EXPAND)
        self.__main_box.Add(self.__cells, proportion=2, flag=wx.EXPAND|wx.ALL, border=3)
        #'''

        self.__frame.SetPosition(wx.Point(0,0))
        self.__panel.SetSizer(self.__main_box)
        self.__frame.Show()

    #'''
    def init_cells_table(self):
        self.__cells.EnableDragGridSize(enable=False)
        self.__cells.EnableEditing(False)
        self.__cells.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        #self.__cells.SetSelectionBackground(wx.Colour(0, 128, 255))
        #self.__cells.SetSelectionForeground(wx.Colour(0, 128, 255))
        self.__cells.SetColLabelSize(1)
        self.__cells.SetRowLabelSize(1)
        self.__cells.SetMargins(10,10)
        self.__cells.EnableGridLines(True)
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(12)
        self.__cells.SetDefaultCellFont(font)

        '''
        i = 0
        for i in range(self.__unitCount):
            row = int(math.floor(i/2.0))
            #self.__cells.SetRowSize(i, 150)
            self.__cells.SetRowSize(row, 150)
            j = 0
            for j in range(self.__lineCells):
                width = math.ceil(self.__resw/self.__lineCells)
                if width < 150:
                    width = 150
                self.__cells.SetColSize(j, width)
                cellNum = i*self.__lineCells+j+1
                unitID = int(math.ceil(cellNum/4.0))
        '''

        self.set_cells_size()
        self.set_cells_default()
        self.__cells.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.left_menu)
        self.__cells.GetGridWindow().Bind(wx.EVT_MOTION, self.onMouseOver)


    def onMouseOver(self,event):

        x, y = self.__cells.CalcUnscrolledPosition(event.GetX(),event.GetY())
        coords = self.__cells.XYToCell(x, y)
        col = coords[1]
        row = coords[0]

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))

        unit_data  = mydb.fetchall("unit")[unit]
        msg = "ip: %s\nloc: %s" % (unit_data[2],unit_data[3])


        if wx.version().find("phoenix") != -1:
            if (cell-1)%4 == 0:
                event.GetEventObject().SetToolTip(None)
                wx.YieldIfNeeded()
                event.GetEventObject().SetToolTip(msg)
            else:
                event.GetEventObject().SetToolTip('')

        else:

            self.eventObj = event.GetEventObject()

            if (cell-1)%4 == 0:
                event.GetEventObject().SetToolTip(None)
                timer1 = Timer(0.04,self.set_Tool_tip,[msg])
                timer1.start()
            else:
                event.GetEventObject().SetToolTip(None)


    def set_Tool_tip(self,msg):
        self.eventObj.SetToolTipString(msg)


    def set_cells_size(self):
        for i in range(int(self.__unitCount/2)):
            self.__cells.SetRowSize(i, 150)

        for j in range(self.__lineCells):
            width = math.ceil(self.__resw/self.__lineCells)
            if width < 150:
                width = 150
            self.__cells.SetColSize(j, width)



    def set_cells_default(self,unit=-1):
        for i in range(self.__unitCount):
            if not unit == -1:
                if not i == unit-1:
                    continue

            row = int(math.floor(i/2.0))
            for j in range(1,self.__unitCells+1):
                col = (i*self.__unitCells+j-1)%self.__lineCells

                ## set default cell color and text ##
                if j == 1:
                    self.__cells.SetCellBackgroundColour(row, col, "#FFFFFF")
                    self.__cells.SetCellValue(row, col,"Unit %d"%(i+1))
                else:
                    self.__cells.SetCellBackgroundColour(row, col, "#F0F0F0")
                    self.__cells.SetCellValue(row, col, "")


    # check input ip format
    def check_ip(self, ip):
        port = ip.strip().split(':')
        if len(port) != 2:
            print("Inputting port error, Please check.")
            return 1
        #cyberPort = int(port[1])

        try:
            port[1]=int(port[1])
        except:
            print("Port must be number.")
            return 2

        if port[1]<1 or port[1]>8:
            print("Port must be in [1, 8].")
            return 3

        addr=port[0].strip().split('.')
        if len(addr) != 4:
            print("IP Address is error, Please check.")
            return 4

        for i in range(4):
            try:
                addr[i] = int(addr[i]) # every para must be number, or check failed.
            except:
                print("IP Address must be number.")
                return 5
            if addr[i]<=255 and addr[i]>=0:
                pass
            else:
                print("IP Address must be in 0~255.")
                return 6
        return 0

    def OnClose(self, event):
        wx.MessageBox("If you want close window, please use Quit which is in File menu or Ctrl+Q to exit.", "waring", wx.OK|wx.ICON_WARNING)
        pass

    def file_exit(self, event):
        #print "Success to exit."
        if self.__update_win.isAlive():
            self.__update_win.stop()
            self.__update_win.join()
        wx.Exit()

    def help(self, event):
        #self.test_unit_array()
        #self.__update_win.stop()
        #mydb.update(1, '', '', 1)
        #self.__show_msg.Clear()
        self.__show_msg.AppendText(VERSION)
        pass


    def receive_process_log(self,msg,unitName):
        self.unitLogView_dict[unitName].addLog(msg)



    def update_cells_status(self,data,unitid):
        for index,value in data.items():
            if hasattr(CELLS_STATUS[unitid-1],index):
                setattr(CELLS_STATUS[unitid-1],index,value)



    def show_main_msg(self,data,unitid):
        self.__show_msg.AppendText(data)



    def unit_run_error(self, msg):
        data = msg.data
        print(data)





    def update_win(self, data):
        buff = data

        for i in range(self.__unitCount):
            row = int(math.floor(i/2.0))

            '''
            j = 1
            if CELLS_START_STATUS.has_key(i*4+j):
                print("unit %d test failed." % (i + 1))
            '''

            j=1
            if buff[i*4+j][4] > 0:
                cellText = "Unit %d\n%s\n%s" % (i+1,buff[i*4+j][1], buff[i*4+j][2])
                self.__cells.SetCellValue(row,(i*4+j-1)%8, cellText)


            if CELLS_STATUS[i]._UnitInfo__testStatus == 0:
                continue


            #if CELLS_STATUS[i]._UnitInfo__startStatus == 0:
            #    continue


            for j in range(2, 4):
                col = (i*4+j-1)%8

                if buff[i*4+j][4] == 0:
                    continue

                cellText = "%s\n%s" % (buff[i*4+j][1], buff[i*4+j][2])
                self.__cells.SetCellValue(row, col, cellText)


                if j == 3:
                    if buff[i*4+j][4] == 1:
                        self.__cells.SetCellBackgroundColour(row, col, "#FFFF00")

                    elif buff[i*4+j][4] == 2:
                        self.__cells.SetCellBackgroundColour(row, col, "#00FF00")

                    elif buff[i*4+j][4] == 3:
                        self.__cells.SetCellBackgroundColour(row, col, "#FF0000")

                    elif buff[i*4+j][4] == 4:
                        self.__cells.SetCellBackgroundColour(row, col, "#FF0000")
                pass
            pass


            j=4
            if buff[i*4+j][4] > 0:
                self.__cells.SetCellValue(row,(i*4+j-1)%8, buff[i*4+j][1])
                self.__cells.SetCellFont(row,(i*4+j-1)%8, wx.Font(30, wx.ROMAN, wx.ITALIC, wx.NORMAL))
                #self.__cells.SetCellTextColour(row, (i*4+j-1)%8,wx.BLUE)

        #self.__update_win.stop()
        pass

    def start_button(self, event):
        print("start_button")

        #print(event.Id)
        #print("###########")
        #print(aa)
        cell = self.curRow * self.__lineCells + self.curCol + 1     # Cell number
        unit = int(math.ceil(cell/4.0))
        unitStartCell = int(math.floor((cell-1)/4.0))*4

        label = "Unit %d - Cell %d" % (unit, cell)

        #print unitStartCell, label

        tmp = "%sStart Time: %s\n" % (self.__label.GetLabelText(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.__show_msg.AppendText(tmp)

        self.__label.SetLabel('')
        self.__start_button.Hide()
        self.__nextStep = self.__inputSNStatus
        self.curEnterStep = 0

        CELLS_STATUS[unit-1]._UnitInfo__startStatus = 1
        CELLS_STATUS[unit-1]._UnitInfo__inputStatus = 0

        #CELLS_STATUS[unit-1]._UnitInfo__process = Process(target=call_run, args=((unit-1)*4+1, CELLS_STATUS[unit-1]._UnitInfo__SerialNumber, CELLS_STATUS[unit-1]._UnitInfo__cyberSwitchIP,msgQueue))
        
        CELLS_STATUS[unit-1]._UnitInfo__process = Process(target=call_run, args=((unit-1)*4+1, CELLS_STATUS[unit-1]._UnitInfo__SerialNumber,msgQueue))


        CELLS_STATUS[unit-1]._UnitInfo__process.start()
        #CELLS_STATUS[unit-1]._UnitInfo__process.join()

        CELLS_STATUS[unit-1]._UnitInfo__processID = CELLS_STATUS[unit-1]._UnitInfo__process.pid
        CELLS_STATUS[unit-1]._UnitInfo__testStatus = 1
        event.Skip()
        pass

    def enter_info(self, event):
        row = self.curRow
        col = self.curCol

        if row<0 or col<0:
            event.Skip()

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))
        tmp = ""
        buff = ""
        ret = 0

        buff = self.__input_line.GetValue()
        ret = len(buff)
        if self.__nextStep == self.__inputSNStatus:
            #print "%d - [%s]" % (ret, buff)
            if ret<=0:
                buff = "Serial Number is empty."
                wx.MessageBox(buff, "Waring", wx.ICON_WARNING | wx.OK)
                return
            CELLS_STATUS[unit-1]._UnitInfo__SerialNumber = buff

            tmp = "%s%s\n" % (self.__label.GetLabelText(), self.__input_line.GetValue())
            #self.__nextStep = self.__inputCyberSwitchIPStatus
            self.__nextStep = self.__startButtonStatus
            #self.__nextStep = self.__inputMacStatus1
            pass

        elif self.__inputMacStatus1 == self.__nextStep:
            print("\33[31m%d - [%s]\33[0m" % (ret, buff))
            if ret<=0:
                buff = "MAC is empty."
                wx.MessageBox(buff, "Waring", wx.ICON_WARNING | wx.OK)
                return
            CELLS_STATUS[unit-1]._UnitInfo__MAC1 = buff

            tmp = "%s%s\n" % (self.__label.GetLabelText(), self.__input_line.GetValue())
            #self.__nextStep = self.__inputCyberSwitchIPStatus
            #self.__nextStep = self.__startButtonStatus
            self.__nextStep = self.__inputMacStatus2
            #self.__nextStep = self.__inputTypeStatus
            pass


        elif self.__inputMacStatus2 == self.__nextStep:
            print("\33[31m%d - [%s]\33[0m" % (ret, buff))
            if ret<=0:
                buff = "MAC is empty."
                wx.MessageBox(buff, "Waring", wx.ICON_WARNING | wx.OK)
                return
            CELLS_STATUS[unit-1]._UnitInfo__MAC2 = buff

            tmp = "%s%s\n" % (self.__label.GetLabelText(), self.__input_line.GetValue())
            #self.__nextStep = self.__inputCyberSwitchIPStatus
            self.__nextStep = self.__startButtonStatus
            #self.__nextStep = self.__inputTypeStatus


        elif self.__inputTypeStatus == self.__nextStep:
            if ret<=0:
                buff = "Type is empty."
                wx.MessageBox(buff, "Waring", wx.ICON_WARNING | wx.OK)
                return
            if buff != "1" and buff != "2":
                wx.MessageBox("Model type should be 1 or 2.", "Waring", wx.ICON_WARNING | wx.OK)
                self.__input_line.Clear()
                return
            CELLS_STATUS[unit-1]._UnitInfo__type = buff
            tmp = "%s%s\n" % (self.__label.GetLabelText(), self.__input_line.GetValue())

            #self.__nextStep = self.__inputCyberSwitchIPStatus
            self.__nextStep = self.__startButtonStatus
            #self.__nextStep = self.__inputMacStatus
            #self.__nextStep = self.__inputTypeStatus
            pass

        elif self.__inputCyberSwitchIPStatus == self.__nextStep:
            if ret<=0:
                buff = "Cyber switch IP and port is empty."
                wx.MessageBox(buff, "Waring", wx.ICON_WARNING | wx.OK)
                return

            waring = ""
            ret = self.check_ip(buff)
            if ret == 0: # correct
                CELLS_STATUS[unit-1]._UnitInfo__cyberSwitchIP = buff
                #self.__nextStep = self.__inputCyberSwitchIPStatus
                self.__nextStep = self.__startButtonStatus
                #self.__nextStep = self.__inputMacStatus
                #self.__nextStep = self.__inputTypeStatus
                tmp = "%s%s\n" % (self.__label.GetLabelText(), self.__input_line.GetValue())
                pass
            elif ret == 1:
                waring = "Cyber Switch IP format: *.*.*.*:port"
                pass
            elif ret == 2:
                waring = "Warning", "Cyber Switch IP format: *.*.*.*:port, port must be number."
                pass
            elif ret == 3:
                waring = "Cyber Switch IP format: *.*.*.*:port, port must be in [1, 8]."
                pass
            elif ret == 4:
                waring = "Cyber Switch IP format: *.*.*.*:port"
                pass
            elif ret == 5:
                waring = "Cyber Switch format: *.*.*.*:port, and every * must be number."
                pass
            elif ret == 6:
                waring = "Cyber Switch format: *.*.*.*:port, and every * must be number."
                pass

            if ret != 0:
                wx.MessageBox(waring, "Waring", wx.ICON_WARNING | wx.OK)
                self.__input_line.Clear()
                return
            pass

        # append inputting info to log
        self.__show_msg.AppendText(tmp)

        self.__input_line.Clear()
        self.curEnterStep += 1

        # set input lable text
        tmp = ""
        if self.__inputMacStatus1 == self.__nextStep:
            tmp = "Unit %d: Enter ROM MAC --> " % unit
            pass
 
        elif self.__inputMacStatus2 == self.__nextStep:
            tmp = "Unit %d: Enter BMC MAC --> " % unit
            pass

        elif self.__nextStep == self.__inputTypeStatus:
            tmp = "Unit %d: Enter Model Type(1 or 2) --> " % unit
            self.__input_line.SetMaxLength(1)
            pass
        elif self.__startButtonStatus == self.__nextStep:
            tmp = "Unit %d: Press Enter key to start --> " % unit
            print(tmp)
            pass
        elif self.__nextStep == self.__inputCyberSwitchIPStatus:
            tmp = "Unit %d: Enter Cyber Switch IP and port --> " % unit
            pass

        self.__label.SetLabel(tmp)
        w, h = self.__label.GetTextExtent(tmp)
        linepos = self.__input_line.GetPosition()
        self.__label.SetSize(wx.Size(w, h))

        if self.__startButtonStatus != self.__nextStep:
            self.__input_line.SetPosition(wx.Point(w+1, linepos.y))
            linesize = self.__input_line.GetSize()
            linesize[0] = linesize[0]-(w+1-linepos[0])
            self.__input_line.SetSize(linesize)
            pass
        else:
            self.__input_line.Hide()
            self.__start_button.SetPosition(wx.Point(w+1, linepos.y))
            self.__start_button.Show()
            self.__start_button.SetFocus()
            self.update_UnitInputInfo()
            pass

        #event.Skip()
        pass



    @property
    def curUnitID(self):
        return (self.curUnit-1)*4+1


    @property
    def curUnit(self):
        cellID = self.curRow * self.__lineCells + self.curCol + 1
        unit = int(math.ceil(cellID/4.0))
        return unit



    def update_UnitInputInfo(self):

        #unitInput = 'SN:%s\nIP:%s' %(CELLS_STATUS[self.curUnit-1]._UnitInfo__SerialNumber,
        #                            CELLS_STATUS[self.curUnit-1]._UnitInfo__cyberSwitchIP)
        unitInput = 'SN: %s' %(CELLS_STATUS[self.curUnit-1]._UnitInfo__SerialNumber)

        mydb.update(self.curUnitID,unitInput, '', 1)



    def left_menu(self, event):
        #pos = event.GetPosition()
        #pos = self.__panel.ScreenToClient(pos)
        row = event.GetRow()
        col = event.GetCol()
        #print row, col

        if self.__nextStep == self.__startButtonStatus:
            return

        self.curRow = row
        self.curCol = col

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))

        label = "Unit %d - Cell %d" % (unit, cell)
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)


        ctrl = self.__left_menu.FindItemById(self.MENU_CELL_ID)
        if wx.version().find("4.1.0") != -1:
            ctrl.SetItemLabel(label)
            ctrl.SetFont(font)
        else:
            ctrl.SetText(label)
            ctrl.SetFont(font)

        self.__panel.PopupMenu(self.__left_menu)
        event.Skip()
        pass

    def left_menu_start(self, event):

        row = self.curRow
        col = self.curCol

        if row<0 or col<0:
            event.Skip()

        cell = row * self.__lineCells + col + 1     # Cell number
        unit = int(math.ceil(cell/4.0))
        unitStartCell = int(math.floor((cell-1)/4.0))*4

        label = "Unit %d - Cell %d" % (unit, cell)

        #print unitStartCell, label
        #print(vars(CELLS_STATUS[unit-1]))

        #allow unit to start test or not


        if not CELLS_STATUS[unit-1]._UnitInfo__testStatus == 0:
            if CELLS_STATUS[unit-1]._UnitInfo__startStatus == 0:
                wx.MessageBox("Please clean unit%s first."%(unit), "waring", wx.OK|wx.ICON_WARNING)

            return

        #if CELLS_STATUS[unit-1]._UnitInfo__startStatus == 1:
        #    return

        #Is current in enter info?
        if self.curEnterStep != 0:
            return

        CELLS_STATUS[unit-1]._UnitInfo__inputStatus = 1  # if unit is in enter status, don't update this unit.

        dbdata = mydb.fetchall()
        try:
            text = "Unit %d: Enter Serial Number(SN) --> " % (unit)
            self.__label.SetLabel(text)
            w, h = self.__label.GetTextExtent(text)
            self.__label.SetSize(wx.Size(w, h))
            labelCtrlPos = self.__label.GetPosition()
            self.__input_line.Show()
            self.__input_line.SetFocus()
            self.__input_line.SetPosition(wx.Point(w+1, labelCtrlPos.y))
            self.__input_line.SetSize(wx.Size(self.__resw - w - 1, -1))
            self.__input_line.SetMaxLength(30)
            self.curEnterStep += 1
            self.__nextStep = self.__inputSNStatus
            pass
        except IndexError as ex:
            pass

        event.Skip()
        pass

    def left_menu_view(self, event):
        row = self.curRow
        col = self.curCol

        if row<0 or col<0:
            event.Skip()

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))

        unit_data  = mydb.fetchall("unit")[unit]

        cur_unitLogView=self.unitLogView_dict["unit%s"%(unit)]
        cur_unitLogView.setInfo(*unit_data[1:-1])
        cur_unitLogView.ShowModal()



        #self.unitLogView_dict["unit%s"%(unit)].addLog("123456895685986958")

        '''
        label = "Wistron Run-in: View Unit %d - Cell %d test log" % (unit, cell)
        val = cell % 4
        logname = ""
        if val == 1:
            logname = "linux.txt"
        elif val == 2:
            logname = "bmc.txt"
        elif val == 3:
            logname = "host.txt"
        else:
            logname = "power.txt"

        logpath = "%s/log/%d/%s" % (os.path.dirname(os.path.abspath(__file__)) , cell, logname)
        #print "LogPath:", logpath
        LogDialog(label, logpath)
        #self.__input_line.SetLabel(label)

        #print row, col, label

        event.Skip()
        pass
        '''

    def left_menu_clean(self, event):
        row = self.curRow
        col = self.curCol

        if row<0 or col<0:
            event.Skip()

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))

        label = "Unit %d - Cell %d" % (unit, cell)



        #print row, col, label
        try:
            if CELLS_STATUS[unit-1]._UnitInfo__testStatus != 0:
                data = mydb.fetchall()
                #if data[(unit-1)*4+1][4]==1 and data[(unit-1)*4+2][4]==1 and data[(unit-1)*4+3][4]==1 or CELLS_STATUS[unit-1]._UnitInfo__processI <= 0:
                if CELLS_STATUS[unit-1]._UnitInfo__startStatus == 1:
                #if data[(unit-1)*4+1][4]==1 and data[(unit-1)*4+2][4]==1 and data[(unit-1)*4+3][4]==1:
                    wx.MessageBox("Your choice cell is testing.\nPlease abort it if you want to clean.", "waring", wx.OK|wx.ICON_WARNING)
                    return
                    pass

            tmp = "Clear unit %d...\n" % (unit)
            write_log(LOG, 'a', tmp)
            mydb.update((unit-1)*4+1, '', '', 0)
            mydb.update((unit-1)*4+2, '', '', 0)
            mydb.update((unit-1)*4+3, '', '', 0)
            mydb.update((unit-1)*4+4, '', '', 0)
            CELLS_STATUS[unit-1]._UnitInfo__startStatus = 0
            CELLS_STATUS[unit-1]._UnitInfo__testStatus = 0

            mydb.unit_update(unit,"","","")

            self.unitLogView_dict["unit%s"%(self.curUnit)].clearLog()
            self.set_cells_default(unit)

            pass
        except:
            tmp = "%s\n" % traceback.format_exc()
            write_log(LOG, 'a', tmp)
            pass

        event.Skip()
        pass

    def left_menu_debug(self, event):
        row = self.curRow
        col = self.curCol

        if row<0 or col<0:
            event.Skip()

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))

        label = "Unit %d - Cell %d" % (unit, cell)

        print(row, col, label)

        event.Skip()
        pass

    def left_menu_abort(self, event):
        row = self.curRow
        col = self.curCol

        if row<0 or col<0:
            event.Skip()

        cell = row * self.__lineCells + col + 1
        unit = int(math.ceil(cell/4.0))

        label = "Unit %d - Cell %d" % (unit, cell)

        #print row, col, label

        CELLS_STATUS[unit-1]._UnitInfo__startStatus = 0
        #CELLS_STATUS[unit-1]._UnitInfo__testStatus = 0
        if CELLS_STATUS[unit-1]._UnitInfo__processID > 0:
            os.kill(CELLS_STATUS[unit-1]._UnitInfo__processID, signal.SIGKILL)
            CELLS_STATUS[unit-1]._UnitInfo__processID = 0


        mydb.update(self.curUnitID+3,"ABORT","",1)

        event.Skip()
        pass



if __name__ == '__main__':
    app = MainWindow()
    app.MainLoop()
