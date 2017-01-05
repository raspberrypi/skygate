#!/usr/bin/env python
#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore, uic
# from PyQt4.QtGui import QPalette
from PyQt4.QtGui import * 
import time
from time import strftime
import os.path
import configparser
import serial
import math
import csv
import calendar
from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox, QDateTimeEdit, QApplication
from PyQt4.QtCore import Qt, QDateTime
import fnmatch
import socket
import json
import threading
import urllib.parse
import urllib.request
import os, glob
import subprocess

Modes=[{'implicit': 0, 'coding': 8, 'bandwidth': 20.8, 'spreading': 11, 'lowopt': 1},
       {'implicit': 1, 'coding': 5, 'bandwidth': 20.8, 'spreading':  6, 'lowopt': 0},
       {'implicit': 0, 'coding': 8, 'bandwidth': 62.5, 'spreading':  8, 'lowopt': 0},
       {'implicit': 0, 'coding': 6, 'bandwidth':  250, 'spreading':  7, 'lowopt': 0},
       {'implicit': 1, 'coding': 5, 'bandwidth':  250, 'spreading':  6, 'lowopt': 0},
       {'implicit': 0, 'coding': 8, 'bandwidth': 41.7, 'spreading': 11, 'lowopt': 0},
       {'implicit': 1, 'coding': 5, 'bandwidth': 41.7, 'spreading':  6, 'lowopt': 0}]

	# {EXPLICIT_MODE, ERROR_CODING_4_8, BANDWIDTH_20K8, SPREADING_11, 1,    60, "Telemetry"},			// 0: Normal mode for telemetry
	# {IMPLICIT_MODE, ERROR_CODING_4_5, BANDWIDTH_20K8, SPREADING_6,  0,  1400, "SSDV"},				// 1: Normal mode for SSDV
	# {EXPLICIT_MODE, ERROR_CODING_4_8, BANDWIDTH_62K5, SPREADING_8,  0,  2000, "Repeater"},			// 2: Normal mode for repeater network	
	# {EXPLICIT_MODE, ERROR_CODING_4_6, BANDWIDTH_250K, SPREADING_7,  0,  8000, "Turbo"},				// 3: Normal mode for high speed images in 868MHz band
	# {IMPLICIT_MODE, ERROR_CODING_4_5, BANDWIDTH_250K, SPREADING_6,  0, 16828, "TurboX"},			// 4: Fastest mode within IR2030 in 868MHz band
	# {EXPLICIT_MODE, ERROR_CODING_4_8, BANDWIDTH_41K7, SPREADING_11, 0,   200, "Calling"},			// 5: Calling mode
	# {IMPLICIT_MODE, ERROR_CODING_4_5, BANDWIDTH_41K7, SPREADING_6,  0,  2800, "Uplink"}				// 6: Uplink mode for 868

SettingsList=[
	# LCARS settings
	{
		'section':	'LCARS',
		'setting':	'Chase.ID',
		'type':		'text',
		'prompt':	'Chase Car ID',
		'text':		'This is what your vehicle will appear as on the live map',
		'save':		1
	},
	{
		'setting':	'Chase.Enabled',
		'type':		'check',
		'prompt':	'Enable Chase Car',
		'text':		'When set, your vehicle position will be uploaded every 30 seconds',
		'save':		1
	},
	{
		'setting':	'SSDV.Path',
		'type':		'text',
		'prompt':	'Path to SSDV Folder',
		'text':		'Images in this folder can be browsed on the SSDV page',
		'save':		1
	},
	{
		'setting':	'Network.GPSServer',
		'type':		'text',
		'prompt':	'GPS server',
		'text':		'Network location of GPS server.  Expects to see a JSON feed as produced by GPSD',
		'save':		1
	},
	{
		'setting':	'Network.GatewayServer',
		'type':		'text',
		'prompt':	'LoRa Gateway',
		'text':		'Network location of LoRa gateway.  Expects to see a JSON feed as produced by the UKHAS LoRa gateway',
		'save':		1
	},
	# Gateway generic settings
	{
		'section':	'LoRa',
		'setting':	'gateway.tracker',
		'type':		'text',
		'prompt':	'LoRa Receiver Callsign',
		'text':		'Name of tracker used by LoRa gateway.  This is what will appear on the map in the list of receivers',
		'save':		0
	},
	{
		'setting':	'gateway.EnableHabitat',
		'type':		'check',
		'prompt':	'LoRa Habitat Upload',
		'text':		'Enables upload of telemetry from LoRa trackers to Habitat, so the flight appears on the web map',
		'save':		0
	},
	{
		'setting':	'gateway.EnableSSDV',
		'type':		'check',
		'prompt':	'LoRa SSDV Upload',
		'text':		'Enables upload of SSDV from LoRa trackers to the SSDV server, so that images from the flight appear on the SSDV page',
		'save':		0
	},
	{
		'setting':	'gateway.LogTelemetry',
		'type':		'check',
		'prompt':	'LoRa Telemetry Log',
		'text':		'Enables logging of the content of telemetry packets to telemetry.txt in the gateway folder.',
		'save':		0
	},
	{
		'setting':	'gateway.LogPackets',
		'type':		'check',
		'prompt':	'LoRa Packet Log',
		'text':		'Enables logging of all packets to packets.txt in the gateway folder.',
		'save':		0
	},
	{
		'setting':	'gateway.CallingTimeout',
		'type':		'integer',
		'prompt':	'LoRa Calling Timeout',
		'text':		'After this period of inactivity, the gateway will retune to the configured frequency and mode',
		'units':	's',
		'save':		0
	},
	{
		'setting':	'gateway.JPGFolder',
		'type':		'text',
		'prompt':	'LoRa JPG Folder',
		'text':		'Incoming LoRa SSDV images will be stored in this folder',
		'save':		0
	},
	# Gateway channel 0 settings
	{
		'section':	'LoRa 0',
		'setting':	'gateway.frequency_0',
		'type':		'float',
		'prompt':	'LoRa Ch0 Frequency',
		'text':		'Frequency for LoRa channel 0',
		'units':	'MHz',
		'save':		0
	},
	{
		'setting':	'gateway.mode_0',
		'type':		'list',
		'prompt':	'LoRa Ch0 Mode',
		'text':		'Preset Mode for LoRa channel 0',
		'values':	'',
		'offset':	0,
		'display':	['Slow','SSDV','Repeater','Turbo','TurboX','Calling'],
		'function':	'loramode',
		'save':		0
	},
	{
		'setting':	'gateway.sf_0',
		'type':		'list',
		'prompt':	'LoRa Ch0 Spreading',
		'text':		'Spreading Factor for LoRa channel 0',
		'values':	'',
		'offset':	6,
		'display':	['6', '7', '8', '9', '10', '11', '12'],
		'save':		0
	},
	{
		'setting':	'gateway.bandwidth_0',
		'type':		'list',
		'prompt':	'LoRa Ch0 Bandwidth',
		'text':		'Bandwidth in kHz for LoRa channel 0',
		'values':	'',
		'offset':	-1,
		'display':	['7.8', '10.4', '15.6k', '20.8', '31.25', '41.7', '62.5', '125', '250', '500'],
		'save':		0
	},
	{
		'setting':	'gateway.implicit_0',
		'type':		'check',
		'prompt':	'LoRa Ch0 Implicit',
		'text':		'Implicit Mode for LoRa channel 0; uncheck to use Explicit Mode',
		'save':		0
	},
	{
		'setting':	'gateway.coding_0',
		'type':		'list',
		'prompt':	'LoRa Ch0 Coding',
		'text':		'Error Coding for LoRa channel 0',
		'values':	'',
		'offset':	5,
		'display':	['5', '6', '7', '8'],
		'save':		0
	},
	{
		'setting':	'gateway.lowopt_0',
		'type':		'check',
		'prompt':	'LoRa Ch0 LDRO',
		'text':		'Low Data Rate Optimisation for LoRa channel 0',
		'save':		0
	},
	{
		'setting':	'gateway.AFC_0',
		'type':		'check',
		'prompt':	'LoRa Ch0 AFC',
		'text':		'Automatic Frequency Control for LoRa channel 0',
		'save':		0
	},
	# Gateway channel 1 settings
	{
		'section':	'LoRa 0',
		'setting':	'gateway.frequency_1',
		'type':		'float',
		'prompt':	'LoRa Ch1 Frequency',
		'text':		'Frequency for LoRa channel 1',
		'units':	'MHz',
		'save':		0
	},
	{
		'setting':	'gateway.mode_1',
		'type':		'list',
		'prompt':	'LoRa Ch1 Mode',
		'text':		'Preset Mode for LoRa channel 1',
		'values':	'',
		'offset':	0,
		'display':	['Slow','SSDV','Repeater','Turbo','TurboX','Calling'],
		'save':		0
	},
	{
		'setting':	'gateway.sf_1',
		'type':		'list',
		'prompt':	'LoRa Ch1 Spreading',
		'text':		'Spreading Factor for LoRa channel 1',
		'values':	'',
		'offset':	6,
		'display':	['6', '7', '8', '9', '10', '11', '12'],
		'save':		0
	},
	{
		'setting':	'gateway.bandwidth_1',
		'type':		'list',
		'prompt':	'LoRa Ch1 Bandwidth',
		'text':		'Bandwidth in kHz for LoRa channel 1',
		'values':	'',
		'offset':	-1,
		'display':	['7.8', '10.4', '15.6k', '20.8', '31.25', '41.7', '62.5', '125', '250', '500'],
		'save':		0
	},
	{
		'setting':	'gateway.implicit_1',
		'type':		'check',
		'prompt':	'LoRa Ch1 Implicit',
		'text':		'Implicit Mode for LoRa channel 0; uncheck to use Explicit Mode',
		'save':		0
	},
	{
		'setting':	'gateway.coding_1',
		'type':		'list',
		'prompt':	'LoRa Ch1 Coding',
		'text':		'Error Coding for LoRa channel 1',
		'values':	'',
		'offset':	5,
		'display':	['5', '6', '7', '8'],
		'save':		0
	},
	{
		'setting':	'gateway.lowopt_1',
		'type':		'check',
		'prompt':	'LoRa Ch0 LDR1',
		'text':		'Low Data Rate Optimisation for LoRa channel 1',
		'save':		0
	},
	{
		'setting':	'gateway.AFC_1',
		'type':		'check',
		'prompt':	'LoRa Ch1 AFC',
		'text':		'Automatic Frequency Control for LoRa channel 1',
		'save':		0
	}
]

