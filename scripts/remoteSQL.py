import psycopg2

remoteSQL = ''
token = ''

try: # Attempt to connect to the local PostgreSQL database
	connection = psycopg2.connect(
		user = "pi",
		password = "oldsCollege",
		host = "127.0.0.1",
		port = "5432",
		database = "pi"
	)
	
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM settings WHERE value = 'token' OR value = 'postgresql_backup';")
    record = cursor.fetchall()
    cursor.close()
    print(record)

except:
    pass # Negate errors and restart service