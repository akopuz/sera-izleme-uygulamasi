from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
app = Flask(__name__)

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client['sensor_network']
rules_collection = db['rules']

CORS(app, resources={r"/api/*": {"origins": "*"}}) 
@app.route('/api/rules', methods=['POST'])
def save_rule():
    try:
        print(request.get_json())
        rule_data = request.get_json()

        if not all(key in rule_data for key in ('email', 'parameter', 'condition', 'value')):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        existing_rule = rules_collection.find_one({'parameter': rule_data['parameter']})

        if existing_rule:

            result = rules_collection.update_one(
                {'_id': existing_rule['_id']}, 
                {'$set': {
                    'email': rule_data['email'],
                    'condition': rule_data['condition'],
                    'value': float(rule_data['value'])
                }}
            )
            return jsonify({
                "success": True,
                "message": "Rule updated",
                "rule_id": str(existing_rule['_id'])
            }), 200
        else:

            rule = {
                'email': rule_data['email'],
                'parameter': rule_data['parameter'],
                'condition': rule_data['condition'],
                'value': float(rule_data['value'])
            }
            result = rules_collection.insert_one(rule)
            return jsonify({
                "success": True,
                "message": "Rule saved",
                "rule_id": str(result.inserted_id)
            }), 201

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)







