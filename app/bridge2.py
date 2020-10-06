# Robin Vize 18-12-19
# Bridging script from Mosquitto to MySQL (both local host)
# bridge2.py version for database and MQTT message overhaul

import paho.mqtt.client as mqtt
import mysql.connector
from time import time

# MySQL connect
cnx = mysql.connector.connect(user='', password='', database='') # REDACTED
curMQTT = cnx.cursor() # for on_message async callback

insertLine = ()
insertMe = ("INSERT INTO ___ "
            "(datetime, bugid, sensor, value) "
            "VALUES (%s, %s, %s, %s)")
            
# Mosquitto connect
def on_connect(client, userdata, flags, rc):
  client.subscribe("bugs/#")
  
# Mosquitto message handle
def on_message(client, userdata, msg):
  # MQTT topic
  splitMessage = msg.topic.split('/')
  bugid = splitMessage[1]
  sensor = splitMessage[2]
  value = splitMessage[3]
  
  # MQTT payload
  dt = msg.payload.decode()
  # swap time->date to date->time for MySQL formatting
  # where date becomes yyyy-MM-dd format as well
  dt = dt.split(' ')
  rd = dt[1].split('/')
  revD = rd[2] + '-' + rd[1] + '-' + rd[0]
  datetime = revD + " " + dt[0]
  # filters out when NTP isn't ready and date is Unix epoch
  if rd[2] == "1970":
    return
    
  # SQL insert
  interLine = (datetime, bugid, sensor, value)
  curMQTT.execute(insertMe, insertLine)
  cnx.commit()
  
# MQTT setup
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("HOSTNAME") # REDACTED
client.loop_start() # this is non-blocking, unlike loop_forever

# MySQL keep alive loop every hour
timeThen = 0
while True:
  if ((time() - timeThen) > 3600):
    timeThen = time()
    alive = cnx.is_connected()
  
