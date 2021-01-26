from time import sleep
from picamera import PiCamera
import sys
import gc

def snapPhoto(name):
    try: 
        camera = PiCamera()
        # camera.resolution = (3280, 2464)
        camera.resolution = (2160,1440)
        camera.start_preview()
        sleep(2) # Camera warm-up time
        camera.capture('/home/pi/oc-rae/Pictures/' + name + '.png')
    finally:
        camera.close()

snapPhoto(str(sys.argv[1]))
gc.collect()
