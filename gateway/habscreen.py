import gi
from misc import *

class HABScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameHAB")
		
		self.LatestLoRaValues = None
		self.LatestRTTYValues = None
		self.PreviousLoRaValues = None
		self.PreviousRTTYValues = None
		self.GPSPosition = None
		
		self.btnAuto = builder.get_object("btnHABAuto")
		self.btnLoRa = builder.get_object("btnHABLoRa")
		self.btnRTTY = builder.get_object("btnHABRTTY")
		
		self.lblHABRate = builder.get_object("lblHABRate")
		
		self.lblHABDistance = builder.get_object("lblHABDistance")
		self.imgHABBall = builder.get_object("imgHABBall")
		self.fixedHABCompass = builder.get_object("fixedHABCompass")
		
		self.lblHABTime = builder.get_object("lblHABTime")
		self.lblHABLatitude = builder.get_object("lblHABLatitude")
		self.lblHABLongitude = builder.get_object("lblHABLongitude")
		self.lblHABAltitude = builder.get_object("lblHABAltitude")
		
	def LatestHABValues(self):
		if self.btnAuto.get_active():
			if self.LatestLoRaValues == None:
				return None
			if self.LatestRTTYValues == None:
				return self.LatestLoRaValues
			if self.LatestLoRaValues['time'] > self.LatestRTTYValues['time']:
				return self.LatestLoRaValues
			return self.LatestRTTValues
		elif self.btnLoRa.get_active():
			return self.LatestLoRaValues
		else:
			return self.LatestRTTYValues
	
			
	def ShowDistanceAndDirection(self, HABPosition, GPSPosition):
		if HABPosition and GPSPosition:
			try:
				DistanceToHAB = CalculateDistance(HABPosition['lat'], HABPosition['lon'], GPSPosition['lat'], GPSPosition['lon'])
				DirectionToHAB = CalculateDirection(HABPosition['lat'], HABPosition['lon'], GPSPosition['lat'], GPSPosition['lon'])
																				
				self.fixedHABCompass.move(self.imgHABBall, 150 + 131 * math.sin(math.radians(DirectionToHAB)), 134 + 131 * math.cos(math.radians(DirectionToHAB)))
				self.lblHABDistance.set_text("%.3f" % (DistanceToHAB/1000) + " km")
			finally:
				pass

	def ShowLatestValues(self):
		HABPosition = self.LatestHABValues()
		if HABPosition:
			self.lblHABRate.set_text("{0:.1f}".format(HABPosition['rate']) + 'm/s')
			self.lblHABTime.set_text(HABPosition['time'].strftime('%H:%M:%S'))
			self.lblHABLatitude.set_text("{0:.5f}".format(HABPosition['lat']))
			self.lblHABLongitude.set_text("{0:.5f}".format(HABPosition['lon']))
			self.lblHABAltitude.set_text(str(HABPosition['alt']) + 'm')
			self.ShowDistanceAndDirection(HABPosition, self.GPSPosition)
		else:
			self.lblHABRate.set_text('')
			self.lblHABTime.set_text('')
			self.lblHABLatitude.set_text('')
			self.lblHABLongitude.set_text('')
			self.lblHABAltitude.set_text('')
			self.fixedHABCompass.move(self.imgHABBall, 150, 134)
			self.lblHABDistance.set_text("")
		pass
		
	def CalculateRate(self, Latest, Previous):
		if Latest and Previous:
			if Latest['time'] > Previous['time']:
				return (Latest['alt'] - Previous['alt']) / (Latest['time'] - Previous['time']).seconds
				
		return 0
	
	def NewLoRaValues(self, LatestLoRaValues):
		self.PreviousLoRaValues = self.LatestLoRaValues
		LatestLoRaValues['rate'] = self.CalculateRate(self.LatestLoRaValues, self.PreviousLoRaValues)
		self.LatestLoRaValues = LatestLoRaValues
		self.ShowLatestValues()
	
	def ShowRTTYValues(self, LatestRTTYValues):
		self.PreviousRTTYValues = self.LatestRTTYValues
		LatestRTTYValues['rate'] = self.CalculateRate(self.LatestRTTYValues, self.PreviousRTTYValues)
		self.LatestRTTYValues = LatestRTTYValues
		self.ShowLatestValues()
		
	def NewGPSPosition(self, GPSPosition):
		self.GPSPosition = GPSPosition
		self.ShowLatestValues()
			
		