from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, length, Email, EqualTo, ValidationError
from flaskapp.models import User, ReservedUsername
from flask_login import current_user



class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min = 2, max = 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('ConfirmPassword', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        res_user = ReservedUsername.query.filter_by(res_username = username.data).first()
        if user or res_user:
            raise ValidationError('That username is taken! Please choose different one')
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email already exists! Please choose different one')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=2, max = 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken, Try another one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is user for an account!!')
         

class searchForm(FlaskForm):
    username = StringField('Search user', validators=[DataRequired(), length(max=60)])
    submit = SubmitField('Search')

class reserveForm(FlaskForm):
    res_username = StringField('username', validators=[DataRequired(), length(min=2, max=20)])
    reserved_for = StringField('Reserved for', validators=[DataRequired()])
    linkedto = SelectField('Choose option', choices=[('notlinked','Not Linked'), ('mobile','Mobile'), ('email','E-Mail')])
    submit = SubmitField('Reserve')

    def validate_res_username(self, res_username):
        user = User.query.filter_by(username=res_username.data).first()
        if user:
            raise ValidationError('Username already taken, Try another one')

class UploadcsvForm(FlaskForm):
    csv_file = FileField('Upload CSV File', validators=[DataRequired(), FileAllowed(['csv'])])
    submit = SubmitField('Upload')
