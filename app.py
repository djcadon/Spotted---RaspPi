from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from DB_config import cur
from ranger import setup_sensor, occupied

occupied = False
verified = False
ID = None

lot_info = {'time_stamp':datetime.now(timezone.utc),
            'id':ID,
            'reservation_id':'',
            'is_verified':verified,
            'is_occupied': occupied
            }

violation = {
            'id':ID,
            'time_stamp':datetime.now(timezone.utc),
            'violation':''
            }

confirmation = {
                'reservation_id':'',
                'time_stamp':datetime.now(timezone.utc),
                'code':''
                }



app = Flask(__name__)
@app.before_request
def config():
    setup_sensor()
    pass

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_code():
    code = request.get_json()
    cur.execute()
    rows = cur.fetchall()

    # Replace with your real API call
    print(f"Received code: {code}")
    # response = requests.post("https://example.com/api/verify_code", json={"code": code})

    return jsonify(success=True, message="Code submitted")

@app.route('/submit', methods=['GET'])
def submit_code():
    return
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
