# handover_app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('handover.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and not user.is_sso_user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('handover.index'))
        else:
            flash('Invalid username or password.', 'error')

    # Conditionally pass the redirect URI for debugging
    debug_redirect_uri = None
    if current_app.config.get('ENABLE_LOGIN_DEBUG') == 'true':
        debug_redirect_uri = url_for('auth.google_authorize', _external=True)

    return render_template('login.html', debug_redirect_uri=debug_redirect_uri)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/login/google')
def google_login():
    """Redirect to Google's authorization page."""
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        flash('Google SSO is not configured by the administrator.', 'error')
        return redirect(url_for('auth.login'))

    oauth = current_app.config['oauth']
    
    # Generate and store a nonce
    nonce = os.urandom(16).hex()
    session['oauth_nonce'] = nonce

    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)

@auth_bp.route('/login/google/authorize')
def google_authorize():
    """Callback route for Google SSO."""
    oauth = current_app.config['oauth']
    try:
        token = oauth.google.authorize_access_token()
        
        # Retrieve and use the nonce for validation
        nonce = session.pop('oauth_nonce', None)
        user_info = oauth.google.parse_id_token(token, nonce=nonce)
        
        email = user_info.get('email')
        if not email:
            flash('Google login failed: Email not provided.', 'error')
            return redirect(url_for('auth.login'))

        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                username=user_info.get('name', email.split('@')[0]),
                is_sso_user=True
            )
            db.session.add(user)
            db.session.commit()
            flash('New user account created via Google SSO.', 'success')

        login_user(user)
        return redirect(url_for('handover.index'))
    except Exception as e:
        flash(f'An error occurred during Google login: {str(e)}', 'error')
        return redirect(url_for('auth.login'))
