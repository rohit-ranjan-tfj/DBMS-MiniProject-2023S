from keyring import set_password
from app import app, db
from werkzeug.security import generate_password_hash
from app.models import *

# Defining shell environment to allow for unittests and debugging.
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Affiliated_with': Affiliated_with, 'Trained_In': Trained_In, 'Procedure_': Procedure_,'Undergoes': Undergoes,'Department':Department, 'Patient': Patient,'Physician': Physician,'Prescribes':Prescribes, 'Room': Room, 'Stay': Stay, 'Appointment': Appointment, 'Medication': Medication, 'Block': Block, 'On_Call': On_Call, 'Nurse': Nurse}



