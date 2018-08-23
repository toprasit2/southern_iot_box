import os
import secrets
import moment
from datetime import datetime
from app import app, bcrypt, login_manager, mqtt
from flask import  render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import RegistrationForm, LoginForm, BoxForm, BoxPasswordForm
from app.login_models import User
from app import firebase as firebase

def my_date_time():
    dt = moment.now()
    d_dict = {
        "day": dt.day,
        "month": dt.month,
        "year" : dt.year,
        "hour" : dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "date" : str(dt)
    }
    return d_dict

def add_date(day, month, year):
    dt = moment.now().add(days=day).add(months=month).add(years=year)
    d_dict = {
        "day": dt.day,
        "month": dt.month,
        "year" : dt.year,
        "hour" : dt.hour,
        "minute": dt.minute,
        "second": dt.second,
        "date" : str(dt)
    }
    return d_dict

@app.route("/map")
@login_required
def map():
    return render_template("map.html", title='Map')

@app.route("/", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        form = BoxForm()
        if form.validate_on_submit():
            box_name = form.name.data
            #print(box_name)
            box = get_box_from_firebase(box_name)
            if not box:
                flash("Don't have"+ box_name, 'red lighten-3')
                return redirect(url_for('home'))

            return redirect(url_for('box', box_name=box_name))
        historys = get_history_from_firebase(current_user.username)
        return render_template("home.html", title='Home', form=form, historys=historys)
    else:
        return redirect(url_for('login'))

def get_box_from_firebase(box_name):
        path = '/boxs/'+ box_name
        return firebase.get(path, None)

def get_history_from_firebase(username):
        path = '/historys/'+ username
        return firebase.get(path, None)

@app.route("/box/<box_name>", methods=['GET', 'POST'])
@login_required
def box(box_name):
    form = BoxPasswordForm()
    box = get_box_from_firebase(box_name)
    if form.validate_on_submit():
        pw = str(form.password.data)
        password = box['password']
        message = box['message']
        password.append(pw)
        reserved_date = box['reserved_date']
        end_date =  box['end_date']
        push = firebase.put('/boxs', box_name, 
                {   'owner': box['owner'],
                    'username': box['username'],
                    'status' : 'reserved',
                    'reserved_date': reserved_date,
                    'end_date' : end_date,
                    'password': password,
                    'message':message
                })
        flash(f'success {pw} was added!', 'green lighten-5') 
    status = box['status']
    if status == 'no':
        #print("ว่าง")
        return render_template('reserve.html', title="Reserve", box_name=box_name)
    else:
        owner = box['owner']
        end_date = box['end_date']
        return render_template('box.html', title='Box'+box_name, box_name=box_name, owner=owner, end_date=end_date, form=form, password=box['password'],message=box['message'])

@app.route("/sending/<box_name>", methods=['GET', 'POST'])
@login_required
def sending(box_name):
    box = get_box_from_firebase(box_name)
    form = BoxPasswordForm()
    if form.validate_on_submit():
        pw = form.password.data
        password = box['password']
        if pw in password:
            sender = current_user.first_name+" "+current_user.last_name
            # print(sender)
            # print(pw)
            password.remove(pw)
            # print(password)
            message = box['message']
            message.append({
                'sender':sender,
                'time':my_date_time(),
                'contact':current_user.cellular
            })
            reserved_date = box['reserved_date']
            end_date =  box['end_date']
            owner = box['owner']
            username = box['username']
            push = firebase.put('/boxs', box_name, 
                    {   'owner': owner,
                        'username': username,
                        'status' : 'reserved',
                        'reserved_date': reserved_date,
                        'end_date' : end_date,
                        'password': password,
                        'message': message
                    })
            flash(f'success {box_name} can open!', 'green lighten-5')
            #function เปิดกล่อง
            mqtt.publish('open_box', box_name)
            path = '/Users/'+username
            data = firebase.get(path, None)
            thumnail = data['link']
            #print(thumnail)
            owner = box['owner']
            end_date = box['end_date']
            return render_template('box.html', title='Box '+box_name, box_name=box_name, owner=owner, end_date=end_date, form=form, thumnail=thumnail)
        else:
            flash(f'invalid ! please contact your customer', 'red lighten-5')
    return redirect(url_for('box', box_name=box_name))

@app.route("/reserve/<box_name>/<int:number>", methods=['GET', 'POST'])
@login_required
def reserve(box_name, number):
    reserve_date = my_date_time()
    if number == 1:
        end_date = add_date(day=1,month=0,year=0)
    elif number == 2:   
        end_date = add_date(day=0,month=1,year=0)
    elif number == 3:
        end_date = add_date(day=0,month=0,year=1)
    box = get_box_from_firebase(box_name)
    if box['status'] == 'no':
        # mqtt.publish('is_reserved', box_name)
        mqtt.publish('status_box', "reserved")
        push = firebase.put('/boxs', box_name,
                {   'owner': current_user.first_name+" "+current_user.last_name,
                    'username': current_user.username,
                    'status' : 'reserved',
                    'reserved_date': reserve_date,
                    'end_date' : end_date,
                    'password': [1],
                    'message': [1]
                })
        historys = get_history_from_firebase(current_user.username)
        box_names = historys['box_name']
        box_names.append(box_name)
        history = historys['history']
        push2 = firebase.put('/historys', current_user.username,
                {   'box_name':box_names,
                    'history':history
                })
        return redirect(url_for('box', box_name=box_name))
    else:
        return redirect(url_for('box', box_name=box_name))

# Authentication ZONE
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #แก้บัคค่า default
        if form.signature.data == "https://firebasestorage.googleapis.com/v0/b/southern-iot-box.appspot.com/o/signature.jpg?alt=media":
            flash(f'Please confirm your sign', 'yellow lighten-5') 
            redirect(url_for('register'))
        else:
            push = firebase.put('/Users', form.username.data,
                {   'username': form.username.data,
                    'password' : hashed_pw,
                    'link' : form.signature.data,
                    'cellular' : form.cellular.data,
                    'first_name' : form.first_name.data,
                    'last_name' : form.last_name.data,
                    'created_date': my_date_time()
                })
            push2 = firebase.put('/historys', form.username.data,
                {   'box_name':[1],
                    'history':[1]
                })    
            print("register success!!")
            flash(f'Account created for {form.username.data}!', 'green lighten-5') 
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

#แก้บัค flask-login
@login_manager.user_loader
def load_user(user):
    path = "Users/"+user
    return User(path)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        path = "Users/"+form.username.data
        user = User(path=path)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'red lighten-3')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@mqtt.on_topic('open_box')
