# app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
SUBMISSIONS_FOLDER = 'submissions'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SUBMISSIONS_FOLDER'] = SUBMISSIONS_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'super-secret-key-for-real' # Necessary for flashing messages
Session(app)

# --- Form and Stage Definitions ---

# Defines the order of the stages
stage_order = ["stage1", "stage2", "stage3", "stage4", "stage5", "stage6"]

# Defines the content of each stage
form_sections = {
    "stage1": {
        "title": "Service Introduction & Overview",
        "fields": [
            {"name": "service_name", "label": "Service/System Name", "type": "text", "placeholder": "e.g., New Web Server Cluster"},
            {"name": "submitter_email", "label": "Your Email Address", "type": "text", "placeholder": "e.g., your.name@example.com (for approval notifications)"},
            {"name": "service_reference", "label": "Service Reference", "type": "text", "placeholder": "e.g., SVC-WEBCL"},
            {"name": "version", "label": "Version", "type": "text", "placeholder": "e.g., 1.0"},
            {"name": "date_prepared", "label": "Date Prepared", "type": "date"},
            {"name": "prepared_by", "label": "Prepared By (Infrastructure Team)", "type": "text", "placeholder": "e.g., Platform Engineering"},
            {"name": "handover_to", "label": "Handover To (Operational Team)", "type": "text", "placeholder": "e.g., IT Operations Team, L2 Support"},
            {"name": "project_reference", "label": "Project Reference", "type": "text", "placeholder": "e.g., PRJ-2025-04-WEBCL"},
            {"name": "purpose", "label": "Purpose", "type": "textarea", "placeholder": "This document provides the necessary information for the..."},
            {"name": "brief_description", "label": "Brief Description", "type": "textarea", "placeholder": "A short description of what the service/system does."},
            {"name": "business_criticality", "label": "Business Criticality", "type": "select", "options": ["", "High (Tier 1)", "Medium (Tier 2)", "Low (Tier 3)"]},
            {"name": "service_hours_sla", "label": "Service Hours / SLA", "type": "text", "placeholder": "e.g., 24x7, Business Hours 9-5 Mon-Fri"},
            {"name": "support_type", "label": "Support Type", "type": "select", "options": ["", "Basic", "Core Support", "Managed Service", "Other"]},
            {"name": "key_users_departments", "label": "Key Users / Departments", "type": "textarea", "placeholder": "List main user groups or departments"},
        ]
    },
    "stage2": {
        "title": "Infrastructure Details",
        "fields": [
            {"name": "component_overview", "label": "Component Overview", "type": "dynamic_table", "columns": ["Component Type", "Hostname / Identifier", "IP Address", "OS Version", "Last Patch Date"], "options": {"Component Type": ["Server", "Network", "Storage", "Rack", "Cable", "Other"]}, "placeholders": {"Hostname / Identifier": "e.g., web-prod-01", "IP Address": "e.g., 10.1.1.10"}},
            {"name": "vlan_details", "label": "VLAN Details", "type": "dynamic_table", "columns": ["VLAN ID", "Description"], "placeholders": {"VLAN ID": "e.g., 101", "Description": "e.g., Production Web VLAN"}},
            {"name": "subnet_details", "label": "Subnets", "type": "dynamic_table", "columns": ["Item", "Description"], "placeholders": {"Item": "e.g., 10.1.1.0/24", "Description": "e.g., Web Tier Subnet"}},
            {"name": "gateway_details", "label": "Gateways", "type": "dynamic_table", "columns": ["Item", "Description"], "placeholders": {"Item": "e.g., 10.1.1.1", "Description": "e.g., Web Tier Gateway"}},
            {"name": "firewall_rule_details", "label": "Firewall Rule References", "type": "dynamic_table", "columns": ["Item", "Description"], "placeholders": {"Item": "e.g., FWR-00123", "Description": "e.g., Allow HTTPS from LB to Web"}},
            {"name": "hardware_model_details", "label": "Hardware Models", "type": "dynamic_table", "columns": ["Item", "Description"], "placeholders": {"Item": "e.g., Dell R750", "Description": "e.g., Production Web Servers"}},
            {"name": "warranty_details", "label": "Warranty Information", "type": "dynamic_table", "columns": ["Item(s)", "Warranty Type", "Warranty Expires", "Warranty With", "Contact Details"], "placeholders": {"Item(s)": "e.g., All Dell R750s", "Warranty Type": "e.g., ProSupport Plus", "Warranty Expires": "e.g., 2028-05-10", "Warranty With": "e.g., Dell"}},
        ]
    },
    "stage3": {
        "title": "CMDB, Configuration & Credentials",
        "fields": [
            {"name": "cmdb_primary_cis", "label": "Primary CI(s)", "type": "textarea", "placeholder": "List primary Configuration Item names/IDs from CMDB..."},
            {"name": "netbox_link", "label": "Netbox Link", "type": "text", "placeholder": "e.g., https://netbox.example.com/dcim/devices/1/"},
            {"name": "cmdb_data_verified_by", "label": "CMDB Data Verified By", "type": "text", "placeholder": "e.g., John Smith on 2025-07-10"},
            {"name": "build_method", "label": "Build Method", "type": "multiselect", "options": ["Manual", "Ansible", "Terraform", "Other"]},
            {"name": "build_config_links", "label": "Link to Build Config", "type": "dynamic_table", "columns": ["Item", "Github Link"], "placeholders": {"Item": "e.g., Web Server Playbook", "Github Link": "e.g., https://github.com/user/repo/playbook.yml"}},
            {"name": "soe_adherence", "label": "SOE Adherence", "type": "conditional_select", "options": ["Yes", "No"], "conditions": {"Yes": [{"name": "presales_doc_upload", "label": "Presales Approved Document", "type": "file"}, {"name": "build_doc_upload", "label": "Build Document", "type": "file"}]}},
            {"name": "key_config_files", "label": "Key Configuration File Paths", "type": "dynamic_table", "columns": ["Item", "Path", "Description"], "placeholders": {"Item": "e.g., Apache Config", "Path": "e.g., /etc/httpd/httpd.conf", "Description": "e.g., Main web server configuration"}},
            {"name": "credentials_management", "label": "Credentials & Secrets Management", "type": "dynamic_table", "columns": ["Location", "Search For / Link"], "options": {"Location": ["1Password", "HashiCorp Vault", "CyberArk", "Other"]}, "placeholders": {"Search For / Link": "e.g., 'PROD Web Server Root' or path/to/secret"}},
        ]
    },
    "stage4": {
        "title": "Operational Procedures",
        "fields": [
            {"name": "service_procedures", "label": "Service Procedures", "type": "dynamic_table", "columns": ["Service Name", "Start Command", "Stop Command", "Restart Command", "Check Status Command", "Test Procedure", "Notes"], "placeholders": {"Service Name": "e.g., httpd", "Start Command": "e.g., systemctl start httpd", "Stop Command": "e.g., systemctl stop httpd", "Restart Command": "e.g., systemctl restart httpd", "Check Status Command": "e.g., systemctl status httpd", "Test Procedure": "e.g., curl localhost"}},
        ]
    },
    "stage5": {
        "title": "Monitoring, Troubleshooting & Contacts",
        "fields": [
            {"name": "monitoring_tool", "label": "Monitoring Tool", "type": "conditional_select", "options": ["None", "Prometheus/Grafana", "Zabbix", "OpsRamp", "Other"], "conditions": {"Other": [{"name": "monitoring_tool_other", "label": "Specify Other Tool", "type": "text"}]}},
            {"name": "key_log_files", "label": "Key Log File Locations & Rotation", "type": "dynamic_table", "columns": ["Service Name", "Log File Location", "Rotation Time in Days"], "placeholders": {"Service Name": "e.g., Apache Access Logs", "Log File Location": "e.g., /var/log/httpd/access_log", "Rotation Time in Days": "e.g., 14"}},
            {"name": "common_issues", "label": "Common Issues & Resolutions", "type": "textarea", "placeholder": "Issue: [e.g., Website Slow] -> Steps: [e.g., Check top on servers...]"},
            {"name": "diagnostic_tools", "label": "Key Diagnostic Tools/Commands", "type": "textarea", "placeholder": "e.g., top, vmstat, netstat, curl, openssl s_client, tail"},
            {"name": "escalation_paths", "label": "Escalation Paths", "type": "textarea", "placeholder": "L1: Service Desk\nL2: IT Operations\nL3 (Infra): ...\nL3 (App): ..."},
            {"name": "support_contacts", "label": "Support Contacts", "type": "textarea", "placeholder": "Infra SME: [Name, Email]\nApp Lead: [Name, Email]\nVendor Support: [Vendor, Contract #, Contact]"},
        ]
    },
    "stage6": {
        "title": "Security, URLs, Diagrams & Final Checks",
        "fields": [
            {"name": "firewall_summary", "label": "Key Firewall Rules Summary", "type": "textarea", "placeholder": "e.g., Allow TCP 443 from ANY. Ref: [Firewall Request ID]"},
            {"name": "firewall_config_link", "label": "Link to Firewall Config", "type": "text", "placeholder": "e.g., https://firewall.example.com/policies/pol123"},
            {"name": "user_account_method", "label": "Method of Adding User Accounts", "type": "conditional_select", "options": ["None", "Manual", "Ansible", "Other"], "conditions": {"Ansible": [{"name": "ansible_code_link", "label": "Link to Ansible Code", "type": "text"}], "Other": [{"name": "user_account_other_method", "label": "Describe Other Method", "type": "textarea"}]}},
            {"name": "ssl_cert_info", "label": "SSL Certificate Information", "type": "dynamic_table", "columns": ["Certificate Type", "Certificate Location", "Expiry Date"], "placeholders": {"Certificate Type": "e.g., Public Wildcard", "Certificate Location": "e.g., /etc/pki/tls/certs/public.crt", "Expiry Date": "e.g., 2026-01-01"}},
            {"name": "related_urls", "label": "Related URLs", "type": "textarea", "placeholder": "Application URL: ...\nGit Repo: ...\nProject Docs: ..."},
            {"name": "network_diagram", "label": "Network Diagram", "type": "file"},
            {"name": "architecture_diagram", "label": "System Architecture Diagram", "type": "file"},
            {"name": "data_flow_diagram", "label": "Data Flow Diagram", "type": "file"},
            {"name": "known_issues", "label": "Known Issues / Limitations", "type": "textarea", "placeholder": "List any known defects, performance limitations, or temporary workarounds..."},
            {"name": "verification_checklist", "label": "Handover Verification Checklist", "type": "dynamic_table", "columns": ["Item", "Date Given", "Meeting/Session Link", "By Whom"], "predefined_rows": ["Knowledge Transfer", "Default Passwords Changed", "Service Team Access Confirmed", "Monitoring Alerts Tested"], "placeholders": {"Date Given": "e.g., 2025-07-10", "Meeting/Session Link": "e.g., https://teams.link/...", "By Whom": "e.g., John Smith"}},
        ]
    }
}

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_dynamic_table(field_name, columns):
    """Helper to process dynamic table data from the form."""
    table_data = []
    first_col_key = f"{field_name}_{columns[0].lower().replace(' / ', '_').replace(' ', '_').replace('(', '').replace(')', '')}[]"
    if first_col_key in request.form:
        num_rows = len(request.form.getlist(first_col_key))
        for i in range(num_rows):
            row = {}
            is_row_empty = True
            for col_name in columns:
                input_name = f"{field_name}_{col_name.lower().replace(' / ', '_').replace(' ', '_').replace('(', '').replace(')', '')}[]"
                values = request.form.getlist(input_name)
                value = values[i] if i < len(values) else ""
                row[col_name] = value
                if value:
                    is_row_empty = False
            if not is_row_empty:
                table_data.append(row)
    return table_data

