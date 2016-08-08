#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *

#network info start
class InterfaceDialogue(Dialogue):
    def __init__(self):
        Dialogue.__init__(self)
        data = Data.Inst()
        data.Update() # Pick up current 'connected' states
        choiceDefs = []

        self.nic=None
        self.converting = False
        self.currentPIF = {}
        choiceArray = []
        nic_dict, configured_nics, ntp_dhcp = data.get_system_nics()
        for key in sorted(nic_dict.iterkeys()):
            dev_interface,dev_bootproto,dev_vendor,dev_address,dev_driver,dev_conf_status,dev_bridge = nic_dict[key].split(",", 6)
            self.currentPIF[dev_interface]={'ip_configuration_mode':dev_bootproto,'IP':data.get_ip_address(dev_interface),'netmask':data.get_netmask(dev_interface),'gateway':data.get_gateway(dev_interface)}
            choiceName = dev_interface +": "+dev_vendor+" "

            if data.get_dev_status(dev_interface) != '(No connected)':
                choiceName += '('+Lang("connected")+')'
            else:
                choiceName += '('+Lang("not connected")+')'

            choiceDefs.append(ChoiceDef(choiceName, lambda: self.HandleNICChoice(self.nicMenu.ChoiceIndex())))
            

        if len(choiceDefs) == 0:
            ovmLog('Configure Management Interface found no device to present')
            choiceDefs.append(ChoiceDef(Lang("<No interfaces present>"), None))

        self.nicMenu = Menu(self, None, "Configure Management Interface", choiceDefs)
        
        self.modeMenu = Menu(self, None, Lang("Select IP Address Configuration Mode"), [
            ChoiceDef(Lang("DHCP"), lambda: self.HandleModeChoice('DHCP2') ), 
            ChoiceDef(Lang("Static"), lambda: self.HandleModeChoice('STATIC') )
            ])
        
        self.postDHCPMenu = Menu(self, None, Lang("Accept or Edit"), [
            ChoiceDef(Lang("Continue With DHCP Enabled"), lambda: self.HandlePostDHCPChoice('CONTINUE') ), 
            ChoiceDef(Lang("Convert to Static Addressing"), lambda: self.HandlePostDHCPChoice('CONVERT') ), 
            ])
        
        
        self.ChangeState('INITIAL')

        # Get best guess of current values
        self.mode = 'DHCP'
        self.IP = '0.0.0.0'
        self.netmask = '0.0.0.0'
        self.gateway = '0.0.0.0'

        # Make the menu current choices point to our best guess of current choices
        if self.nic is not None:
            self.nicMenu.CurrentChoiceSet(self.nic)
        if self.mode.lower().startswith('static'):
            self.modeMenu.CurrentChoiceSet(1)
        else:
            self.modeMenu.CurrentChoiceSet(0)
            
        if self.mode.lower().startswith('dhcp') and self.nic is not None:
            self.nicMenu.AddChoice(name = Lang('Renew DHCP Lease On Current Interface'),
                onAction = lambda: self.HandleRenewChoice()
                )
    
        self.ChangeState('INITIAL')
        
    def BuildPane(self):
        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Management Interface Configuration"))
        pane.AddBox()
        
    def UpdateFieldsINITIAL(self):
        pane = self.Pane()
        pane.ResetFields()
        
        pane.AddTitleField(Lang("Select NIC for Management Interface"))
        pane.AddMenuField(self.nicMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )

    def UpdateFieldsMODE(self):
        pane = self.Pane()
        pane.ResetFields()
        
        pane.AddTitleField(Lang("Select DHCP or static IP address configuration"))
        pane.AddMenuField(self.modeMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )
        
    def UpdateFieldsSTATICIP(self):
        pane = self.Pane()
        pane.ResetFields()
        if self.converting:
            pane.AddTitleField(Lang("Please confirm or edit the static IP configuration"))
        else:
            pane.AddTitleField(Lang("Enter static IP address configuration"))
        pane.AddInputField(Lang("IP Address",  14),  self.currentPIF['eth'+str(self.nic)]['IP'], 'IP')
        pane.AddInputField(Lang("Netmask",  14),  self.currentPIF['eth'+str(self.nic)]['netmask'], 'netmask')
        pane.AddInputField(Lang("Gateway",  14),  self.currentPIF['eth'+str(self.nic)]['gateway'], 'gateway')
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )
        if pane.InputIndex() is None:
            pane.InputIndexSet(0) # Activate first field for input

    def UpdateFieldsPRECOMMIT(self):
        pane = self.Pane()
        pane.ResetFields()
        
        pane.AddTitleField(Lang("Press <Enter> to apply the following configuration"))
        
        if self.nic is None:
            pane.AddWrappedTextField(Lang("The Management Interface will be disabled"))
        else:
            #pif = Data.Inst().host.PIFs()[self.nic]
            pane.AddStatusField(Lang("Device",  16),  self.nic)
            pane.AddStatusField(Lang("Name",  16),  "pif['metrics']['device_name']")
            pane.AddStatusField(Lang("IP Mode",  16),  self.mode)
            if self.mode == 'Static':
                pane.AddStatusField(Lang("IP Address",  16),  self.currentPIF['eth'+str(self.nic)]['IP'])
                pane.AddStatusField(Lang("Netmask",  16),  self.currentPIF['eth'+str(self.nic)]['netmask'])
                pane.AddStatusField(Lang("Gateway",  16),  self.currentPIF['eth'+str(self.nic)]['gateway'])
                      
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )
        
    def UpdateFieldsPOSTDHCP(self):
        pane = self.Pane()
        pane.ResetFields()
   
        pane.AddWrappedBoldTextField(Lang("The following addresses have been assigned by DHCP.  Would you like to accept them and continue with DHCP enabled, or convert to a static configuration?"))
        pane.NewLine()
        
        if self.nic is None:
            pane.AddWrappedTextField(Lang("<No interface configured>"))
        else:
            pif = Data.Inst().host.PIFs()[self.nic]
            pane.AddStatusField(Lang("Device",  16),  pif['device'])
            pane.AddStatusField(Lang("Name",  16),  pif['metrics']['device_name'])
            pane.AddStatusField(Lang("IP Address",  16),  self.currentPIF['eth'+str(self.nic)]['IP'])
            pane.AddStatusField(Lang("Netmask",  16),  self.currentPIF['eth'+str(self.nic)]['netmask'])
            pane.AddStatusField(Lang("Gateway",  16),  self.currentPIF['eth'+str(self.nic)]['gateway'])
        pane.NewLine()
        pane.AddMenuField(self.postDHCPMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )
    

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, 'UpdateFields'+self.state)() # Despatch method named 'UpdateFields'+self.state
    
    def ChangeState(self, inState):
        self.state = inState
        self.BuildPane()
        self.UpdateFields()
                            
    def HandleKeyINITIAL(self, inKey):
        return self.nicMenu.HandleKey(inKey)

    def HandleKeyMODE(self, inKey):
        return self.modeMenu.HandleKey(inKey)

    def HandleKeySTATICIP(self, inKey):
        handled = True
        pane = self.Pane()
        if inKey == 'KEY_ENTER':
            if pane.IsLastInput():
                inputValues = pane.GetFieldValues()
                self.IP = inputValues['IP']
                self.netmask = inputValues['netmask']
                self.gateway = inputValues['gateway']
                #self.hostname = inputValues['hostname']
                try:
                    failedName = Lang('IP Address')
                    IPUtils.AssertValidIP(self.IP)
                    failedName = Lang('Netmask')
                    IPUtils.AssertValidNetmask(self.netmask)
                    failedName = Lang('Gateway')
                    IPUtils.AssertValidIP(self.gateway)
                    failedName = Lang('Hostname')
                    #IPUtils.AssertValidNetworkName(self.hostname)
                    self.ChangeState('PRECOMMIT')
                except:
                    pane.InputIndexSet(None)
                    Layout.Inst().PushDialogue(InfoDialogue(Lang('Invalid ')+failedName))

            else:
                pane.ActivateNextInput()
        elif inKey == 'KEY_TAB':
            pane.ActivateNextInput()
        elif inKey == 'KEY_BTAB':
            pane.ActivatePreviousInput()
        elif pane.CurrentInput().HandleKey(inKey):
            pass # Leave handled as True
        else:
            handled = False
        return handled


    def HandleKeyPRECOMMIT(self, inKey):
        handled = True
        pane = self.Pane()
        if inKey == 'KEY_ENTER':
            Layout.Inst().TransientBanner( Lang("Reconfiguring network..."))
            try:
                self.Commit()
                if self.mode == 'DHCP':
                    data = Data.Inst()
                    self.IP = data.ManagementIP()
                    self.netmask = data.ManagementNetmask()
                    self.gateway = data.ManagementGateway()
                    self.ChangeState('POSTDHCP')
                elif self.nic != None:
                    # Not disabling, so show post-hostname dialogue
                    self.ChangeState('POSTHOSTNAME')
                else:
                    self.Complete() # Disabled management interface
                
            except Exception, e:
                self.Complete(Lang("Configuration Failed: "+Lang(e)))
                
        else:
            handled = False
        return handled
    
    def HandleKeyPOSTDHCP(self, inKey):
        return self.postDHCPMenu.HandleKey(inKey)
    
    def HandleKeyPOSTHOSTNAME(self, inKey):
        return self.postHostnameMenu.HandleKey(inKey)
    
    def HandleKeyNAMELABEL(self, inKey):
        handled = True
        pane = self.Pane()
        if inKey == 'KEY_ENTER':
            inputValues = pane.GetFieldValues()
            nameLabel = inputValues['namelabel']
            try:
                Data.Inst().NameLabelSet(nameLabel)
                self.Complete()
            except Exception, e:
                self.Complete(Lang("Name Change Failed: ")+str(e))

        elif pane.CurrentInput().HandleKey(inKey):
            pass # Leave handled as True
        else:
            handled = False
        return handled
    
    def HandleKey(self,  inKey):
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)
        
        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled
            
    def HandleNICChoice(self,  inChoice):
        self.nic = inChoice
        if self.nic is None:
            self.ChangeState('PRECOMMIT')
        else:
            self.ChangeState('MODE')
        
    def HandleModeChoice(self,  inChoice):
        self.hostname = ''
        if inChoice == 'DHCP2': # DHCP with DHCP-assigned hostname
            self.mode = 'DHCP'
            self.ChangeState('PRECOMMIT')
        elif inChoice == 'DHCPMANUAL': # DHCP with manually assigned hostname
            self.mode = 'DHCP'
            self.ChangeState('HOSTNAME')
        elif inChoice == 'STATIC':
            #self.hostname = Data.Inst().host.hostname('')
            self.mode = 'Static'
            self.ChangeState('STATICIP')

    def HandlePostDHCPChoice(self,  inChoice):
        if inChoice == 'CONTINUE':
            self.ChangeState('POSTHOSTNAME')
        elif inChoice == 'CONVERT':
            self.converting = True
            self.mode = 'Static'
            self.ChangeState('STATICIP')

    def HandlePostHostnameChoice(self,  inChoice):
        data = Data.Inst()
        if inChoice == 'COPY':
            #data.NameLabelSet(data.host.hostname(''))
            self.Complete() # We're done
        elif inChoice == 'KEEP':
            self.Complete() # We're done
        elif inChoice == 'NEW':
            self.ChangeState('NAMELABEL')

    def HandleRenewChoice(self):
        data = Data.Inst()
        pif = data.host.PIFs()[self.nic]
        
        Layout.Inst().PopDialogue()
        Layout.Inst().TransientBanner(Lang('Renewing DHCP Lease...'))
        
        try:
            data.ReconfigureManagement(pif, 'DHCP', '', '', '')
            data.Update()
            ipAddress = data.host.address('')
            if ipAddress == '':
                # Try again using disable/reenable
                data.DisableManagement()
                data.ReconfigureManagement(pif, 'DHCP', '', '', '')
                data.Update()
                ipAddress = data.host.address('')
            if ipAddress == '':
                ipAddress = Lang('<Unknown>')
            Layout.Inst().PushDialogue(InfoDialogue(Lang("DHCP Renewed with IP address ")+ipAddress))
        except Exception, e:
            Layout.Inst().PushDialogue(InfoDialogue(Lang("Renewal Failed"), Lang(e)))
            
    def Commit(self):
        data = Data.Inst()
        if self.nic is None:
            self.mode = None
            data.DisableManagement()
        else:
            pif = data.host.PIFs()[self.nic]
            if self.mode.lower().startswith('static'):
                # Comma-separated list of nameserver IPs
                dns = ','.join(data.dns.nameservers([]))
            else:
                dns = ''
                
            # Operation of the dhclient-script is:
            # If the current hostname from bin/hostname is '(none)', 'localhost' or 'localhost.localdomain',
            # get the hostname from DHCP, otherwise keep the current hostname.  So we set the hostname
            # here to control the action of DHCP when ReconfigureManagement runs
            # if self.hostname == '':
            #      # DHCP will override if the DHCP server offers a hostname, otherwise we'll keep this one
            #     data.HostnameSet('localhost')
            # else:                
            #     data.HostnameSet(self.hostname)
            data.ReconfigureManagement(pif, self.mode, self.IP,  self.netmask, self.gateway, dns)
        data.Update()
        #self.hostname = data.host.hostname('') # Hostname may have changed.  Must be after data.Update()

    def Complete(self, inMessage = None):
        Layout.Inst().PopDialogue()
        Layout.Inst().PushDialogue(InfoDialogue(FirstValue(inMessage, Lang("Network Configuration Successful"))))

