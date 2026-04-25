import os
from flask import Blueprint, url_for, session, redirect, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    # Using Google Identity Services / OpenID Connect metadata
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

@auth_bp.route('/login')
def login():
    redirect_uri = url_for('auth.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    try:
        token = oauth.google.authorize_access_token()
        user = token.get('userinfo')
        if user:
            session['user'] = user
    except Exception as e:
        print(f"OAuth Authentication Error: {e}")
    return redirect('/')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
