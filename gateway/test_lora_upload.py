from lora import *
from habitat import *
import time

def woo_got_a_packet(packet):
	if packet == None:
		print("Failed packet")
	elif hab.IsSentence(packet[0]):
		# ASCII
		Sentence = ''.join(map(chr,bytes(packet).split(b'\x00')[0]))
		print("Sentence=" + Sentence, end='')
		hab.UploadTelemetry('python', Sentence)
	elif hab.IsSSDV(packet[0]):
		print("SSDV Packet")
		hab.UploadSSDV('python', packet)
	else:
		print("Unknown packet ", packet[0])

print("Creating lora object")
mylora = LoRa(1, 434.444, 1)

mylora.listen_for_packets(woo_got_a_packet)

print("Creating habitat object")
hab = habitat()

while 1:
	time.sleep(0.01)

