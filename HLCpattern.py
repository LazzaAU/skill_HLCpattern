
from pathlib import Path
import re
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class HLCpattern(AliceSkill):
	"""
	Author: lazza
	Description: Change between pre configured led light patterns of your devices.

	NOTE for future. If extra patterns are added in the future. Update line 20 and line talk file
	line for the pointer on line 42
	"""


	def __init__(self):
		self._hlcServiceFilePath = Path('/etc/systemd/system/hermesledcontrol.service')
		self._hlcTempPath = ""
		self._patternOptions = ["google", "alexa", "projectalice", "pgas", "kiboost"]
		self._choosenPatternOption = 0
		self._exitCode = False
		super().__init__()


	@IntentHandler('ChangeLedPattern')
	def ledPatternIntent(self, session: DialogSession, **_kwargs):
		# If there is no service file then exit
		if not self._hlcServiceFilePath.exists():
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text="dialogMessage1")
			)
			return

		# Path to the temporary file that we will edit initially
		self._hlcTempPath = f'{self.skillPath}/HermesledControl.service'

		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text="dialogMessage2"),
			intentFilter=['patternOption'],
			currentDialogState='UserChosePattern'
		)


	@IntentHandler(intent='patternOption', requiredState='UserChosePattern')
	def selectPatternOption(self, session: DialogSession):
		if 'number' in session.slots:
			self._choosenPatternOption = int(session.slotValue('number') - 1)
			if self._choosenPatternOption > 4 or self._choosenPatternOption < 0:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk(text="dialogMessage3")
				)
				return

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text="dialogMessage4")
		)

		self.modifyHLCServiceFile()


	def modifyHLCServiceFile(self):
		self.Commons.runSystemCommand(f'cp {self._hlcServiceFilePath} {self._hlcTempPath}'.split())

		# Read current service file data
		with open(self._hlcTempPath, 'r+') as file:
			originalData = file.read()

		# write new data to the temp file
		with open(self._hlcTempPath, 'w+') as file:
			newData = ""

			for line in originalData.split('\n'):
				if 'ExecStart=' in line:
					line = self.checkExistingPattern(line)
					newData = f'{newData}{line}\n'
				else:
					newData = f'{newData}{line}\n'

			file.write(newData)

		if not self._exitCode:
			self.copyBackInPlace()


	def checkExistingPattern(self, line):

		for item in self._patternOptions:
			existingPattern = re.findall(f'--pattern={item}', line)
			if not existingPattern:
				continue

			newPatternChoice = f'--pattern={self._patternOptions[self._choosenPatternOption]}'
			self.logInfo(f'Changing to {newPatternChoice} from {existingPattern[0]}')
			if existingPattern[0] == newPatternChoice:
				self.say(
					text=self.randomTalk(text="dialogMessage5")
				)
				self.cleanupTempFiles()
				self._exitCode = True
				break

			if existingPattern[0] in line:
				line = re.sub(existingPattern[0], newPatternChoice, line)
				return line


	def copyBackInPlace(self):

		self.logWarning('About to use sudo while doing the following operations...')
		self.Commons.runSystemCommand(f'sudo cp -rf {self._hlcTempPath} {self._hlcServiceFilePath}'.split())
		self.logInfo('Overwriting the existing HLC service file')
		self.Commons.runSystemCommand(f'sudo systemctl daemon-reload'.split())
		self.logInfo('I\'m now reloading system daemons')
		self.Commons.runSystemCommand(f'sudo systemctl restart hermesledcontrol'.split())
		self.logInfo(f'Now restarting the HLC service and removing temp files')
		self.cleanupTempFiles()

		self.say(
			text=self.randomTalk(text="dialogMessage6")
		)


	def cleanupTempFiles(self):
		self.Commons.runSystemCommand(f'rm -rf {self._hlcTempPath}'.split())
