# handover_app/api_routes.py
from flask import Blueprint, request, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/onboard/customer', methods=['POST'])
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