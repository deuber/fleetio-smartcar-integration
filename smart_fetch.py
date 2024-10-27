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
# Commented out to prevent sensitive data exposure
# print("Redirect URI from .env:", REDIRECT_URI)

# Fleetio API credentials
fleetio_api_token = os.getenv("FLEETIO_API_TOKEN")
fleetio_account_token = os.getenv("FLEETIO_ACCOUNT_TOKEN")

def update_env_file(new_tokens):
    # Read existing environment variables
    from dotenv import dotenv_values

    env_path = ".env"
    env_vars = dotenv_values(env_path)

    # Update with new tokens
    env_vars.update(new_tokens)

    # Write back to the .env file
    with open(env_path, 'w') as env_file:
        for key, value in env_vars.items():
            env_file.write(f"{key}={value}\n")

def get_smartcar_access_token():
    # Load tokens from .env
    access_token = os.getenv("SMARTCAR_ACCESS_TOKEN")
    refresh_token = os.getenv("SMARTCAR_REFRESH_TOKEN")

    if access_token:
        # Test if the access token is still valid
        test_url = "https://api.smartcar.com/v1.0/vehicles"
        headers = {'Authorization': f'Bearer {access_token}'}
        test_response = requests.get(test_url, headers=headers)

        if test_response.status_code == 200:
            # print("Using existing access token from .env")
            return access_token
        elif refresh_token:
            # Refresh the access token
            # print("Access token expired. Attempting to refresh...")
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

                # Update tokens in .env
                update_env_file({
                    'SMARTCAR_ACCESS_TOKEN': access_token,
                    'SMARTCAR_REFRESH_TOKEN': refresh_token
                })
                # print("Access token refreshed successfully.")
                return access_token
            else:
                print("Failed to refresh token.")
        else:
            print("Access token expired and no refresh token available.")

    # Proceed with authorization flow
    auth_url = (
        f"https://connect.smartcar.com/oauth/authorize?response_type=code&client_id={SMARTCAR_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=read_odometer read_vehicle_info&approval_prompt=force"
    )
    print("Go to the following URL to authorize access:")
    print(auth_url)

    # Enter the authorization code after user grants access
    authorization_code = input("Enter the authorization code from the URL: ")

    # Exchange authorization code for access token
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

        # Save the new tokens in .env
        update_env_file({
            'SMARTCAR_ACCESS_TOKEN': access_token,
            'SMARTCAR_REFRESH_TOKEN': refresh_token
        })
        # print("Access token obtained successfully.")
    else:
        print("Error obtaining access token.")
        access_token = None

    return access_token

def get_vehicle_ids(access_token):
    # Retrieve vehicle IDs from Smartcar
    vehicle_list_url = "https://api.smartcar.com/v1.0/vehicles"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(vehicle_list_url, headers=headers)

    # Check for successful response
    if response.status_code == 200:
        try:
            # Parse the JSON response
            response_json = response.json()
            vehicle_ids = [vehicle for vehicle in response_json['vehicles']]
            return vehicle_ids
        except (KeyError, TypeError):
            print("Error parsing vehicle IDs.")
            return []
    else:
        print("Error fetching vehicle IDs.")
        return []

def fetch_vehicle_details(access_token, vehicle_id):
    # Fetch details of each vehicle from Smartcar
    vehicle_url = f"https://api.smartcar.com/v1.0/vehicles/{vehicle_id}"
    headers = {'Authorization': f'Bearer {access_token}'}
    vehicle_response = requests.get(vehicle_url, headers=headers)
    vehicle_data = vehicle_response.json()

    # Commented out to prevent sensitive data exposure
    # print("Vehicle Details Response:", vehicle_data)

    # Parse vehicle data and handle potential missing keys
    return {
        'make': vehicle_data.get('make', 'Unknown Make'),
        'model': vehicle_data.get('model', 'Unknown Model'),
        'year': vehicle_data.get('year', 'Unknown Year'),
        'vin': vehicle_data.get('vin', None)  # Include VIN if needed
    }

def fetch_vehicle_odometer(access_token, vehicle_id):
    odometer_url = f"https://api.smartcar.com/v2.0/vehicles/{vehicle_id}/odometer"
    headers = {'Authorization': f'Bearer {access_token}'}
    odometer_response = requests.get(odometer_url, headers=headers)
    odometer_data = odometer_response.json()

    # Commented out to prevent sensitive data exposure
    # print("Odometer Response:", odometer_data)

    # Get the odometer reading in kilometers
    odometer_km = odometer_data.get('distance')

    # Convert to miles if needed
    if odometer_km is not None:
        odometer_mi = round(odometer_km * 0.621371)
        return odometer_mi
    else:
        return None

