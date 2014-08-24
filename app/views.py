from flask import render_template, request, session, url_for, redirect
from flask_login import login_required, current_user
from app import app
from app import db
from app import forms
from forms import EventCreateForm
from app import datastore
from datastore import Event, User, preferences

@app.route('/')
@app.route('/index')
def index():
  if current_user.is_anonymous() : 
    return 'plz login'
  else :
    events = Event.query.filter(Event.attendees.any(id=current_user.id)).all()
    return render_template('index.html', events=events)

@app.route('/dashboard')
@login_required
def dashboard(): 
  events = Event.query.filter(Event.host.has(id=current_user.id)).all()
  events_string = ''
  for event in events :
    events_string = events_string + event.name
  return render_template('dashboard.html', events_string=events_string)

@app.route('/events/view/<int:event_id>')
@login_required
def events_view(event_id):
  event = Event.query.get(event_id)
  # check if this person is an attendee or host
  if current_user == event.host or current_user in event.attendees :
    return 'is_host or attendee'
  else :
    return 'not host'
  

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def events_create():
  form = EventCreateForm(request.form)
  if request.method == 'POST' and form.validate():
    new_event = Event(name=form.name.data, host=current_user, start_time=form.start.data, end_time=form.end.data)
    db.session.add(new_event)
    db.session.commit()
    return str(preferences)
  else :
    return render_template('events_create.html', form=form)

@app.route('/events/join/<int:event_id>')
@login_required
def events_join(event_id):
  event = Event.query.filter(Event.id == event_id).first()
  if current_user not in event.attendees and current_user != event.host :
    event.attendees.append(current_user)
    db.session.commit()
    return 'you have joined!'
  else :
    return redirect(url_for('events_view', event_id=event_id))

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