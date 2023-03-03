# Here we define the forms used in the application.
# These forms are automatically rendered onto the webpage via wtf_forms.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, IntegerField, FloatField, DateField, TimeField, DateTimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length,NumberRange
from app import app
from app.models import *
from flask import request
from datetime import date

# This is the form used to create a search query.
class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)

# This is the form used to login an existing user. All stakeholders can login via the same form.
class LoginForm(FlaskForm):
    user_cat = StringField('User Category', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# This is the form used to create a new customer user.
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# This is the form used to create a new staff user.
class StaffRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    sys_pass = PasswordField(
        'System Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    
    def validate_sys_pass(self, sys_pass):
        if not str(sys_pass.data) == str(app.config['SYS_PASSWORD']):
            raise ValidationError('Incorrect System Password!')

# These are the forms to reset password.
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

# This is the form used to edit the profile of a user.
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

# This is the form to add funds to a user account.
class AddFundsForm(FlaskForm):
    balance = FloatField('Funds to add', validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField('Submit')

# This is the form to add more copies of a movie to the database.
class AddStockForm(FlaskForm):
    id = IntegerField('Movie ID', validators=[DataRequired()])
    stock = IntegerField('Stock to add', validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField('Submit')

# An empty form.
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

# This is the form to add a new user to the database.
class UserForm(FlaskForm):
    user_cat = StringField('User Category', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AddResultsPrescriptionsForm(FlaskForm):
    physician = IntegerField('Physician ID', validators=[DataRequired()])
    patient = IntegerField('Patient ID', validators=[DataRequired()])
    medication = IntegerField('Medication ID', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    appointment = IntegerField('Appointment ID', validators=[DataRequired()])
    dose = IntegerField('Dose', validators=[DataRequired()])
    report = StringField('Report URL')
    submit = SubmitField('Submit')

class AddMedicationForm(FlaskForm):
    code = IntegerField('Code', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddAffiliationForm(FlaskForm):
    physician = IntegerField('Physician ID', validators=[DataRequired()])
    department = IntegerField('Department ID', validators=[DataRequired()])
    primaryAffiliation = BooleanField('Primary Affiliation',default=False)
    submit = SubmitField('Submit')

class AddTrainingForm(FlaskForm):
    physician = IntegerField('Physician ID', validators=[DataRequired()])
    treatment = IntegerField('Treatment ID', validators=[DataRequired()])
    certificationDate = DateField('Certification Date', validators=[DataRequired()], format='%Y-%m-%d')
    certificationExprires = DateField('Certification Expires', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Submit')

class ScheduleAppointmentForm(FlaskForm):
    appointmentID = IntegerField('Appointment ID', validators=[DataRequired()])
    patient = IntegerField('Patient ID', validators=[DataRequired()])
    prepNurse = IntegerField('Prep Nurse ID', validators=[DataRequired()])
    physician = IntegerField('Physician ID', validators=[DataRequired()])
    start = DateTimeField('Start', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    end = DateTimeField('End', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    submit = SubmitField('Submit')

class AdmitPatientForm(FlaskForm):
    patient = IntegerField('Patient ID', validators=[DataRequired()])
    procedure = IntegerField('Procedure ID', validators=[DataRequired()])
    stay = IntegerField('Stay ID', validators=[DataRequired(),NumberRange(min=0)])
    room = IntegerField('Room ID', validators=[DataRequired(),NumberRange(min=0)])
    start = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    physician = IntegerField('Physician ID', validators=[DataRequired()])
    assistingNurse = IntegerField('Assisting Nurse ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DischargePatientForm(FlaskForm):
    stay = IntegerField('Stay ID', validators=[DataRequired(),NumberRange(min=0)])
    end = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Submit')

class AddProcedureForm(FlaskForm):
    code = IntegerField('Procedure Code', validators=[DataRequired()])
    name = StringField('Procedure Name', validators=[DataRequired()])
    cost = IntegerField('Procedure Cost', validators=[DataRequired(),NumberRange(min=0)])
    submit = SubmitField('Submit')

class AddDepartmentForm(FlaskForm):
    departmentID = IntegerField('Department ID', validators=[DataRequired()])
    name = StringField('Department Name', validators=[DataRequired()])
    head = IntegerField('Department Head', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddPhysicianForm(FlaskForm):
    employeeID = IntegerField('Physician ID', validators=[DataRequired()])
    name = StringField('Physician Name', validators=[DataRequired()])
    position = StringField('Physician Position', validators=[DataRequired()])
    SSN = IntegerField('Physician SSN', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegisterPatientForm(FlaskForm):
    name = StringField('Patient Name', validators=[DataRequired()])
    address = StringField('Patient Address', validators=[DataRequired()])
    phone = StringField('Patient Phone', validators=[DataRequired()])
    insuranceID = IntegerField('Patient Insurance ID', validators=[DataRequired()])
    SSN = IntegerField('Patient SSN', validators=[DataRequired()])
    PCP = IntegerField('Patient PCP', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddRoomForm(FlaskForm):
    number = IntegerField('Room ID', validators=[DataRequired()])
    type = StringField('Room Type', validators=[DataRequired()])
    unavailable = BooleanField('Room Unavailable',default=False)
    submit = SubmitField('Submit')

class AddNurseForm(FlaskForm):
    employeeID = IntegerField('Nurse ID', validators=[DataRequired()])
    name = StringField('Nurse Name', validators=[DataRequired()])
    position = StringField('Nurse Position', validators=[DataRequired()])
    SSN = IntegerField('Nurse SSN', validators=[DataRequired()])
    registered = BooleanField('Nurse Registered', default=False)
    submit = SubmitField('Submit')

# This is the form to add a new movie to the database.
class MovieForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    img_path = TextAreaField('Image URL', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired(),NumberRange(min=1,max=10)])
    price = FloatField('Price', validators=[DataRequired(),NumberRange(min=1,max=1000)])
    quantity = IntegerField('Quantity', validators=[DataRequired(),NumberRange(min=1,max=1000)])
    submit = SubmitField('Submit')

# This is the form to edit a movie in the database.
class EditMovieForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    img_path = TextAreaField('Image URL')
    description = TextAreaField('Description')
    genre = StringField('Genre')
    rating = FloatField('Rating', validators=[NumberRange(min=1,max=10)])
    price = FloatField('Price', validators=[NumberRange(min=1,max=1000)])
    quantity = IntegerField('Quantity', validators=[NumberRange(min=1,max=1000)])
    submit = SubmitField('Submit')

    def __init__(self, original_movie, *args, **kwargs):
        super(EditMovieForm, self).__init__(*args, **kwargs)
        self.original_name = original_movie.name

    def validate_name(self, name):
        if name.data != self.original_name:
            movie = Movie.query.filter_by(name=self.name.data).first()
            if movie is not None:
                raise ValidationError('Please use a different name.')