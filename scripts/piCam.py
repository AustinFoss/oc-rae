from time import sleep
from picamera import PiCamera

camera = PiCamera()

def snapPhoto(name):

    camera.resolution = (1920, 1080)
    camera.start_preview()
    sleep(2) # Camera warm-up time
    camera.capture('/home/pi/Pictures/' + name + '.jpg')

# snapPhoto()