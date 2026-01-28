#!/usr/bin/env python3
"""
ERCOT API Endpoint Discovery Script

This script authenticates to the ERCOT API and discovers all available endpoints
by querying the API directly and parsing responses.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
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


def test_endpoint_pattern(access_token, subscription_key, endpoint_id):
    """Test if a specific endpoint pattern exists."""
    url = f"{BASE_API_URL}/{endpoint_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)

        # 200 = success, 400 = exists but needs parameters
        if response.status_code in [200, 400]:
            return {
                "endpoint_id": endpoint_id,
                "status_code": response.status_code,
                "exists": True,
                "preview": str(response.text[:200]) if response.text else ""
            }
        else:
            return {"endpoint_id": endpoint_id, "exists": False}

    except Exception as e:
        return {"endpoint_id": endpoint_id, "exists": False, "error": str(e)}


def discover_by_pattern(access_token, subscription_key):
    """Discover endpoints by testing known patterns."""
    print("\nMethod 2: Testing known endpoint patterns...")
    print("(This may take a few moments...)")

    # Known endpoint patterns based on documentation
    known_patterns = [
        # NP3 series
        "np3-965-er", "np3-966-er",
        # NP4 series
        "np4-33-cd", "np4-183-cd", "np4-190-cd", "np4-191-cd", "np4-732-cd",
        # NP6 series
        "np6-86-cd", "np6-787-cd", "np6-788-cd", "np6-905-cd", "np6-970-cd",
    ]

    discovered = []

    for pattern in known_patterns:
        result = test_endpoint_pattern(access_token, subscription_key, pattern)

        if result.get("exists"):
            print(f"  ✓ Found: {pattern} (HTTP {result['status_code']})")
            discovered.append(result)
        else:
            print(f"  ✗ Not found: {pattern}")

    return discovered


def get_endpoint_details(access_token, subscription_key, endpoint_id):
    """Try to get detailed information about an endpoint."""
    url = f"{BASE_API_URL}/{endpoint_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            # Endpoint exists but needs parameters
            error_data = response.json()
            return {
                "endpoint_id": endpoint_id,
                "status": "requires_parameters",
                "error_message": error_data
            }
        else:
            return {"endpoint_id": endpoint_id, "status": "unknown"}

    except Exception as e:
        return {"endpoint_id": endpoint_id, "error": str(e)}


def scrape_api_explorer():
    """Attempt to scrape endpoint list from API Explorer page."""
    print("\nMethod 3: Scraping API Explorer page...")

    explorer_url = "https://apiexplorer.ercot.com/api-details#api=pubapi-apim-api"

    try:
        response = requests.get(explorer_url, timeout=10)

        if response.status_code == 200:
            # Look for endpoint patterns in HTML
            endpoints = re.findall(r'np[0-9]-[0-9]+-[a-z]+(?:/[a-z_0-9]+)?', response.text)

            if endpoints:
                unique_endpoints = sorted(set(endpoints))
                print(f"✓ Found {len(unique_endpoints)} endpoint references in HTML")
                return unique_endpoints
            else:
                print("⚠ No endpoints found in HTML (may require JavaScript rendering)")
                return []
        else:
            print(f"⚠ API Explorer returned status {response.status_code}")
            return []

    except Exception as e:
        print(f"✗ Error scraping API Explorer: {e}")
        return []


def save_results(discovered_endpoints, detailed_info):
    """Save discovery results to files."""
    print("\nSaving results...")

    # Save unique endpoint IDs
    with open("discovered_endpoints.json", "w") as f:
        json.dump({
            "discovered_at": str(Path.cwd()),
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
    print("ERCOT API Endpoint Discovery")
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

    all_discovered = []
    detailed_info = []

    # Step 2: Discover from base API
    base_endpoints = discover_base_endpoints(access_token, subscription_key)
    all_discovered.extend(base_endpoints)

    # Step 3: Test known patterns
    pattern_results = discover_by_pattern(access_token, subscription_key)
    for result in pattern_results:
        if result["endpoint_id"] not in all_discovered:
            all_discovered.append(result["endpoint_id"])
    detailed_info.extend(pattern_results)

    # Step 4: Scrape API Explorer
    explorer_endpoints = scrape_api_explorer()
    for endpoint in explorer_endpoints:
        # Extract just the base endpoint ID (before the /)
        base_endpoint = endpoint.split('/')[0]
        if base_endpoint not in all_discovered:
            all_discovered.append(base_endpoint)

    # Remove duplicates and sort
    all_discovered = sorted(set(all_discovered))

    # Save results
    save_results(all_discovered, detailed_info)

    # Summary
    print()
    print("=" * 60)
    print("Discovery Summary")
    print("=" * 60)
    print(f"Total unique endpoints discovered: {len(all_discovered)}")
    print()
    print("Discovered endpoints:")
    for endpoint in all_discovered:
        print(f"  • {endpoint}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
