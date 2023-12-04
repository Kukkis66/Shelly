from flask import Flask, jsonify
import json
import subprocess


app = Flask(__name__)


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
    app.run(debug=True)
