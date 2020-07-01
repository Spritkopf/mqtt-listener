import paho.mqtt.client as mqtt

class MqttSWitch(object):

    
    
    def __init__(self, host, cmd_topic, state_topic, available_topic, on_callback, off_callback, port=1883, client_id=None, payload_on="ON", payload_off="OFF", payload_available="online", payload_not_available="offline", initial_state=None):

        self.client = mqtt.Client(client_id=client_id)

        self.client.will_set(available_topic, payload_not_available, retain=True)
        self.client.connect(host, port, 60)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self._callbacks = dict([(payload_on, on_callback),(payload_off, off_callback)])
        
        self.client.subscribe(cmd_topic)
        
        self._state_topic = state_topic
        self._payload_on = payload_on
        self._payload_off = payload_off

        self.client.publish(available_topic, payload_available, retain=True)

        if initial_state is not None:
            self.client.publish(state_topic, initial_state)
        

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
