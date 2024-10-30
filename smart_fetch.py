#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Smartcar and Fleetio API credentials
SMARTCAR_CLIENT_ID = os.getenv("SMARTCAR_CLIENT_ID")
SMARTCAR_CLIENT_SECRET = os.getenv("SMARTCAR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FLEETIO_API_TOKEN = os.getenv("FLEETIO_API_TOKEN")
FLEETIO_ACCOUNT_TOKEN = os.getenv("FLEETIO_ACCOUNT_TOKEN")


def update_env_file(new_tokens):
    """
    Updates the .env file with new token values.
    """
    from dotenv import dotenv_values
    env_path = ".env"
    env_vars = dotenv_values(env_path)
    env_vars.update(new_tokens)

    with open(env_path, 'w') as env_file:
        for key, value in env_vars.items():
            env_file.write(f"{key}={value}\n")


def get_smartcar_access_token():
    """
    Retrieves a valid Smartcar access token, refreshing it if necessary.
    """
    access_token = os.getenv("SMARTCAR_ACCESS_TOKEN")
    refresh_token = os.getenv("SMARTCAR_REFRESH_TOKEN")
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        if requests.get("https://api.smartcar.com/v1.0/vehicles", headers=headers).status_code == 200:
            return access_token
        elif refresh_token:
            token_response = requests.post(
                "https://auth.smartcar.com/oauth/token",
                data={
                    "client_id": SMARTCAR_CLIENT_ID,
                    "client_secret": SMARTCAR_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
            if token_response.status_code == 200:
                token_data = token_response.json()
                update_env_file({
                    'SMARTCAR_ACCESS_TOKEN': token_data.get("access_token"),
                    'SMARTCAR_REFRESH_TOKEN': token_data.get("refresh_token")
                })
                return token_data.get("access_token")
            else:
                print("Failed to refresh Smartcar token.")
        else:
            print("Access token expired and no refresh token available.")
    else:
        print("No Smartcar access token found.")
    return None


def get_vehicle_ids(access_token):
    """
    Retrieves a list of vehicle IDs associated with the Smartcar access token.
    """
    response = requests.get(
        "https://api.smartcar.com/v1.0/vehicles",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if response.status_code == 200:
        return response.json().get('vehicles', [])
    else:
        print(f"Failed to fetch vehicles from Smartcar: {response.status_code} - {response.text}")
        return []


def fetch_vehicle_details(access_token, vehicle_id):
    """
    Fetches vehicle details including VIN and odometer reading.
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Fetch basic vehicle data
    vehicle_response = requests.get(f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}", headers=headers)
    if vehicle_response.status_code != 200:
        print(f"Failed to fetch vehicle data for ID {vehicle_id}: {vehicle_response.status_code} - {vehicle_response.text}")
        return None
    vehicle_data = vehicle_response.json()
    
    # Fetch VIN
    vin_response = requests.get(f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}/vin", headers=headers)
    if vin_response.status_code != 200:
        print(f"Failed to fetch VIN for vehicle ID {vehicle_id}: {vin_response.status_code} - {vin_response.text}")
        return None
    vin_data = vin_response.json()
    vehicle_data['vin'] = vin_data.get('vin')
    
    # Fetch odometer data
    odometer_response = requests.get(f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}/odometer", headers=headers)
    if odometer_response.status_code != 200:
        print(f"Failed to fetch odometer for vehicle ID {vehicle_id}: {odometer_response.status_code} - {odometer_response.text}")
        distance_km = 0
    else:
        odometer_data = odometer_response.json()
        distance_km = odometer_data.get('distance', 0)
    
    mileage = distance_km / 1.60934  # Convert to miles if distance is in kilometers
    vehicle_data['mileage'] = mileage

    make = vehicle_data.get('make', 'Unknown Make')
    model = vehicle_data.get('model', 'Unknown Model')
    year = vehicle_data.get('year', 'Unknown Year')
    
    print(f"Odometer for {make} {model} ({year}): {mileage:.2f} miles")
    
    return {
        'make': make,
        'model': model,
        'year': year,
        'vin': vehicle_data.get('vin'),
        'mileage': mileage
    }


def find_vehicle_in_fleetio_by_vin(vin):
    """
    Searches for a vehicle in Fleetio by VIN.
    """
    fleetio_headers = {
        'Authorization': f'Token token={FLEETIO_API_TOKEN}',
        'Account-Token': FLEETIO_ACCOUNT_TOKEN,
        'Content-Type': 'application/json'
    }
    response = requests.get(
        'https://secure.fleetio.com/api/v1/vehicles',
        headers=fleetio_headers,
        params={'q[vin_eq]': vin}
    )

    if response.status_code == 200:
        vehicles = response.json().get('records', [])
        if vehicles:
            vehicle_id = vehicles[0].get('id')
            print(f"Found vehicle in Fleetio with VIN '{vin}' and ID {vehicle_id}.")
            return vehicle_id
        else:
            print(f"No vehicle found in Fleetio with VIN: {vin}")
    else:
        print(f"Error searching for vehicle by VIN '{vin}': {response.status_code} - {response.text}")
    return None


def verify_vehicle_exists(vehicle_id):
    """
    Verifies that a vehicle with the given ID exists in Fleetio.
    """
    fleetio_headers = {
        'Authorization': f'Token token={FLEETIO_API_TOKEN}',
        'Account-Token': FLEETIO_ACCOUNT_TOKEN,
        'Content-Type': 'application/json'
    }
    response = requests.get(
        f'https://secure.fleetio.com/api/v1/vehicles/{vehicle_id}',
        headers=fleetio_headers
    )
    if response.status_code == 200:
        print(f"Vehicle ID {vehicle_id} exists in Fleetio.")
        return True
    else:
        print(f"Vehicle ID {vehicle_id} does not exist: {response.status_code} - {response.text}")
        return False


def create_vehicle_meter_entry_in_fleetio(vehicle_id, mileage, meter_type=None):
    """
    Creates a meter entry for a vehicle in Fleetio.
    """
    fleetio_headers = {
        'Authorization': f'Token token={FLEETIO_API_TOKEN}',
        'Account-Token': FLEETIO_ACCOUNT_TOKEN,
        'Content-Type': 'application/json'
    }
    payload = {
        'vehicle_id': vehicle_id,
        'value': mileage,  
        'date': datetime.now().isoformat()
    }
    
    if meter_type == 'secondary':
        payload['meter_type'] = 'secondary'

    print(f"Creating meter entry for vehicle ID {vehicle_id} with mileage {mileage:.2f} miles.")
    response = requests.post(
        'https://secure.fleetio.com/api/v1/meter_entries', 
        headers=fleetio_headers,
        json=payload
    )

    if response.status_code == 201:
        print(f"Successfully created meter entry for vehicle ID {vehicle_id} with mileage {mileage:.2f} miles.")
    else:
        print(f"Error creating meter entry for vehicle ID {vehicle_id}: {response.status_code} - {response.text}")


def create_or_update_vehicle_in_fleetio(vehicle_data):
    """
    Creates a new vehicle in Fleetio or updates an existing one, then creates a meter entry.
    """
    vin = vehicle_data['vin']
    if not vin:
        print("VIN is missing. Skipping vehicle.")
        return

    vehicle_id = find_vehicle_in_fleetio_by_vin(vin)

    if vehicle_id:
        print(f"Vehicle with VIN '{vin}' found in Fleetio with ID {vehicle_id}.")
        if verify_vehicle_exists(vehicle_id):
            create_vehicle_meter_entry_in_fleetio(vehicle_id, vehicle_data['mileage'])
    else:
        fleetio_headers = {
            'Authorization': f'Token token={FLEETIO_API_TOKEN}',
            'Account-Token': FLEETIO_ACCOUNT_TOKEN,
            'Content-Type': 'application/json'
        }
        fleetio_payload = {
            'make': vehicle_data['make'],
            'model': vehicle_data['model'],
            'year': vehicle_data['year'],
            'name': f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}",
            'vin': vin,
            'primary_meter_unit': 'mi',
            'vehicle_type_name': 'Vehicle',
            'vehicle_status_name': 'Active'
        }

        response = requests.post(
            'https://secure.fleetio.com/api/v1/vehicles',
            headers=fleetio_headers,
            json=fleetio_payload
        )

        if response.status_code == 201:
            new_vehicle_id = response.json().get('id')
            print(f"Vehicle '{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}' created in Fleetio with ID {new_vehicle_id}.")
            create_vehicle_meter_entry_in_fleetio(new_vehicle_id, vehicle_data['mileage'])
        else:
            print(f"Error creating vehicle in Fleetio with VIN '{vin}': {response.status_code} - {response.text}")


def main():
    """
    Main function to execute the Smartcar to Fleetio data synchronization.
    """
    access_token = get_smartcar_access_token()
    if not access_token:
        print("Failed to obtain Smartcar access token.")
        return

    vehicle_ids = get_vehicle_ids(access_token)
    if not vehicle_ids:
        print("No vehicles found in Smartcar account.")
        return

    for vehicle_id in vehicle_ids:
        vehicle_data = fetch_vehicle_details(access_token, vehicle_id)
        if vehicle_data:
            create_or_update_vehicle_in_fleetio(vehicle_data)


if __name__ == "__main__":
    main()
