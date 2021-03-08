import wx

class Rename(wx.Dialog):
    def __init__(self,parent,id,title):
        wx.Dialog.__init__(self,parent,id,title,size=(400,800))

        '''
        self.info_sizer = wx.GridBagSizer(0,0)
        self.ST_sn_name = wx.StaticText(self, label = "SN :")
        self.ST_sn_value = wx.StaticText(self, label = "ddddddddd")
        self.ST_ip_name = wx.StaticText(self, label = "IP :")
        self.ST_ip_value = wx.StaticText(self, label = "")
        self.ST_location_name = wx.StaticText(self, label = "LOC :")
        self.ST_location_value = wx.StaticText(self, label = "")

        self.info_sizer.Add(self.ST_sn_name, pos = (0, 0))
        self.info_sizer.Add(self.ST_sn_value, pos = (0, 3))
        self.info_sizer.Add(self.ST_ip_name, pos = (1, 0))
        self.info_sizer.Add(self.ST_ip_value, pos = (1, 3))
        self.info_sizer.Add(self.ST_location_name, pos = (2, 0))
        self.info_sizer.Add(self.ST_location_value, pos = (2, 3))
        '''



        #panel=wx.Panel(self,-1)

        self.ST_sn_name = wx.StaticText(self, label = "SN :")
        self.ST_sn_value = wx.StaticText(self, label = "sssssss")


        sizer=wx.GridBagSizer(0,0)
        #text=wx.StaticText(self,-1,'RenameTo')
        #text0=wx.StaticText(self,-1,'RenameTo')
        #text2=wx.StaticText(self,-1,'RenameTo')
        #sizer.Add(text,(0,0),flag=wx.TOP|wx.LEFT|wx.BOTTOM,border=5)
        #tc=wx.TextCtrl(self,-1)
        #sizer.Add(tc,(1,0),(1,5),wx.EXPAND|wx.LEFT|wx.RIGHT,5)
        #buttonOk=wx.Button(self,-1,'Ok',size=(90,28))
        #buttonClose=wx.Button(self,-1,'Close',size=(90,28))
        sizer.Add(self.ST_sn_name,(3,0))
        sizer.Add(self.ST_sn_value,(3,3))
        #sizer.Add(text2,(3,4),flag=wx.RIGHT|wx.BOTTOM,border=5)
        sizer.AddGrowableCol(1)
        #sizer.AddGrowableRow(2)


        self.SetSizer(sizer)


        #panel.SetSizerAndFit(sizer)
        #self.Centre()
        self.Show(True)


app=wx.App()
Rename(None,-1,'RenameDialog')
app.MainLoop()
