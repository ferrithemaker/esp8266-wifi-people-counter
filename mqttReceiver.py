
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import time
import datetime
import snifferconfig as cfg

def on_message(client,userdata,message):
	mac = str(message.payload.decode("utf-8"))
	if mac != "":
		last15mResults = influxclient.query('SELECT activity FROM traffic_accounting WHERE mac = \''+mac+'\' and time > now() - 15m;')
		#print('SELECT total FROM traffic_accounting WHERE mac = \''+mac+'\' and time > now() - 1h;')
		last15mPoints = last15mResults.get_points()
		last15mPoints = list(last15mPoints)
		#print(len(points))
		twoHoursResults = influxclient.query('SELECT activity FROM traffic_accounting WHERE mac = \''+mac+'\' and time > now() - 2h;')
		twoHoursPoints = twoHoursResults.get_points()
		twoHoursPoints = list(twoHoursPoints)
		allResults = influxclient.query('SELECT activity FROM traffic_accounting WHERE mac = \''+mac+'\';')
		allPoints = allResults.get_points()
		allPoints = list(allPoints)
		lenAllPoints = len(allPoints)
		if len(last15mPoints) == 0 and len(twoHoursPoints) > 6:
			json_insert = [ { "measurement" : "traffic_accounting", "tags" : { "mac" : mac, "permanent" : "yes" }, "fields" : { "activity" : 1, "total_activity" : lenAllPoints } } ]
			influxclient.write_points(json_insert)
			if log:
				logfile.write("%s,PERMANENT,%s\r\n" %(mac,datetime.datetime.now()))
			if debug:
				print("MAC Received:",mac,"ADDED AS PERMANENT at",datetime.datetime.now())
		elif len(last15mPoints) == 0 and len(twoHoursPoints) <= 6:
			json_insert = [ { "measurement" : "traffic_accounting", "tags" : { "mac" : mac, "permanent" : "no" }, "fields" : { "activity" : 1, "total_activity" : lenAllPoints } } ]
			influxclient.write_points(json_insert)
			if log:
                                logfile.write("%s,NOT PERMANENT,%s\r\n" %(mac,datetime.datetime.now()))
			if debug:
				print("MAC Received:",mac,"ADDED AS NOT PERMANENT at",datetime.datetime.now())
		else:
			if log:
                                logfile.write("%s,NOT ADDED (TOO SOON),%s\r\n" %(mac,datetime.datetime.now()))
			if debug:
				print("MAC Received:",mac,"NOT ADDED BECAUSE RECENT PREVIOUS PRESENCE DETECTED < 15M at",datetime.datetime.now())

debug = True
log = True

if log:
	logfile = open("log.csv", "a")


# Influx setup
influxclient = InfluxDBClient(host=cfg.db_address, port=cfg.db_port)
influxclient.switch_database(cfg.db_name)


#print("creating new instance")
mqttclient = mqtt.Client("mqttsniffer") #create new instance
mqttclient.username_pw_set(cfg.broker_user,cfg.broker_password)

#print("connecting to broker")
mqttclient.connect(cfg.broker_address,port=cfg.broker_port) #connect to broker
mqttclient.loop_start()

#print("Subscribing to topic")
mqttclient.subscribe(cfg.broker_topic)
mqttclient.on_message=on_message        #attach function to callback

try:
	while True:
		time.sleep(1)

except KeyboardInterrupt:
	print("bye")
	if log:
		logfile.close()
	mqttclient.disconnect()
	mqttclient.loop_stop()
