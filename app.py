from flask import Flask, jsonify, request
from flask_cors import CORS
import json



import os
app = Flask(__name__)
CORS(app)



JSON_DIR = os.path.join(os.path.dirname(__file__), 'json_files')

def read_json_file(filename):
    file_path = os.path.join(f'{filename}.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json_file(data):
    with open('settings.json', 'w') as file:
        json.dump(data, file, indent=2)

def generate_unique_id(settings):
    # Find the maximum existing 'id' value
    if len(settings.get('shellies', [])) > 0:
        max_id = max(device.get('id', 0) for device in settings.get('shellies', []))
        # Increment the maximum 'id' value to generate a new unique 'id'
        return max_id + 1
    else:
        return 1

@app.route('/api/<name>', methods=['GET'])
def get_data(name):
    try:
        data = read_json_file(name)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        # Get the JSON payload from the POST request
        new_settings = request.json

        # Validate the payload structure, adjust this based on your requirements
        if 'shellies' in new_settings:
            # Update the settings.json file with the new data
            current_settings = read_json_file("settings")

            # Generate unique ids for new items
            for new_device in new_settings['shellies']:
                if 'id' not in new_device:
                    new_device['id'] = generate_unique_id(current_settings)

            current_settings['shellies'] = new_settings['shellies']
            write_json_file(current_settings)

            return jsonify({"message": "Settings updated successfully"})
        else:
            return jsonify({"error": "Invalid payload structure"}), 400

    except Exception as e:
        return jsonify({"error": f"Error updating settings: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
