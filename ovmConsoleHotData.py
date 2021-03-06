#!/usr/bin/env python
#-*-coding:utf-8-*-

import commands, re, shutil, sys, socket
from pprint import pprint

from ovmConsoleAuth import *
from ovmConsoleLang import *
from ovmConsoleState import *
from ovmConsoleUtils import *

class HotOpaqueRef:
    def __init__(self, inOpaqueRef, inType):
        self.opaqueRef = inOpaqueRef
        self.type = inType
        self.hash = hash(inOpaqueRef)
    
    def __repr__(self):
        return str(self.__dict__)
        
    # __hash__ and __cmp__ allow this object to be used as a dictionary key
    def __hash__(self):
        return self.hash
    
    def __cmp__(self, inOther):
        if not isinstance(inOther, HotOpaqueRef):
            return 1
        if self.opaqueRef == inOther.opaqueRef:
            return 0
        if self.opaqueRef < inOther.opaqueRef:
            return -1
        return 1
    
    def OpaqueRef(self): return self.opaqueRef
    def Type(self): return self.type
        
class HotAccessor:
    def __init__(self, inName = None, inRefs = None):
        self.name = FirstValue(inName, [])
        self.refs = FirstValue(inRefs, [])
        
    def __getattr__(self, inName):
        retVal = HotAccessor(self.name[:], self.refs[:]) # [:] copies the array
        retVal.name.append(inName)
        retVal.refs.append(None)
        return retVal

    def __iter__(self):
        iterData = HotData.Inst().GetData(self.name, {}, self.refs)
        if isinstance(iterData, types.DictType):
            self.iterKeys = iterData.keys()
        elif isinstance(iterData, (types.ListType, types.TupleType)):
            self.iterKeys = iterData[:] # [:] copy is necessary
        else:
            raise Exception(Lang("Cannot iterate over type '")+str(type(iterData))+"'")
        return self
        
    # This method will hide fields called 'next' in the xapi database.  If any appear, __iter__ will need to
    # return a new object type and this method will need to be moved into that
    def next(self):
        if len(self.iterKeys) <= 0:
            raise StopIteration
        retVal = HotAccessor(self.name[:], self.refs[:]) # [:] copies the array
        retVal.refs[-1] = self.iterKeys.pop(0)
        return retVal

    def __getitem__(self, inParam):
        # These are square brackets selecting a particular item from a dict using its OpaqueRef
        if not isinstance(inParam, (types.IntType, HotOpaqueRef)):
            raise Exception('Use of HotAccessor[param] requires param of type int or HotOpaqueRef, but got '+str(type(inParam)))
        retVal = HotAccessor(self.name[:], self.refs[:])
        retVal.refs[-1] = inParam
        return retVal

    def __call__(self, inParam = None):
        # These are the brackets on the end of the statement, with optional default value.
        # That makes it a request to fetch the data
        if isinstance(inParam, HotOpaqueRef):
            raise Exception('Use [] to pass HotOpaqueRefs to HotAccessors')
        return HotData.Inst().GetData(self.name, inParam, self.refs)
    
    def HotOpaqueRef(self):
        return self.refs[-1]
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

