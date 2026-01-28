#!/usr/bin/env python3
"""
Daily Real-Time LMP Collector

Automatically collects Real-Time Market LMP data for the previous day.
Designed to run daily via cron at 1 AM to collect yesterday's data.

Usage:
    python3 scripts/daily_rtm_lmp.py [--debug]

Example cron entry (runs daily at 1 AM):
    0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_rtm_lmp.py
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import ercot_query module
sys.path.insert(0, str(Path(__file__).parent.parent))

from ercot_query import ERCOTAPIClient


def get_yesterday_timestamps():
    """
    Calculate yesterday's timestamp range (00:00:00 to 23:59:59).

    Returns:
        tuple: (timestamp_from, timestamp_to) as strings in YYYY-MM-DDTHH:MM:SS format
    """
    yesterday = datetime.now() - timedelta(days=1)
    timestamp_from = yesterday.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%dT%H:%M:%S')
    timestamp_to = yesterday.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%dT%H:%M:%S')
    return timestamp_from, timestamp_to


def collect_rtm_lmp(debug=False):
    """
    Collect Real-Time Market LMP data for yesterday.

    Args:
        debug (bool): Enable debug output

    Returns:
        bool: True if successful, False otherwise
    """
    # Calculate yesterday's timestamp range
    timestamp_from, timestamp_to = get_yesterday_timestamps()
    date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    print("=" * 60)
    print("Daily Real-Time Market LMP Collection")
    print("=" * 60)
    print(f"Date: {date_str}")
    print(f"Timestamp Range: {timestamp_from} to {timestamp_to}")
    print()

    # Initialize ERCOT API client
    client = ERCOTAPIClient(debug=debug)

    # Authenticate
    if not client.authenticate():
        print("✗ Authentication failed")
        return False

    # Define API endpoint and parameters
    endpoint = "np6-788-cd/lmp_node_zone_hub"
    parameters = {
        "SCEDTimestampFrom": timestamp_from,
        "SCEDTimestampTo": timestamp_to
    }

    # Query the API
    print(f"Querying endpoint: {endpoint}")
    print(f"Parameters: {parameters}")
    print()

    response_data = client.query_api(endpoint, parameters)

    if response_data is None:
        print("✗ Query failed")
        return False

    # Create output directory structure: output/daily/rtm/YYYY/MM/
    output_dir = Path("output/daily/rtm") / date_str[:4] / date_str[5:7]
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename: lmp_node_zone_hub_2025-01-27.json
    output_file = output_dir / f"lmp_node_zone_hub_{date_str}.json"

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
        description='Collect Real-Time Market LMP data for yesterday',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect RTM LMP data for yesterday
  python3 scripts/daily_rtm_lmp.py

  # Enable debug output
  python3 scripts/daily_rtm_lmp.py --debug

Note:
  This script collects LMP data by resource node, load zone, and trading hub
  for the entire previous day (00:00:00 to 23:59:59).
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    args = parser.parse_args()

    # Run collection
    success = collect_rtm_lmp(debug=args.debug)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
