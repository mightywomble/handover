# handover_app/utils.py

from flask import request
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_dynamic_table(field_name, columns):
    """
    Processes form data for a dynamic table.
    This function is now corrected to properly handle the list of column dictionaries.
    """
    table_data = []
    
    # Ensure there are columns defined to avoid an IndexError.
    if not columns:
        return []

    # The first column dictionary from the list of column definitions.
    first_column_def = columns[0]
    # The 'name' of the first column (e.g., 'contact_name').
    first_col_name = first_column_def['name']
    
    # Construct the key for the list of values from the form.
    # e.g., 'contacts_table_contact_name[]'
    first_col_form_key = f"{field_name}_{first_col_name}[]"
    
    # The number of rows is determined by how many items were submitted for the first column.
    num_rows = len(request.form.getlist(first_col_form_key))

    for i in range(num_rows):
        row_data = {}
        # Iterate through the column definitions (the list of dictionaries).
        for col_def in columns:
            # The 'name' of the current column (e.g., 'contact_email').
            col_name = col_def['name']
            
            # Construct the key for the current column's form data.
            # e.g., 'contacts_table_contact_email[]'
            input_name = f"{field_name}_{col_name}[]"
            
            # Get the list of values for this column from the form.
            values = request.form.getlist(input_name)
            
            # Check if there is a value at the current row index.
            if len(values) > i:
                # Store the value in our row_data dictionary using the column's name as the key.
                row_data[col_name] = values[i]
        
        # Add the completed row dictionary to our list of table data.
        if row_data:
            table_data.append(row_data)
    
    return table_data
