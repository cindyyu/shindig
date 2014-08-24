from flask import render_template, request, session, url_for, redirect
from flask_login import login_required, current_user
from app import app
from app import db
from app import forms
from forms import EventCreateForm, EventPreferenceForm
from app import datastore
from datastore import Event, User, attendance, Preference
from sqlalchemy import desc

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
    new_event = Event(name=form.name.data, host=current_user, start_time=form.start.data, end_time=form.end.data)
    db.session.add(new_event)
    db.session.commit()
    return str(attendance)
  # if form was not submitted (get request)
  else :
    return render_template('events_create.html', form=form)

# Join Event: allows user to join an event *** TO ADD: PASSWORD TO JOIN ***
@app.route('/events/join/<int:event_id>')
@login_required
def events_join(event_id):
  event = Event.query.filter(Event.id == event_id).first()
  # check if current user is already attendee or host
  # if not, add them
  if current_user not in event.attendees and current_user != event.host :
    event.attendees.append(current_user)
    db.session.commit()
    return 'you have joined!'
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
  form = EventPreferenceForm(request.form)
  event = Event.query.get(event_id)
  if is_attendee_or_host(current_user, event) :
    # if form was submitted
    if request.method == 'POST' and form.validate():
      # check if preference already exists
      if Preference.attendee == current_user : 
        return 'already!'
      else :
        new_preference = Preference(attendee_id=current_user.id, event_id=event_id, start_time=form.start.data)
        db.session.add(new_preference)
        db.session.commit()
        return 'added!'
    else :
      return render_template('events_preference.html', form=form, event_id=event_id)
  else :
    return 'u dont even go here'