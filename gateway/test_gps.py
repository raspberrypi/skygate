from cgps import *
import time

print("Creating GPS object ...")
mygps = GPS();

print("Open GPS ...")
mygps.open()
print("GPS open OK")

# mygps.GetPositions()
mygps.run()

while 1:
	time.sleep(1)
	print (mygps.Position())
