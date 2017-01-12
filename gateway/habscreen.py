import gi
from misc import *
#import misc
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk, GObject, Pango, GdkPixbuf
#from gateway import *


class HABScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameHAB")
		self.textHABLoRa = builder.get_object("textHABLoRa")
		self.textHABRTTY = builder.get_object("textHABRTTY")
		self.lblHABDirection = builder.get_object("lblHABDirection")
		self.lblHABDistance = builder.get_object("lblHABDistance")
		self.lblHABLoRaFrequency = builder.get_object("lblHABLoRaFrequency")
		self.lblHABRTTYFrequency = builder.get_object("lblHABRTTYFrequency")		
			
	def ShowLoRaFrequencyAndMode(self, LoRaFrequency, LoRaMode):
		self.lblHABLoRaFrequency.set_text("{0:.3f}".format(LoRaFrequency) + ' MHz, Mode ' + str(LoRaMode))
	
	def ShowRTTYFrequency(self, RTTYFrequency):
		self.lblHABRTTYFrequency.set_text("{0:.4f}".format(RTTYFrequency) + ' MHz')

	def ShowDistanceAndDirection(self, LatestHABValues, GPSPosition):
		if LatestHABValues and GPSPosition:
			try:
				DistanceToHAB = CalculateDistance(LatestHABValues['lat'], LatestHABValues['lon'], GPSPosition['lat'], GPSPosition['lon'])
				DirectionToHAB = CalculateDirection(LatestHABValues['lat'], LatestHABValues['lon'], GPSPosition['lat'], GPSPosition['lon'])
																				
				self.lblHABDirection.set_markup("<span font='48'>" + ["N","NE","E","SE","S","SW","W","NW","N"][int(round(DirectionToHAB/45))] + "</span>")
				self.lblHABDistance.set_markup("<span font='32'>" + "%.3f" % (DistanceToHAB/1000) + " km</span>")
			finally:
				pass

	def ShowHABValues(self, TextBox, LatestHABValues, GPSPosition):
		if LatestHABValues:
			PlaceTextInTextBox(TextBox,
									"\n" +
									LatestHABValues['payload'] + "\n" +
									LatestHABValues['time'] + "\n" +
									"{0:.5f}".format(LatestHABValues['lat']) + "\n" +
									"{0:.5f}".format(LatestHABValues['lon']) + "\n" +
									str(LatestHABValues['alt']) + 'm')
			self.ShowDistanceAndDirection(LatestHABValues, GPSPosition)
	
	def ShowLoRaValues(self, LatestLoRaValues, GPSPosition):
		self.ShowHABValues(self.textHABLoRa, LatestLoRaValues, GPSPosition)
	
	def ShowRTTYValues(self, LatestRTTYValues, GPSPosition):
		self.ShowHABValues(self.textHABRTTY, LatestRTTYValues, GPSPosition)
			
		