# --- Routes ---
@app.route('/')
def index():
    """Initializes session and redirects to the first stage."""
    session.clear()
    session['form_data'] = {}
    return redirect(url_for('stage', stage_name=stage_order[0]))

@app.route('/stage/<stage_name>', methods=['GET', 'POST'])
def stage(stage_name):
    """Renders a form stage and handles its submission."""
    if stage_name not in stage_order:
        return "Stage not found", 404

    if request.method == 'POST':
        if stage_name not in session['form_data']:
            session['form_data'][stage_name] = {}

        for field in form_sections[stage_name]["fields"]:
            field_name = field['name']
            if field['type'] == 'dynamic_table':
                session['form_data'][stage_name][field_name] = process_dynamic_table(field_name, field['columns'])
            elif field['type'] == 'file':
                if field_name in request.files:
                    file = request.files[field_name]
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(f"{field_name}_{file.filename}")
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        session['form_data'][stage_name][field_name] = filename
            elif field['type'] == 'multiselect':
                 session['form_data'][stage_name][field_name] = request.form.getlist(field_name)
            elif field['type'] == 'conditional_select':
                session['form_data'][stage_name][field_name] = {}
                selection = request.form.get(field_name)
                session['form_data'][stage_name][field_name]['selection'] = selection
                if selection in field.get('conditions', {}):
                    for sub_field in field['conditions'][selection]:
                        sub_field_name = sub_field['name']
                        if sub_field['type'] == 'file':
                             if sub_field_name in request.files:
                                file = request.files[sub_field_name]
                                if file and file.filename and allowed_file(file.filename):
                                    filename = secure_filename(f"{sub_field_name}_{file.filename}")
                                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                    session['form_data'][stage_name][field_name][sub_field_name] = filename
                        else:
                            session['form_data'][stage_name][field_name][sub_field_name] = request.form.get(sub_field_name)
            else:
                session['form_data'][stage_name][field_name] = request.form.get(field_name)
        
        session.modified = True
        action = request.form.get('action', 'continue')
        current_index = stage_order.index(stage_name)

        if action == 'review':
             return redirect(url_for('review'))
        elif action == 'back' and current_index > 0:
            previous_stage_name = stage_order[current_index - 1]
            return redirect(url_for('stage', stage_name=previous_stage_name))
        elif current_index + 1 < len(stage_order):
            next_stage_name = stage_order[current_index + 1]
            return redirect(url_for('stage', stage_name=next_stage_name))
        else:
            return redirect(url_for('review'))

    current_index = stage_order.index(stage_name)
    form_data = session.get('form_data', {}).get(stage_name, {})
    
    return render_template('index.html', 
                           stage_name=stage_name,
                           stage_data=form_sections[stage_name],
                           form_data=form_data,
                           stage_order=stage_order,
                           current_stage_index=current_index,
                           form_sections=form_sections)

