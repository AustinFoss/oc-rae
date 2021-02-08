import psycopg2
import time as pyTime
import gc

postgresql_backup = ''
token = ''
user = ''

# Fetch and set values from the settings table
def getSettings():

	global postgresql_backup
	global token
	global user

	cursor = localConnection.cursor()
	cursor.execute("SELECT * FROM settings WHERE setting = 'token' OR setting = 'postgresql_backup' OR setting = 'user';")
	record = cursor.fetchall()
	cursor.close()

	for setting in record:
		if setting[0] == 'token':
			token = setting[1]
		if setting[0] == 'postgresql_backup':
			postgresql_backup = setting[1]
		if setting[0] == 'user':
			user = setting[1]

try: # Attempt to connect to the local PostgreSQL database
	localConnection = psycopg2.connect(
		user = "pi",
		password = "oldsCollege",
		host = "127.0.0.1",
		port = "5432",
		database = "pi"
	)
	localCursor = localConnection.cursor()

except:
    print('Cannot to local SQL DB')

else:
	# Get the settings needed to connect to the remote sql server
	getSettings()

	try:
		#Connect to the remote sql server
		remoteConnection = psycopg2.connect(
			user = user,
			password = token,
			host = postgresql_backup,
			port = "5432",
			database = user,
			sslmode = 'require'
		)
		remoteCursor = remoteConnection.cursor()
	
	except:
		print('Cannot reach remote SQL')
	
	else:
		# Check for a data_collection table
		remoteCursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = 'data_collection');")
		record = remoteCursor.fetchone()
		# Create data_collection table if none present on the remote db
		if record == (False,):
			remoteCursor.execute("CREATE TABLE data_collection(time_stamp FLOAT, temperature FLOAT, relative_humidity FLOAT, ambient_light FLOAT, soil_moisture FLOAT, plant1Height FLOAT, plant2Height FLOAT, plant3Height FLOAT, plant4Height FLOAT);")
			remoteConnection.commit()
			remoteCursor.close()

		# Begin saving data to the remote server
		while True:

			#First check for the greatest time stamp on the remote sql connection
			remoteCursor = remoteConnection.cursor()
			remoteCursor.execute("SELECT MAX(time_stamp) FROM data_collection;")
			record = remoteCursor.fetchone()

			# Set the last saved time stamp on the remote sql server
			lastSaved = record[0]
			if lastSaved == None:
				lastSaved = 0
			lastSaved = str(lastSaved)

			# Fetch the oldest row of data in the local sql server that hasn't been saved to 
			localCursor.execute("SELECT MIN(time_stamp) FROM data_collection WHERE time_stamp > " + lastSaved + ";") 
			record = localCursor.fetchone()

			# If there is a new row of data
			if record[0] != None:
				localCursor.execute("SELECT * FROM data_collection WHERE time_stamp = " + str(record[0]) + ";")
				record = localCursor.fetchone()
				
				# Save the fetched row of data to the remote db
				remoteCursor.execute("INSERT INTO data_collection values(" + str(record[0]) + ", " + str(record[1]) + ", " + str(record[2]) + ", " + str(record[3]) + ", " + str(record[4]) + ", " + str(record[5]) + ", " + str(record[6]) + ", " + str(record[7]) + ", " + str(record[8]) + ");")
				remoteConnection.commit()
				remoteCursor.close()

			# Pause for 1 second and 
			pyTime.sleep(1)
			gc.collect()
		