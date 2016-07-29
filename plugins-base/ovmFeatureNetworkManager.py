#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *

#network info start
class ovmFeatureNetworkInfo:
    '''展示网络信息'''

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'NETWORK_INFO', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Configure Management Interface'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 100,
                'menutext' : Lang('Network Configure') ,
                'needsauth' : True,
                'statusupdatehandler' : None,
                'activatehandler' : None
            }
        )

#network info end

#NDS info start
class ovmFeatureDNS:
    '''展示DNS信息'''

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'DNS', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Display DNS Servers'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 101,
                'menutext' : Lang('Display DNS Servers') ,
                'statusupdatehandler' : None
            }
        )

#NDS info end


# test network start
class ovmFeatureTestNetwork:
    '''测试网络'''

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'TEST_NETWORK', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Test Network'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 102,
                'menutext' : Lang('Test Network') ,
                'statusupdatehandler' : None,
                'activatehandler' : None
            }
        )

#test network  end

#set NTP start
class ovmFeatureNTP:
    '''展示网络信息'''

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'NTP', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Network Time (NTP)'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 103,
                'menutext' : Lang('Network Time (NTP)') ,
                'statusupdatehandler' : None,
                'activatehandler' : None
            }
        )

#set NTP end

#NICs info start
class ovmFeatureDisplayNICs:
    '''展示网络信息'''

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'DISPLAY_NICS', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Display NICs'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 104,
                'menutext' : Lang('Display NICs') ,
                'statusupdatehandler' : None,
                'activatehandler' : None
            }
        )

#NICs info end


# Register this plugin when module is imported
ovmFeatureNetworkInfo().Register()
ovmFeatureDNS().Register()
ovmFeatureTestNetwork().Register()
ovmFeatureNTP().Register()
ovmFeatureDisplayNICs().Register()