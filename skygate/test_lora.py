from skygate.lora import *
import time

def woo_got_a_packet(packet):
	print(packet)
	if packet == None:
		print("Failed packet")
	elif (packet[0] & 0x80) == 0:
		# ASCII
		Sentence = ''.join(map(chr,bytes(packet).split(b'\x00')[0]))
		print("Sentence=" + Sentence, end='')
	else:
		print("Packet=", packet)
	
mylora = LoRa(1, 434.450, 1)

mylora.listen_for_packets(woo_got_a_packet)

while 1:
	time.sleep(0.01)

