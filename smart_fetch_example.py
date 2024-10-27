import requests

# Step 1: Fetch mileage from Toyota (using Smartcar API)
smartcar_access_token = 'your_smartcar_access_token'
vehicle_id = 'your_vehicle_id'

headers = {
    'Authorization': f'Bearer {smartcar_access_token}'
}

# Make request to Smartcar API
smartcar_response = requests.get(f'https://api.smartcar.com/v1.0/vehicles/{vehicle_id}/odometer', headers=headers)
mileage_data = smartcar_response.json()['data']['odometer']

# Step 2: Update mileage in Fleetio
fleetio_api_token = 'your_fleetio_api_token'
fleetio_vehicle_id = 'your_fleetio_vehicle_id'
fleetio_headers = {
    'Authorization': f'Token {fleetio_api_token}',
    'Content-Type': 'application/json'
}

fleetio_payload = {
    'odometer_reading': mileage_data
}

fleetio_response = requests.post(f'https://api.fleetio.com/v1/vehicles/{fleetio_vehicle_id}/update_odometer', headers=fleetio_headers, json=fleetio_payload)

print(fleetio_response.status_code)  # 200 means success
