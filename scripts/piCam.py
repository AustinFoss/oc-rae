#!/usr/bin/python3

from time import sleep
from picamera import PiCamera
import sys
import gc



def snapPhoto(name):
    try: 
        camera = PiCamera()
        camera.resolution = (3280, 2464)
        camera.start_preview()
        sleep(2) # Camera warm-up time
        camera.capture('/home/pi/oc-rae/Pictures/' + name + '.jpg')
    finally:
        camera.close()

snapPhoto(str(sys.argv[1]))
gc.collect()
