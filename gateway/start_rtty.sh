#!/bin/bash

cd /home/pi

sleep 5

/usr/bin/pulseaudio -D

sleep 1

rtl_fm -M usb -f 434.253M -s 192000 -r 48000 - | aplay -r 48k -f S16_LE -t raw -c 1 &

sleep 2

while :
do
	echo "Restarting dl-fldigi"
	
	./src/dl-fldigi --wfall-only
	cd /home/pi/dl-fldigi
done

