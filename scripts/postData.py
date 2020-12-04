import psycopg2
import time
import requests
import json

remoteServer = 'http://192.168.7.105:5000/'

def postData():
        
    try:
        postingConnection = psycopg2.connect(user = "postgres",
                                        password = "postgres",
                                        host = "127.0.0.1",
                                        port = "5432",
                                        database = "postgres")
        postingCursor = postingConnection.cursor()
        # Create dataCollection table if none present
        postingCursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE  table_schema = 'public' AND table_name = 'posted_data');")
        record = postingCursor.fetchone()
        if record == (False,):
            postingCursor.execute("CREATE TABLE posted_data(time_stamp FLOAT, temperature FLOAT, relative_humidity FLOAT, ambient_light FLOAT, soil_moisture FLOAT);")

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    else:
    
        while True:
            # Check for row where posted = false
            postingCursor = postingConnection.cursor()
            postingCursor.execute("SELECT time_stamp, temperature, relative_humidity, ambient_light, soil_moisture FROM public.data_collection WHERE posted = false LIMIT 1;")
            record = postingCursor.fetchone()
            postingCursor.close()

            if record == None:
                print("Nothing to post")
                pass

            else:
                data = {
                    "time_stamp": record[0],
                    "temperature_c": record[1],
                    "relative_humidity": record[2],
                    "ambient_light": record[3],
                    "soil_moisture": record[4]
                }
                # files = {'file': open('/home/pi/rem/photos/' + str(int(record[0])) + '.jpg', 'rb')}
                files = [
                    # ('data', json.dumps(data)),
                    ('photo', (str(int(record[0])) + '.jpg', open('/home/pi/rem/photos/' + str(int(record[0])) + '.jpg', 'rb'), 'image/jpg'))
                ]
                # Post data to server
                response = requests.post(remoteServer, files=files)
                print(response)
                
                # postingCursor = postingConnection.cursor()
                # postingCursor.execute("UPDATE public.data_collection SET posted = True WHERE time_stamp = " + str(record[0]) + ";")
                # postingConnection.commit()
                # postingCursor.close()

                # postingCursor = postingConnection.cursor()
                # postingCursor.execute("INSERT INTO posted_data values(" + str(record[0]) + ", " + str(record[1]) + ", " + str(record[2]) + ", " + str(record[3]) + ", " + str(record[4]) + ");")
                # postingConnection.commit()
                # postingCursor.close()

            time.sleep(3)
postData()