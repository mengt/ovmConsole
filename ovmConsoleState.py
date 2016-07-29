#!/usr/bin/env python
#-*-coding:utf-8-*-

import re, os, pickle

from ovmConsoleBases import *
from ovmConsoleLang import *
from ovmConsoleLog import *

class State:
    instance = None
    savePath = '/etc/ovmconsole'
    saveLeafname = 'state.txt'
    thisVersion = 9
    
    #***
    #*** Increment thisVersion (above) when adding attributes to this object
    #***
    def __init__(self):
        self.version = self.thisVersion
        self.authTimeoutSeconds = 5*60
        self.passwordChangeRequired = False # IsPasswordSet now takes care of this
        self.modified = True
        self.rebootMessage = None
        self.weStoppedXAPI = False
        self.verboseBoot = False
        self.keymap = None
        self.sleepSeconds = 30*60
        
    @classmethod
    def SaveFilename(self):
        return self.savePath+'/'+self.saveLeafname
        
    @classmethod
    def Inst(cls):
        # 如果可以加载保存的状态，则创建一个默认对象
        if cls.instance is None:
            isFirstBoot = True
            try:
                if os.path.isfile(cls.SaveFilename()):
                    saveFile = open(cls.SaveFilename(), "r")
                    unpickler = pickle.Unpickler(saveFile)
                    cls.instance = unpickler.load()
                    saveFile.close()
                    isFirstBoot = False
                    if cls.instance.version != cls.instance.thisVersion:
                        # Version mismatch - don't use the state information
                        cls.instance = None
                        ovmLog('State file version mismatch - discarding')
            except Exception, e:
                cls.instance = None
            
            if cls.instance is None:
                cls.instance = State()
                ovmLog('No saved state available - using default state')
            
            # Fill in pseudo-state
            cls.instance.isFirstBoot = isFirstBoot
            cls.instance.MakeSane()
            
        return cls.instance
        
    def AuthTimeoutSeconds(self):
        return self.authTimeoutSeconds
        
    def PasswordChangeRequired(self):
        return self.passwordChangeRequired
        
    def PasswordChangeRequiredSet(self, inValue):
        self.passwordChangeRequired = inValue
        self.modified = True
    
    def RebootMessage(self):
        return self.rebootMessage
        
    def RebootMessageSet(self, inValue):
        self.rebootMessage = inValue
        self.modified = True
    
    def VerboseBoot(self):
        return self.verboseBoot
        
    def VerboseBootSet(self, inValue):
        self.verboseBoot = inValue
        self.modified = True
    
    def Keymap(self):
        return self.keymap
        
    def KeymapSet(self, inValue):
        self.keymap = inValue
        self.modified = True

    def IsFirstBoot(self):
        return self.isFirstBoot
    

    def AuthTimeoutSecondsSet(self, inSeconds): # Don't call this directly - use Auth.TimeoutSecondsSet
        if inSeconds < 60:
            raise Exception("Cannot set a session timeout of less than one minute")
        if self.authTimeoutSeconds != inSeconds:
            self.authTimeoutSeconds = inSeconds
            self.modified = True
        
    def AuthTimeoutMinutes(self):
        return int((self.AuthTimeoutSeconds() + 30) / 60)
    
    def SleepSeconds(self):
        return self.sleepSeconds
    
    def MakeSane(self):
        self.authTimeoutSeconds = int(self.authTimeoutSeconds)
        if self.authTimeoutSeconds < 60:
            AuthTimeoutSecondsSet(60)
    
    def SaveIfRequired(self):
        if self.modified:
            self.MakeSane()
            try:
                if not os.path.isdir(self.savePath):
                    os.mkdir(self.savePath, 0700)
                
                saveFile = open(self.SaveFilename(), "w")
                pickler = pickle.Pickler(saveFile)
                self.modified = False # Set unmodified before saving
                pickler.dump(self)
                saveFile.close()
                ovmLog('Saved state file')
            except Exception, e:
                ovmLogFailure('Failed to save state file', e)


