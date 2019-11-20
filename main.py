#!/usr/bin/env python
#
# Simple manager prototype for xqemu
#
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QMessageBox
from PyQt5.uic import loadUiType
from PyQt5 import QtCore, QtGui
from qmp import QEMUMonitorProtocol
import sys
import os, os.path
import json
import time
import platform

SETTINGS_FILE = './settings.json'

# Load UI files
settings_class, _ = loadUiType('settings.ui')
mainwindow_class, _ = loadUiType('mainwindow.ui')

class SettingsManager(object):
	def __init__(self):
		self.reset()

	def reset(self):
		self.settings = {
			'xqemu_path': '/path/to/xqemu',
			'mcpx_path': '/path/to/mcpx.bin',
			'flash_path': '/path/to/flash.bin',
			'hdd_path': '/path/to/hdd.img',
			'hdd_locked': True,
			'dvd_present': True,
			'dvd_path': '/path/to/disc.iso',
			'short_anim': False,
			'sys_memory': '64 MiB',
			'use_accelerator': False,
			'gdb_enabled': False,
			'gdb_wait': False,
			'gdb_port': '1234',
			'controller_one': 'Not connected',
			'controller_two': 'Not connected',
			'controller_three': 'Not connected',
			'controller_four': 'Not connected',
			'xmu_1a_path': '',
			'xmu_1b_path': '',
			'xmu_2a_path': '',
			'xmu_2b_path': '',
			'xmu_3a_path': '',
			'xmu_3b_path': '',
			'xmu_4a_path': '',
			'xmu_4b_path': '',
			'extra_args': '',
		}

	def save(self):
		with open(SETTINGS_FILE, 'w') as f:
			f.write(json.dumps(self.settings, indent=2))

	def load(self):
		if os.path.exists(SETTINGS_FILE):
			with open(SETTINGS_FILE, 'r') as f:
				d = f.read()
			self.settings = json.loads(d)
		else:
			self.reset()

