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
    return redirect(url_for('auth.login_success'))

@auth_bp.route('/login-success')
def login_success():
    return """
    <html>
        <head><title>Login Successful</title></head>
        <body>
            <script>
                if (window.opener) {
                    window.opener.location.reload();
                    window.close();
                } else {
                    window.location.href = '/';
                }
            </script>
            <p>Login successful! Closing window...</p>
        </body>
    </html>
    """

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
