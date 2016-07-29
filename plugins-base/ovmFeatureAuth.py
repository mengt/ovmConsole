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

class ChangePasswordDialogue(Dialogue):
	def __init__(self, inText = None,  inSuccessFunc = None):
		Dialogue.__init__(self)
		self.text = inText
		self.successFunc = inSuccessFunc
		self.isPasswordSet = Auth.Inst().IsPasswordSet()

		pane = self.NewPane(DialoguePane(self.parent))
		pane.TitleSet("Change Password")
		pane.AddBox()
		self.UpdateFields()
		if not self.isPasswordSet:
			pane.InputIndexSet(None) # Reactivate cursor if this dialogue is initially covered and revealed later
		
	def UpdateFields(self):
		pane = self.Pane()
		pane.ResetFields()
		if self.text is not None:
			pane.AddTitleField(self.text)
		if self.isPasswordSet:
			pane.AddPasswordField(Lang("Old Password", 21), Auth.Inst().DefaultPassword(), 'oldpassword')
		pane.AddPasswordField(Lang("New Password", 21), Auth.Inst().DefaultPassword(), 'newpassword1')
		pane.AddPasswordField(Lang("Repeat New Password", 21), Auth.Inst().DefaultPassword(), 'newpassword2')
		pane.AddKeyHelpField( {
			Lang("<Enter>") : Lang("Next/OK"),
			Lang("<Esc>") : Lang("Cancel"),
			Lang("<Tab>") : Lang("Next")
		})
		
		if pane.InputIndex() is None:
			pane.InputIndexSet(0) # Activate first field for input
		
	def HandleKey(self, inKey):
		handled = True
		pane = self.Pane()
		if inKey == 'KEY_ESCAPE':
			Layout.Inst().PopDialogue()
		elif inKey == 'KEY_ENTER':
			if not pane.IsLastInput():
				pane.ActivateNextInput()
			else:
				inputValues = pane.GetFieldValues()

				Layout.Inst().TransientBanner(Lang("Changing password..."))
				successMessage = Lang('Password Change Successful')
				try:
					if not Auth.Inst().IsAuthenticated() and self.isPasswordSet:
						# Log in automatically if we're not
						Auth.Inst().ProcessLogin('root', inputValues.get('oldpassword', ''))
						successMessage += Lang(".  User 'root' logged in.")
						
					if inputValues['newpassword1'] != inputValues['newpassword2']:
						raise Exception(Lang('New passwords do not match'))
					if len(inputValues['newpassword1']) < 6:
						raise Exception(Lang('New password is too short (minimum length is 6 characters)'))

					Auth.Inst().ChangePassword(inputValues.get('oldpassword', ''), inputValues['newpassword1'])
					
				except Exception, e:
					if self.isPasswordSet:
						# Only remove the dialogue if this isn't the initial password set (which needs to succeed)
						Layout.Inst().PopDialogue()
					else:
						# Disable the input field so that it gets reactivated by UpdateFields  when the info box is dismissed
						pane.InputIndexSet(None)
						
					Layout.Inst().PushDialogue(InfoDialogue(
						Lang('Password Change Failed: ')+Lang(e)))
					
				else:
					Layout.Inst().PushDialogue(InfoDialogue(successMessage))
					Layout.Inst().PopDialogue()
					State.Inst().PasswordChangeRequiredSet(False)
				Data.Inst().Update()

		elif inKey == 'KEY_TAB':
			pane.ActivateNextInput()
		elif inKey == 'KEY_BTAB':
			pane.ActivatePreviousInput()
		elif pane.CurrentInput().HandleKey(inKey):
			pass # Leave handled as True
		else:
			handled = False
		return True

class ovmFeatureChangePasswd:
	@classmethod
	def StatusUpdateHandler(cls, inPane):
		inPane.AddTitleField(Lang('Change Password'))
		inPane.AddWrappedTextField(Lang('Press <Enter> to change the password for root'))
		inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Change Password") })
		
	@classmethod
	def ActivateHandler(cls, *inParams):
		DialogueUtils.AuthenticatedOrPasswordUnsetOnly(lambda: Layout.Inst().PushDialogue(ChangePasswordDialogue(*inParams)))

	def Register(self):
		Importer.RegisterNamedPlugIn(
			self,
			'CHANGE_PASSWD',
			{
				'menuname' : 'MENU_AUTH',
				'menupriority' : 101,
				'menutext' : Lang('Change Password'),
				'statusupdatehandler' : ovmFeatureChangePasswd.StatusUpdateHandler,
				'activatehandler' : ovmFeatureChangePasswd.ActivateHandler
			}
		)


ovmFeatureLogInOut().Register()
ovmFeatureChangePasswd().Register()