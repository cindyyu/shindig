from flask import session
from wtforms import Form, StringField, DateTimeField

class EventCreateForm(Form):
  name = StringField('Name')
  start = DateTimeField('Start Time')
  end = DateTimeField('End Time')
  