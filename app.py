from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from DB_config import cur, conn
from config import RASP_ID
from ranger import setup_sensor, check_occupied, cleanup_sensor
import threading
import atexit
import time
#Global Config
#Get parking spot owner id
def get_owner_id():
    cur.execute("""
        SELECT * FROM parkings
        WHERE id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (RASP_ID,))
    parking = cur.fetchone()
    if parking is None:
        exit(1)
    return parking['owner_id']
owner_id = get_owner_id()

#Thread function for checking occupancy and validation of parking spot
def monitor_sensor_loop():
    active_reservation = False
    reservation_end_time = None
    while True:
        now = datetime.now(timezone.utc)
        #Parking spot is occupied
        if check_occupied():
            #Checking if reservation is verfied already
            if active_reservation:
                if now > reservation_end_time:
                    active_reservation = False
                time.sleep(10)
                continue
            #Main check for reservation
            else:
                renter_id = None
                reservation_id = None
                #Finding if there is an active reservation
                cur.execute("""
                    SELECT * FROM reservations
                    WHERE parking_id = %s
                    AND start_time <= %s
                    AND end_time >= %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (RASP_ID, now, now))
                reservation = cur.fetchone()
                #No active reservation, check if violation
                if reservation is None:
                    check_violation(owner_id, renter_id, reservation_id, active_reservation)
                    continue
                #Active reservation, check if validated
                else:
                    is_verified = reservation['is_verified']
                    reservation_end_time = reservation['end_time']
                    renter_id = reservation['renter_id']
                    reservation_id = reservation['id']
                    if is_verified:
                        active_reservation = True
                    else:
                        check_violation(owner_id, renter_id, reservation_id, active_reservation)
        #Sleep for a while because spot is empty
        else:
            time.sleep(10)

#Violation checking and sending to database
def check_violation(owner_id, renter_id, reservation_id, active_reservation):
    duration = 60  # seconds
    #Determining type of violation
    if active_reservation:
        violation_type = 'UNVERIFIED'
    else:
        violation_type = 'UNAUTHORIZED'
    #Violation check loop
    for _ in range(duration // 5):
        #Object has moved
        if not check_occupied():
            return 
        time.sleep(5)
    #Send violation 
    cur.execute("""
        INSERT INTO violations
        (parking_id, owner_id, renter_id, reservation_id, type)
        VALUES
        (%s, %s, %s, %s, %s)
    """, (RASP_ID, owner_id, renter_id, reservation_id,violation_type))
    conn.commit()

#APP
app = Flask(__name__)
#Touchscreen Frontend for Pi
@app.route('/')
def home():
    return render_template('index.html')
#POST method for verification code
@app.route('/submit', methods=['POST'])
def submit_code():
    data = request.get_json()
    user_code = data.get('code')
    if len(user_code) != 4:
        return jsonify(success=False, message="Code must be exactly 4 digits"), 400
    now = datetime.now(timezone.utc)
    print(now)
    #Finding if there is an active reservation
    cur.execute("""
        SELECT * FROM reservations
        WHERE parking_id = %s
        AND start_time <= %s
        AND end_time >= %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (RASP_ID, now, now))
    reservation = cur.fetchone()
    print(reservation) #Uncomment to check reservation data
    if reservation is None:
        return jsonify(success=False, message="No active reservation found"), 404
    reservation_id = reservation['id']
    #Finding auth code for reservation
    cur.execute("""
        SELECT auth_code FROM parking_authentication
        WHERE reservation_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (reservation_id,))
    auth_row = cur.fetchone()
    print(auth_row) #Uncomment to check parking_authentication
    #No active reservation
    if auth_row is None:
        return jsonify(success=False, message="No auth code found for this reservation"), 404
    expected_code = str(auth_row['auth_code'])
    #Auth code is correct for reservation
    if user_code == expected_code:
        #Updating verification
        cur.execute("""
            UPDATE reservations
            SET is_verified = TRUE
            WHERE id = %s
        """, (reservation_id,))
        conn.commit()
        return jsonify(success=True, message="Code verified successfully")
    #Auth code is incorrect for reservation
    #Auth code is incorrect for reservation
    else:
        return jsonify(success=False, message="Invalid code"), 401

#Shutdown Cleanup 
@atexit.register
def shutdown():
    print("Flask is shutting down...")
    cleanup_sensor()

#MAIN
if __name__ == '__main__':
    setup_sensor()
    threading.Thread(target=monitor_sensor_loop, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)



