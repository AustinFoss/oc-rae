import os
import serial

ip = os.system('hostname -I > ip.txt')
f = open('ip.txt', 'r')
ip = f.read()
print(ip[:ip.index(' ')])


arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)


print(arduino.write(bytes(ip[:ip.index(' ')], 'utf-8')))