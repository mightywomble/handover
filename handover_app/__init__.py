# handover_app/__init__.py
from flask import Flask
from flask_session import Session
import os
from .models import db, User, Setting
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """Create and configure an instance of the Flask application."""
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, 'templates')
    instance_dir = os.path.join(project_root, 'instance')

    app = Flask(__name__,
                instance_path=instance_dir,
                instance_relative_config=True,
                template_folder=template_dir)

    # Add ProxyFix middleware to handle reverse proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # --- Configuration ---
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'a-very-secure-dev-key'),
        SESSION_PERMANENT=False,
        SESSION_TYPE="filesystem",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'app.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(project_root, 'uploads'),
        SUBMISSIONS_FOLDER=os.path.join(project_root, 'submissions'),
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
    
    # Create database tables and default admin/settings
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@local.host')
            admin_user.set_password('admin')
            admin_user.generate_api_key()
            db.session.add(admin_user)
            db.session.commit()

        # Create default settings if they don't exist
        default_settings = {
            'APP_HOSTNAME': 'http://localhost:5015',
            'GOOGLE_CLIENT_ID': '',
            'GOOGLE_CLIENT_SECRET': '',
            'ENABLE_LOGIN_DEBUG': 'false',
            'SYSAID_URL': '',
            'SYSAID_USERNAME': '',
            'SYSAID_PASSWORD': ''
        }
        for key, value in default_settings.items():
            if not Setting.query.filter_by(key=key).first():
                db.session.add(Setting(key=key, value=value))
        db.session.commit()
            
        # Load settings from DB into app config
        for setting in Setting.query.all():
            app.config[setting.key] = setting.value

        # Now that config is loaded, register OAuth
        oauth.register(
            name='google',
            client_id=app.config.get('GOOGLE_CLIENT_ID'),
            client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        app.config['oauth'] = oauth

        # Register Blueprints
        from . import routes
        app.register_blueprint(routes.bp)

        from . import api_routes
        app.register_blueprint(api_routes.api_bp)

        from . import auth
        app.register_blueprint(auth.auth_bp)

    return app
