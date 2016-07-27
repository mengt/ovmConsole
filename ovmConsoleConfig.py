#!/usr/bin/env python
#-*-coding:utf-8-*-

import os, sys

class Config:
    '''色彩表'''
    instance = None
    
    def __init__(self):
        self.colours = {
            # Colours specified as name : (red, green, blue), value range 0..999
            'fg_dark' : (400, 400, 360),
            'fg_normal' : (600, 600, 550),
            'fg_bright' : (999, 999, 800),
            'bg_dark' : (258, 258, 258), 
            'bg_normal' : (176, 325, 643), 
            'bg_bright' : (0, 200, 400), 
        }
        
        self.ftpserver = ''
    
    @classmethod
    def Inst(cls):
        if cls.instance is None:
            cls.instance = Config()
        return cls.instance
    
    @classmethod
    def Mutate(cls, inConfig):
        cls.instance = inConfig
    
    def Colour(self,  inName):
        return self.colours[inName]
    
    def FTPServer(self):
        return self.ftpserver
    
    def BrandingMap(self):
        return {}
    
    def AllShellsTimeout(self):
        return True
    
    def DisplaySerialNumber(self):
        return True
        
    def DisplayAssetTag(self):
        return True
    
    def BMCName(self):
        return 'BMC'
        
    def FirstBootEULAs(self):
        # Subclasses in ovmconsoleConfigOEM can add their EULAs to this array
        return ['/EULA']
        
# Import a more specific configuration if available
if os.path.isfile(sys.path[0]+'/ovmConsoleConfigOEM.py'):
    import ovmConsoleConfigOEM
    