OurStatus = {'time': '', 'lat': 51.95023, 'lon': -2.54445, 'alt': 0, 'speed': 0, 'track': 0, 'network': '', 'netcolour': 'Black', 'chasecarstatus' : 0}
ButtonText = ['PAYLOADS', 'HAB', 'CHASE', 'SOURCE', 'NAV', 'SSDV', 'BATC', 'SETTINGS']
ButtonColour = ['#FFFF33', '#98CCFF', '#FFFFCC', '#FFFF33', '#98CCFF', '#FFFFCC', '#FFFF33', '#98CCFF']
TempHABStatus = {'updatechart': 0, 'updated': 0, 'lastupdate': 0, 'payload': '', 'time': '', 'lat': 0, 'lon': 0, 'alt': 0, 'rate': 0}
TempSourceStatus = {'letter': '?', 'lastupdate': 0, 'connected':  0}

# Payloads
MAX_PAYLOADS=32
HABStatii = []
for i in range(0,MAX_PAYLOADS):
	HABStatii.append(TempHABStatus.copy())

# Data sources - LoRa 1, LoRa 2, RTTY, Habitat
Sources = []
for i in range(0,4):
	Sources.append(TempSourceStatus.copy())
Sources[0]['letter'] = '1'
Sources[1]['letter'] = '2'
Sources[2]['letter'] = 'R'
Sources[3]['letter'] = 'H'


SelectedPayloadIndex = 0
BATCStatus = 0

global SelectedSSDVFile
global SelectedSSDVFileName
global SSDVModificationDate
global CurrentScreen
global CurrentScreenTitle
global Settings
global EditSettings
global HABBalloonMode
global LoRaSocket
global SettingsPage, SettingsRows

def BoolToStr(value):
	if value:
		return '1'
	else:
		return '0'

def CalculateDescentRate(Weight, Density, CDTimesArea):
	return math.sqrt((Weight * 9.81)/(0.5 * Density * CDTimesArea))

def CalculateAirDensity(alt):
	if alt < 11000.0:
		# below 11Km - Troposphere
		Temperature = 15.04 - (0.00649 * alt)
		Pressure = 101.29 * math.pow((Temperature + 273.1) / 288.08, 5.256)
	elif alt < 25000.0:
		# between 11Km and 25Km - lower Stratosphere
		Temperature = -56.46
		Pressure = 22.65 * math.exp(1.73 - ( 0.000157 * alt))
	else:
		# above 25Km - upper Stratosphere
		Temperature = -131.21 + (0.00299 * alt)
		Pressure = 2.488 * math.pow((Temperature + 273.1) / 216.6, -11.388)

	return Pressure / (0.2869 * (Temperature + 273.1))

def CalculateCDA(Weight, Altitude, DescentRate):
	Density = CalculateAirDensity(Altitude)

	return (Weight * 9.81)/(0.5 * Density * DescentRate * DescentRate)

def CalculateLanding(Altitude, LandingAltitude, DescentRate):
	CDTimesArea = CalculateCDA(1.0, Altitude, DescentRate);
	TotalTime = 0
	Step = 100
	
	while Altitude > LandingAltitude:
		Density = CalculateAirDensity(Altitude)

		DescentRate = CalculateDescentRate(1.0, Density, CDTimesArea)

		TimeAtAltitude = Step / DescentRate
		TotalTime = TotalTime + TimeAtAltitude

		Altitude = Altitude - Step

	return {'landingspeed': DescentRate, 'timetilllanding': TotalTime}
				  
