import gi
from skygate.misc import *
from datetime import datetime

class HABScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameHAB")
		
		self.LatestLoRaValues = None
		self.LatestRTTYValues = None
		self.PreviousLoRaValues = None
		self.PreviousRTTYValues = None
		self.GPSPosition = None
		self.ShowBalloon = True
		
		self.MaximumAltitude = 0
		self.LastPositionAt = None
		
		self.btnAuto = builder.get_object("btnHABAuto")
		self.btnLoRa = builder.get_object("btnHABLoRa")
		self.btnRTTY = builder.get_object("btnHABRTTY")
		
		self.lblHABPayload = builder.get_object("lblHABPayload")
		self.lblHABRate = builder.get_object("lblHABRate")
		self.imgHABBalloon = builder.get_object("imgHABBalloon")
		self.imgHABChute = builder.get_object("imgHABChute")
		
		self.lblHABDistance = builder.get_object("lblHABDistance")
		self.imgHABBall = builder.get_object("imgHABBall")
		self.fixedHABCompass = builder.get_object("fixedHABCompass")
		
		self.lblHABTime = builder.get_object("lblHABTime")
		self.lblHABLatitude = builder.get_object("lblHABLatitude")
		self.lblHABLongitude = builder.get_object("lblHABLongitude")
		self.lblHABAltitude = builder.get_object("lblHABAltitude")
		self.lblHABMaxAltitude = builder.get_object("lblHABMaxAltitude")
		
		self.lblHABTimeSince = builder.get_object("lblHABTimeSince")
	
	def ShowTimeSinceData(self):
		if self.LastPositionAt:
			self.lblHABTimeSince.set_text(str(round((datetime.utcnow() - self.LastPositionAt).total_seconds())) + ' s')

		
	def RadioButtonsChanged(self):
		self.ShowLatestValues()
		
	def LatestHABValues(self):
		if self.btnAuto.get_active():
			if self.LatestLoRaValues == None:
				return None
			if self.LatestRTTYValues == None:
				return self.LatestLoRaValues
			if self.LatestLoRaValues['time'] > self.LatestRTTYValues['time']:
				return self.LatestLoRaValues
			return self.LatestRTTYValues
		elif self.btnLoRa.get_active():
			return self.LatestLoRaValues
		else:
			return self.LatestRTTYValues
	
			
	def ShowDistanceAndDirection(self, HABPosition, GPSPosition):
		if HABPosition and GPSPosition:
			# try:
				DistanceToHAB = CalculateDistance(HABPosition['lat'], HABPosition['lon'], GPSPosition['lat'], GPSPosition['lon'])
				DirectionToHAB = CalculateDirection(HABPosition['lat'], HABPosition['lon'], GPSPosition['lat'], GPSPosition['lon'])
																				
				self.fixedHABCompass.move(self.imgHABBall, 150 + 131 * math.sin(math.radians(DirectionToHAB)), 134 + 131 * math.cos(math.radians(DirectionToHAB)))
				self.lblHABDistance.set_text("%.3f" % (DistanceToHAB/1000) + " km")
			#finally:
			#	pass

	def ShowLatestValues(self):
		HABPosition = self.LatestHABValues()
		if HABPosition:
			self.lblHABPayload.set_text(HABPosition['payload'])
			self.lblHABRate.set_text("{0:.1f}".format(HABPosition['rate']) + 'm/s')
			self.lblHABTime.set_text(HABPosition['time'].strftime('%H:%M:%S'))
			self.lblHABLatitude.set_text("{0:.5f}".format(HABPosition['lat']))
			self.lblHABLongitude.set_text("{0:.5f}".format(HABPosition['lon']))
			self.lblHABAltitude.set_text(str(round(HABPosition['alt'])) + 'm')
			self.MaximumAltitude = max(self.MaximumAltitude, round(HABPosition['alt']))
			self.lblHABMaxAltitude.set_text(str(self.MaximumAltitude) + 'm')
			self.ShowDistanceAndDirection(HABPosition, self.GPSPosition)
			if (HABPosition['rate'] >= -1) != self.ShowBalloon:
				self.ShowBalloon = not self.ShowBalloon
				# self.imgHABBalloon.set_visible(self.ShowBalloon)
				# self.imgHABChute.set_visible(not self.ShowBalloon)
		else:
			self.lblHABPayload.set_text('')
			self.lblHABRate.set_text('')
			self.lblHABTime.set_text('')
			self.lblHABLatitude.set_text('')
			self.lblHABLongitude.set_text('')
			self.lblHABAltitude.set_text('')
			self.fixedHABCompass.move(self.imgHABBall, 150, 134)
			self.lblHABDistance.set_text("")
		
	def CalculateRate(self, Latest, Previous):
		if Latest and Previous:
			if Latest['time'] > Previous['time']:
				return (Latest['alt'] - Previous['alt']) / (Latest['time'] - Previous['time']).seconds			
		return 0
	
	def NewLoRaValues(self, LatestLoRaValues):
		self.PreviousLoRaValues = self.LatestLoRaValues
		LatestLoRaValues['rate'] = self.CalculateRate(self.LatestLoRaValues, self.PreviousLoRaValues)
		self.LatestLoRaValues = LatestLoRaValues
		self.LastPositionAt	= datetime.utcnow()
		self.lblHABTimeSince.set_text('0 s')
		self.ShowLatestValues()
	
	def NewRTTYValues(self, LatestRTTYValues):
		self.PreviousRTTYValues = self.LatestRTTYValues
		LatestRTTYValues['rate'] = self.CalculateRate(self.LatestRTTYValues, self.PreviousRTTYValues)
		self.LatestRTTYValues = LatestRTTYValues
		self.LastPositionAt	= datetime.utcnow()
		self.lblHABTimeSince.set_text('0 s')
		self.ShowLatestValues()
		
	def NewGPSPosition(self, GPSPosition):
		self.GPSPosition = GPSPosition
		self.ShowLatestValues()
			
		