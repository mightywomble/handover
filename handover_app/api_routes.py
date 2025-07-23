# handover_app/api_routes.py
from flask import Blueprint, request, jsonify
from functools import wraps
from .models import User

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- API Key Decorator ---
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                api_key = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Malformed Authorization header. Use 'Bearer <key>'."}), 401
        
        if not api_key:
            return jsonify({"error": "Authorization header is missing or invalid."}), 401
        
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({"error": "Invalid API key."}), 401
        
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/onboard/customer', methods=['POST'])
@api_key_required
def onboard_customer_api():
    """API endpoint to onboard a new customer."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Basic validation (can be expanded)
    required_fields = ['company_name', 'account_manager', 'salesforce_reference']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields", "required": required_fields}), 400

    # For now, just echo back the received data with a success message
    # In the future, this would process and save the data
    response = {
        "message": "Customer onboarding data received successfully.",
        "received_data": data
    }
    return jsonify(response), 201

@api_bp.route('/onboard/supplier', methods=['POST'])
@api_key_required
def onboard_supplier_api():
    """API endpoint to onboard a new supplier."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Basic validation
    required_fields = ['supplier_name', 'ci_type', 'status']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields", "required": required_fields}), 400

    response = {
        "message": "Supplier onboarding data received successfully.",
        "received_data": data
    }
    return jsonify(response), 201