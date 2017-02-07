# skygate - Modular Python/GTK HAB Receiver and Uploader

HAB receiver software for tracking LoRa and RTTY payloads, and uploading telemetry and image data to Habitat along with the receiver's GPS position.  Uses external software (dl-fldigi) to decode RTTY, using audio from a real radio or from an RTL-SDR using rtl_fm program.


## Receiver ##


This software is written for Python 3.4.

It needs these install items:


    sudo apt-get install wmctrl

And this Python library:


    sudo pip3 install psutil

It also requires SSDV to be installed:

	cd  
	git clone https://github.com/fsphil/ssdv.git  
	cd ssdv  
	sudo make install  
 
## Decoding RTTY ##

RTTY is decoded external using dl-fldigi, with the audio feed by pulseaudio.  To install:

	sudo apt-get install git-core libcurl4-openssl-dev autoconf libfltk1.3-dev

	sudo apt-get install libjpeg9-dev libsamplerate0-dev libssl-dev gettext pavucontrol libpulse-dev portaudio19-dev

	cd
	git clone git://github.com/ukhas/dl-fldigi.git  
	cd dl-fldigi  
	git checkout DL3.1  
	git submodule init  
	git submodule update  

Then edit the following file with nano/vi/whatever, e.g.:

	nano src/Makefile.am**

**You have to comment-out TESTS line (add "#" at the start)**

save and then proceed with:

	autoreconf -vfi
	./configure --disable-flarq
	make
	sudo make install


## RTL SDR ##

Assuming use of an RTL_FM radio receiver, the RTL SDR software needs to be installed.  Specifically, my modified version is need in order to allow for retuning.

	sudo apt-get install git cmake libusb-1.0-0-dev
	cd ~  
	git clone https://github.com/daveake/rtl-sdr.git  
	cd rtl-sdr  
	mkdir build  
	cd build  
	cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON  
	make  
	sudo make install  
	sudo ldconfig  


## Raspbian Configuration ##

Enable the following with raspi-config:

	Advanced Options --> Enable SPI

Note that the SPI settings have been moved to "Interfacing Options" in the latest Raspbian update.


If you are using a GPS HAT, then allow the serial port to be used with:

	sudo systemctl mask serial-getty@ttyAMA0.service

That disables the serial port login.  We also need to stop the kernel from using the serial port, by editing the cmdline.txt file, e.g.:

	sudo nano /boot/cmdline.txt

**and remove the part that says console=serial0,115200**

Save your changes.


## Usage (Autostart) ##

Edit the following text file:

~/.config/lxsession/LXDE-pi/autostart

and append these 2 lines:

@/home/pi/skygate/gateway/start_gateway.sh  
@/home/pi/skygate/gateway/start_rtty.sh


## Usage (Manual) ##

Start pulseaudio with

	pulseaudio -D

Start the RTL SDR software with

	rtl_fm -M usb -f 434.253M -s 192000 -r 48000 - | aplay -r 48k -f S16_LE -t raw -c 1

You should now hear sound (noise unless you tuned to a payload) through the Pi speaker.

Start dl-fldigi with

	cd
	cd dl-fldigi
	./src/dl-fldigi --wfall-only

At startup, enter your receiver callsign.  Then, on the audio config page, select Pulse Audio

Then configure dl-fldigi through its menus:

	Op Mode --> RTTY Custom --> Set 300 baud, 8 data bits, 2 stop bits, 830Hz shift

(or, if not using SSDV) 50 baud, 7 data bits, 2 stop bits, 830Hz shift


dl-fldigi includes an fldigi bug that causes it to sometimes fail on startup with an error code of 11.  Try again if this happens.


The receiver program can be started manually from a terminal window in an X session with:

	cd
	cd skygate/gateway
	python3 skygate.py


## Test programs ##

There are various test_*.py programs in the tracker folder, to individually test GPS, car tracking etc.


