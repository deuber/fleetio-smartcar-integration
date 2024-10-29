# Fleetio-Smartcar Integration

This project integrates the **Smartcar API** with **Fleetio** to enable seamless vehicle data synchronization. The scripts connect to Smartcar to retrieve vehicle information (like odometer readings) and update or create corresponding entries in Fleetio.

> **Watch the Demo**: Check out the [YouTube demo here](https://youtu.be/ADai9EPfKKg).

> **User Guide**: For a detailed, user-friendly tutorial, refer to the [Fleetio-Smartcar Integration Guide](Fleetio-Smartcar_Integration_Guide.pdf). This guide provides step-by-step instructions for setting up and automating the integration, especially helpful if you’re new to working with APIs.

> **Tip**: [Set up Postman to interact with API](https://www.postman.com/smartcar/smartcar-api/documentation/fqmwehs/smartcar-ap).

> **Note**: This integration has been successfully tested with Toyota vehicles to retrieve and sync vehicle data with Fleetio.

## Features

- **Vehicle Retrieval**: Automatically retrieves vehicle information and mileage from the Smartcar API.
- **Fleetio Integration**: Syncs vehicle data with Fleetio, updating vehicle info or creating new entries as needed.
- **Odometer Updates**: Keeps odometer readings up-to-date within Fleetio for accurate tracking.
- **SDK-Based Integration**: Utilizes the Smartcar Python SDK for enhanced functionality and easier maintenance.

## Requirements

- Python 3.6+
- Git
- A [Smartcar](https://smartcar.com/) account with API access
- A [Fleetio](https://www.fleetio.com/) account with API access

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/deuber/fleetio-smartcar-integration.git
    cd fleetio-smartcar-integration
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Create a `.env` file in the root directory with your API credentials.** Ensure that each script uses distinct tokens to avoid conflicts. Here's an example:

    ```env
    # Smartcar credentials
    SMARTCAR_CLIENT_ID=your_smartcar_client_id
    SMARTCAR_CLIENT_SECRET=your_smartcar_client_secret
    REDIRECT_URI=http://localhost:8000/callback

    # Fleetio credentials
    FLEETIO_API_TOKEN=your_fleetio_api_token
    FLEETIO_ACCOUNT_TOKEN=your_fleetio_account_token

    # Tokens for smart_fetch.py
    SMARTCAR_ACCESS_TOKEN=your_smartcar_access_token
    SMARTCAR_REFRESH_TOKEN=your_smartcar_refresh_token

    # Tokens for smart_fetch_sdk.py
    SMARTCAR_ACCESS_TOKEN_SDK=your_smartcar_access_token_sdk
    SMARTCAR_REFRESH_TOKEN_SDK=your_smartcar_refresh_token_sdk
    ```

    > **Important:** Ensure that `.env` is included in your `.gitignore` to keep your credentials secure.

2. **Ensure your `.gitignore` includes `.env` to keep your credentials safe:**

    ```plaintext
    .env
    ```

## Scripts Overview

This project includes two primary scripts:

1. [`smart_fetch.py`](#smart_fetchpy)
2. [`smart_fetch_sdk.py`](#smart_fetchsdkpy)

### `smart_fetch.py`

A basic script that interacts directly with the Smartcar API using HTTP requests. It handles token management manually and performs vehicle data synchronization with Fleetio.

### `smart_fetch_sdk.py`

An enhanced version of `smart_fetch.py` that leverages the **Smartcar Python SDK**. This version simplifies interactions with the Smartcar API by utilizing the SDK's built-in functionalities for token management, error handling, and API requests.

## Why Use the SDK Version?

The SDK version (`smart_fetch_sdk.py`) offers several advantages over the basic version (`smart_fetch.py`):

- **Simplified Token Management:** The SDK handles token refreshes and storage automatically, reducing the complexity in your code.
- **Robust Error Handling:** The SDK provides comprehensive exception classes, making it easier to manage and debug errors.
- **Cleaner Codebase:** The SDK abstracts away low-level HTTP requests, allowing you to focus on core functionality.
- **Built-in Utilities:** The SDK offers utilities for common tasks, such as fetching vehicle attributes and VIN, streamlining your workflow.

## Differences Between `smart_fetch.py` and `smart_fetch_sdk.py`

| Feature                        | `smart_fetch.py`                                 | `smart_fetch_sdk.py`                            |
|--------------------------------|--------------------------------------------------|-------------------------------------------------|
| **API Interaction**            | Direct HTTP requests                             | Smartcar Python SDK                             |
| **Token Management**           | Manual handling of access and refresh tokens     | Automated token management via SDK              |
| **Error Handling**             | Basic error checks                               | Enhanced exception handling provided by SDK     |
| **Code Complexity**            | More verbose, handling low-level details         | More concise, leveraging SDK abstractions       |
| **Ease of Maintenance**        | Requires manual updates for API changes          | Easier updates through SDK's maintained methods |
| **Additional Functionalities** | Limited to implemented features                  | Access to SDK's extended features and utilities |

## Usage

You can choose to use either the basic script (`smart_fetch.py`) or the SDK-based script (`smart_fetch_sdk.py`) based on your preference and requirements.

### Using `smart_fetch.py`

1. **Run the script:**

    ```bash
    python smart_fetch.py
    ```

2. **Authentication Flow:**

    - If running for the first time or tokens are expired, the script will prompt you to authorize access via a URL.
    - Follow the instructions to obtain the authorization code and enter it when prompted.

3. **Functionality:**

    - Retrieves vehicle IDs from Smartcar.
    - Fetches vehicle details and VINs.
    - Searches for corresponding vehicles in Fleetio by VIN or name.
    - Updates existing vehicles or creates new entries in Fleetio.

### Using `smart_fetch_sdk.py`

1. **Run the SDK script:**

    ```bash
    python smart_fetch_sdk.py
    ```

2. **Authentication Flow:**

    - If running for the first time or tokens are expired, the script will prompt you to authorize access via a URL.
    - Follow the instructions to obtain the authorization code and enter it when prompted.

3. **Functionality:**

    - Utilizes the Smartcar Python SDK to handle API interactions.
    - Automatically manages token refreshes and validations.
    - Retrieves vehicle IDs, attributes, and VINs.
    - Searches for corresponding vehicles in Fleetio by VIN or name.
    - Updates existing vehicles or creates new entries in Fleetio with simplified and more reliable code.

## Automating Daily Execution on macOS

To keep vehicle data up-to-date, you can schedule the script to run once daily. This requires creating an additional script and setting up a **cron job**.

### Step 1: Choose the Script to Automate

Decide whether you want to automate the basic script (`smart_fetch.py`) or the SDK-based script (`smart_fetch_sdk.py`). It is recommended to use the SDK version for its enhanced features and reliability.

### Step 2: Create the Cron Job

1. **Open the crontab editor:**

    ```bash
    crontab -e
    ```

2. **Add the following line to schedule the script to run daily at midnight:**

    ```bash
    0 0 * * * /usr/bin/python3 /path/to/smart_fetch_sdk.py >> /path/to/smart_fetch_sdk.log 2>&1
    ```

    - **Explanation:**
        - `0 0 * * *`: Runs the script every day at midnight.
        - `/usr/bin/python3`: Path to the Python interpreter.
        - `/path/to/smart_fetch_sdk.py`: Replace with the actual path to your script.
        - `>> /path/to/smart_fetch_sdk.log 2>&1`: Redirects both standard output and standard error to a log file.

3. **Save and exit the editor.**

### Step 3: Verify the Cron Job

Ensure that the cron job is set up correctly by listing all cron jobs:

```bash
crontab -l
   ```


# Security Best Practices



### Protect Your \`.env\` File:

Ensure that your \`.env\` file is included in your \`.gitignore\` to prevent sensitive information from being committed to version control systems like GitHub.

`.env\`

### Use Strong API Tokens:

Always use strong and unique API tokens. Rotate them periodically and revoke any that are no longer in use.

### Limit API Permissions:

Grant only the necessary permissions to your API tokens to minimize potential security risks.

Virtual Environments


Using virtual environments helps manage dependencies and avoid conflicts between different projects.
### Create a virtual environment:


`python3 -m venv venv\`

### Activate the virtual environment:



`source venv/bin/activate  # On Windows, use \`venv\\Scripts\\activate\`\`

### Install dependencies:



`pip install -r requirements.txt\`

# Maintenance and Updates


### Keep Dependencies Updated:

Regularly update your Python packages to benefit from the latest features and security patches.



`pip install --upgrade smartcar requests python-dotenv\`

### Monitor API Changes:

Stay informed about any updates or changes to the Smartcar and Fleetio APIs to ensure continued compatibility.

# Troubleshooting


### Authentication Issues:

-   Ensure that your Smartcar and Fleetio API credentials are correct and properly set in the \`.env\` file.

-   Verify that your redirect URI matches the one configured in your Smartcar application settings.

### API Rate Limits:

-   Be aware of the API rate limits imposed by Smartcar and Fleetio. Implement exponential backoff strategies if you encounter rate limit errors.

### Network Connectivity:

-   Ensure that your system has a stable internet connection to communicate with the Smartcar and Fleetio APIs.

# Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements or bug fixes.

License

This project is licensed under the \[MIT License\](LICENSE).