#!/usr/bin/env python3
"""
Daily DAM Settlement Point Prices Collector

Automatically collects Day-Ahead Market settlement point prices for the previous day.
Designed to run daily via cron at 1 AM to collect yesterday's data.

Usage:
    python3 scripts/daily_dam_settlement_prices.py [--settlement-point HB_HOUSTON] [--debug]

Example cron entry (runs daily at 1 AM):
    0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py
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
    Calculate yesterday's date range (midnight to 11:59 PM).

    Returns:
        tuple: (date_from, date_to) as strings in YYYY-MM-DD format
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    return date_str, date_str


def collect_dam_settlement_prices(settlement_point='HB_HOUSTON', debug=False):
    """
    Collect DAM settlement point prices for yesterday.

    Args:
        settlement_point (str): Settlement point to query (default: HB_HOUSTON)
        debug (bool): Enable debug output

    Returns:
        bool: True if successful, False otherwise
    """
    # Calculate yesterday's date
    date_from, date_to = get_yesterday_dates()

    print("=" * 60)
    print("Daily DAM Settlement Point Prices Collection")
    print("=" * 60)
    print(f"Settlement Point: {settlement_point}")
    print(f"Date Range: {date_from} to {date_to}")
    print()

    # Initialize ERCOT API client
    client = ERCOTAPIClient(debug=debug)

    # Authenticate
    if not client.authenticate():
        print("✗ Authentication failed")
        return False

    # Define API endpoint and parameters
    endpoint = "np4-190-cd/dam_stlmnt_pnt_prices"
    parameters = {
        "deliveryDateFrom": date_from,
        "deliveryDateTo": date_to,
        "settlementPoint": settlement_point
    }

    # Query the API
    print(f"Querying endpoint: {endpoint}")
    print(f"Parameters: {parameters}")
    print()

    response_data = client.query_api(endpoint, parameters)

    if response_data is None:
        print("✗ Query failed")
        return False

    # Create output directory structure: output/daily/dam/YYYY/MM/
    output_dir = Path("output/daily/dam") / date_from[:4] / date_from[5:7]
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename: settlement_prices_HB_HOUSTON_2025-01-27.json
    output_file = output_dir / f"settlement_prices_{settlement_point}_{date_from}.json"

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
        description='Collect DAM settlement point prices for yesterday',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect for default settlement point (HB_HOUSTON)
  python3 scripts/daily_dam_settlement_prices.py

  # Collect for specific settlement point
  python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_NORTH

  # Enable debug output
  python3 scripts/daily_dam_settlement_prices.py --debug

Available Settlement Points:
  HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON, HB_BUSAVG, HB_PAN
        """
    )

    parser.add_argument(
        '--settlement-point',
        default='HB_HOUSTON',
        help='Settlement point to query (default: HB_HOUSTON)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    args = parser.parse_args()

    # Run collection
    success = collect_dam_settlement_prices(
        settlement_point=args.settlement_point,
        debug=args.debug
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
