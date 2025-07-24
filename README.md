
# Service Team Portal

## Overview

The Service Team Portal is a comprehensive web application designed to streamline and formalize various operational processes for a service team. It provides a centralized platform for service handovers, onboarding new customers and suppliers, and managing user access through a secure, unified interface.

The application features a robust forms engine for capturing detailed information, an approval workflow for service handovers, and a secure REST API for programmatic integration. User management is handled through both local authentication for service accounts and Google SSO for team members.

## Key Features

-   **Multiple Form Workflows**:
    
    -   **Service Handovers**: Detailed, multi-stage forms for complex "Large Cluster" projects and a streamlined single-page form for "Base Installs".
        
    -   **Onboarding**: Dedicated forms for onboarding new customers and suppliers, capturing all necessary details.
        
-   **User & Access Management**:
    
    -   Secure login system with local password authentication and Google SSO.
        
    -   Admin settings panel to manage users (create/delete local users).
        
    -   Per-user API key generation for secure access to the API.
        
-   **REST API**:
    
    -   Secure endpoints for programmatically onboarding customers and suppliers.
        
    -   Requires Bearer Token authentication using user-specific API keys.
        
    -   Includes an in-app documentation page with `curl` examples.
        
-   **Dynamic Configuration**:
    
    -   Application settings (like the public hostname and Google SSO credentials) are managed directly from the UI, with no need for `.env` files or manual configuration file edits.
        
-   **Reverse Proxy Support**:
    
    -   Built to run correctly behind a reverse proxy (like HAProxy or Nginx), ensuring proper URL generation for SSO and other external links.
        

## Prerequisites

-   Python 3.8 or newer
    
-   `pip3` (Python package installer)
    

## Installation and Setup

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

First, clone the project files to your local machine.

```
git clone <your-repository-url>
cd <repository-folder>

```

### 2. Create and Activate a Virtual Environment

It is highly recommended to run the application in a Python virtual environment.

```
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

```

### 3. Install Required Packages

Install all the necessary Python libraries with a single command:

```
pip3 install Flask Flask-Session Flask-SQLAlchemy Flask-Login Authlib Werkzeug

```

### 4. Run the Application

Once the packages are installed, you can run the application for the first time.

```
python3 run.py

```

The first time you run the app, it will automatically:

1.  Create an `instance` folder in your project directory.
    
2.  Inside `instance/`, it will create the SQLite database file (`app.db`).
    
3.  Populate the database with the necessary tables.
    
4.  Create a default `admin` user with the password `admin`.
    
5.  Create the default application settings in the database.
    

The application will be running at `http://127.0.0.1:5015`.

## Configuration

After running the application for the first time, you need to perform some initial configuration through the web interface.

1.  **Log In**: Open your web browser and navigate to `http://127.0.0.1:5015`. You will be redirected to the login page. Log in with:
    
    -   **Username**: `admin`
        
    -   **Password**: `admin`
        
2.  **Navigate to Settings**: In the top-right corner, click on the user menu (`admin`) and select **Settings**.
    
3.  **Configure Hostname & Google SSO**:
    
    -   **Application Hostname (Base URL)**: Change this to the public URL where your application will be accessed (e.g., `https://handover.yourcompany.com`). This is crucial for Google SSO to work correctly.
        
    -   **Google** Client **ID / Secret**: Paste the credentials you obtained from the Google Cloud Console.
        
    -   **Enable Login Debug**: If you are having trouble with SSO, tick this box. It will display the exact redirect URL the app is generating on the login page, which you can compare with the URL in your Google Cloud Console.
        
    -   Click **Save Settings**.
        

## API Usage

The API is protected and requires an API key for access.

1.  **Get** an **API Key**: Go to the **Settings** page. You can use the API key for the `admin` user or create a new "Service User" to get a dedicated key.
    
2.  **Make a Request**: Include the API key in the `Authorization` header as a Bearer Token.
    
    ```
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <YOUR_API_KEY>" \
      -d '{ "company_name": "API Test", "account_manager": "Test", "salesforce_reference": "SF-API-123" }' \
      [https://handover.yourcompany.com/api/onboard/customer](https://handover.yourcompany.com/api/onboard/customer)
    
    ```
    

For more details and example payloads, visit the **API** page from the link in the application's header.
