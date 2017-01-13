from misc import *

class LoRaScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameLoRa")
		self.textLoRa = builder.get_object("textLoRa")
		self.scrollLoRa = builder.get_object("scrollLoRa")
		self.lblLoRaFrequency = builder.get_object("lblLoRaFrequency")
		self.lblLoRaFrequencyError = builder.get_object("lblLoRaFrequencyError")		
	
	def AppendLine(self, Line):
		AppendTextToTextBox(self.scrollLoRa, self.textLoRa, Line)
		
	def ShowLoRaFrequencyAndMode(self, LoRaFrequency, LoRaMode):
		self.lblLoRaFrequency.set_text("{0:.3f}".format(LoRaFrequency) + ' MHz, Mode ' + str(LoRaMode))

	def ShowFrequencyError(self, LoRaFrequencyError):
		self.lblLoRaFrequencyError.set_text("Err: {0:.1f}".format(LoRaFrequencyError) + ' kHz')
		