from app import app
from app import db

@app.route('/')
@app.route('/index')
def index():
	return 'hi'