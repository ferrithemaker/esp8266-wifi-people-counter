
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import time

def on_message(client,userdata,message):
	mac = str(message.payload.decode("utf-8"))
	print("message received: " , mac)
	if mac != "":
		last15mResults = influxclient.query('SELECT total FROM traffic_accounting WHERE mac = \''+mac+'\' and time > now() - 15m;')
		last15mPoints = last15mResults.get_points()
		last15mPoints = list(last15mPoints)
		halfDayResults = influxclient.query('SELECT total FROM traffic_accounting WHERE mac = \''+mac+'\' and time > now() - 12h;')
		halfDayPoints = halfDayResults.get_points()
		halfDayPoints = list(halfDayPoints)
		allResults = influxclient.query('SELECT total FROM traffic_accounting WHERE mac = \''+mac+'\';')
		allPoints = allResults.get_points()
		allPoints = list(allPoints)
		lenAllPoints = len(allPoints)
		if len(last15mPoints) == 0 and len(halfDayPoints) > 6:
			json_insert = [ { "measurement" : "traffic_accounting", "tags" : { "mac" : mac, "permanent" : "yes" }, "fields" : { "total" : 1, "accumulated" : lenAllPoints } } ]
			influxclient.write_points(json_insert)
		if len(last15mPoints) == 0 and len(halfDayPoints) <= 6:
                        json_insert = [ { "measurement" : "traffic_accounting", "tags" : { "mac" : mac, "permanent" : "no" }, "fields" : { "total" : 1, "accumulated" : lenAllPoints } } ]
                        influxclient.write_points(json_insert)

# MQTT server

broker_address="localhost"
broker_port=1883
broker_user=""
broker_password=""

# Influx setup

influxclient = InfluxDBClient(host='localhost', port=8086)
influxclient.switch_database('sniffer')


#print("creating new instance")

mqttclient = mqtt.Client("mqttsniffer") #create new instance
mqttclient.username_pw_set(broker_user,broker_password)

#print("connecting to broker")

mqttclient.connect(broker_address,port=broker_port) #connect to broker
mqttclient.loop_start()

#print("Subscribing to topic")

mqttclient.subscribe("esp/sniffer")
mqttclient.on_message=on_message        #attach function to callback

try:
	while True:
		time.sleep(1)
except KeyboardInterrupt:
	print("bye")
	mqttclient.disconnect()
	mqttclient.loop_stop()
