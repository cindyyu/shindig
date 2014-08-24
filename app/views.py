from flask import render_template, request, session
from flask_login import login_required, current_user
from app import app
from app import db
from app import forms
from forms import EventCreateForm
from app import datastore
from datastore import Events, User

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard(): 
	return render_template('dashboard.html')

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def events_create():
  form = EventCreateForm(request.form)
  if request.method == 'POST' and form.validate():
    new_event = Events(name=form.name.data, host=current_user, start_time=form.start.data, end_time=form.end.data)
    db.session.add(new_event)
    db.session.commit()
    return str(new_event.host.first_name)
  else :
    return render_template('events_create.html', form=form)