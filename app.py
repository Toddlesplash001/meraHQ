from flask import Flask, request, jsonify
from script import extract_workspace_details, send_workspace_email
from flask_cors import CORS
import requests
import json
import pandas as pd
app = Flask(__name__)

# Enable CORS on /run-model with all origins (for development)
CORS(app, resources={r"/run-model": {"origins": "*"}}, supports_credentials=True)

@app.route('/run-model', methods=['POST', 'OPTIONS'])
def handle_model_input():
    # Handle preflight request
    if request.method == 'OPTIONS':
        # Allow the preflight to succeed
        return jsonify({'status': 'ok'}), 200

    try:
        input_data = request.get_json()
        # print("Received data:", input_data)

        # Call myHQ API
        url = "https://api.web.myhq.in/meeting-room/web/list-slug"
        try:
            # print(input_data)
            response = requests.post(url, json=input_data['request'])
            response.raise_for_status()
            response_data = response.json()
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            return jsonify({'status': 'error', 'message': 'API request failed'}), 500
        except json.JSONDecodeError:
            print("Failed to parse response JSON")
            return jsonify({'status': 'error', 'message': 'Invalid JSON response'}), 500

        # Process response through your model
        # print("response_data: ",response_data,"\n")
        results = extract_workspace_details(response_data, input_data['request'], int(input_data["count"]))
        # print("results: ",results)
        # Send email
        sender_email = "ayaan.gautam@myhq.in"
        receiver_email = input_data['receiverEmail']
        cc_email = input_data['ccEmail']
        app_password = 'jmzq bmmu jhmo aviw'  # Make sure to hide this in prod
        timings = "10:00 AM to 5:00 PM"
        send_workspace_email(results, input_data["name"],sender_email, receiver_email, input_data["request"], app_password, timings, cc_email)

        return jsonify({'status': 'success'})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)
