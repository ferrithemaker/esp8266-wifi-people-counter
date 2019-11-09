This project is based on two programs:

WiFiPeopleCounter directory

ESP8266 Arduino INO program to collect the WiFi MAC addresses and send it to a MQTT broker

mqttReceiver.py

Python script to get the information from a MQTT broker and store it to influxdb server


Important note: the MQTT broker and influxdb server can be local or remote (it's up to you)

