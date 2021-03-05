import psycopg2
import time
import requests
import json
import gc
import base64

postingServer = 0
lastPosted = 0
token = ''

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

    cursor.execute("SELECT * FROM settings WHERE setting = 'token';")
    record = cursor.fetchall()
    if len(record) == 0:
        cursor.execute("INSERT INTO settings (setting, value) VALUES ('token', 0);")
        connection.commit()
    else:
        global token
        token = record[0][1]

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
                time.sleep(10)
                cursor.execute("SELECT * FROM data_collection WHERE time_stamp = " + str(record[0]) + ";")
                record = cursor.fetchone()
                cursor.close()

                data = {
                    "time_stamp": round(record[0]),
                    "temperature_c": record[1],
                    "relative_humidity": record[2],
                    "ambient_light": record[3],
                    "soil_moisture": record[4]                    
                }
                try:
                    with open("/home/pi/oc-rae/Pictures/" + str(round(record[0])) + ".png", 'rb') as img:
                        files = [
                            ('Token', (None, token)),
                            ('data', (str(round(record[1])) + ".png", img, 'image/png')),
                            ('sensor', (None, json.dumps(data), 'application/json'))    
                        ]                
                        response = requests.post(postingServer, files=files)
                    
                    if response.status_code != 200:
                        print("Error Posting: Handle Error")
                    else:
                        print(round(record[0]))
                        
                        cursor = connection.cursor()
                        cursor.execute("UPDATE settings SET value = " + str(record[0]) + " WHERE setting = 'lastPosted';")
                        connection.commit()
                        cursor.close()   

                except Exception: 

                    with open("/home/pi/oc-rae/Pictures/" + str(round(record[0])) + ".jpg", 'rb') as img:
                        files = [
                            ('Token', (None, token)),
                            ('data', (str(round(record[1])) + ".jpg", img, 'image/jpg')),
                            ('sensor', (None, json.dumps(data), 'application/json'))    
                        ]                
                        response = requests.post(postingServer, files=files)
                    
                    if response.status_code != 200:
                        print("Error Posting: Handle Error")
                    else:
                        print(round(record[0]))
                        
                        cursor = connection.cursor()
                        cursor.execute("UPDATE settings SET value = " + str(record[0]) + " WHERE setting = 'lastPosted';")
                        connection.commit()
                        cursor.close()   
                    
        time.sleep(1)
        gc.collect()
