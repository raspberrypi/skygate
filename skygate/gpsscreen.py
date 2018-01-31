from skygate.misc import *

class GPSScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameGPS")
		self.Log = []
		
		self.lblGPSDevice = builder.get_object("lblGPSDevice")
		self.lblGPSTime = builder.get_object("lblGPSTime")
		self.lblGPSLatitude = builder.get_object("lblGPSLatitude")
		self.lblGPSLongitude = builder.get_object("lblGPSLongitude")
		self.lblGPSAltitude = builder.get_object("lblGPSAltitude")
		self.lblGPSSatellites = builder.get_object("lblGPSSatellites")
	
	def ShowPortStatus(self, Status):
		self.lblGPSDevice.set_text(Status)
		
	def ShowPosition(self, Position):
		self.lblGPSTime.set_text(Position['time'])
		self.lblGPSLatitude.set_text("{0:.5f}".format(Position['lat']))
		self.lblGPSLongitude.set_text("{0:.5f}".format(Position['lon']))
		self.lblGPSAltitude.set_text(str(int(Position['alt'])))
		self.lblGPSSatellites.set_text(str(Position['sats']))
