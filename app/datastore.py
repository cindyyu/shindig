from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin.contrib.sqla import ModelView
from app import app
from app import db

# User
class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.String, unique=True)
  email = db.Column(db.String, unique=True)
  first_name = db.Column(db.String)
  last_name = db.Column(db.String)
  host_of = db.relationship('Events', backref='host', lazy='dynamic')
  picture = db.Column(db.String)

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

# Events
class Events(db.Model):
  __tablename__ = 'events'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  start_time = db.Column(db.DateTime)
  end_time = db.Column(db.DateTime)
  location = db.Column(db.String)
  user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

# class Attendees(db.Model):
#   __tablename__ = 'attendees'
#   id = db.Column(db.Integer, primary_key=True)
#   event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
#   attendee_id = db.Column(db.Integer, db.ForeignKey('attendee.id'))

db.create_all()