# skygate - Modular Python HAB receiver and uploader, with PyGTK user interface

HAB receiver software for tracking LoRa and RTTY payloads, and uploading telemetry and image data to Habitat along with the receiver's GPS posotion


GPS
===

The GPS program is written in C, and uses WiringPi which should be installed with:

sudo apt-get install wiringpi

This part of the software needs to be compiled and linked, with:

cd gps
make


Receiver
========

This part of the software is Python 3.4.  It uses these Python libraries which can be installed with PIP:

(need to check my notes to see if any need to be installed or if they were already installed)


It also requires SSDV to be installed:

cd
git clone https://github.com/fsphil/ssdv.git
cd ssdv
sudo make install

 

Raspbian Configuration
======================

Enable the following with raspi-config:

Advanced Options --> Enable SPI

Note that the SPI settings have been moved to "Interfacing Options" in the latest Raspbian update.


Allow the serial port to be used with:

sudo systemctl mask serial-getty@ttyAMA0.service

That disables the serial port login.  We also need to stop the kernel from using the serial port, by editing the cmdline.txt file:

sudo nano /boot/cmdline.txt

and remove the part that says console=serial0,115200

Save your changes.


Usage
=====

The GPS program needs to be run (before or after the main tracker - makes no difference):

cd
cd skygate/gps
sudo ./gps

The receiver program can be started manually from a terminal window in an X session with:

cd
cd skygate/gateway
python3 skygate.py


Test programs
=============

There are various test_*.py programs in the tracker folder, to individually test GPS, car tracking etc.


