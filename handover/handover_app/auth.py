# handover_app/auth.py
from flask import Blueprint, redirect, url_for, current_app, flash, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from .models import User
import json
import os
from functools import wraps

# --- User Database Functions ---
USER_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.json')

def get_user_db():
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_db(db):
    with open(USER_DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)

# --- Flask-Login Setup ---
login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID from the JSON database."""
    try:
        db = get_user_db()
        if user_id in db:
            return User.from_json(db[user_id])
        return None
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None

# --- Custom Decorators ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Admin":
            flash("You do not have permission to access this page.", "warning")
            return redirect(url_for("handover.index"))
        return f(*args, **kwargs)
    return decorated_function

# --- Blueprint Setup ---
auth_bp = Blueprint('auth', __name__)

google_bp = make_google_blueprint(
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
)

@auth_bp.route("/login")
def login():
    # The redirect URL is now generated automatically by Flask-Dance.
    # We can still display it for debugging if needed.
    debug_info = {
        "SERVER_NAME_from_env": os.getenv("SERVER_NAME"),
        "Generated_Redirect_URL_for_GCP": url_for('google.authorized', _external=True)
    }
    return render_template("login.html", debug_info=debug_info)

# This function is no longer a route. It's a signal listener that fires
# after Flask-Dance completes the OAuth flow.
@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from Google."
        flash(msg, category="error")
        return False

    google_info = resp.json()
    print(f"Google userinfo response: {google_info}")  # Debug print
    
    # Map Google fields to your User model
    user_data = {
        'id': google_info['id'],
        'email': google_info['email'],
        'name': google_info.get('name') or google_info.get('given_name', '') + ' ' + google_info.get('family_name', ''),
        'picture': google_info.get('picture', ''),
        'role': 'user'  # Default role
    }
    
    # Check if user exists in database
    db = get_user_db()
    if google_info['id'] in db:
        # Update existing user
        db[google_info['id']].update(user_data)
        user = User.from_json(db[google_info['id']])
    else:
        # Create new user
        user = User.from_json(user_data)
        db[google_info['id']] = user_data
        save_user_db(db)
    
    login_user(user, remember=True)
    flash(f"Successfully signed in as {user.name}!", "success")
    return False  # Don't redirect automatically

# Optional: Add an error handler for better feedback
@oauth_error.connect_via(google_bp)
def google_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))

@google_bp.route("/authorized")
def google_authorized():
    # ...OAuth logic...
    if user:
        login_user(user, remember=True)  # Make sure this is called
        return redirect(url_for('routes.index'))
    # ...existing code...
