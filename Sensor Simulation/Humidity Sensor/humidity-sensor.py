from flask import Flask, jsonify
import threading
import random
import time

app = Flask(__name__)

current_humidity = 50

def generate_humidity():
    global current_humidity
    while True:
        current_humidity = float(50 + random.normalvariate(0, 5))
        print(f"Current humidity: {current_humidity:.2f}%")
        time.sleep(10)  

@app.route('/humidity', methods=['GET'])
def get_humidity():
    global current_humidity
    return jsonify({'humidity': current_humidity})

if __name__ == '__main__':
    humidity_thread = threading.Thread(target=generate_humidity)
    humidity_thread.daemon = True
    humidity_thread.start()

    app.run(host='0.0.0.0', port=5000)  
