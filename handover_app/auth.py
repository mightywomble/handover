# handover_app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User
from urllib.parse import urlencode

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
            flash('Invalid username or password.')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/login/google')
def google_login():
    """Redirect to Google's authorization page."""
    oauth = current_app.config['oauth']
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/authorize')
def google_authorize():
    """Callback route for Google SSO."""
    oauth = current_app.config['oauth']
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    
    # Find or create user
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            email=user_info['email'],
            username=user_info['email'], # Use email as username for simplicity
            is_sso_user=True
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('handover.index'))