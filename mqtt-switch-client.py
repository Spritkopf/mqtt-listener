#!/usr/bin/env python

from mqtt_switch import MqttSWitch
import configparser
import argparse

def my_callback_on():
    # perform your actions here
    print("turning ON")
    return True

def my_callback_off():
    # perform your actions here
    print("turning OFF")
    return True


parser = argparse.ArgumentParser(description='Client for a Home Assistant MQTT Switch')
parser.add_argument('-c', '--configfile', dest='config_file', action='store', type=str,
                    default='mqtt-switch.conf', help='Path to config file to use')

args = parser.parse_args()

print(args.config_file)    
try:
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    config.read(args.config_file)

    l = MqttSWitch(config['CONFIG']['broker_url'], 
                    config['CONFIG']['cmd_topic'], 
                    config['CONFIG']['state_topic'], 
                    config['CONFIG']['available_topic'], 
                    my_callback_on, 
                    my_callback_off,
                    payload_on = config['CONFIG']['payload_on'], 
                    payload_off = config['CONFIG']['payload_off'], 
                    payload_available = config['CONFIG']['payload_available'],
                    payload_not_available = config['CONFIG']['payload_not_available'])
except KeyError:
    print("Invalid config file format")
    exit(1)


l.start_listening_thread()

try:
    while True:
        pass
except KeyboardInterrupt:
    pass
finally:
    print ("Disconnecting...")
    l.stop_listening_thread()