class ovmFeatureNetworkInfo:
    '''展示网络信息'''
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        
        inPane.AddTitleField(Lang("Configure Management Interface"))
        
        nic_dict, configured_nics, ntp_dhcp = data.get_system_nics()
        if len(nic_dict) == 0:
            inPane.AddWrappedTextField(Lang("<No interface configured>"))
        else:
            for key in sorted(nic_dict.iterkeys()):
                dev_interface,dev_bootproto,dev_vendor,dev_address,dev_driver,dev_conf_status,dev_bridge = nic_dict[key].split(",", 6)
                if data.get_dev_status(dev_interface) != '(No connected)':
                    inPane.AddStatusField(Lang('Device', 16), dev_interface)
                    inPane.AddStatusField(Lang('MAC Address', 16),  dev_address)
                    inPane.AddStatusField(Lang('DHCP/Static IP', 16),  dev_bootproto)
                    inPane.AddStatusField(Lang('IP address', 16), data.get_ip_address(dev_interface))
                    inPane.AddStatusField(Lang('Netmask', 16),  data.get_netmask(dev_interface))
                    inPane.AddStatusField(Lang('Gateway', 16),  data.get_gateway(dev_interface))
                else:
                    inPane.AddStatusField(Lang('Device', 16), dev_interface)
                    inPane.AddStatusField(Lang('Status', 16),  '(No connected)')
                # inPane.AddTitleField(Lang("NIC Model"))
                # inPane.AddWrappedTextField(pif['metrics']['device_name'])
                inPane.AddWrappedTextField(Lang("---"))
        inPane.AddKeyHelpField( {
            Lang("<Enter>") : Lang("Reconfigure"),
            Lang("<F5>") : Lang("Refresh")
        } )

    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(InterfaceDialogue()))
        #pass
      
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
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

