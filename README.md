# Fleetio-Smartcar Integration

This project integrates the **Smartcar API** with **Fleetio** to enable seamless vehicle data synchronization. The script connects to Smartcar to retrieve vehicle information (like odometer readings) and updates or creates corresponding entries in Fleetio.


> **Watch the Demo**: Check out the [YouTube demo here](https://youtu.be/ADai9EPfKKg).

> **User Guide**: For a detailed, user-friendly tutorial, refer to the [Fleetio-Smartcar Integration Guide](Fleetio-Smartcar_Integration_Guide.pdf). This guide provides step-by-step instructions for setting up and automating the integration, especially helpful if you’re new to working with APIs.

> **Tip**: [Set up Postman](https://www.postman.com/smartcar/smartcar-api/documentation/fqmwehs/smartcar-ap).

> **Tip**: Use Postman to test:
i

> **Note**: This integration has been successfully tested with my Toyota vehicles to retrieve and sync vehicle data with Fleetio.


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


The script will:

1. **Prompt for authentication** with Smartcar.
2. **Retrieve vehicle information** and odometer readings.
3. **Sync this information with Fleetio**, either updating existing vehicle entries or creating new ones.

## Automating Daily Execution on macOS

To keep vehicle data up-to-date, you can schedule the script to run once daily. This requires creating an additional script, `schedule_fetch.py`, and setting up a **cron job**.

### Step 1: Create the `schedule_fetch.py` Script

This script will run `smart_fetch.py` and log its execution time:

```python
import subprocess
import datetime

# Log the execution time
current_time = datetime.datetime.now()
print(f"Running smart_fetch.py at {current_time}")

# Run smart_fetch.py
subprocess.run(["python3", "smart_fetch.py"])
