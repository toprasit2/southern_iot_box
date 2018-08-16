from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from firebase import firebase
import firebase_admin
from firebase_admin import credentials
import datetime

cred = credentials.Certificate("southern-iot-box-firebase-adminsdk-m2cbd-77872d57f7.json")
firebase_admin.initialize_app(cred)
firebase = firebase.FirebaseApplication('https://southern-iot-box.firebaseio.com')

app = Flask(__name__) 
#auto reloading

app.config['SECRET_KEY'] = '39380a3952f0ae125a699fd873560c51'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'red lighten-2'

from flask_mqtt import Mqtt
app.config['MQTT_BROKER_URL'] = 'localhost'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
mqtt = Mqtt(app)
mqtt.subscribe('open_box')
mqtt.subscribe('is_reserved')
mqtt.subscribe('is_opened')

from app import routes
