#!/usr/bin/env python3
"""
ERCOT Public API Query Script

This script queries the ERCOT Public Data Portal API and retrieves data in JSON format.
It handles authentication, token refresh, and flexible parameter handling.

Author: Your Name
Date: January 2025
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Third-party imports (install via requirements.txt)
import requests
from dotenv import load_dotenv


class ERCOTAPIClient:
    """
    A client for interacting with the ERCOT Public Data Portal API.
    
    This class handles:
    - Authentication and token management
    - Token refresh (tokens expire every 30 minutes)
    - API requests with flexible parameters
    - Error handling and response validation
    """
    
    def __init__(self, debug=False):
        """
        Initialize the ERCOT API client.
        Loads credentials from the .env file.

        Args:
            debug (bool): Enable debug output
        """
        # Load environment variables from .env file
        # This reads your secrets without hardcoding them in the script
        load_dotenv()

        # Store debug flag
        self.debug = debug

        # Retrieve credentials from environment variables
        # These are set in your .env file
        self.username = os.getenv('ERCOT_USERNAME')
        self.password = os.getenv('ERCOT_PASSWORD')
        self.subscription_key = os.getenv('ERCOT_SUBSCRIPTION_KEY')

        # Base URL for the ERCOT API (update if needed)
        self.base_url = os.getenv('ERCOT_BASE_URL', 'https://data.ercot.com')

        # ERCOT Public Reports API requires bearer token authentication
        # Always use bearer auth
        self.use_bearer_auth = True

        # Validate that all required credentials are present
        self._validate_credentials()

        # Token will be stored here after authentication (only if using bearer auth)
        self.access_token = None
        self.token_expiry = None

        if self.debug:
            print("\n[DEBUG] ERCOTAPIClient initialized")
            print(f"[DEBUG] Base URL: {self.base_url}")
            print(f"[DEBUG] Authentication: Azure B2C ROPC Flow")
            if self.username:
                print(f"[DEBUG] Username: {self.username[:3]}***{self.username[-2:] if len(self.username) > 5 else '***'}")
            if self.password:
                print(f"[DEBUG] Password length: {len(self.password)} characters")
            print(f"[DEBUG] Subscription key: {self.subscription_key[:8]}...{self.subscription_key[-4:]}")
    
    def _validate_credentials(self):
        """
        Check that all required credentials are present in the .env file.
        Exits the program with an error message if any are missing.
        """
        # Subscription key is always required
        if not self.subscription_key:
            print("ERROR: ERCOT_SUBSCRIPTION_KEY not found in .env file")
            sys.exit(1)

        # Username and password only required for bearer token authentication
        if self.use_bearer_auth:
            if not self.username:
                print("ERROR: ERCOT_USERNAME not found in .env file")
                sys.exit(1)
            if not self.password:
                print("ERROR: ERCOT_PASSWORD not found in .env file")
                sys.exit(1)
    
    def authenticate(self):
        """
        Authenticate with the ERCOT API and obtain an access token.

        Uses Azure B2C ROPC (Resource Owner Password Credentials) flow.
        The token is valid for 60 minutes (3600 seconds).

        Returns:
            bool: True if authentication successful, False otherwise
        """
        print("Authenticating with ERCOT API...")

        # ERCOT uses Azure B2C authentication
        # Authentication endpoint for Public Reports API
        auth_url = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"

        # ERCOT Public API client ID
        client_id = "fec253ea-0d06-4272-a5e6-b478baeecd70"

        # Build the authentication URL with query parameters
        # ERCOT's B2C endpoint expects parameters in the URL, not JSON body
        auth_params = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "scope": f"openid {client_id} offline_access",
            "client_id": client_id,
            "response_type": "id_token"
        }

        # Headers for authentication request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        if self.debug:
            print("\n[DEBUG] ========== Authentication Request ==========")
            print(f"[DEBUG] URL: {auth_url}")
            print(f"[DEBUG] Method: POST")
            print("[DEBUG] Headers:")
            for key, value in headers.items():
                print(f"[DEBUG]   {key}: {value}")
            print("[DEBUG] Parameters:")
            for key, value in auth_params.items():
                if key == "password":
                    print(f"[DEBUG]   {key}: {'*' * len(value)}")
                else:
                    print(f"[DEBUG]   {key}: {value}")
            print("[DEBUG] ================================================\n")

        try:
            # Send POST request with form-encoded parameters
            response = requests.post(auth_url, data=auth_params, headers=headers)

            if self.debug:
                print("\n[DEBUG] ========== Authentication Response ==========")
                print(f"[DEBUG] Status Code: {response.status_code}")
                print(f"[DEBUG] Status Reason: {response.reason}")
                print("[DEBUG] Response Headers:")
                for key, value in response.headers.items():
                    print(f"[DEBUG]   {key}: {value}")
                print(f"[DEBUG] Response Body:")
                try:
                    # Try to pretty-print JSON response
                    print(json.dumps(response.json(), indent=2))
                except:
                    # If not JSON, print raw text
                    print(f"[DEBUG]   {response.text}")
                print("[DEBUG] ==================================================\n")

            # Check if request was successful (HTTP 200)
            if response.status_code == 200:
                # Parse the JSON response
                token_data = response.json()

                # Extract the access token (ERCOT returns 'access_token')
                self.access_token = token_data.get('access_token')

                if self.debug:
                    if self.access_token:
                        print(f"[DEBUG] Access token received: {self.access_token[:20]}...{self.access_token[-10:] if len(self.access_token) > 30 else ''}")
                    else:
                        print("[DEBUG] WARNING: No access_token field in response!")
                        print(f"[DEBUG] Response keys: {list(token_data.keys())}")

                # ERCOT tokens expire after 60 minutes (3600 seconds)
                # We subtract 5 minutes as a safety buffer to refresh before actual expiry
                self.token_expiry = datetime.now() + timedelta(minutes=55)

                print(f"✓ Authentication successful. Token valid until {self.token_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                # Authentication failed
                print(f"✗ Authentication failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            # Network error or other request issue
            print(f"✗ Error during authentication: {e}")
            if self.debug:
                import traceback
                print("\n[DEBUG] Full exception traceback:")
                traceback.print_exc()
            return False
    
    def _is_token_valid(self):
        """
        Check if the current access token is still valid.
        
        Returns:
            bool: True if token exists and hasn't expired, False otherwise
        """
        if not self.access_token:
            return False
        if not self.token_expiry:
            return False
        # Check if current time is before expiry time
        return datetime.now() < self.token_expiry
    
    def _ensure_authenticated(self):
        """
        Ensure we have a valid access token, refreshing if necessary.

        This method is called before each API request to guarantee
        we always have a valid token (only for bearer token auth).
        """
        # Skip authentication if using subscription key only
        if not self.use_bearer_auth:
            if self.debug:
                print("[DEBUG] Skipping bearer token authentication (using subscription key only)")
            return

        # For bearer token auth, check and refresh if needed
        if not self._is_token_valid():
            print("Token expired or not available. Refreshing...")
            if not self.authenticate():
                raise Exception("Failed to authenticate with ERCOT API")
    
    def query_api(self, endpoint, parameters=None):
        """
        Query the ERCOT API with the specified endpoint and parameters.

        Args:
            endpoint (str): The API endpoint path (e.g., '/api/v1/actual_system_load')
            parameters (dict): Query parameters to send with the request
                             (e.g., {'deliveryDateFrom': '2025-01-01', 'deliveryDateTo': '2025-01-27'})

        Returns:
            dict: JSON response from the API, or None if request failed
        """
        # Ensure we have a valid token before making the request
        self._ensure_authenticated()

        # Construct the full URL
        url = f"{self.base_url}{endpoint}"

        # Prepare headers for the API request
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }

        # Add Bearer token only if using bearer authentication
        if self.use_bearer_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        # Log the request details
        print(f"\nQuerying endpoint: {endpoint}")
        if parameters:
            print(f"Parameters: {json.dumps(parameters, indent=2)}")

        if self.debug:
            print("\n[DEBUG] ========== API Query Request ==========")
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Method: GET")
            print("[DEBUG] Headers:")
            for key, value in headers.items():
                if key == "Authorization":
                    token_preview = self.access_token[:20] + "..." if len(self.access_token) > 20 else self.access_token
                    print(f"[DEBUG]   {key}: Bearer {token_preview}")
                elif key == "Ocp-Apim-Subscription-Key":
                    print(f"[DEBUG]   {key}: {value[:8]}...{value[-4:]}")
                else:
                    print(f"[DEBUG]   {key}: {value}")
            if parameters:
                print(f"[DEBUG] Query Parameters: {json.dumps(parameters, indent=2)}")
            print("[DEBUG] ==========================================\n")

        try:
            # Send GET request to the API
            # params will be URL-encoded automatically by requests library
            response = requests.get(url, headers=headers, params=parameters)

            if self.debug:
                print("\n[DEBUG] ========== API Query Response ==========")
                print(f"[DEBUG] Status Code: {response.status_code}")
                print(f"[DEBUG] Status Reason: {response.reason}")
                print("[DEBUG] Response Headers:")
                for key, value in response.headers.items():
                    print(f"[DEBUG]   {key}: {value}")
                print(f"[DEBUG] Response Body (first 500 chars):")
                print(f"[DEBUG]   {response.text[:500]}")
                print("[DEBUG] ==========================================\n")

            # Check if request was successful
            if response.status_code == 200:
                print(f"✓ Request successful (HTTP {response.status_code})")
                # Parse and return the JSON response
                return response.json()
            else:
                # Request failed
                print(f"✗ Request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            # Network error or other request issue
            print(f"✗ Error during API request: {e}")
            if self.debug:
                import traceback
                print("\n[DEBUG] Full exception traceback:")
                traceback.print_exc()
            return None
    
    def save_response(self, data, output_file):
        """
        Save the API response to a JSON file.
        
        Args:
            data (dict): The data to save (typically the API response)
            output_file (str): Path where the JSON file should be saved
        """
        try:
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write data to file with pretty formatting (indent=2)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ Data saved to: {output_file}")
            
            # Print some statistics about the saved data
            file_size = output_path.stat().st_size
            print(f"  File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
            
        except Exception as e:
            print(f"✗ Error saving data to file: {e}")


def load_query_config(config_file):
    """
    Load a query configuration from a JSON file.
    
    The configuration file should contain:
    - endpoint: The API endpoint to query
    - parameters: Dictionary of query parameters
    - output_file: Where to save the response
    
    Args:
        config_file (str): Path to the JSON configuration file
    
    Returns:
        dict: The parsed configuration, or None if file cannot be loaded
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Validate that required fields are present
        if 'endpoint' not in config:
            print(f"✗ Configuration file missing required field: 'endpoint'")
            return None
        
        # Set defaults for optional fields
        if 'parameters' not in config:
            config['parameters'] = {}
        if 'output_file' not in config:
            # Generate default output filename based on endpoint and timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            endpoint_name = config['endpoint'].split('/')[-1]
            config['output_file'] = f"output/{endpoint_name}_{timestamp}.json"
        
        return config
        
    except FileNotFoundError:
        print(f"✗ Configuration file not found: {config_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in configuration file: {e}")
        return None


