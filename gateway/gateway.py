from cgps import *
from lora import *
from rtty import *
from habitat import *
from ssdv import *
from time import sleep

class gateway(object):
	"""
	Combines GPS, LoRa, RTTY with habitat uploads.
	Provides callbacks so that user can provide screen updates
	"""
	
	def __init__(self, CarID='Python', CarPeriod=30, CarEnabled=True, RadioCallsign='python', LoRaChannel=1, LoRaFrequency=434.450, LoRaMode=1, EnableLoRaUpload=True, StoreSSDVLocally=True, RTTYFrequency=434.250):
		self.RadioCallsign = RadioCallsign
		self.EnableLoRaUpload = EnableLoRaUpload
		self.StoreSSDVLocally = StoreSSDVLocally
		self.LatestLoRaSentence = None
		self.LatestLoRaPacketHeader = None
		self.LoRaFrequencyError = 0
		self.LatestRTTYSentence = None
		
		self.ssdv = SSDV()
		self.ssdv.StartConversions()
		
		self.gps = GPS()
		self.gps.open()
		
		self.habitat = habitat(ChaseCarID=CarID, ChaseCarPeriod=CarPeriod, ChaseCarEnabled=CarEnabled)
		self.habitat.open()
		
		self.lora = LoRa(LoRaChannel, LoRaFrequency, LoRaMode)
		self.lora.listen_for_packets(self.__lora_packet)
	
		self.rtty = RTTY(Frequency=RTTYFrequency)
		self.rtty.listen_for_sentences(self.__rtty_sentence)
	
	def __chase_thread(self):
		while 1:
			sleep(1)
			self.habitat.CarPosition = self.gps.Position()
			
	def __lora_packet(self, result):
		packet = result['packet']
		if packet == None:
			print("Failed packet")
		else:
			self.LoRaFrequencyError = result['freq_error']
			if self.habitat.IsSentence(packet[0]):
				self.LatestLoRaSentence = ''.join(map(chr,bytes(packet).split(b'\x00')[0]))
				print("LoRa Sentence=" + self.LatestLoRaSentence, end='')
				if self.EnableLoRaUpload:
					self.habitat.UploadTelemetry(self.RadioCallsign, self.LatestLoRaSentence)
			elif self.habitat.IsSSDV(packet[0]):
				packet = bytearray([0x55] + packet)
				header = self.ssdv.extract_header(packet)
				print("LoRa SSDV Header = ", header)
				if self.EnableLoRaUpload:
					self.habitat.UploadSSDV(self.RadioCallsign, packet)
				if self.StoreSSDVLocally:
					self.ssdv.write_packet(header['callsign'], header['imagenumber'], packet)
				self.LatestLoRaPacketHeader = header
			else:
				print("Unknown packet ", packet[0])

	def __rtty_sentence(self, sentence):
		self.LatestRTTYSentence = sentence
		print("RTTY Sentence=" + sentence, end='')

	def run(self):
		self.gps.run()
		self.habitat.run()

		t = threading.Thread(target=self.__chase_thread)
		t.daemon = True
		t.start()
