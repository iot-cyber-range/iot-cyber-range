from flask import Flask, render_template
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
import requests
import threading
import time

app = Flask(__name__)

responses = []

NAMESPACE = 'iot'

def list_services(namespace):
    try:
        # Try to load in-cluster configuration first
        config.load_incluster_config()
    except ConfigException:
        # Fall back to kube-config file for local development
        config.load_kube_config()
    
    v1 = client.CoreV1Api()
    print(f"Listing services in the namespace: {namespace}")
    services = v1.list_namespaced_service(namespace)
    
    categorized_services = {
        "humidity_sensors": [],
        "smartlocks": [],
        "temp_sensors": []
    }
    
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
    endpoints = {
        "humidity_sensors": "/humidity",
        "smartlocks": "/lock",
        "temp_sensors": "/temperature"
    }
    
    # Initialize an empty list for the new set of responses
    new_responses = []
    
    for category, services in categorized_services.items():
        for service_name, ip in services:
            url = f"http://{ip}{endpoints[category]}"
            try:
                response = requests.get(url, timeout=5)
                new_responses.append(f"Response from {service_name} ({ip}): Status code {response.status_code}")
            except requests.exceptions.RequestException as e:
                new_responses.append(f"Request to {service_name} ({ip}) failed: {e}")
    
    # Return the new set of responses
    return new_responses



def update_responses_periodically():
    global responses
    while True:
        categorized_services = list_services(NAMESPACE)
        # Overwrite the global responses with the latest results
        responses = simulate_traffic(categorized_services)
        time.sleep(30)  # Sleep for 30 seconds

@app.route('/')
def home():
    return render_template('index.html', responses=responses)

if __name__ == "__main__":
    updater_thread = threading.Thread(target=update_responses_periodically)
    updater_thread.start()
    app.run(host='0.0.0.0', port=5000)