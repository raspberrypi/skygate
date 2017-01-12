#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango, GdkPixbuf
from gateway import *
import configparser

def BoolToStr(value):
	if value:
		return '1'
	else:
		return '0'
		
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
		self.DisplayedSSDVFileName = ''
		self.SSDVModificationDate = 0
		self.LoRaFrequencyError = 999
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file("skygate.glade")
		self.builder.connect_signals(self)

		self.windowMain = self.builder.get_object("windowMain")
		self.frameMain = self.builder.get_object("frameMain")
		self.frameDefault = self.builder.get_object("frameDefault")

		# Selectable screens
		self.frameHAB = self.builder.get_object("frameHAB")
		self.frameLoRa = self.builder.get_object("frameLoRa")
		self.frameRTTY = self.builder.get_object("frameRTTY")
		self.frameGPS = self.builder.get_object("frameGPS")
		self.frameSSDV = self.builder.get_object("frameSSDV")
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
		
		# HAB Screen
		self.textHABLoRa = self.builder.get_object("textHABLoRa")
		self.textHABRTTY = self.builder.get_object("textHABRTTY")
		self.lblHABDirection = self.builder.get_object("lblHABDirection")
		self.lblHABDistance = self.builder.get_object("lblHABDistance")
		self.lblHABLoRaFrequency = self.builder.get_object("lblHABLoRaFrequency")
		self.lblHABRTTYFrequency = self.builder.get_object("lblHABRTTYFrequency")
		
		# LoRa Screen
		self.textLoRa = self.builder.get_object("textLoRa")
		self.scrollLoRa = self.builder.get_object("scrollLoRa")
		self.lblLoRaFrequency = self.builder.get_object("lblLoRaFrequency")
		self.lblLoRaFrequencyError = self.builder.get_object("lblLoRaFrequencyError")		
		
		# RTTY Screen
		self.textRTTY = self.builder.get_object("textRTTY")
		self.lblCurrentRTTY = self.builder.get_object("lblCurrentRTTY")
		self.scrollRTTY = self.builder.get_object("scrollRTTY")
		self.lblRTTYFrequency = self.builder.get_object("lblRTTYFrequency")
		
		# GPS Screen
		self.textGPS = self.builder.get_object("textGPS")
		
		# SSDV Screen
		self.imageSSDV = self.builder.get_object("imageSSDV")
		self.boxSSDV = self.builder.get_object("boxSSDV")
		self.lblSSDVInfo = self.builder.get_object("lblSSDVInfo")
		
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
		self.lblHABLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.lblHABRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')

		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))

		self.lblRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		
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
		self.SetNewWindow(self.frameHAB)
	
	def on_buttonLoRa_clicked(self, button):
		self.SetNewWindow(self.frameLoRa)
		
	def on_buttonRTTY_clicked(self, button):
		self.SetNewWindow(self.frameRTTY)
		
	def on_buttonGPS_clicked(self, button):
		self.SetNewWindow(self.frameGPS)
		
	def on_buttonSSDV_clicked(self, button):
		self.SetNewWindow(self.frameSSDV)
		self.SelectedSSDVIndex = 0
		self.ShowSSDVFile(self.SelectedSSDVIndex, True)
		
	def on_buttonSettings_clicked(self, button):
		self.PopulateSettingsScreen()
		self.SetNewWindow(self.frameSettings)
		
	# HAB window signals
	
	# LoRa window signals
	def on_btnLoRaDown_clicked(self, button):
		self.LoRaFrequency = self.LoRaFrequency - 0.001
		self.lblHABLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
	
	def on_btnLoRaUp_clicked(self, button):
		self.LoRaFrequency = self.LoRaFrequency + 0.001
		self.lblHABLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.gateway.lora.SetLoRaFrequency(self.LoRaFrequency)
	
	# RTTY window signals
	def on_btnRTTYDown_clicked(self, button):
		self.RTTYFrequency = self.RTTYFrequency - 0.0005
		self.lblHABRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		self.lblRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)

	def on_btnRTTYUp_clicked(self, button):
		self.RTTYFrequency = self.RTTYFrequency + 0.0005
		self.lblHABRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		self.lblRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)
		
	# GPS window signals
	
	# SSDV window signals
	def on_btnSSDVPrevious_clicked(self, button):
		self.SelectedSSDVIndex += 1
		self.ShowSSDVFile(self.SelectedSSDVIndex, True)
	
	def on_btnSSDVNext_clicked(self, button):
		if self.SelectedSSDVIndex > 0:
			self.SelectedSSDVIndex -= 1
		self.ShowSSDVFile(self.SelectedSSDVIndex, True)
	
	# Settings window signals
	def on_btnSettingsSave_clicked(self, button):
		self.LoadFromSettingsScreen()
		self.ApplySettings()
		self.SaveSettingsToFile(self.ConfigFileName)
		
	def on_btnSettingsCancel_clicked(self, button):
		self.PopulateSettingsScreen()

	# General functions
	def ShowDistanceAndDirection(self):
		if self.LatestHABValues and self.gateway.gps:
			DistanceToHAB = CalculateDistance(self.LatestHABValues['lat'], self.LatestHABValues['lon'], self.gateway.gps.Position()['lat'], self.gateway.gps.Position()['lon'])
			DirectionToHAB = CalculateDirection(self.LatestHABValues['lat'], self.LatestHABValues['lon'], self.gateway.gps.Position()['lat'], self.gateway.gps.Position()['lon'])
																			
			self.lblHABDirection.set_markup("<span font='48'>" + ["N","NE","E","SE","S","SW","W","NW","N"][int(round(DirectionToHAB/45))] + "</span>")
			self.lblHABDistance.set_markup("<span font='32'>" + "%.3f" % (DistanceToHAB/1000) + " km</span>")
	
	def SetNewWindow(self, SomeWindow):
		if self.CurrentWindow:
			self.CurrentWindow.reparent(self.CurrentParent)
			
		self.CurrentParent = SomeWindow.get_parent()
		self.CurrentWindow = SomeWindow
		
		self.CurrentWindow.reparent(self.frameMain)
		
		ShowDlFldigi(SomeWindow == self.frameRTTY)

		
	def GetSSDVFileName(self, SelectedFileIndex=0):
		# Get list of jpg files
		date_file_list = []
		for file in glob.glob('images/*.jpg'):
			stats = os.stat(file)
			lastmod_date = time.localtime(stats[8])
			date_file_tuple = lastmod_date, file
			date_file_list.append(date_file_tuple)

		if len(date_file_list) == 0:
			return ''

		if SelectedFileIndex < 0:
			SelectedFileIndex = 0

		if SelectedFileIndex >= len(date_file_list):
			SelectedFileIndex = len(date_file_list)-1
			
		Index = len(date_file_list) - SelectedFileIndex - 1
			
		selection = sorted(date_file_list)[Index]
		
		return selection[1]

	def ExtractImageInfoFromFileName(self, FileName):
		print(FileName)
		temp = FileName.split('/')
		temp = temp[1].split('.')
		fields = temp[0].split('_')
		return {'callsign': fields[0], 'imagenumber': fields[1]}
		
	def ShowSSDVFile(self, SelectedFileIndex, Always):
		# 0 means latest file; 1 onwards means 1st file (oldest), etc
		FileName = self.GetSSDVFileName(SelectedFileIndex)
		if FileName != '':
			ModificationDate = time.ctime(os.path.getmtime(FileName))
			if Always or (FileName != self.DisplayedSSDVFileName) or (ModificationDate != self.SSDVModificationDate):
				# self.imageSSDV.set_from_file(FileName)
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(FileName)
				pixbuf = pixbuf.scale_simple(552, 414, GdkPixbuf.InterpType.BILINEAR)
				self.imageSSDV.set_from_pixbuf(pixbuf)

				ImageInfo = self.ExtractImageInfoFromFileName(FileName)
				self.lblSSDVInfo.set_text('Callsign ' + ImageInfo['callsign'] + ', Image ' + ImageInfo['imagenumber'])

		
			self.DisplayedSSDVFileName = FileName
			self.SSDVModificationDate = ModificationDate
		
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
		self.lblHABLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.gateway.EnableLoRaUpload = self.EnableLoRaUpload
		
		# RTTY
		self.gateway.rtty.SetFrequency(self.RTTYFrequency)
		self.lblHABRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		self.lblRTTYFrequency.set_text("{0:.4f}".format(self.RTTYFrequency) + ' MHz')
		
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
			buffer = self.textGPS.get_buffer()
			if buffer.get_line_count() > 50:
				start = buffer.get_iter_at_line(0)
				end = buffer.get_iter_at_line(1)
				buffer.delete(start, end)
			buffer.insert_at_cursor(str(CarPosition) + "\r\n")
			# scroll to bottom
			adjustment = self.frameGPS.get_vadjustment()
			adjustment.set_value(adjustment.get_upper())
			
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
			buffer = self.textHABLoRa.get_buffer()		
			start = buffer.get_iter_at_offset(0)
			end = buffer.get_iter_at_offset(999)
			buffer.delete(start, end)
			buffer.insert_at_cursor(self.LatestLoRaValues['payload'] + "\n" +
									self.LatestLoRaValues['time'] + "\n" +
									"{0:.5f}".format(self.LatestLoRaValues['lat']) + "\n" +
									"{0:.5f}".format(self.LatestLoRaValues['lon']) + "\n" +
									str(self.LatestLoRaValues['alt']) + 'm')
			self.ShowDistanceAndDirection()

			# LoRa screen
			buffer = self.textLoRa.get_buffer()
			if buffer.get_line_count() > 50:
				start = buffer.get_iter_at_line(0)
				end = buffer.get_iter_at_line(1)
				buffer.delete(start, end)
			buffer.insert_at_cursor(str(self.LatestLoRaSentence))
			# scroll to bottom
			adjustment = self.scrollLoRa.get_vadjustment()
			adjustment.set_value(adjustment.get_upper())
			
		# LoRa SSDV
		if self.gateway.LatestLoRaPacketHeader != self.LatestLoRaPacketHeader:
			# New SSDV packet
			self.LatestLoRaPacketHeader = self.gateway.LatestLoRaPacketHeader
			buffer = self.textLoRa.get_buffer()
			if buffer.get_line_count() > 50:
				start = buffer.get_iter_at_line(0)
				end = buffer.get_iter_at_line(1)
				buffer.delete(start, end)
			buffer.insert_at_cursor(str(self.LatestLoRaPacketHeader) + '\n')
			# scroll to bottom
			adjustment = self.scrollLoRa.get_vadjustment()
			adjustment.set_value(adjustment.get_upper())
		
		# LoRa RSSI etc
		if self.gateway.LoRaFrequencyError != self.LoRaFrequencyError:
			self.LoRaFrequencyError = self.gateway.LoRaFrequencyError
			self.lblLoRaFrequencyError.set_text("Err: {0:.1f}".format(self.LoRaFrequencyError) + ' kHz')
			

		self.lblCurrentRTTY.set_text(self.gateway.rtty.CurrentRTTY)
		
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
				buffer = self.textHABRTTY.get_buffer()		
				start = buffer.get_iter_at_offset(0)
				end = buffer.get_iter_at_offset(999)
				buffer.delete(start, end)
				buffer.insert_at_cursor(self.LatestRTTYValues['payload'] + "\n" +
										self.LatestRTTYValues['time'] + "\n" +
										"{0:.5f}".format(self.LatestRTTYValues['lat']) + "\n" +
										"{0:.5f}".format(self.LatestRTTYValues['lon']) + "\n" +
										str(self.LatestRTTYValues['alt']) + 'm')
				self.ShowDistanceAndDirection()

				# RTTY screen
				buffer = self.textRTTY.get_buffer()
				if buffer.get_line_count() > 50:
					start = buffer.get_iter_at_line(0)
					end = buffer.get_iter_at_line(1)
					buffer.delete(start, end)
				buffer.insert_at_cursor(str(self.LatestRTTYSentence + '\n'))
				# scroll to bottom
				adjustment = self.scrollRTTY.get_vadjustment()
				adjustment.set_value(adjustment.get_upper())
			
		# Only update the image on the SSDV window if it's being displayed
		if self.CurrentWindow == self.frameSSDV:
			self.ShowSSDVFile(self.SelectedSSDVIndex, False)
			
		return True	# Run again

		
hwg = SkyGate()
Gtk.main()
	