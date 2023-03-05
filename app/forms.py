# Here we define the forms used in the application.
# These forms are automatically rendered onto the webpage via wtf_forms.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, IntegerField, FloatField, DateField, TimeField, DateTimeField, SelectField
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
    user_cat = SelectField('User Category', choices= [ ('admin'), ('front_desk'), ('data_entry'), ('doctor')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# These are the forms to reset password.
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

# An empty form.
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

# This is the form to add a new user to the database.
class UserForm(FlaskForm):
    user_cat = SelectField('User Category', choices=[('front_desk'), ('data_entry'), ('doctor')], validators=[DataRequired()])
    SSN = IntegerField('SSN', validators=[DataRequired()])
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

class QueryPatientsSSNForm(FlaskForm):
    SSN = IntegerField('Patient SSN', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DeleteUserForm(FlaskForm):
    SSN = IntegerField('User SSN', validators=[DataRequired()])
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
    certificationExpires = DateField('Certification Expires', validators=[DataRequired()], format='%Y-%m-%d')
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
    head = IntegerField('Department Head ID', validators=[DataRequired()])
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
