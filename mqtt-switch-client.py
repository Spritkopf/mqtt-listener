#!/usr/bin/env python
import paho.mqtt.client as mqtt

class MqttSWitch(object):

    
    
    def __init__(self, host, cmd_topic, state_topic, available_topic, on_callback, off_callback, port=1883, client_id=None, payload_on="ON", payload_off="OFF", payload_available="online", payload_not_available="offline"):

        self.client = mqtt.Client(client_id=client_id)

        self.client.will_set(available_topic, payload_not_available, retain=True)
        self.client.connect(host, port, 60)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self._callbacks = dict([(payload_on, on_callback),(payload_off, off_callback)])
        #self._callbacks.append(dict(payload_on, on_callback))
        #self._callbacks.append(dict(payload_off, off_callback))
        
        self.client.subscribe(cmd_topic)
        
        self._state_topic = state_topic
        self._payload_on = payload_on
        self._payload_off = payload_off

        self.client.publish(available_topic, payload_available, retain=True)
        

    def start_listening_thread(self):
        self.client.loop_start()

    def stop_listening_thread(self):
        self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def _on_message(self, client, userdata, msg):
        ''' Execute the callbacks for messages matching `payload_on` or `payload_off` '''

        try:
            payload_str = msg.payload.decode('UTF-8')
            result = self._callbacks[payload_str]()

            if result == True:
                self.client.publish(self._state_topic, payload_str, retain=True)

        except KeyError:
            # just ignore messages with unknown payloads
            pass


if __name__ == "__main__":

    import configparser
    import subprocess

    import argparse

    sys_command_on = ""
    sys_command_off = ""

    def my_callback_on():
        print("turning ON")
        try:
            cmd_result = subprocess.run(sys_command_on)
            print("The exit code was: %d" % cmd_result.returncode)
        except Exception as e:
            print(e)

        if cmd_result.returncode == 0:
            return True
        
        return False

    def my_callback_off():
        print("turning OFF")
        cmd_result = subprocess.run(sys_command_off)
        print("The exit code was: %d" % cmd_result.returncode)
        
        if cmd_result.returncode == 0:
            return True

        return False

    parser = argparse.ArgumentParser(description='Client for a Home Assistant MQTT Switch')
    parser.add_argument('-c', '--configfile', dest='config_file', action='store', type=str,
                        default='mqtt-switch.conf', help='Path to config file to use')

    args = parser.parse_args()

    print(args.config_file)    
    try:
        config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
        config.read(args.config_file)
        sys_command_on = config.getlist('CONFIG', 'cmd_on')
        sys_command_off = config.getlist('CONFIG', 'cmd_off')

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
