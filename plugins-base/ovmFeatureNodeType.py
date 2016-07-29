#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *

class ovmFeatureNodeType:
    '''展示系统信息'''
    def StatusUpdateHandlerSYSTEM(cls, inPane):
        inPane.AddTitleField(Lang('System Info'))
        inPane.AddWrappedTextField(Lang('Press <Enter> to log out'))
        inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})       
    def StatusUpdateHandlerPROCESSOR(cls, inPane):
        inPane.AddTitleField(Lang('System Info'))
        inPane.AddWrappedTextField(Lang('Press <Enter> to log out'))
        inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})       


    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'ENABLEDISABLE_KVM', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Enable/disable Kvm'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NODETYPE',
                'menupriority' : 100,
                'menutext' : Lang('Enable/disable Kvm') ,
                'statusupdatehandler' : self.StatusUpdateHandlerSYSTEM
            }
        )

        Importer.RegisterNamedPlugIn(
            self,
            'ENABLEDISABLE_DOCKER', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Enable/disable Docker'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NODETYPE',
                'menupriority' : 200,
                'menutext' : Lang('Enable/disable Docker') ,
                'statusupdatehandler' : self.StatusUpdateHandlerPROCESSOR
            }
        )
            

# Register this plugin when module is imported
ovmFeatureNodeType().Register()