def handle_mytopic(client, userdata, message):
    print('Received message on topic {}: {}'
          .format(message.topic, message.payload.decode()))

@app.route("/open/<box_name>", methods=['GET', 'POST'])
def open(box_name):
    mqtt.publish('open_box', box_name)
    box = get_box_from_firebase(box_name)
    owner = box['owner']
    message = box['message']
    message.append({
        'sender':owner,
        'time':my_date_time(),
        'contact':1
    })
    reserved_date = box['reserved_date']
    end_date =  box['end_date']
    username = box['username']
    password = box['password']
    push = firebase.put('/boxs', box_name, 
            {   'owner': owner,
                'username': username,
                'status' : 'reserved',
                'reserved_date': reserved_date,
                'end_date' : end_date,
                'password': password,
                'message': message
            })
    #print(box_name)
    return redirect(url_for('box', box_name=box_name))

@mqtt.on_topic('is_opened')
def handle_mytopic(client, userdata, message):
    box_name = message.payload.decode()
    box = get_box_from_firebase(box_name)
    message = box['message']
    message.append({
        'sender':'opened box',
        'time':my_date_time(),
        'contact':1
    })
    reserved_date = box['reserved_date']
    end_date =  box['end_date']
    owner = box['owner']
    username = box['username']
    password = box['password']
    push = firebase.put('/boxs', box_name, 
            {   'owner': owner,
                'username': username,
                'status' : 'reserved',
                'reserved_date': reserved_date,
                'end_date' : end_date,
                'password': password,
                'message': message
            })
    #print(box_name)

@mqtt.on_topic('is_closed')
def handle_mytopic(client, userdata, message):
    box_name = message.payload.decode()
    box = get_box_from_firebase(box_name)
    message = box['message']
    message.append({
        'sender':'closed box',
        'time':my_date_time(),
        'contact':1
    })
    reserved_date = box['reserved_date']
    end_date =  box['end_date']
    owner = box['owner']
    username = box['username']
    password = box['password']
    push = firebase.put('/boxs', box_name, 
            {   'owner': owner,
                'username': username,
                'status' : 'reserved',
                'reserved_date': reserved_date,
                'end_date' : end_date,
                'password': password,
                'message': message
            })
    # print(box_name)

import json
@app.route("/api")
def api():
    data = {
        'a' : 'apple',
        'b' : 'banana',
        'c' : 'carrot'
    }
    
    return json.dumps(data, ensure_ascii=False)