def find_vehicle_in_fleetio_by_vin(vin):
    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(
        'https://secure.fleetio.com/api/v1/vehicles',
        headers=fleetio_headers,
        params={'q[vin_eq]': vin}
    )
    # Commented out to prevent sensitive data exposure
    # print("Fleetio VIN Search Response Status Code:", response.status_code)
    # print("Fleetio VIN Search Response JSON:", response.json())

    if response.status_code == 200:
        vehicles = response.json().get('records', [])
        if vehicles:
            return vehicles[0]['id']
    return None

def find_vehicle_in_fleetio(vehicle_name):
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
    # Commented out to prevent sensitive data exposure
    # print("Fleetio Vehicle Search Response Status Code:", response.status_code)
    # print("Fleetio Vehicle Search Response JSON:", response.json())

    if response.status_code == 200:
        vehicles = response.json().get('records', [])
        if vehicles:
            for vehicle in vehicles:
                fleetio_vehicle_name = vehicle.get('name', '').strip().lower()
                search_vehicle_name = vehicle_name.strip().lower()
                if fleetio_vehicle_name == search_vehicle_name:
                    return vehicle.get('id')
    return None

def create_meter_entry_in_fleetio(vehicle_id, odometer_value):
    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }
    meter_entry_payload = {
        'vehicle_id': vehicle_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        # 'meter_type': 'Odometer',  # Removed as per Fleetio API requirements
        'value': odometer_value,
        'unit': 'mi'  # or 'km' if using kilometers
    }

    # Commented out to prevent sensitive data exposure
    # print("Meter Entry Payload:", meter_entry_payload)

    # Make the POST request to create a Meter Entry
    meter_entry_response = requests.post(
        'https://secure.fleetio.com/api/v1/meter_entries',
        headers=fleetio_headers,
        json=meter_entry_payload
    )

    # Check for successful creation
    if meter_entry_response.status_code == 201:
        print(f"Meter entry created successfully for vehicle ID {vehicle_id}.")
    else:
        print(f"Error creating meter entry for vehicle ID {vehicle_id}.")

def create_or_update_vehicle_in_fleetio(vehicle_data):
    vehicle_name = f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}"
    vin = vehicle_data.get('vin')
    vehicle_id = None

    if vin:
        vehicle_id = find_vehicle_in_fleetio_by_vin(vin)
    else:
        vehicle_id = find_vehicle_in_fleetio(vehicle_name)

    fleetio_headers = {
        'Authorization': f'Token token={fleetio_api_token}',
        'Account-Token': fleetio_account_token,
        'Content-Type': 'application/json'
    }

    if vehicle_id:
        print(f"Vehicle '{vehicle_name}' found in Fleetio with ID {vehicle_id}.")
    else:
        # Create new vehicle
        fleetio_payload = {
            'make': vehicle_data['make'],
            'model': vehicle_data['model'],
            'year': vehicle_data['year'],
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
            vehicle_id = fleetio_response.json()['id']
            print(f"Vehicle '{vehicle_name}' created successfully in Fleetio with ID {vehicle_id}.")
        else:
            print(f"Error creating vehicle '{vehicle_name}' in Fleetio.")
            return  # Exit the function if vehicle creation failed

    # Create or update the meter entry
    if vehicle_data['odometer'] is not None:
        create_meter_entry_in_fleetio(vehicle_id, vehicle_data['odometer'])
    else:
        print(f"Odometer reading not available for vehicle '{vehicle_name}'.")

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
        print("Fleetio authentication failed.")

def main():
    # Test Fleetio authentication
    test_fleetio_authentication()

    # Authorize and get access token
    access_token = get_smartcar_access_token()
    if not access_token:
        print("Failed to obtain access token. Exiting.")
        return

    # Get vehicle IDs linked to your account via Smartcar
    vehicle_ids = get_vehicle_ids(access_token)

    # For each vehicle ID, fetch details and create or update it in Fleetio
    for vehicle_id in vehicle_ids:
        vehicle_data = fetch_vehicle_details(access_token, vehicle_id)
        # Fetch odometer reading
        odometer = fetch_vehicle_odometer(access_token, vehicle_id)
        vehicle_data['odometer'] = odometer
        create_or_update_vehicle_in_fleetio(vehicle_data)

if __name__ == "__main__":
    main()
