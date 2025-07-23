# handover_app/forms.py

# --- Large Cluster Form Definition (Existing Stages) ---
large_cluster_stage_order = ["stage1", "stage2", "stage3", "stage4", "stage5", "stage6"]

large_cluster_form_sections = {
    "stage1": {
        "title": "Service Introduction & Overview",
        "fields": [
            {"name": "customer_name", "label": "Customer Name", "type": "text", "placeholder": "e.g., Example Corp"},
            {"name": "submitter_email", "label": "Your Email Address", "type": "text", "placeholder": "e.g., your.name@example.com (for approval notifications)"},
            {"name": "sales_reference", "label": "Sales Reference", "type": "text", "placeholder": "e.g., SVC-WEBCL"},
            {"name": "salesforce_link", "label": "Salesforce Link", "type": "text", "placeholder": "e.g., https://example.my.salesforce.com/..."},
            {"name": "version", "label": "Version", "type": "text", "placeholder": "e.g., 1.0"},
            {"name": "date_prepared", "label": "Date Prepared", "type": "date"},
            {"name": "prepared_by", "label": "Handover Prepared By (Engineer Name)", "type": "text", "placeholder": "e.g., Jane Doe"},
            {"name": "project_reference", "label": "Project Reference", "type": "text", "placeholder": "e.g., PRJ-2025-04-WEBCL"},
            {"name": "brief_description", "label": "Brief Description", "type": "textarea", "placeholder": "A short description of what the service/system does."},
            {"name": "support_type", "label": "Support Type", "type": "select", "options": ["", "Basic", "Core Support", "Managed Service", "Other"]},
            {"name": "service_hours_sla", "label": "Service Hours / SLA", "type": "text", "placeholder": "e.g., 24x7, Business Hours 9-5 Mon-Fri"},
            {"name": "customer_contacts", "label": "Customer Contacts", "type": "textarea", "placeholder": "List main user groups or departments"},
            {"name": "slack_group_url", "label": "Slack Group URL", "type": "text", "placeholder": "e.g., https://app.slack.com/client/T0.../C0..."},
            {"name": "supplier_details", "label": "Supplier Details", "type": "dynamic_table", "columns": ["Supplier Name", "Support Email", "Contract Number", "Notes"], "placeholders": {"Supplier Name": "e.g., Dell", "Support Email": "e.g., support@dell.com", "Contract Number": "e.g., 123-456-789"}},
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
            {"name": "netbox_link", "label": "Netbox Link", "type": "text", "placeholder": "e.g., https://netbox.example.com/dcim/devices/1/"},
            {"name": "cmdb_data_verified_by", "label": "CMDB Data Verified By", "type": "text", "placeholder": "e.g., John Smith on 2025-07-10"},
            {"name": "build_method", "label": "Build Method", "type": "multiselect", "options": ["Manual", "Ansible", "Terraform", "Other"]},
            {"name": "build_config_links", "label": "Link to Build Config", "type": "dynamic_table", "columns": ["Item", "Github Link"], "placeholders": {"Item": "e.g., Web Server Playbook", "Github Link": "e.g., https://github.com/user/repo/playbook.yml"}},
            {"name": "last_os_patch_date", "label": "Last OS Patch Date", "type": "text", "placeholder": "e.g., When was sudo apt-get update run last?"},
            {"name": "upload_build_docs", "label": "Upload Build Docs", "type": "conditional_select", "options": ["Yes", "No"], "conditions": {"Yes": [{"name": "presales_doc_upload", "label": "Presales Approved Document", "type": "file"}, {"name": "build_doc_upload", "label": "Build Document", "type": "file"}]}},
            {"name": "key_config_files", "label": "Key Configuration File Paths", "type": "dynamic_table", "columns": ["Item", "Path", "Description"], "placeholders": {"Item": "e.g., Apache Config", "Path": "e.g., /etc/httpd/httpd.conf", "Description": "e.g., Main web server configuration"}},
            {"name": "credentials_management", "label": "Credentials & Secrets Management", "type": "dynamic_table", "columns": ["Item", "Location", "Search For / Link"], "options": {"Location": ["1Password", "HashiCorp Vault", "CyberArk", "Other"]}, "placeholders": {"Item": "e.g., Web App DB Password", "Search For / Link": "e.g., 'PROD Web Server Root' or path/to/secret"}},
        ]
    },
    "stage4": {
        "title": "Operational Procedures",
        "fields": [
            {"name": "service_procedures", "label": "Service Procedures", "type": "dynamic_table", "columns": ["Service Name", "Start Command", "Stop Command", "Restart Command", "Check Status Command", "Test Procedure", "Notes"], "placeholders": {"Service Name": "e.g., httpd", "Start Command": "e.g., systemctl start httpd", "Stop Command": "e.g., systemctl stop httpd", "Restart Command": "e.g., systemctl restart httpd", "Check Status Command": "e.g., systemctl status httpd", "Test Procedure": "e.g., curl localhost"}},
            {"name": "installed_services", "label": "What services/systems are installed on this cluster?", "type": "textarea", "placeholder": "e.g., NFS, Nvidia Drivers, Slurm, Kubernetes, Docker, etc."},
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


# --- Base Install Form Definition (New) ---
base_install_form_definition = {
    "title": "Base Install Handover",
    "sections": [
        {
            "title": "Service Introduction & Overview",
            "fields": [
                {"name": "customer_name", "label": "Customer Name", "type": "text", "placeholder": "e.g., Example Corp"},
                {"name": "submitter_email", "label": "Your Email Address", "type": "text", "placeholder": "e.g., your.name@example.com (for approval notifications)"},
                {"name": "sales_reference", "label": "Sales Reference", "type": "text", "placeholder": "e.g., SVC-WEBCL"},
                {"name": "salesforce_link", "label": "Salesforce Link", "type": "text", "placeholder": "e.g., https://example.my.salesforce.com/..."},
                {"name": "version", "label": "Version", "type": "text", "placeholder": "e.g., 1.0"},
                {"name": "date_prepared", "label": "Date Prepared", "type": "date"},
                {"name": "prepared_by", "label": "Handover Prepared By (Engineer Name)", "type": "text", "placeholder": "e.g., Jane Doe"},
                {"name": "project_reference", "label": "Project Reference", "type": "text", "placeholder": "e.g., PRJ-2025-04-WEBCL"},
                {"name": "brief_description", "label": "Brief Description", "type": "textarea", "placeholder": "A short description of what the service/system does."},
                {"name": "support_type", "label": "Support Type", "type": "select", "options": ["", "Basic", "Core Support", "Managed Service", "Other"]},
                {"name": "service_hours_sla", "label": "Service Hours / SLA", "type": "text", "placeholder": "e.g., 24x7, Business Hours 9-5 Mon-Fri"},
                {"name": "customer_contacts", "label": "Customer Contacts", "type": "textarea", "placeholder": "List main user groups or departments"},
                {"name": "slack_group_url", "label": "Slack Group URL", "type": "text", "placeholder": "e.g., https://app.slack.com/client/T0.../C0..."},
                {"name": "supplier_details", "label": "Supplier Details", "type": "dynamic_table", "columns": ["Supplier Name", "Support Email", "Contract Number", "Notes"], "placeholders": {"Supplier Name": "e.g., Dell", "Support Email": "e.g., support@dell.com", "Contract Number": "e.g., 123-456-789"}},
                {"name": "deployment_location", "label": "Deployment Location", "type": "conditional_select", "options": ["Cudo Compute", "3rd Party"], "conditions": {"3rd Party": [{"name": "baremetal_supplier", "label": "Baremetal Supplier Name:", "type": "text"}]}},
            ]
        },
        {
            "title": "Infrastructure & Configuration",
            "fields": [
                {"name": "component_overview", "label": "Component Overview", "type": "dynamic_table", "columns": ["Component Type", "Hostname / Identifier", "IP Address", "OS Version", "Last Patch Date"], "options": {"Component Type": ["Server", "Network", "Storage", "Rack", "Cable", "Other"]}, "placeholders": {"Hostname / Identifier": "e.g., web-prod-01", "IP Address": "e.g., 10.1.1.10"}},
                {"name": "public_ip_address", "label": "Public IP Address", "type": "text", "placeholder": "e.g., 8.8.8.8"},
                {"name": "credentials_management", "label": "Credentials & Secrets Management", "type": "dynamic_table", "columns": ["Item", "Location", "Search For / Link"], "options": {"Location": ["1Password", "HashiCorp Vault", "CyberArk", "Other"]}, "placeholders": {"Item": "e.g., Web App DB Password", "Search For / Link": "e.g., 'PROD Web Server Root' or path/to/secret"}},
                {"name": "build_method", "label": "Build Method", "type": "multiselect", "options": ["Manual", "Ansible", "Terraform", "Other"]},
                {"name": "build_config_links", "label": "Link to Build Config", "type": "dynamic_table", "columns": ["Item", "Github Link"], "placeholders": {"Item": "e.g., Web Server Playbook", "Github Link": "e.g., https://github.com/user/repo/playbook.yml"}},
                {"name": "last_os_patch_date", "label": "Last OS Patch Date", "type": "text", "placeholder": "e.g., When was sudo apt-get update run last?"},
            ]
        }
    ]
}

# --- Onboard Customer Form Definition (New) ---
onboard_customer_form_definition = {
    "title": "Onboard Customer",
    "sections": [
        {
            "title": "Cudo Details",
            "fields": [
                {"name": "account_manager", "label": "Account Manager", "type": "text", "placeholder": "e.g., John Doe"},
                {"name": "salesforce_reference", "label": "Salesforce Reference", "type": "text", "placeholder": "e.g., SF-12345"},
            ]
        },
        {
            "title": "Company Details",
            "fields": [
                {"name": "company_name", "label": "Name", "type": "text"},
                {"name": "address_1", "label": "Address", "type": "text"},
                {"name": "address_2", "label": "Address 2", "type": "text"},
                {"name": "city", "label": "City", "type": "text"},
                {"name": "state", "label": "State", "type": "text"},
                {"name": "zip_code", "label": "Zip", "type": "text"},
                {"name": "country", "label": "Country", "type": "text"},
                {"name": "phone", "label": "Phone", "type": "text"},
                {"name": "notes", "label": "Notes", "type": "textarea"},
            ]
        },
        {
            "title": "Contacts",
            "fields": [
                {"name": "contacts", "label": "Contacts", "type": "dynamic_table", "columns": ["First Name", "Last Name", "Email", "Phone", "Company", "Dept", "Is Supervisor"]},
            ]
        },
        {
            "title": "Supplier",
            "fields": [
                {"name": "supplier_placeholder", "label": "Supplier Details", "type": "textarea", "placeholder": "This will be an API call into an application eventually, its a placeholder now"},
            ]
        },
    ]
}

# --- Onboard Supplier Form Definition (New) ---
onboard_supplier_form_definition = {
    "title": "Onboard Supplier",
    "sections": [
        {
            "title": "Supplier Details",
            "fields": [
                {"name": "supplier_name", "label": "Supplier Name", "type": "text"},
                {"name": "ci_type", "label": "CI Type", "type": "select", "options": ["", "On Platform", "Off Platform"]},
                {
                    "name": "ci_sub_type", "label": "CI Sub Type", "type": "multiselect_conditional",
                    "options": ["Baremetal", "VM", "DC", "Colo", "Rack", "Other"],
                    "conditions": {
                        "Other": [{"name": "ci_sub_type_other", "label": "Specify Other CI Sub Type", "type": "text"}]
                    }
                },
                {"name": "status", "label": "Status", "type": "select", "options": ["", "Production Live", "Production Available"]},
                {"name": "supplier_dc", "label": "Supplier Data Center", "type": "text", "placeholder": "e.g., in-hydrabad-01"},
                {"name": "dc_address", "label": "Data Center Address", "type": "text"},
                {"name": "primary_contact_name", "label": "Primary Contact Name (Escalation Point)", "type": "text"},
                {"name": "primary_contact_email", "label": "Primary Contact Email (Escalation Point)", "type": "text"},
                {
                    "name": "support_contact_method", "label": "Support Contact Method", "type": "multiselect_conditional",
                    "options": ["Portal", "Email", "Slack", "SMS", "Other"],
                    "conditions": {
                        "Other": [{"name": "support_contact_method_other", "label": "Specify Other Method", "type": "text"}]
                    }
                },
                {"name": "support_email", "label": "Support email address", "type": "text"},
                {
                    "name": "support_hours", "label": "Support hours", "type": "conditional_select",
                    "options": ["", "24/7", "24/5", "9/5/M-F", "Other"],
                    "conditions": {
                        "Other": [{"name": "support_hours_other", "label": "Specify Other Hours", "type": "text"}]
                    }
                },
                {"name": "on_site_tech_name", "label": "On site Tech Name", "type": "text"},
            ]
        }
    ]
}
