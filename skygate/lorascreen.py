from skygate.misc import *

class LoRaScreen(object):
	
	def __init__(self, builder):
		self.frame = builder.get_object("frameLoRa")
		self.textLoRa = builder.get_object("textLoRa")
		self.scrollLoRa = builder.get_object("scrollLoRa")
		self.lblLoRaFrequency = builder.get_object("lblLoRaFrequency")
		self.lblLoRaFrequencyError = builder.get_object("lblLoRaFrequencyError")		
		
		# Place description in log window
		self.Log = UpdateLog(self.textLoRa, ['', '',
											 '		This window will show messages received from the LoRa device',
											 '',
											 '		If no such messages appear, then check the following:',
											 '',
											 '			-	that your tracker is configured and running',
											 '			-	that the LoRa frequency (see Settings screen) matches the tracker',
											 '			-	that the LoRa mode (see Settings screen) matches the tracker',
											 '			-	that the tracker and receiver are very close or have aerials attached',
											 '',
											 '		If all of the above are OK, try tuning the receiver up/down using the buttons below.',
											 '		These step the frequency up/down in 1kHz steps.',
											 '',
											 '		You may need to tune as far as 5kHz away from the transmitter frequency before it works.',
											 '',
											 '		Once you are receiving data, adjust to reduce the displayed error to 1kHz or less',
											 ''], '', 15)
	
	def AppendLine(self, Line):
		self.Log = UpdateLog(self.textLoRa, self.Log, Line, 15)
		
	def ShowLoRaFrequencyAndMode(self, LoRaFrequency, LoRaMode):
		self.lblLoRaFrequency.set_text("{0:.3f}".format(LoRaFrequency) + ' MHz, Mode ' + str(LoRaMode))

	def ShowFrequencyError(self, LoRaFrequencyError):
		self.lblLoRaFrequencyError.set_text("Err: {0:.1f}".format(LoRaFrequencyError) + ' kHz')
		