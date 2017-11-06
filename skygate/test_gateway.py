from gateway import *
import time

print("Creating gateway object ...")
mygateway = gateway()

mygateway.run()

while 1:
	time.sleep(1)
	CarPosition = mygateway.gps.Position()
	print (CarPosition)
