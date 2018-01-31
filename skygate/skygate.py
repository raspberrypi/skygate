#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango, Gdk, GLib, GdkPixbuf
from pkg_resources import resource_filename
import skygate.misc
from skygate.gateway import *
from skygate.habscreen import *
from skygate.lorascreen import *
from skygate.rttyscreen import *
from skygate.gpsscreen import *
from skygate.ssdvscreen import *
import configparser
import datetime
import string
	

class SkyGate:
	def __init__(self):
		self.CurrentWindow = None
		self.CurrentParent = None
		self.LatestLoRaSentence = None
		self.LatestLoRaPacketHeader = None
		self.LatestLoRaValues = None
		self.LatestRTTYSentence = None
		self.LatestRTTYValues = None
		self.LatestHABValues = None
		self.SelectedSSDVIndex = 0
		self.LoRaFrequencyError = 0
		self.CurrentGPSPosition = None
		self.SettingsEditBox = None

		self.GladeFile=resource_filename('skygate',
			'skygate.glade')
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.GladeFile)
		self.builder.connect_signals(self)

		self.windowMain = self.builder.get_object("windowMain")
		self.frameMain = self.builder.get_object("frameMain")
		self.frameDefault = self.builder.get_object("frameDefault")

		# Stop windows from getting too large and expanding main window
		# self.windowMain.set_resizable(False)
		
		# Selectable screens
		self.HABScreen = HABScreen(self.builder)
		self.LoRaScreen = LoRaScreen(self.builder)
		self.RTTYScreen = RTTYScreen(self.builder)
		self.GPSScreen = GPSScreen(self.builder)
		self.SSDVScreen = SSDVScreen(self.builder)
		self.frameSettings = self.builder.get_object("frameSettings")
		
		# Show default window
		self.SetNewWindow(self.frameDefault)

		# Main screen widgets - upper status bar
		# self.lblLoRaPayload = self.builder.get_object("lblLoRaPayload")
		# self.lblLoRaTime = self.builder.get_object("lblLoRaTime")
		# self.lblLoRaLat = self.builder.get_object("lblLoRaLat")
		# self.lblLoRaLon = self.builder.get_object("lblLoRaLon")
		# self.lblLoRaAlt = self.builder.get_object("lblLoRaAlt")
		
		# Main screen widgets - lower status bar
		# self.lblTime = self.builder.get_object("lblTime")
		# self.lblLat = self.builder.get_object("lblLat")
		# self.lblLon = self.builder.get_object("lblLon")
		# self.lblAlt = self.builder.get_object("lblAlt")
		# self.lblSats = self.builder.get_object("lblSats")
		
		# Settings screen
		# This presently is done as-required
		
		# Size main window to match the official Pi display, if we can
		ScreenInfo = Gdk.Screen.get_default()
		ScreenWidth = ScreenInfo.get_width()
		ScreenHeight = ScreenInfo.get_height()
		# Set to size of official display, or available space, whichever is smaller
		self.windowMain.resize(min(ScreenWidth, 800), min(ScreenHeight, 414))
		# If this is the official touchscreen or smaller, position at top-left
		if (ScreenWidth <= 800) or (ScreenHeight <= 480):
			self.windowMain.move(0,0)
		else:
			self.windowMain.move(100,100)
			
		self.windowMain.show_all()
				
		self.PositionDlFldigi()
		
		# Read config file
		self.ConfigFileName = 'skygate.ini'
		self.LoadSettingsFromFile(self.ConfigFileName)
		
		# Show current settings
		self.LoRaScreen.ShowLoRaFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)
		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
				
		# Timer for updating UI
		GObject.timeout_add_seconds(1, self.ssdv_update_timer)

		# Gateway
		self.gateway = gateway(CarID=self.ChaseCarID, CarPeriod=30, CarEnabled=self.ChaseCarEnabled,
								RadioCallsign=self.ReceiverCallsign,
								LoRaChannel=1, LoRaFrequency=self.LoRaFrequency, LoRaMode=self.LoRaMode, EnableLoRaUpload=self.EnableLoRaUpload,
								RTTYFrequency=self.RTTYFrequency,
								OnNewGPSPosition=self._NewGPSPosition,
								OnNewRTTYData=self._NewRTTYData, OnNewRTTYSentence=self._NewRTTYSentence,
								OnNewLoRaSentence=self._NewLoRaSentence, OnNewLoRaSSDV=self._NewLoRaSSDV, OnLoRaFrequencyError=self._LoRaFrequencyError,
								GPSDevice=self.GPSDevice)
		if self.gateway.gps.IsOpen:
			self.GPSScreen.ShowPortStatus("OK")
		else:
			self.GPSScreen.ShowPortStatus("Failed to open GPS device " + self.GPSDevice)

		self.gateway.run()

	def AdjustLoRaFrequency(self, Delta):
		# Adjust and set frequency
		self.LoRaFrequency = self.LoRaFrequency + Delta
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
		
		# Update screens
		self.LoRaScreen.ShowLoRaFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)

	def AdjustRTTYFrequency(self, Delta):
		# Adjust and set frequency
		self.RTTYFrequency = self.RTTYFrequency + Delta
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)
		
		# Update screens
		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
		
	# Main window signals
	def onDeleteWindow(self, *args):
		self.ShowDlFldigi(False)
		Gtk.main_quit(*args)
		
	def on_windowMain_check_resize(self, window):
		pass

	# Main window button signals
	def on_buttonHAB_clicked(self, button):
		self.SetNewWindow(self.HABScreen.frame)
	
	def on_buttonLoRa_clicked(self, button):
		self.SetNewWindow(self.LoRaScreen.frame)
		
	def on_buttonRTTY_clicked(self, button):
		self.SetNewWindow(self.RTTYScreen.frame)
		
	def on_buttonGPS_clicked(self, button):
		self.SetNewWindow(self.GPSScreen.frame)
		
	def on_buttonSSDV_clicked(self, button):
		self.SetNewWindow(self.SSDVScreen.frame)
		self.SelectedSSDVIndex = 0
		self.SSDVScreen.ShowFile(self.SelectedSSDVIndex, True)
		
	def on_buttonSettings_clicked(self, button):
		self.PopulateSettingsScreen()
		self.SetKeyboardCase(False)
		self.SetNewWindow(self.frameSettings)
		
	def on_AutoScroll(self, *args):
		ScrolledWindow = args[0]
		adj = ScrolledWindow.get_vadjustment()
		adj.set_value(adj.get_upper() - adj.get_page_size())		
	
	# HAB window signals
	def on_btnHABAuto_toggled(self, button):
		self.HABScreen.RadioButtonsChanged()
	
	# LoRa window signals
	def on_btnLoRaDown_clicked(self, button):
		self.AdjustLoRaFrequency(-0.001)
	
	def on_btnLoRaUp_clicked(self, button):
		self.AdjustLoRaFrequency(0.001)
	
	# RTTY window signals
	def on_btnRTTYDown_clicked(self, button):
		self.AdjustRTTYFrequency(-0.0005)

	def on_btnRTTYUp_clicked(self, button):
		self.AdjustRTTYFrequency(0.0005)

	def on_btnRTTYdlfldigi_clicked(self, button):
		self.PositionDlFldigi()
		self.ShowDlFldigi(True)
		
	def on_textRTTY_button_press_event(self, thing1, thing2):
		self.ShowDlFldigi(False)
	# GPS window signals
		
	# (none)
	
	# SSDV window signals
	def on_btnSSDVPrevious_clicked(self, button):
		self.SelectedSSDVIndex += 1
		self.SSDVScreen.ShowFile(self.SelectedSSDVIndex, True)
	
	def on_btnSSDVNext_clicked(self, button):
		if self.SelectedSSDVIndex > 0:
			self.SelectedSSDVIndex -= 1
		self.SSDVScreen.ShowFile(self.SelectedSSDVIndex, True)
	
	# Settings window signals
	def on_btnSettingsSave_clicked(self, button):
		self.LoadFromSettingsScreen()
		self.ApplySettings()
		self.SaveSettingsToFile(self.ConfigFileName)
		
	def on_btnSettingsCancel_clicked(self, button):
		self.PopulateSettingsScreen()
	
	def on_textSettings_focus(self, textbox, event):
		self.SettingsEditBox = textbox
	
	def on_button1_clicked(self, button):
		if self.SettingsEditBox:
			if button.get_label() == '<-':		
				self.SettingsEditBox.set_text(self.SettingsEditBox.get_text()[:-1])
			else:
				self.SettingsEditBox.set_text(self.SettingsEditBox.get_text() + button.get_label())
				
	def on_btnShift_clicked(self, button):
		ToUpper = self.builder.get_object("buttonQ").get_label() == 'q'
		self.SetKeyboardCase(ToUpper)
		
	# Gtk UI updaters
	def _UpdateGPSPosition(self):
		Position = self.CurrentGPSPosition

		# GPS screen
		self.GPSScreen.ShowPosition(Position)
		
		# HAB screen
		self.HABScreen.NewGPSPosition(Position)
		
		return False	# So we don't get called again, until there's a new GPS position
	
	def PositionDlFldigi(self):
		os.system('wmctrl -r "dl-fldigi - waterfall-only mode" -e 0,' + str(self.windowMain.get_position()[0]+0) + ',' + str(self.windowMain.get_position()[1]+150) + ',700,173')

	def ShowDlFldigi(self, Show):
		os.system('wmctrl -r "dl-fldigi - waterfall-only mode" -b add,' + ('above' if Show else 'below'))
		if Show:
			os.system('wmctrl -a "dl-fldigi - waterfall-only mode"')

	def _UpdateCurrentRTTY(self):
		self.RTTYScreen.ShowCurrentRTTY(self.CurrentRTTY[-80:])	
		return False
		
	def _UpdateRTTYSentence(self):	
		# Update HAB screen
		self.HABScreen.NewRTTYValues(self.LatestRTTYValues)

		# Update RTTY screen
		self.RTTYScreen.AppendLine(str(self.LatestRTTYSentence + '\n'))
	
		return False

	def _UpdateLoRaSentence(self):		
		# Update HAB screen
		self.HABScreen.NewLoRaValues(self.LatestLoRaValues)

		# Update LoRa screen
		self.LoRaScreen.AppendLine(str(self.LatestLoRaSentence))
	
		return False
			
	def _UpdateLoRaSSDV(self):
		# Update LoRa screen
		self.LoRaScreen.AppendLine('SSDV packet, payload ID: ' + self.LatestLoRaPacketHeader['callsign'] + ', image #: ' + str(self.LatestLoRaPacketHeader['imagenumber']) + ', packet #: ' + str(self.LatestLoRaPacketHeader['packetnumber']))
		
		return False

	def _UpdateLoRaFrequencyError(self):
		# LoRa Frequency Error
		self.LoRaScreen.ShowFrequencyError(self.LoRaFrequencyError)			
	
		return False
		
	# Callbacks
	
	def _NewGPSPosition(self, Position):
		self.CurrentGPSPosition = Position
		GLib.idle_add(self._UpdateGPSPosition)

	def _NewRTTYData(self, CurrentRTTY):
		self.CurrentRTTY = CurrentRTTY
		GLib.idle_add(self._UpdateCurrentRTTY)

	def _NewRTTYSentence(self, Sentence):
		self.LatestRTTYSentence = Sentence
		self.LatestRTTYValues = self.DecodeSentence(Sentence)
		if self.LatestRTTYValues:
			self.LatestHABValues = self.LatestRTTYValues
			GLib.idle_add(self._UpdateRTTYSentence)

	def _NewLoRaSentence(self, Sentence):
		self.LatestLoRaSentence = Sentence
		self.LatestLoRaValues = self.DecodeSentence(Sentence)

		if self.LatestLoRaValues:
			self.LatestHABValues = self.LatestLoRaValues
			GLib.idle_add(self._UpdateLoRaSentence)

	def _NewLoRaSSDV(self, header):
		self.LatestLoRaPacketHeader = header		
		GLib.idle_add(self._UpdateLoRaSSDV)
		
	def _LoRaFrequencyError(self, FrequencyError):
		self.LoRaFrequencyError = FrequencyError
		GLib.idle_add(self._UpdateLoRaFrequencyError)
			
	# Functions
	
	def SetNewWindow(self, SomeWindow):
		# Hide dl-fldigi in case it's been brought up on top of us
		self.ShowDlFldigi(False)
		
		# Send existing screen back to mummy
		if self.CurrentWindow:
			self.CurrentWindow.reparent(self.CurrentParent)
		
		# Swap back to initial screen if user taps the same button again
		if SomeWindow == self.CurrentWindow:
			SomeWindow = self.frameDefault
			
		# Get parent so we can return window after use
		self.CurrentParent = SomeWindow.get_parent()
		self.CurrentWindow = SomeWindow

		# Load window as requested
		self.CurrentWindow.reparent(self.frameMain)
				
	def LoadSettingsFromFile(self, FileName):
		# Open config file
		config = configparser.RawConfigParser()   
		config.read(FileName)

		self.ReceiverCallsign = config.get('Receiver', 'Callsign', fallback='CHANGE_ME')

		self.LoRaFrequency = float(config.get('LoRa', 'Frequency', fallback='434.450'))
		self.LoRaMode = int(config.get('LoRa', 'Mode', fallback='1'))
		self.EnableLoRaUpload = config.getboolean('LoRa', 'EnableUpload', fallback=False)
		
		self.RTTYFrequency = float(config.get('RTTY', 'Frequency', fallback='434.250'))
		
		self.ChaseCarID = config.get('ChaseCar', 'ID', fallback='CHANGE_ME')
		self.ChaseCarPeriod = int(config.get('ChaseCar', 'Period', fallback='30'))
		self.ChaseCarEnabled = config.getboolean('ChaseCar', 'EnableUpload', fallback=False)

		self.GPSDevice = config.get('GPS', 'Device', fallback='/dev/ttyAMA0')

	def ApplySettings(self):
		# LoRa
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
		self.gateway.lora.SetStandardLoRaParameters(self.LoRaMode)
		self.LoRaScreen.ShowLoRaFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)
		self.gateway.EnableLoRaUpload = self.EnableLoRaUpload
		
		# RTTY
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)
		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
		
		# Car
		self.gateway.habitat.ChaseCarEnabled = self.ChaseCarEnabled
		
		# GPS
		self.gateway.gps.SetDevice(self.GPSDevice)
		if self.gateway.gps.IsOpen:
			self.GPSScreen.ShowPortStatus("OK")
		else:
			self.GPSScreen.ShowPortStatus("Failed to open GPS device " + self.GPSDevice)
	
	def SaveSettingsToFile(self, FileName):
		config = configparser.RawConfigParser()   
		config.read(FileName)

		if not config.has_section('Receiver'):
			config.add_section('Receiver')
		config.set('Receiver', 'Callsign', self.ReceiverCallsign)
		
		if not config.has_section('LoRa'):
			config.add_section('LoRa')
		config.set('LoRa', 'Frequency', self.LoRaFrequency)
		config.set('LoRa', 'Mode', self.LoRaMode)
		config.set('LoRa', 'EnableUpload', BoolToStr(self.EnableLoRaUpload))
		
		if not config.has_section('RTTY'):
			config.add_section('RTTY')
		config.set('RTTY', 'Frequency', self.RTTYFrequency)
		
		if not config.has_section('ChaseCar'):
			config.add_section('ChaseCar')
		config.set('ChaseCar', 'ID', self.ChaseCarID)
		config.set('ChaseCar', 'Period', self.ChaseCarPeriod)
		config.set('ChaseCar', 'EnableUpload', BoolToStr(self.ChaseCarEnabled))
		
		if not config.has_section('GPS'):
			config.add_section('GPS')
		# if self.GPSDevice:
		config.set('GPS', 'Device', self.GPSDevice)
		
		with open(FileName, 'wt') as configfile:
			config.write(configfile)
		
	def PopulateSettingsScreen(self):
		self.builder.get_object("textSettingsReceiverCallsign").set_text(self.ReceiverCallsign)
		self.builder.get_object("chkEnableLoRaUpload").set_active(self.EnableLoRaUpload)
		
		self.builder.get_object("textSettingsLoRaFrequency").set_text("{0:.3f}".format(self.LoRaFrequency))
		self.builder.get_object("cmbSettingsLoRaMode").set_active(self.LoRaMode)
		
		self.builder.get_object("textSettingsRTTYFrequency").set_text("{0:.4f}".format(self.RTTYFrequency))
		
		self.builder.get_object("textSettingsChaseCarID").set_text(self.ChaseCarID)
		self.builder.get_object("textSettingsChaseCarPeriod").set_text(str(self.ChaseCarPeriod))
		self.builder.get_object("chkEnableChaseCarUpload").set_active(self.ChaseCarEnabled)
		
		self.builder.get_object("textSettingsGPSDevice").set_text(self.GPSDevice)
	
	def LoadFromSettingsScreen(self):
		self.ReceiverCallsign = self.builder.get_object("textSettingsReceiverCallsign").get_text()
		self.EnableLoRaUpload = self.builder.get_object("chkEnableLoRaUpload").get_active()
		
		self.LoRaFrequency = float(self.builder.get_object("textSettingsLoRaFrequency").get_text())
		self.LoRaMode = self.builder.get_object("cmbSettingsLoRaMode").get_active()
		
		self.RTTYFrequency = float(self.builder.get_object("textSettingsRTTYFrequency").get_text())
		
		self.ChaseCarID = self.builder.get_object("textSettingsChaseCarID").get_text()
		self.ChaseCarPeriod = int(self.builder.get_object("textSettingsChaseCarPeriod").get_text())
		self.ChaseCarEnabled = self.builder.get_object("chkEnableChaseCarUpload").get_active()
		
		self.GPSDevice = self.builder.get_object("textSettingsGPSDevice").get_text()

	def SetKeyboardCase(self, ToUpper):
		for character in string.ascii_uppercase:
			button = self.builder.get_object("button" + character)
			button.set_label(character if ToUpper else character.lower())
		
	def DecodeSentence(self, sentence):
		# $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
		try:
			list = sentence.split(",")
			
			payload = list[0].split("$")
			payload = payload[len(payload)-1]
			
			TimeStamp = datetime.datetime.strptime(list[2], '%H:%M:%S')

			return {'payload': payload, 'time': TimeStamp, 'lat': float(list[3]), 'lon': float(list[4]), 'alt': float(list[5])}
		except:
			return None
		
	def ssdv_update_timer(self, *args):
		# Only update the image on the SSDV window if it's being displayed
		if self.CurrentWindow == self.SSDVScreen.frame:
			self.SSDVScreen.ShowFile(self.SelectedSSDVIndex, False)
			
		self.HABScreen.ShowTimeSinceData()
			
		return True	# Run again

		
hwg = SkyGate()
Gtk.main()
	
