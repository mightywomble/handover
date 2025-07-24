# handover_app/sysaid.py
import requests
import json

def login(base_url, username, password):
    """Logs into the SysAid API and returns session cookies or an error."""
    login_url = f"{base_url.rstrip('/')}/api/v1/login"
    credentials = {
        "user_name": username,
        "password": password
    }
    try:
        response = requests.post(login_url, json=credentials, timeout=10)
        response.raise_for_status()
        return response.cookies, None
    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP Error: {e.response.status_code} {e.response.reason}"
        if e.response.status_code == 401:
            error_message += " (Unauthorized - check credentials)"
        if e.response.status_code == 405:
            error_message += " (Method Not Allowed - check SysAid URL in settings)"
        return None, error_message
    except requests.exceptions.RequestException as e:
        error_message = f"Request Failed: {e}"
        return None, error_message

def create_company(session_cookies, base_url, form_data):
    """Creates a new company in SysAid."""
    company_url = f"{base_url.rstrip('/')}/api/v1/company"
    
    company_payload = {
        "info": [
            {"key": "name", "value": form_data.get('company_name', '')},
            {"key": "address", "value": form_data.get('address_1', '')},
            {"key": "address2", "value": form_data.get('address_2', '')},
            {"key": "city", "value": form_data.get('city', '')},
            {"key": "state", "value": form_data.get('state', '')},
            {"key": "zip_code", "value": form_data.get('zip_code', '')},
            {"key": "country", "value": form_data.get('country', '')},
            {"key": "main_phone", "value": form_data.get('phone', '')},
            {"key": "notes", "value": form_data.get('notes', '')}
        ]
    }

    try:
        # FIX: SysAid API seems to use POST for creating new objects, not PUT.
        response = requests.post(company_url, json=company_payload, cookies=session_cookies, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        error_message = f"API Error: {e.response.status_code} {e.response.reason} on URL {e.request.url}."
        if e.response.status_code == 405:
            error_message += f" The API endpoint does not support the '{e.request.method}' method."
        try:
            error_details = e.response.json()
            error_message += f" Details: {error_details.get('message', e.response.text)}"
        except json.JSONDecodeError:
            pass # No JSON body in the error response
        return None, error_message
    except requests.exceptions.RequestException as e:
        return None, f"Request Failed: {e}"

def create_ci(session_cookies, base_url, form_data):
    """Creates a new CI in SysAid."""
    ci_url = f"{base_url.rstrip('/')}/api/v1/ci"

    ci_payload = {
        "info": [
            {"key": "name", "value": form_data.get('supplier_name', '')},
            {"key": "type", "value": ", ".join(form_data.get('ci_sub_type', {}).get('selection', []))},
            {"key": "status", "value": form_data.get('status', '')},
            {"key": "location", "value": form_data.get('dc_address', '')},
        ]
    }

    try:
        # FIX: SysAid API seems to use POST for creating new objects, not PUT.
        response = requests.post(ci_url, json=ci_payload, cookies=session_cookies, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        error_message = f"API Error: {e.response.status_code} {e.response.reason} on URL {e.request.url}."
        if e.response.status_code == 405:
            error_message += f" The API endpoint does not support the '{e.request.method}' method."
        try:
            error_details = e.response.json()
            error_message += f" Details: {error_details.get('message', e.response.text)}"
        except json.JSONDecodeError:
            pass
        return None, error_message
    except requests.exceptions.RequestException as e:
        return None, f"Request Failed: {e}"
