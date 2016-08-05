#!/usr/bin/env python
#-*-coding:utf-8-*-

import syslog
from ovmConsoleBases import *
from ovmConsoleLang import *

class ovmLogger:
    __instance = None

    def __init__(self):
        syslog.openlog('OvmLog')

    @classmethod
    def Inst(cls):
        if cls.__instance is None:
            cls.__instance = ovmLogger()
        return cls.__instance

    def Log(self, inPriority, *inParams):
        for param in inParams:
            syslog.syslog(inPriority, str(param))

    def logFailure(self, *inParams):
        logString = "\n".join([str(param) for param in inParams])
        message = Lang(Exception(logString))

    def ErrorLoggingHook(self, *inParams):
        # This hook is called by Lang(Exception), so mustn't call Lang(Exception) itself
        logString = "\n".join( [ str(param) for param in inParams ] )
        self.Log(syslog.LOG_ERR, 'Exception: '+logString)

def ovmLog(*inParams):
    ovmLogger.Inst().Log(syslog.LOG_INFO, *inParams)
    
def ovmLogFatal(*inParams):
    ovmLogger.Inst().Log(syslog.LOG_CRIT, *inParams)

# ovmLogFailure should be used for errors implying a test failure.  Otherwise use ovmLogError
def ovmLogError(*inParams):
    ovmLogger.Inst().Log(syslog.LOG_ERR, *inParams)

def ovmLogFailure(*inParams):
    ovmLogger.Inst().logFailure(*inParams)


Language.SetErrorLoggingHook(ovmLogger.Inst().ErrorLoggingHook)