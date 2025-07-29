# handover_app/topdesk_api.py

import requests
from requests.auth import HTTPBasicAuth
from flask import current_app, flash

def _get_api_details():
    """Helper function to get API config from the current app context."""
    config = current_app.config
    base_url = f"{config.get('TOPDESK_URL')}/tas/api"
    auth = HTTPBasicAuth(config.get('TOPDESK_USERNAME'), config.get('TOPDESK_APP_PASSWORD'))
    return base_url, auth

def get_country_id_by_name(country_name):
    """
    Looks up a country by its name in TopDesk and returns its ID.
    Returns None if not found or an error occurs.
    """
    if not country_name:
        return None
        
    base_url, auth = _get_api_details()
    endpoint = f"{base_url}/countries"
    
    try:
        # Fetch all countries and filter locally for robustness
        response = requests.get(endpoint, auth=auth)
        response.raise_for_status()
        countries = response.json()
        for country in countries:
            if country.get("name", "").lower() == country_name.lower():
                return country.get("id")
        
        flash(f"Country '{country_name}' not found in TopDesk. It will be left blank.", 'warning')
        return None
    except requests.exceptions.RequestException as e:
        flash(f"Error looking up country '{country_name}' in TopDesk: {e}", 'danger')
        print(f"Error looking up country '{country_name}': {e}")
        return None

def create_topdesk_branch(form_data):
    """
    Creates a new branch in TopDesk using data from the onboarding form.
    Returns the new branch ID on success, None on failure.
    """
    base_url, auth = _get_api_details()
    endpoint = f"{base_url}/branches"
    
    country_id = get_country_id_by_name(form_data.get('customer_country'))

    # Construct the payload with the correct nested 'address' object
    address_payload = {
        "street": form_data.get('customer_street'),
        "number": form_data.get('customer_street_number'),
        "postcode": form_data.get('customer_postcode'),
        "city": form_data.get('customer_city'),
    }
    if country_id:
        address_payload["country"] = {"id": country_id}

    # Dynamically build the main payload to only include fields with values
    payload = {
        "name": form_data.get('customer_name'),
        "address": address_payload
    }
    
    if form_data.get('customer_email'):
        payload['email'] = form_data.get('customer_email')
    if form_data.get('customer_website'):
        payload['website'] = form_data.get('customer_website')
    
    try:
        response = requests.post(endpoint, json=payload, auth=auth)
        response.raise_for_status()
        new_branch = response.json()
        flash(f"Successfully created branch in TopDesk for '{payload['name']}'.", 'success')
        return new_branch.get('id')
    except requests.exceptions.RequestException as e:
        error_message = f"Error creating TopDesk branch: {e}"
        if e.response is not None:
            try:
                error_details = e.response.json()
                if isinstance(error_details, list) and error_details:
                    error_message += f" - Response: {error_details[0].get('message')}"
                else:
                     error_message += f" - Response: {e.response.text}"
            except ValueError:
                error_message += f" - Response: {e.response.text}"
        flash(error_message, 'danger')
        print(error_message)
        return None

def create_topdesk_person(person_data, branch_id):
    """
    Creates a new person in TopDesk and links them to a branch.
    Returns True on success, False on failure.
    """
    base_url, auth = _get_api_details()
    endpoint = f"{base_url}/persons"
    
    payload = {
        "surName": person_data.get('contact_name'),
        "email": person_data.get('contact_email'),
        "branch": {
            "id": branch_id
        }
    }
    
    try:
        response = requests.post(endpoint, json=payload, auth=auth)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        error_message = f"Error creating TopDesk person '{payload['surName']}': {e}"
        if e.response is not None:
            error_message += f" - Response: {e.response.text}"
        flash(error_message, 'danger')
        print(error_message)
        return False
