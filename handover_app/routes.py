# handover_app/routes.py
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app, send_from_directory
)
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime

from .forms import (
    large_cluster_form_sections,
    large_cluster_stage_order,
    base_install_form_definition,
    onboard_customer_form_definition,
    onboard_supplier_form_definition
)
from .utils import allowed_file, process_dynamic_table

bp = Blueprint('handover', __name__)

@bp.route('/')
def index():
    """Shows the initial selection screen."""
    session.clear()
    return render_template('start.html')

@bp.route('/form/large-cluster')
def large_cluster_start():
    """Starts the multi-stage form for a Large Cluster."""
    session.clear()
    session['form_data'] = {}
    session['form_type'] = 'large_cluster'
    return redirect(url_for('handover.stage', stage_name=large_cluster_stage_order[0]))

@bp.route('/form/base-install', methods=['GET', 'POST'])
def base_install_form():
    """Handles the single-page form for a Base Install."""
    session['form_type'] = 'base_install'
    form_data = session.get('form_data', {})

    if request.method == 'POST':
        # Flatten all fields from all sections into one list for processing
        all_fields = []
        for section in base_install_form_definition['sections']:
            all_fields.extend(section['fields'])

        for field in all_fields:
            field_name = field['name']
            if field['type'] == 'dynamic_table':
                form_data[field_name] = process_dynamic_table(field_name, field['columns'])
            elif field['type'] == 'file':
                 if field_name in request.files:
                    file = request.files[field_name]
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(f"{field_name}_{file.filename}")
                        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                        form_data[field_name] = filename
            elif field['type'] == 'multiselect':
                 form_data[field_name] = request.form.getlist(field_name)
            elif field['type'] == 'conditional_select':
                form_data[field_name] = {}
                selection = request.form.get(field_name)
                form_data[field_name]['selection'] = selection
                if selection in field.get('conditions', {}):
                    for sub_field in field['conditions'][selection]:
                        sub_field_name = sub_field['name']
                        if sub_field['type'] == 'file':
                             if sub_field_name in request.files:
                                file = request.files[sub_field_name]
                                if file and file.filename and allowed_file(file.filename):
                                    filename = secure_filename(f"{sub_field_name}_{file.filename}")
                                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                                    form_data[field_name][sub_field_name] = filename
                        else:
                            form_data[field_name][sub_field_name] = request.form.get(sub_field_name)
            else:
                form_data[field_name] = request.form.get(field_name)

        session['form_data'] = form_data
        session.modified = True
        return redirect(url_for('handover.review'))

    return render_template('base_install_form.html',
                           form_definition=base_install_form_definition,
                           form_data=form_data)


@bp.route('/stage/<stage_name>', methods=['GET', 'POST'])
def stage(stage_name):
    """Renders a form stage for the Large Cluster form."""
    if stage_name not in large_cluster_stage_order:
        return "Stage not found", 404

    if 'form_data' not in session or session.get('form_type') != 'large_cluster':
        # If session is invalid, restart the process
        return redirect(url_for('handover.index'))

    if request.method == 'POST':
        session['form_data'][stage_name] = {}

        for field in large_cluster_form_sections[stage_name]["fields"]:
            field_name = field['name']
            if field['type'] == 'dynamic_table':
                session['form_data'][stage_name][field_name] = process_dynamic_table(field_name, field['columns'])
            elif field['type'] == 'file':
                if field_name in request.files:
                    file = request.files[field_name]
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(f"{field_name}_{file.filename}")
                        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
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
                                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                                    session['form_data'][stage_name][field_name][sub_field_name] = filename
                        else:
                            session['form_data'][stage_name][field_name][sub_field_name] = request.form.get(sub_field_name)
            else:
                session['form_data'][stage_name][field_name] = request.form.get(field_name)

        session.modified = True
        action = request.form.get('action', 'continue')
        current_index = large_cluster_stage_order.index(stage_name)

        if action == 'review':
             return redirect(url_for('handover.review'))
        elif action == 'back' and current_index > 0:
            previous_stage_name = large_cluster_stage_order[current_index - 1]
            return redirect(url_for('handover.stage', stage_name=previous_stage_name))
        elif current_index + 1 < len(large_cluster_stage_order):
            next_stage_name = large_cluster_stage_order[current_index + 1]
            return redirect(url_for('handover.stage', stage_name=next_stage_name))
        else:
            return redirect(url_for('handover.review'))

    current_index = large_cluster_stage_order.index(stage_name)
    form_data = session.get('form_data', {}).get(stage_name, {})

    return render_template('index.html',
                           stage_name=stage_name,
                           stage_data=large_cluster_form_sections[stage_name],
                           form_data=form_data,
                           stage_order=large_cluster_stage_order,
                           current_stage_index=current_index,
                           form_sections=large_cluster_form_sections)

