#!/usr/bin/env python3

import os
import smartcar
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Smartcar API credentials and redirect URI
SMARTCAR_CLIENT_ID = os.getenv("SMARTCAR_CLIENT_ID")
SMARTCAR_CLIENT_SECRET = os.getenv("SMARTCAR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Fleetio API credentials
fleetio_api_token = os.getenv("FLEETIO_API_TOKEN")
fleetio_account_token = os.getenv("FLEETIO_ACCOUNT_TOKEN")

# Create a new Smartcar AuthClient
client = smartcar.AuthClient(
    client_id=SMARTCAR_CLIENT_ID,
    client_secret=SMARTCAR_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    test_mode=False  # Set to True if using Smartcar test mode
)

def update_env_file(new_tokens):
    from dotenv import dotenv_values

    env_path = ".env"
    env_vars = dotenv_values(env_path)

    env_vars.update(new_tokens)

    with open(env_path, 'w') as env_file:
        for key, value in env_vars.items():
            env_file.write(f"{key}={value}\n")

def get_smartcar_access():
    access_token = os.getenv("SMARTCAR_ACCESS_TOKEN_SDK")
    refresh_token = os.getenv("SMARTCAR_REFRESH_TOKEN_SDK")

    if access_token:
        # Test if the access token is still valid using the SDK
        try:
            vehicles_response = smartcar.get_vehicles(access_token)
            return {'access_token': access_token, 'refresh_token': refresh_token}
        except smartcar.AuthAuthenticationError:
            # Token expired or invalid, refresh it using the SDK
            if refresh_token:
                try:
                    new_access = client.exchange_refresh_token(refresh_token)
                    access_token = new_access.access_token
                    refresh_token = new_access.refresh_token

                    update_env_file({
                        'SMARTCAR_ACCESS_TOKEN_SDK': access_token,
                        'SMARTCAR_REFRESH_TOKEN_SDK': refresh_token
                    })

                    return {'access_token': access_token, 'refresh_token': refresh_token}
                except smartcar.SmartcarException as ex:
                    print("Failed to refresh token:")
                    print(f"Code: {ex.code}, Message: {ex.message}")
                    return None
            else:
                print("Access token expired and no refresh token available.")
                return None
        except smartcar.SmartcarException as e:
            print(f"Error validating access token: Code: {e.code}, Message: {e.message}")
            return None

    # If we don't have an access token, start the OAuth flow using the SDK
    auth_url = client.get_auth_url(
        scope=['read_vehicle_info', 'read_odometer', 'read_vin']
        # Removed 'force=True' to fix the TypeError
    )

    print("Go to the following URL to authorize access:")
    print(auth_url)

    authorization_code = input("Enter the authorization code from the URL: ")

    try:
        # Exchange the authorization code for an access token using the SDK
        access = client.exchange_code(authorization_code)
        print("Type of access:", type(access))
        print("Value of access:", access)

        # Access the tokens directly from the Access object
        access_token = access.access_token
        refresh_token = access.refresh_token

        update_env_file({
            'SMARTCAR_ACCESS_TOKEN_SDK': access_token,
            'SMARTCAR_REFRESH_TOKEN_SDK': refresh_token
        })

        return {'access_token': access_token, 'refresh_token': refresh_token}
    except smartcar.SmartcarException as e:
        print("Error obtaining access token:")
        print(f"Code: {e.code}, Message: {e.message}")
        return None

def get_vehicle_ids(access_token):
    try:
        # Use the SDK to get vehicle IDs
        response = smartcar.get_vehicles(access_token)
        vehicle_ids = response.vehicles
        print("Vehicle IDs:", vehicle_ids)
        return vehicle_ids
    except smartcar.SmartcarException as e:
        print("Error fetching vehicle IDs:")
        print(f"Code: {e.code}, Message: {e.message}")
        return []

def fetch_vehicle_details(access_token, vehicle_id):
    # Use the SDK's Vehicle class to interact with the vehicle
    vehicle = smartcar.Vehicle(vehicle_id, access_token)

    try:
        # Fetch basic vehicle details using the SDK
        info = vehicle.attributes()
        # Fetch the VIN using the SDK
        vin_info = vehicle.vin()

        print("Vehicle Info:", info)
        print("Vehicle VIN:", vin_info)

        return {
            'make': info.make or 'Unknown Make',
            'model': info.model or 'Unknown Model',
            'year': str(info.year) if info.year else 'Unknown Year',
            'vin': vin_info.vin or 'Unknown VIN'
        }
    except smartcar.SmartcarException as e:
        print("Error fetching vehicle details:")
        print(f"Code: {e.code}, Message: {e.message}")
        return {}

def find_vehicle_in_fleetio(vehicle_name, vin):
    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }

    # Ensure VIN and vehicle_name are properly formatted
    vehicle_name = vehicle_name.strip()
    vin = vin.strip().upper() if vin else None

    # First, try to find the vehicle by VIN
    if vin:
        print(f"Searching for vehicle by VIN: {vin}")
        response = requests.get(
            'https://secure.fleetio.com/api/v1/vehicles',
            headers=fleetio_headers,
            params={'q[vin_eq]': vin}
        )
        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            vehicles = data.get('records', [])
            for vehicle in vehicles:
                fleetio_vin = vehicle.get('vin', '').strip().upper()
                if fleetio_vin == vin:
                    vehicle_id = vehicle.get('id')
                    print(f"Vehicle found in Fleetio by VIN with ID {vehicle_id}.")
                    return vehicle_id
            print(f"No vehicle found in Fleetio with VIN: {vin}")
        else:
            error_info = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            print(f"Error searching Fleetio by VIN: {response.status_code}, Response: {error_info}")

    # If not found by VIN, try to find by name
    print(f"Searching for vehicle by name: {vehicle_name}")
    response = requests.get(
        'https://secure.fleetio.com/api/v1/vehicles',
        headers=fleetio_headers,
        params={'q[name_eq]': vehicle_name}
    )
    print(f"Request URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        vehicles = data.get('records', [])
        for vehicle in vehicles:
            fleetio_name = vehicle.get('name', '').strip()
            if fleetio_name == vehicle_name:
                vehicle_id = vehicle.get('id')
                print(f"Vehicle found in Fleetio by name with ID {vehicle_id}.")
                return vehicle_id
        print(f"No vehicle found in Fleetio with name: {vehicle_name}")
    else:
        error_info = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
        print(f"Error searching Fleetio by name: {response.status_code}, Response: {error_info}")
    return None

def create_or_update_vehicle_in_fleetio(vehicle_data):
    # Ensure all necessary keys are present
    year = str(vehicle_data.get('year', 'Unknown Year')).strip()
    make = vehicle_data.get('make', 'Unknown Make').strip()
    model = vehicle_data.get('model', 'Unknown Model').strip()
    vin = vehicle_data.get('vin', None)

    vehicle_name = f"{year} {make} {model}".strip()
    vin = vin.strip().upper() if vin else None

    # Attempt to find the vehicle in Fleetio by VIN or name
    vehicle_id = find_vehicle_in_fleetio(vehicle_name, vin)

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

    if vehicle_id:
        print(f"Vehicle '{vehicle_name}' found in Fleetio with ID {vehicle_id}. Updating vehicle.")
        # Update the vehicle in Fleetio
        fleetio_response = requests.put(
            f'https://secure.fleetio.com/api/v1/vehicles/{vehicle_id}',
            headers=fleetio_headers,
            json=fleetio_payload
        )

        if fleetio_response.status_code == 200:
            print(f"Vehicle '{vehicle_name}' updated successfully in Fleetio.")
        else:
            try:
                error_info = fleetio_response.json()
            except ValueError:
                error_info = fleetio_response.text
            print(f"Error updating vehicle '{vehicle_name}' in Fleetio: {error_info}")
    else:
        print(f"No existing vehicle found. Creating vehicle '{vehicle_name}' in Fleetio.")
        # Create a new vehicle in Fleetio
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

    access_data = get_smartcar_access()
    if not access_data:
        print("Failed to obtain access token. Exiting.")
        return

    access_token = access_data['access_token']

    vehicle_ids = get_vehicle_ids(access_token)

    for vehicle_id in vehicle_ids:
        vehicle_data = fetch_vehicle_details(access_token, vehicle_id)
        if not vehicle_data:
            print(f"Skipping vehicle ID {vehicle_id} due to missing data.")
            continue
        create_or_update_vehicle_in_fleetio(vehicle_data)

if __name__ == "__main__":
    main()
