# Robin Vize 6-1-20
# Heavy lifting script that does lots of queries to MySQL
# Gets all the sensor data into a usable format ready
# for presentation in PHP or such later

assetN = '1718'
station = 1

import mysql.connector
from datetime import datetime, timedelta
from collections import Counter
from statistics import stdev

# MySQL connect
cnx = mysql.connector.connect(user='', password='', database='') # REDACTED
cur1 = cnx.cursor()
cur2 = cnx.cursor()

# cur1: BCD signals for chosen asset and station
# SQL query
params1 = (assetNo, station) # NB params argument has to be tuple even if single variable used
print("Asset chosen: {}".format(assetNo))
print("Station chosen: {}".format(station))

query1 = ("SELECT `pubsub`.`datetime`, `pubsub`.`bugid`, `pubsub`.`sensor`, "
          "`pubsub`.`value`, `sensors`.`station 1`, `sensors`.`station 2`, "
          "`sensors`.`BCD`, `sensors`.`description` FROM `pubsub` "
          "JOIN `bugs` ON `pubsub`.`bugid` = `bugs`.`bugid` "
          "JOIN `sensors` ON `sensors`.`sensor` = `pubsub`.`sensor` "
          "AND `sensors`.`bugid` = `pubsub`.`bugid` "
          "WHERE `bugs`.`asset` = %s AND `sensors`.`.BCD` = 1 "
          AND %s = 1 ORDER BY `pubsub`.`datetime`")
          
# Execute query
cur1.execute(query1, params1)
station1BCD = []
for result in curl:
  station1BCD.append(result)
  
# Determine station 1 changeover events
eventsStation1BCD = []
events = 0
for e in range(len(station1BCD)):
  BCDval = int(station1BCD[e][7].replace("BCD",""))
  # events 0, initial entry
  if e == 0:
    eventsStation1BCD.append([datetime(1,1,1), BCDval])
    continue
  prevSignal = station1BCD[e][0] - station1BCD[e-1][0]
  # carrying on with BCD cluster
  if prevSignla <= timedelta(seconds=3):
    if station1BCD[e][3] == 1:
      eventsStation1BCD[events][1] += BCDval
    else:
      eventsStation1BCD[events][1] -= BCDval
    eventsStation1BCD[events][0] = station1BCD[e][0]
  else: # new BCD cluster
    eventsStation1BCD.append([datetime(1,1,1), eventsStation1BCD[events][1])
    events += 1
    if station1BCD[e][3] == 1:
      eventsStation1BCD[events][1] += BCDval
    else:
      eventsStation1BCD[events][1] -= BCDval
    eventsStation1BCD[events][0] = station1BCD[e][0]
    
# List of all the unique BCD combinations used
Counter(x[1] for x in eventsStation1BCD).keys()
# Number of times each BCD combo used
Counter(x[1] for x in eventsStation1BCD).value()

# cur2: Sensor signals for first run, first variant
# SQL query
dt1 = eventsStation1BCD[4][0]
dt2 = eventsStation1BCD[5][0]
variant = eventsStation1BCD[4][1]
print("Variant chosen: {}".format(variant))
params2 = (assetNo, dt1, dt2)

query2 = ("SELECT `pubsub`.`datetime`, `pubsub`.`bugid`, `pubsub`.`sensor`, "
          "`pubsub`.`value`, `sensors`.`station 1`, `sensors`.`station 2`, "
          "`sensors`.`BCD`, `sensors`.`description` FROM `pubsub` "
          "JOIN `bugs` ON `pubsub`.`bugid` = `bugs`.`bugid` "
          "JOIN `sensors` ON `sensors`.`sensor` = `pubsub`.`sensor` "
          "AND `sensors`.`bugid` = `pubsub`.`bugid` "
          "WHERE `bugs`.`asset` = %s AND `sensors`.`BCD` = 0 "
          "AND `sensors`.`station 1` = 1 "
          "AND `pubsub`.`datetime` BETWEEN %s AND %s "
          "ORDER BY `pubsub`.`datetime`")
          
# Execute query
cur2.execute(query2, params2)
station1cycle = []
for result in cur2:
  station1cycle.append(result)
  print(result)
  
# Sensors present in cycle(s)
sensorPres = Counter(x[2] for x in station1cycle).keys()
print("Sensors present: {}".format(sensorsPres))

# Present sensors time differences
tdArray = []
uid = 0
for sensor in sensorsPres:
  for state in (0, 1):
    uid += 1
    firstDt = datetime(1,1,1)
    for entry in station1cycle:
      if (sensor in entry[2]) and (state == entry[3]):
        if firstDt == datetime(1,1,1):
          firstDt = entry[0]
        else:
          currentDt = entry[0]
          
          diffDt = currentDt - firstDt
          tdArray.append([uid, sensor, state, diffDt])
          firstDt = currentDt
          
# Calculate means and SD's to get flagship sensor
means = {}
SDs = {}
for unique in Counter(x[0] for x in tdArray).keys():
  tds = [i[3] for i in tdArray if unique == i[0]]
  
  averageTd = sum(tds, timedelta(0)) / len(tds)
  means[unique] = averageTd.seconds
  
  tdSecs = [x.seconds for x in tds]
  SD = stdev(tdSecs)
  SDs[unique] = SD
  
smallestSD = min(SDs.values()) # what happens if tie for lowest?

for key, value, in SDs.items():
  if value == smallestSD:
    fsSensor = key
    
for x in tdArray:
  if x[0] == fsSensor:
    sensor = x[1]
    state = x[2]
    flagshipSensor = (sensor, state)
    
# Safe exit
cur1.close()
cur2.close()
cnx.close()
  
