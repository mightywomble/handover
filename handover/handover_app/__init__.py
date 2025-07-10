# handover_app/__init__.py
from dotenv import load_dotenv
# Load environment variables at the very top of the file.
load_dotenv() 

from flask import Flask, url_for
from flask_session import Session
import os
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # This middleware helps the app understand it's behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    project_root = os.path.dirname(app.root_path)

    # --- Configuration ---
    server_name = os.getenv("SERVER_NAME")
    # For development, comment out SERVER_NAME to avoid cookie issues
    # if not server_name:
    #     raise ValueError("FATAL ERROR: SERVER_NAME is not set in your .env file. Please set it to your public domain (e.g., SERVER_NAME='handover.safehomelan.com')")

    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
        SESSION_PERMANENT=False,
        SESSION_TYPE="filesystem",
        UPLOAD_FOLDER=os.path.join(project_root, 'uploads'),
        SUBMISSIONS_FOLDER=os.path.join(project_root, 'submissions'),
        GOOGLE_OAUTH_CLIENT_ID=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        GOOGLE_OAUTH_CLIENT_SECRET=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        # SERVER_NAME=server_name,  # <-- Comment this out for local/dev
        SESSION_COOKIE_DOMAIN=None,  # <-- Add this line
        SESSION_COOKIE_SECURE=True,  # Since you're using HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600  # 1 hour
    )
    
    # This is a standard setting for development to allow OAuth to work
    # correctly when the internal connection is HTTP but the external is HTTPS.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # Explicitly set the template_folder using the calculated project root.
    app.template_folder = os.path.join(project_root, 'templates')

    # Initialize extensions
    Session(app)
    # The login_manager will be initialized within the app context below.

    # Create necessary folders
    for folder in [app.config['UPLOAD_FOLDER'], app.config['SUBMISSIONS_FOLDER'], app.template_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Register blueprints and initialize extensions that need the app context
    with app.app_context():
        # Import auth before routes to resolve the circular dependency.
        from . import auth
        from . import routes
        
        # Initialize login_manager here, after the app is configured.
        auth.login_manager.init_app(app)
        
        # Manually construct the redirect_url with https and the server name from .env
        # auth.google_bp.redirect_url = f"https://{server_name}/login/google/authorized"
        
        app.register_blueprint(auth.google_bp, url_prefix="/login")
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(routes.bp)
        
        # Make current_user available in all templates
        @app.context_processor
        def inject_user():
            from flask_login import current_user
            return dict(current_user=current_user)

    return app
