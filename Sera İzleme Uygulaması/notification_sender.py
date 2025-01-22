from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from utils.mqttBroker import MQTTBroker
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client['sensor_network'] 
collection = db['rules']


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "serauygulamasi@gmail.com"
SMTP_PASSWORD = "password"  

TIMEOUT = 10

last_sent_time = 0

def on_message(client, userdata, message):
    try:
        data = eval(message.payload.decode())  
        print(f"Gelen Mesajı: {data}")

        rules = get_rules()
        notifications = check_rule(data, rules)

        global last_sent_time
        current_time = time.time()
        if current_time - last_sent_time > TIMEOUT:
            last_sent_time = current_time
            for email, parameter, param_value, condition, rule_value in notifications:
                subject = f"Notification: Rule Triggered for {parameter}"
                body = (f"The parameter '{parameter}' has triggered a rule.\n\n"
                        f"Condition: {parameter} {condition.replace('_', ' ')} {rule_value}\n"
                        f"Current Value: {param_value}\n\n"
                        f"Please take necessary action.")

                send_email(email, subject, body)

    except Exception as e:
        print(f"Veri işleme hatası: {e}")
    
def check_rule(data, rules):

    notifications = []
    for rule in rules:
        parameter = rule['parameter']
        condition = rule['condition']
        value = rule['value']
        email = rule['email']

        if parameter in data:
            if condition == "greater_than" and data[parameter] > value:
                notifications.append((email, parameter, data[parameter], condition, value))
            elif condition == "less_than" and data[parameter] < value:
                notifications.append((email, parameter, data[parameter], condition, value))
        print("Notifincation: " + notifications)
    return notifications

def get_rules():
    return list(collection.find())

def check_rule(data, rules):

    notifications = []
    for rule in rules:
        parameter = rule['parameter']
        condition = rule['condition']
        value = rule['value']
        email = rule['email']

        if parameter in data:
            if condition == "greater_than" and data[parameter] > value:
                notifications.append((email, parameter, data[parameter], condition, value))
            elif condition == "less_than" and data[parameter] < value:
                notifications.append((email, parameter, data[parameter], condition, value))

    return notifications

def send_email(to_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)

            print(f"E-posta gönderildi: {to_email}")
        except Exception as e:
            print(f"E-posta gönderilemedi: {e}")
        print("eposta gonder")


_mqtt = MQTTBroker()
_mqtt.on_message_callback(on_message)
_mqtt.connect() 


if __name__ == '__main__':    
    try:
        _mqtt.start_loop()
    
    except KeyboardInterrupt:
        print("Dinleme sonlandırıldı.")
        _mqtt.disconnect()



    