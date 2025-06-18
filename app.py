from datetime import datetime
from flask import Flask, render_template, request, jsonify
import requests  # For forwarding the code to your API

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_code', methods=['POST'])
def submit_code():
    data = request.get_json()
    code = data.get('code')

    # Replace with your real API call
    print(f"Received code: {code}")
    # response = requests.post("https://example.com/api/verify_code", json={"code": code})

    return jsonify(success=True, message="Code submitted")

occupied = False
ID = None

lot_info = {'id':ID,
            #'time_stamp':datetime.datetime.now(datetime.UTC),
            'occupied': occupied
            }

violation = {
    'id':ID,
    #'time_stamp':datetime.datetime.now(datetime.UTC),
    'violation':''
    }

confirmation = {
    'reservation_id':'',
    #'time_stamp':datetime.datetime.now(datetime.UTC),
    'code':''
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
