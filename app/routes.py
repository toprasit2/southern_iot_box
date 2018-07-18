import os
import secrets
import datetime
from app import app, firebase, bcrypt, login_manager
from flask import  render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from app.login_models import User

@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("home.html", title='Home')
    else:
        return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.signature.data == "https://firebasestorage.googleapis.com/v0/b/southern-iot-box.appspot.com/o/signature.jpg?alt=media":
            flash(f'Please confirm your sign', 'yellow lighten-5') 
            redirect(url_for('register'))
        else:
            push = firebase.put('/Users', form.username.data,
                {   'username': form.username.data,
                    'password' : hashed_pw,
                    'link' : form.signature.data,
                    'email' : form.email.data,
                    'created_date': datetime.datetime.now()
                })
            print("register success!!")
            flash(f'Account created for {form.username.data}!', 'green lighten-5') 
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

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