class SettingsWindow(QDialog, settings_class):
	def __init__(self, settings, *args):
		super(SettingsWindow, self).__init__(*args)
		self.settings = settings
		self.setupUi(self)

		# Little helper functions to hook up the gui to the model
		def setTextAttr(widget, var): self.settings.settings[var] = widget.text()
		def getTextAttr(widget, var): widget.setText(self.settings.settings[var])
		def setCheckAttr(widget, var): self.settings.settings[var] = widget.isChecked()
		def getCheckAttr(widget, var): widget.setChecked(self.settings.settings[var])
		def setDropdownAttr(widget, var): self.settings.settings[var] = widget.currentText()
		def getDropdownAttr(widget, var): widget.setCurrentText(self.settings.settings[var])
		def updateLaunchCmd(): self.invocationPreview.setPlainText(Xqemu.launchCmdToString(Xqemu.generateLaunchCmd(self.settings, True)))

		def updateControllerUi():
			# Update all four controllers
			for i in [1, 2, 3, 4]:
				controller = getattr(self, 'controller' + str(i))
				is_connected = (controller.currentIndex() != 0)
				group = getattr(self, 'controller' + str(i) + 'Additional')
				group.setEnabled(is_connected)

		def bindTextWidget(widget, var):
			getTextAttr(widget, var)
			widget.textChanged.connect(lambda:setTextAttr(widget, var))
			widget.textChanged.connect(updateLaunchCmd)

		def bindCheckWidget(widget, var):
			getCheckAttr(widget, var)
			widget.stateChanged.connect(lambda:setCheckAttr(widget, var))
			widget.stateChanged.connect(updateLaunchCmd)

		def bindFilePicker(button, text):
			button.clicked.connect(lambda:self.setSaveFileName(text))

		def bindDropdownWidget(widget, var):
			getDropdownAttr(widget, var)
			widget.currentIndexChanged.connect(lambda:setDropdownAttr(widget, var))
			widget.currentIndexChanged.connect(updateLaunchCmd)

		bindTextWidget(self.xqemuPath, 'xqemu_path')
		bindFilePicker(self.setXqemuPath, self.xqemuPath)
		bindCheckWidget(self.useShortBootAnim, 'short_anim')
		bindCheckWidget(self.dvdPresent, 'dvd_present')
		bindTextWidget(self.dvdPath, 'dvd_path')
		bindFilePicker(self.setDvdPath, self.dvdPath)
		bindTextWidget(self.mcpxPath, 'mcpx_path')
		bindFilePicker(self.setMcpxPath, self.mcpxPath)
		bindTextWidget(self.flashPath, 'flash_path')
		bindFilePicker(self.setFlashPath, self.flashPath)
		bindTextWidget(self.hddPath, 'hdd_path')
		bindFilePicker(self.setHddPath, self.hddPath)
		bindCheckWidget(self.hddLocked, 'hdd_locked')
		bindDropdownWidget(self.systemMemory, 'sys_memory')
		bindCheckWidget(self.useAccelerator, 'use_accelerator')
		bindDropdownWidget(self.controller1, 'controller_one')
		bindDropdownWidget(self.controller2, 'controller_two')
		bindDropdownWidget(self.controller3, 'controller_three')
		bindDropdownWidget(self.controller4, 'controller_four')
		bindFilePicker(self.setXmu1A, self.xmu1APath)
		bindTextWidget(self.xmu1APath, 'xmu_1a_path')
		bindFilePicker(self.setXmu1B, self.xmu1BPath)
		bindTextWidget(self.xmu1BPath, 'xmu_1b_path')
		bindFilePicker(self.setXmu2A, self.xmu2APath)
		bindTextWidget(self.xmu2APath, 'xmu_2a_path')
		bindFilePicker(self.setXmu2B, self.xmu2BPath)
		bindTextWidget(self.xmu2BPath, 'xmu_2b_path')
		bindFilePicker(self.setXmu3A, self.xmu3APath)
		bindTextWidget(self.xmu3APath, 'xmu_3a_path')
		bindFilePicker(self.setXmu3B, self.xmu3BPath)
		bindTextWidget(self.xmu3BPath, 'xmu_3b_path')
		bindFilePicker(self.setXmu4A, self.xmu4APath)
		bindTextWidget(self.xmu4APath, 'xmu_4a_path')
		bindFilePicker(self.setXmu4B, self.xmu4BPath)
		bindTextWidget(self.xmu4BPath, 'xmu_4b_path')
		bindCheckWidget(self.gdbEnabled, 'gdb_enabled')
		bindCheckWidget(self.waitForGdb, 'gdb_wait')
		bindTextWidget(self.gdbPort, 'gdb_port')
		bindTextWidget(self.additionalArgs, 'extra_args')
		
		# Controller UI has additional logic
		self.controller1.currentIndexChanged.connect(updateControllerUi)
		self.controller2.currentIndexChanged.connect(updateControllerUi)
		self.controller3.currentIndexChanged.connect(updateControllerUi)
		self.controller4.currentIndexChanged.connect(updateControllerUi)
		
		# Prepare initial UI state
		updateLaunchCmd()
		updateControllerUi()

	def setSaveFileName(self, obj):
		options = QFileDialog.Options()
		fileName, _ = QFileDialog.getOpenFileName(self,
				"Select File",
				obj.text(),
				"All Files (*)", options=options)
		if fileName:
			obj.setText(fileName)

