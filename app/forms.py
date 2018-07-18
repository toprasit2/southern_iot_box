from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app import firebase
class RegistrationForm(FlaskForm):
    username = StringField('Name',
                            validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Comfirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    signature = StringField('Signature', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        path ='/Users/'+ username.data +'/username'
        username_check = firebase.get(path, None)

        if username_check == username.data:
            raise ValidationError('That username is taken. Please Choose a different.')
    def validate_email(self, email):
        path ='/Users'
        data = firebase.get(path, None)
        if data:
            for key,value in data.items():
                if email.data == value['email']:
                    raise ValidationError('That email is taken. Please Choose a different.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken. Please Choose a different.')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please Choose a different.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