#network info end

class TestNetworkDialogue(Dialogue):
    def __init__(self):
        Dialogue.__init__(self)

        pane = self.NewPane(DialoguePane(self.parent))
        pane.TitleSet(Lang("Test Network Configuration"))
        pane.AddBox()
        
        gatewayName = Data.Inst().ManagementGateway()
        if gatewayName is None:
            gatewayName = Lang('Unknown')
        
        self.testMenu = Menu(self, None, Lang("Select Test Type"), [
            ChoiceDef(Lang("Ping local address 127.0.0.1"), lambda: self.HandleTestChoice('local') ), 
            #if Data.Inst().ManagementGateway() != '':
            ChoiceDef(Lang("Ping gateway address")+" ("+gatewayName+")", lambda: self.HandleTestChoice('gateway') ), 
            ChoiceDef(Lang("Ping www.kernel.org"), lambda: self.HandleTestChoice('fixedserver') ), 
            ChoiceDef(Lang("Ping custom address"), lambda: self.HandleTestChoice('custom') ), 
            ])
    
        self.customIP = '0.0.0.0'
        self.state = 'INITIAL'
    
        self.UpdateFields()

    def UpdateFields(self):
        self.Pane().ResetPosition()
        getattr(self, 'UpdateFields'+self.state)() # Despatch method named 'UpdateFields'+self.state
        
    def UpdateFieldsINITIAL(self):
        pane = self.Pane()
        pane.ResetFields()
        
        pane.AddTitleField(Lang("Select Test"))
        pane.AddMenuField(self.testMenu)
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Cancel") } )
        
    def UpdateFieldsCUSTOM(self):
        pane = self.Pane()
        pane.ResetFields()
        
        pane.AddTitleField(Lang("Enter hostname or IP address to ping"))
        pane.AddInputField(Lang("Address",  16), self.customIP, 'address')
        pane.AddKeyHelpField( { Lang("<Enter>") : Lang("OK"), Lang("<Esc>") : Lang("Exit") } )
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)
            
    def HandleKey(self, inKey):
        handled = False
        if hasattr(self, 'HandleKey'+self.state):
            handled = getattr(self, 'HandleKey'+self.state)(inKey)
        
        if not handled and inKey == 'KEY_ESCAPE':
            Layout.Inst().PopDialogue()
            handled = True

        return handled
        
    def HandleKeyINITIAL(self, inKey):
        handled = self.testMenu.HandleKey(inKey)
        if not handled and inKey == 'KEY_LEFT':
            Layout.Inst().PopDialogue()
            handled = True
        return handled
        
    def HandleKeyCUSTOM(self, inKey):
        handled = True
        pane = self.Pane()
        if pane.CurrentInput() is None:
            pane.InputIndexSet(0)
        if inKey == 'KEY_ENTER':
            inputValues = pane.GetFieldValues()
            self.customIP = inputValues['address']
            self.DoPing(self.customIP)
            self.state = 'INITIAL'
            
        elif pane.CurrentInput().HandleKey(inKey):
            pass # Leave handled as True
        else:
            handled = False
        return handled
        
    def HandleTestChoice(self,  inChoice):
        pingTarget = None
        custom = False
        if inChoice == 'local':
            pingTarget = '127.0.0.1'
        elif inChoice == 'gateway':
            pingTarget = Data.Inst().ManagementGateway()
        elif inChoice == 'fixedserver':
            pingTarget = 'www.kernel.org'
        else:
            custom = True

        if custom:
            self.state = 'CUSTOM'
            self.UpdateFields()
            self.Pane().InputIndexSet(0)
        else:
            self.DoPing(pingTarget)

    def DoPing(self, inAddress):
        success = False
        output = 'Cannot determine address to ping'
            
        if inAddress is not None:
            try:
                Layout.Inst().TransientBanner(Lang('Pinging...'))
                (success,  output) = Data.Inst().Ping(inAddress)
            except Exception,  e:
                output = Lang(e)
            
        if success:
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Ping successful"), output))
        else:
            ovmLogFailure('Ping failed ', str(output))
            Layout.Inst().PushDialogue(InfoDialogue( Lang("Ping failed"), output))




