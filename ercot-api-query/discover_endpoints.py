#!/usr/bin/env python3
"""
ERCOT API Endpoint Discovery Script

This script authenticates to the ERCOT API and discovers all available endpoints,
then creates query configuration files for each endpoint with basic parameters.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re

# Load environment variables
load_dotenv()

# Configuration
AUTH_URL = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
CLIENT_ID = "fec253ea-0d06-4272-a5e6-b478baeecd70"
BASE_API_URL = "https://api.ercot.com/api/public-reports"


def authenticate():
    """Authenticate and get access token."""
    print("Authenticating to ERCOT API...")

    auth_params = {
        "username": os.getenv("ERCOT_USERNAME"),
        "password": os.getenv("ERCOT_PASSWORD"),
        "grant_type": "password",
        "scope": f"openid {CLIENT_ID} offline_access",
        "client_id": CLIENT_ID,
        "response_type": "id_token"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(AUTH_URL, data=auth_params, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            print("✗ Authentication failed: No access token received")
            return None

        print(f"✓ Authentication successful")
        print(f"  Token: {access_token[:20]}...")
        return access_token

    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return None


def discover_base_endpoints(access_token, subscription_key):
    """Query base API URL to discover available endpoints."""
    print("\nMethod 1: Querying base API for endpoint discovery...")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json"
    }

    try:
        response = requests.get(BASE_API_URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Base API response received")

            # Try to find endpoint references in the response
            response_text = json.dumps(data)
            endpoints = re.findall(r'np[0-9]-[0-9]+-[a-z]+', response_text)

            if endpoints:
                unique_endpoints = sorted(set(endpoints))
                print(f"✓ Found {len(unique_endpoints)} unique endpoint IDs")
                return unique_endpoints
            else:
                print("⚠ No endpoint patterns found in base API")
                return []
        else:
            print(f"⚠ Base API returned status {response.status_code}")
            return []

    except Exception as e:
        print(f"✗ Error querying base API: {e}")
        return []


def get_endpoint_metadata(access_token, subscription_key, endpoint_id):
    """Query endpoint to get its metadata and parameter information."""
    url = f"{BASE_API_URL}/{endpoint_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        metadata = {
            "endpoint_id": endpoint_id,
            "status_code": response.status_code,
            "exists": response.status_code in [200, 400]
        }

        if response.status_code == 200:
            data = response.json()
            metadata["data"] = data
            metadata["fields"] = data.get("fields", [])

        elif response.status_code == 400:
            # Endpoint exists but needs parameters - parse the error message
            try:
                error_data = response.json()
                metadata["error_data"] = error_data

                # Try to extract parameter names from error message
                error_msg = json.dumps(error_data)

                # Look for common parameter patterns
                metadata["uses_delivery_date"] = "deliveryDate" in error_msg
                metadata["uses_sced_timestamp"] = "SCEDTimestamp" in error_msg
                metadata["uses_post_datetime"] = "postDatetime" in error_msg

            except:
                pass

        return metadata

    except Exception as e:
        return {
            "endpoint_id": endpoint_id,
            "exists": False,
            "error": str(e)
        }


def detect_parameter_type(metadata):
    """Detect what type of date/time parameters the endpoint uses."""
    endpoint_id = metadata.get("endpoint_id", "")

    # Check if metadata has explicit parameter info
    if metadata.get("uses_sced_timestamp"):
        return "SCED"
    elif metadata.get("uses_delivery_date"):
        return "DAM"
    elif metadata.get("uses_post_datetime"):
        return "ARCHIVE"

    # Check fields if available
    fields = metadata.get("fields", [])
    for field in fields:
        field_name = field.get("name", "").lower()
        if "scedtimestamp" in field_name:
            return "SCED"
        elif "deliverydate" in field_name:
            return "DAM"
        elif "postdatetime" in field_name:
            return "ARCHIVE"

    # Fallback to endpoint naming convention
    # NP4 are typically DAM, NP6 are typically RTM/SCED
    if endpoint_id.startswith("np4"):
        return "DAM"
    elif endpoint_id.startswith("np6"):
        return "SCED"
    elif "archive" in endpoint_id.lower():
        return "ARCHIVE"

    # Default to DAM for unknown
    return "DAM"


def create_query_config(endpoint_id, parameter_type):
    """Create a query configuration JSON for an endpoint."""
    # Calculate date ranges (yesterday)
    yesterday = datetime.now() - timedelta(days=1)

    config = {
        "endpoint": endpoint_id,
        "parameters": {},
        "output_file": f"output/discovered/{endpoint_id.replace('-', '_')}.json"
    }

    if parameter_type == "DAM":
        # Day-Ahead Market uses deliveryDate (YYYY-MM-DD)
        date_str = yesterday.strftime('%Y-%m-%d')
        config["parameters"]["deliveryDateFrom"] = date_str
        config["parameters"]["deliveryDateTo"] = date_str

    elif parameter_type == "SCED":
        # Real-Time/SCED uses SCEDTimestamp (YYYY-MM-DDTHH:MM:SS)
        timestamp_from = yesterday.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%S')
        timestamp_to = yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%dT%H:%M:%S')
        config["parameters"]["SCEDTimestampFrom"] = timestamp_from
        config["parameters"]["SCEDTimestampTo"] = timestamp_to

    elif parameter_type == "ARCHIVE":
        # Archive uses postDatetime
        timestamp_from = yesterday.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%S')
        timestamp_to = yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%dT%H:%M:%S')
        config["parameters"]["postDatetimeFrom"] = timestamp_from
        config["parameters"]["postDatetimeTo"] = timestamp_to

    return config


def create_query_files(endpoints_metadata):
    """Create query configuration files for all discovered endpoints."""
    print("\nCreating query configuration files...")

    # Create output directory
    queries_dir = Path("queries/discovered")
    queries_dir.mkdir(parents=True, exist_ok=True)

    created_count = 0
    skipped_count = 0

    for metadata in endpoints_metadata:
        if not metadata.get("exists"):
            skipped_count += 1
            continue

        endpoint_id = metadata["endpoint_id"]
        parameter_type = detect_parameter_type(metadata)

        # Create query config
        query_config = create_query_config(endpoint_id, parameter_type)

        # Add metadata comment
        query_config["_metadata"] = {
            "endpoint_id": endpoint_id,
            "parameter_type": parameter_type,
            "discovered_at": datetime.now().isoformat(),
            "note": "Auto-generated query configuration. Adjust parameters as needed."
        }

        # Save to file
        filename = queries_dir / f"{endpoint_id.replace('-', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(query_config, f, indent=2)

        print(f"  ✓ Created: {filename.name} ({parameter_type})")
        created_count += 1

    print(f"\n✓ Created {created_count} query files")
    print(f"  Skipped {skipped_count} non-working endpoints")
    print(f"  Location: {queries_dir}/")

    return created_count


def save_results(discovered_endpoints, detailed_info):
    """Save discovery results to files."""
    print("\nSaving discovery results...")

    # Save unique endpoint IDs
    with open("discovered_endpoints.json", "w") as f:
        json.dump({
            "discovered_at": datetime.now().isoformat(),
            "total_endpoints": len(discovered_endpoints),
            "endpoints": discovered_endpoints
        }, f, indent=2)
    print("  ✓ Saved to: discovered_endpoints.json")

    # Save detailed information
    with open("discovered_endpoints_detailed.json", "w") as f:
        json.dump(detailed_info, f, indent=2)
    print("  ✓ Saved to: discovered_endpoints_detailed.json")

    # Also save a simple text list
    with open("discovered_endpoints.txt", "w") as f:
        for endpoint in discovered_endpoints:
            f.write(f"{endpoint}\n")
    print("  ✓ Saved to: discovered_endpoints.txt")


def main():
    """Main discovery process."""
    print("=" * 60)
    print("ERCOT API Endpoint Discovery & Query Generator")
    print("=" * 60)
    print()

    # Check environment variables
    if not os.getenv("ERCOT_USERNAME") or not os.getenv("ERCOT_PASSWORD"):
        print("✗ Error: ERCOT credentials not found in .env file")
        sys.exit(1)

    subscription_key = os.getenv("ERCOT_SUBSCRIPTION_KEY")

    # Step 1: Authenticate
    access_token = authenticate()
    if not access_token:
        sys.exit(1)

    # Step 2: Discover endpoints
    print("\nDiscovering endpoints...")
    all_discovered = discover_base_endpoints(access_token, subscription_key)

    if not all_discovered:
        print("✗ No endpoints discovered")
        sys.exit(1)

    # Step 3: Get metadata for each endpoint
    print("\nGetting endpoint metadata...")
    print("(This will take a few moments...)")

    detailed_metadata = []
    for i, endpoint_id in enumerate(all_discovered, 1):
        print(f"  [{i}/{len(all_discovered)}] Querying {endpoint_id}...", end=" ")

        metadata = get_endpoint_metadata(access_token, subscription_key, endpoint_id)
        detailed_metadata.append(metadata)

        if metadata.get("exists"):
            param_type = detect_parameter_type(metadata)
            print(f"✓ ({param_type})")
        else:
            print("✗ (unavailable)")

    # Step 4: Create query configuration files
    query_count = create_query_files(detailed_metadata)

    # Step 5: Save discovery results
    save_results(all_discovered, detailed_metadata)

    # Summary
    print()
    print("=" * 60)
    print("Discovery Summary")
    print("=" * 60)
    print(f"Total endpoints discovered: {len(all_discovered)}")
    print(f"Query files created: {query_count}")
    print()

    # Count by parameter type
    dam_count = sum(1 for m in detailed_metadata if m.get("exists") and detect_parameter_type(m) == "DAM")
    sced_count = sum(1 for m in detailed_metadata if m.get("exists") and detect_parameter_type(m) == "SCED")
    archive_count = sum(1 for m in detailed_metadata if m.get("exists") and detect_parameter_type(m) == "ARCHIVE")

    print(f"Parameter Types:")
    print(f"  • DAM (deliveryDate): {dam_count} endpoints")
    print(f"  • SCED (SCEDTimestamp): {sced_count} endpoints")
    print(f"  • ARCHIVE (postDatetime): {archive_count} endpoints")
    print()
    print("=" * 60)
    print()
    print("Query files location: queries/discovered/")
    print("You can now run any query with:")
    print("  python3 ercot_query.py --config queries/discovered/ENDPOINT.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