@bp.route('/review')
def review():
    """Displays all collected data for final review before submission."""
    if 'form_data' not in session or not session['form_data']:
        flash("No data to review. Please start from the beginning.", "warning")
        return redirect(url_for('handover.index'))

    return render_template('review.html',
                           form_data=session.get('form_data', {}),
                           form_type=session.get('form_type'),
                           large_cluster_form_sections=large_cluster_form_sections,
                           base_install_form_definition=base_install_form_definition,
                           large_cluster_stage_order=large_cluster_stage_order)

@bp.route('/submit_report', methods=['POST'])
def submit_report():
    """Saves the report to a file and redirects to a success page with the approval link."""
    if 'form_data' not in session:
        return redirect(url_for('handover.index'))

    handover_id = str(uuid.uuid4())
    submission_data = {
        "id": handover_id,
        "status": "PENDING_APPROVAL",
        "submitted_at": datetime.utcnow().isoformat(),
        "form_data": session['form_data'],
        "form_type": session.get('form_type'),
        "approvals": {}
    }

    filepath = os.path.join(current_app.config['SUBMISSIONS_FOLDER'], f"{handover_id}.json")
    with open(filepath, 'w') as f:
        json.dump(submission_data, f, indent=4)

    session.clear()
    return redirect(url_for('handover.submission_success', handover_id=handover_id))

@bp.route('/submission_success/<handover_id>')
def submission_success(handover_id):
    """Shows a success message with the unique link for the approval process."""
    approval_link = url_for('handover.approve', handover_id=handover_id, _external=True)
    print(f"--- SIMULATED EMAIL ---")
    print(f"To: itsm@cudoventures.com")
    print(f"From: service.review@cudoventures.com")
    print(f"Subject: New Service Handover for Approval")
    print(f"Please review and approve the following service handover: {approval_link}")
    print(f"-----------------------")
    return render_template('submission_success.html', approval_link=approval_link)

@bp.route('/approve/<handover_id>', methods=['GET'])
def approve(handover_id):
    """The approval page for the service team."""
    filepath = os.path.join(current_app.config['SUBMISSIONS_FOLDER'], f"{handover_id}.json")
    if not os.path.exists(filepath):
        return "Submission not found", 404

    with open(filepath, 'r') as f:
        submission_data = json.load(f)

    return render_template('approval.html',
                           submission=submission_data,
                           large_cluster_form_sections=large_cluster_form_sections,
                           base_install_form_definition=base_install_form_definition,
                           large_cluster_stage_order=large_cluster_stage_order)

@bp.route('/process_approval/<handover_id>', methods=['POST'])
def process_approval(handover_id):
    """Processes the submitted approval form."""
    filepath = os.path.join(current_app.config['SUBMISSIONS_FOLDER'], f"{handover_id}.json")
    if not os.path.exists(filepath):
        return "Submission not found", 404

    with open(filepath, 'r') as f:
        submission_data = json.load(f)

    approvals = {}
    requires_more_info = False

    # Determine which form sections to check for approvals
    approval_sections = []
    if submission_data.get('form_type') == 'large_cluster':
        approval_sections = large_cluster_stage_order
    else: # base_install
        approval_sections = [s['title'] for s in base_install_form_definition['sections']]

    for section_key in approval_sections:
        approval_status = request.form.get(f'approval_{section_key}')
        notes = request.form.get(f'notes_{section_key}', '')
        if approval_status == 'More Information Needed' and not notes:
            flash(f"Please provide notes for '{section_key}' when requesting more information.", "warning")
            return redirect(url_for('handover.approve', handover_id=handover_id))

        approvals[section_key] = {'status': approval_status, 'notes': notes}
        if approval_status == 'More Information Needed':
            requires_more_info = True

    submission_data['approvals'] = approvals
    submission_data['last_updated_at'] = datetime.utcnow().isoformat()
    submitter_email = submission_data.get('form_data', {}).get('submitter_email', '[Submitter Email Not Found]')

    if requires_more_info:
        submission_data['status'] = 'REQUIRES_INFORMATION'
        flash("The report has been marked as 'More Information Needed' and feedback has been saved. The original submitter will be notified.", "warning")
        print(f"--- SIMULATED EMAIL (MORE INFO) ---")
        print(f"To: {submitter_email}")
        print(f"From: itsm@cudoventures.com")
        print(f"Subject: More Information Required for Service Handover")
        print(f"Please review the feedback and update the service handover document: {url_for('handover.approve', handover_id=handover_id, _external=True)}")
        print(f"------------------------------------")
    else:
        submission_data['status'] = 'APPROVED'
        flash("The handover report has been successfully approved!", "success")
        print(f"--- SIMULATED EMAIL (APPROVED) ---")
        print(f"To: {submitter_email}, itsm@cudoventures.com")
        print(f"From: service.review@cudoventures.com")
        print(f"Subject: Service Handover Approved")
        print(f"The service handover has been approved: {url_for('handover.approve', handover_id=handover_id, _external=True)}")
        print(f"---------------------------------")

    with open(filepath, 'w') as f:
        json.dump(submission_data, f, indent=4)

    return redirect(url_for('handover.approve', handover_id=handover_id))


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serves uploaded files."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/form/onboard-customer', methods=['GET', 'POST'])
def onboard_customer():
    """Handles the form for onboarding a new customer."""
    session['form_type'] = 'onboard_customer'
    form_data = session.get('form_data', {})

    if request.method == 'POST':
        all_fields = []
        for section in onboard_customer_form_definition['sections']:
            all_fields.extend(section['fields'])

        for field in all_fields:
            field_name = field['name']
            if field['type'] == 'dynamic_table':
                form_data[field_name] = process_dynamic_table(field_name, field['columns'])
            else:
                form_data[field_name] = request.form.get(field_name)

        session['form_data'] = form_data
        session.modified = True
        return redirect(url_for('handover.review_onboard_customer'))

    return render_template('onboard_customer_form.html',
                           form_definition=onboard_customer_form_definition,
                           form_data=form_data)


