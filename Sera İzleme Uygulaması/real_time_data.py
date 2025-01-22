from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from utils.mqttBroker import MQTTBroker
import json
import threading
from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:8080")


CORS(app, resources={r"/api/*": {"origins": "*"}}) 
def on_message(client, userdata, message):
    data = json.loads(message.payload.decode())
    socketio.emit('new_data', data)


_mqtt = MQTTBroker()
_mqtt.on_message_callback(on_message)
_mqtt.connect() 


if __name__ == '__main__':

        
    try:
        mqtt_threading = threading.Thread(target=_mqtt.start_loop)
        mqtt_threading.start()
        socketio.run(app, port=5000,debug=True)
    
    except KeyboardInterrupt:
        print("Dinleme sonlandırıldı.")
        _mqtt.disconnect()



    