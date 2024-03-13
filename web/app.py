from flask import Flask, jsonify
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
import requests
import yaml, os, time
from uuid import uuid4
from flask import render_template


app = Flask(__name__)

DEPLOYMENT_DIRS = {
    "temp-sensor": "/app/deployments/temp-sensor",
    "hum-sensor": "/app/deployments/hum-sensor",
    "smartlock": "/app/deployments/smartlock",
}


@app.route('/')
def gui():
    return render_template('index.html')


try:
    # Use in-cluster config if available
    config.load_incluster_config()
except ConfigException:
    # Fall back to kubeconfig file
    config.load_kube_config()

k8s_client = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()

@app.route('/namespaces')
def list_namespaces():
    namespaces = k8s_client.list_namespace()
    return jsonify([ns.metadata.name for ns in namespaces.items])

def create_deployment_from_yaml(folder_path, unique_id):
    # Load and apply deployment
    with open(os.path.join(folder_path, "deployment.yaml"), 'r') as file:
        dep = yaml.safe_load(file)
        # Append unique_id to the deployment name
        dep['metadata']['name'] += f"-{unique_id}"
        # Update label selector with unique_id
        dep['spec']['selector']['matchLabels']['app'] += f"-{unique_id}"
        dep['spec']['template']['metadata']['labels']['app'] += f"-{unique_id}"
        apps_v1.create_namespaced_deployment(body=dep, namespace='iot')
    
    
    # Load and apply service
    with open(os.path.join(folder_path, "service.yaml"), 'r') as file:
        svc = yaml.safe_load(file)
        # Append unique_id to the service name
        svc['metadata']['name'] += f"-{unique_id}"
        # Update selector with unique_id
        svc['spec']['selector']['app'] += f"-{unique_id}"
        core_v1.create_namespaced_service(body=svc, namespace='iot')

@app.route('/deploy/<sensor_type>', methods=['POST'])
def deploy_sensor(sensor_type):
    if sensor_type not in DEPLOYMENT_DIRS:
        return jsonify({"error": "Invalid sensor type"}), 400
    
    folder_path = DEPLOYMENT_DIRS[sensor_type]
    unique_id = str(uuid4())[:8]  # Generate a unique identifier

    try:
        create_deployment_from_yaml(folder_path, unique_id)
        return jsonify({"message": f"{sensor_type} deployment and service created successfully with ID: {unique_id}"})
    except Exception as e:
        # Log the full exception
        app.logger.error('Failed to deploy sensor: %s', traceback.format_exc())
        # Respond with error details (be cautious about revealing too much information in production environments)
        return jsonify({"error": "Failed to deploy sensor", "details": str(e)}), 500


@app.route('/devices', methods=['GET'])
def list_devices():
    namespace = 'iot'  # Your namespace
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
    devices = [{"name": dep.metadata.name, "id": dep.metadata.uid} for dep in deployments.items]
    return jsonify(devices)

@app.route('/device/<string:name>', methods=['DELETE'])
def delete_device(name):
    namespace = 'iot'  # Your namespace
    # Attempt to delete the Deployment
    try:
        apps_v1.delete_namespaced_deployment(name=name, namespace=namespace, body=client.V1DeleteOptions())
    except client.rest.ApiException as e:
        return jsonify({"error": f"Failed to delete deployment {name}: {e.reason}"}), e.status
    
    # Attempt to delete the Service
    try:
        core_v1.delete_namespaced_service(name=name, namespace=namespace, body=client.V1DeleteOptions())
    except client.rest.ApiException as e:
        return jsonify({"error": f"Failed to delete service {name}: {e.reason}"}), e.status

    return jsonify({"message": f"Device and its service {name} deleted successfully"})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)