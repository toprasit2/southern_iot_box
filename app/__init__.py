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

app.config['SECRET_KEY'] = '39380a3952f0ae125a699fd873560c51'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'red lighten-2'


from app import routes