#NDS info start
class ovmFeatureDNS:
    '''展示DNS信息'''
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("DNS Servers"))
    
        inPane.AddTitleField(Lang("Current Nameservers"))
        dnslist = data.readdnsconf(r'/etc/resolv.conf')
        if len(dnslist) == 0:
            inPane.AddWrappedTextField(Lang("<No nameservers are configured>"))
        for dns in dnslist:
            inPane.AddWrappedTextField(str(dns))
        inPane.NewLine()
        inPane.AddKeyHelpField( {
            Lang("<F5>") : Lang("Refresh")
        })

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'DNS', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Display DNS Servers'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 101,
                'menutext' : Lang('Display DNS Servers') ,
                'statusupdatehandler' : self.StatusUpdateHandler
            }
        )

#NDS info end


# test network start
class ovmFeatureTestNetwork:
    '''测试网络'''
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Test Network"))
    
        inPane.AddWrappedTextField(Lang(
            "This option will test the configured network using ping."))
        
        inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Test Network") })
        
    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(TestNetworkDialogue()))

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'TEST_NETWORK', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Test Network'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 102,
                'menutext' : Lang('Test Network') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

#test network  end

#set NTP start

class NTPInputDialogue(InputDialogue):
    def __init__(self):
        self.ntplist = Data().Inst().readntpconf(r'/etc/ntp.conf')
        self.custom = {
            'title' : Lang("Set NTP Address"),
            'info' : Lang("Please Enter the NTP Server Name or Address"), 
            'fields' : [ [Lang("NTP address", 20),'', 'ntp1'],[Lang("NTP address", 20),'', 'ntp2']]
            }
        InputDialogue.__init__(self)

    def HandleCommit(self, inValues):
        D_def = Data.Inst()
        if D_def.updateNtpConf(inValues):
            Data.Inst().Update()
            return Lang('Set NTP Successful'),'Please reboot the server'
        else:
            return Lang("Set NTP"),"Error"


