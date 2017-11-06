#!/bin/bash

cd /home/pi

sleep 1

modprobe snd-aloop pcm_substreams=1

sleep 1

rtl_fm -M usb -f 434.100M -s 192000 -r 8000 - | aplay -f S16_LE -t raw -c 1 -D loopout

sleep 1

while :
do
	echo "Restarting dl-fldigi"
	
	dl-fldigi --wfall-only
done

