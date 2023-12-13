from flask import Flask, jsonify
from flask_cors import CORS
import json



app = Flask(__name__)
CORS(app)

JSON_FILE = "shellyReadings.json"

def read_json_file():
    with open(JSON_FILE, 'r') as file:
        data = json.load(file)
    return data

@app.route('/api', methods=['GET'])
def get_data():
   
    data = read_json_file()
    return jsonify(data)

    

if __name__ == '__main__':
    app.run()
