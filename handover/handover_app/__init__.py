# handover_app/__init__.py
from flask import Flask
from flask_session import Session
import os

def create_app():
    """Create and configure an instance of the Flask application."""
    
    # Calculate the absolute path for the project's root directory.
    # This is one level up from the directory containing this file (handover_app).
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define the absolute path to the templates folder.
    template_dir = os.path.join(project_root, 'templates')
    
    # Define the absolute path to the instance folder.
    instance_dir = os.path.join(project_root, 'instance')

    # Create the Flask app instance, providing explicit, absolute paths.
    # This is the most reliable way to ensure Flask finds the correct folders.
    app = Flask(__name__,
                instance_path=instance_dir,
                instance_relative_config=True,
                template_folder=template_dir)

    # --- Configuration ---
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this for production
        SESSION_PERMANENT=False,
        SESSION_TYPE="filesystem",
        # Set other folder paths relative to the calculated project root
        UPLOAD_FOLDER=os.path.join(project_root, 'uploads'),
        SUBMISSIONS_FOLDER=os.path.join(project_root, 'submissions')
    )

    # Initialize extensions
    Session(app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Create necessary folders if they don't exist, including the templates folder.
    folders_to_create = [
        app.config['UPLOAD_FOLDER'],
        app.config['SUBMISSIONS_FOLDER'],
        app.template_folder 
    ]
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Register routes
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app
