#!/usr/bin/env python
#-*-coding:utf-8-*-

import commands, re, shutil, sys, tempfile, socket
from pprint import pprint
from simpleconfig import SimpleConfigFile

from ovmConsoleAuth import *
from ovmConsoleLang import *
from ovmConsoleLog import *
from ovmConsoleState import *
from ovmConsoleUtils import *

class DataMethod:
    def __init__(self, inSend, inName):
        self.send = inSend
        self.name = inName
        
    def __getattr__(self, inName):
        return DataMethod(self.send, self.name+[inName])

    def __call__(self,  inDefault = None):
        return self.send(self.name,  inDefault)

class Data:
    DISK_TIMEOUT_SECONDS = 60
    instance = None
    
    def __init__(self):
        self.data = {}
        self.session = None
    
    @classmethod
    def Inst(cls):
        if cls.instance is None:
            cls.instance = Data()
            cls.instance.Create()
        return cls.instance
    
    @classmethod
    def Reset(cls):
        if cls.instance is not None:
            del cls.instance
            cls.instance = None
    
    def DataCache(self):
        # Not for general use
        return self.data
    
    def GetData(self, inNames, inDefault = None):
        data = self.data
        for name in inNames:
            if name is '__repr__':
                # Error - missing ()
                raise Exception('Data call Data.' + '.'.join(inNames[:-1]) + ' must end with ()')
            elif name in data:
                data = data[name]
            else:
                return FirstValue(inDefault, Lang('<Unknown>'))
        return data
    
    # Attribute access can be used in two ways
    #   self.host.software_version.oem_model()
    # returns the value of self.data['hos']['software_version']['oem_model'], or the string '<Unknown>'
    # if the element doesn't exist.
    #   self.host.software_version.oem_model('Default')
    # is similar but returns the parameter ('Default' in this case) if the element doesn't exist
    def __getattr__(self, inName):
        if inName[0].isupper():
            # Don't expect elements to start with upper case, so probably an unknown method name
            raise Exception("Unknown method Data."+inName)
        return DataMethod(self.GetData, [inName])
    
    def RequireSession(self):
        if self.session is None:
            self.session = Auth.Inst().OpenSession()
        return self.session
    
    def Create(self):
        '''创建静态数据，更新动态数据'''
        self.data = {}
        
        self.ReadTimezones()
        (status, output) = commands.getstatusoutput("dmidecode")
        if status != 0:
            # Use test dmidecode file if there's no real output
            (status, output) = commands.getstatusoutput("/bin/cat ./dmidecode.txt")
        
        if status == 0:
            self.ScanDmiDecode(output.split("\n"))
     
        (status, output) = commands.getstatusoutput("/sbin/lspci -m")
        if status != 0:
            (status, output) = commands.getstatusoutput("/usr/bin/lspci -m")

        if status == 0:
            self.ScanLspci(output.split("\n"))
     
        if os.path.isfile("/usr/bin/ipmitool"):
            (status, output) = commands.getstatusoutput("/usr/bin/ipmitool mc info")
            if status == 0:
                self.ScanIpmiMcInfo(output.split("\n"))
        
        # /proc/cpuinfo has details of the virtual CPUs exposed to DOM-0, not necessarily the real CPUs
        (status, output) = commands.getstatusoutput("/bin/cat /proc/cpuinfo")
        if status == 0:
            self.ScanCPUInfo(output.split("\n"))

        (status, output) = commands.getstatusoutput("/usr/bin/openssl x509 -in /etc/xensource/xapi-ssl.pem -fingerprint -noout")
        if status == 0:
            fp = output.split("=")
            if len(fp) >= 2:
                self.data['sslfingerprint'] = fp[1]
            else:
                self.data['sslfingerprint'] = "<Unknown>"
        
        try:
            #通过hostname文件获得节点名称
            self.data['hostname'] = ShellPipe('hostname').AllOutput()[0]
        except:
            self.data['hostname'] = Lang('<Unknown>')
        try:
            #通过/etc/system-release文件获得节点版本
            self.data['version'] = ShellPipe('/usr/bin/cat','/etc/system-release').AllOutput()[0]
        except:
            self.data['version'] = Lang('<Unknown>')
        try:
            self.data['sshfingerprint'] = ShellPipe('/usr/bin/ssh-keygen', '-lf', '/etc/ssh/ssh_host_rsa_key.pub').AllOutput()[0].split(' ')[1]
        except:
            self.data['sshfingerprint'] = Lang('<Unknown>')
        
        try:
            self.data['state_on_usb_media'] = ( ShellPipe('/bin/bash', '-c', 'source /opt/xensource/libexec/oem-functions; if state_on_usb_media; then exit 1; else exit 0; fi').CallRC() != 0 )
        except:
            self.data['state_on_usb_media'] = True
    


        self.Update()
    
    def FakeMetrics(self, inPIF):
        retVal = {
            'carrier' : False,
            'device_name' : '',
            'vendor_name' : ''
            }
        return retVal
    
    def CloseSession(self):
        if self.session is not None:
            self.session = Auth.Inst().CloseSession(self.session)
    
    def Update(self):
        '''更新动态数据'''
        self.data['host'] = {}

        self.RequireSession()
        if self.session is not None:
            try:
                self.data['host'] = None
                self.data['host']['opaqueref'] = None
                
                # Expand the items we need in the host record
                self.data['host']['metrics'] = None
                
                try:
                    self.data['host']['suspend_image_sr'] = None
                    # NULL or dangling reference
                except:
                    self.data['host']['suspend_image_sr'] = None
                    
                try:
                    self.data['host']['crash_dump_sr'] = None
                except:
                    # NULL or dangling reference
                    self.data['host']['crash_dump_sr'] = None
                
                convertCPU = lambda cpu: None
                self.data['host']['host_CPUs'] = map(convertCPU, self.data['host']['host_CPUs'])
                
                def convertPIF(inPIF):
                    retVal = {}
                    try:
                        retVal['metrics'] = None
                    except e:
                        retVal['metrics' ] = None
                    
                    try:
                        retVal['network'] = None
                    except e:
                        ovmLogError('Missing network record: ', e)
                        
                    retVal['opaqueref'] = inPIF
                    return retVal
    
                self.data['host']['PIFs'] = map(convertPIF, self.data['host']['PIFs'])
    
                # Create missing PIF names
                for pif in self.data['host']['PIFs']:
                    if pif['metrics']['device_name'] == '':
                        if not pif['physical']:
                            # Bonded PIF
                            pif['metrics']['device_name'] = Lang("Virtual PIF within ")+pif['network'].get('name_label', Lang('<Unknown>'))
                        else:
                            pif['metrics']['device_name'] = Lang('<Unknown>')
    
                # Sort PIFs by device name for consistent order
                self.data['host']['PIFs'].sort(lambda x, y : cmp(x['device'], y['device']))

                def convertVBD(inVBD):
                    return None
                    
                def convertVDI(inVDI):
                    return None
                    
                def convertPBD(inPBD):
                    return None
                    
                self.data['host']['PBDs'] = map(convertPBD, self.data['host']['PBDs'])

                # Only load the to DOM-0 VM to save time
                vmList = self.data['host']['resident_VMs']
                
                pools = None
                
                def convertPool(inID, inPool):
                    retPool = inPool
                    retPool['opaqueref'] = inID
                    try:
                        retPool['master_uuid'] = None
                    except:
                        retPool['master_uuid'] = None

                    # SRs in the pool record are often apparently valid but dangling references.
                    # We fetch the uuid to determine whether the SRs are real.
                    try:
                        retPool['default_SR_uuid'] = None
                    except:
                        retPool['default_SR_uuid'] = None

                    try:
                        retPool['suspend_image_SR_uuid'] = None
                    except:
                        retPool['suspend_image_SR_uuid'] = None
                        
                    try:
                        retPool['crash_dump_SR_uuid'] = None
                    except:
                        retPool['crash_dump_SR_uuid'] = None
                    return retPool
                
                self.data['pools'] = {}
                for id, pool in pools.iteritems():
                   self.data['pools'][id] = convertPool(id, pool)

            except socket.timeout:
                self.session = None
            except Exception, e:
                ovmLogError('Data update failed: ', e)

            try:
                self.data['sr'] = []

                pbdRefs = []
                for pbd in self.data['host'].get('PBDs', []):
                    pbdRefs.append(pbd['opaqueref'])
                    
                    
            except Exception, e:
                ovmLogError('SR data update failed: ', e)

        self.UpdateFromResolveConf()
        self.UpdateFromSysconfig()
        self.UpdateFromNTPConf()
        self.UpdateFromTimezone()
        
        if os.path.isfile("/sbin/chkconfig"):
            (status, output) = commands.getstatusoutput("/sbin/chkconfig --list sshd && /sbin/chkconfig --list ntpd")
            if status == 0:
                self.ScanChkConfig(output.split("\n"))

        self.DeriveData()
        
    def DeriveData(self):
        self.data.update({
            'derived' : {
                'app_name' : Lang("UniCenter"),
                'full_app_name' : Lang("Esage UniCenter"),
                'cpu_name_summary' : {}
            }
        })
        
        # Gather up the CPU model names into a more convenient form
        if 'host_CPUs' in self.data['host']:
            hostCPUs = self.data['host']['host_CPUs']
    
            cpuNameSummary = self.data['derived']['cpu_name_summary']
            
            for cpu in hostCPUs:
                name = " ".join(cpu['modelname'].split())
                if name in cpuNameSummary:
                    cpuNameSummary[name] += 1
                else:
                    cpuNameSummary[name] = 1        
        
        # Select the current management PIFs
        self.data['derived']['managementpifs'] = []
        if 'PIFs' in self.data['host']:
            for pif in self.data['host']['PIFs']:
                if pif['management']:
                    self.data['derived']['managementpifs'].append(pif)
        
        # Add a reference to the DOM-0 VM
        if 'resident_VMs' in self.data['host']:
            for vm in self.data['host']['resident_VMs']:
                if 'domid' in vm and vm['domid'] == '0':
                    self.data['derived']['dom0_vm'] = vm
     
        # Calculate the full version string
        version = self.host.software_version.product_version(self.host.software_version.platform_version())
        version += '-' + self.host.software_version.build_number('')

        oemBuildNumber = self.host.software_version.oem_build_number('')
        if oemBuildNumber != '':
            version += '-'+oemBuildNumber
        if version.startswith('-'):
            version = Lang("<Unknown>")
        self.data['derived']['fullversion'] = version

        # Calculate the branding string
        brand = self.host.software_version.product_brand(self.host.software_version.platform_name())
        self.data['derived']['brand'] = brand

    def Dump(self):
        pprint(self.data)

    def HostnameSet(self, inHostname):
        Auth.Inst().AssertAuthenticated()

        # Protect from shell escapes
        if not re.match(r'[-A-Za-z0-9.]+$', inHostname):
            raise Exception("Invalid hostname '"+inHostname+"'")
        IPUtils.AssertValidNetworkName(inHostname)
        
    def NameLabelSet(self, inNameLabel):
        pass

    def NameserversSet(self, inServers):
        self.data['dns']['nameservers'] = inServers

    def NTPServersSet(self, inServers):
        self.data['ntp']['servers'] = inServers


    
    def UpdateFromResolveConf(self):
        (status, output) = commands.getstatusoutput("/bin/cat /etc/resolv.conf")
        if status == 0:
            self.ScanResolvConf(output.split("\n"))
    
    def UpdateFromSysconfig(self):
        (status, output) = commands.getstatusoutput("/bin/cat /etc/sysconfig/network")
        if status == 0:
            self.ScanSysconfigNetwork(output.split("\n"))
    
    def UpdateFromNTPConf(self):
        (status, output) = commands.getstatusoutput("/bin/cat /etc/ntp.conf")
        if status == 0:
            self.ScanNTPConf(output.split("\n"))
            
    def StringToBool(self, inString):
        return inString.lower().startswith('true')

    def RootLabel(self):
        output = commands.getoutput('/bin/cat /proc/cmdline')
        match = re.search(r'root=\s*LABEL\s*=\s*(\S+)', output)
        if match:
            retVal = match.group(1)
        else:
            retVal = 'xe-0x'
        return retVal

    def GetVersion(self, inLabel):
        match = re.match(r'(xe-|rt-)(\d+)[a-z]', inLabel)
        if match:
            retVal = int(match.group(2))
        else:
            retVal = 0
        
        return retVal

    def SaveToSysconfig(self):
        # Double-check authentication
        Auth.Inst().AssertAuthenticated()
        
        file = None
        try:
            file = open("/etc/sysconfig/network", "w")
            for other in self.sysconfig.network.othercontents([]):
                file.write(other+"\n")
            file.write("HOSTNAME="+self.sysconfig.network.hostname('')+"\n")
        finally:
            if file is not None: file.close()
            self.UpdateFromSysconfig()
    
    def SaveToNTPConf(self):
        # Double-check authentication
        Auth.Inst().AssertAuthenticated()
        
        file = None
        try:
            file = open("/etc/ntp.conf", "w")
            for other in self.ntp.othercontents([]):
                file.write(other+"\n")
            for server in self.ntp.servers([]):
                file.write("server "+server+"\n")
        finally:
            if file is not None: file.close()
            self.UpdateFromNTPConf()
    
    def ScanDmiDecode(self, inLines):
        STATE_NEXT_ELEMENT = 2
        state = 0
        handles = []
        
        self.data['dmi'] = {
            'cpu_sockets' : 0,
            'cpu_populated_sockets' : 0,
            'memory_sockets' : 0,
            'memory_modules' : 0,
            'memory_size' : 0
        }
        
        for line in inLines:
            indent = 0
            while len(line) > 0 and line[0] == "\t":
                indent += 1
                line = line[1:]
                    
            if indent == 0 and state > 3:
                state = STATE_NEXT_ELEMENT
                
            if state == 0:
                self.data['dmi']['dmi_banner'] = line
                state += 1
            elif state == 1:
                match = re.match(r'(SMBIOS\s+\S+).*', line)
                if match:
                    self.data['dmi']['smbios'] = match.group(1)
                    state += 1
            elif state == 2:
                # scan for 'Handle...' line
                if indent == 0:
                    match = re.match(r'Handle (.*)$', line)
                    if match and (match.group(1) not in handles):
                        handles.append(match.group(1))
                        state += 1
            elif state == 3:
                if indent == 0:
                    elementName = line
                    if elementName == 'BIOS Information': state = 4
                    elif elementName == 'System Information': state = 5
                    elif elementName == 'Chassis Information': state = 6
                    elif elementName == 'Processor Information': state = 7
                    elif elementName == 'Memory Device': state = 8
                    else:        
                        state = STATE_NEXT_ELEMENT
                else:        
                    state = STATE_NEXT_ELEMENT
            elif state == 4: # BIOS Information
                self.Match(line, r'Vendor:\s*(.*?)\s*$', 'bios_vendor')
                self.Match(line, r'Version:\s*(.*?)\s*$', 'bios_version')
            elif state == 5: # System Information
                self.Match(line, r'Manufacturer:\s*(.*?)\s*$', 'system_manufacturer')
                self.Match(line, r'Product Name:\s*(.*?)\s*$', 'system_product_name')
                self.Match(line, r'Serial Number:\s*(.*?)\s*$', 'system_serial_number')
            elif state == 6: # Chassis information
                self.Match(line, r'Asset Tag:\s*(.*?)\s*$', 'asset_tag')
            elif state == 7: # Processor information
                if self.MultipleMatch(line, r'Socket Designation:\s*(.*?)\s*$', 'cpu_socket_designations'):
                    self.data['dmi']['cpu_sockets'] += 1
                if re.match(r'Status:.*Populated.*', line):
                    self.data['dmi']['cpu_populated_sockets'] += 1
            elif state == 8: # Memory Device
                if self.MultipleMatch(line, r'Locator:\s*(.*?)\s*$', 'memory_locators'):
                    self.data['dmi']['memory_sockets'] += 1
                match = self.MultipleMatch(line, r'Size:\s*(.*?)\s*$', 'memory_sizes')
                if match:
                    size = re.match(r'(\d+)\s+([MGBmgb]+)', match.group(1))
                    if size and size.group(2).lower() == 'mb':
                        self.data['dmi']['memory_size'] += int(size.group(1))
                        self.data['dmi']['memory_modules'] += 1
                    elif size and size.group(2).lower() == 'gb':
                        self.data['dmi']['memory_size'] += int(size.group(1)) * 1024
                        self.data['dmi']['memory_modules'] += 1
    
    def Match(self, inLine, inRegExp, inKey):
        match = re.match(inRegExp, inLine)
        if match:
            self.data['dmi'][inKey] = match.group(1)
        return match
    
    def MultipleMatch(self, inLine, inRegExp, inKey):
        match = re.match(inRegExp, inLine)
        if match:
            if not self.data['dmi'].has_key(inKey):
                self.data['dmi'][inKey] = []
            self.data['dmi'][inKey].append(match.group(1))

        return match

    def ScanLspci(self, inLines):
        self.data['lspci'] = {
            'storage_controllers' : []
        }
        # Spot storage controllers by looking for keywords or the phrase 'storage controller' in the lspci output
        classExp = re.compile(r'[Ss]torage|IDE|PATA|SATA|SCSI|SAS|RAID|[Ff]iber [Cc]hannel|[Ff]ibre [Cc]hannel')
        nameExp = re.compile(r'IDE|PATA|SATA|SCSI|SAS|RAID|[Ff]iber [Cc]hannel|[Ff]ibre [Cc]hannel')
        unknownExp = re.compile(r'[Uu]nknown [Dd]evice')
        regExp = re.compile(
            r'[^"]*' + # Bus position, etc.
            r'"([^"]*)"[^"]+' + # Class 
            r'"([^"]*)"[^"]+' + # Vendor 
            r'"([^"]*)"[^"]+' + # Device 
            r'"([^"]*)"[^"]+' + # SVendor 
            r'"([^"]*)"') # SDevice 
            
        for line in inLines:
            match = regExp.match(line)
            if match:
                devClass = match.group(1)
                devVendor = match.group(2)
                devName = match.group(3)
                devSVendor = match.group(4)
                devSName = match.group(5)

                # Determine whether this device is a storage controller
                if (classExp.search(devClass) or
                    nameExp.search(devName) or
                    nameExp.search(devSName)):
                    # Device is a candidate for the list.  Do we have a useful name for it?  
                    if not unknownExp.search(devSName) and devSName != '':
                        self.data['lspci']['storage_controllers'].append((devClass, devSVendor+' '+devSName)) # Tuple so double brackets
                    elif not unknownExp.search(devName):
                        self.data['lspci']['storage_controllers'].append((devClass, devName)) # Tuple so double brackets
                    else:
                        self.data['lspci']['storage_controllers'].append((devClass, devVendor+' '+devName)) # Tuple so double brackets
            
    def ScanIpmiMcInfo(self, inLines):
        self.data['bmc'] = {}

        for line in inLines:
            match = re.match(r'Firmware\s+Revision\s*:\s*([-0-9.]+)', line)
            if match:
                self.data['bmc']['version'] = match.group(1)
    
    def ScanChkConfig(self, inLines):
        self.data['chkconfig'] = {}

        for line in inLines:
            # Is sshd on for runlevel 5?
            if re.match(r'sshd.*5\s*:\s*on', line, re.IGNORECASE):
                self.data['chkconfig']['sshd'] = True
            elif re.match(r'sshd.*5\s*:\s*off', line, re.IGNORECASE):
                self.data['chkconfig']['sshd'] = False
            # else leave as Unknown
            elif re.match(r'ntpd.*5\s*:\s*on', line, re.IGNORECASE):
                self.data['chkconfig']['ntpd'] = True
            elif re.match(r'ntpd.*5\s*:\s*off', line, re.IGNORECASE):
                self.data['chkconfig']['ntpd'] = False

    def ScanResolvConf(self, inLines):
        self.data['dns'] = {
            'nameservers' : [], 
            'othercontents' : []
        }
        for line in inLines:
            match = re.match(r'nameserver\s+(\S+)',  line)
            if match:
                self.data['dns']['nameservers'].append(match.group(1))
            else:
                self.data['dns']['othercontents'].append(line)
    
    def ScanSysconfigNetwork(self, inLines):
        if not 'sysconfig' in self.data:
            self.data['sysconfig'] = {}
            
        self.data['sysconfig']['network'] = {'othercontents' : [] }
        
        for line in inLines:
            match = re.match(r'HOSTNAME\s*=\s*(.*)', line)
            if match:
                self.data['sysconfig']['network']['hostname'] = match.group(1)
            else:
                self.data['sysconfig']['network']['othercontents'].append(line)
    
    def ScanNTPConf(self, inLines):
        if not 'ntp' in self.data:
            self.data['ntp'] = {}
        
        self.data['ntp']['servers'] = []
        self.data['ntp']['othercontents'] = []
        
        for line in inLines:
            match = re.match(r'server\s+(\S+)', line)
            if match and not match.group(1).startswith('127.127.'):
                self.data['ntp']['servers'].append(match.group(1))
            else:
                self.data['ntp']['othercontents'].append(line)
                
    def ScanCPUInfo(self, inLines):
        self.data['cpuinfo'] = {}
        for line in inLines:
            match = re.match(r'flags\s*:\s*(.*)', line)
            if match:
                self.data['cpuinfo']['flags'] = match.group(1).split()

    def ReadTimezones(self):
        self.data['timezones'] = {
            'continents': {
                Lang('Africa') : 'Africa',
                Lang('Americas') : 'America',
                Lang('US') : 'US',
                Lang('Canada') : 'Canada',
                Lang('Asia') : 'Asia',
                Lang('Atlantic Ocean') : 'Atlantic',
                Lang('Australia') : 'Australia',
                Lang('Europe') : 'Europe',
                Lang('Indian Ocean') : 'Indian',
                Lang('Pacific Ocean') : 'Pacific',
                Lang('Other') : 'Etc'
            },
            'cities' : {} 
        }
        
        filterExp = re.compile('('+'|'.join(self.data['timezones']['continents'].values())+')')

        zonePath = '/usr/share/zoneinfo'
        for root, dirs, files in os.walk(zonePath):
            for filename in files:
                filePath = os.path.join(root, filename)
                localPath = filePath[len(zonePath)+1:] # Just the path after /usr/share/zoneinfo/
                if filterExp.match(localPath):
                    # Store only those entries starting with one of our known prefixes
                    self.data['timezones']['cities'][localPath] = filePath

    def UpdateFromTimezone(self):
        if os.path.isfile('/etc/timezone'):
            file = open('/etc/timezone')
            self.data['timezones']['current'] = file.readline().rstrip()
            file.close()

    def TimezoneSet(self, inTimezone):
        localtimeFile = '/etc/localtime'
        if os.path.isfile(localtimeFile):
            os.remove(localtimeFile)
        os.symlink(self.timezones.cities({})[inTimezone], localtimeFile)
        
        file = open('/etc/timezone', 'w')
        file.write(inTimezone+"\n")
        file.close()

        if os.path.exists('/etc/sysconfig/clock'):
            cfg = SimpleConfigFile()
            cfg.read('/etc/sysconfig/clock')
            cfg.info["ZONE"] = inTimezone
            cfg.write('/etc/sysconfig/clock')

    def CurrentTimeString(self):
        return commands.getoutput('/bin/date -R')

    
    def RemovePartitionSuffix(self, inDevice):
        regExpList = [
            r'(/dev/disk/by-id.*?)-part[0-9]+$',
            r'(/dev/cciss/.*?)p[0-9]+$',
            r'(/dev/.*?)[0-9]+$'
        ]
            
        retVal = inDevice
        for regExp in regExpList:
            match = re.match(regExp, inDevice)
            if match:
                retVal = match.group(1)
                break
        return retVal
        
    def GetSRFromDevice(self, inDevice):
        retVal = None

        for pbd in self.host.PBDs([]):
            device = pbd.get('device_config', {}).get('device', '')
            if self.RemovePartitionSuffix(device) == inDevice:
                # This is the PBD containing the device.  Does it have an SR?
                sr = pbd.get('SR', None)
                if sr.get('name_label', None) is not None:
                    retVal = sr
        return retVal
    
    def SetPoolSRIfRequired(self, inOpaqueRef):
        pass

    def SetPoolSRsFromDeviceIfNotSet(self, inDevice):
        sr = self.GetSRFromDevice(inDevice)
        if sr is None:
            raise Exception(Lang("Device does not have an associated SR"))

        self.SetPoolSRIfRequired(sr['opaqueref'])

    def GetPoolForThisHost(self):
        self.RequireSession()
        retVal = None
        for pool in self.pools({}).values():
            # Currently there is only one pool
            retVal = pool
            break
            
        return retVal
    
    def ReconfigureManagement(self, inPIF, inMode,  inIP,  inNetmask,  inGateway, inDNS = None):
        pass

    
    def DisableManagement(self):
        pass
    
    def LocalHostEnable(self):
        pass
        
    def LocalHostDisable(self):
        pass

    def ConfigureRemoteShell(self, inEnable):
        if inEnable:
            status, output = commands.getstatusoutput("/sbin/chkconfig sshd on")
        else:
            status, output = commands.getstatusoutput("/sbin/chkconfig sshd off")
        
        if status != 0:
            raise Exception(output)
    
    def Ping(self,  inDest):
        # Must be careful that no unsanitised data is passed to the command
        if not re.match(r'[0-9a-zA-Z][-0-9a-zA-Z.]*$',  inDest):
            raise Exception("Invalid destination '"+inDest+"'")
        IPUtils.AssertValidNetworkName(inDest)
        pipe = ShellPipe('/bin/ping', '-c',  '1',  '-w', '2', inDest)
        status = pipe.CallRC()
        return (status == 0, "\n".join(pipe.AllOutput()))
    
    def ManagementIP(self, inDefault = None):
        retVal = inDefault
        
        retVal = self.host.address(retVal)
        
        return retVal

    def ManagementNetmask(self, inDefault = None):
        retVal = inDefault
        
        # FIXME: Address should come from API, but not available at present.  For DHCP this is just a guess at the gateway address
        for pif in self.derived.managementpifs([]):
            if pif['ip_configuration_mode'].lower().startswith('static'):
                # For static IP the API address is correct
                retVal = pif['netmask']
            elif pif['ip_configuration_mode'].lower().startswith('dhcp'):
                # For DHCP,  find the gateway address by parsing the output from the 'route' command
                if 'bridge' in pif['network']:
                    device = pif['network']['bridge']
                else:
                    device = pif['device']

                device = ShellUtils.MakeSafeParam(device)

                ipre = r'[0-9a-f.:]+'
                ifRE = re.compile(r'\s*inet\s+addr\s*:'+ipre+'\s+bcast\s*:\s*'+ipre+r'\s+mask\s*:\s*('+ipre+r')\s*$',
                    re.IGNORECASE)

                ifconfig = commands.getoutput("/sbin/ifconfig '"+device+"'").split("\n")
                for line in ifconfig:
                    match = ifRE.match(line)
                    if match:
                        retVal = match.group(1)
                        break
    
        return retVal
    
    def ManagementGateway(self, inDefault = None):
        retVal = inDefault
        
        # FIXME: Address should come from API, but not available at present.  For DHCP this is just a guess at the gateway address
        for pif in self.derived.managementpifs([]):
            if pif['ip_configuration_mode'].lower().startswith('static'):
                # For static IP the API address is correct
                retVal = pif['gateway']
            elif pif['ip_configuration_mode'].lower().startswith('dhcp'):
                # For DHCP,  find the gateway address by parsing the output from the 'route' command
                if 'bridge' in pif['network']:
                    device = pif['network']['bridge']
                else:
                    device = pif['device']
                routeRE = re.compile(r'([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+UG\s+\d+\s+\d+\s+\d+\s+'+device,
                    re.IGNORECASE)
    
                routes = commands.getoutput("/sbin/route -n").split("\n")
                for line in routes:
                    match = routeRE.match(line)
                    if match:
                        retVal = match.group(2)
                        break
    
        return retVal

    def VBDGetRecord(self, inVBD):
        self.RequireSession()

        vbdRecord = {}
        vbdRecord['opaqueref'] = inVBD
        
        return vbdRecord

    def CreateVBD(self, inVM, inVDI, inDeviceNum, inMode = None,  inType = None):
        self.RequireSession()
        
        vbd = {
            'VM' : inVM['opaqueref'],
            'VDI' : inVDI['opaqueref'], 
            'userdevice' : inDeviceNum, 
            'mode' : FirstValue(inMode, 'ro'),
            'bootable' : False, 
            'type' : FirstValue(inType, 'disk'), 
            'unpluggable' : True,
            'empty' : False, 
            'other_config' : { 'ovmconsole_tmp' : 'Created: '+time.asctime(time.gmtime()) }, 
            'qos_algorithm_type' : '', 
            'qos_algorithm_params' : {}
        }

        newVBD = None

        return self.VBDGetRecord(newVBD)
    
    def PlugVBD(self, inVBD):
        def TimedOp():
            pass
            
        TimeUtils.TimeoutWrapper(TimedOp, self.DISK_TIMEOUT_SECONDS)
        
        # Must reread to get filled-in device fieldcat 
        return self.VBDGetRecord(inVBD['opaqueref'])
        
    def UnplugVBD(self, inVBD):
        return None

    def DestroyVBD(self, inVBD):
        pass

    def PurgeVBDs(self):
        # Destroy any VBDs that ovmconsole created but isn't using
        
        vbdRefs = {} # Use a dict to remove duplicates
        
        # Iterate through all VBDs we know about
        for pbd in Data.Inst().host.PBDs([]):
            sr = pbd.get('SR', {})
            for vdi in sr.get('VDIs', []):
                for vbd in vdi.get('VBDs', []):
                    if 'ovmconsole_tmp' in vbd.get('other_config', {}):
                        vbdRefs[ vbd['opaqueref'] ] = vbd
        
        for vbd in vbdRefs.values():
            try:
                # Currently this won't destroy mounted VBDs
                if vbd['currently_attached']:
                    self.UnplugVBD(vbd)
                self.DestroyVBD(vbd)
            except Exception, e:
                ovmLogError('VBD purge failed', e)
    
    def IsXAPIRunning(self):
        try:
            if ShellPipe('/sbin/pidof', '-s',  '/opt/xensource/bin/xapi').CallRC() == 0:
                retVal = True
            else:
                retVal = False
        except:
            retVal = False
        return retVal
        
    def StopXAPI(self):
        if self.IsXAPIRunning():
            State.Inst().WeStoppedXAPISet(True)
            State.Inst().SaveIfRequired()        
            ShellPipe('/etc/init.d/xapi', 'stop').Call()
                
    def StartXAPI(self):
        if not self.IsXAPIRunning():
            ShellPipe('/etc/init.d/xapi', 'start').Call()
            State.Inst().WeStoppedXAPISet(False)
            State.Inst().SaveIfRequired()
    
    def EnableNTP(self):
        status, output = commands.getstatusoutput(
            "(export TERM=xterm && /sbin/chkconfig ntpd on && /etc/init.d/ntpd start)")
        if status != 0:
            raise Exception(output)
        
    def DisableNTP(self):
        status, output = commands.getstatusoutput(
            "(export TERM=xterm && /sbin/chkconfig ntpd off && /etc/init.d/ntpd stop)")
        if status != 0:
            raise Exception(output)

    def RestartNTP(self):
        status, output = commands.getstatusoutput("(export TERM=xterm && /etc/init.d/ntpd restart)")
        if status != 0:
            raise Exception(output)

    def NTPStatus(self):
        status, output = commands.getstatusoutput("/usr/bin/ntpstat")
        return output
            
    def SetVerboseBoot(self, inVerbose):
        if inVerbose:
            name = 'noisy'
        else:
            name = 'quiet'

        status, output = commands.getstatusoutput(
            "(export TERM=xterm && /opt/xensource/libexec/set-boot " + name + ")")
        if status != 0:
            raise Exception(output)
            
        State.Inst().VerboseBootSet(inVerbose)