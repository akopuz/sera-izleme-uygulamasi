import paho.mqtt.client as mqtt


class MQTTBroker:
    def __init__(self, host="localhost", topic = "sera/veriler", port=1883, keep_alive = 60):
        self.host = host
        self.topic = topic
        self.port = port
        self.keep_alive = keep_alive
        self.client = mqtt.Client()

    def connect(self):
        try:
            self.client.connect(self.host, self.port, self.keep_alive)
            self.client.subscribe(self.topic)
        except Exception as e:
            print(f"Hata: {e}")

    def on_message_callback(self, callback_fnc):
        self.client.on_message = callback_fnc

    def start_loop(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()
            
