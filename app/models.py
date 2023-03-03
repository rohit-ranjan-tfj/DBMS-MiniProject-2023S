# All SQLAlchemy Database classes are defined here.
from datetime import datetime, timedelta
from hashlib import md5
from re import S
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.search import add_to_index, remove_from_index, query_index
import jwt
from app import app, db, login
from fpdf import FPDF
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import bindparam
from sqlalchemy import Interval

# A Mixin Class is implemented to handle the search functionality and its changes on the databases.
# The search functionality is implemented in the search.py file.
class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

# db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
# db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

# The User Database.
# The UserMixin class handles the authentication and its changes on the databases.
# The same database stores all the stakeholders of the HMS differentiated by user_cat column
class User(UserMixin, db.Model):
    user_cat = db.Column(db.String(64), index=True)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def getName(self):
        return self.username
    
    def getCategory(self):
        return self.user_cat
    
    def setName(self, name):
        self.username = name
    
    def getEmail(self):
        return self.email


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Affiliated_with(db.Model):
    __tablename__ = 'Affiliated_with'
    Physician = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'), primary_key=True)
    Department = db.Column(db.Integer, db.ForeignKey('Department.DepartmentID'), primary_key=True)
    PrimaryAffiliation = db.Column(db.Boolean, nullable=False)

class Trained_In(db.Model):
    __tablename__ = 'Trained_In'
    Physician = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'), primary_key=True)
    Treatment = db.Column(db.Integer, db.ForeignKey('Procedure_.Code'), primary_key=True)
    CertificationDate = db.Column(db.DateTime, nullable=False)
    CertificationExpires = db.Column(db.DateTime, nullable=False)

class Procedure_(db.Model):
    __tablename__ = 'Procedure_'
    Code = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(40), nullable=False)
    Cost = db.Column(db.Float, nullable=False)

class Undergoes(db.Model):
    __tablename__ = 'Undergoes'
    Patient = db.Column(db.Integer, db.ForeignKey('Patient.SSN'), primary_key=True)
    Procedure_ = db.Column(db.Integer, db.ForeignKey('Procedure_.Code'), primary_key=True)
    Stay = db.Column(db.Integer, db.ForeignKey('Stay.StayID'), primary_key=True)
    Date = db.Column(db.DateTime, primary_key=True)
    Physician = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'))
    AssistingNurse = db.Column(db.Integer, db.ForeignKey('Nurse.EmployeeID'))

class Department(db.Model):
    __tablename__ = 'Department'
    DepartmentID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(40), nullable=False)
    Head = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'), nullable=False)

class Physician(db.Model):
    __tablename__ = 'Physician'
    EmployeeID = db.Column(db.Integer, primary_key=True)
    img_path = db.Column(db.String(140))
    Name = db.Column(db.String(40), nullable=False)
    Position = db.Column(db.String(40), nullable=False)
    SSN = db.Column(db.Integer, nullable=False)

class Patient(db.Model):
    __tablename__ = 'Patient'
    SSN = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(40), nullable=False)
    Address = db.Column(db.String(40), nullable=False)
    Phone = db.Column(db.String(40), nullable=False)
    PCP = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'), nullable=False)
    InsuranceID = db.Column(db.String(40), nullable=False)

class Prescribes(db.Model):
    __tablename__ = 'Prescribes'
    Physician = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'), primary_key=True)
    Patient = db.Column(db.Integer, db.ForeignKey('Patient.SSN'), primary_key=True)
    Medication = db.Column(db.Integer, db.ForeignKey('Medication.Code'), primary_key=True)
    Date = db.Column(db.DateTime,primary_key=True, nullable=False)
    Appointment = db.Column(db.Integer, db.ForeignKey('Appointment.AppointmentID'))
    Dose = db.Column(db.Integer, nullable=False)
    
class Room(db.Model):
    __tablename__ = 'Room'
    Number = db.Column(db.Integer, primary_key=True)
    # BlockFloor = db.Column(db.Integer, db.ForeignKey('Block.Floor'), nullable=False)
    # BlockCode = db.Column(db.Integer, db.ForeignKey('Block.Code'), nullable=False)
    Type = db.Column(db.String(40), nullable=False)
    Unavailable = db.Column(db.Boolean, nullable=False)

