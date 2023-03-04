# This file contains all the route registrations for the application.
# Routes are called when a specific url is requested by the user.
from datetime import datetime
from locale import getlocale
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import *
from app.models import *
from app.email import send_password_reset_email
from app.functions import *
from flask import g
from datetime import datetime

# Required setup for the search bar.
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

    g.search_form = SearchForm()
    g.locale = str(getlocale())

# Dashboard for admin user.
@app.route('/index_admin', methods=['GET', 'POST'])
@login_required
def index_admin():
    if request.form.get('Add User') == 'Add User':
        return redirect(url_for('add_user'))
    
    if request.form.get('Add Procedure') == 'Add Procedure':
        return redirect(url_for('add_procedure'))
    
    if request.form.get('Add Department') == 'Add Department':
        return redirect(url_for('add_department'))

    if request.form.get('Add Physician') == 'Add Physician':
        return redirect(url_for('add_physician'))
    
    if request.form.get('Add Medication') == 'Add Medication':
        return redirect(url_for('add_medication'))
    
    if request.form.get('Add Room') == 'Add Room':
        return redirect(url_for('add_room'))
    
    if request.form.get('Add Nurse') == 'Add Nurse':
        return redirect(url_for('add_nurse'))
    
    if request.form.get('Add Affiliation') == 'Add Affiliation':
        return redirect(url_for('add_affiliation'))
    
    if request.form.get('Add Training') == 'Add Training':
        return redirect(url_for('add_training'))

    if request.form.get('View Users') == 'View Users':
        page = request.args.get('page', 1, type=int)
        users = User.query.filter(User.user_cat != 'admin').paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=users.next_num) \
            if users.has_next else None
        prev_url = url_for('explore', page=users.prev_num) \
            if users.has_prev else None
        return render_template('index.html', title='Home', users=users.items,
                            next_url=next_url, prev_url=prev_url)

    if request.form.get('Delete User') == 'Delete User':
        return redirect(url_for('delete_user'))
    
    return render_template('index.html', title='Home')

@app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.filter(User.SSN==form.SSN.data).first()
        if user is None:
            flash('User not found')
            return redirect(url_for('delete_user'))
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            flash('User could not be deleted')
            return redirect(url_for('delete_user'))
        flash('User deleted')
        return redirect(url_for('index_admin'))
    return render_template('add_data.html', title='Delete User', form=form)

# Dashboard for front_desk user.
@app.route('/index_front_desk', methods=['GET', 'POST'])
@login_required
def index_front_desk():
    if request.form.get('Register Patient') == 'Register Patient':
        return redirect(url_for('register_patient'))
    
    if request.form.get('Admit Patient') == 'Admit Patient':
        return redirect(url_for('admit_patient'))
    
    if request.form.get('Schedule Appointment') == 'Schedule Appointment':
        return redirect(url_for('schedule_appointment'))
    
    if request.form.get('Discharge Patient') == 'Discharge Patient':
        return redirect(url_for('discharge_patient'))
    
    return render_template('index.html', title='Home')

# Dashboard for data_entry user.
@app.route('/index_data_entry', methods=['GET', 'POST'])
@login_required
def index_data_entry():
    if request.form.get('Add results and prescriptions') == 'Add results and prescriptions':
        return redirect(url_for('add_results_prescriptions'))
    
    return render_template('index.html', title='Home')

