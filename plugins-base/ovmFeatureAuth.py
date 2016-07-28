#!/usr/bin/env python
#-*-coding:utf-8-*-

from ovmConsoleStandard import *

class ovmFeatureLogInOut:

	@classmethod
	def StatusUpdateHandler(cls, inPane):
		'''更新状态窗口'''
		if Auth.Inst().IsAuthenticated():
			inPane.AddTitleField(Lang('Log Out'))
			inPane.AddWrappedTextField(Lang('Press <Enter> to log out'))
			inPane.AddKeyHelpField({Lang("Enter") : Lang("Log Out")})
		else:
			inPane.AddTitleField(Lang('Log In'))
			inPane.AddWrappedTextField(Lang('Press <Enter> to log in'))
			inPane.AddKeyHelpField({Lang("Enter") : Lang("Log In")})

	@classmethod
	def ActivateHandler(cls):
		'''事件点击事件'''
		if Auth.Inst().IsAuthenticated():
			name = Auth.Inst().LoggedInUsername()
			Auth.Inst().LogOut()
			Data.Inst().Update()
			Layout.Inst().PushDialogue(InfoDialogue( Lang("User '")+name+Lang("' logged out")))
		else:
			Layout.Inst().PushDialogue(LoginDialogue())

	def Register(self):
		'''使用此方法与主menu匹配,并绑定点击事件'''
		Importer.RegisterNamedPlugIn(
			self,
			'LOGINOUT',
			{
				'menuname' : 'MENU_AUTH',
				'menupriority' : 100,
				'menutext' : Lang('Log In/Out'),
				'statusupdatehandler' : ovmFeatureLogInOut.StatusUpdateHandler,
				'activatehandler' : ovmFeatureLogInOut.ActivateHandler
			}
		)



class ovmFeatureChangePasswd:
	@classmethod
	def StatusUpdateHandler(cls, inPane):
		inPane.AddTitleField(Lang('Change Password'))
		inPane.AddWrappedTextField(Lang('Press <Enter> to change the password for root'))
		inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Change Password") })
		
	@classmethod
	def ActivateHandler(cls, *inParams):
		pass
	def Register(self):
		Importer.RegisterNamedPlugIn(
			self,
			'CHANGE_PASSWD',
			{
				'menuname' : 'MENU_AUTH',
				'menupriority' : 101,
				'menutext' : Lang('Change Password'),
				'StatusUpdateHandler' : ovmFeatureChangePasswd.StatusUpdateHandler,
				'activatehandler' : ovmFeatureChangePasswd.ActivateHandler
			}
		)


ovmFeatureLogInOut().Register()
ovmFeatureChangePasswd().Register()