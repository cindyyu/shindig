from flask import Flask, request, url_for, redirect, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_oauth import OAuth
from app import app
from app import datastore
from app import db
from datastore import User
from facebook import GraphAPI

# Flask-Login Configuration

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid): 
  if userid is not None: 
  	user = User.query.get(userid)
  	if user: 
  		return user

# OAuth Configuration

oauth = OAuth()
 
facebook_oauth = oauth.remote_app('facebook',
  base_url='https://graph.facebook.com/',
  request_token_url=None,
  access_token_url='/oauth/access_token',
  authorize_url='https://www.facebook.com/dialog/oauth',
  consumer_key='941129455902199',
  consumer_secret='529258ac1fc1e7a38e17ae8d13d684ec',
  request_token_params={'scope': 'email, public_profile'}
)

@facebook_oauth.tokengetter
def get_facebook_oauth_token():
  return session.get('oauth_token')

@app.route('/login')
def facebook_login():
  next_url = request.args.get('next') or url_for('dashboard')
  return facebook_oauth.authorize(callback=url_for('facebook_authorized',
    next=next_url,
    _external=True))

@app.route('/login/authorized')
@facebook_oauth.authorized_handler
def facebook_authorized(resp):
  next_url = request.args.get('next') or url_for('dashboard')
  if resp is None:
    # The user likely denied the request
    flash(u'There was a problem logging in.')
    return redirect(next_url)
  session['oauth_token'] = (resp['access_token'], '')
  graph = facebook.GraphAPI(resp['access_token'])
  picture = graph.get_object("/me/picture")['url']
  friends = graph.get_object('me/friends')
  user_data = facebook_oauth.get('/me').data
  user = User.query.filter(User.email == user_data['email']).first()
  if user is None:
    new_user = User(user_id=user_data['id'], email=user_data['email'], first_name=user_data['first_name'], last_name=user_data['last_name'], picture=picture)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user)
  else:
    login_user(user)
  return redirect(next_url)

@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect('/')