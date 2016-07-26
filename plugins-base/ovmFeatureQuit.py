#!/usr/bin/env python
#-*-coding:utf-8-*-
from ovmConsoleStandard import *

class ovmFeatureQuit:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Quit"))
    
        inPane.AddWrappedTextField(Lang(
            "Press <Enter> to quit this console."))

    @classmethod
    def ActivateHandler(cls):
        Layout.Inst().ExitBannerSet(Lang("Quitting..."))
        Layout.Inst().ExitCommandSet('') # 退出
        
    def Register(self):
        # 防止从initab或者mingetty加-f命令退出
        if not '-f' in sys.argv:
            Importer.RegisterNamedPlugIn(
                self,
                'Quit', # 界面显示的名称
                {
                    'menuname' : 'MENU_ROOT',
                    'menupriority' : 10000,
                    'menutext' : Lang('Quit'),
                    'statusupdatehandler' : ovmFeatureQuit.StatusUpdateHandler,
                    'activatehandler' : ovmFeatureQuit.ActivateHandler
                }
            )

# 通过import的方式调用register方法将选项加入到menu中
ovmFeatureQuit().Register()
