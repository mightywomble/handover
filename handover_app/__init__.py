# handover_app/__init__.py
from flask import Flask
from flask_session import Session
import os
from .models import db, User
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash

def create_app():
    """Create and configure an instance of the Flask application."""
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, 'templates')
    instance_dir = os.path.join(project_root, 'instance')

    app = Flask(__name__,
                instance_path=instance_dir,
                instance_relative_config=True,
                template_folder=template_dir)

    # --- Configuration ---
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this for production
        SESSION_PERMANENT=False,
        SESSION_TYPE="filesystem",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'app.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(project_root, 'uploads'),
        SUBMISSIONS_FOLDER=os.path.join(project_root, 'submissions'),
        # !!! REPLACE WITH YOUR GOOGLE OAUTH CREDENTIALS !!!
        # You can get these from the Google Cloud Console
        GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com",
        GOOGLE_CLIENT_SECRET="your-google-client-secret",
    )

    # Initialize extensions
    Session(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    oauth = OAuth(app)
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    app.config['oauth'] = oauth


    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Create necessary folders if they don't exist
    for folder in [app.config['UPLOAD_FOLDER'], app.config['SUBMISSIONS_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Create database tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@local.host')
            admin_user.set_password('admin')
            admin_user.generate_api_key()
            db.session.add(admin_user)
            db.session.commit()

        # Register Blueprints
        from . import routes
        app.register_blueprint(routes.bp)

        from . import api_routes
        app.register_blueprint(api_routes.api_bp)

        from . import auth
        app.register_blueprint(auth.auth_bp)

    return app