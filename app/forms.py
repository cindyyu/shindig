from flask import session
from wtforms import Form, StringField, DateTimeField, RadioField, validators

class EventCreateForm(Form):
  name = StringField('Name')
  password = StringField('Password')

class EventJoinForm(Form):
  password = StringField('Password')
  
class EventPreferenceForm(Form):
  start = DateTimeField('Start Time')
  end = DateTimeField('End Time')
  location = StringField('Location')
  availability = StringField('Availability')
  willing_to_spend = RadioField('Willing To Spend', choices=[('1', '$'),('2', '$$'),('3', '$$$'),('4', '$$$$')], coerce=unicode)