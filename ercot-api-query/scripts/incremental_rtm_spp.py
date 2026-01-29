#!/usr/bin/env python3
"""
Incremental Real-Time LMP Poller

Polls the ERCOT API every 15 minutes and retrieves ONLY new data since the last successful poll.
Tracks state to avoid duplicate data retrieval.

Usage:
    python3 scripts/incremental_rtm_spp.py [--debug]

Cron Example (runs every 15 minutes):
    */15 * * * * cd /path/to/ercot-api-query && python3 scripts/incremental_rtm_spp.py

How It Works:
    1. Reads last successful timestamp from state file
    2. Queries API for data from (last_timestamp + 1 second) to now
    3. Saves new data to timestamped file
    4. Updates state file with latest timestamp retrieved
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


# State file location
STATE_DIR = Path("state")
STATE_FILE = STATE_DIR / "incremental_rtm_lmp_state.json"

# Configuration
# Using LMP endpoint which supports SCEDTimestamp parameters
ENDPOINT = "np6-788-cd/lmp_node_zone_hub"
OUTPUT_DIR_BASE = Path("output/incremental/rtm_lmp")


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
        tuple: (timestamp_from, timestamp_to) as ISO format strings
    """
    now = datetime.now()

    if last_state is None:
        # First run - get last 15 minutes
        timestamp_from = (now - timedelta(minutes=15)).replace(microsecond=0)
        if debug:
            print("[DEBUG] First run - querying last 15 minutes")
    else:
        # Incremental - start from 1 second after last timestamp
        last_timestamp = datetime.fromisoformat(last_state['last_timestamp'])
        timestamp_from = last_timestamp + timedelta(seconds=1)
        if debug:
            print(f"[DEBUG] Incremental run - last poll was at {last_state['last_timestamp']}")
            print(f"[DEBUG] Last poll retrieved {last_state.get('last_records_retrieved', 'unknown')} records")

    timestamp_to = now.replace(microsecond=0)

    # Format as ISO strings
    timestamp_from_str = timestamp_from.strftime('%Y-%m-%dT%H:%M:%S')
    timestamp_to_str = timestamp_to.strftime('%Y-%m-%dT%H:%M:%S')

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
    print("Incremental Real-Time SPP Poller")
    print("=" * 60)

    ensure_directories()

    # Read last state
    last_state = read_state()

    if last_state is None:
        print("First run detected - will retrieve last 15 minutes")
    else:
        last_poll = datetime.fromisoformat(last_state['last_poll_time'])
        print(f"Last successful poll: {last_poll.strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate time range for this query
    timestamp_from, timestamp_to = calculate_time_range(last_state, debug)

    print(f"Querying new data from: {timestamp_from}")
    print(f"                    to: {timestamp_to}")
    print()

    # Check if there's actually a time gap to query
    from_dt = datetime.fromisoformat(timestamp_from)
    to_dt = datetime.fromisoformat(timestamp_to)

    if from_dt >= to_dt:
        print("⚠ No new time range to query (already up to date)")
        return True

    # Initialize ERCOT API client
    client = ERCOTAPIClient(debug=debug)

    # Authenticate
    if not client.authenticate():
        print("✗ Authentication failed")
        return False

    # Define API parameters
    parameters = {
        "SCEDTimestampFrom": timestamp_from,
        "SCEDTimestampTo": timestamp_to
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

    # Organize by date and hour
    date_str = to_dt.strftime('%Y-%m-%d')
    hour_str = to_dt.strftime('%H')

    output_dir = OUTPUT_DIR_BASE / date_str / hour_str
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"lmp_{from_str}_to_{to_str}.json"

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
        print("Next run will retrieve last 15 minutes of data")
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
        description='Incremental polling for Real-Time LMP data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run incremental poll (normal operation)
  python3 scripts/incremental_rtm_spp.py

  # Run with debug output
  python3 scripts/incremental_rtm_spp.py --debug

  # Check current status
  python3 scripts/incremental_rtm_spp.py --status

  # Reset state (start fresh)
  python3 scripts/incremental_rtm_spp.py --reset

Cron Setup (every 15 minutes):
  */15 * * * * cd /path/to/ercot-api-query && python3 scripts/incremental_rtm_spp.py

State File Location:
  state/incremental_rtm_lmp_state.json

Output Location:
  output/incremental/rtm_lmp/YYYY-MM-DD/HH/lmp_YYYYMMDD_HHMMSS_to_YYYYMMDD_HHMMSS.json
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
