#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *

class ovmFeatureRepertory:
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
            'KVM_REPERTORY', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Set Kvm Repertory'), # Name of this plugin for plugin list
                'menuname' : 'MENU_REPERTORY',
                'menupriority' : 100,
                'menutext' : Lang('Set Kvm Repertory') ,
                'statusupdatehandler' : self.StatusUpdateHandlerSYSTEM
            }
        )

        Importer.RegisterNamedPlugIn(
            self,
            'DOCKER_REPERTORY', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Set Docker Repertory'), # Name of this plugin for plugin list
                'menuname' : 'MENU_REPERTORY',
                'menupriority' : 200,
                'menutext' : Lang('Set Docker Repertory') ,
                'statusupdatehandler' : self.StatusUpdateHandlerPROCESSOR
            }
        )
            
# Register this plugin when module is imported
ovmFeatureRepertory().Register()