from flask import Flask, jsonify, request
from flask_cors import CORS
import json



import os
app = Flask(__name__)
CORS(app)



JSON_DIR = os.path.join(os.path.dirname(__file__), 'json_files')

def read_json_file(filename):
    file_path = os.path.join(os.path.dirname(__file__), f'{filename}.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json_file(filename, data):
    file_path = os.path.join(os.path.dirname(__file__), f'{filename}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def generate_unique_id(settings):
    # Find the maximum existing 'id' value
    if len(settings.get('shellies', [])) > 0:
        max_id = max(device.get('id', 0) for device in settings.get('shellies', []))
        # Increment the maximum 'id' value to generate a new unique 'id'
        return max_id + 1
    else:
        return 1

@app.route('/api/device/<device_id>', methods=['GET'])
def get_device_data(device_id):
    try:
        # Load the current settings
        current_settings = read_json_file("settings")

        # Find the device with the specified ID
        device = None
        for device_info in current_settings.get('shellies', []):
            if device_info.get('id') == device_id:
                device = device_info
                break

        # If the device is found, return its data
        if device:
            name = device.get('name')
            data = read_json_file(name)
            return jsonify(data)

        # If the device is not found, return an error
        return jsonify({"error": "Device not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Error fetching device data: {str(e)}"}), 500



@app.route('/api/settings', methods=['PUT'])
def update_settings():
    try:
        # Get the JSON payload from the POST request
        new_settings = request.json

        # Validate the payload structure, adjust this based on your requirements
        if 'shellies' in new_settings:
            # Update the settings.json file with the new data
            current_settings = read_json_file("settings")

            # Validate each device in the payload
            for new_device in new_settings['shellies']:
                # Validate the device name
                if 'name' not in new_device or not isinstance(new_device['name'], str) or not new_device['name'].strip():
                    return jsonify({"error": "Invalid device name"}), 400

                # Validate the device IP
                if 'ip' not in new_device or not isinstance(new_device['ip'], str) or not new_device['ip'].strip():
                    return jsonify({"error": "Invalid device IP"}), 400

                # Check if a device with the same IP already exists
                existing_device = next((device for device in current_settings['shellies'] if device.get('ip') == new_device['ip']), None)
                if existing_device:
                    # Update the existing device's name
                    existing_device['name'] = new_device['name']
                else:
                    # Generate unique ids for new items
                    if 'id' not in new_device:
                        new_device['id'] = generate_unique_id(current_settings)

                    current_settings['shellies'].append(new_device)

            write_json_file("settings", current_settings)
            return jsonify({"message": "Settings updated successfully"})
        else:
            return jsonify({"error": "Invalid payload structure"}), 400

    except Exception as e:
        return jsonify({"error": f"Error updating settings: {str(e)}"}), 500

@app.route('/api/settings/device/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        # Load the current settings
        current_settings = read_json_file("settings")

        # Find the index of the device with the specified ID
        device_index = None
        for i, device in enumerate(current_settings.get('shellies', [])):
            if device.get('id') == device_id:
                device_index = i
                break

        # If the device is found, remove it
        if device_index is not None:
            del current_settings['shellies'][device_index]

            # Update the settings file
            write_json_file("settings", current_settings)

            return jsonify({"message": "Device deleted successfully"})

        # If the device is not found, return an error
        return jsonify({"error": "Device not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Error deleting device: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True)
