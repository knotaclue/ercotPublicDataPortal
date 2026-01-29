#!/usr/bin/env python3
"""
TEMPLATE - Incremental Poller

This is a template for creating new incremental polling scripts.
Copy this file and modify it for your specific endpoint.

Usage:
    1. Copy this file: cp TEMPLATE_incremental_poller.py incremental_your_endpoint.py
    2. Update ENDPOINT, STATE_FILE, and OUTPUT_DIR_BASE
    3. Adjust parameter names if needed (deliveryDate vs SCEDTimestamp)
    4. Test it: python3 scripts/incremental_your_endpoint.py --debug
    5. Add to cron if needed

Example cron entry (runs every 15 minutes):
    */15 * * * * cd /path/to/ercot-api-query && python3 scripts/incremental_your_endpoint.py
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import ercot_query module
sys.path.insert(0, str(Path(__file__).parent.parent))

from ercot_query import ERCOTAPIClient


# TODO: Update these configuration values for your endpoint
# ==========================================================

# State file location (make it unique per endpoint)
STATE_DIR = Path("state")
STATE_FILE = STATE_DIR / "incremental_YOUR_ENDPOINT_state.json"

# Your ERCOT API endpoint
ENDPOINT = "np6-xxx-cd/your_endpoint"

# Base output directory
OUTPUT_DIR_BASE = Path("output/incremental/your_endpoint")

# Poll interval (minutes) - how often the script runs
POLL_INTERVAL_MINUTES = 15

# Parameter type: "SCED" for SCEDTimestamp or "DAM" for deliveryDate
PARAMETER_TYPE = "SCED"  # or "DAM"

# ==========================================================


def ensure_directories():
    """Create necessary directories if they don't exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_BASE.mkdir(parents=True, exist_ok=True)


def read_state():
    """
    Read the last successful poll state.

    Returns:
        dict: State containing last_timestamp and other metadata
              Returns None if state file doesn't exist (first run)
    """
    if not STATE_FILE.exists():
        return None

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        return state
    except Exception as e:
        print(f"⚠ Warning: Could not read state file: {e}")
        return None


def write_state(timestamp_to, records_retrieved):
    """
    Write the current state after successful poll.

    Args:
        timestamp_to (str): The latest timestamp successfully retrieved
        records_retrieved (int): Number of records retrieved in this poll
    """
    state = {
        "last_timestamp": timestamp_to,
        "last_poll_time": datetime.now().isoformat(),
        "last_records_retrieved": records_retrieved,
        "endpoint": ENDPOINT
    }

    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print(f"✗ Error writing state file: {e}")
        return False


def calculate_time_range(last_state, debug=False):
    """
    Calculate the time range to query based on last state.

    Args:
        last_state (dict): Previous state, or None for first run
        debug (bool): Enable debug output

    Returns:
        tuple: (timestamp_from, timestamp_to) as appropriate format strings
    """
    now = datetime.now()

    if last_state is None:
        # First run - get last N minutes
        timestamp_from = (now - timedelta(minutes=POLL_INTERVAL_MINUTES)).replace(microsecond=0)
        if debug:
            print(f"[DEBUG] First run - querying last {POLL_INTERVAL_MINUTES} minutes")
    else:
        # Incremental - start from 1 second after last timestamp
        last_timestamp = datetime.fromisoformat(last_state['last_timestamp'])
        timestamp_from = last_timestamp + timedelta(seconds=1)
        if debug:
            print(f"[DEBUG] Incremental run - last poll was at {last_state['last_timestamp']}")
            print(f"[DEBUG] Last poll retrieved {last_state.get('last_records_retrieved', 'unknown')} records")

    timestamp_to = now.replace(microsecond=0)

    # Format based on parameter type
    if PARAMETER_TYPE == "SCED":
        # Real-time endpoints use: YYYY-MM-DDTHH:MM:SS
        timestamp_from_str = timestamp_from.strftime('%Y-%m-%dT%H:%M:%S')
        timestamp_to_str = timestamp_to.strftime('%Y-%m-%dT%H:%M:%S')
    else:  # DAM
        # Day-ahead endpoints use: YYYY-MM-DD
        timestamp_from_str = timestamp_from.strftime('%Y-%m-%d')
        timestamp_to_str = timestamp_to.strftime('%Y-%m-%d')

    return timestamp_from_str, timestamp_to_str


