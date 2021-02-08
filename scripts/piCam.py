from time import sleep
from picamera import PiCamera
import sys
import gc

# 
def snapPhoto(name):
    try: 
        camera = PiCamera()
        # Resolution for .jpg images
        # camera.resolution = (3280, 2464)
        #Resolution for .png images; the .jpg resolution is too big for the memory capacity of the pi zero
        camera.resolution = (2160,1440)

        camera.start_preview()
        sleep(2) # Camera warm-up time and sensor exposure

        # Save the image to the Pictures folder on the raspberry pi zero
        camera.capture('/home/pi/oc-rae/Pictures/' + name + '.png')
    finally:
        # Stop the camera
        camera.close()

snapPhoto(str(sys.argv[1]))
gc.collect()
