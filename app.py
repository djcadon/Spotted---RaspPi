from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from DB_config import cur
#from ranger import setup_sensor, check_occupied() cleanup_sensor
import threading
import atexit
import time

raspberry_id = 1

def monitor_sensor_loop():
    while True():
        #Parking spot is occupied
        if check_occupied():
            now = datetime.now(timezone.utc)
            cur.execute("""
                SELECT * FROM reservations
                WHERE parking_id = %s
                    AND start_time <= %s
                    AND end_time >= %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (raspberry_id, now, now))
            row = cur.fetchone()
            #Possible violation has taken place
            if row == None:
                print (jsonify({'message': 'No user found with this email'}))
            print (f'Database Response:{row}')
        #Parking spot is empty and can 
        else:
            time.sleep(5)

app = Flask(__name__)
#Touchscreen Frontend for Pi
@app.route('/')
def home():
    return render_template('index.html')

#POST method for verification code
@app.route('/submit', methods=['POST'])
def submit_code():
    code = request.get_json() #Getting code from screen
    print(f"Received code: {code}")
    cur.execute('SELECT * FROM reservations ORDER BY id DESC LIMIT 1')
    rows = cur.fetchall()
    if len(rows) == 0:
        print (jsonify({'message': 'No user found with this email'}))
    print (f'Database Response:{rows}')
    
    return jsonify(success=True, message="Code submitted")

#Shutdown Cleanup 
@atexit.register
def shutdown():
    print("Flask is shutting down...")
    #cleanup_sensor()

#MAIN RUN
if __name__ == '__main__':
    #setup_sensor()
    #threading.Thread(target=monitor_sensor_loop, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)



