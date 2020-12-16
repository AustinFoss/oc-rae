import serial
import time as pyTime
import psycopg2
import piCam
import os

dataCollectionPeriod = 15 # Time in minutes to collect data samples before finding the averages
dataSampleRate = 1 # Time in seconds between samples within each period
dataPoints = [] # An array of all data samples collected

# Defines the function to capture a camera image from the piCam script
snapPhoto = piCam.snapPhoto

# Fetches the local IP address of the Raspberry Pi Zero
os.system('hostname -I > /home/pi/environments/oc-rae/ip.txt')
f = open('/home/pi/environments/oc-rae/ip.txt', 'r')
ip = f.read()

# Defines the USB connected arduino device
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# The class object that holds the information of each data sample + a time stamp
class DataPoint:
	def __init__(self, time, tmp, hum, lux, mst):
		self.time = time
		self.tmp = tmp
		self.hum = hum
		self.lux = lux
		self.mst = mst

try: # Attempt to connect to the local PostgreSQL database
	connection = psycopg2.connect(user = "pi",
								password = "oldsCollege",
								host = "127.0.0.1",
								port = "5432",
								database = "pi")
	cursor = connection.cursor()

	# Create dataCollection table if none present
	cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = 'data_collection');")
	record = cursor.fetchone()
	if record == (False,):
		cursor.execute("CREATE TABLE data_collection(posted BOOLEAN NOT NULL, time_stamp FLOAT, temperature FLOAT, relative_humidity FLOAT, ambient_light FLOAT, soil_moisture FLOAT);")

	# Create settings table if none present
	cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = 'settings');")
	record = cursor.fetchone()
	if record == (False,):
		cursor.execute("CREATE TABLE settings(setting VARCHAR(100), value VARCHAR(100));")
		cursor.execute("INSERT INTO settings (settings, value) VALUES ('dataCollectionPeriod', 0), ('dataSampleRate', 0);")
	connection.commit()
	cursor.close()
	# PostgreSQL database setup confirmed

except (Exception, psycopg2.Error) as error :
	print ("Error while connecting to PostgreSQL", error)

else:
	# Begin data collection logic
	while True: # Primary Loop

		# Send the IP address to the arduino to be printed
		arduino.write(bytes(ip[:ip.index(' ')], 'utf-8')) 

		# If you have more than 2 dataPoints and have collected data samples over the span of a full sample period
		if len(dataPoints) >= 2 and (dataPoints[-1].time - dataPoints[0].time)/60 >= dataCollectionPeriod :
			# Average all dataPeriod sample values
			time = []
			tmp = []
			hum = []
			lux = []
			mst = []
			for dataPoint in dataPoints:
				time.append(dataPoint.time)
				tmp.append(dataPoint.tmp)
				hum.append(dataPoint.hum)
				lux.append(dataPoint.lux)
				mst.append(dataPoint.mst)
			time = str(int(round(sum(time)/len(time))))

			# Write average data samples for that period to the PostgreSQL database
			cursor = connection.cursor()
			cursor.execute("INSERT INTO data_collection values('0', " + time + ", " + str(sum(tmp)/len(tmp)) + ", " + str(sum(hum)/len(hum)) + ", " + str(sum(lux)/len(lux)) + ", " + str(sum(mst)/len(mst)) + ");")
			connection.commit()
			cursor.close()

			# Reset data points
			dataPoints = []
			print("Sampled Data")	
			# Take a photo for that data period			
			snapPhoto(time)
			print("Photo taken")
		
		else: 
			# Watch for a data line on the USB connection
			data = arduino.readline() 
			if data:
				# Convert the USB information to usable information
				data = data[:-2].decode("utf-8") 
				slicePoints = []
				i = 0
				tmp = 0
				hum = 0
				lux = 0
				mst = 0

				#
				for character in data:
					if character == "T" or character == "H" or character == "L" or character == "M":
						slicePoints.append(i)
					i = i+1
				for point in slicePoints:
					if data[point] == "T":
						if point == slicePoints[-1]:
							tmp = data[point+1:]
						else:
							tmp = data[point+1:slicePoints[slicePoints.index(point)+1]]
					if data[point] == "H":
						if point == slicePoints[-1]:
							hum = data[point+1:]
						else:
							hum = data[point+1:slicePoints[slicePoints.index(point)+1]]
					if data[point] == "L":
						if point == slicePoints[-1]:
							lux = data[point+1:]
						else:
							lux = data[point+1:slicePoints[slicePoints.index(point)+1]]
					if data[point] == "M":
						if point == slicePoints[-1]:
							mst = data[point+1:]
						else:
							mst = data[point+1:slicePoints[slicePoints.index(point)+1]]
				tStamp = pyTime.time()				
				if len(dataPoints) != 0 and tStamp - dataPoints[-1].time >= dataSampleRate or len(dataPoints) == 0:
					dataPoints.append(DataPoint(tStamp, float(tmp), float(hum), float(lux), float(mst)))
				else:
					pass # Possible error negation
		
# def dataCollection(connection)
# 	cursor = connection.cursor()
# 	cursor.execute("SELECT value FROM settings WHERE setting = 'dataCollectionPeriod' AND setting = 'dataSampleRate';")
# 	record = cursor.fetchmany(2)
	
