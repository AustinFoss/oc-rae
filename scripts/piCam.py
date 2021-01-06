from time import sleep
from picamera import PiCamera

camera = PiCamera()

def snapPhoto(name):

    camera.resolution = (3280, 2464)
    camera.start_preview()
    sleep(2) # Camera warm-up time
    camera.capture('/home/pi/oc-rae/Pictures/' + name + '.jpg')

# snapPhoto()
