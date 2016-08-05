#!/usr/bin/env python
#-*-coding:utf-8-*-  

from ovmConsoleStandard import *

#network info start
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