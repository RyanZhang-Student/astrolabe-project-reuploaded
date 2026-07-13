import os
from flask import Blueprint, url_for, session, redirect, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv(override=True)
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    # Using Google Identity Services / OpenID Connect metadata
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID', '').strip(),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET', '').strip(),
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
        if not user:
            # Fallback to fetch user info directly
            resp = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
            resp.raise_for_status()
            user = resp.json()
            
        if user:
            # Convert to plain dictionary to guarantee JSON serialization in Flask Session
            plain_user = {
                'name': user.get('name', user.get('given_name', 'Astrolabe User')),
                'picture': user.get('picture', ''),
                'email': user.get('email', '')
            }
            session.clear() # Clear any corrupt session data
            session['user'] = plain_user
            session.modified = True
            
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
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        print(f"OAuth Authentication Error: {err_detail}", flush=True)
        return f"""
        <html>
            <head><title>Login Error</title></head>
            <body>
                <h3 style='color:red;'>Authentication Error</h3>
                <p>There was an error communicating with Google or verifying your login state.</p>
                <p><b>Error Details:</b> {e}</p>
                <pre style='background:#f4f4f4; padding:10px; overflow-x:auto;'>{err_detail}</pre>
                <p>Please take a screenshot of this error and show it to the assistant.</p>
                <button onclick='window.close()'>Close Window</button>
            </body>
        </html>
        """, 400

from flask import Blueprint, url_for, session, redirect, request, make_response

@auth_bp.route('/logout')
def logout():
    session.clear()
    session.modified = True
    response = make_response(redirect('/'))
    response.delete_cookie('session')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
