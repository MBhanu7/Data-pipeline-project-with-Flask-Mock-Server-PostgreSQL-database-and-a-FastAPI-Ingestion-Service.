from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    data = load_data()
    
    total = len(data)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    return jsonify({
        "data": data[start_idx:end_idx],
        "total": total,
        "page": page,
        "limit": limit
    })

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    data = load_data()
    customer = next((c for c in data if c["customer_id"] == customer_id), None)
    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404