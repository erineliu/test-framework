import wx
from wx.lib import sized_controls
import re
import time



class logView(wx.Dialog):
    def __init__(self,parent,title=""):
        wx.Dialog.__init__(self,
                           parent,
                           wx.ID_NEW,
                           title,
                           size=(900,800))

        self.draw_gui()
        self.CenterOnParent()


    def draw_gui(self):


        #self.panel = wx.Panel(self)
        self.info_sizer = wx.GridBagSizer(0,0)
        self.ST_sn_name = wx.StaticText(self, label = "SN : ")
        self.ST_sn_value = wx.StaticText(self, label = "ddd")
        self.ST_ip_name = wx.StaticText(self, label = "IP : ")
        self.ST_ip_value = wx.StaticText(self, label = "")
        self.ST_location_name = wx.StaticText(self, label = "LOC : ")
        self.ST_location_value = wx.StaticText(self, label = "")
        self.ST_testCase_name = wx.StaticText(self, label = "Case : ")
        self.ST_testCase_value = wx.StaticText(self, label = "",size=(400,-1))
        #self.ST_testCase_value = wx.StaticText(self, label = "")


        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(16)

        self.ST_sn_name.SetFont(font)
        self.ST_ip_name.SetFont(font)
        self.ST_location_name.SetFont(font)
        self.ST_sn_value.SetFont(font)
        self.ST_ip_value.SetFont(font)
        self.ST_location_value.SetFont(font)
        self.ST_testCase_value.SetFont(font)
        self.ST_testCase_name.SetFont(font)

        self.ST_sn_name.SetForegroundColour(wx.Colour(0,0,255))
        self.ST_ip_name.SetForegroundColour(wx.Colour(0,0,255))
        self.ST_location_name.SetForegroundColour(wx.Colour(0,0,255))
        self.ST_testCase_name.SetForegroundColour(wx.Colour(0,0,255))

        self.info_sizer.Add(self.ST_sn_name, pos = (0, 0), flag = wx.ALIGN_RIGHT)
        self.info_sizer.Add(self.ST_sn_value, pos = (0, 1), flag = wx.ALIGN_LEFT)
        self.info_sizer.Add(self.ST_ip_name, pos = (1, 0), flag = wx.ALIGN_RIGHT)
        self.info_sizer.Add(self.ST_ip_value, pos = (1, 1), flag = wx.ALIGN_LEFT)
        self.info_sizer.Add(self.ST_location_name, pos = (2, 0), flag = wx.ALIGN_RIGHT)
        self.info_sizer.Add(self.ST_location_value, pos = (2, 1),flag = wx.ALIGN_LEFT)
        self.info_sizer.Add(self.ST_testCase_name, pos = (1, 2),flag = wx.ALIGN_RIGHT)
        self.info_sizer.Add(self.ST_testCase_value, pos = (1, 3),flag = wx.ALIGN_LEFT)
        self.info_sizer.AddGrowableCol(1)
        self.info_sizer.AddGrowableCol(3)
        #self.info_sizer.AddGrowableCol(3,2)



        self.log_group_box = wx.StaticBox(self,
                                            wx.ID_NEW,
                                            "Process Log")
        self.log_sizer = wx.StaticBoxSizer(self.log_group_box,
                                             wx.HORIZONTAL)

        self.logctrl1 = wx.TextCtrl(self,
                                     wx.ID_NEW,
                                     style=wx.TE_MULTILINE| wx.HSCROLL)

        self.logctrl1.SetEditable(False)
        self.logctrl1.SetBackgroundColour((227,251,227))

        self.log_sizer.Add(self.logctrl1, 1, wx.EXPAND | wx.ALL, 2)


        line = wx.StaticLine(self)

        #self.panel.SetSizer(self.info_sizer)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.info_sizer,0, wx.EXPAND | wx.ALL,10)
        main_sizer.Add(line,0, wx.EXPAND | wx.ALL,10)
        main_sizer.Add(self.log_sizer, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(main_sizer)



    def setInfo(self,sn,ip,location):
        self.ST_sn_value.SetLabel(sn)
        self.ST_ip_value.SetLabel(ip)
        self.ST_location_value.SetLabel(location)



    def addLog(self,msg):

        reaesc = re.compile(r'\x1b[^m]*m')
        msg = reaesc.sub('',msg)
        self.catchCaseInfo(msg)
        self.logctrl1.AppendText(msg+"\n")
        self.logctrl1.ShowPosition(self.logctrl1.GetLastPosition())



    def clearLog(self):
        self.logctrl1.SetValue("")
        self.ST_testCase_value.SetLabel("")


    def catchCaseInfo(self,msg):
        output = msg
        if msg.find("Test Case  :") != -1:
            #self.Refresh()
            caseName = output.split(":")[1].strip()
            self.ST_testCase_value.SetLabel(caseName)








if __name__ == '__main__':
    app = wx.App()
    aa =logView(None,"this")

    for i in range(1000):
        aa.addLog(str(i))
    aa.addLog("sdfdfdfdfd")
    #aa.clearLog()
    aa.Show()
    app.MainLoop()





