#!/usr/bin/env python
#-*-coding:utf-8-*-

from ovmConsoleAuth import *
from ovmConsoleBases import *
from ovmConsoleHotData import *

class TaskEntry:
    def __init__(self, inHotOpaqueRef, inSession):
        self.hotOpaqueRef = inHotOpaqueRef
        self.session = inSession
        self.startTime = time.time()
        self.completed = False
        self.creationTime = None
        self.finishTime = None
        
    def Completed(self):
        return self.completed
        
    def HandleCompletion(self, inStatus):
        self.session = None

    def Status(self):
        if self.Completed():
            status = self.completionStatus
        else:
            status = None
            if not status.startswith('pending'):
                self.HandleCompletion(status)
        return status
    
    def Result(self):
        if self.Completed():
            result = self.completionStatus
        else:
            result= None
        return HotOpaqueRef(result, 'any')
    
    def CanCancel(self):
        if self.Completed():
            retVal = False
        else:
            allowedOps = None   
            retVal = ('cancel' in allowedOps)
            
        return retVal
        
    def Message(self):
        status = self.Status().lower()
        if status.startswith('pending'):
            retVal = Lang('In progress')
        elif status.startswith('success'):
            retVal = Lang('Operation was successful')
        elif status.startswith('failure'):
            retVal = Lang('Failed: ')+Language.XapiError(self.errorInfo)
        elif status.startswith('cancelling'):
            retVal = Lang('Cancellation in progress')
        elif status.startswith('cancelled'):
            retVal = Lang('Cancelled')
        else:
            retVal = Lang('<Unknown>')
            
        return retVal
    
    def RaiseIfFailed(self):
        if self.Status().lower().startswith('failure'):
            raise Exception(Language.XapiError(self.errorInfo))
    
    def IsPending(self):
        if self.Status().lower().startswith('pending'):
            retVal = True
        else:
            retVal = False
        return retVal

    def ProgressValue(self):
        if self.Completed():
            retVal = 1.0
        else:
            retVal = None
        return retVal
    
    def DurationSecs(self):
        if self.creationTime is not None and self.finishTime is not None:
            retVal = self.finishTime - self.creationTime
        else:
            retVal = time.time() - self.startTime
        return retVal
    
    def Cancel(self):
        pass
    
class Task:
    instance = None
    def __init__(self):
        self.taskList = {}
        self.syncSession = None
            
    @classmethod
    def Inst(cls):
        if cls.instance is None:
            cls.instance = Task()
        return cls.instance
    
    def Create(self, inProc):
        session = None
        try:
            session = Auth.Inst().NewSession()
            taskRef = inProc(session)
        except:
            if session is not None:
                Auth.Inst().CloseSession(session)
            raise
        
        hotTaskRef = HotOpaqueRef(taskRef, 'task')
        taskEntry = TaskEntry(hotTaskRef, session)
        self.taskList[hotTaskRef] = taskEntry
        return taskEntry

    def GarbageCollect(self):
        # This may be expensive as it must fetch status from xapi for each incomplete task
        deleteKeys = []
        for key, value in self.taskList.iteritems():
            # Forget tasks that have of duration of greater than one day
            value.Status()
            if value.Completed() or value.DurationSecs() > 86400:
                deleteKeys.append(key)
        
        for key in deleteKeys:
            del self.taskList[key]

    def SyncSession(self):
        if self.syncSession is None:
            self.syncSession = Auth.Inst().NewSession()
        return self.syncSession

    def SyncOperation(self, inProc):
        retVal = inProc(self.SyncSession())
        return retVal

    @classmethod
    def New(cls, inProc):
        return cls.Inst().Create(inProc)
    
    @classmethod
    def Sync(cls, inProc):
        return cls.Inst().SyncOperation(inProc)

    
