from flask import session
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin
from app import app
from app import db
from app import datastore
from datastore import User, Event, attendance, Preference

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Preference, db.session))