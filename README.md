# Intro

All code in this repository is inteded to be installed on a fresh install of Raspi OS Lite on a Pi Zero

https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2020-12-04/2020-12-02-raspios-buster-armhf-lite.zip
or
https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2020-12-04/2020-12-02-raspios-buster-armhf-lite.zip.torrent

Once you have this image flashed to an SD card, before you insert it into the Pi Zero, please copy both the `/ssh` and `/wpa_supplicant.conf` to the boot partition of the SD cad.

Open the `/boot/wpa_supplicant.conf` file you just copied to the card, editing lines 5 & 8

ssid="your_network_name"

psk="your_network_password"

# Install OC-RAE over SSH

SSH into the Raspberry Pi Zero with the default `pi` user and `raspberry` password. Change your password by entering `passwd` and raplace it with your own.

Enter the following:

`sudo apt update`
`sudo apt upgrade`
`sudo apt install git`
`git clone https://github.com/AustinFoss/oc-rae.git`
`sudo oc-rae/install.sh`

Wait for the reboot and for the Raspberry Pi Zero IP address to appear on the LCD display. 

# Users

By default you have 2 users:

1. The system `pi` user with your defined password
2. PostgresQL `pi` user with a default password of `oldsCollege`

If you change you the PotgreSQL user password it must also be changed in the Python scripts.