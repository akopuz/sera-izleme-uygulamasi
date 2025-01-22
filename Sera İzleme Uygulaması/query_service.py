from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client['sensor_network']
data_collection = db['sensor_values']

@app.route('/api/query-data', methods=['POST'])
def query_data():
    try:
        query_params = request.get_json()
        print(f"Received query params: {query_params}")

        if not all(key in query_params for key in ('start_time', 'end_time', 'parameter')):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        start_time = query_params['start_time']
        end_time = query_params['end_time']
        parameter = query_params['parameter']

        start_time += ":00.000+00:00"
        end_time += ":00.000+00:00"
        print(start_time)
        print(end_time)


        start_time_dt = datetime.fromisoformat(str(start_time)).replace(tzinfo=pytz.UTC)
        end_time_dt = datetime.fromisoformat(str(end_time)).replace(tzinfo=pytz.UTC)

        
        query = {
            "timestamp": {"$gte": start_time_dt, "$lte": end_time_dt},
            parameter: {"$exists": True}
        }

        print(query)

        results = list(data_collection.find(query, {"_id": 0, "timestamp": 1, parameter: 1}))

        print(f"Query results: {results}")

        return jsonify({"success": True, "data": results}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5006)