class Main(QtGui.QMainWindow):

	def LoadConfig(self):
		global Settings, EditSettings
	
		filename = 'lcars.txt'
		print ('Loading config file ' + filename)

		if os.path.isfile(filename):
			# Open config file
			config = configparser.RawConfigParser()   
			config.read(filename)
								
		for index, item in enumerate(SettingsList):
			Setting = item['setting']
			words = Setting.split('.')
			if len(words) == 2:
				Section = words[0]
				Field = words[1]
				if item['save']:
					if item['type'] in ['text', 'integer', 'float']:
						Settings[Setting] = config.get(Section, Field)
					elif item['type'] == 'check':
						Settings[Setting] = config.getboolean(Section, Field)			
				else:
					if item['type'] in ['text']:
						Settings[Setting] = ''
					elif item['type'] in ['check', 'integer', 'float', 'list']:
						Settings[Setting] = 0
			item['changed'] = 0

		if len(sys.argv) >= 2:
			# Override servers
			Settings['Network.GPSServer'] = sys.argv[1]
			Settings['Network.GatewayServer'] = sys.argv[1]
			
		EditSettings = Settings.copy()
		
	def SaveConfig(self):
		global Settings
		
		filename = 'lcars.txt'
		print ('Saving config file ' + filename)

		config = configparser.RawConfigParser()   
		config.read(filename)

		MessageForGateway = ''
		for index, item in enumerate(SettingsList):
			if item['changed']:
				Setting = item['setting']
				words = Setting.split('.')
				if len(words) == 2:
					Section = words[0]
					if not config.has_section(Section):
						config.add_section(Section)
					Field = words[1]
					if item['save']:
						if item['type'] in ['text', 'integer', 'float', 'list']:
							config.set(Section, Field, Settings[Setting])
						elif item['type'] == 'check':
							config.set(Section, Field, BoolToStr(Settings[Setting]))
					else:
						SaveRemote = 1
						try:
							if item['type'] == 'text':
								MessageForGateway = MessageForGateway + Field + '=' + Settings[Setting] + '\r\n'
							elif item['type'] == 'integer':
								MessageForGateway = MessageForGateway + Field + '=' + str(Settings[Setting]) + '\r\n'
							elif item['type'] == 'float':
								MessageForGateway = MessageForGateway + Field + '=' + str(Settings[Setting]) + '\r\n'
							elif item['type'] == 'check':
								MessageForGateway = MessageForGateway + Field + '=' + BoolToStr(Settings[Setting]) + '\r\n'
							elif item['type'] == 'list':
								MessageForGateway = MessageForGateway + Field + '=' + str(Settings[Setting]) + '\r\n'								
						except:
							pass
				item['changed'] = 0
			
		with open(filename, 'wt') as configfile:
			config.write(configfile)
			
		if MessageForGateway != '':
			MessageForGateway = MessageForGateway + 'SAVE\r\n'
			LoRaSocket.send(MessageForGateway.encode('utf-8'))
		
		
	def __init__(self):
		global Settings, EditSettings, CurrentScreenTitle, SelectedSSDVFile, SSDVModificationDate, CameraMode, HABBalloonMode

		CurrentScreenTitle = ''
		SelectedSSDVFile = 0
		SelectedSSDVFileName = '' 
		SSDVModificationDate = 0
		CameraMode = 0
		HABBalloonMode = 0
		CheckCamera()
		
		QtGui.QMainWindow.__init__(self)
		
		# Set defaults
		Settings = {'Network.GPSServer': 'localhost', 'Network.GatewayServer': 'localhost',
					'Chase.ID': 'default_chase', 'Chase.Enabled': False,
					'SSDV.Path': ''}

		if Settings['Chase.Enabled']:
			OurStatus['chasecarstatus'] = 1
					
		# Load config
		self.LoadConfig()
			
		# Set up main window and widgets
		self.initStaticUI()
		
		# os.system("./start_dlfldigi")

		# os.system("./start_gateway")
		
		self.show()
				
	def closeEvent(self, event):
		print ("")

	def handleSSDVScreenClick(self, event):
		global SelectedSSDVFile
		global CurrentScreen

		x=event.pos().x()
		
		if x < (self.width() / 2):
			# Go further away from the last file
			SelectedSSDVFile = SelectedSSDVFile + 1
		elif SelectedSSDVFile > 0:
			SelectedSSDVFile = SelectedSSDVFile - 1
			
		print("SelectedSSDVFile = " + str(SelectedSSDVFile))
		self.ShowSSDVFile(True)
		
	def handlePayloadLabelClick(self, event):
		global SelectedPayloadIndex
		
		sender = self.sender()
		for index, item in enumerate(self.HABPayloadLabels):
			if sender is item:
				PayloadIndex = index
		print("Payload button " + str(PayloadIndex) + " pressed")
		if HABStatii[PayloadIndex]['payload'] != '':
			if PayloadIndex != SelectedPayloadIndex:
				SelectedPayloadIndex = PayloadIndex;
				UpdateSelectedScreen()

	# Settings page signals]
	def handleSettingItemSelect(self):
		global EditSettings, SettingsPage, SettingsRows
		
		# User has changed selection
		sender = self.sender()
		Row = sender.currentRow() + SettingsRows[SettingsPage]
		screen = self.screens[7]
		
		# Disconnect previous handler
		# screen.findChild(QLineEdit, 'edtSetting').textChanged.disconnect()
		# screen.findChild(QSpinBox,  'spnSetting').valueChanged.disconnect()
		# screen.findChild(QDoubleSpinBox, 'spnDoubleSetting').disconnect()
		# screen.findChild(QCheckBox, 'chkSetting').stateChanged.disconnect()
		try:
			screen.findChild(QComboBox, 'cmbSetting').currentIndexChanged.disconnect()
		except Exception: pass	
		

		# Show explanation
		screen.findChild(QLabel, 'lblText').setText(SettingsList[Row]['text'])
		
		# Display and populate correct widget type
		screen.findChild(QLineEdit, 'edtSetting').hide()
		screen.findChild(QCheckBox, 'chkSetting').hide()
		screen.findChild(QSpinBox,  'spnSetting').hide()
		screen.findChild(QDoubleSpinBox,  'spnDoubleSetting').hide()
		screen.findChild(QComboBox,  'cmbSetting').hide()

		if 'units' in SettingsList[Row]:
			screen.findChild(QLabel,  'lblUnits').setText(SettingsList[Row]['units'])
		else:
			screen.findChild(QLabel,  'lblUnits').setText('')
		
		if SettingsList[Row]['type'] == 'text':
			screen.findChild(QLineEdit, 'edtSetting').show()
			screen.findChild(QLineEdit, 'edtSetting').setText(EditSettings[SettingsList[Row]['setting']])
			screen.findChild(QLineEdit, 'edtSetting').textChanged.connect(self.handleSettingTextChanged)
		elif SettingsList[Row]['type'] == 'integer':
			screen.findChild(QSpinBox,  'spnSetting').show()
			screen.findChild(QSpinBox,  'spnSetting').setValue(EditSettings[SettingsList[Row]['setting']])
			screen.findChild(QSpinBox,  'spnSetting').valueChanged.connect(self.handleSettingSpinChanged)
		elif SettingsList[Row]['type'] == 'float':
			screen.findChild(QDoubleSpinBox, 'spnDoubleSetting').show()
			screen.findChild(QDoubleSpinBox, 'spnDoubleSetting').setValue(EditSettings[SettingsList[Row]['setting']])
			screen.findChild(QDoubleSpinBox, 'spnDoubleSetting').valueChanged.connect(self.handleSettingDoubleSpinChanged)
		elif SettingsList[Row]['type'] == 'check':
			screen.findChild(QCheckBox, 'chkSetting').show()
			screen.findChild(QCheckBox, 'chkSetting').setText(SettingsList[Row]['prompt'])
			screen.findChild(QCheckBox, 'chkSetting').setChecked(EditSettings[SettingsList[Row]['setting']])
			screen.findChild(QCheckBox, 'chkSetting').stateChanged.connect(self.handleSettingCheckboxChanged)
		else:
			screen.findChild(QComboBox, 'cmbSetting').show()
			# Populate list
			screen.findChild(QComboBox, 'cmbSetting').clear()
			screen.findChild(QComboBox, 'cmbSetting').addItems(SettingsList[Row]['display'])
			if SettingsList[Row]['offset'] >= 0:
				# We use the item index as the value
				screen.findChild(QComboBox, 'cmbSetting').setCurrentIndex(EditSettings[SettingsList[Row]['setting']] - SettingsList[Row]['offset'])
			else:
				# We use the item itself as the value
				index = screen.findChild(QComboBox, 'cmbSetting').findText(str(EditSettings[SettingsList[Row]['setting']]))
				screen.findChild(QComboBox, 'cmbSetting').setCurrentIndex(index)
			screen.findChild(QComboBox, 'cmbSetting').currentIndexChanged.connect(self.handleSettingComboChanged)		
		
	def handleSettingTextChanged(self):
		global EditSettings, SettingsPage, SettingsRows
		
		# User is typing into an text box setting
		screen = self.screens[7]
		Row = screen.findChild(QListWidget, 'lstSettings').currentRow() + SettingsRows[SettingsPage]
		EditSettings[SettingsList[Row]['setting']] = screen.findChild(QLineEdit, 'edtSetting').text()
		SettingsList[Row]['changed'] = 1

	def handleSettingSpinChanged(self):
		global EditSettings, SettingsPage, SettingsRows
		
		# User is changing a spinbox value
		screen = self.screens[7]
		Row = screen.findChild(QListWidget, 'lstSettings').currentRow() + SettingsRows[SettingsPage]
		EditSettings[SettingsList[Row]['setting']] = screen.findChild(QSpinBox, 'spnSetting').value()
		SettingsList[Row]['changed'] = 1

	def handleSettingDoubleSpinChanged(self):
		global EditSettings, SettingsPage, SettingsRows

		# User is changing a double spinbox value
		screen = self.screens[7]
		Row = screen.findChild(QListWidget, 'lstSettings').currentRow() + SettingsRows[SettingsPage]
		EditSettings[SettingsList[Row]['setting']] = screen.findChild(QDoubleSpinBox, 'spnDoubleSetting').value()
		SettingsList[Row]['changed'] = 1

	def handleSettingCheckboxChanged(self):
		global EditSettings, SettingsPage, SettingsRows

		# User has changed check box value
		screen = self.screens[7]
		Row = screen.findChild(QListWidget, 'lstSettings').currentRow() + SettingsRows[SettingsPage]
		EditSettings[SettingsList[Row]['setting']] = screen.findChild(QCheckBox, 'chkSetting').isChecked()
		SettingsList[Row]['changed'] = 1
		
	def DoSpecialFunction(self, Row):
		if 'function' in SettingsList[Row]:
			if SettingsList[Row]['function'] == 'loramode':
				Channel = SettingsList[Row]['setting'][-1:]		# channel is '0' or '1' from end of setting name
				Mode = EditSettings[SettingsList[Row]['setting']]
				EditSettings['gateway.implicit_' + Channel] = Modes[Mode]['implicit']
				EditSettings['gateway.coding_' + Channel] = Modes[Mode]['coding']
				EditSettings['gateway.bandwidth_' + Channel] = Modes[Mode]['bandwidth']
				EditSettings['gateway.sf_' + Channel] = Modes[Mode]['spreading']
				EditSettings['gateway.lowopt_' + Channel] = Modes[Mode]['lowopt']
       
	def handleSettingComboChanged(self):
		global EditSettings, SettingsPage, SettingsRows

		# User has changed combo box value
		screen = self.screens[7]
		if screen.findChild(QComboBox, 'cmbSetting').currentIndex() >= 0:
			Row = screen.findChild(QListWidget, 'lstSettings').currentRow() + SettingsRows[SettingsPage]
			if SettingsList[Row]['offset'] >= 0:
				# We use the item index as the value
				EditSettings[SettingsList[Row]['setting']] = screen.findChild(QComboBox, 'cmbSetting').currentIndex() + SettingsList[Row]['offset']
			else:
				# We use the item itself as the value
				EditSettings[SettingsList[Row]['setting']] = screen.findChild(QComboBox, 'cmbSetting').currentText()
			self.DoSpecialFunction(Row)
			SettingsList[Row]['changed'] = 1
		
	def handleSaveSettingsClick(self, event):
		global Settings, EditSettings
		
		print("Settings SAVE button pressed")
		Settings = EditSettings.copy()
		if Settings['Chase.Enabled'] and (OurStatus['chasecarstatus'] == 0):
			OurStatus['chasecarstatus'] = 1
		elif not Settings['Chase.Enabled']:
			OurStatus['chasecarstatus'] = 0
		self.SaveConfig()

	def handleCancelSettingsClick(self, event):
		global Settings, EditSettings, CurrentScreen
		
		print("Settings CANCEL button pressed")
		self.InitSettingsScreen()
		# EditSettings = Settings.copy()
		# listView = CurrentScreen.findChild(QListWidget, 'lstSettings')
		# listView.setCurrentRow(0)		

	def handleKeyboardClick(self, event):
		os.system("killall matchbox-keyboard")		
		os.system("matchbox-keyboard -d &")		

	def handleLCARSSettingsClick(self, event):
		self.ShowSettingsPage(0)

	def handleLoRaSettingsClick(self, event):
		self.ShowSettingsPage(1)

	def handleLoRa0SettingsClick(self, event):
		self.ShowSettingsPage(2)

	def handleLoRa1SettingsClick(self, event):
		self.ShowSettingsPage(3)

	# Map/Nav page signals
	def handleMapClick(self, event):
		LoadMap()
		
	def handleNavitViewClick(self, event):
		LoadNavit(-1)
		
	def handleNavitRouteClick(self, event):
		LoadNavit(SelectedPayloadIndex)
		
	def handleSourcesGatewayClick(self, event):
		LoadGateway()
		
	def handleSourcesdlfldigiClick(self, event):
		Loaddlfldigi()
		
	def handleBATCNoneClick(self, event):
		global CameraMode
		CameraMode = 0
		CheckCamera()

	def handleBATCViewClick(self, event):
		global CameraMode
		CameraMode = 1
		CheckCamera()

	def handleBATCBothClick(self, event):
		global CameraMode
		CameraMode = 3
		CheckCamera()
		
	def handleButton(self):
		global CameraMode

		# hide screens
		global SelectedSSDVFile
		global CurrentScreen
		global CurrentScreenTitle
		
		self.logo.hide()
		
		for screen in self.screens:
			screen.hide()
		
		sender = self.sender()
		for index, item in enumerate(self.buttons):
			if sender is item:
				button_index = index
				
		CurrentScreen = self.screens[button_index]
		CurrentScreenTitle = ButtonText[button_index]
		
		if button_index == 0:
			# PAYLOADS
			pass
		elif button_index == 1:
			# HAB
			pass
		elif button_index == 2:
			# CHASE
			pass
			# CurrentScreen.findChild(QPushButton, 'btnOpen').clicked.connect(self.handleMapViewClick)
		elif button_index == 3:
			# SOURCES
			CurrentScreen.findChild(QPushButton, 'btnGateway').clicked.connect(self.handleSourcesGatewayClick)
			CurrentScreen.findChild(QPushButton, 'btndlfldigi').clicked.connect(self.handleSourcesdlfldigiClick)
		elif button_index == 4:
			# NAV
			CurrentScreen.findChild(QPushButton, 'btnMap').clicked.connect(self.handleMapClick)			
			CurrentScreen.findChild(QPushButton, 'btnOpen').clicked.connect(self.handleNavitViewClick)
			CurrentScreen.findChild(QPushButton, 'btnRoute').clicked.connect(self.handleNavitRouteClick)
		elif button_index == 5:
			# SSDV
			SelectedSSDVFile=0			# 0 means latest file; 1 means one before, etc
			self.ShowSSDVFile(True)
			CurrentScreen.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
			CurrentScreen.mousePressEvent = self.handleSSDVScreenClick
		elif button_index == 6:
			# BATC
			CurrentScreen.findChild(QPushButton, 'btnNone').clicked.connect(self.handleBATCNoneClick)
			CurrentScreen.findChild(QPushButton, 'btnView').clicked.connect(self.handleBATCViewClick)
			CurrentScreen.findChild(QPushButton, 'btnBoth').clicked.connect(self.handleBATCBothClick)
		elif button_index == 7:
			# SETTINGS
			self.InitSettingsScreen()
			# CurrentScreen.mousePressEvent = self.handleSettingsScreenClick
			CurrentScreen.findChild(QPushButton, 'btnSave').clicked.connect(self.handleSaveSettingsClick)
			CurrentScreen.findChild(QPushButton, 'btnCancel').clicked.connect(self.handleCancelSettingsClick)
			CurrentScreen.findChild(QPushButton, 'btnKeyboard').clicked.connect(self.handleKeyboardClick)
			CurrentScreen.findChild(QPushButton, 'btnLCARS').clicked.connect(self.handleLCARSSettingsClick)
			CurrentScreen.findChild(QPushButton, 'btnLoRa').clicked.connect(self.handleLoRaSettingsClick)
			CurrentScreen.findChild(QPushButton, 'btnLoRa0').clicked.connect(self.handleLoRa0SettingsClick)
			CurrentScreen.findChild(QPushButton, 'btnLoRa1').clicked.connect(self.handleLoRa1SettingsClick)

		# Switch off camera viewing
		if CameraMode == 1:
			CameraMode = 0
			CheckCamera()
		if CameraMode == 3:
			CameraMode = 2
			CheckCamera()
		
		CurrentScreen.show()

		self.UpdateSelectedScreen()
	
	def UpdateSelectedScreen(self):
		if CurrentScreenTitle == "HAB":
			self.UpdateHABChart(1)
			
				
	def initStaticUI(self):
		palette = QPalette()

		# Position main window top-left
		self.move(0,0)
		
		# Background
		self.background = QLabel(self) 
		self.background.move(0,0)
		self.background.resize(800,480)
		pixmap = QPixmap('background.png')
		self.background.setPixmap(pixmap)

		# STNG font
		font = QFont()
		font.setFamily("Swiss911 UCm BT")
		font.setPointSize(20)

		# Status bar (bottom of screen - GPS mainly)
		self.SourcesLabel = QLabel("", self)
		self.SourcesLabel.setFont(font)
		self.SourcesLabel.setFixedWidth(53)
		self.SourcesLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.SourcesLabel.move(128,452)
		
		self.BCLabel = QLabel("", self)
		self.BCLabel.setFont(font)
		self.BCLabel.setFixedWidth(23)
		self.BCLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.BCLabel.move(202,452)
		
		self.TimeLabel = QLabel("", self)
		self.TimeLabel.setFont(font)
		self.TimeLabel.setFixedWidth(66)
		self.TimeLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.TimeLabel.move(284,452)
		
		self.LatitudeLabel = QLabel("", self)
		self.LatitudeLabel.setFont(font)
		self.LatitudeLabel.setFixedWidth(82)
		self.LatitudeLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.LatitudeLabel.move(372,452)
		
		self.LongitudeLabel = QLabel("", self)
		self.LongitudeLabel.setFont(font)
		self.LongitudeLabel.setFixedWidth(72)
		self.LongitudeLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.LongitudeLabel.move(471,452)
		
		self.AltitudeLabel = QLabel("", self)
		self.AltitudeLabel.setFont(font)
		self.AltitudeLabel.setFixedWidth(58)
		self.AltitudeLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
		self.AltitudeLabel.move(560,452)
		
		self.InternetLabel = QLabel("", self)
		self.InternetLabel.setFont(font)
		self.InternetLabel.setFixedWidth(65)
		self.InternetLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.InternetLabel.move(690,452)
		
		# Payload bar
		self.HABPayloadLabels = []
		for i in range(1,4):
			HABPayloadLabel = QPushButton("", self)	# Payload " + str(i), self)
			HABPayloadLabel.setStyleSheet("background: #F3DF6F")
			HABPayloadLabel.setFont(font)
			HABPayloadLabel.resize(84,25)
			HABPayloadLabel.move(113 + (i-1) * 86, 2)
			HABPayloadLabel.clicked.connect(self.handlePayloadLabelClick)
			self.HABPayloadLabels.append(HABPayloadLabel)
		
		self.HABTimeLabel = QLabel("", self)
		self.HABTimeLabel.setFont(font)
		self.HABTimeLabel.setFixedWidth(66)
		self.HABTimeLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.HABTimeLabel.move(405,0)
		
		self.HABLatitudeLabel = QLabel("", self)
		self.HABLatitudeLabel.setFont(font)
		self.HABLatitudeLabel.setFixedWidth(82)
		self.HABLatitudeLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.HABLatitudeLabel.move(490,0)
		
		self.HABLongitudeLabel = QLabel("", self)
		self.HABLongitudeLabel.setFont(font)
		self.HABLongitudeLabel.setFixedWidth(72)
		self.HABLongitudeLabel.setAlignment(QtCore.Qt.AlignCenter| QtCore.Qt.AlignVCenter)
		self.HABLongitudeLabel.move(590,0)
		
		self.HABAltitudeLabel = QLabel("", self)
		self.HABAltitudeLabel.setFont(font)
		self.HABAltitudeLabel.setFixedWidth(66)
		self.HABAltitudeLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
		self.HABAltitudeLabel.move(679,0)

		# self.HABRateLabel = QLabel("", self)
		# self.HABRateLabel.setFont(font)
		# self.HABRateLabel.setFixedWidth(65)
		# self.HABRateLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
		# self.HABRateLabel.move(712,0)

		# Buttons
		self.buttons = []
		MenuTop = 36
		MenuHeight = 446-MenuTop
		ButtonGap = 3
		ButtonTop = MenuTop + ButtonGap
		ButtonHeight = (MenuHeight-ButtonGap) / len(ButtonText) - ButtonGap
		for index, item in enumerate(ButtonText):
			button = QtGui.QPushButton(item, self)
			font.setPointSize(24)
			button.setFont(font)
			button.setStyleSheet("text-align: center; background-color: " + ButtonColour[index])
			button.move(2,ButtonTop + index*(ButtonHeight + ButtonGap))
			button.resize(96,ButtonHeight)
			button.clicked.connect(self.handleButton)
			self.buttons.append(button)
		
		# logo
		self.logo = QLabel(self) 
		self.logo.move(324,66)
		self.logo.resize(251,337)
		pixmap = QPixmap('logo.png')
		self.logo.setPixmap(pixmap)

		self.screens = []
		for index, item in enumerate(ButtonText):
			screen = QLabel(self)
			screen.move(101,30)
			screen.resize(700,420)
			screen.hide()
			self.screens.append(screen)
			
		uic.loadUi('PAYLOADS.ui', self.screens[0])
		uic.loadUi('HAB.ui', self.screens[1])
		uic.loadUi('CHASE.ui', self.screens[2])
		uic.loadUi('SOURCE.ui', self.screens[3])
		uic.loadUi('NAVIT.ui', self.screens[4])
		# uic.loadUi('SSDV.ui', self.screens[5])
		uic.loadUi('BATC.ui', self.screens[6])
		uic.loadUi('SETTINGS.ui', self.screens[7])
		
		# SSDV image
		# self.ssdvscreen = QLabel(self) 
		# self.ssdvscreen.hide()
		
		timer = QtCore.QTimer(self)
		timer.timeout.connect(self.Time)
		timer.start(1000)
	
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)		# Remove caption bar
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)				# Remove border
		
		#palette.setBrush(QPalette.Background,QBrush(QPixmap("Background.png")))
		#self.setPalette(palette)	
				
		self.resize(800, 480)
			
	# def initDynamicUI(self):

	def ShowSSDVFile(self, Always):
		global SelectedSSDVFileName
		global CurrentScreen
		global SSDVModificationDate
		
		# 0 means latest file; 1 onwards means 1st file (by date), 2nd etc
		FileName = GetSSDVFileName()
		if FileName != '':
			ModificationDate = time.ctime(os.path.getmtime(FileName))
		
			if Always or (FileName != SelectedSSDVFileName) or (ModificationDate != SSDVModificationDate):
				print("Update SSDV Image")
				pixmap = QPixmap(FileName)
				CurrentScreen.setPixmap(pixmap.scaled(CurrentScreen.size(), QtCore.Qt.KeepAspectRatio))
				
			SelectedSSDVFileName = FileName
			SSDVModificationDate = ModificationDate
	
	def ShowSettingsPage(self, Page):
		global SettingsPage, SettingsRows
		
		SettingsPage = Page
		screen = self.screens[7]
		
		# Populate settings list
		listView = screen.findChild(QListWidget, 'lstSettings')
		listView.clear()
		
		for index in range(SettingsRows[Page], SettingsRows[Page+1]):
			listView.addItem(SettingsList[index]['prompt'])
		
		listView.itemSelectionChanged.connect(self.handleSettingItemSelect)
		listView.setCurrentRow(0)

	def InitSettingsScreen(self):
		global Settings, EditSettings, LoRaSocket, SettingsPage, SettingsRows
		
		try:
			LoRaSocket.send('SETTINGS\r\n'.encode('utf-8'))
		except:
			pass
		
		EditSettings = Settings.copy()
						
		# Look for sections
		SettingsRows = []
		for index, item in enumerate(SettingsList):
			if 'section' in item:
				SettingsRows.append(index)
		SettingsRows.append(len(SettingsList))
		
		# Show section
		self.ShowSettingsPage(0)
		
	def UpdateHABChart(self, Always):
		if HABStatii[SelectedPayloadIndex]['updatechart'] or Always:
			HABStatii[SelectedPayloadIndex]['updatechart'] = 0
			
			# Create gnuplot command file
			with open("hab.gnuplot", "w") as file:
				file.write("set border lw 1 lc rgb 'white'\n")
				file.write("set xtics textcolor rgb 'white'\n")
				file.write("set ytics textcolor rgb 'white'\n")
				file.write("set title '" + HABStatii[SelectedPayloadIndex]['payload'] + "'\n")
				file.write("set ylabel 'Altitude (m)' textcolor rgb 'yellow'\n")
				file.write("set timefmt '%H:%M:%S'\n");
				file.write("set format x '%H:%M'\n");
				file.write("set xdata time\n")
				file.write("set xlabel 'Time' textcolor rgb 'yellow'\n")
				file.write("set grid\n")
				file.write("set key textcolor rgb 'white'\n")
				file.write("set term png size 580, 350 background rgb 'black'\n")
				file.write("set output 'hab.png'\n")
				file.write("set datafile separator ','\n")
				file.write("plot '" + HABStatii[SelectedPayloadIndex]['payload'] + ".csv' u 1:2 linecolor rgb 'yellow' notitle with lines\n")
						
			# Run gnuplot to produce png image
			os.system("gnuplot < hab.gnuplot")
			
			# Display that image
			pixmap = QPixmap('hab.png')
			self.screens[1].findChild(QLabel, 'lblChart').setPixmap(pixmap)

	def UpdatePayloadButtons(self):
		for PayloadIndex, HABPayloadLabel in enumerate(self.HABPayloadLabels):
			if HABStatii[PayloadIndex]['payload'] != '':
				if int(time.time()) <= (HABStatii[PayloadIndex]['lastupdate'] + 60):
					if PayloadIndex == SelectedPayloadIndex:
						# Live data, button selected
						ButtonStyle = "background: #00FF00"
					else:
						# Live data, payload unselected
						ButtonStyle = "background: #008000"
				else:
					if PayloadIndex == SelectedPayloadIndex:
						# Old data, button selected
						ButtonStyle = "background: #FF0000"
					else:
						ButtonStyle = "background: #800000"
				
				HABPayloadLabel.setStyleSheet(ButtonStyle)				
	
	def UpdatePayloadInformation(self):
		global HABBalloonMode
		
		for PayloadIndex, HABStatus in enumerate(HABStatii):
			if HABStatus['updated'] == 1:
				HABStatus['updated'] = 0
				
				# Write to CSV
				with open(HABStatus['payload'] + ".csv", "a") as file:
					file.write(str(HABStatus['time']) + "," + str(HABStatus['alt']) + "\n")
				HABStatus['updatechart'] = 1				
				
				# Payload bar at top of screen	
				if PayloadIndex == SelectedPayloadIndex:
					self.HABTimeLabel.setText("<font color='orange'>" + HABStatus['time'] + "</font>")
					self.HABLatitudeLabel.setText("<font color='orange'>" + "%.5f" % HABStatus['lat'] + "</font>")
					self.HABLongitudeLabel.setText("<font color='orange'>" + "%.5f" % HABStatus['lon'] + "</font>")
					self.HABAltitudeLabel.setText("<font color='orange'>" + "%.0f" % HABStatus['alt'] + "m</font>")
					
				if HABStatus['payload'] != "":
					self.HABPayloadLabels[PayloadIndex].setText(HABStatus['payload']) 		
						
				# Payloads screen
				listView = self.screens[0].findChild(QListWidget, 'lstPayload_' + str(PayloadIndex+1))
				listView.clear()
				listView.addItem(HABStatus['payload']);
				listView.addItem("");
				listView.addItem(str(HABStatus['time']))
				listView.addItem(str(HABStatus['alt']) + 'm')
				listView.addItem(str(HABStatus['lat']))
				listView.addItem(str(HABStatus['lon']))
				listView.addItem(str(HABStatus['rate']) + 'm/s')
				if (int(time.time()) - HABStatus['lastupdate']) < 1000:
					listView.addItem(str(int(time.time()) - HABStatus['lastupdate']) + 's')
				
				
				# HAB screen
				if PayloadIndex == SelectedPayloadIndex:
					# Balloon/chute bitmap
					Balloon = self.screens[1].findChild(QLabel, 'lblBalloon')
					if Balloon is not None:
						if HABStatus['rate'] > 2:
							Mode = 1
						elif HABStatus['rate'] < -2:
							Mode = 2
						elif HABStatus['alt'] > 2000:
							Mode = 1
						else:
							Mode = 0				
						if Mode != HABBalloonMode:
							HABBalloonMode = Mode;
							pixmap = QPixmap(['payload.png', 'balloon.png', 'parachute.png'][Mode])
							Balloon.setPixmap(pixmap)
						# Balloon/chute position from altitude
						Balloon.setGeometry(610,240-240*HABStatus['alt']/45000,66,115)

					# Altitude label
					self.screens[1].findChild(QLabel, 'lblAltitude').setText(str(HABStatus['alt']) + 'm')
					
					# Vertical rate
					self.screens[1].findChild(QLabel, 'lblRate').setText(str(HABStatus['rate']) + 'm/s')
					
					# Distance and direction
					DistanceToHAB = CalculateDistance(HABStatus['lat'], HABStatus['lon'], OurStatus['lat'], OurStatus['lon'])
					DirectionToHAB = CalculateDirection(HABStatus['lat'], HABStatus['lon'], OurStatus['lat'], OurStatus['lon'])
					self.screens[1].findChild(QLabel, 'lblDirection').setText("%.1f km " % (DistanceToHAB/1000) + ["N","NE","E","SE","S","SW","W","NW","N"][int(round(DirectionToHAB/45))])
				
				
				# Chase Screen
				if PayloadIndex == SelectedPayloadIndex:
					listView = self.screens[2].findChild(QListWidget, 'lstValues')
					listView.clear()
					listView.addItem(HABStatus['payload']);
					listView.addItem("");
					listView.addItem(str(HABStatus['time']))
					listView.addItem(str(HABStatus['alt']) + 'm')
					listView.addItem(str(HABStatus['lat']))
					listView.addItem(str(HABStatus['lon']))
					listView.addItem(str(HABStatus['rate']) + 'm/s')
					if (int(time.time()) - HABStatus['lastupdate']) < 1000:
						listView.addItem(str(int(time.time()) - HABStatus['lastupdate']) + 's')
					
					# Distance and direction
					DistanceToHAB = CalculateDistance(HABStatus['lat'], HABStatus['lon'], OurStatus['lat'], OurStatus['lon'])
					DirectionToHAB = CalculateDirection(HABStatus['lat'], HABStatus['lon'], OurStatus['lat'], OurStatus['lon'])
					self.screens[2].findChild(QDial, 'dial').setValue(DirectionToHAB)
					if DistanceToHAB > 2000:
						self.screens[2].findChild(QLabel, 'lblDistance').setText("%.1f km" % (DistanceToHAB/1000))
					else:
						self.screens[2].findChild(QLabel, 'lblDistance').setText("%.0f m" % DistanceToHAB)
						
					VerticalDistance = HABStatus['alt'] - OurStatus['alt']
					if VerticalDistance < 0:
						self.screens[2].findChild(QLabel, 'lblVertical').setText("%d m below" % -VerticalDistance)
					elif abs(VerticalDistance) < 500:
						self.screens[2].findChild(QLabel, 'lblVertical').setText("%d m above" % VerticalDistance)
					else:
						self.screens[2].findChild(QLabel, 'lblVertical').setText("")

					if (HABStatus['alt'] > (OurStatus['alt'] + 100)) and (HABStatus['rate'] < -1.0):
						Prediction = CalculateLanding(HABStatus['alt'], OurStatus['alt'], HABStatus['rate'])
						self.screens[2].findChild(QLabel, 'lblEstimatedSpeed').setText("%.1f m/s landing" % Prediction['landingspeed'])
						self.screens[2].findChild(QLabel, 'lblEstimatedTime').setText("%ds to landing" % Prediction['timetilllanding'])
					else:
						self.screens[2].findChild(QLabel, 'lblEstimatedSpeed').setText("")
						self.screens[2].findChild(QLabel, 'lblEstimatedTime').setText("")
				
					# Altitude label
					self.screens[1].findChild(QLabel, 'lblAltitude').setText(str(HABStatus['alt']) + 'm')
					
					# Vertical rate
					self.screens[1].findChild(QLabel, 'lblRate').setText(str(HABStatus['rate']) + 'm/s')
					
					# Distance and direction
					DistanceToHAB = CalculateDistance(HABStatus['lat'], HABStatus['lon'], OurStatus['lat'], OurStatus['lon'])
					DirectionToHAB = CalculateDirection(HABStatus['lat'], HABStatus['lon'], OurStatus['lat'], OurStatus['lon'])
					self.screens[1].findChild(QLabel, 'lblDirection').setText("%.1f km " % (DistanceToHAB/1000) + ["N","NE","E","SE","S","SW","W","NW","N"][int(round(DirectionToHAB/45))])
	