@bp.route('/review/onboard-customer')
def review_onboard_customer():
    """Displays collected data for customer onboarding for final review."""
    if 'form_data' not in session or session.get('form_type') != 'onboard_customer':
        flash("No data to review. Please start from the beginning.", "warning")
        return redirect(url_for('handover.index'))

    return render_template('review_onboard_customer.html',
                           form_data=session.get('form_data', {}),
                           form_definition=onboard_customer_form_definition)


@bp.route('/onboard/create_company', methods=['POST'])
def create_company():
    """Placeholder for creating the company."""
    # This will eventually be an API call
    # For now, just clear the session and show a success message.
    session.clear()
    flash("Company created successfully! (This is a placeholder)", "success")
    return redirect(url_for('handover.index'))

@bp.route('/form/onboard-supplier', methods=['GET', 'POST'])
def onboard_supplier():
    """Handles the form for onboarding a new supplier."""
    session['form_type'] = 'onboard_supplier'
    form_data = session.get('form_data', {})

    if request.method == 'POST':
        all_fields = []
        for section in onboard_supplier_form_definition['sections']:
            all_fields.extend(section['fields'])

        for field in all_fields:
            field_name = field['name']
            if field['type'] == 'conditional_select':
                form_data[field_name] = {}
                selection = request.form.get(field_name)
                form_data[field_name]['selection'] = selection
                if selection in field.get('conditions', {}):
                    for sub_field in field['conditions'][selection]:
                        sub_field_name = sub_field['name']
                        form_data[field_name][sub_field_name] = request.form.get(sub_field_name)
            elif field['type'] == 'multiselect_conditional':
                form_data[field_name] = {}
                selections = request.form.getlist(field_name)
                form_data[field_name]['selection'] = selections
                if 'Other' in selections and 'Other' in field.get('conditions', {}):
                     for sub_field in field['conditions']['Other']:
                        sub_field_name = sub_field['name']
                        form_data[field_name][sub_field_name] = request.form.get(sub_field_name)
            else:
                form_data[field_name] = request.form.get(field_name)

        session['form_data'] = form_data
        session.modified = True
        return redirect(url_for('handover.review_onboard_supplier'))

    return render_template('onboard_supplier_form.html',
                           form_definition=onboard_supplier_form_definition,
                           form_data=form_data)


@bp.route('/review/onboard-supplier')
def review_onboard_supplier():
    """Displays collected data for supplier onboarding for final review."""
    if 'form_data' not in session or session.get('form_type') != 'onboard_supplier':
        flash("No data to review. Please start from the beginning.", "warning")
        return redirect(url_for('handover.index'))

    return render_template('review_onboard_supplier.html',
                           form_data=session.get('form_data', {}),
                           form_definition=onboard_supplier_form_definition)


@bp.route('/onboard/send-to-itsm', methods=['POST'])
def send_to_itsm():
    """Placeholder for sending supplier details to ITSM."""
    session.clear()
    flash("Supplier details sent to ITSM successfully! (This is a placeholder)", "success")
    return redirect(url_for('handover.index'))

@bp.route('/api-docs')
def api_docs():
    """Shows the API documentation page."""
    return render_template('api_docs.html')