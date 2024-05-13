from flask import Flask, render_template
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from flask_socketio import SocketIO, emit
import requests
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

NAMESPACE = 'iot'

def list_services(namespace):
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    
    v1 = client.CoreV1Api()
    print(f"Listing services in the namespace: {namespace}")
    services = v1.list_namespaced_service(namespace)
    
    categorized_services = {"humidity_sensors": [], "smartlocks": [], "temp_sensors": []}
    
    for service in services.items:
        name = service.metadata.name
        if service.spec.cluster_ip not in ["None", None]:
            if "humidity-sensor" in name:
                categorized_services["humidity_sensors"].append((name, service.spec.cluster_ip))
            elif "smartlock" in name:
                categorized_services["smartlocks"].append((name, service.spec.cluster_ip))
            elif "temp-sensor" in name:
                categorized_services["temp_sensors"].append((name, service.spec.cluster_ip))

    return categorized_services

def simulate_traffic(categorized_services):
    endpoints = {"humidity_sensors": "/humidity", "smartlocks": "/lock", "temp_sensors": "/temperature"}
    
    new_responses = {"humidity_sensors": [], "smartlocks": [], "temp_sensors": []}
    
    for category, services in categorized_services.items():
        for service_name, ip in services:
            url = f"http://{ip}{endpoints[category]}"
            try:
                response = requests.get(url, timeout=5)
                new_responses[category].append({
                    "name": service_name,
                    "ip": ip,
                    "status": response.status_code,
                    "data": response.text
                })
            except requests.exceptions.RequestException as e:
                new_responses[category].append({
                    "name": service_name,
                    "ip": ip,
                    "error": str(e)
                })
    
    return new_responses

def update_responses_periodically():
    while True:
        categorized_services = list_services(NAMESPACE)
        responses = simulate_traffic(categorized_services)
        socketio.emit('update', {'responses': responses})
        time.sleep(30)

@socketio.on('connect')
def handle_connect():
    # Call the function to get the current state of devices
    categorized_services = list_services(NAMESPACE)
    current_responses = simulate_traffic(categorized_services)
    emit('update', {'responses': current_responses})

@app.route('/')
def home():
    categorized_services = list_services(NAMESPACE)
    responses = simulate_traffic(categorized_services)
    # No need to pass 'responses' to the template if you're using Socket.IO for updates
    return render_template('index.html')

if __name__ == "__main__":
    updater_thread = threading.Thread(target=update_responses_periodically, daemon=True)
    updater_thread.start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
