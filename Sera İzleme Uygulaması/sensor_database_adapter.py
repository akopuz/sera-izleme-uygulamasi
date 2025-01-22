import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import json
from utils.mqttBroker import MQTTBroker
import pytz

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client['sensor_network'] 
collection = db['sensor_values']


def on_message(client, userdata, message):
    msg = json.loads(message.payload.decode())
    msg['timestamp'] = datetime.now(pytz.UTC)
    print(f"Mesaj alındı -> Topic: {message.topic}, Payload: {message.payload.decode()}")
    collection.insert_one(msg)


_mqtt = MQTTBroker()
_mqtt.on_message_callback(on_message)
_mqtt.connect() 

try:
    _mqtt.start_loop()
except KeyboardInterrupt:
    print("Dinleme sonlandırıldı.")
    _mqtt.disconnect()
