from cgps import *
from lora import *
# from rtty import *
from habitat import *
from time import sleep

class gateway(object):
	"""
	Combines GPS, LoRa, RTTY with habitat uploads.
	Provides callbacks so that user can provide screen updates
	"""
	
	def __init__(self, CarID = 'Python', CarPeriod = 30, RadioCallsign='python', LoRaChannel=1, LoRaFrequency=434.450, LoRaMode=1):
		self.RadioCallsign = RadioCallsign
		self.LatestLoRaSentence = None
		
		self.gps = GPS()
		self.gps.open()
		
		self.habitat = habitat(ChaseCarID = 'Python', ChaseCarPeriod = CarPeriod, ChaseCarEnabled = CarPeriod > 0)
		self.habitat.open()
		
		self.lora = LoRa(LoRaChannel, LoRaFrequency, LoRaMode)
		self.lora.listen_for_packets(self.__lora_packet)		
	
	def __chase_thread(self):
		while 1:
			sleep(1)
			self.habitat.CarPosition = self.gps.Position()
			
	def __lora_packet(self, packet):
		if packet == None:
			print("Failed packet")
		elif self.habitat.IsSentence(packet[0]):
			self.LatestLoRaSentence = ''.join(map(chr,bytes(packet).split(b'\x00')[0]))
			print("Sentence=" + self.LatestLoRaSentence, end='')
			self.habitat.UploadTelemetry(self.RadioCallsign, self.LatestLoRaSentence)
		elif self.habitat.IsSSDV(packet[0]):
			print("SSDV Packet")
			self.habitat.UploadSSDV(self.RadioCallsign, packet)
		else:
			print("Unknown packet ", packet[0])

	def run(self):
		self.gps.run()
		self.habitat.run()

		t = threading.Thread(target=self.__chase_thread)
		t.daemon = True
		t.start()
