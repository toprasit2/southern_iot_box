from flask import Flask
app = Flask(__name__) 

from flask_mqtt import Mqtt
app.config['MQTT_BROKER_URL'] = 'localhost'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
mqtt = Mqtt(app)

import pyrebase

config = {
    "apiKey": "AIzaSyCk9qv1iJZp16IXL5Uit6oJL0l39P2WwTE",
    "authDomain": "southern-iot-box.firebaseapp.com",
    "databaseURL": "https://southern-iot-box.firebaseio.com",
    "projectId": "southern-iot-box",
    "storageBucket": "southern-iot-box.appspot.com",
    "messagingSenderId": "937282602359"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

import time
import moment
from datetime import datetime
#ทุกๆ 5 วินาที ตรวจสอบสถานะ ถ้า กล่องไม่หมดอายุ(มีคนจอง) ไฟสีแดง กล่องหมดอายุ(ไม่มีคนจอง) กล่องสีเขียว
#localost:9000
@app.route('/')
def init():
    while(1):
        results = db.child("boxs").get()
        historys = db.child("historys").get()
        
        dt = moment.now()
        for i in results.each():
            data = i.val()
            if data['owner'] == 'no':
                pass
            else:
                end_date = data['end_date']
                d_ed = moment.date(end_date['year'],end_date['month'],end_date['day'],end_date['hour'],end_date['minute'],end_date['second'])
                #print(d_ed < dt)
                if d_ed < dt:
                    # mqtt.publish('status_box', i.key())
                    mqtt.publish('status_box', "free")
                    data2 = {"owner": 'no', "status": 'no', "password":[1], "message":[1]}
                    db.child("boxs").child(i.key()).set(data2)
                    for history in historys.each():
                        his = history.val()
                        a = his['box_name']
                        if i.key() in a:
                            a.remove(i.key())
                            data3 = {"box_name":a, "history":his['history']}
                            owner = str(history.key())
                            print(a, owner)
                            db.child('historys').child(history.key()).set(data3)
                else:   
                    pass
        time.sleep(1)
        
if __name__ == '__main__':
    # app.run(port=3134, debug=True)  #on local host
    #app.run(host = '0.0.0.0', port = 3134, debug= False)
    app.run(host = '0.0.0.0',  debug=True, port = 9000)