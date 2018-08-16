from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app import firebase
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(),Length(min=2, max=20)])
    first_name = StringField('First Name',
                            validators=[DataRequired(),Length(min=2, max=20)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(),Length(min=2, max=20)])                        
    cellular = StringField('Phone number',
                        validators=[DataRequired(),Length(min=10, max=10)])
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
    # def validate_cellular(self, cellular):
    #     path ='/Users'
    #     data = firebase.get(path, None)
    #     if data:
    #         for key,value in data.items():
    #             if cellular.data == value['cellular']:
    #                 raise ValidationError('That cellular is taken. Please Choose a different.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class BoxForm(FlaskForm):
    name = StringField('Box Name', validators=[DataRequired()])
    submit = SubmitField('Go')

class BoxPasswordForm(FlaskForm):
    password = StringField('password : รหัสไปรษณีย์', validators=[DataRequired()])
    submit = SubmitField('Submit')
