from flask import Flask, jsonify
from flask_cors import CORS
import json


import os
app = Flask(__name__)
CORS(app)

JSON_FILE = os.path.join(os.path.dirname(__file__), 'shelly.json')

def read_json_file():
    with open(JSON_FILE, 'r') as file:
        data = json.load(file)
    return data


def read_settings():
    with open('settings.json', 'r') as file:
        settings = json.load(file)
        return settings

@app.route('/api', methods=['GET'])
def get_data():
   
    data = read_json_file()
    return jsonify(data)

    

if __name__ == '__main__':
    app.run()
