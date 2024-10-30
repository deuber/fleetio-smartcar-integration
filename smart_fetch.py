#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Smartcar API credentials and redirect URI
SMARTCAR_CLIENT_ID = os.getenv("SMARTCAR_CLIENT_ID")
SMARTCAR_CLIENT_SECRET = os.getenv("SMARTCAR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Fleetio API credentials
fleetio_api_token = os.getenv("FLEETIO_API_TOKEN")
fleetio_account_token = os.getenv("FLEETIO_ACCOUNT_TOKEN")

def update_env_file(new_tokens):
    from dotenv import dotenv_values

    env_path = ".env"
    env_vars = dotenv_values(env_path)

    env_vars.update(new_tokens)

    with open(env_path, 'w') as env_file:
        for key, value in env_vars.items():
            env_file.write(f"{key}={value}\n")

def get_smartcar_access_token():
    access_token = os.getenv("SMARTCAR_ACCESS_TOKEN")
    refresh_token = os.getenv("SMARTCAR_REFRESH_TOKEN")

    if access_token:
        test_url = "https://api.smartcar.com/v1.0/vehicles"
        headers = {'Authorization': f'Bearer {access_token}'}
        test_response = requests.get(test_url, headers=headers)

        if test_response.status_code == 200:
            return access_token
        elif refresh_token:
            token_url = "https://auth.smartcar.com/oauth/token"
            token_response = requests.post(
                token_url,
                data={
                    "client_id": SMARTCAR_CLIENT_ID,
                    "client_secret": SMARTCAR_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
            if token_response.status_code == 200:
                token_data = token_response.json()
                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token")

                update_env_file({
                    'SMARTCAR_ACCESS_TOKEN': access_token,
                    'SMARTCAR_REFRESH_TOKEN': refresh_token
                })
                return access_token
            else:
                print("Failed to refresh token.")
        else:
            print("Access token expired and no refresh token available.")

    # Include the 'read_vin' scope in the authorization URL
    auth_url = (
        f"https://connect.smartcar.com/oauth/authorize?response_type=code&client_id={SMARTCAR_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=read_odometer read_vehicle_info read_vin&approval_prompt=force"
    )
    print("Go to the following URL to authorize access:")
    print(auth_url)

    authorization_code = input("Enter the authorization code from the URL: ")

    token_url = "https://auth.smartcar.com/oauth/token"
    token_response = requests.post(
        token_url,
        data={
            "client_id": SMARTCAR_CLIENT_ID,
            "client_secret": SMARTCAR_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        },
    )

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        update_env_file({
            'SMARTCAR_ACCESS_TOKEN': access_token,
            'SMARTCAR_REFRESH_TOKEN': refresh_token
        })
    else:
        print("Error obtaining access token.")
        access_token = None

    return access_token

def get_vehicle_ids(access_token):
    vehicle_list_url = "https://api.smartcar.com/v1.0/vehicles"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(vehicle_list_url, headers=headers)

    if response.status_code == 200:
        try:
            response_json = response.json()
            # Print the full response for debugging
            print("Full Vehicle List Response:", response_json)

            # Directly extract vehicle IDs since they are strings in the list
            vehicle_ids = response_json.get('vehicles', [])
            print("Vehicle IDs:", vehicle_ids)
            return vehicle_ids
        except (KeyError, TypeError) as e:
            print("Error parsing vehicle IDs:", e)
            return []
    else:
        print("Error fetching vehicle IDs:", response.json())
        return []


def fetch_vehicle_details(access_token, vehicle_id):
    headers = {'Authorization': f'Bearer {access_token}'}

    # Fetch basic vehicle details
    vehicle_url = f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}"
    vehicle_response = requests.get(vehicle_url, headers=headers)

    # Fetch the VIN separately
    vin_url = f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}/vin"
    vin_response = requests.get(vin_url, headers=headers)

    # Fetch the odometer reading
    odometer_url = f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}/odometer"
    odometer_response = requests.get(odometer_url, headers=headers)

    if vehicle_response.status_code == 200 and vin_response.status_code == 200 and odometer_response.status_code == 200:
        vehicle_data = vehicle_response.json()
        vin_data = vin_response.json()
        odometer_data = odometer_response.json()

        # Combine the data
        vehicle_data['vin'] = vin_data.get('vin')
        vehicle_data['odometer'] = odometer_data.get('distance')

        # Check unit and convert if necessary
        distance_km = vehicle_data['odometer']
        distance_miles = distance_km / 1.60934  # Convert to miles if in kilometers

        print("Vehicle Details:", vehicle_data)
        print(f"Odometer Reading for {vehicle_data['make']} {vehicle_data['model']} ({vehicle_data['year']}): {distance_miles:.2f} miles")

        return {
            'make': vehicle_data.get('make', 'Unknown Make'),
            'model': vehicle_data.get('model', 'Unknown Model'),
            'year': vehicle_data.get('year', 'Unknown Year'),
            'vin': vehicle_data.get('vin'),
            'mileage': distance_miles  # Include mileage in miles
        }
    else:
        print("Error fetching vehicle details or VIN:")
        if vehicle_response.status_code != 200:
            print("Vehicle Response:", vehicle_response.json())
        if vin_response.status_code != 200:
            print("VIN Response:", vin_response.json())
        if odometer_response.status_code != 200:
            print("Odometer Response:", odometer_response.json())
        return {}

