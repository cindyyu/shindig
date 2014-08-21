from flask import render_template
from flask_login import login_required
from app import app
from app import db

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard(): 
	return render_template('dashboard.html')