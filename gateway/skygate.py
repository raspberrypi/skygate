#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango, GdkPixbuf
import misc
from gateway import *
from habscreen import *
from lorascreen import *
from rttyscreen import *
from gpsscreen import *
from ssdvscreen import *
import configparser
	
def PositionDlFldigi(window):
	os.system('wmctrl -r "dl-fldigi - waterfall-only mode" -e 0,' + str(window.get_position()[0]+6) + ',' + str(window.get_position()[1]+250) + ',700,173')

def ShowDlFldigi(Show):
	os.system('wmctrl -r "dl-fldigi - waterfall-only mode" -b add,' + ('above' if Show else 'below'))

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
		self.LoRaFrequencyError = 999
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file("skygate.glade")
		self.builder.connect_signals(self)

		self.windowMain = self.builder.get_object("windowMain")
		self.frameMain = self.builder.get_object("frameMain")
		self.frameDefault = self.builder.get_object("frameDefault")

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
		self.lblLoRaPayload = self.builder.get_object("lblLoRaPayload")
		self.lblLoRaTime = self.builder.get_object("lblLoRaTime")
		self.lblLoRaLat = self.builder.get_object("lblLoRaLat")
		self.lblLoRaLon = self.builder.get_object("lblLoRaLon")
		self.lblLoRaAlt = self.builder.get_object("lblLoRaAlt")
		
		# Main screen widgets - lower status bar
		self.lblTime = self.builder.get_object("lblTime")
		self.lblLat = self.builder.get_object("lblLat")
		self.lblLon = self.builder.get_object("lblLon")
		self.lblAlt = self.builder.get_object("lblAlt")
		self.lblSats = self.builder.get_object("lblSats")
		
		# Settings screen
		
		self.windowMain.resize(800,480)
		self.windowMain.move(100,100)
		self.windowMain.show_all()
		
		PositionDlFldigi(self.windowMain)
		
		# Default settings
		self.ReceiverCallsign = 'Python'
		self.EnableLoRaUpload = True
		
		self.LoRaFrequency = 434.450
		self.LoRaMode = 1
		
		self.RTTYFrequency = 434.250
		
		self.ChaseCarID = 'Python'
		self.ChaseCarPeriod = 30
		self.ChaseCarEnabled = True
		
		# Read config file
		self.ConfigFileName = 'skygate.ini'
		self.LoadSettingsFromFile(self.ConfigFileName)
		
		# Show current settings
		self.HABScreen.ShowLoRaFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)
		self.HABScreen.ShowRTTYFrequency(self.RTTYFrequency)

		self.LoRaScreen.ShowLoRaFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)

		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
		
		GObject.timeout_add_seconds(1, self.screen_updates_timer)

		# Gateway
		self.gateway = gateway(CarID=self.ChaseCarID, CarPeriod=30, CarEnabled=self.ChaseCarEnabled, RadioCallsign=self.ReceiverCallsign, LoRaChannel=1, LoRaFrequency=self.LoRaFrequency, LoRaMode=self.LoRaMode, EnableLoRaUpload=self.EnableLoRaUpload, RTTYFrequency=self.RTTYFrequency)
		self.gateway.run()

	# Main window signals
	def onDeleteWindow(self, *args):
		ShowDlFldigi(False)
		Gtk.main_quit(*args)
		
	def on_windowMain_check_resize(self, window):
		PositionDlFldigi(window)

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
		self.SetNewWindow(self.frameSettings)
		
	# LoRa window signals
	def on_btnLoRaDown_clicked(self, button):
		self.LoRaFrequency = self.LoRaFrequency - 0.001
		self.HABScreen.ShowFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)
		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
	
	def on_btnLoRaUp_clicked(self, button):
		self.LoRaFrequency = self.LoRaFrequency + 0.001
		self.HABScreen.ShowFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)
		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
	
	# RTTY window signals
	def on_btnRTTYDown_clicked(self, button):
		self.RTTYFrequency = self.RTTYFrequency - 0.0005
		self.HABScreen.ShowRTTYFrequency(self.RTTYFrequency)
		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)

	def on_btnRTTYUp_clicked(self, button):
		self.RTTYFrequency = self.RTTYFrequency + 0.0005
		self.HABScreen.ShowRTTYFrequency(self.RTTYFrequency)
		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)
		
	# GPS window signals
	
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
	
	def SetNewWindow(self, SomeWindow):
		if self.CurrentWindow:
			self.CurrentWindow.reparent(self.CurrentParent)
			
		self.CurrentParent = SomeWindow.get_parent()
		self.CurrentWindow = SomeWindow
		
		self.CurrentWindow.reparent(self.frameMain)
		
		ShowDlFldigi(SomeWindow == self.RTTYScreen.frame)
				
	def LoadSettingsFromFile(self, FileName):
		if os.path.isfile(FileName):
			# Open config file
			config = configparser.RawConfigParser()   
			config.read(FileName)
								
			self.ReceiverCallsign = config.get('Receiver', 'Callsign')
			
			self.LoRaFrequency = float(config.get('LoRa', 'Frequency'))
			self.LoRaMode = int(config.get('LoRa', 'Mode'))
			self.EnableLoRaUpload = config.getboolean('LoRa', 'EnableUpload')
			
			self.RTTYFrequency = float(config.get('RTTY', 'Frequency'))
			
			self.ChaseCarID = config.get('ChaseCar', 'ID')
			self.ChaseCarPeriod = int(config.get('ChaseCar', 'Period'))
			self.ChaseCarEnabled = config.getboolean('ChaseCar', 'EnableUpload')

	def ApplySettings(self):
		# LoRa
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
		self.gateway.lora.SetStandardLoRaParameters(self.LoRaMode)
		self.HABScreen.ShowFrequencyAndMode(self.LoRaFrequency, self.LoRaMode)
		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.gateway.EnableLoRaUpload = self.EnableLoRaUpload
		
		# RTTY
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)
		self.HABScreen.ShowRTTYFrequency(self.RTTYFrequency)
		self.RTTYScreen.ShowRTTYFrequency(self.RTTYFrequency)
		
		# Car
		self.gateway.habitat.ChaseCarEnabled = self.ChaseCarEnabled
	
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
	
	def LoadFromSettingsScreen(self):
		self.ReceiverCallsign = self.builder.get_object("textSettingsReceiverCallsign").get_text()
		self.EnableLoRaUpload = self.builder.get_object("chkEnableLoRaUpload").get_active()
		
		self.LoRaFrequency = float(self.builder.get_object("textSettingsLoRaFrequency").get_text())
		self.LoRaMode = self.builder.get_object("cmbSettingsLoRaMode").get_active()
		
		self.RTTYFrequency = float(self.builder.get_object("textSettingsRTTYFrequency").get_text())
		
		self.ChaseCarID = self.builder.get_object("textSettingsChaseCarID").get_text()
		self.ChaseCarPeriod = int(self.builder.get_object("textSettingsChaseCarPeriod").get_text())
		self.ChaseCarEnabled = self.builder.get_object("chkEnableChaseCarUpload").get_active()
		
	def DecodeSentence(self, sentence):
		# $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
		try:
			list = sentence.split(",")
			
			payload = list[0].split("$")
			payload = payload[len(payload)-1]

			return {'payload': payload, 'time': list[2], 'lat': float(list[3]), 'lon': float(list[4]), 'alt': float(list[5])}
		except:
			return None
		
	def screen_updates_timer(self, *args):
		# Local GPS
		CarPosition = self.gateway.gps.Position()
		if CarPosition:
			# Lower status bar
			self.lblTime.set_text(CarPosition['time'])
			self.lblLat.set_text("{0:.5f}".format(CarPosition['lat']))
			self.lblLon.set_text("{0:.5f}".format(CarPosition['lon']))
			self.lblAlt.set_text(str(int(CarPosition['alt'])) + ' m')
			self.lblSats.set_text(str(CarPosition['sats']) + ' Sats')
			
			# GPS screen
			self.GPSScreen.AppendLine(str(CarPosition) + "\n")
			
		# LoRa
		if self.gateway.LatestLoRaSentence != self.LatestLoRaSentence:
			# New sentence
			# Top status line
			self.LatestLoRaSentence = self.gateway.LatestLoRaSentence
			self.LatestLoRaValues = self.DecodeSentence(self.LatestLoRaSentence)
			if self.LatestLoRaValues:
				self.LatestHABValues = self.LatestLoRaValues
				self.lblLoRaPayload.set_text(self.LatestLoRaValues['payload'])
				self.lblLoRaTime.set_text(self.LatestLoRaValues['time'])
				self.lblLoRaLat.set_text("{0:.5f}".format(self.LatestLoRaValues['lat']))
				self.lblLoRaLon.set_text("{0:.5f}".format(self.LatestLoRaValues['lon']))
				self.lblLoRaAlt.set_text(str(self.LatestLoRaValues['alt']) + 'm')
			
			# HAB screen updates
			self.HABScreen.ShowLoRaValues(self.LatestLoRaValues, self.gateway.gps.Position())

			# LoRa screen
			self.LoRaScreen.AppendLine(str(self.LatestLoRaSentence))
			
		# LoRa SSDV
		if self.gateway.LatestLoRaPacketHeader != self.LatestLoRaPacketHeader:
			# New SSDV packet
			self.LatestLoRaPacketHeader = self.gateway.LatestLoRaPacketHeader
			
			self.LoRaScreen.AppendLine(str(self.LatestLoRaPacketHeader) + '\n')
		
		# LoRa RSSI etc
		if self.gateway.LoRaFrequencyError != self.LoRaFrequencyError:
			self.LoRaFrequencyError = self.gateway.LoRaFrequencyError
			self.LoRaScreen.ShowFrequencyError(self.LoRaFrequencyError)			

		self.RTTYScreen.ShowCurrentRTTY(self.gateway.rtty.CurrentRTTY)
		
		# RTTY
		if self.gateway.LatestRTTYSentence != self.LatestRTTYSentence:
			# New sentence
			# Top status line
			self.LatestRTTYSentence = self.gateway.LatestRTTYSentence
			self.LatestRTTYValues = self.DecodeSentence(self.LatestRTTYSentence)
			if self.LatestRTTYValues:
				self.LatestHABValues = self.LatestRTTYValues
				self.lblLoRaPayload.set_text(self.LatestRTTYValues['payload'])
				self.lblLoRaTime.set_text(self.LatestRTTYValues['time'])
				self.lblLoRaLat.set_text("{0:.5f}".format(self.LatestRTTYValues['lat']))
				self.lblLoRaLon.set_text("{0:.5f}".format(self.LatestRTTYValues['lon']))
				self.lblLoRaAlt.set_text(str(self.LatestRTTYValues['alt']) + 'm')
			
				# HAB screen updates
				self.HABScreen.ShowRTTYValues(self.LatestRTTYValues, self.gateway.gps.Position())

				# RTTY screen
				self.RTTYScreen.AppendLine(str(self.LatestRTTYSentence + '\n'))
			
		# Only update the image on the SSDV window if it's being displayed
		if self.CurrentWindow == self.SSDVScreen.frame:
			self.SSDVScreen.ShowFile(self.SelectedSSDVIndex, False)
			
		return True	# Run again

		
hwg = SkyGate()
Gtk.main()
	