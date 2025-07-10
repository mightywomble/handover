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

from .forms import form_sections, stage_order
from .utils import allowed_file, process_dynamic_table

bp = Blueprint('handover', __name__)

@bp.route('/')
def index():
    """Initializes session and redirects to the first stage."""
    session.clear()
    session['form_data'] = {}
    return redirect(url_for('handover.stage', stage_name=stage_order[0]))

@bp.route('/stage/<stage_name>', methods=['GET', 'POST'])
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
        current_index = stage_order.index(stage_name)

        if action == 'review':
             return redirect(url_for('handover.review'))
        elif action == 'back' and current_index > 0:
            previous_stage_name = stage_order[current_index - 1]
            return redirect(url_for('handover.stage', stage_name=previous_stage_name))
        elif current_index + 1 < len(stage_order):
            next_stage_name = stage_order[current_index + 1]
            return redirect(url_for('handover.stage', stage_name=next_stage_name))
        else:
            return redirect(url_for('handover.review'))

    current_index = stage_order.index(stage_name)
    form_data = session.get('form_data', {}).get(stage_name, {})
    
    return render_template('index.html', 
                           stage_name=stage_name,
                           stage_data=form_sections[stage_name],
                           form_data=form_data,
                           stage_order=stage_order,
                           current_stage_index=current_index,
                           form_sections=form_sections)

@bp.route('/review')
def review():
    """Displays all collected data for final review before submission."""
    if 'form_data' not in session or not session['form_data']:
        flash("No data to review. Please start from the beginning.", "warning")
        return redirect(url_for('handover.index'))
        
    return render_template('review.html',
                           form_data=session.get('form_data', {}),
                           form_sections=form_sections,
                           stage_order=stage_order)

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
                           form_sections=form_sections,
                           stage_order=stage_order)

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
    for stage_key in stage_order:
        approval_status = request.form.get(f'approval_{stage_key}')
        notes = request.form.get(f'notes_{stage_key}', '')
        if approval_status == 'More Information Needed' and not notes:
            flash(f"Please provide notes for '{form_sections[stage_key]['title']}' when requesting more information.", "warning")
            return redirect(url_for('handover.approve', handover_id=handover_id))

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
