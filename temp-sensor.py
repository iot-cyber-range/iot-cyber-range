import time
from random import normalvariate
from flask import Flask, jsonify
import threading

app = Flask(__name__)

# Global variable to store the current temperature
current_temperature = 20.1

def generate_temperature():
    global current_temperature
    while True:
        # Generate a random temperature around 20°C with a standard deviation of 1
        current_temperature = 20 + normalvariate(0, 1)
        print(f"Current temperature: {current_temperature:.2f}°C")
        time.sleep(10)  # Update temperature every 10 seconds

@app.route('/temperature', methods=['GET'])
def get_temperature():
    return jsonify({'temperature': current_temperature})

if __name__ == '__main__':
    # Create and start a background thread for temperature generation
    temperature_thread = threading.Thread(target=generate_temperature)
    temperature_thread.daemon = True
    temperature_thread.start()

    # Start the Flask application
    app.run(host='0.0.0.0', port=5000)
