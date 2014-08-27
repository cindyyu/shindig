from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin.contrib.sqla import ModelView
from app import app
from app import db

# Attendance
attendance = db.Table('attendance',
  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
  db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
)

# User
class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.String, unique=True)
  email = db.Column(db.String, unique=True)
  first_name = db.Column(db.String)
  last_name = db.Column(db.String)
  picture = db.Column(db.String)
  host_of = db.relationship('Event', backref='host', lazy='dynamic')
  preferences = db.relationship('Preference', backref='attendee', lazy='dynamic')

  def __init__(self, email, first_name=None, last_name=None, user_id=None, picture=None):
    self.email = email.lower()
    self.user_id = user_id
    self.first_name = first_name
    self.last_name = last_name
    self.picture = picture

  # These four methods are for Flask-Login
  def is_authenticated(self):
    return True
  def is_active(self):
    return True
  def is_anonymous(self):
    return False
  def get_id(self):
    return unicode(self.id)

  def full_name(self):
    return self.first_name + ' ' + self.last_name

# Event
class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  start_time = db.Column(db.DateTime)
  end_time = db.Column(db.DateTime)
  location = db.Column(db.String)
  password = db.Column(db.String)
  categories = db.Column(db.PickleType)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
  attendees = db.relationship(
    'User', 
    secondary=attendance,
    backref=db.backref('events', lazy='dynamic')
  )
  preferences = db.relationship('Preference', backref='event', lazy='dynamic')

  def __init__(self, name, host, start_time=None, end_time=None, location=None, password=None, categories=None): 
    self.name = name
    self.host = host
    self.start_time = start_time
    self.end_time = end_time
    self.location = location
    self.password = password
    self.categories = categories

  def url_view(self):
    return '/events/view/' + str(self.id)

# Preferences
class Preference(db.Model):
  __tablename__ = 'preference'
  id = db.Column(db.Integer, primary_key=True)
  attendee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
  availability = db.Column(db.PickleType)
  willing_to_spend = db.Column(db.Integer)
  location = db.Column(db.String)
  attending = db.Column(db.Boolean)

db.create_all()