#-------- Slots ------------------------------------------
		
	def Time(self):		# this happens once per second
		global OurStatus
		global CurrentScreenTitle
		
		# Buttons
		self.UpdatePayloadButtons()
		
		# Source status
		temp = ' '
		for index, source in enumerate(Sources):
			if source['connected']:
				if int(time.time()) <= (source['lastupdate'] + 60):
					colour = 'lime'
				else:
					colour = 'yellow'
			else:
				colour = 'gray'
			TempSourceStatus = {'letter': '?', 'lastupdate': 0, 'connected':  0}

			temp = temp + "<font color='" + colour + "'>" + source['letter'] + " </font>"

		self.SourcesLabel.setText(temp)
		
		# BATC and Chase Car status
		temp = "<font color='" + ["grey","red","lime"][BATCStatus] + "'>B </font>"
		temp = temp + "<font color='" + ["grey","yellow","red","lime"][OurStatus['chasecarstatus']] + "'>C</font>"

		self.BCLabel.setText(temp)

		# GPS
		self.TimeLabel.setText("<font color='orange'>" + OurStatus['time'] + "</font>")
		self.LatitudeLabel.setText("<font color='orange'>" + "%.5f" % OurStatus['lat'] + "</font>")
		self.LongitudeLabel.setText("<font color='orange'>" + "%.5f" % OurStatus['lon'] + "</font>")
		self.AltitudeLabel.setText("<font color='orange'>" + "%.0f" % OurStatus['alt'] + "m</font>")
		self.InternetLabel.setText("<font color='" + OurStatus['netcolour'] + "'>" + OurStatus['network'] + "</font>")
		
		self.UpdatePayloadInformation()
		
		# CAR screen
		# self.screens[1].findChild(QLabel, 'lblTime').setText(str(OurStatus['time']))
		
		# HAB screen
		if CurrentScreenTitle == 'HAB':
			self.UpdateHABChart(0)
		
		# SSDV screen
		if CurrentScreenTitle == 'SSDV':
			self.ShowSSDVFile(False)
			
		
