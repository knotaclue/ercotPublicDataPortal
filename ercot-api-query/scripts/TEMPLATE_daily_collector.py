#!/usr/bin/env python3
"""
TEMPLATE - Daily Data Collector

This is a template for creating new daily data collection scripts.
Copy this file and modify it for your specific endpoint.

Usage:
    1. Copy this file: cp TEMPLATE_daily_collector.py daily_your_endpoint.py
    2. Update the endpoint and parameters in collect_data()
    3. Update the docstrings and help text
    4. Make it executable: chmod +x daily_your_endpoint.py
    5. Test it: python3 scripts/daily_your_endpoint.py --debug
    6. Add to cron if needed

Example cron entry (runs daily at 1 AM):
    0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_your_endpoint.py
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import ercot_query module
sys.path.insert(0, str(Path(__file__).parent.parent))

from ercot_query import ERCOTAPIClient


def get_yesterday_dates():
    """
    Calculate yesterday's date range for DAM endpoints (YYYY-MM-DD format).

    Returns:
        tuple: (date_from, date_to) as strings in YYYY-MM-DD format
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    return date_str, date_str


def get_yesterday_timestamps():
    """
    Calculate yesterday's timestamp range for RTM endpoints (00:00:00 to 23:59:59).

    Returns:
        tuple: (timestamp_from, timestamp_to) as strings in YYYY-MM-DDTHH:MM:SS format
    """
    yesterday = datetime.now() - timedelta(days=1)
    timestamp_from = yesterday.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%S')
    timestamp_to = yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%dT%H:%M:%S')
    return timestamp_from, timestamp_to


def collect_data(debug=False):
    """
    Collect data for yesterday.

    TODO: Update this function for your specific endpoint

    Args:
        debug (bool): Enable debug output

    Returns:
        bool: True if successful, False otherwise
    """
    # TODO: Choose the appropriate date function for your endpoint
    # For DAM endpoints, use get_yesterday_dates()
    # For RTM endpoints, use get_yesterday_timestamps()

    # Example for DAM endpoint:
    date_from, date_to = get_yesterday_dates()
    date_str = date_from

    # Example for RTM endpoint:
    # timestamp_from, timestamp_to = get_yesterday_timestamps()
    # date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("=" * 60)
    print("Daily Data Collection - YOUR ENDPOINT NAME")  # TODO: Update title
    print("=" * 60)
    print(f"Date: {date_str}")
    print()

    # Initialize ERCOT API client
    client = ERCOTAPIClient(debug=debug)

    # Authenticate
    if not client.authenticate():
        print("✗ Authentication failed")
        return False

    # TODO: Define your API endpoint and parameters
    endpoint = "np4-xxx-cd/your_endpoint"  # TODO: Update endpoint

    # For DAM endpoints, use deliveryDate parameters:
    parameters = {
        "deliveryDateFrom": date_from,
        "deliveryDateTo": date_to
        # TODO: Add any additional parameters your endpoint needs
    }

    # For RTM endpoints, use SCEDTimestamp parameters:
    # parameters = {
    #     "SCEDTimestampFrom": timestamp_from,
    #     "SCEDTimestampTo": timestamp_to
    #     # TODO: Add any additional parameters your endpoint needs
    # }

    # Query the API
    print(f"Querying endpoint: {endpoint}")
    print(f"Parameters: {parameters}")
    print()

    response_data = client.query_api(endpoint, parameters)

    if response_data is None:
        print("✗ Query failed")
        return False

    # TODO: Update output directory structure
    # Create output directory structure: output/daily/YOUR_CATEGORY/YYYY/MM/
    output_dir = Path("output/daily/your_category") / date_str[:4] / date_str[5:7]
    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Update output filename
    # Generate output filename: your_data_2025-01-27.json
    output_file = output_dir / f"your_data_{date_str}.json"

    # Save the response
    client.save_response(response_data, str(output_file))

    print()
    print("=" * 60)
    print("✓ Collection completed successfully!")
    print("=" * 60)

    return True


def main():
    """Main function to parse arguments and run collection."""
    parser = argparse.ArgumentParser(
        description='Collect YOUR DATA for yesterday',  # TODO: Update description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect data for yesterday
  python3 scripts/daily_your_endpoint.py

  # Enable debug output
  python3 scripts/daily_your_endpoint.py --debug

TODO: Add your own help text and examples here
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    # TODO: Add any additional command-line arguments your script needs
    # parser.add_argument(
    #     '--your-option',
    #     default='default_value',
    #     help='Description of your option'
    # )

    args = parser.parse_args()

    # Run collection
    success = collect_data(debug=args.debug)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