class Xqemu(object):
	def __init__(self):
		self._p = QtCore.QProcess()
		self._qmp = None

	@staticmethod
	def generateControllerArg(settings):
		def genArg(settings, name, port):
			arg = {'Not connected': '',
			 'Keyboard': 'usb-xbox-gamepad',
			 'Gamepad #0': 'usb-xbox-gamepad-sdl,index=0',
			 'Gamepad #1': 'usb-xbox-gamepad-sdl,index=1',
			 'Gamepad #2': 'usb-xbox-gamepad-sdl,index=2',
			 'Gamepad #3': 'usb-xbox-gamepad-sdl,index=3'}.get(settings.settings[name], '')
			if arg != '':
				return ['-device', 'usb-hub,port=' + str(port), '-device'] + [arg + ',port=' + str(port) + ".1"]
			return []

		args = []
		for controller in zip([3, 4, 1, 2], ['controller_one', 'controller_two', 'controller_three', 'controller_four']):
			args += genArg(settings, controller[1], controller[0])
		return args

	@staticmethod
	def generateXmuArg(settings, skipPathChecks):
		def check_path(path):
			if not skipPathChecks:
				if not os.path.exists(path) or os.path.isdir(path):
					raise Exception('File %s could not be found!' % path)

		def escape_path(path):
			return path.replace(',', ',,')

		def genArg(settings, name, port):
			port_arr = ['controller_three', 'controller_four', 'controller_one', 'controller_two']
			if settings.settings[name] != '' and settings.settings[port_arr[int(port[:1]) - 1]] != 'Not connected':
				check_path(settings.settings[name])
				return ['-drive', 'if=none,id=' + name + ',file=' + escape_path(settings.settings[name]),
						'-device', 'usb-storage,drive=' + name + ',port=' + port]
			return []

		args = []
		for xmu in zip([1, 2, 3, 4], [3, 4, 1, 2]):
			args += genArg(settings, 'xmu_' + str(xmu[0]) + 'a_path', str(xmu[1]) + '.2')
			args += genArg(settings, 'xmu_' + str(xmu[0]) + 'b_path', str(xmu[1]) + '.3')
		return args

	@staticmethod
	def generateLaunchCmd(settings, skipPathChecks=False):
		def check_path(path):
			if not skipPathChecks:
				if not os.path.exists(path) or os.path.isdir(path):
					raise Exception('File %s could not be found!' % path)

		def escape_path(path):
			return path.replace(',', ',,')

		xqemu_path = settings.settings['xqemu_path']
		check_path(xqemu_path)
		mcpx_path = settings.settings['mcpx_path']
		check_path(mcpx_path)
		mcpx_path_arg = escape_path(mcpx_path)
		flash_path = settings.settings['flash_path']
		check_path(flash_path)
		flash_path_arg = escape_path(flash_path)
		hdd_path = settings.settings['hdd_path']
		check_path(hdd_path)
		hdd_path_arg = escape_path(hdd_path)
		short_anim_arg = ',short_animation' if settings.settings['short_anim'] else ''
		hdd_lock_arg = ',locked' if settings.settings['hdd_locked'] else ''
		sys_memory = settings.settings['sys_memory'].split(' ')[0]+'M'
		accel_arg = ',accel=kvm:hax:whpx,kernel_irqchip=off' if settings.settings['use_accelerator'] else ''
		dvd_path_arg = ''
		if settings.settings['dvd_present']:
			check_path(settings.settings['dvd_path'])
			dvd_path_arg = ',file=' + escape_path(settings.settings['dvd_path'])

		extra_args = [x for x in settings.settings['extra_args'].split(' ') if x != '']

		# Build qemu launch cmd
		cmd = [xqemu_path,
		       '-cpu','pentium3',
		       '-machine','xbox%(accel_arg)s,bootrom=%(mcpx_path_arg)s%(short_anim_arg)s' % locals(),
		       '-m', '%(sys_memory)s' % locals(),
		       '-bios', '%(flash_path_arg)s' % locals(),
		       '-drive','file=%(hdd_path_arg)s,index=0,media=disk%(hdd_lock_arg)s' % locals(),
		       '-drive','index=1,media=cdrom%(dvd_path_arg)s' % locals(),
		       '-qmp','tcp:localhost:4444,server,nowait',
		       '-display','sdl']

		cmd += Xqemu.generateControllerArg(settings)
		cmd += Xqemu.generateXmuArg(settings, skipPathChecks)

		if settings.settings['gdb_enabled']:
			cmd.append('-gdb')
			cmd.append('tcp::' + settings.settings['gdb_port'])
			if settings.settings['gdb_wait']:
				cmd.append('-S')

		cmd += extra_args

		return cmd

	@staticmethod
	def launchCmdToString(cmd):
		# Attempt to interpret the constructed command line
		cmd_escaped = []
		for cmd_part in cmd:
			if ' ' in cmd_part:
				cmd_escaped += ['"%s"' % cmd_part.replace('"', '\\"')]
			else:
				cmd_escaped += [cmd_part]

		return ' '.join(cmd_escaped)

	def start(self, settings):
		cmd = self.generateLaunchCmd(settings)
		cmd_string = self.launchCmdToString(cmd)

		print('Running: %s' % cmd_string)

		self._p.start(cmd_string)
		i = 0
		while True:
			print('Trying to connect %d' % i)
			if i > 0: time.sleep(1)
			try:
				self._qmp = QEMUMonitorProtocol(('localhost', 4444))
				self._qmp.connect()
			except Exception as e:
				# If XQEMU quits, we abort the loop
				if self._p.waitForFinished(1):
					return

				if i > 4:
					raise
				else:
					i += 1
					continue
			break

	def stop(self):
		if self.isRunning:
			self._p.terminate()

	def run_cmd(self, cmd):
		if type(cmd) is str:
			cmd = {
			    "execute": cmd, 
			    "arguments": {}
			}
		resp = self._qmp.cmd_obj(cmd)
		if resp is None:
			raise Exception('Disconnected!')
		return resp

	def pause(self):
		return self.run_cmd('stop')

	def cont(self):
		return self.run_cmd('cont')

	def restart(self):
		return self.run_cmd('system_reset')

	def screenshot(self):
		cmd = {
		    "execute": "screendump", 
		    "arguments": {
		        "filename": "screenshot.ppm"
		    }
		}
		return self.run_cmd(cmd)

	def isPaused(self):
		resp = self.run_cmd('query-status')
		return resp['return']['status'] == 'paused'

	@property
	def isRunning(self):
		return self._p is not None and self._p.state() == QtCore.QProcess.Running