@app.route('/review')
def review():
    """Displays all collected data for final review before submission."""
    if 'form_data' not in session or not session['form_data']:
        flash("No data to review. Please start from the beginning.", "warning")
        return redirect(url_for('index'))
        
    return render_template('review.html',
                           form_data=session.get('form_data', {}),
                           form_sections=form_sections,
                           stage_order=stage_order)

@app.route('/submit_report', methods=['POST'])
def submit_report():
    """Saves the report to a file and redirects to a success page with the approval link."""
    if 'form_data' not in session:
        return redirect(url_for('index'))

    handover_id = str(uuid.uuid4())
    submission_data = {
        "id": handover_id,
        "status": "PENDING_APPROVAL",
        "submitted_at": datetime.utcnow().isoformat(),
        "form_data": session['form_data'],
        "approvals": {}
    }
    
    filepath = os.path.join(app.config['SUBMISSIONS_FOLDER'], f"{handover_id}.json")
    with open(filepath, 'w') as f:
        json.dump(submission_data, f, indent=4)
    
    session.clear()
    return redirect(url_for('submission_success', handover_id=handover_id))

@app.route('/submission_success/<handover_id>')
def submission_success(handover_id):
    """Shows a success message with the unique link for the approval process."""
    approval_link = url_for('approve', handover_id=handover_id, _external=True)
    print(f"--- SIMULATED EMAIL ---")
    print(f"To: itsm@cudoventures.com")
    print(f"From: service.review@cudoventures.com")
    print(f"Subject: New Service Handover for Approval")
    print(f"Please review and approve the following service handover: {approval_link}")
    print(f"-----------------------")
    return render_template('submission_success.html', approval_link=approval_link)

@app.route('/approve/<handover_id>', methods=['GET'])
def approve(handover_id):
    """The approval page for the service team."""
    filepath = os.path.join(app.config['SUBMISSIONS_FOLDER'], f"{handover_id}.json")
    if not os.path.exists(filepath):
        return "Submission not found", 404
        
    with open(filepath, 'r') as f:
        submission_data = json.load(f)
        
    return render_template('approval.html',
                           submission=submission_data,
                           form_sections=form_sections,
                           stage_order=stage_order)

