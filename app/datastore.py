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
  host_of = db.Column(db.String)
  events = db.Column(db.String)

  def __init__(self, email, first_name=None, last_name=None, user_id=None, host_of=None, events=None):
    self.email = email.lower()
    self.user_id = user_id
    self.first_name = first_name
    self.last_name = last_name
    self.host_of = host_of
    self.events = events

  # These four methods are for Flask-Login
  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.id)

db.create_all()