# Dashboard for doctor user.
@app.route('/index_doctor', methods=['GET', 'POST'])
@login_required
def index_doctor():
    doctor = Physician.query.filter(Physician.SSN==current_user.SSN).first()

    if request.form.get('View my Patients') == 'View my Patients':
        page = request.args.get('page', 1, type=int)
        patients_1 = Prescribes.query.filter(Prescribes.Physician == doctor.EmployeeID).with_entities(Prescribes.Patient)
        patients_2 = Patient.query.filter(Patient.PCP==doctor.EmployeeID).with_entities(Patient.SSN)
        patients_3 = Undergoes.query.filter(Undergoes.Physician==doctor.EmployeeID).with_entities(Undergoes.Patient)
        patients_4 = Appointment.query.filter(Appointment.Physician==doctor.EmployeeID).with_entities(Appointment.Patient)
        patients=[]
        for p in patients_1:
            patients.append(p[0])
        for p in patients_2:
            patients.append(p[0])
        for p in patients_3:
            patients.append(p[0])
        for p in patients_4:
            patients.append(p[0])

        patients_full = Patient.query.filter(Patient.SSN==patients[0])
        for p in patients:
            pp = Patient.query.filter(Patient.SSN==p)
            patients_full.union(pp)
        patients = patients_full
        patients = patients.paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=patients.next_num) \
            if patients.has_next else None
        prev_url = url_for('explore', page=patients.prev_num) \
            if patients.has_prev else None
        return render_template('index.html', title='Home', patients=patients.items,
                            next_url=next_url, prev_url=prev_url)
    
    if request.form.get('View my Appointments') == 'View my Appointments':
        page = request.args.get('page', 1, type=int)
        appointments = Appointment.query.filter(Appointment.Physician==doctor.EmployeeID).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=appointments.next_num) \
            if appointments.has_next else None
        prev_url = url_for('explore', page=appointments.prev_num) \
            if appointments.has_prev else None
        return render_template('index.html', title='Home', appointments=appointments.items,
                            next_url=next_url, prev_url=prev_url)
    
    if request.form.get('View my Prescriptions') == 'View my Prescriptions':
        page = request.args.get('page', 1, type=int)
        prescriptions = Prescribes.query.filter(Prescribes.Physician==doctor.EmployeeID).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        next_url = url_for('explore', page=prescriptions.next_num) \
            if prescriptions.has_next else None
        prev_url = url_for('explore', page=prescriptions.prev_num) \
            if prescriptions.has_prev else None
        return render_template('index.html', title='Home', prescriptions=prescriptions.items,
                            next_url=next_url, prev_url=prev_url)
    
    if request.form.get('Query all patient information by SSN') == 'Query all patient information by SSN':
        return redirect(url_for('query_patients_ssn'))
    
    return render_template('index.html', title='Home')

@app.route('/query_patients_ssn', methods=['GET', 'POST'])
@login_required
def query_patients_ssn():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = QueryPatientsSSNForm()
    if form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        patient = Patient.query.filter(Patient.SSN==form.SSN.data).first()
        patients = Patient.query.filter(Patient.SSN==form.SSN.data).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        if patient is None:
            flash('Patient not found')
            return redirect(url_for('query_patients_ssn'))
        
        appointments = Appointment.query.filter(Appointment.Patient==patient.SSN).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        prescriptions = Prescribes.query.filter(Prescribes.Patient==patient.SSN).paginate(
            page, app.config['USERS_PER_PAGE'], False)
        return render_template('index.html', title='Home', patients=patients.items, appointments=appointments.items, prescriptions=prescriptions.items)
    return render_template('add_data.html', title='Query Patients by SSN', form=form)

