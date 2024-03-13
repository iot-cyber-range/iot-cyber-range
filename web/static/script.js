document.addEventListener('DOMContentLoaded', fetchDevices);

function fetchDevices() {
    fetch('/devices')
        .then(response => response.json())
        .then(devices => {
            const tempSensors = devices.filter(device => device.name.includes('temp-sensor'));
            const humiditySensors = devices.filter(device => device.name.includes('humidity-sensor'));
            const smartlocks = devices.filter(device => device.name.includes('smartlock'));

            document.getElementById('tempSensorsList').innerHTML = createDeviceListHtml(tempSensors, 'temp-sensor');
            document.getElementById('humiditySensorsList').innerHTML = createDeviceListHtml(humiditySensors, 'humidity-sensor');
            document.getElementById('smartlocksList').innerHTML = createDeviceListHtml(smartlocks, 'smartlock');
        })
        .catch(error => console.error('Error fetching devices:', error));
}

function createDeviceListHtml(devices, type) {
    return devices.map(device => `
        <div class="device-item d-flex justify-content-between align-items-center">
            <span>${device.name}</span>
            <button class="btn btn-danger btn-sm" onclick="deleteDevice('${device.name}', '${type}')">Delete</button>
        </div>
    `).join('');
}

function deleteDevice(name) {
    // Assuming the name includes the sensor type and a unique identifier, like 'temp-sensor-xxxx'
    fetch(`/device/${name}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Or handle the response more gracefully
            fetchDevices(); // Refresh the list after deletion
        })
        .catch(error => console.error('Error deleting device:', error));
}

function deploySensor(sensorType) {
    fetch(`/deploy/${sensorType}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        const responseElement = document.getElementById('response');
        responseElement.className = 'alert alert-success';
        responseElement.style.display = 'block';
        responseElement.innerText = data.message;
        fetchDevices();
    })
    .catch(error => {
        console.error('Error:', error);
        const responseElement = document.getElementById('response');
        responseElement.className = 'alert alert-danger';
        responseElement.style.display = 'block';
        responseElement.innerText = 'Error deploying device: ' + error;
    });
}