class HotData:
    instance = None
    
    def __init__(self):
        self.data = {}
        self.timestamps = {}
        self.session = None
        self.InitialiseFetchers()

    @classmethod
    def Inst(cls):
        if cls.instance is None:
            cls.instance = HotData()
        return cls.instance
    
    @classmethod
    def Reset(cls):
        if cls.instance is not None:
            del cls.instance
            cls.instance = None
    
    def DeleteCache(self):
        self.data = {}
        self.timestamps = {}
    
    def Fetch(self, inName, inRef):
        # Top-level object are cached by name, referenced objects by reference
        cacheName = FirstValue(inRef, inName)
        cacheEntry = self.data.get(cacheName, None)
        fetcher = self.fetchers[inName]
        timeNow = time.time()
        # If inRef is an array index, the result can't be cached
        if not isinstance(inRef, types.IntType) and cacheEntry is not None and timeNow - cacheEntry.timestamp < fetcher.lifetimeSecs:
            retVal = cacheEntry.value
        else:
            try:
                retVal = fetcher.fetcher(inRef)
                # Save in the cache
                self.data[cacheName] = Struct(timestamp = timeNow, value = retVal)
            except socket.timeout:
                self.session = None
                raise socket.timeout
        return retVal    
    
    def FetchByRef(self, inRef):
        retVal = self.Fetch(inRef.Type(), inRef)
        return retVal
    
    def FetchByNameOrRef(self, inName, inRef):
        if inName in self.fetchers:
            retVal = self.Fetch(inName, inRef)
        else:
            retVal = self.Fetch(inRef.Type(), inRef)
        return retVal

    def GetData(self, inNames, inDefault, inRefs):
        try:
            itemRef = self.data # Start at the top level
    
            for i, name in enumerate(inNames):
                currentRef = inRefs[i]
                if isinstance(currentRef, HotOpaqueRef):
                    # If currentRef is a HotOpaqueRef, always fetch the corresponding object
                    itemRef = self.FetchByNameOrRef(name, currentRef)
                else:
                    # Look for a data fetcher matching this item name
                    if name in self.fetchers:
                        # We have a fetcher for this element, so use it
                        
                        # Handle the case where itemRef is a dictionary containing the key/value pair ( current name : HotOpaqueRef )
                        if isinstance(itemRef, types.DictType) and name in itemRef and isinstance(itemRef[name], HotOpaqueRef):
                            # This is a subitem with an OpaqueRef supplied by xapi, so fetch the obect it's referring to
                            itemRef = self.Fetch(name, itemRef[name])
                        else:
                            # Fetch without a reference
                            itemRef = self.Fetch(name, None)
                    else:
                        # No fetcher for this item, so return the value of the named element if is in the dictionary,
                        # or the default if not
                        # First, promote OpaqueRefs to the object they refer to
                        if isinstance(itemRef, HotOpaqueRef):
                            itemRef = self.FetchByRef(itemRef)

                        # This allows hash navigation using HotAccessor().key1.key2.key3(), etc.
                        itemRef = itemRef[name] # Allow to throw if element not present
    
                    # Handle integer references as list indices
                    if isinstance(currentRef, types.IntType):
                        if not isinstance(itemRef, (types.ListType, types.TupleType)):
                            raise Exception("List index supplied but element '"+'.'.join(inNames)+"' is not a list")
                        if inRefs[i] >= len(itemRef) or currentRef < -len(itemRef):
                            raise Exception("List index "+str(currentRef)+" out of range in '"+'.'.join(inNames)+"'")
                        itemRef = itemRef[currentRef]
            return itemRef
        except Exception, e:
            # Data not present/fetchable, so return the default value
            return FirstValue(inDefault, None)                
        
    def __getattr__(self, inName):
        if inName[0].isupper():
            # Don't expect elements to start with upper case, so probably an unknown method name
            raise Exception("Unknown method HotData."+inName)
        return HotAccessor([inName], [None])

    def AddFetcher(self, inKey, inFetcher, inLifetimeSecs):
        self.fetchers[inKey] = Struct( fetcher = inFetcher, lifetimeSecs = inLifetimeSecs ) 

    def InitialiseFetchers(self):
        self.fetchers = {}
        self.AddFetcher('host', self.FetchHost, 5)
        self.AddFetcher('host_cpu', self.FetchHostCPUs, 5)
        self.AddFetcher('local_host', self.FetchLocalHost, 5) # Derived
        self.AddFetcher('local_host_ref', self.FetchLocalHostRef, 60) # Derived
        self.AddFetcher('local_pool', self.FetchLocalPool, 5) # Derived
        self.AddFetcher('metrics', self.FetchMetrics, 5)
        self.AddFetcher('pbd', self.FetchPBD, 5)
        self.AddFetcher('pool', self.FetchPool, 5)
        self.AddFetcher('sr', self.FetchSR, 5)
        self.AddFetcher('visible_sr', self.FetchVisibleSR, 5) # Derived
    


    def FetchGuestVM(self, inOpaqueRef):
        if inOpaqueRef is not None:
            # Don't need to filter, so can use the standard VM fetch
            retVal = self.FetchVM(inOpaqueRef)
        else:
            retVal = {}
            for key, value in self.vm().iteritems():
                if not value.get('is_a_template', False) and not value.get('is_control_domain', False):
                    retVal[key] = value
        return retVal

    def FetchHostCPUs(self, inOpaqueRef):
        def LocalConverter(inCPU):
            return HotData.ConvertOpaqueRefs(inCPU,
                host='host'
                )
        return None

    def FetchGuestVMDerived(self, inOpaqueRef):
        retVal = {}
        halted = 0
        paused = 0
        running = 0
        suspended = 0

        for key, vm in self.guest_vm().iteritems():
            powerState = vm.get('power_state', '').lower()
            if powerState.startswith('halted'):
                halted += 1
            elif powerState.startswith('paused'):
                paused += 1
            elif powerState.startswith('running'):
                running += 1
            elif powerState.startswith('suspended'):
                suspended += 1
            
        retVal['num_halted'] = halted
        retVal['num_paused'] = paused
        retVal['num_running'] = running
        retVal['num_suspended'] = suspended

        return retVal

    def FetchLocalHost(self, inOpaqueRef):
        retVal = self.FetchHost(self.FetchLocalHostRef(inOpaqueRef))
        return retVal
        
    def FetchLocalHostRef(self, inOpaqueRef):
        if inOpaqueRef is not None:
            raise Exception("Request for local host must not be passed an OpaqueRef")
        #retVal = HotOpaqueRef(thisHost, 'host')
        return None    
    
    def FetchLocalPool(self, inOpaqueRef):
        if inOpaqueRef is not None:
            raise Exception("Request for local pool must not be passed an OpaqueRef")
        return None
        
    def FetchHost(self, inOpaqueRef):
        def LocalConverter(inHost):
            return HotData.ConvertOpaqueRefs(inHost,
                crash_dump_sr = 'sr',
                consoles = 'console',
                current_operations = 'task',
                host_CPUs = 'host_cpu',
                metrics = 'host::metrics',
                PBDs = 'pbd',
                PIFs='pif',
                resident_VMs = 'vm',
                suspend_image_sr = 'sr',
                VBDs = 'vbd',
                VIFs = 'vif'
                )
        return None
        
    def FetchMetrics(self, inOpaqueRef):
        if inOpaqueRef is None:
            raise Exception("Request for VM metrics requires an OpaqueRef")
        if inOpaqueRef.Type() == 'vm::metrics':
            retVal = None
        elif inOpaqueRef.Type() == 'host::metrics':
            retVal = None
        else:
            raise Exception("Unknown metrics type '"+inOpaqueRef.Type()+"'")
        return retVal

    def FetchPBD(self, inOpaqueRef):
        def LocalConverter(inPBD):
            return HotData.ConvertOpaqueRefs(inPBD,
                host='host',
                SR='sr'
            )
                
        return None

    def FetchPool(self, inOpaqueRef):
        def LocalConverter(inPool):
            return HotData.ConvertOpaqueRefs(inPool,
                crash_dump_SR='sr',
                default_SR='sr',
                master='host',
                suspend_image_SR='sr'
            )
        return None
        
    def FetchSR(self, inOpaqueRef):
        return None
    
    def FetchVisibleSR(self, inOpaqueRef):
        if inOpaqueRef is not None:
            # Make sr[ref] and visible_sr[ref] do the same thing, i.e. don't check the the SR is visible
            retVal = self.FetchSR(inOpaqueRef) 
        else:
            retVal = {}
            for sr in HotAccessor().sr: # Iterates through HotAccessors to SRs
                visible = False
                if len(sr.PBDs()) == 0:
                    visible = True # This is a detached SR so list it as visible
                else:
                    for pbd in sr.PBDs(): # Iterates through HotOpaqueRefs to PBDs
                        if pbd in HotAccessor().local_host.PBDs(): # host.PBDs() is a list of HotOpaqueRefs
                            visible = True
                if visible:
                    retVal[sr.HotOpaqueRef()] = sr
                    
        return retVal


    @classmethod # classmethod so that other class's fetchers can use it easily
    def ConvertOpaqueRefs(cls, *inArgs, **inKeywords):
        if len(inArgs) != 1:
            raise Exception('ConvertOpaqueRef requires a dictionary object as the first argument')
        ioObj = inArgs[0]
        for keyword, value in inKeywords.iteritems():
            obj = ioObj.get(keyword, None)
            if obj is not None:
                if isinstance(obj, str):
                    ioObj[keyword] = HotOpaqueRef(obj, value)
                elif isinstance(obj, types.ListType):
                    ioObj[keyword] = [ HotOpaqueRef(x, value) for x in obj ]
                elif isinstance(obj, types.DictType):
                    result = {}
                    for key, item in obj.iteritems():
                        result[ HotOpaqueRef(key, value) ] = item
                    ioObj[keyword] = result
                    
        if Auth.Inst().IsTestMode(): # Tell the caller what they've missed, when in test mode
            for key,value in ioObj.iteritems():
                if isinstance(value, str) and value.startswith('OpaqueRef'):
                    print('Missed OpaqueRef string in HotData item: '+key)
                elif isinstance(value, types.ListType):
                    for item in value:
                        if isinstance(item, str) and item.startswith('OpaqueRef'):
                            print('Missed OpaqueRef List in HotData item: '+key)
                            break
                elif isinstance(value, types.DictType):
                    for item in value.keys():
                        if isinstance(item, str) and item.startswith('OpaqueRef'):
                            print('Missed OpaqueRef Dict in HotData item: '+key)
                            break

        return ioObj

    def Session(self):
        if self.session is None:
            self.session = Auth.Inst().OpenSession()
        return self.session
        
    def Dump(self):
        print "Contents of HotData cache:"
        pprint(self.data)