def poll_incremental(debug=False):
    """
    Poll the API for new data since last successful poll.

    Args:
        debug (bool): Enable debug output

    Returns:
        bool: True if successful, False otherwise
    """
    print("=" * 60)
    print(f"Incremental Poller: {ENDPOINT}")  # TODO: Update display name
    print("=" * 60)

    ensure_directories()

    # Read last state
    last_state = read_state()

    if last_state is None:
        print(f"First run detected - will retrieve last {POLL_INTERVAL_MINUTES} minutes")
    else:
        last_poll = datetime.fromisoformat(last_state['last_poll_time'])
        print(f"Last successful poll: {last_poll.strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate time range for this query
    timestamp_from, timestamp_to = calculate_time_range(last_state, debug)

    print(f"Querying new data from: {timestamp_from}")
    print(f"                    to: {timestamp_to}")
    print()

    # Check if there's actually a time gap to query
    from_dt = datetime.fromisoformat(timestamp_from.replace('T', ' ')) if 'T' in timestamp_from else datetime.strptime(timestamp_from, '%Y-%m-%d')
    to_dt = datetime.fromisoformat(timestamp_to.replace('T', ' ')) if 'T' in timestamp_to else datetime.strptime(timestamp_to, '%Y-%m-%d')

    if from_dt >= to_dt:
        print("⚠ No new time range to query (already up to date)")
        return True

    # Initialize ERCOT API client
    client = ERCOTAPIClient(debug=debug)

    # Authenticate
    if not client.authenticate():
        print("✗ Authentication failed")
        return False

    # TODO: Define API parameters based on your endpoint
    if PARAMETER_TYPE == "SCED":
        parameters = {
            "SCEDTimestampFrom": timestamp_from,
            "SCEDTimestampTo": timestamp_to
            # TODO: Add any additional parameters your endpoint needs
        }
    else:  # DAM
        parameters = {
            "deliveryDateFrom": timestamp_from,
            "deliveryDateTo": timestamp_to
            # TODO: Add any additional parameters your endpoint needs
        }

    # Query the API
    print(f"Querying endpoint: {ENDPOINT}")
    if debug:
        print(f"Parameters: {parameters}")
    print()

    response_data = client.query_api(ENDPOINT, parameters)

    if response_data is None:
        print("✗ Query failed - state not updated")
        return False

    # Count records retrieved
    records_count = 0
    if isinstance(response_data, dict):
        if 'data' in response_data:
            records_count = len(response_data['data'])
        elif '_meta' in response_data and 'totalRecords' in response_data['_meta']:
            records_count = response_data['_meta']['totalRecords']
        elif 'report' in response_data:
            records_count = len(response_data.get('report', {}).get('data', []))

    print(f"✓ Retrieved {records_count} new records")

    # Generate output filename with timestamp range
    from_str = from_dt.strftime('%Y%m%d_%H%M%S')
    to_str = to_dt.strftime('%Y%m%d_%H%M%S')

    # Organize by date and hour (or just date for DAM)
    date_str = to_dt.strftime('%Y-%m-%d')
    if PARAMETER_TYPE == "SCED":
        hour_str = to_dt.strftime('%H')
        output_dir = OUTPUT_DIR_BASE / date_str / hour_str
    else:
        output_dir = OUTPUT_DIR_BASE / date_str

    output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Update output filename prefix
    output_file = output_dir / f"data_{from_str}_to_{to_str}.json"

    # Save the response
    client.save_response(response_data, str(output_file))

    # Update state file with latest timestamp
    if write_state(timestamp_to, records_count):
        print("✓ State updated successfully")
    else:
        print("⚠ Warning: Data saved but state update failed")

    print()
    print("=" * 60)
    print("✓ Incremental poll completed successfully!")
    print("=" * 60)

    return True


def show_status():
    """Display current state status."""
    print("=" * 60)
    print("Incremental Poller Status")
    print("=" * 60)

    state = read_state()

    if state is None:
        print("Status: Never run (no state file)")
        print(f"Next run will retrieve last {POLL_INTERVAL_MINUTES} minutes of data")
    else:
        print(f"Endpoint: {state['endpoint']}")
        print(f"Last Poll: {state['last_poll_time']}")
        print(f"Last Timestamp Retrieved: {state['last_timestamp']}")
        print(f"Records in Last Poll: {state.get('last_records_retrieved', 'unknown')}")

        last_poll = datetime.fromisoformat(state['last_poll_time'])
        time_since = datetime.now() - last_poll
        print(f"Time Since Last Poll: {time_since}")

        # Calculate what will be queried next
        timestamp_from, timestamp_to = calculate_time_range(state)
        print(f"\nNext poll will query:")
        print(f"  From: {timestamp_from}")
        print(f"  To:   {timestamp_to}")

    print("=" * 60)


def reset_state():
    """Reset the state file (useful for testing or recovery)."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        print("✓ State file deleted")
    else:
        print("No state file to delete")


def main():
    """Main function to parse arguments and run incremental poll."""
    parser = argparse.ArgumentParser(
        description='Incremental polling for YOUR ENDPOINT',  # TODO: Update description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Run incremental poll (normal operation)
  python3 scripts/incremental_your_endpoint.py

  # Run with debug output
  python3 scripts/incremental_your_endpoint.py --debug

  # Check current status
  python3 scripts/incremental_your_endpoint.py --status

  # Reset state (start fresh)
  python3 scripts/incremental_your_endpoint.py --reset

Cron Setup (every {POLL_INTERVAL_MINUTES} minutes):
  */{POLL_INTERVAL_MINUTES} * * * * cd /path/to/ercot-api-query && python3 scripts/incremental_your_endpoint.py

State File Location:
  {STATE_FILE}

Output Location:
  {OUTPUT_DIR_BASE}/YYYY-MM-DD/HH/data_YYYYMMDD_HHMMSS_to_YYYYMMDD_HHMMSS.json
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current state status and exit'
    )

    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset state file (next run will be like first run)'
    )

    args = parser.parse_args()

    # Handle special commands
    if args.status:
        show_status()
        sys.exit(0)

    if args.reset:
        reset_state()
        sys.exit(0)

    # Run incremental poll
    success = poll_incremental(debug=args.debug)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
