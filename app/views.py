import calendar, json, urllib2, os, foursquare, datetime
from flask import render_template, request, session, url_for, redirect
from flask_login import login_required, current_user
from app import app
from app import db
from app import forms, datastore, api
from api import foursquare
from forms import EventCreateForm, EventPreferenceForm, EventJoinForm
from datastore import Event, User, attendance, Preference
from sqlalchemy import desc
from passlib.hash import sha256_crypt
from datetime import date
from geopy.geocoders import Nominatim

geolocator = Nominatim()

def is_attendee_or_host(user, event):
  if user == event.host or user in event.attendees :
    return True
  else :
    return False

def is_host(user, event): 
  if user == event.host : 
    return True
  else : 
    return False

@app.route('/')
@app.route('/index')
def index():
  if current_user.is_anonymous() : 
    return render_template('homepage.html')
  else :
    return redirect('/dashboard')

@app.route('/about')
def about():
  return render_template('about.html')

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
  preferences = Preference.query.filter(Preference.event.has(id=event_id))
  num_preferences = preferences.count()
  # check if this person is an attendee or host
  user_is_host = is_host(current_user, event)
  if is_attendee_or_host(current_user, event) :
    return render_template('events_view.html', event=event, num_preferences=num_preferences, preferences=preferences, is_host=user_is_host, current_user=current_user)
  else :
    return render_template('events_view.html', error='you dunbelong')
  
# Create Event: allows user to create an event as a host
@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def events_create():
  form = EventCreateForm(request.form)
  # if form was submitted
  if request.method == 'POST' and form.validate():
    password = sha256_crypt.encrypt(form.password.data) if form.password.data else None
    new_event = Event(name=form.name.data, host=current_user, password=password)
    db.session.add(new_event)
    db.session.commit()
    return render_template('events_create.html', method='post')
  # if form was not submitted (get request)
  elif not form.validate():
    return render_template('events_create.html', method='post', error=form.errors)
  else :
    return render_template('events_create.html', form=form, method='get')

# Delete Event: allows host to delete an event
@app.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
def events_delete(event_id): 
  preferences = Preference.query.filter(Preference.event.has(id=event_id))
  event = Event.query.filter(Event.id == event_id).first()
  if current_user == event.host : 
    db.session.delete(event)
    for preference in preferences :
      db.session.delete(preference)
    db.session.commit()
  return redirect(url_for('dashboard'))

# Join Event: allows user to join an event *** TO ADD: PASSWORD TO JOIN ***
@app.route('/events/join/<int:event_id>', methods=['GET', 'POST'])
@login_required
def events_join(event_id):
  form = EventJoinForm(request.form)
  event = Event.query.filter(Event.id == event_id).first()
  # check if current user is already attendee or host
  # if not, add them
  if current_user not in event.attendees and current_user != event.host :
    if request.method == 'POST' and form.validate() :
      if event.password :
        if sha256_crypt.verify(form.password.data, event.password) :
          event.attendees.append(current_user)
          db.session.commit()
          return render_template('events_join.html', event=event, response='you have joined!')
        else :
          return render_template('events_join.html', response='wrong pass yo!')
      else :
        event.attendees.append(current_user)
        db.session.commit()
        return render_template('events_join.html', event=event, response='you have joined!')
    else : 
      return render_template('events_join.html', form=form, event=event, event_id=event_id, method='get')
  else :
    return redirect(url_for('events_view', event_id=event_id))

# Leave Event: allows user to leave an event
@app.route('/events/leave/<int:event_id>')
@login_required
def events_leave(event_id):
  preference = Preference.query.filter(Preference.event.has(id=event_id)).filter(Preference.attendee.has(id=current_user.id)).first()
  event = Event.query.filter(Event.id == event_id).first()
  if current_user in event.attendees :
    event.attendees.remove(current_user)
    db.session.delete(preference)
    db.session.commit()
    return render_template('events_leave.html', response='you have been removed!')
  else :
    return render_template('events_leave.html', response='you not even in it yo')

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
      return render_template('events_preferences.html', response='preference already created')
    else :
      # check to see if the form was submitted
      if request.method == 'POST' and form.validate():
        new_preference = Preference(attendee_id=current_user.id, event_id=event_id, availability=form.availability.data, willing_to_spend=int(form.willing_to_spend.data), location=form.location.data)
        db.session.add(new_preference)
        db.session.commit()
        return render_template('events_preferences.html', response='preference added')
      else :
        return render_template('events_preferences.html', form=form, event_id=event_id, today=today, calendar=calendar)
  else :
    return render_template('events_preferences.html', error='you dont have permission')