# Layout.Inst().PopDialogue()
class ovmFeatureNTP:
    '''展示ntp信息'''
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data().Inst()
        inPane.AddTitleField(Lang('Server NTP'))
        for i in data.data['ntp']['servers']:
            inPane.AddWrappedTextField(Lang(i))
        inPane.NewLine()
        inPane.AddWrappedTextField(Lang('Add an NTP Server,Can specify up to two.'))
        inPane.AddKeyHelpField({Lang("F5") : Lang("Refresh")})   
        
    @classmethod
    def ActivateHandler(cls):
        Layout.Inst().PushDialogue(NTPInputDialogue())
        #DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(NTPDialogue()))

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'NTP', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Network Time (NTP)'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 103,
                'menutext' : Lang('Network Time (NTP)') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

#set NTP end

#NICs info start
class ovmFeatureDisplayNICs:
    '''展示网络信息'''

    @classmethod
    def StatusUpdateHandler(cls, inPane):
        try:
            data = Data.Inst()
            inPane.AddTitleField(Lang("Network Interfaces"))
            nic_dict, configured_nics, ntp_dhcp = data.get_system_nics()
            for key in sorted(nic_dict.iterkeys()):
                dev_interface,dev_bootproto,dev_vendor,dev_address,dev_driver,dev_conf_status,dev_bridge = nic_dict[key].split(",", 6)
                inPane.AddWrappedBoldTextField(dev_interface)
                inPane.AddWrappedTextField(Lang(data.get_dev_status(dev_interface)))
                inPane.AddStatusField(Lang("MAC Address", 16), dev_address)
                inPane.AddStatusField(Lang("Device", 16), dev_vendor)
                inPane.NewLine()
        except Exception, e:
            raise e
        
    @classmethod
    def ActivateHandler(cls):
        pass

    def Register(self):
        
        Importer.RegisterNamedPlugIn(
            self,
            'DISPLAY_NICS', # Key of this plugin for replacement, etc.
            {
                'title' : Lang('Display NICs'), # Name of this plugin for plugin list
                'menuname' : 'MENU_NETWORK',
                'menupriority' : 104,
                'menutext' : Lang('Display NICs') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

#NICs info end


# Register this plugin when module is imported
ovmFeatureNetworkInfo().Register()
ovmFeatureDNS().Register()
ovmFeatureTestNetwork().Register()
ovmFeatureNTP().Register()
ovmFeatureDisplayNICs().Register()