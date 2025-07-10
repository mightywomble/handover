# handover_app/utils.py
from flask import request, flash, redirect, url_for
from flask_login import current_user
from functools import wraps

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

def admin_required(f):
    """
    A decorator to ensure a user is logged in and has the 'Admin' role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "Admin":
            flash("You do not have permission to access this page.", "warning")
            return redirect(url_for("handover.index"))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_dynamic_table(field_name, columns):
    """Helper to process dynamic table data from the form."""
    table_data = []
    # Use the first column to determine the number of rows submitted
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