def GetSSDVFileName():
	global SelectedSSDVFile

	# Get list of jpg files
	date_file_list = []
	for file in glob.glob(Settings['SSDVPath'] + '/*.JPG'):
		stats = os.stat(file)
		lastmod_date = time.localtime(stats[8])
		date_file_tuple = lastmod_date, file
		date_file_list.append(date_file_tuple)

	if len(date_file_list) == 0:
		return ''

	if SelectedSSDVFile < 0:
		SelectedSSDVFile = 0

	if SelectedSSDVFile >= len(date_file_list):
		SelectedSSDVFile = len(date_file_list)-1
		
	Index = len(date_file_list) - SelectedSSDVFile - 1
		
	selection = sorted(date_file_list)[Index]
	return selection[1]
		
  
def ProcessGPS(s):
	s.send(b'?WATCH={"enable":true,"json":true}')

	while 1:
		reply = s.recv(4096)                                     
		if reply:
			inputstring = reply.split(b'\n')
			for line in inputstring:
				if line:
					temp = line.decode('utf-8')
					j = json.loads(temp)
					if j['class'] == 'TPV':
						global OurStatus
						
						# print ("time = " + j['time'])
						temp=j['time'].split('T')		# ['2015-09-14', '12:48:43.000Z']
						temp=temp[1].split('.')			# '12:48:43'
						OurStatus['time'] = temp[0]
						OurStatus['lat'] = j['lat']
						OurStatus['lon'] = j['lon']
						OurStatus['alt'] = j['alt']
						OurStatus['speed'] = j['speed'] * 2.23693629	# m/s --> mph
						OurStatus['track'] = j['track']
						# print ("GPSD: t=" + temp[0] +
								# ",lat=" + str(j['lat']) +
								# ",lon=" + str(j['lon']) +
								# ",alt=" + str(j['alt']) +
								# ",spd=" + str(j['speed']) +
								# ",dir=" + str(j['track']))
		else:
			time.sleep(1)
		
	s.close()

