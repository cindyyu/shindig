from flask import session
from wtforms import Form, StringField, DateTimeField

class EventCreateForm(Form):
  name = StringField('Name')
  start = DateTimeField('Start Time')
  password = StringField('Password')
  end = DateTimeField('End Time')

class EventJoinForm(Form):
  password = StringField('Password')
  
class EventPreferenceForm(Form):
  start = DateTimeField('Start Time')
  end = DateTimeField('End Time')
  location = StringField('Location')