# Decide on location and time 
@app.route('/events/decide/<int:event_id>', methods=['POST'])
@login_required
def events_decide(event_id):
  location_name = request.form.get('location_name')
  location_address = request.form.get('location_address')
  date = request.form.get('date')
  start_time = request.form.get('start_time')
  end_time = request.form.get('end_time')
  preferences = Preference.query.filter(Preference.event.has(id=event_id))
  event = Event.query.filter(Event.id == event_id).first()
  if current_user == event.host : 
    if location_name and location_address : 
      event.location_name = location_name
      event.location_address = location_address
    if date and start_time and end_time :
      event.date = datetime.datetime.strptime(date, "%m-%d-%Y").date()
      event.start_time = datetime.datetime.strptime(start_time, '%H:%M:%S').time()
      event.end_time = datetime.datetime.strptime(end_time, '%H:%M:%S').time()
    db.session.commit()
  return redirect(url_for('dashboard'))

# Analyze Preferences
@app.route('/events/generate/<int:event_id>', methods=['GET', 'POST'])
@login_required
def events_generate(event_id):
  event = Event.query.get(event_id)
  preferences = Preference.query.filter(Preference.event.has(id=event_id))
  if preferences.count() > 1:
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
          possible_dates[available_date['date']]['attendance'] += 1
          if available_date['start_time'] > possible_dates[available_date['date']]['start_time'] :
            possible_dates[available_date['date']]['start_time'] = available_date['start_time']
          if available_date['end_time'] < possible_dates[available_date['date']]['end_time'] :
            possible_dates[available_date['date']]['end_time'] = available_date['end_time']
        else :
          possible_dates[available_date['date']] = {}
          possible_dates[available_date['date']]['attendance'] = 1
          possible_dates[available_date['date']]['start_time'] = available_date['start_time']
          possible_dates[available_date['date']]['end_time'] = available_date['end_time']
      # Get rid of buggy possible dates, like start times after end times
      true_possible_dates = {}
      for possible_date in possible_dates :
        if possible_dates[possible_date]['start_time'] < possible_dates[possible_date]['end_time'] :
          true_possible_dates[possible_date] = possible_dates[possible_date]

      possible_dates = true_possible_dates
      possible_willing_to_spend.append(preference.willing_to_spend)
      possible_locations.append(preference.location)

    # Get optimal date, first one
    # optimal_date = possible_dates.keys()[0];
    # optimal_date_object = possible_dates[optimal_date]
    # optimal_start_time = optimal_date_object['start_time']
    # optimal_end_time = optimal_date_object['end_time']

    # Get optimal willing_to_spend: averages how much everyone is willing to spend
    optimal_willing_to_spend = sum(possible_willing_to_spend)/len(possible_willing_to_spend)
    
    # Get optimal location: average latitude and longitude, return its address
    possible_locations_lat = []
    possible_locations_lng = []
    for possible_location in possible_locations : 
      location = geolocator.geocode(possible_location, timeout=20)
      possible_locations_lat.append(location.latitude)
      possible_locations_lng.append(location.longitude)
    optimal_location_latlng = str(sum(possible_locations_lat)/len(possible_locations_lat)) + ', ' + str(sum(possible_locations_lng)/len(possible_locations_lng))
    optimal_location_full = geolocator.reverse(optimal_location_latlng, timeout=25).raw['address']
    if 'postcode' in optimal_location_full.keys() : 
      optimal_location = optimal_location_full['postcode']
    elif 'city' in optimal_location_full.keys() : 
      optimal_location = optimal_location_full['city']
    else : 
      optimal_location = optimal_location_full['county']

    possible_venues = foursquare.venues.explore(params={'query': '', 'near': optimal_location, 'limit': '5', 'sortByDistance': '1', 'time': 'any', 'price': optimal_willing_to_spend})['groups'][0]['items']
    return render_template('events_generate.html', possible_venues=possible_venues, possible_times=possible_dates, event=event)
  else : 
    return 'no preferences submitted'