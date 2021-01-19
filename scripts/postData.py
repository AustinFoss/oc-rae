import psycopg2
import time
import requests
import json
import gc

postingServer = 0
lastPosted = 0

def checkSettings(connection):
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM settings WHERE setting = 'lastPosted';")
    record = cursor.fetchall()
    if len(record) == 0:
        cursor.execute("INSERT INTO settings (setting, value) VALUES ('lastPosted', 0);")
        connection.commit()
    else:
        global lastPosted
        lastPosted = record[0][1]

    cursor.execute("SELECT * FROM settings WHERE setting = 'postingServer';")
    record = cursor.fetchall()
    if len(record) == 0:
        cursor.execute("INSERT INTO settings (setting, value) VALUES ('postingServer', 0);")
        connection.commit()   
    else:
        global postingServer
        postingServer = record[0][1]

    cursor.close()
        
try:
    connection = psycopg2.connect(
        user = "pi",
        password = "oldsCollege",
        host = "127.0.0.1",
        port = "5432",
        database = "pi"
    )

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
else:

    while True:
        checkSettings(connection)

        if postingServer == 0:
            print("Nowhere to post")
            pass

        else:
            cursor = connection.cursor()
            cursor.execute("SELECT MIN(time_stamp) FROM data_collection WHERE time_Stamp > " + lastPosted + ";")
            record = cursor.fetchone()
            
            # If there is no new data point wait for a few seconds then check again
            if record[0] != None:

                cursor.execute("SELECT * FROM data_collection WHERE time_stamp = " + str(record[0]) + ";")
                record = cursor.fetchone()
                cursor.close()

                data = {
                    "time_stamp": record[1],
                    "temperature_c": record[2],
                    "relative_humidity": record[3],
                    "ambient_light": record[4],
                    "soil_moisture": record[5]
                }

                # Post data to server
                response = requests.post(postingServer, data={'Token': 'Token1', 'data': data})
                
                if response.status_code != 200:
                    print("Error Posting: Handle Error")
                else:
                    print(data['time_stamp'])
                    
                    cursor = connection.cursor()
                    cursor.execute("UPDATE settings SET value = " + str(data['time_stamp']) + " WHERE setting = 'lastPosted';")
                    connection.commit()
                    cursor.close()   
                    
        time.sleep(1)
        gc.collect()