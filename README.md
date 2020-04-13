# The WiFi people counter project is based on two programs:

## WiFiPeopleCounter directory:

You can find the ESP8266 Arduino INO program to collect the WiFi MAC addresses and send it to a MQTT broker

## mqttReceiver.py:

Python script to get the information from a MQTT broker and store it to influxdb server


**Important note:** the MQTT broker and influxdb server can be local or remote (it's up to you)

**Important note:** you need to rename the snifferconfig_template.py file to snifferconfig.py and add the requiered data

options:

**debug**  enables information output
**log** enables creation of data csv file
**mac_randomizer_mode** enables mac randomizer mode detection to (try to) avoid privacy settings of some WiFi devices 
