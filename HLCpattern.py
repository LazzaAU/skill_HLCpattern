from pathlib import Path
import re
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class HLCpattern(AliceSkill):
	"""
	Author: lazza
	Description: Change between pre configured led light patterns of your devices.

	NOTE for future. If extra patterns are added in the future. Update line 20 and talk file
	line for the pointer on line 51 and also update line 60
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
		# re init some vars
		self._exitCode = False
		self._choosenPatternOption = 0
		# Path to the temporary file that we will edit initially
		self._hlcTempPath = f'{self.skillPath}/HermesledControl.service'

		# If there is no service file then exit
		if not self._hlcServiceFilePath.exists():
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text="dialogMessage1")
			)
			return

		# Check if user specified the pattern name
		if self.checkIfNameInUtterance(session):
			return

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
			# Capture those that can't listen or count
			if self._choosenPatternOption > 4 or self._choosenPatternOption < 0:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk(text="dialogMessage3")
				)
				return
		# Let user know Lights will be adjusted
		self.sayGoingToProceed(session)

		self.modifyHLCServiceFile()


	def checkIfNameInUtterance(self, session) -> bool:
		# If user has given the pattern to use in the intial utterance
		if 'namedPattern' in session.slots:
			namedPattern: str = session.slotValue('namedPattern')
			index = self._patternOptions.index(namedPattern.replace(' ', ''))
			self._choosenPatternOption = index

			self.sayGoingToProceed(session)

			self.modifyHLCServiceFile()
			return True
		else:
			return False


	def sayGoingToProceed(self, session):
		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text="dialogMessage4")
		)


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
			self._runSystemCommands()


	def checkExistingPattern(self, line):
		"""
		1. Cancel if the current pattern is the same as requested
		2. re.sub the new pattern to the current line
		"""
		for item in self._patternOptions:
			existingPattern = re.findall(f'--pattern={item}', line)
			if not existingPattern:
				continue

			newPatternChoice = f'--pattern={self._patternOptions[self._choosenPatternOption]}'
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


	def _runSystemCommands(self):

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
		""" Delete temporary file """
		self.Commons.runSystemCommand(f'rm -rf {self._hlcTempPath}'.split())
