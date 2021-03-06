import serial
import time as pyTime
import psycopg2
import os
import gc
import sensors

dataCollectionPeriod = 0 # Time in minutes to collect data samples before finding the averages
dataSampleRate = 0 # Time in seconds between samples within each period
dataPoints = [] # An array of all data samples collected
moistureMax = 0 # Soil moisture calibration value
moistureMin = 0 # Soil moisture calibration value
plant1Height = 0 
plant2Height = 0
plant3Height = 0
plant4Height = 0

# Fetches the local IP address of the Raspberry Pi Zero
os.system('hostname -I > /home/pi/environments/oc-rae/ip.txt')
ipFile = open('/home/pi/environments/oc-rae/ip.txt', 'r')
ip = ipFile.read()

# Defines the USB connected arduino device and the baud communication value
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
pyTime.sleep(2)

# Send the IP address to the arduino to be printed
arduino.write(bytes(ip[:ip.index(' ')], 'utf-8')) 

# The class object that holds the information of each data sample + a time_stamp
class DataPoint:
	def __init__(self, time, tmp, hum, lit, mst):
		self.time = time
		self.tmp = tmp
		self.hum = hum
		self.lit = lit
		self.mst = mst

# Fetches all necessary values from the settings table
def checkSettings(connection):
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM settings;")
	connection.commit()
	settings = cursor.fetchall()
	cursor.close()
	
	for setting in settings:
		if setting[0] == "dataCollectionPeriod":
			global dataCollectionPeriod
			dataCollectionPeriod = float(setting[1])
		if setting[0] == "dataSampleRate":
			global dataSampleRate
			dataSampleRate = float(setting[1])
		if setting[0] == "moistureMax":
			global moistureMax
			moistureMax = float(setting[1])
		if setting[0] == "moistureMin":
			global moistureMin
			moistureMin = float(setting[1])
		if setting[0] == "plant1Height":
			global plant1Height
			plant1Height = float(setting[1])
		if setting[0] == "plant2Height":
			global plant2Height
			plant2Height = float(setting[1])
		if setting[0] == "plant3Height":
			global plant3Height
			plant3Height = float(setting[1])
		if setting[0] == "plant4Height":
			global plant4Height
			plant4Height = float(setting[1])

try: # Attempt to connect to the local PostgreSQL database
	connection = psycopg2.connect(
		user = "pi",
		password = "oldsCollege",
		host = "127.0.0.1",
		port = "5432",
		database = "pi"
	)
	cursor = connection.cursor()

	# Create dataCollection table if none present
	cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = 'data_collection');")
	record = cursor.fetchone()
	if record == (False,):
		cursor.execute("CREATE TABLE data_collection(time_stamp FLOAT, temperature FLOAT, relative_humidity FLOAT, ambient_light FLOAT, soil_moisture FLOAT, plant1Height FLOAT, plant2Height FLOAT, plant3Height FLOAT, plant4Height FLOAT);")

	# Create settings table if none present
	cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = 'settings');")
	record = cursor.fetchone()
	if record == (False,):
		cursor.execute("CREATE TABLE settings(setting VARCHAR(100), value VARCHAR(100));")
		cursor.execute("INSERT INTO settings (setting, value) VALUES ('dataCollectionPeriod', 0), ('dataSampleRate', 0), ('moistureMax', 0), ('moistureMin', 0), ('lightOnMin', 0), ('plant1Height', 0), ('plant2Height', 0), ('plant3Height', 0), ('plant4Height', 0), ('token', 0), ('postgresql_backup', 0), ('user', 0);")
	else:
		checkSettings(connection)

	connection.commit()
	cursor.close()
	# PostgreSQL database setup confirmed

except (Exception, psycopg2.Error) as error :
	# Sometimes this script starts faster than the SQL server can start up on a fresh boot of the device
	# Throw an error and try again
	print ("Error while connecting to PostgreSQL", error)

else:
	# Begin the data collection loop
	while True:
		# Check settings for changes at the beginning of every loop
		checkSettings(connection)

		# Do nothing if the dataCollection period is zero
		# Allows you to stop the collection process if needed
		if dataCollectionPeriod > 0:

			# If you have more than 2 dataPoints and have collected data samples over the span of a full sample period
			if len(dataPoints) > 0 and (dataPoints[-1].time - dataPoints[0].time)/60 >= dataCollectionPeriod:
				# Average all dataPeriod sample values
				time = []
				tmp = []
				hum = []
				lit = []
				mst = []
				for dataPoint in dataPoints:
					time.append(dataPoint.time)
					tmp.append(dataPoint.tmp)
					hum.append(dataPoint.hum)
					lit.append(dataPoint.lit)
					mst.append(dataPoint.mst)
				time = str(int(round(sum(time)/len(time))))

				# Write average data samples for that period to the PostgreSQL database
				cursor = connection.cursor()
				cursor.execute("INSERT INTO data_collection values(" + time + ", " + str(sum(tmp)/len(tmp)) + ", " + str(sum(hum)/len(hum)) + ", " + str(sum(lit)/len(lit)) + ", " + str(sum(mst)/len(mst)) + ", " + str(plant1Height) + ", " + str(plant2Height) + ", " + str(plant3Height) + ", " + str(plant4Height) + ");")
				connection.commit()
				cursor.close()

				# Reset the collected dataPoints array to nothing
				dataPoints = []	

				# Take a photo for that data period		
				os.system('/home/pi/environments/oc-rae/bin/python /home/pi/environments/oc-rae/piCam.py ' + time)
			
			else: 
				# Watch for a data line on the USB connection
				data = arduino.readline() 
				if data:
					# Convert the USB information to usable information
					# Minus the last two "new Line" characters
					data = data[:-2].decode("utf-8") 
					slicePoints = []
					i = 0
					tmp = 0
					hum = 0
					lit = 0
					mst = 0
					
					# Find the position of each data value in the line; which for now is a single string
					for character in data:
						if character == "T" or character == "H" or character == "L" or character == "M":
							slicePoints.append(i)
						i = i+1
					# Chop each data value out of the string
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
								lit = data[point+1:]
							else:
								lit = data[point+1:slicePoints[slicePoints.index(point)+1]]
						if data[point] == "M":
							if point == slicePoints[-1]:
								mst = data[point+1:]
							else:
								mst = data[point+1:slicePoints[slicePoints.index(point)+1]]
					# Assigne the time_stamp value for this data sample
					tStamp = pyTime.time()		

					# If this data sample was captured after the dataSampleRate, or is the first of this dataCollectionPeriod 		
					if len(dataPoints) != 0 and tStamp - dataPoints[-1].time >= dataSampleRate or len(dataPoints) == 0:
						try:
							# Add it to the array of dataPoints for this dataCollectionPeriod
							if moistureMax != 0 and moistureMin != 0:
								mst = sensors.soilMoisture(moistureMin, moistureMax, float(mst))						
							dataPoints.append(DataPoint(tStamp, float(tmp), float(hum), float(lit), float(mst)))
						except:
							pass # Error negation; sometimes the data read from the arduino isn't usable
					else:
						pass # Possible error negation; just in case
		else:
			dataPoints = []

		# This 1sec delay is required otherwise I experienced random crashing of the Pi Zero
		pyTime.sleep(1)
		gc.collect()
	
