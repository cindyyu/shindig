from flask import render_template, request, session, url_for, redirect
from flask_login import login_required, current_user
from app import app
from app import db
from app import forms
from forms import EventCreateForm, EventPreferenceForm, EventJoinForm
from app import datastore
from datastore import Event, User, attendance, Preference
from sqlalchemy import desc
from passlib.hash import sha256_crypt
from datetime import date
import calendar, json

def is_attendee_or_host(user, event):
  if user == event.host or user in event.attendees :
    return True
  else :
    return False

@app.route('/')
@app.route('/index')
def index():
  if current_user.is_anonymous() : 
    return 'plz login'
  else :
    return redirect('/dashboard')

# Dashboard: displays the events the user is either hosting or attending
@app.route('/dashboard')
@login_required
def dashboard(): 
  events_hosting = Event.query.order_by(desc(Event.start_time)).filter(Event.host.has(id=current_user.id)).all()
  events_attending = Event.query.order_by(desc(Event.start_time)).filter(Event.attendees.any(id=current_user.id)).all()
  return render_template('dashboard.html', events_hosting=events_hosting, events_attending=events_attending)

# View Event: displays basic information about an event to host and attendees only
@app.route('/events/view/<int:event_id>')
@login_required
def events_view(event_id):
  event = Event.query.get(event_id)
  # check if this person is an attendee or host
  if is_attendee_or_host(current_user, event) :
    attendees = ''
    for attendee in event.attendees : 
      attendees = attendees + attendee.full_name()
    return attendees
  else :
    return 'u dont belong'
  
# Create Event: allows user to create an event as a host
@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def events_create():
  form = EventCreateForm(request.form)
  # if form was submitted
  if request.method == 'POST' and form.validate():
    password = sha256_crypt.encrypt(form.password.data) if form.password.data else None
    new_event = Event(name=form.name.data, host=current_user, start_time=form.start.data, end_time=form.end.data, password=password)
    db.session.add(new_event)
    db.session.commit()
    return str(attendance)
  # if form was not submitted (get request)
  elif not form.validate():
    return str(form.errors)
  else :
    return render_template('events_create.html', form=form)

# Join Event: allows user to join an event *** TO ADD: PASSWORD TO JOIN ***
@app.route('/events/join/<int:event_id>', methods=['GET', 'POST'])
@login_required
def events_join(event_id):
  form = EventJoinForm(request.form)
  event = Event.query.filter(Event.id == event_id).first()
  # check if current user is already attendee or host
  # if not, add them
  if current_user not in event.attendees and current_user != event.host :
    if request.method == 'POST' and form.validate():
      if event.password :
        if sha256_crypt.verify(form.password.data, event.password) :
          event.attendees.append(current_user)
          db.session.commit()
          return 'you have joined!'
        else :
          return 'wrong pass yo'
      else :
        event.attendees.append(current_user)
        db.session.commit()
        return 'you have joined!'
    else : 
      return render_template('events_join.html', form=form, event_id=event_id)
  else :
    return redirect(url_for('events_view', event_id=event_id))

# Leave Event: allows user to leave an event
@app.route('/events/leave/<int:event_id>')
@login_required
def events_leave(event_id):
  event = Event.query.filter(Event.id == event_id).first()
  if current_user in event.attendees :
    event.attendees.remove(current_user)
    db.session.commit()
    return 'you have been removed!'
  else :
    return 'you not even in it yo'

# Event Preferences: allows user to add their preferences for a specific event
@app.route('/events/preferences/<int:event_id>', methods=['GET', 'POST'])
@login_required
def events_preferences(event_id):
  today = date.today()
  form = EventPreferenceForm(request.form)
  event = Event.query.get(event_id)

  # check if user is either a host or attendee
  if is_attendee_or_host(current_user, event) :
    # check if a permission already exists
    if Preference.query.filter(Preference.attendee.has(id=current_user.id) & Preference.event.has(id=event_id)).count() != 0 : 
      preference = Preference.query.filter(Preference.attendee.has(id=current_user.id) & Preference.event.has(id=event_id)).first()
      available_times = json.loads(preference.availability)
      return 'preference already created'
    else :
      # check to see if the form was submitted
      if request.method == 'POST' and form.validate():
        new_preference = Preference(attendee_id=current_user.id, event_id=event_id, availability=form.availability.data, willing_to_spend=int(form.willing_to_spend.data), location=form.location.data)
        db.session.add(new_preference)
        db.session.commit()
        return 'added!'
      else :
        return render_template('events_preference.html', form=form, event_id=event_id, today=today, calendar=calendar)
  else :
    return 'you dont have permission'

# Analyze Preferences
@app.route('/events/generate/<int:event_id>', methods=['GET', 'POST'])
@login_required
def events_generate(event_id):
  preferences = Preference.query.filter(Preference.event.has(id=event_id))
  possible_dates = {}
  possible_locations = []
  possible_willing_to_spend = []
  # Gather preferences and place them into lists/dictionaries we can parse through later
  for preference in preferences :
    # For each preference, load its available dates
    available_dates = json.loads(preference.availability)
    # Add available dates to a dictionary and record the number of people that date works for
    for available_date in available_dates : 
      if available_date['date'] in possible_dates :
        possible_dates[available_date['date']] += 1
      else :
        possible_dates[available_date['date']] = 1
    possible_willing_to_spend.append(preference.willing_to_spend)
    possible_locations.append(preference.location)
  # Get optimal meeting dates, willing_to_spend, location
  optimal_date = max(possible_dates, key=possible_dates.get)
  optimal_willing_to_spend = sum(possible_willing_to_spend)/len(possible_willing_to_spend)
  return str(optimal_willing_to_spend)