def main():
    """
    Main function that orchestrates the ERCOT API query process.
    
    This function:
    1. Parses command-line arguments
    2. Loads the query configuration
    3. Initializes the API client
    4. Executes the query
    5. Saves the results
    """
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        description='Query the ERCOT Public Data Portal API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query using a configuration file
  python3 ercot_query.py --config queries/realtime_load.json
  
  # Query with verbose output
  python3 ercot_query.py --config queries/settlement_prices.json --verbose
        """
    )
    
    # Define command-line arguments
    parser.add_argument(
        '--config',
        required=True,
        help='Path to the query configuration JSON file'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output (shows detailed request/response information)'
    )
    
    # Parse the arguments provided by the user
    args = parser.parse_args()
    
    # Display header
    print("=" * 60)
    print("ERCOT Public API Query Tool")
    print("=" * 60)
    
    # Load the query configuration from the specified file
    config = load_query_config(args.config)
    if not config:
        sys.exit(1)
    
    print(f"\nConfiguration loaded from: {args.config}")
    
    # Initialize the ERCOT API client
    # This loads credentials from .env file
    client = ERCOTAPIClient(debug=args.debug)

    # Authenticate with the API (only if using bearer token authentication)
    # For subscription key-only APIs, this step is skipped
    if client.use_bearer_auth:
        if not client.authenticate():
            print("\n✗ Failed to authenticate. Please check your credentials in .env file")
            sys.exit(1)
    else:
        print("Using subscription key authentication (no bearer token required)")
    
    # Execute the API query
    response_data = client.query_api(
        endpoint=config['endpoint'],
        parameters=config.get('parameters', {})
    )
    
    # Check if we got a valid response
    if response_data is None:
        print("\n✗ Query failed. No data retrieved.")
        sys.exit(1)
    
    # Save the response to a file
    client.save_response(response_data, config['output_file'])
    
    print("\n" + "=" * 60)
    print("✓ Query completed successfully!")
    print("=" * 60)


# This block runs when the script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()
