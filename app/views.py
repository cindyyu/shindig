from flask import render_template, flash, redirect
from app import app
from app import db
from app import User
from app import facebook

@app.route('/')
@app.route('/index')
def index():
	return 'hi'