@app.route('/add_results_prescriptions', methods=['GET', 'POST'])
@login_required
def add_results_prescriptions():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddResultsPrescriptionsForm()
    if form.validate_on_submit():
        prescribes = Prescribes(Physician = form.physician.data, Patient = form.patient.data, Medication = form.medication.data, Dose = form.dose.data, Date = form.date.data, Appointment = form.appointment.data, Report = form.report.data)
        try:
            db.session.add(prescribes)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error!')
            return redirect(url_for('add_results_prescriptions'))
        flash('Results and prescriptions added!')
        return redirect(url_for('add_results_prescriptions'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/register_patient', methods=['GET', 'POST']) 
@login_required
def register_patient():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = RegisterPatientForm()
    if form.validate_on_submit():

        proc = Patient(SSN=form.SSN.data, Name=form.name.data, Address=form.address.data, Phone = form.phone.data, InsuranceID = form.insuranceID.data, PCP=form.PCP.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Patient already exists!')
            return redirect(url_for('register_patient'))
        flash('Congratulations, patient has been registered!')
        return redirect(url_for('register_patient'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/admit_patient', methods=['GET', 'POST'])
@login_required
def admit_patient():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AdmitPatientForm()
    if form.validate_on_submit():
        stay = Stay(StayID=form.stay.data ,Patient=form.patient.data,Room=form.room.data,Start=form.start.data)
        undergoes = Undergoes(Patient=form.patient.data ,Procedure_=form.procedure.data,Stay=form.stay.data,Date=form.start.data,Physician=form.physician.data,AssistingNurse=form.assistingNurse.data)
        room = Room.query.filter_by(Number = form.room.data).first()
        if(room.Unavailable == 1):
            flash('Room is unavailable!')
            return redirect(url_for('admit_patient'))
        room.Unavailable = 1

        try:
            db.session.add(stay)
            db.session.add(undergoes)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error, patient has not been admitted!')
            return redirect(url_for('admit_patient'))
        
        flash('Congratulations, patient has been admitted!')
        return redirect(url_for('admit_patient'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/schedule_appointment', methods=['GET', 'POST'])
@login_required
def schedule_appointment():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = ScheduleAppointmentForm()
    if form.validate_on_submit():
        appointment = Appointment(AppointmentID = form.appointmentID.data, Patient = form.patient.data, PrepNurse = form.prepNurse.data, Physician = form.physician.data, Start = form.start.data, End = form.end.data)
        if(form.start.data < datetime.now()):
            flash('Error, appointment has not been scheduled, date must be today or later!' + str(form.date.data) + " " + str(date.today()))
            return redirect(url_for('schedule_appointment'))
        if(form.start.data >= form.end.data):
            flash('Error, appointment has not been scheduled, start time must be before end time!')
            return redirect(url_for('schedule_appointment'))
        earlier_appointment_patient_s = Appointment.query.filter(Appointment.Patient == form.patient.data).filter(Appointment.Start >= form.start.data).filter(Appointment.Start <= form.end.data).first()
        earlier_appointment_physician_s = Appointment.query.filter(Appointment.Physician == form.physician.data).filter(Appointment.Start >= form.start.data).filter(Appointment.Start <= form.end.data).first()
        earlier_appointment_patient_e = Appointment.query.filter(Appointment.Patient == form.patient.data).filter(Appointment.End >= form.start.data).filter(Appointment.End <= form.end.data).first()
        earlier_appointment_physician_e = Appointment.query.filter(Appointment.Physician == form.physician.data).filter(Appointment.End >= form.start.data).filter(Appointment.End <= form.end.data).first()
        if(earlier_appointment_patient_s is not None):
            flash('Error, appointment has not been scheduled, patient has another appointment!')
            return redirect(url_for('schedule_appointment'))
        if(earlier_appointment_patient_e is not None):
            flash('Error, appointment has not been scheduled, patient has another appointment!')
            return redirect(url_for('schedule_appointment'))
        if(earlier_appointment_physician_s is not None):
            flash('Error, appointment has not been scheduled, physician has another appointment!')
            return redirect(url_for('schedule_appointment'))
        if(earlier_appointment_physician_e is not None):
            flash('Error, appointment has not been scheduled, physician has another appointment!')
            return redirect(url_for('schedule_appointment'))
        try:
            db.session.add(appointment)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error, appointment has not been scheduled!')
            return redirect(url_for('schedule_appointment'))
        flash('Congratulations, appointment has been scheduled!')
        return redirect(url_for('schedule_appointment'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/discharge_patient', methods=['GET', 'POST'])
@login_required
def discharge_patient():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = DischargePatientForm()
    if form.validate_on_submit():
        stay = Stay.query.filter_by(StayID = form.stay.data).first()
        if(stay is None):
            flash('Stay not found!')
            return redirect(url_for('discharge_patient'))
        if(stay.End is not None):
            flash('Patient has already been discharged!')
            return redirect(url_for('discharge_patient'))
        stay.End = form.end.data
        room = Room.query.filter_by(Number = stay.Room).first()
        room.Unavailable = 0
        db.session.commit()
        flash('Congratulations, patient has been discharged!')
        return redirect(url_for('discharge_patient'))
    return render_template('add_data.html', title='Home', form=form)


# # Dashboard for front_desk user.
# @app.route('/index_front_desk', methods=['GET', 'POST'])
# @login_required
# def index_front_desk():
#     if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
#         rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))

#     if request.form.get('View Orders') == 'View Orders':
#         orders = view_orders(current_user.id)
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No orders found.')
#             return render_template('index.html', title='Home')
    
#     if request.form.get('View Deadlines') == 'View Deadlines':
#         orders = view_orders(current_user.id)
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             if order.status == 'NO':
#                 order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No approaching deadlines found.')
#             return render_template('index.html', title='Home')
    
#     if str(request.form.get("Return Order"))[:12] == "Return Order":
#         return_movie(int(str(request.form.get('Return Order'))[16:]))

#     if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
#         generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
#     rec_movies = generate_reccomendations(current_user)
#     return render_template('index.html', title='Home',rec_movies=rec_movies)


# # Dashboard for customer user.
# @app.route('/index_user', methods=['GET', 'POST'])
# @login_required
# def index_user():
#     if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
#         rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))

#     if request.form.get('View Orders') == 'View Orders':
#         orders = view_orders(current_user.id)
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No orders found.')
#             return render_template('index.html', title='Home')
    
#     if request.form.get('View Deadlines') == 'View Deadlines':
#         orders = view_orders(current_user.id)
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             if order.status == 'NO':
#                 order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No approaching deadlines found.')
#             return render_template('index.html', title='Home')
    
#     if str(request.form.get("Return Order"))[:12] == "Return Order":
#         return_movie(int(str(request.form.get('Return Order'))[16:]))

#     if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
#         generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
#     rec_movies = generate_reccomendations(current_user)
#     return render_template('index.html', title='Home',rec_movies=rec_movies)

# # Dashboard for staff user
# @app.route('/index_staff', methods=['GET', 'POST'])
# @login_required
# def index_staff():
#     if request.form.get('Add Movie') == 'Add Movie':
#         return redirect(url_for('add_movie'))

#     if request.form.get('View Users') == 'View Users':
#         page = request.args.get('page', 1, type=int)
#         users = User.query.filter_by(user_cat='user').order_by(User.id.desc()).paginate(
#             page, app.config['USERS_PER_PAGE'], False)
#         next_url = url_for('explore', page=users.next_num) \
#             if users.has_next else None
#         prev_url = url_for('explore', page=users.prev_num) \
#             if users.has_prev else None
#         return render_template('index.html', title='Home', users=users.items,
#                             next_url=next_url, prev_url=prev_url)

#     if str(request.form.get('View Orders'))[:11] == 'View Orders':
#         orders = view_orders(int(str(request.form.get('View Orders'))[23:]))
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No orders found.')
#             return render_template('index.html', title='Home')

#     if str(request.form.get('View Deadlines'))[:14] == 'View Deadlines':
#         orders = view_orders(int(str(request.form.get('View Deadlines'))[26:]))
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             if order.status == 'NO':
#                 order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No approaching deadlines found.')
#             return render_template('index.html', title='Home')

#     if str(request.form.get('Delete User'))[:11] == 'Delete User':
#         tbd_user = User.query.filter_by(id = int(str(request.form.get('Delete User'))[15:])).first()
#         if tbd_user is not None:
#             db.session.delete(tbd_user)
#             db.session.commit()
#             flash('User deleted.')
#         else:
#             flash('User not found.')
    
#     if str(request.form.get("Return Order"))[:12] == "Return Order":
#         return_movie(int(str(request.form.get('Return Order'))[16:]))
    
#     if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
#         generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
                                
#     return render_template('index.html', title='Home')

# # Dashboard for manager user.
# @app.route('/index_manager', methods=['GET', 'POST'])
# @login_required
# def index_manager():
#     if request.form.get('Add Movie') == 'Add Movie':
#         return redirect(url_for('add_movie'))

#     if request.form.get('View Users') == 'View Users':
#         page = request.args.get('page', 1, type=int)
#         users = User.query.filter_by(user_cat='user').order_by(User.id.desc()).paginate(
#             page, app.config['USERS_PER_PAGE'], False)
#         next_url = url_for('explore', page=users.next_num) \
#             if users.has_next else None
#         prev_url = url_for('explore', page=users.prev_num) \
#             if users.has_prev else None
#         return render_template('index.html', title='Home', users=users.items,
#                             next_url=next_url, prev_url=prev_url)

#     if request.form.get('View Staff') == 'View Staff':
#         page = request.args.get('page', 1, type=int)
#         users = User.query.filter_by(user_cat='staff').order_by(User.id.desc()).paginate(
#             page, app.config['USERS_PER_PAGE'], False)
#         next_url = url_for('explore', page=users.next_num) \
#             if users.has_next else None
#         prev_url = url_for('explore', page=users.prev_num) \
#             if users.has_prev else None
#         return render_template('index.html', title='Home', users=users.items,
#                             next_url=next_url, prev_url=prev_url)

#     if str(request.form.get('View Orders'))[:11] == 'View Orders':
#         orders = view_orders(int(str(request.form.get('View Orders'))[23:]))
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No orders found.')
#             return render_template('index.html', title='Home')

#     if str(request.form.get('View Deadlines'))[:14] == 'View Deadlines':
#         orders = view_orders(int(str(request.form.get('View Deadlines'))[26:]))
#         order_list=[]
#         for order in orders:
#             movie = Movie.query.filter_by(id = order.movie_id).first()
#             if order.status == 'NO':
#                 order_list.append((order,movie))
#         if len(order_list)>0:
#             return render_template('index.html', order_list=order_list)
#         else:
#             flash('No approaching deadlines found.')
#             return render_template('index.html', title='Home')

#     if str(request.form.get('Delete User'))[:11] == 'Delete User':
#         tbd_user = User.query.filter_by(id = int(str(request.form.get('Delete User'))[15:])).first()
#         if tbd_user is not None:
#             db.session.delete(tbd_user)
#             db.session.commit()
#             flash('User deleted.')
#         else:
#             flash('User not found.')
    
#     if str(request.form.get("Return Order"))[:12] == "Return Order":
#         return_movie(int(str(request.form.get('Return Order'))[16:]))
    
#     if str(request.form.get("Generate Receipt"))[:16] == "Generate Receipt":
#         generate_receipt(int(str(request.form.get('Generate Receipt'))[30:]))
    
#     if request.form.get("Audit") == "Audit":
#         audit()
    
#     return render_template('index.html', title='Home')
                                                     
# The landing page.
@app.route('/', methods=['GET', 'POST'])
def landing():
    return redirect(url_for('explore'))

# All doctors can be explored via the explore page.
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    # if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
    #     rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))
    page = request.args.get('page', 1, type=int)
    doctors = Physician.query.paginate(
        page, app.config['DOCTORS_PER_PAGE'], False)
    next_url = url_for('explore', page=doctors.next_num) \
        if doctors.has_next else None
    prev_url = url_for('explore', page=doctors.prev_num) \
        if doctors.has_prev else None
    return render_template('explore.html', title='Explore', doctors=doctors.items,
                           next_url=next_url, prev_url=prev_url)

# Login page.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated :
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = LoginForm()
    if form.validate_on_submit():
        cat = form.user_cat.data
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) or user.user_cat != cat:
            flash('Invalid credentials')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index'+"_" + current_user.user_cat)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# Logout page.
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('explore'))

# # Registration page for customer user.
# @app.route('/register', methods=['GET', 'POST'])
# def register(user_cat = "user"):
#     if current_user.is_authenticated:
#         return redirect(url_for('index'+"_" + current_user.user_cat))
#     form = RegistrationForm()
#     if form.validate_on_submit():

#         user = User(username=form.username.data, email=form.email.data,user_cat = user_cat)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)

# # Registration page for customer user.
# @app.route('/register', methods=['GET', 'POST'])
# def register(user_cat = "user"):
#     if current_user.is_authenticated:
#         return redirect(url_for('index'+"_" + current_user.user_cat))
#     form = RegistrationForm()
#     if form.validate_on_submit():

#         user = User(username=form.username.data, email=form.email.data,user_cat = user_cat)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)

# # Registration page for staff user.
# @app.route('/staff_register', methods=['GET', 'POST'])
# def staff_register(user_cat = "staff"):
#     if current_user.is_authenticated:
#         return redirect(url_for('index'+"_" + current_user.user_cat))
#     form = StaffRegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data,user_cat = user_cat)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered staff!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)

# Reset Password request page.
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

# Reset Password page.
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

# Personal profile for each user.
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    return render_template('user.html', user=user)

# # Personal page for each movie.
# @app.route('/movie/<id>', methods=['GET', 'POST'])
# def movie(id):
#     if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
#         if(current_user.is_authenticated):
#             rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))
#         else:
#             flash('Please login to rent a movie')
#     movie = Movie.query.filter_by(id=id).first_or_404()
#     page = request.args.get('page', 1, type=int)
#     movies = Movie.query.order_by(Movie.timestamp.desc()).paginate(
#         page, app.config['MOVIES_PER_PAGE'], False)
#     next_url = url_for('movie',id=Movie.query.order_by(Movie.id.data)[-1], page=movies.next_num) \
#         if movies.has_next else None
#     prev_url = url_for('movie',id=Movie.query.order_by(Movie.id.data)[0], page=movies.prev_num) \
#         if movies.has_prev else None
#     return render_template('movie.html', movie=movie, movies=movies.items,
#                            next_url=next_url, prev_url=prev_url)

# # Edit Profile page.
# @app.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title='Edit Profile',
#                            form=form)

# # Edit Movie page.
# @app.route('/edit_movie/<id>', methods=['GET', 'POST'])
# @login_required
# def edit_movie(id):
#     movie = Movie.query.filter_by(id=id).first_or_404()
#     if movie is None:
#         flash('Movie not found')
#         return redirect(url_for('explore'))
#     form = EditMovieForm(movie)
#     if form.validate_on_submit():
#         if form.name.data is not None:
#             movie.name = form.name.data
#         if form.img_path.data is not None:
#             movie.img_path = form.img_path.data
#         if form.description.data is not None:
#             movie.description = form.description.data
#         if form.genre.data is not None:
#             movie.genre = form.genre.data
#         if form.rating.data is not None:
#             movie.rating = form.rating.data
#         if form.price.data is not None:
#             movie.price = form.price.data
#         if form.quantity.data is not None:
#             movie.quantity = form.quantity.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('explore'))
#     elif request.method == 'GET':
#         form.name.data = movie.name
#         form.img_path.data = movie.img_path
#         form.description.data = movie.description
#         form.genre.data = movie.genre
#         form.rating.data = movie.rating
#         form.price.data = movie.price
#         form.quantity.data = movie.quantity
#     return render_template('add_movie.html', title='Edit Movie',
#                            form=form)

# # Add funds page.
# @app.route('/add_funds', methods=['GET', 'POST'])
# @login_required
# def add_funds():
#     form = AddFundsForm()
#     if form.validate_on_submit():
#         current_user.balance += form.balance.data
#         db.session.commit()
#         flash('Funds successfully added.')
#         return redirect(url_for('user',username=current_user.username))
#     elif request.method == 'GET':
#         form.balance.data = current_user.balance
#     return render_template('add_funds.html', title='Add Funds',
#                            form=form)

# # Add stock page.
# @app.route('/add_stock', methods=['GET', 'POST'])
# @login_required
# def add_stock():
#     form = AddStockForm()
#     if form.validate_on_submit():
#         movie = Movie.query.filter_by(id=form.id.data).first_or_404()
#         if movie is None:
#             flash('Movie not found')
#             return redirect(url_for('add_stock'))
#         movie.quantity += form.stock.data
#         db.session.commit()
#         flash('Stock successfully added.')
#         return redirect(url_for('movie',id=form.id.data))

#     return render_template('add_funds.html', title='Add Stock of Movie',
#                            form=form)

# Add user page.
@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = UserForm()
    if form.validate_on_submit():

        user = User(SSN =form.SSN.data,username=form.username.data, email=form.email.data, user_cat=form.user_cat.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Username or email already exists')
            return redirect(url_for('add_user'))
        flash('Congratulations, user has been added!')
        return redirect(url_for('add_user'))
    return render_template('add_data.html', title='Home', form=form)

# Add procedure page.
@app.route('/add_procedure', methods=['GET', 'POST'])
@login_required
def add_procedure():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddProcedureForm()
    if form.validate_on_submit():

        proc = Procedure_(Code=form.code.data, Name=form.name.data, Cost=form.cost.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Procedure already exists')
            return redirect(url_for('add_procedure'))
        flash('Congratulations, procedure has been added!')
        return redirect(url_for('add_procedure'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddDepartmentForm()
    if form.validate_on_submit():

        proc = Department(DepartmentID=form.departmentID.data, Name=form.name.data, Head=form.head.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding department')
            return redirect(url_for('add_department'))
        flash('Congratulations, deaprtment has been added!')
        return redirect(url_for('add_department'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_medication', methods=['GET', 'POST'])
@login_required
def add_medication():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddMedicationForm()
    if form.validate_on_submit():

        proc = Medication(Code = form.code.data, Name = form.name.data, Brand = form.brand.data, Description = form.description.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding medication')
            return redirect(url_for('add_medication'))
        flash('Congratulations, medication has been added!')
        return redirect(url_for('add_medication'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_affiliation', methods=['GET', 'POST'])
@login_required
def add_affiliation():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddAffiliationForm()
    if form.validate_on_submit():

        proc = Affiliated_with(Physician=form.physician.data, Department = form.department.data, PrimaryAffiliation = form.primaryAffiliation.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding affiliation')
            return redirect(url_for('add_affiliation'))
        flash('Congratulations, affiliation has been added!')
        return redirect(url_for('add_affiliation'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_training', methods=['GET', 'POST'])
@login_required
def add_training():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddTrainingForm()
    if form.validate_on_submit():

        proc = Trained_In(Physician=form.physician.data, Treatment = form.treatment.data, CertificationDate = form.certificationDate.data, CertificationExpires = form.certificationExpires.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding training')
            return redirect(url_for('add_training'))
        flash('Congratulations, training has been added!')
        return redirect(url_for('add_training'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_physician', methods=['GET', 'POST'])
@login_required
def add_physician():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddPhysicianForm()
    if form.validate_on_submit():

        proc = Physician(EmployeeID=form.employeeID.data, Name=form.name.data, Position=form.position.data, SSN = form.SSN.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding physician')
            return redirect(url_for('add_physician'))
        flash('Congratulations, physician has been added!')
        return redirect(url_for('add_procedure'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_room', methods=['GET', 'POST'])
@login_required
def add_room():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddRoomForm()
    if form.validate_on_submit():

        proc = Room(Number = form.number.data, Type = form.type.data, Unavailable = form.unavailable.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding room')
            return redirect(url_for('add_room'))
        flash('Congratulations, room has been added!')
        return redirect(url_for('add_room'))
    return render_template('add_data.html', title='Home', form=form)

@app.route('/add_nurse', methods=['GET', 'POST'])
@login_required
def add_nurse():
    if request.form.get('Back to Dashboard') == 'Dashboard':
        return redirect(url_for('index'+"_" + current_user.user_cat))
    form = AddNurseForm()
    if form.validate_on_submit():

        proc = Nurse(EmployeeID=form.employeeID.data, Name=form.name.data, Position=form.position.data, SSN = form.SSN.data,Registered = form.registered.data)
        try:
            db.session.add(proc)
            db.session.commit()
        except:
            db.session.rollback()
            flash('Error adding nurse')
            return redirect(url_for('add_nurse'))
        flash('Congratulations, nurse has been added!')
        return redirect(url_for('add_nurse'))
    return render_template('add_data.html', title='Home', form=form)

# # Add movie page.
# @app.route('/add_movie', methods=['GET', 'POST'])
# @login_required
# def add_movie():
#     if request.form.get('Back to Dashboard') == 'Dashboard':
#         return redirect(url_for('index'+"_" + current_user.user_cat))
#     form = MovieForm()
#     if form.validate_on_submit():
#         movie = Movie(name=form.name.data,description = form.description.data, genre = form.genre.data,rating=form.rating.data,price = form.price.data,quantity=form.quantity.data, img_path=form.img_path.data)
#         db.session.add(movie)
#         db.session.commit()
#         flash('The movie is now live on the store!')
#         return redirect(url_for('add_movie'))
#     return render_template('add_movie.html', title='Home', form=form)

# # Search page.
# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     if str(request.form.get('Rent Movie'))[:10] == 'Rent Movie':
#         if(current_user.is_authenticated):
#             rent_movie(current_user.id, int(str(request.form.get('Rent Movie'))[14:]))
#         else:
#             flash("Login to rent the movie.")
        
#     if not g.search_form.validate():
#         return redirect(url_for('explore'))
#     page = request.args.get('page', 1, type=int)
#     movies, total = Movie.search(g.search_form.q.data, page,
#                                app.config['MOVIES_PER_PAGE'])
#     next_url = url_for('search', q=g.search_form.q.data, page=page + 1) \
#         if total > page * app.config['MOVIES_PER_PAGE'] else None
#     prev_url = url_for('search', q=g.search_form.q.data, page=page - 1) \
#         if page > 1 else None
#     return render_template('search.html', title='Search', movies=movies,
#                            next_url=next_url, prev_url=prev_url)