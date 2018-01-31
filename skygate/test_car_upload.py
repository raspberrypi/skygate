from skygate.gps import *
from skygate.habitat import *
import time

print("Creating GPS object ...")
mygps = GPS()

print("Creating habitat object")
hab = habitat()

print("Open GPS ...")
mygps.open()
print("GPS open OK")

mygps.run()
hab.EnableCarUpload = True

while 1:
	time.sleep(1)
	CarPosition = mygps.Position()
	print (CarPosition)
	print(hab.SetCarPosition(CarPosition))