@app.route('/process_approval/<handover_id>', methods=['POST'])
def process_approval(handover_id):
    """Processes the submitted approval form."""
    filepath = os.path.join(app.config['SUBMISSIONS_FOLDER'], f"{handover_id}.json")
    if not os.path.exists(filepath):
        return "Submission not found", 404

    with open(filepath, 'r') as f:
        submission_data = json.load(f)

    approvals = {}
    requires_more_info = False
    for stage_key in stage_order:
        approval_status = request.form.get(f'approval_{stage_key}')
        notes = request.form.get(f'notes_{stage_key}', '')
        if approval_status == 'More Information Needed' and not notes:
            flash(f"Please provide notes for '{form_sections[stage_key]['title']}' when requesting more information.", "warning")
            return redirect(url_for('approve', handover_id=handover_id))

        approvals[stage_key] = {'status': approval_status, 'notes': notes}
        if approval_status == 'More Information Needed':
            requires_more_info = True

    submission_data['approvals'] = approvals
    submission_data['last_updated_at'] = datetime.utcnow().isoformat()
    submitter_email = submission_data.get('form_data', {}).get('stage1', {}).get('submitter_email', '[Submitter Email Not Found]')

    if requires_more_info:
        submission_data['status'] = 'REQUIRES_INFORMATION'
        flash("The report has been marked as 'More Information Needed' and feedback has been saved. The original submitter will be notified.", "warning")
        print(f"--- SIMULATED EMAIL (MORE INFO) ---")
        print(f"To: {submitter_email}")
        print(f"From: itsm@cudoventures.com")
        print(f"Subject: More Information Required for Service Handover")
        print(f"Please review the feedback and update the service handover document: {url_for('approve', handover_id=handover_id, _external=True)}")
        print(f"------------------------------------")
    else:
        submission_data['status'] = 'APPROVED'
        flash("The handover report has been successfully approved!", "success")
        print(f"--- SIMULATED EMAIL (APPROVED) ---")
        print(f"To: {submitter_email}, itsm@cudoventures.com")
        print(f"From: service.review@cudoventures.com")
        print(f"Subject: Service Handover Approved")
        print(f"The service handover has been approved: {url_for('approve', handover_id=handover_id, _external=True)}")
        print(f"---------------------------------")

    with open(filepath, 'w') as f:
        json.dump(submission_data, f, indent=4)

    return redirect(url_for('approve', handover_id=handover_id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Main Execution ---
if __name__ == '__main__':
    for folder in [UPLOAD_FOLDER, SUBMISSIONS_FOLDER, 'templates']:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # --- HTML Templates ---
    
    # templates/base.html
    base_html = """
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}HPC Service Handover{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .container { max-width: 1024px; }
        .form-input, .form-select, .form-textarea, .table-input, .table-select {
            background-color: #1F2937; /* bg-gray-800 */
            border-color: #4B5563; /* border-gray-600 */
            color: #D1D5DB; /* text-gray-300 */
        }
        .form-input:focus, .form-select:focus, .form-textarea:focus, .table-input:focus, .table-select:focus {
            --tw-ring-color: #4f46e5; /* ring-indigo-500 */
            border-color: #4f46e5; /* border-indigo-500 */
        }
        .form-select, .table-select {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 0.5rem center;
            background-repeat: no-repeat;
            background-size: 1.5em 1.5em;
            padding-right: 2.5rem;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .table-select option, .form-select option {
            background-color: #1F2937;
            color: #D1D5DB;
        }
        [x-cloak] { display: none !important; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body class="bg-gray-900 text-gray-300">
    <div class="container mx-auto p-4 sm:p-6 lg:p-8">
        {% block content %}{% endblock %}
        <footer class="text-center text-sm text-gray-500 mt-8 py-4 border-t border-gray-800">
            <p>&copy; 2025 Cudo Ventures. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
"""
    with open('templates/base.html', 'w') as f:
        f.write(base_html)

    # templates/index.html
    index_html = """
{% extends "base.html" %}

{% block title %}HPC Service Handover - {{ stage_data.title }}{% endblock %}

{% block content %}
<header class="mb-10">
    <h1 class="text-3xl font-bold text-white">HPC Service Handover</h1>
    <p class="text-gray-400 mt-1">A staged process to ensure smooth service transition.</p>
</header>

<!-- Stepper -->
<nav aria-label="Progress" class="mb-10 hidden sm:block">
  <ol role="list" class="space-y-4 md:flex md:space-x-8 md:space-y-0">
    {% for stage in stage_order %}
    <li class="md:flex-1">
      {% if loop.index0 < current_stage_index %}
      <a href="{{ url_for('stage', stage_name=stage) }}" class="group flex flex-col border-l-4 border-indigo-600 py-2 pl-4 hover:border-indigo-800 md:border-l-0 md:border-t-4 md:pl-0 md:pt-4 md:pb-0">
        <span class="text-sm font-medium text-indigo-400 group-hover:text-indigo-300">{{ "Step %d"|format(loop.index) }}</span>
        <span class="text-sm font-medium text-gray-400">{{ form_sections[stage].title }}</span>
      </a>
      {% elif loop.index0 == current_stage_index %}
      <a href="#" class="flex flex-col border-l-4 border-indigo-600 py-2 pl-4 md:border-l-0 md:border-t-4 md:pl-0 md:pt-4 md:pb-0" aria-current="step">
        <span class="text-sm font-medium text-indigo-400">{{"Step %d"|format(loop.index)}}</span>
        <span class="text-sm font-medium text-white">{{ form_sections[stage].title }}</span>
      </a>
      {% else %}
      <a href="#" class="group flex flex-col border-l-4 border-gray-700 py-2 pl-4 hover:border-gray-500 md:border-l-0 md:border-t-4 md:pl-0 md:pt-4 md:pb-0">
        <span class="text-sm font-medium text-gray-500 group-hover:text-gray-400">{{"Step %d"|format(loop.index)}}</span>
        <span class="text-sm font-medium text-gray-500">{{ form_sections[stage].title }}</span>
      </a>
      {% endif %}
    </li>
    {% endfor %}
  </ol>
</nav>

<main>
    <div class="bg-gray-800/50 border border-gray-700 p-8 rounded-lg shadow-lg">
        <h2 class="text-2xl font-semibold text-white mb-6 border-b border-gray-700 pb-4">{{ stage_data.title }}</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="rounded-md {{ 'bg-red-900/20' if category == 'warning' else 'bg-green-900/20' }} p-4 mb-4 border {{ 'border-red-500/30' if category == 'warning' else 'border-green-500/30' }}">
                <p class="text-sm {{ 'text-red-300' if category == 'warning' else 'text-green-300' }}">{{ message }}</p>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        {% include 'form_template.html' %}
    </div>
</main>
{% endblock %}
"""
    with open('templates/index.html', 'w') as f:
        f.write(index_html)

    # templates/form_template.html
    form_template_html = """
<form action="{{ url_for('stage', stage_name=stage_name) }}" method="post" enctype="multipart/form-data">
    <div class="space-y-8">
        {% for field in stage_data.fields %}
            <div x-data='{{ '{"selection": "' ~ (form_data.get(field.name, {}).get('selection', '') or field.options[0]) ~ '"}' if field.type == 'conditional_select' else '{}' }}'>
                <label for="{{ field.name }}" class="block text-sm font-bold text-gray-300 mb-2">{{ field.label }}</label>
                
                {% if field.type in ['text', 'date'] %}
                    <input type="{{ field.type }}" id="{{ field.name }}" name="{{ field.name }}" class="form-input mt-1 block w-full rounded-md shadow-sm sm:text-sm" placeholder="{{ field.placeholder or '' }}" value="{{ form_data.get(field.name, '') }}">
                
                {% elif field.type == 'textarea' %}
                    <textarea id="{{ field.name }}" name="{{ field.name }}" rows="4" class="form-textarea mt-1 block w-full rounded-md shadow-sm sm:text-sm" placeholder="{{ field.placeholder or '' }}">{{ form_data.get(field.name, '') }}</textarea>
                
                {% elif field.type == 'select' %}
                    <select id="{{ field.name }}" name="{{ field.name }}" class="form-select mt-1 block w-full rounded-md shadow-sm sm:text-sm">
                        {% for option in field.options %}
                            <option class="bg-gray-800 text-gray-300" {% if form_data.get(field.name) == option %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>

                {% elif field.type == 'multiselect' %}
                    <select id="{{ field.name }}" name="{{ field.name }}" multiple class="form-input mt-1 block w-full rounded-md shadow-sm sm:text-sm" style="height: 100px;">
                        {% for option in field.options %}
                            <option class="bg-gray-800 text-gray-300" value="{{ option }}" {% if option in form_data.get(field.name, []) %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>
                    <p class="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple.</p>

                {% elif field.type == 'file' %}
                    <input type="file" id="{{ field.name }}" name="{{ field.name }}" class="mt-1 block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-500/10 file:text-indigo-300 hover:file:bg-indigo-500/20">
                    {% if form_data.get(field.name) %}
                        <p class="text-sm text-gray-400 mt-2">Current file: <a href="{{ url_for('uploaded_file', filename=form_data.get(field.name)) }}" class="text-indigo-400" target="_blank">{{ form_data.get(field.name) }}</a></p>
                    {% endif %}

                {% elif field.type == 'conditional_select' %}
                    <select id="{{ field.name }}" name="{{ field.name }}" x-model="selection" class="form-select mt-1 block w-full rounded-md shadow-sm sm:text-sm">
                        {% for option in field.options %}
                            <option class="bg-gray-800 text-gray-300" value="{{ option }}">{{ option }}</option>
                        {% endfor %}
                    </select>
                    <div class="mt-4 space-y-4 border-l-2 border-gray-700 pl-4">
                    {% for condition, sub_fields in field.conditions.items() %}
                        <div x-show="selection === '{{ condition }}'" x-cloak>
                        {% for sub_field in sub_fields %}
                            <label class="block text-sm font-medium text-gray-400">{{ sub_field.label }}</label>
                            {% if sub_field.type == 'file' %}
                                <input type="file" name="{{ sub_field.name }}" class="mt-1 block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-500/10 file:text-indigo-300 hover:file:bg-indigo-500/20">
                                {% set sub_field_value = form_data.get(field.name, {}).get(sub_field.name) %}
                                {% if sub_field_value %}
                                   <p class="text-sm text-gray-400 mt-2">Current file: <a href="{{ url_for('uploaded_file', filename=sub_field_value) }}" class="text-indigo-400" target="_blank">{{ sub_field_value }}</a></p>
                                {% endif %}
                            {% elif sub_field.type == 'textarea' %}
                                <textarea name="{{ sub_field.name }}" class="form-textarea mt-1 block w-full rounded-md shadow-sm sm:text-sm">{{ form_data.get(field.name, {}).get(sub_field.name, '') }}</textarea>
                            {% else %}
                                <input type="text" name="{{ sub_field.name }}" class="form-input mt-1 block w-full rounded-md shadow-sm sm:text-sm" value="{{ form_data.get(field.name, {}).get(sub_field.name, '') }}">
                            {% endif %}
                        {% endfor %}
                        </div>
                    {% endfor %}
                    </div>

                {% elif field.type == 'dynamic_table' %}
                    {% set new_row_object = {} %}
                    {% for col in field.columns %}{% set _ = new_row_object.update({col: ''}) %}{% endfor %}
                    <div x-data='{ 
                            rows: {{ form_data.get(field.name, [])|tojson|safe or "[]" }}, 
                            predefined: {{ field.get("predefined_rows", [])|tojson|safe }},
                            newRowTemplate: {{ new_row_object|tojson|safe }}
                         }' 
                         x-init="if (rows.length === 0) {
                                    if (predefined.length > 0) { 
                                        predefined.forEach(item => rows.push({ 'Item': item, 'Date Given': '', 'Meeting/Session Link': '', 'By Whom': '' }))
                                    } else { 
                                        rows.push(JSON.parse(JSON.stringify(newRowTemplate))) 
                                    }
                                 }">
                        <div class="overflow-x-auto">
                            <table class="min-w-full">
                                <thead class="border-b border-gray-700">
                                    <tr>
                                        {% for col in field.columns %}
                                            <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">{{ col }}</th>
                                        {% endfor %}
                                        <th scope="col" class="relative px-3 py-2"><span class="sr-only">Delete</span></th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-700">
                                    <template x-for="(row, index) in rows" :key="index">
                                        <tr class="hover:bg-gray-700/50">
                                            {% for col_name in field.columns %}
                                                {% set input_name = field.name + '_' + col_name.lower().replace(' / ', '_').replace(' ', '_').replace('(', '').replace(')', '') + '[]' %}
                                                {% set placeholder_text = field.placeholders.get(col_name, '') if field.placeholders else '' %}
                                                <td class="px-3 py-2 whitespace-nowrap">
                                                    {% if field.options and col_name in field.options %}
                                                        <select :name="input_name" class="table-select" x-model="row['{{ col_name }}']">
                                                            <option class="bg-gray-800 text-gray-300" value="" disabled>Select...</option>
                                                            {% for option in field.options[col_name] %}
                                                                <option class="bg-gray-800 text-gray-300" value="{{ option }}">{{ option }}</option>
                                                            {% endfor %}
                                                        </select>
                                                    {% else %}
                                                        <input type="text" :name="input_name" class="table-input" x-model="row['{{ col_name }}']" 
                                                               :readonly="predefined.includes(row['Item']) && '{{ col_name }}' === 'Item'"
                                                               placeholder="{{ placeholder_text }}">
                                                    {% endif %}
                                                </td>
                                            {% endfor %}
                                            <td class="px-3 py-2">
                                                <button type="button" @click="rows.splice(index, 1)" class="text-red-500 hover:text-red-400 p-1" x-show="rows.length > 1">X</button>
                                            </td>
                                        </tr>
                                    </template>
                                </tbody>
                            </table>
                        </div>
                        <button type="button" @click="rows.push(JSON.parse(JSON.stringify(newRowTemplate)))" class="mt-2 text-sm font-semibold text-indigo-400 hover:text-indigo-300">+ Add Row</button>
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    </div>
    <div class="mt-8 pt-5 border-t border-gray-700">
        <div class="flex justify-between items-center">
            <button type="submit" name="action" value="back" class="inline-flex justify-center py-2 px-4 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 bg-gray-700 hover:bg-gray-600 disabled:opacity-50" {% if current_stage_index == 0 %}disabled{% endif %}>Back</button>
            <div class="flex items-center space-x-3">
                <button type="submit" name="action" value="review" class="inline-flex justify-center py-2 px-4 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 bg-gray-700 hover:bg-gray-600">Review</button>
                <button type="submit" name="action" value="continue" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    {{ 'Save and Review' if current_stage_index == stage_order|length - 1 else 'Save and Continue' }}
                </button>
            </div>
        </div>
    </div>
</form>
"""
    with open('templates/form_template.html', 'w') as f:
        f.write(form_template_html)

    # templates/review.html
    review_html = """
{% extends "base.html" %}
{% block title %}Review Handover Report{% endblock %}
{% block content %}
<header class="mb-10">
    <h1 class="text-3xl font-bold text-white">Handover Report Review</h1>
    <p class="text-gray-400 mt-1">Please verify all details before final submission.</p>
</header>
<main class="bg-gray-800/50 border border-gray-700 p-8 rounded-lg shadow-lg space-y-8">
    {% for stage_key in stage_order %}
        {% if form_data.get(stage_key) %}
            <section>
                <div class="flex justify-between items-center border-b-2 border-gray-700 pb-2 mb-4">
                    <h2 class="text-xl font-semibold text-white">{{ form_sections[stage_key].title }}</h2>
                    <a href="{{ url_for('stage', stage_name=stage_key) }}" class="text-sm font-medium text-indigo-400 hover:text-indigo-300">Edit</a>
                </div>
                <dl class="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-4">
                    {% for field in form_sections[stage_key].fields %}
                        {% set value = form_data[stage_key].get(field.name) %}
                        {% if value %}
                            <div class="py-2 {% if field.type in ['textarea', 'dynamic_table'] or (field.type == 'conditional_select' and value.get('selection') in field.conditions) %}md:col-span-3{% else %}md:col-span-1{% endif %}">
                                <dt class="text-sm font-medium text-gray-400">{{ field.label }}</dt>
                                {% if field.type == 'dynamic_table' and value %}
                                    <dd class="mt-1 text-sm text-gray-300">
                                        <div class="overflow-x-auto mt-2">
                                            <table class="min-w-full">
                                                <thead class="border-b border-gray-600">
                                                    <tr>
                                                        {% for col in field.columns %}
                                                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase">{{ col }}</th>
                                                        {% endfor %}
                                                    </tr>
                                                </thead>
                                                <tbody class="divide-y divide-gray-600">
                                                    {% for row in value %}
                                                        <tr>
                                                            {% for col_name in field.columns %}
                                                                <td class="px-3 py-2 whitespace-nowrap text-sm">{{ row.get(col_name, '') }}</td>
                                                            {% endfor %}
                                                        </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </div>
                                    </dd>
                                {% elif field.type == 'conditional_select' %}
                                    <dd class="mt-1 text-sm text-gray-300">{{ value.selection }}</dd>
                                    {% if value.selection in field.conditions %}
                                        <div class="mt-2 pl-4 border-l-2 border-gray-700">
                                        {% for sub_field in field.conditions[value.selection] %}
                                            {% set sub_value = value.get(sub_field.name) %}
                                            {% if sub_value %}
                                                <dt class="text-sm font-medium text-gray-500 mt-2">{{ sub_field.label }}</dt>
                                                {% if sub_field.type == 'file' %}
                                                    <dd class="mt-1 text-sm text-indigo-400 hover:text-indigo-300"><a href="{{ url_for('uploaded_file', filename=sub_value) }}" target="_blank">{{ sub_value }}</a></dd>
                                                {% else %}
                                                    <dd class="mt-1 text-sm text-gray-300 whitespace-pre-wrap">{{ sub_value }}</dd>
                                                {% endif %}
                                            {% endif %}
                                        {% endfor %}
                                        </div>
                                    {% endif %}
                                {% elif field.type == 'file' %}
                                    <dd class="mt-1 text-sm text-indigo-400 hover:text-indigo-300"><a href="{{ url_for('uploaded_file', filename=value) }}" target="_blank">{{ value }}</a></dd>
                                {% elif field.type == 'textarea' %}
                                    <dd class="mt-1 text-sm text-gray-300 whitespace-pre-wrap">{{ value }}</dd>
                                {% elif field.type == 'multiselect' %}
                                    <dd class="mt-1 text-sm text-gray-300">{{ value|join(', ') }}</dd>
                                {% else %}
                                    <dd class="mt-1 text-sm text-gray-300">{{ value }}</dd>
                                {% endif %}
                            </div>
                        {% endif %}
                    {% endfor %}
                </dl>
            </section>
        {% endif %}
    {% endfor %}
</main>
<div class="mt-8 bg-gray-800/50 border border-gray-700 p-6 rounded-lg shadow-lg">
    <h3 class="text-lg font-medium leading-6 text-white">Final Submission</h3>
    <p class="mt-1 text-sm text-gray-400">The handover report will be sent to <strong>itsm@cudoventures.com</strong> from <strong>service.review@cudoventures.com</strong> for approval.</p>
    <form action="{{ url_for('submit_report') }}" method="post" class="mt-4">
        <button type="submit" class="w-full inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
            Submit for Approval
        </button>
    </form>
</div>
{% endblock %}
"""
    with open('templates/review.html', 'w') as f:
        f.write(review_html)

    # templates/submission_success.html
    submission_success_html = """
{% extends "base.html" %}
{% block title %}Submission Successful{% endblock %}
{% block content %}
<div class="bg-gray-800/50 border border-gray-700 p-8 rounded-lg shadow-lg text-center mt-10">
    <svg class="mx-auto h-12 w-12 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <h2 class="mt-4 text-2xl font-bold text-white">Submission Successful!</h2>
    <p class="mt-2 text-gray-400">Your handover report has been submitted for approval. An email has been sent to the service team.</p>
    <div class="mt-6">
        <p class="text-sm text-gray-500">For your records, the unique approval link is:</p>
        <div class="mt-2 p-3 bg-gray-800 rounded-md">
            <a href="{{ approval_link }}" class="text-indigo-400 break-all">{{ approval_link }}</a>
        </div>
    </div>
    <div class="mt-8">
        <a href="{{ url_for('index') }}" class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
            Create a New Handover
        </a>
    </div>
</div>
{% endblock %}
"""
    with open('templates/submission_success.html', 'w') as f:
        f.write(submission_success_html)

    # templates/approval.html
    approval_html = """
{% extends "base.html" %}
{% block title %}Approve Handover Report{% endblock %}
{% block content %}
<header class="bg-gray-800/50 border border-gray-700 rounded-lg p-6 mb-8">
    <div class="flex justify-between items-center">
        <div>
            <h1 class="text-3xl font-bold text-white">Handover Approval</h1>
            <p class="text-gray-400 mt-1">Service: <span class="font-semibold text-gray-200">{{ submission.form_data.stage1.service_name }}</span></p>
        </div>
        <div class="text-right">
             <p class="text-sm text-gray-500">Status:</p>
             <span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full 
                {% if submission.status == 'APPROVED' %} bg-green-500/10 text-green-300 
                {% elif submission.status == 'REQUIRES_INFORMATION' %} bg-yellow-500/10 text-yellow-300
                {% else %} bg-blue-500/10 text-blue-300 {% endif %}">
                {{ submission.status.replace('_', ' ') }}
             </span>
        </div>
    </div>
</header>

{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <div class="mb-6">
    {% for category, message in messages %}
      <div class="rounded-md {{ 'bg-yellow-900/20' if category == 'warning' else 'bg-green-900/20' }} p-4 border {{ 'border-yellow-500/30' if category == 'warning' else 'border-green-500/30' }}">
        <p class="text-sm {{ 'text-yellow-300' if category == 'warning' else 'text-green-300' }}">{{ message }}</p>
      </div>
    {% endfor %}
    </div>
  {% endif %}
{% endwith %}

<form action="{{ url_for('process_approval', handover_id=submission.id) }}" method="post">
<main class="bg-gray-800/50 border border-gray-700 p-8 rounded-lg shadow-lg space-y-8">
    {% for stage_key in stage_order %}
        {% if submission.form_data.get(stage_key) %}
            <section x-data="{ approval: '{{ submission.approvals.get(stage_key, {}).get('status', 'Approved') }}' }">
                <div class="flex justify-between items-center border-b-2 border-gray-700 pb-2 mb-4">
                    <h2 class="text-xl font-semibold text-white">{{ form_sections[stage_key].title }}</h2>
                    <div class="no-print flex items-center space-x-4">
                        <select :name="'approval_' + '{{ stage_key }}'" x-model="approval" class="form-select rounded-md shadow-sm text-sm">
                            <option class="bg-gray-800 text-gray-300">Approved</option>
                            <option class="bg-gray-800 text-gray-300">More Information Needed</option>
                        </select>
                    </div>
                </div>
                
                <div x-show="approval === 'More Information Needed'" x-cloak class="no-print my-4 p-4 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                    <label :for="'notes_' + '{{ stage_key }}'" class="block text-sm font-medium text-yellow-300">Notes (Required if more information is needed)</label>
                    <textarea :name="'notes_' + '{{ stage_key }}'" rows="2" class="form-textarea mt-1 block w-full rounded-md shadow-sm sm:text-sm"
                              placeholder="Specify what information is needed...">{{ submission.approvals.get(stage_key, {}).get('notes', '') }}</textarea>
                </div>
                
                {% if submission.approvals.get(stage_key, {}).get('status') == 'More Information Needed' %}
                <div class="my-4 p-4 bg-yellow-900/20 rounded-lg border border-yellow-500/30">
                     <p class="text-sm font-bold text-yellow-300">Feedback Provided:</p>
                     <p class="mt-1 text-sm text-yellow-400 whitespace-pre-wrap">{{ submission.approvals[stage_key]['notes'] }}</p>
                </div>
                {% endif %}

                <dl class="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-4">
                    {% for field in form_sections[stage_key].fields %}
                        {% set value = submission.form_data[stage_key].get(field.name) %}
                        {% if value %}
                            <div class="py-2 {% if field.type in ['textarea', 'dynamic_table'] or (field.type == 'conditional_select' and value.get('selection') in field.conditions) %}md:col-span-3{% else %}md:col-span-1{% endif %}">
                                <dt class="text-sm font-medium text-gray-400">{{ field.label }}</dt>
                                {% if field.type == 'dynamic_table' and value %}
                                    <dd class="mt-1 text-sm text-gray-300">
                                        <div class="overflow-x-auto mt-2">
                                            <table class="min-w-full">
                                                <thead class="border-b border-gray-600">
                                                    <tr>
                                                        {% for col in field.columns %}
                                                            <th class="px-3 py-2 text-left text-xs font-medium text-gray-400 uppercase">{{ col }}</th>
                                                        {% endfor %}
                                                    </tr>
                                                </thead>
                                                <tbody class="divide-y divide-gray-600">
                                                    {% for row in value %}
                                                        <tr>
                                                            {% for col_name in field.columns %}
                                                                <td class="px-3 py-2 whitespace-nowrap text-sm">{{ row.get(col_name, '') }}</td>
                                                            {% endfor %}
                                                        </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </div>
                                    </dd>
                                {% elif field.type == 'conditional_select' %}
                                    <dd class="mt-1 text-sm text-gray-300">{{ value.selection }}</dd>
                                    {% if value.selection in field.conditions %}
                                        <div class="mt-2 pl-4 border-l-2 border-gray-700">
                                        {% for sub_field in field.conditions[value.selection] %}
                                            {% set sub_value = value.get(sub_field.name) %}
                                            {% if sub_value %}
                                                <dt class="text-sm font-medium text-gray-500 mt-2">{{ sub_field.label }}</dt>
                                                {% if sub_field.type == 'file' %}
                                                    <dd class="mt-1 text-sm text-indigo-400 hover:text-indigo-300"><a href="{{ url_for('uploaded_file', filename=sub_value) }}" target="_blank">{{ sub_value }}</a></dd>
                                                {% else %}
                                                    <dd class="mt-1 text-sm text-gray-300 whitespace-pre-wrap">{{ sub_value }}</dd>
                                                {% endif %}
                                            {% endif %}
                                        {% endfor %}
                                        </div>
                                    {% endif %}
                                {% elif field.type == 'file' %}
                                    <dd class="mt-1 text-sm text-indigo-400 hover:text-indigo-300"><a href="{{ url_for('uploaded_file', filename=value) }}" target="_blank">{{ value }}</a></dd>
                                {% elif field.type == 'textarea' %}
                                    <dd class="mt-1 text-sm text-gray-300 whitespace-pre-wrap">{{ value }}</dd>
                                {% elif field.type == 'multiselect' %}
                                    <dd class="mt-1 text-sm text-gray-300">{{ value|join(', ') }}</dd>
                                {% else %}
                                    <dd class="mt-1 text-sm text-gray-300">{{ value }}</dd>
                                {% endif %}
                            </div>
                        {% endif %}
                    {% endfor %}
                </dl>
            </section>
        {% endif %}
    {% endfor %}
</main>

<div class="no-print mt-8 bg-gray-800/50 border border-gray-700 p-6 rounded-lg shadow-lg">
    <div class="flex justify-end">
        <button type="submit" class="w-full sm:w-auto inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700">
            Submit Review
        </button>
    </div>
</div>
</form>
{% endblock %}
"""
    with open('templates/approval.html', 'w') as f:
        f.write(approval_html)

    app.run(debug=True, host='0.0.0.0', port=5015)