class Stay(db.Model):
    __tablename__ = 'Stay'
    StayID = db.Column(db.Integer, primary_key=True)
    Patient = db.Column(db.Integer, db.ForeignKey('Patient.SSN'), nullable=False)
    Room = db.Column(db.Integer, db.ForeignKey('Room.Number'), nullable=False)
    Start = db.Column(db.DateTime, nullable=False)
    End = db.Column(db.DateTime, nullable=False)

class Appointment(db.Model):
    __tablename__ = 'Appointment'
    AppointmentID = db.Column(db.Integer, primary_key=True)
    Patient = db.Column(db.Integer, db.ForeignKey('Patient.SSN'), nullable=False)
    PrepNurse = db.Column(db.Integer, db.ForeignKey('Nurse.EmployeeID'), nullable=False)
    Physician = db.Column(db.Integer, db.ForeignKey('Physician.EmployeeID'), nullable=False)
    Start = db.Column(db.DateTime, nullable=False)
    End = db.Column(db.DateTime, nullable=False)

class Medication(db.Model):
    __tablename__ = 'Medication'
    Code = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(40), nullable=False)
    Brand = db.Column(db.String(40), nullable=False)
    Description = db.Column(db.String(40), nullable=False)

class Block(db.Model):
    __tablename__ = 'Block'
    Floor = db.Column(db.Integer,primary_key=True)
    Code = db.Column(db.Integer, primary_key=True)

class On_Call(db.Model):
    __tablename__ = 'On_Call'
    Nurse = db.Column(db.Integer, db.ForeignKey('Nurse.EmployeeID'), primary_key=True)
    # BlockCode = db.Column(db.Integer, db.ForeignKey('Block.Code'), primary_key=True)
    # BlockFloor = db.Column(db.Integer, db.ForeignKey('Block.Floor'), primary_key=True)
    Start = db.Column(db.DateTime, primary_key=True, nullable=False)
    End = db.Column(db.DateTime, primary_key=True, nullable=False)


class Nurse(db.Model):
    __tablename__ = 'Nurse'
    EmployeeID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(40), nullable=False)
    Position = db.Column(db.String(40), nullable=False)
    SSN = db.Column(db.Integer, nullable=False)
    Registered = db.Column(db.Boolean, nullable=False)

# # Movies database.
# class Movie(SearchableMixin, db.Model):
#     __searchable__ = ['name', 'genre', 'rating', 'price', 'description']
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40))
#     img_path = db.Column(db.String(140))
#     description = db.Column(db.String(140))
#     genre = db.Column(db.String(40))
#     rating = db.Column(db.Float)
#     price = db.Column(db.Float)
#     quantity = db.Column(db.Integer)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

#     def __repr__(self):
#         return '<Movie {} {} {} {} {}>'.format(self.id, self.name, self.genre, self.rating, self.price)

#     def getName(self):
#         return self.name

#     def getDescription(self):
#         return self.description
    
#     def getPrice(self):
#         return self.price

#     def getID(self):
#         return self.id

# # Orders database.
# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     deadline = db.Column(db.DateTime, index=True, default=(datetime.utcnow() + timedelta(days=30)))
#     returned = db.Column(db.DateTime, default=None)
#     status = db.Column(db.String(40))
#     price = db.Column(db.Float)
#     quantity = db.Column(db.Integer)
    
#     def __repr__(self):
#         return '<Order {} {} {} {}>'.format(self.id, self.user_id, self.movie_id, self.timestamp)

#     def getID(self):
#         return self.id

#     def getUserID(self):
#         return self.user_id

#     def getMovieID(self):
#         return self.movie_id

#     def getTimestamp(self):
#         return self.timestamp
    
#     def getDeadline(self):
#         return self.deadline

#     def getReturned(self):
#         return self.returned
    
#     def getStatus(self):
#         return self.status
    
#     def getPrice(self):
#         return self.price

    
            
        
