# skygate - Modular Python/GTK HAB Receiver and Uploader

HAB receiver software for tracking LoRa and RTTY payloads, and uploading telemetry and image data to Habitat along with the receiver's GPS position.  Uses external software (dl-fldigi) to decode RTTY, using audio from a real radio or from an RTL-SDR using rtl_fm program.


## Receiver ##


This software is written for Python 3.

It needs these items to be installed:

    sudo apt-get install wmctrl rtl-sdr dl-fldigi ssdv 

 
## Raspbian Configuration ##

Enable the following with raspi-config:

	Interfacing Options --> SPI --> Yes

If you are using a GPS HAT, then you also need to set the serial port:

	Interfacing Options --> Serial --> No (login) --> Yes (hardware)
	
## Loopback Sound Device ##

Create a new ~/.asoundrc file using the supplied file, with

	cp ~/skygate/.asoundrc ~ 

## Usage (Autostart) ##

Edit the following text file:

	~/.config/lxsession/LXDE-pi/autostart

and append these 2 lines:

	@/home/pi/skygate/skygate/start_gateway.sh  
	@/home/pi/skygate/skygate/start_rtty.sh


## Usage (Manual) ##

Set up the loopback audio device, with

	modprobe snd-aloop pcm_substreams=1

Start the RTL SDR software with

	rtl_fm -M usb -f 434.100M -s 192000 -r 8000 - | aplay -f S16_LE -t raw -c 1 -D loopout


Start dl-fldigi with

	./src/dl-fldigi --wfall-only

At startup, enter your receiver callsign.  Then, on the audio config page, select Port Audio and the first device.

Then configure dl-fldigi through its menus (these settings suit pytrack and Pi In The Sky default settings):

	Op Mode --> RTTY Custom --> Set 300 baud, 8 data bits, 2 stop bits, 830Hz shift

(or, if not using SSDV) 50 baud, 7 data bits, 2 stop bits, 830Hz shift


dl-fldigi includes an fldigi bug that causes it to sometimes fail on startup with an error code of 11.  Try again if this happens.


The receiver program can be started manually from a terminal window in an X session with:

	cd
	cd skygate/gateway
	python3 skygate.py