def doGPS(host, port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

		s.connect((host, port))                               
		
		ProcessGPS(s)

		s.close()
	except:
		pass
	
def gps_thread():

	host = Settings['Network.GPSServer']
	port = 2947
	
	while 1:
		doGPS(host, port)

def ProcessdlfldigiLine(line):
	# $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
	print(line)	

	field_list = line.split(",")

	Payload = field_list[0][1:]
	PayloadIndex = FindFreePayload(Payload)
	
	HABStatii[PayloadIndex]['payload'] = Payload
	if j['time'] != HABStatii[PayloadIndex]['time']:
		HABStatii[PayloadIndex]['lastupdate'] = int(time.time())
		Sources[2]['lastupdate'] = int(time.time())
	HABStatii[PayloadIndex]['time'] = field_list[2]
	HABStatii[PayloadIndex]['lat'] = float(field_list[3])
	HABStatii[PayloadIndex]['lon'] = float(field_list[4])
	HABStatii[PayloadIndex]['alt'] = float(field_list[5])
	HABStatii[PayloadIndex]['rate'] = 0
	HABStatii[PayloadIndex]['updated'] = 1					

def Processdlfldigi(s):
	line = ''
	while 1:
		reply = s.recv(1)
		if reply:
			value = reply[0]
			if value == 9:
				pass
			elif value == 10:
				if line != '':
					ProcessdlfldigiLine(line)
					line = ''
			elif (value >= 32) and (value < 128):
				temp = chr(reply[0])
				if temp == '$':
					line = temp
				elif line != '':
					line = line + temp
		else:
			time.sleep(1)
		
def dodlfldigi(host, port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

		s.connect((host, port))    
		
		print("Connected to dl-fldigi")
		Sources[2]['connected'] = 1
		
		Processdlfldigi(s)

		s.close()
	except:
		Sources[2]['connected'] = 0
		pass

def dlfldigi_thread():

	host = "localhost"
	port = 7322
	
	print("Trying to connect to dl-fldigi at " + host + ":" + str(port))
	
	while 1:
		dodlfldigi(host, port)

def Speech(Message):
	os.system('espeak -ven+f3 -k5 -s150 "' + Message + '" &')

def ProcessLoRa(s):
	QuietCount = 0
	LineBuffer = ''
	while 1:
		# Any data from gateway?
		reply = s.recv(4096)                                     
		if reply:
			QuietCount = 0
			inputstring = reply.split(b'\n')
			for line in inputstring:
				temp = line.decode('utf-8')
				temp = LineBuffer + temp
				LineBuffer = ''
				
				if temp.endswith('\r'):
					j = json.loads(temp)
					if j['class'] == 'POSN':
						if j['payload'] != '':
							global HABStatii
							
							print ("LORA: " + j['payload'] +
									", t= " + j['time'] +
									", lat=" + str(j['lat']) +
									", lon=" + str(j['lon']) +
									", alt = " + str(j['alt']))

							PayloadIndex = FindFreePayload(j['payload'])
							Channel = j['channel']
							
							# HABStatii[PayloadIndex]['payload'] = j['payload']
							if j['time'] != HABStatii[PayloadIndex]['time']:
								if HABStatii[PayloadIndex]['time'] == '':
									Speech("First telemetry from payload " + j['payload'])
								elif int(time.time()) > (HABStatii[PayloadIndex]['lastupdate'] + 60):
									Speech("Resumed telemetry from payload " + j['payload'])
								HABStatii[PayloadIndex]['lastupdate'] = int(time.time())
								Sources[Channel]['lastupdate'] = int(time.time())
							HABStatii[PayloadIndex]['time'] = j['time']
							HABStatii[PayloadIndex]['lat'] = j['lat']
							HABStatii[PayloadIndex]['lon'] = j['lon']
							HABStatii[PayloadIndex]['alt'] = j['alt']
							# HABStatii[PayloadIndex]['rate'] = j['rate']

							HABStatii[PayloadIndex]['updated'] = 1					
					elif j['class'] == 'SET':
						EditSettings['gateway.' + j['set']] = j['val']
				else:
					LineBuffer = temp
		else:
			QuietCount += 1
			if QuietCount >= 5:
				print ("TIMED OUT")
				return
			time.sleep(1)
		
def doLoRa(host, port):
	global LoRaSocket
	
	try:
		LoRaSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

		LoRaSocket.connect((host, port))    
		
		print("Connected to gateway")
		Sources[0]['connected'] = 1
		Sources[1]['connected'] = 1
		
		ProcessLoRa(LoRaSocket)

		LoRaSocket.close()
	except:
		Sources[0]['connected'] = 0
		Sources[1]['connected'] = 0
		pass

def lora_thread():

	host = Settings['Network.GatewayServer']
	port = 6004
	
	print("Trying to connect to gateway at " + host + ":" + str(port))
	
	while 1:
		doLoRa(host, port)

def ConvertTimeForHabitat(GPSTime):
	return GPSTime[0:2] + GPSTime[3:5] + GPSTime[6:8]

def car_thread():
	while 1:
		if Settings['Chase.Enabled'] and (len(OurStatus['time']) > 0):
			print("UPLOAD CAR")
			url = 'http://spacenear.us/tracker/track.php'
			values = {'vehicle' : Settings['Chase.ID'],
					 'time'  : ConvertTimeForHabitat(OurStatus['time']),
					 'lat'  : OurStatus['lat'],
					 'lon'  : OurStatus['lon'],
					 'speed'  : OurStatus['speed'],
					 'alt'  : OurStatus['alt'],
					 'heading'  : OurStatus['track'],
					 'pass'  : 'aurora'}
			data = urllib.parse.urlencode(values)
			data = data.encode('utf-8') # data should be bytes
			req = urllib.request.Request(url, data)
			with urllib.request.urlopen(req) as response:
				the_page = response.read()			# content = urllib.request.urlopen(url=url, data=data).read()
			OurStatus['chasecarstatus'] = 3
			time.sleep(30)
		else:
			time.sleep(1)
		
def internet_on():
	# try:
		urllib.request.urlopen('http://google.com',timeout=5)
		return True
# 	except:
		return False

def get_lan_type():		
	
	if sys.platform == 'win32':
		return 'Windows'
		
	p = subprocess.Popen("iwconfig wlan0", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	p_status = p.wait()

	if p_status == 0:
		temp = output.decode("utf-8") 
		temp = temp.split('ESSID:"', 1)
		if len(temp) > 1:
			temp = temp[1].split('"', 1)
			# print("WLAN " + temp[0])
			return temp[0]

	p = subprocess.Popen("ifconfig eth0", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	p_status = p.wait()

	if p_status == 0:
		temp = output.decode("utf-8") 
		temp = temp.split('inet addr:', 1)
		if len(temp) > 1:
			# print ("LAN")
			return 'LAN'

	return ''

def CheckCamera():
	global CameraMode
	
	os.system("sudo killall ffmpeg")
	os.system("sudo killall raspivid")
	if CameraMode == 1:
		# View only, in window
		# if CurrentScreenIndex=6
		os.system("raspivid -p 105,0,690,480 -t 1000000 &")
	elif CameraMode == 2:
		# Stream to batc, no view
		os.system("raspivid -n -w 720 -h 405 -fps 25 -t 1000000 -b 2000000 -ih -o - | ffmpeg -i - -vcodec copy -an -f flv rtmp://batc.tv/live/h53d96/h53d96 &")
	elif CameraMode == 3:
		# Stream to batc, with view if window showing
		os.system("raspivid -p 105,0,690,480 -w 720 -h 405 -fps 25 -t 1000000 -b 2000000 -ih -o - | ffmpeg -i - -vcodec copy -an -f flv rtmp://batc.tv/live/h53d96/h53d96 &")

def LoadMap():
	# start browser if not running, then switch to it
	# http://tracker.habhub.org/#!mt=roadmap&mz=11&qm=1_day&f=NOTAFLIGHT&q=NOTAFLIGHT
	print ("Map")

	IncludePayloads = ''	# '&q=NOTAFLIGHT;X0'
	TargetPayload = '' '&f=NOTAFLIGHT'
	for PayloadIndex, HABStatus in enumerate(HABStatii):
		if HABStatus['payload'] != '':
			if IncludePayloads == '':
				IncludePayloads = '&q=' + HABStatus['payload']
			else:
				IncludePayloads = IncludePayloads + ';' + HABStatus['payload']

			if TargetPayload == '':
				TargetPayload = '&f=' + HABStatus['payload']
	
	URL = 'http://tracker.habhub.org/#!mt=roadmap&mz=11&qm=1_day' + TargetPayload + IncludePayloads	
	
	os.system("./start_web \"" + URL + "\"")
		
def LoadNavit(PayloadIndex):
	# start Navit if not running, then switch to it
	# subprocess.Popen("./start_navit", stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)		
	# -2.536681 51.941036
	if PayloadIndex >= 0:
		os.system("./start_navit " + str(HABStatii[PayloadIndex]['lon']) + " " + str(HABStatii[PayloadIndex]['lat']) + " &")
	else:
		os.system("./start_navit &")
		

def LoadGateway():
	os.system("./start_gateway &")

def Loaddlfldigi():
	os.system("./start_dlfldigi &")
		
def network_thread():

	while 1:
		lantype = get_lan_type()
		
		OurStatus['network'] = lantype;
		
		if lantype != '':
			if internet_on():
				OurStatus['netcolour'] = 'Orange';
			else:
				OurStatus['netcolour'] = 'Red';
		time.sleep(1)
		
def FindFreePayload(PayloadID):
	# Find matching slot
	for PayloadIndex, HABStatus in enumerate(HABStatii):
		if HABStatus['payload'] == PayloadID:
			return PayloadIndex

	# Find free slot	
	for PayloadIndex, HABStatus in enumerate(HABStatii):
		if HABStatus['payload'] == "":
			HABStatus['payload'] = PayloadID
			return PayloadIndex
	
	# Find oldest slot	
	for PayloadIndex, HABStatus in enumerate(HABStatii):
		if HABStatus['payload'] == "":
			HABStatus['payload'] = PayloadID
			return PayloadIndex
			
	return 0

def CalculateDistance(HABLatitude, HABLongitude, CarLatitude, CarLongitude):
	HABLatitude = HABLatitude * math.pi / 180
	HABLongitude = HABLongitude * math.pi / 180
	CarLatitude = CarLatitude * math.pi / 180
	CarLongitude = CarLongitude * math.pi / 180

	return 6371000 * math.acos(math.sin(CarLatitude) * math.sin(HABLatitude) + math.cos(CarLatitude) * math.cos(HABLatitude) * math.cos(HABLongitude-CarLongitude))

def CalculateDirection(HABLatitude, HABLongitude, CarLatitude, CarLongitude):
	HABLatitude = HABLatitude * math.pi / 180
	HABLongitude = HABLongitude * math.pi / 180
	CarLatitude = CarLatitude * math.pi / 180
	CarLongitude = CarLongitude * math.pi / 180

	y = math.sin(HABLongitude - CarLongitude) * math.cos(HABLatitude)
	x = math.cos(CarLatitude) * math.sin(HABLatitude) - math.sin(CarLatitude) * math.cos(HABLatitude) * math.cos(HABLongitude - CarLongitude)

	return math.atan2(y, x) * 180 / math.pi
	
def main():
	app = QtGui.QApplication(sys.argv)
	main = Main()

	t = threading.Thread(target=gps_thread)
	t.daemon = True
	t.start()
	
	t = threading.Thread(target=lora_thread)
	t.daemon = True
	t.start()

	t = threading.Thread(target=dlfldigi_thread)
	t.daemon = True
	t.start()

	t = threading.Thread(target=car_thread)
	t.daemon = True
	t.start()
	
	t = threading.Thread(target=network_thread)
	t.daemon = True
	t.start()

	main.show()

	sys.exit(app.exec_())

if __name__ == "__main__":
	main()