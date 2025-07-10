HPC Service Handover Application
This is a Python Flask web application designed to streamline the process of creating and approving HPC (High-Performance Computing) service handover documents. It provides a structured, multi-stage form for submitting service details and includes a complete approval workflow for the receiving team.

Features
Google SSO Login: Secure user authentication via Google accounts.

Role-Based Access Control (RBAC):

Users default to the "Engineer" role upon first login.

A local "Admin" user is configured to manage user roles.

A protected /settings page allows admins to view all users and promote other users to "Admin".

Multi-Stage & Single-Page Forms: Two distinct handover workflows ("Large Cluster" and "Base Install") are available after login.

Dynamic & Conditional Forms: The UI dynamically adapts based on user input, using dynamic tables and conditional fields.

Persistent Submissions: Each completed handover form is saved as a unique, persistent JSON file.

Approval Workflow:

Generates a unique link for each submission for the approval process.

Approvers can mark each section as "Approved" or "More Information Needed".

Simulates email notifications for new submissions and feedback requests.

Project Structure
/project-root
|-- handover_app/
|   |-- __init__.py
|   |-- auth.py             # Handles authentication, user loading, and SSO
|   |-- forms.py
|   |-- models.py           # Defines the User class
|   |-- routes.py
|   |-- utils.py
|   |-- templates/
|   |   |-- base.html
|   |   |-- login.html          # New login page
|   |   |-- settings.html       # New admin settings page
|   |   |-- ... (etc.)
|
|-- run.py
|-- users.json              # (Created automatically) Simple user database
|-- .env                    # You must create this for Google credentials
|-- ...

Installation & Setup
To run this application, you need Python and pip installed.

1. Install Dependencies
Install all required Python libraries from your terminal:

pip install Flask Flask-Session Flask-Login Flask-Dance Authlib python-dotenv

2. Set up Google OAuth Credentials
You must have Google OAuth 2.0 credentials to allow users to log in.

Go to the Google Cloud Console.

Create a new project or select an existing one.

Go to APIs & Services > Credentials.

Click Create Credentials > OAuth client ID.

Select Web application as the application type.

Under Authorized JavaScript origins, add http://127.0.0.1:5015 and http://0.0.0.0:5015.

Under Authorized redirect URIs, add http://127.0.0.1:5015/login/google/authorized and http://0.0.0.0:5015/login/google/authorized.

Click Create. Copy the Client ID and Client Secret.

3. Create the Environment File
In the root of your project, create a file named .env and add your Google credentials and a designated admin email to it, like this:

# .env file
FLASK_SECRET_KEY='a-very-secret-key-change-me'
GOOGLE_OAUTH_CLIENT_ID='YOUR_CLIENT_ID_HERE'
GOOGLE_OAUTH_CLIENT_SECRET='YOUR_CLIENT_SECRET_HERE'
ADMIN_EMAIL='your.admin.email@example.com'

Important: The ADMIN_EMAIL will be the first user granted Admin privileges. Make sure this is a Google account you can log in with.

Running the Application
Navigate to the project's root directory in your terminal.

Run the Flask application:

python run.py

Access the application:
Open your web browser and go to http://127.0.0.1:5015. You will be prompted to log in with Google.

Application Data & Reset
users.json: A simple file that acts as the user database, storing user IDs, emails, and roles.

submissions/: Stores all the completed handover reports.

uploads/: Stores all uploaded files.

flask_session/: Stores temporary session data.

To reset the application, delete the users.json file and the submissions, uploads, and flask_session folders.