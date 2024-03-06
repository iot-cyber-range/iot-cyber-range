from flask import Flask, jsonify, request
import threading
import random
import time

app = Flask(__name__)

lock_status = "locked"

def change_lock_status():
    global lock_status
    while True:
        # Randomly toggle the lock status for simulation
        lock_status = "unlocked" if lock_status == "locked" else "locked"
        print(f"Lock status: {lock_status}")
        time.sleep(random.randint(5, 15))  # Change status at random intervals

@app.route('/lock', methods=['GET', 'POST'])
def get_or_set_lock():
    global lock_status
    if request.method == 'POST':
        requested_status = request.json.get('status', '')
        if requested_status in ["locked", "unlocked"]:
            lock_status = requested_status
            return jsonify({'status': lock_status}), 200
        else:
            return jsonify({'error': 'Invalid status'}), 400
    return jsonify({'status': lock_status})

if __name__ == '__main__':
    lock_status_thread = threading.Thread(target=change_lock_status)
    lock_status_thread.daemon = True
    lock_status_thread.start()

    app.run(host='0.0.0.0', port=5000)