from flask import Flask, request, url_for, redirect, session
from flask.ext.admin import Admin
from flask_login import LoginManager, login_user
from flask_oauth import OAuth
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

# User
class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, unique=True)
  first_name = db.Column(db.String)
  last_name = db.Column(db.String)

  def __init__(self, email, first_name=None, last_name=None):
    self.email = email.lower()
    self.first_name = first_name
    self.last_name = last_name

  # These four methods are for Flask-Login
  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.id)

db.create_all()


admin = Admin(app)
admin.add_view(ModelView(User, db.session))

# Flask-Login Configuration

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid): 
	user = User.query.get(int(userid))
	if user: 
		return user

# OAuth Configuration

oauth = OAuth()
 
facebook = oauth.remote_app('facebook',
  base_url='https://graph.facebook.com/',
  request_token_url=None,
  access_token_url='/oauth/access_token',
  authorize_url='https://www.facebook.com/dialog/oauth',
  consumer_key='941129455902199',
  consumer_secret='529258ac1fc1e7a38e17ae8d13d684ec',
  request_token_params={'scope': 'email'}
)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/login')
def facebook_login():
  next_url = request.args.get('next') or url_for('index')
  return facebook.authorize(callback=url_for('facebook_authorized',
      next=next_url,
      _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        # The user likely denied the request
        flash(u'There was a problem logging in.')
        return redirect(next_url)
    session['oauth_token'] = (resp['access_token'], '')
    user_data = facebook.get('/me').data
    user = User.query.filter(User.email == user_data['email']).first()
    if user is None:
        new_user = User(email=user_data['email'], first_name=user_data['first_name'], last_name=user_data['last_name'])
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
    else:
        login_user(user)
    return redirect(next_url)

from app import views