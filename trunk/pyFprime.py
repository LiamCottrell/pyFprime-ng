#!/usr/bin/env python

import wx

import fprime
import Element

modules ={u'PickElement': [0, '', u'PickElement.py'],
 u'fprime': [1, 'Main frame of Application', u'fprime.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = fprime.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        self.main.OnFPRIMENewMenu(None)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
