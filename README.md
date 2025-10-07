
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

---

## Standalone Single‑File Form (Offline)

In addition to the Flask web app, this repository can generate a single self‑contained HTML file that users can open directly in their browser (file://) with no install or server. It works offline and allows users to fill in the form and download a JSON file with their responses.

### What it does
- Produces one portable .html containing:
  - The UI (all HTML/CSS/JS inline)
  - The form definition (schema)
  - Optional prefill payload
- Users double‑click the .html, fill out the form, and click “Download Results” to save a JSON containing their answers (and any uploaded files embedded as base64).

### Generate a bundle (Base Install form)
Run the generator from the project root. These examples write the output into this folder.

```bash
python3 generate_bundle.py \
  --form base_install \
  --out handover_base_install.html \
  --message "Fill out the form and click Download Results to save a JSON file. This works offline." \
  --output-filename handover_base_install_result.json
```

Optionally add prefill values:

```bash
python3 generate_bundle.py \
  --form base_install \
  --prefill '{"customer_name":"Example Corp","submitter_email":"ops@example.com"}' \
  --out handover_base_install.html
```

Supported forms:
- `base_install`
- `onboard_customer`
- `onboard_supplier`
- `large_cluster` (merges all stages into a single page)

### Quick commands for other forms

Onboard Customer
```bash
python3 generate_bundle.py \
  --form onboard_customer \
  --out handover_onboard_customer.html \
  --output-filename onboard_customer_result.json
```

Onboard Supplier
```bash
python3 generate_bundle.py \
  --form onboard_supplier \
  --out handover_onboard_supplier.html \
  --output-filename onboard_supplier_result.json
```

Large Cluster (all stages in one page)
```bash
python3 generate_bundle.py \
  --form large_cluster \
  --out handover_large_cluster.html \
  --output-filename large_cluster_result.json
```

Notes:
- The generator applies some usability enhancements in the portable bundle:
  - Support Type uses checkboxes for “None”, “Basic Support”, and “Managed Services”. When “Managed Services” is selected, additional tier fields are shown (Managed Systems Administration: Gold/Silver/Bronze; Managed Slurm: None/Gold/Silver/Bronze).
  - Component Overview includes a per‑row “Component Type” dropdown (Node/Switch/Router/OOB Management). Depending on the selection, extra row fields appear (e.g., GPU Make/Model/Driver Version for Node; Make/Model for Switch/Router).
- The single‑file app works directly from file:// in Chrome/Edge/Firefox and Safari on desktop.

### Example output JSON
This is an abbreviated example of the downloaded JSON structure produced by the portable file.

```json
{
  "meta": {
    "generated_at": "2025-10-07T15:00:00.000Z",
    "version": 1
  },
  "payload": {
    "message": "Fill out the form and click Download Results to save a JSON file. This works offline.",
    "prefill": {
      "customer_name": "Example Corp",
      "submitter_email": "ops@example.com"
    },
    "draftKey": "handover_draft_base_install",
    "outputFilename": "handover_base_install_result.json"
  },
  "form_definition": { "title": "Base Install Handover", "sections": ["…"] },
  "answers": {
    "customer_name": "Example Corp",
    "submitter_email": "ops@example.com",
    "support_type": {
      "selection": ["Managed Services"]
    },
    "managed_systems_administration": "Gold",
    "managed_slurm": "None",
    "component_overview": [
      {
        "component_type": "Node",
        "hostname": "node-01",
        "ip_address": "10.0.0.10",
        "os_version": "Ubuntu 22.04",
        "last_patch_date": "2025-09-20",
        "gpu_make": "NVIDIA",
        "gpu_model": "H100",
        "driver_version": "535.54"
      },
      {
        "component_type": "Switch",
        "hostname": "sw-core-01",
        "ip_address": "10.0.0.2",
        "os_version": "",
        "last_patch_date": "",
        "make": "Arista",
        "model": "7050X3"
      }
    ],
    "public_ip_addresses": [
      {
        "description": "primary web",
        "ip_address": "203.0.113.10",
        "dns": "app.example.com",
        "dns_config_location": "Route53"
      }
    ]
  }
}
```

File uploads: If your schema includes file inputs, uploaded files are included in the JSON as objects with name/type/size and a base64 field. This keeps the result fully self‑contained for offline handover.