class MainWindow(QMainWindow, mainwindow_class):
	def __init__(self, *args):
		super(MainWindow, self).__init__(*args)
		self.setupUi(self)
		self.inst = Xqemu()
		self.settings = SettingsManager()
		self.settings.load()
		self.runButton.setText('Start')
		self.pauseButton.setText('Pause')
		self.screenshotButton.setText('Screenshot')

		# Connect signals
		self.runButton.clicked.connect(self.onRunButtonClicked)
		self.pauseButton.clicked.connect(self.onPauseButtonClicked)
		self.screenshotButton.clicked.connect(self.onScreenshotButtonClicked)
		self.restartButton.clicked.connect(self.onRestartButtonClicked)
		self.actionExit.triggered.connect(self.onExitClicked)
		self.actionSettings.triggered.connect(self.onSettingsClicked)
		self.inst._p.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
		self.inst._p.readyReadStandardError.connect(self.onReadyReadStandardError)
		self.inst._p.stateChanged.connect(self.onXqemuStateChanged)

	def onReadyReadStandardOutput(self):
		text = self.inst._p.readAllStandardOutput().data().decode()
		self.log.moveCursor(QtGui.QTextCursor.End)
		self.log.insertPlainText(text)
		self.log.moveCursor(QtGui.QTextCursor.End)

	def onReadyReadStandardError(self):
		text = self.inst._p.readAllStandardError().data().decode()
		self.log.moveCursor(QtGui.QTextCursor.End)
		self.log.insertPlainText(text)
		self.log.moveCursor(QtGui.QTextCursor.End)

	def onXqemuStateChanged(self):
		if self.inst.isRunning:
			self.runButton.setText('Stop')
		else:
			self.runButton.setText('Start')
			if self.inst._p.exitCode() != 0:
				QMessageBox.critical(self, 'XQEMU quit prematurely!', 'XQEMU quit prematurely.\n\n'
					'This may be a known issue with this specific game, a problem in XQEMU, or an error in your settings.\n'
					'Please check your settings for correctness and see the log area for details.\n'
					'If you need help resolving this problem, make sure to include this log in your error report, '
					'along with as many details about how and what you were doing when the error happened.')
		self.pauseButton.setText('Pause')

	def onRunButtonClicked(self):
		if not self.inst.isRunning:
			# No active instance
			try:
				self.log.clear()
				self.inst.start(self.settings)
			except Exception as e:
				QMessageBox.critical(self, 'Error!', str(e))
		else:
			# Instance exists
			self.inst.stop()

	def onPauseButtonClicked(self):
		if not self.inst.isRunning: return

		# We should probably actually pull from event queue to reflect state
		# here instead of querying during the button press
		if self.inst.isPaused():
			self.inst.cont()
			self.pauseButton.setText('Pause')
		else:
			self.inst.pause()
			self.pauseButton.setText('Continue')

	def onScreenshotButtonClicked(self):
		if not self.inst.isRunning: return
		self.inst.screenshot()

	def onRestartButtonClicked(self):
		if not self.inst.isRunning: return
		self.inst.restart()

	def onSettingsClicked(self):
		s = SettingsWindow(self.settings)
		s.exec_()
		self.settings.save()

	def onExitClicked(self):
		self.inst.stop()
		sys.exit(0)

def main():
	app = QApplication(sys.argv)
	app.setStyle('Fusion')

	# Dark theme via https://gist.github.com/gph03n1x/7281135 with modifications
	palette = QtGui.QPalette()
	palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
	palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
	palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15,15,15))
	palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
	palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
	palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
	palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
	palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
	palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
	palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
	palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45,197,45).lighter())
	palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
	palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
	palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
	palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
	app.setPalette(palette)

	widget = MainWindow()
	widget.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