def update_vehicle_vin_in_fleetio(vehicle_id, vin):
    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }
    payload = {'vin': vin}

    response = requests.patch(
        f'https://secure.fleetio.com/api/v1/vehicles/{vehicle_id}',
        headers=fleetio_headers,
        json=payload
    )

    if response.status_code == 200:
        print(f"Updated VIN for vehicle ID {vehicle_id} to {vin}.")
    else:
        try:
            error_info = response.json()
        except ValueError:
            error_info = response.text
        print(f"Error updating VIN for vehicle ID {vehicle_id}: {error_info}")

def find_vehicle_in_fleetio_by_name(vehicle_name):
    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(
        'https://secure.fleetio.com/api/v1/vehicles',
        headers=fleetio_headers,
        params={'q[name_eq]': vehicle_name}
    )

    if response.status_code == 200:
        data = response.json()
        vehicles = data.get('records', [])
        if isinstance(vehicles, list) and vehicles:
            for vehicle in vehicles:
                fleetio_vehicle_name = vehicle.get('name', '').strip().lower()
                search_vehicle_name = vehicle_name.strip().lower()
                if fleetio_vehicle_name == search_vehicle_name:
                    return vehicle.get('id')
        else:
            print(f"No vehicle found in Fleetio with name: {vehicle_name}")
    else:
        try:
            error_info = response.json()
        except ValueError:
            error_info = response.text
        print(f"Error searching Fleetio by name: {response.status_code}, Response: {error_info}")
    return None

def create_or_update_vehicle_in_fleetio(vehicle_data):
    # Ensure all necessary keys are present
    year = vehicle_data.get('year', 'Unknown Year')
    make = vehicle_data.get('make', 'Unknown Make')
    model = vehicle_data.get('model', 'Unknown Model')
    vin = vehicle_data.get('vin', None)

    vehicle_name = f"{year} {make} {model}"
    vehicle_id = None

    if vin:
        # Attempt to find the vehicle in Fleetio by VIN
        print(f"Fetching safety recalls for VIN: {vin}")  # This line can be removed as safety recalls are not needed
        # Since safety recalls are not needed, we can comment out related code
        # vehicle_id = find_vehicle_in_fleetio_by_vin(vin)

        # Instead, find the vehicle by name
        vehicle_id = find_vehicle_in_fleetio_by_name(vehicle_name)
    else:
        # If VIN is not available, find the vehicle by name
        vehicle_id = find_vehicle_in_fleetio_by_name(vehicle_name)

    if vehicle_id:
        print(f"Vehicle '{vehicle_name}' found in Fleetio with ID {vehicle_id}.")
        if vin:
            # Update the VIN in Fleetio
            update_vehicle_vin_in_fleetio(vehicle_id, vin)
    else:
        fleetio_headers = {
            'Authorization': f'Token token={fleetio_api_token}',
            'Account-Token': fleetio_account_token,
            'Content-Type': 'application/json'
        }
        fleetio_payload = {
            'make': make,
            'model': model,
            'year': year,
            'name': vehicle_name,
            'vin': vin,
            'primary_meter_unit': 'mi',
            'vehicle_type_name': 'Vehicle',
            'vehicle_status_name': 'Active'
        }
        print(f"Creating vehicle '{vehicle_name}' in Fleetio.")
        fleetio_response = requests.post(
            'https://secure.fleetio.com/api/v1/vehicles',
            headers=fleetio_headers,
            json=fleetio_payload
        )

        if fleetio_response.status_code == 201:
            vehicle_id = fleetio_response.json().get('id')
            print(f"Vehicle '{vehicle_name}' created successfully in Fleetio with ID {vehicle_id}.")
        else:
            try:
                error_info = fleetio_response.json()
            except ValueError:
                error_info = fleetio_response.text
            print(f"Error creating vehicle '{vehicle_name}' in Fleetio: {error_info}")
            return  # Exit the function if vehicle creation failed

    # Since safety recalls and meter entries are not needed, we can remove related code
    # If you want to keep meter entries, you can implement it with proper error handling

def test_fleetio_authentication():
    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }
    test_response = requests.get(
        'https://secure.fleetio.com/api/v1/vehicles',
        headers=fleetio_headers
    )
    if test_response.status_code == 200:
        print("Fleetio authentication successful.")
    else:
        try:
            error_info = test_response.json()
        except ValueError:
            error_info = test_response.text
        print("Fleetio authentication failed:", error_info)

def main():
    test_fleetio_authentication()

    access_token = get_smartcar_access_token()
    if not access_token:
        print("Failed to obtain access token. Exiting.")
        return

    vehicle_ids = get_vehicle_ids(access_token)

    for vehicle_id in vehicle_ids:
        vehicle_data = fetch_vehicle_details(access_token, vehicle_id)
        if not vehicle_data:
            print(f"Skipping vehicle ID {vehicle_id} due to missing data.")
            continue
        create_or_update_vehicle_in_fleetio(vehicle_data)

if __name__ == "__main__":
    main()
