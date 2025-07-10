# handover_app/utils.py
from flask import request

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

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
