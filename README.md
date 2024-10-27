# Fleetio-Smartcar Integration

This project integrates the **Smartcar API** with **Fleetio** to enable seamless vehicle data synchronization. The script connects to Smartcar to retrieve vehicle information (like odometer readings) and updates or creates corresponding entries in Fleetio.

> **Note**: This integration has been successfully tested with the **Toyota API** to retrieve and sync vehicle data with Fleetio.

## Features

- **Vehicle Retrieval**: Automatically retrieves vehicle information and mileage from the Smartcar API.
- **Fleetio Integration**: Syncs vehicle data with Fleetio, updating vehicle info or creating new entries as needed.
- **Odometer Updates**: Keeps odometer readings up-to-date within Fleetio for accurate tracking.

## Requirements

- Python 3.6+
- Git
- A [Smartcar](https://smartcar.com/) account with API access
- A [Fleetio](https://www.fleetio.com/) account with API access

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/deuber/fleetio-smartcar-integration.git
    cd fleetio-smartcar-integration
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Create a `.env` file in the root directory with your API credentials. Here’s an example:

    ```plaintext
    SMARTCAR_CLIENT_ID=your_smartcar_client_id
    SMARTCAR_CLIENT_SECRET=your_smartcar_client_secret
    FLEETIO_API_TOKEN=your_fleetio_api_token
    FLEETIO_ACCOUNT_TOKEN=your_fleetio_account_token
    REDIRECT_URI=http://localhost:8000/callback
    ```

2. Ensure your `.gitignore` includes `.env` to keep your credentials safe:

    ```plaintext
    .env
    ```

## Usage

To run the script:

```bash
python smart_fetch.py
