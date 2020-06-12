#!/usr/bin/env python
import paho.mqtt.client as mqtt


class MqttListener(object):

    _topic_callbacks = dict()

    def __init__(self, host, port=1883, client_id=None):

        self.client = mqtt.Client(client_id=client_id)
   
        self.client.connect(host, port, 60)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        

    def start_listening_thread(self):
        self.client.loop_start()

    def stop_listening_thread(self):
        self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    def _on_message(self, client, userdata, msg):
        ''' Execute the callback matching the received topic '''

        try:
            self._topic_callbacks[msg.topic](msg.payload)
        except KeyError:
            # just ignore topics which are not registered
            pass

    def set_topic_callback(self, topic, callback):
        ''' Subscribe to a topic and store it together with the 
        associated callback'''

        self.client.subscribe(topic)
        self._topic_callbacks[str(topic)]=callback


if __name__ == "__main__":
    
    def my_callback(payload):
        print("Got a payload: ", payload)

    l = MqttListener("localhost")
    l.set_topic_callback('test', my_callback)
    l.start_listening_thread()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        print ("Disconnecting...")
        l.stop_listening_thread()