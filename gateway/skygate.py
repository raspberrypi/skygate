#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from gateway import *

class SkyGate:
	def __init__(self):
		self.CurrentWindow = None
		self.CurrentParent = None
		self.LatestLoRaSentence = None
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file("skygate.glade")
		# builder.add_from_file("HAB.glade")
		self.builder.connect_signals(self)

		self.windowMain = self.builder.get_object("windowMain")
		self.frameMain = self.builder.get_object("frameMain")
		self.frameDefault = self.builder.get_object("frameDefault")
		self.SetNewWindow(self.frameDefault)

		# Selectable screens
		self.frameHAB = self.builder.get_object("frameHAB")
		self.frameLoRa = self.builder.get_object("frameLoRa")
		self.frameRTTY = self.builder.get_object("frameRTTY")
		self.frameGPS = self.builder.get_object("frameGPS")
		self.frameSSDV = self.builder.get_object("frameSSDV")
		
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
		self.arrowDirection = self.builder.get_object("arrowDirection")
		self.lblHABLoRaFrequency = self.builder.get_object("lblHABLoRaFrequency")
		self.lblHABRTTYFrequency = self.builder.get_object("lblHABRTTYFrequency")
		
		# LoRa Screen
		self.textLoRa = self.builder.get_object("textLoRa")
		self.scrollLoRa = self.builder.get_object("scrollLoRa")
		self.lblLoRaFrequency = self.builder.get_object("lblLoRaFrequency")
		
		# RTTY Screen
		# self.lblRTTYFrequency = self.builder.get_object("lblRTTYFrequency")
		
		# GPS Screen
		self.textGPS = self.builder.get_object("textGPS")
		
		# SSDV Screen
		
		# Settings screen
		
		self.windowMain.resize(800,480)
		self.windowMain.move(100,100)
		self.windowMain.show_all()
		
		# Read config file
		self.LoRaFrequency = 434.450
		self.LoRaMode = 1
		self.RTTYFrequency = 434.250
		self.RTTYBaudRate = 50
		
		# Show current settings
		self.lblHABLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))
		self.lblHABRTTYFrequency.set_text("{0:.3f}".format(self.RTTYFrequency) + ' MHz, ' + str(self.RTTYBaudRate) + ' baud')

		self.lblLoRaFrequency.set_text("{0:.3f}".format(self.LoRaFrequency) + ' MHz, Mode ' + str(self.LoRaMode))

		# self.lblRTTYFrequency.set_text("{0:.3f}".format(self.RTTYFrequency) + ' MHz, ' + str(self.RTTYBaudRate) + ' baud')
		
		GObject.timeout_add_seconds(1, self.screen_updates_timer)

		# Gateway
		self.gateway = gateway()
		self.gateway.run()

	# Main window signals
	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)

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
		
	# HAB window signals
	
	# LoRa window signals
	
	# RTTY window signals
	
	# GPS window signals
	
	# SSDV window signals
	def on_btnSSDVPrevious_clicked(self, button):
		print("SSDV Previous")
	
	def on_btnSSDVNext_clicked(self, button):
		print("SSDV Next")
	
	# Settings window signals
		
	def SetNewWindow(self, SomeWindow):
		if self.CurrentWindow:
			self.CurrentWindow.reparent(self.CurrentParent)
			
		self.CurrentParent = SomeWindow.get_parent()
		self.CurrentWindow = SomeWindow
		
		self.CurrentWindow.reparent(self.frameMain)
		
	def DecodeSentence(self, sentence):
		# $BUZZ,483,10:04:27,51.95022,-2.54435,00190,5*6856
		list = sentence.split(",")
		
		payload = list[0].split("$")
		payload = payload[len(payload)-1]

		return {'payload': payload, 'time': list[2], 'lat': float(list[3]), 'lon': float(list[4]), 'alt': float(list[5])}
		
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
			# Top status line
			self.LatestLoRaSentence = self.gateway.LatestLoRaSentence
			self.LatestLoRaValues = self.DecodeSentence(self.LatestLoRaSentence)
			self.lblLoRaPayload.set_text(self.LatestLoRaValues['payload'])
			self.lblLoRaTime.set_text(self.LatestLoRaValues['time'])
			self.lblLoRaLat.set_text("{0:.5f}".format(self.LatestLoRaValues['lat']))
			self.lblLoRaLon.set_text("{0:.5f}".format(self.LatestLoRaValues['lon']))
			self.lblLoRaAlt.set_text(str(self.LatestLoRaValues['alt']) + 'm')
			
			# HAB screen
			buffer = self.textHABLoRa.get_buffer()		
			start = buffer.get_iter_at_offset(0)
			end = buffer.get_iter_at_offset(999)
			buffer.delete(start, end)
			buffer.insert_at_cursor(self.LatestLoRaValues['payload'] + "\n" +
									self.LatestLoRaValues['time'] + "\n" +
									"{0:.5f}".format(self.LatestLoRaValues['lat']) + "\n" +
									"{0:.5f}".format(self.LatestLoRaValues['lon']) + "\n" +
									str(self.LatestLoRaValues['alt']) + 'm')

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
			
			
			
		return True	# Run again

		
hwg = SkyGate()
Gtk.main()
	