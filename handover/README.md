# Service Handover Application

A Flask-based web application for managing service handover documentation and approvals with Google OAuth authentication.

## Features

### Core Features
- **Google OAuth Authentication**: Secure login using Google SSO
- **Form Management**: Multiple handover form types (Base Install, Large Cluster, etc.)
- **File Uploads**: Support for documentation and evidence files
- **Approval Workflow**: Multi-section approval process with feedback
- **Status Tracking**: Track handover status (Pending, Approved, Requires Information)
- **Email Notifications**: Automated notifications for status changes
- **User Management**: Role-based access control

### Form Types
- Base Install handover
- Large Cluster handover
- Custom form templates

### Approval System
- Section-based approvals
- Feedback and comments
- "More Information Required" workflow
- Approval history tracking

## Prerequisites

- Python 3.8+
- Google OAuth 2.0 credentials
- HTTPS-enabled domain (for OAuth)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd handover
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip3 install flask
pip3 install flask-login
pip3 install flask-dance
pip3 install flask-session
pip3 install werkzeug
pip3 install python-dotenv
pip3 install gunicorn
```

### 4. Create Required Directories
```bash
mkdir -p uploads submissions data
```

## Google OAuth Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API and Google OAuth2 API

### 2. Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **Internal** (for organization use) or **External**
3. Fill in required information:
   - App name: "Service Handover"
   - User support email: your email
   - Developer contact: your email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users if using external type

### 3. Create OAuth Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Add authorized redirect URIs:
   ```
   https://your-domain.com/login/google/authorized
   ```
5. Save the **Client ID** and **Client Secret**

## Configuration

### 1. Environment Variables
Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:

```bash
# Flask Configuration
FLASK_SECRET_KEY=your-very-long-random-secret-key-here
FLASK_ENV=production

# Server Configuration
SERVER_NAME=your-domain.com

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
```

### 2. Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Directory Structure
Ensure these directories exist:
```
handover/
├── handover_app/
├── templates/
├── static/
├── uploads/          # File uploads
├── submissions/      # Form submissions
├── data/            # User database
└── .env
```

## Running the Application

### Development Mode
```bash
export FLASK_APP=handover_app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Production Mode
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "handover_app:create_app()"
```

### Using systemd (Production)
Create `/etc/systemd/system/handover.service`:

```ini
[Unit]
Description=Handover App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/handover
Environment="PATH=/path/to/handover/venv/bin"
ExecStart=/path/to/handover/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "handover_app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable handover
sudo systemctl start handover
```

## Nginx Configuration

Example Nginx configuration for HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    client_max_body_size 100M;  # For file uploads
}
```

## Usage

### First Time Setup
1. Access your application at `https://your-domain.com`
2. Click "Sign in with Google"
3. The first user will be created automatically
4. Edit `data/users.json` to set admin role:
   ```json
   {
     "user-id": {
       "id": "user-id",
       "email": "admin@your-domain.com",
       "name": "Admin User",
       "role": "admin"
     }
   }
   ```

### Creating Handover Forms
1. Navigate to the form type (Base Install, Large Cluster)
2. Fill in all required fields
3. Upload supporting documentation
4. Submit for approval

### Approval Process
1. Admin users can access submitted forms
2. Review each section and provide feedback
3. Mark sections as approved or requiring more information
4. Submit final approval decision

## File Structure

```
handover/
├── handover_app/
│   ├── __init__.py          # App factory
│   ├── auth.py              # Authentication logic
│   ├── models.py            # User model
│   ├── routes.py            # Main routes
│   └── templates/           # Jinja2 templates
├── static/                  # CSS, JS, images
├── uploads/                 # Uploaded files
├── submissions/             # Form submissions (JSON)
├── data/                    # User database (JSON)
└── README.md               # This file
```

## Troubleshooting

### Common Issues

**OAuth Redirect Mismatch**
- Ensure redirect URI in Google Console matches your domain
- Check HTTPS is properly configured

**Session Issues**
- Verify `FLASK_SECRET_KEY` is set and consistent
- Clear browser cookies after configuration changes

**File Upload Issues**
- Check directory permissions for `uploads/` folder
- Verify `client_max_body_size` in Nginx

**Database Issues**
- Ensure `data/` directory is writable
- Check JSON file formatting in `data/users.json`

### Debug Mode
Enable debug logging:
```python
# In __init__.py
app.config['DEBUG'] = True
```

### Log Files
Check application logs:
```bash
# Systemd service logs
sudo journalctl -u handover -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Security Considerations

- Always use HTTPS in production
- Keep OAuth credentials secure
- Regularly update dependencies
- Set proper file permissions
- Use strong secret keys
- Implement proper backup procedures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Create an issue in the repository
- Contact: [your-email@domain.com]