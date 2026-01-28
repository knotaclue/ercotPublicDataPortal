# ERCOT API Query Tool - Complete Usage Guide

This guide explains the three different ways to use this tool, helping you choose the right approach for your needs.

---

## 📊 Three Usage Scenarios

### 1. **Manual/Ad-Hoc Queries** - One-time data retrieval
### 2. **Daily Collection** - Automatic previous day data (runs once daily)
### 3. **Incremental Polling** - Continuous real-time collection (runs every 15 minutes)

---

## Scenario 1: Manual/Ad-Hoc Queries

**Best for:** One-time data pulls, historical research, custom date ranges, exploring the API

### How It Works

You create a JSON configuration file specifying exactly what you want to query, then run it manually.

### Quick Start

```bash
# Run a predefined query
python3 ercot_query.py --config queries/realtime_system_load.json

# With debug output
python3 ercot_query.py --config queries/settlement_point_prices.json --debug
```

### Creating Custom Queries

**Step 1:** Create a JSON config file in the `queries/` directory:

```json
{
  "endpoint": "np4-190-cd/dam_stlmnt_pnt_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-15",
    "deliveryDateTo": "2025-01-20",
    "settlementPoint": "HB_HOUSTON"
  },
  "output_file": "output/my_custom_query.json"
}
```

**Step 2:** Run it:

```bash
python3 ercot_query.py --config queries/my_custom_query.json
```

### When to Use This Approach

✅ **Use when:**
- You need a specific date range (not just yesterday)
- You're doing one-time historical analysis
- You're exploring different endpoints
- You need custom parameters
- You want full control over the query

❌ **Don't use when:**
- You need daily automated collection
- You want continuous real-time updates
- You're building a monitoring system

### Example Use Cases

1. **Research Project**: "I need DAM prices for Houston from Jan 1-15, 2025"
   ```bash
   # Create queries/research_jan.json with those dates
   python3 ercot_query.py --config queries/research_jan.json
   ```

2. **Compare Multiple Hubs**: "I want to compare prices across all trading hubs for a specific week"
   ```bash
   # Create separate configs for each hub
   python3 ercot_query.py --config queries/houston_week1.json
   python3 ercot_query.py --config queries/north_week1.json
   python3 ercot_query.py --config queries/south_week1.json
   ```

3. **Archive Download**: "I need to download a specific archived report"
   ```bash
   # Create config with archive endpoint and document ID
   python3 ercot_query.py --config queries/archive_download.json
   ```

### Output Location

Data is saved wherever you specify in `output_file`, or auto-generated if not specified.

---

## Scenario 2: Daily Collection (Previous Day)

**Best for:** Daily retrospective reporting, regulatory compliance, daily analysis workflows

### How It Works

Scripts automatically calculate "yesterday" (midnight to 11:59 PM) and collect that full day's data. Perfect for running at 1 AM every day via cron.

### Available Scripts

**1. DAM Settlement Prices** (`scripts/daily_dam_settlement_prices.py`)
```bash
# Default (Houston Hub)
python3 scripts/daily_dam_settlement_prices.py

# Specific hub
python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_NORTH

# Available: HB_HOUSTON, HB_NORTH, HB_SOUTH, HB_WEST, HB_BUSAVG, HB_PAN
```

**2. Real-Time LMP** (`scripts/daily_rtm_lmp.py`)
```bash
# Collects yesterday's RTM LMP data (nodes, zones, hubs)
python3 scripts/daily_rtm_lmp.py
```

**3. 15-Minute Settlement Point Prices** (`scripts/daily_spp_15min.py`)
```bash
# Collects yesterday's 15-minute interval data
python3 scripts/daily_spp_15min.py
```

### Setting Up Cron (Automated Daily Collection)

Edit your crontab:
```bash
crontab -e
```

Add entries to run at 1 AM every day:
```bash
# DAM prices at 1:00 AM
0 1 * * * cd /home/user/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py

# RTM LMP at 1:15 AM
15 1 * * * cd /home/user/ercot-api-query && python3 scripts/daily_rtm_lmp.py

# 15-min SPP at 1:30 AM
30 1 * * * cd /home/user/ercot-api-query && python3 scripts/daily_spp_15min.py
```

**Important:** Use absolute paths to your project directory!

### What Happens Automatically

- Script runs at 1 AM on January 28
- It automatically calculates: "Yesterday = January 27"
- Queries: January 27, 00:00:00 to January 27, 23:59:59
- Saves to: `output/daily/dam/2025/01/settlement_prices_HB_HOUSTON_2025-01-27.json`

### When to Use This Approach

✅ **Use when:**
- You need complete daily datasets
- You want "yesterday's data" every day
- You're building daily reports or dashboards
- You need reliable daily archives
- Regulatory/compliance reporting

❌ **Don't use when:**
- You need real-time or near-real-time data
- You need data more frequently than once per day
- You need custom date ranges

### Example Use Cases

1. **Daily Price Report**: "Every morning, I need yesterday's DAM prices for all hubs"
   ```bash
   # Set up cron for all hubs
   0 1 * * * cd /path && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_HOUSTON
   0 1 * * * cd /path && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_NORTH
   0 1 * * * cd /path && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_SOUTH
   ```

2. **Regulatory Archive**: "I need to maintain a complete archive of daily LMP data"
   ```bash
   # One cron job, runs every day, builds your archive automatically
   15 1 * * * cd /path && python3 scripts/daily_rtm_lmp.py
   ```

3. **Morning Dashboard**: "My dashboard shows yesterday's market activity"
   ```bash
   # Run all daily scripts at 1 AM, dashboard refreshes at 2 AM
   ```

### Output Location

```
output/daily/
├── dam/YYYY/MM/settlement_prices_HUB_DATE.json
├── rtm/YYYY/MM/lmp_node_zone_hub_DATE.json
└── spp/YYYY/MM/spp_15min_DATE.json
```

### Debugging

```bash
# Run with debug flag to see what dates are being calculated
python3 scripts/daily_dam_settlement_prices.py --debug
```

---

## Scenario 3: Incremental Polling (Continuous Collection)

**Best for:** Real-time monitoring, live dashboards, event detection, operational systems

### How It Works

Scripts track the last timestamp they retrieved, then query ONLY new data since that point. Runs every 15 minutes and never re-downloads old data.

### Available Scripts

**Real-Time LMP Incremental Poller** (`scripts/incremental_rtm_spp.py`)

```bash
# Normal operation (run every 15 minutes via cron)
python3 scripts/incremental_rtm_spp.py

# Check current status
python3 scripts/incremental_rtm_spp.py --status

# Reset state (start fresh)
python3 scripts/incremental_rtm_spp.py --reset

# Debug mode
python3 scripts/incremental_rtm_spp.py --debug
```

### How State Tracking Works

**First Run:**
```
10:00 AM - No state file exists
         → Queries: 9:45 AM to 10:00 AM (last 15 minutes)
         → Retrieves: 1,000 records
         → Saves state: "last_timestamp": "2025-01-28T10:00:00"
```

**Second Run:**
```
10:15 AM - Reads state file
         → Last timestamp was 10:00:00
         → Queries: 10:00:01 to 10:15:00 (NEW DATA ONLY!)
         → Retrieves: 300 NEW records
         → Updates state: "last_timestamp": "2025-01-28T10:15:00"
```

**Third Run:**
```
10:30 AM - Reads state file
         → Last timestamp was 10:15:00
         → Queries: 10:15:01 to 10:30:00 (NEW DATA ONLY!)
         → Retrieves: 275 NEW records
         → Updates state: "last_timestamp": "2025-01-28T10:30:00"
```

**No duplicate data!** Each poll only gets records you haven't seen before.

### Setting Up Cron (Automated Incremental Collection)

Edit your crontab:
```bash
crontab -e
```

Add entry to run every 15 minutes:
```bash
# Run incremental RTM LMP poller every 15 minutes
*/15 * * * * cd /home/user/ercot-api-query && python3 scripts/incremental_rtm_spp.py
```

### Monitoring Your Poller

**Check status:**
```bash
python3 scripts/incremental_rtm_spp.py --status
```

**Output:**
```
============================================================
Incremental Poller Status
============================================================
Endpoint: np6-788-cd/lmp_node_zone_hub
Last Poll: 2025-01-28T10:30:00.123456
Last Timestamp Retrieved: 2025-01-28T10:30:00
Records in Last Poll: 275
Time Since Last Poll: 0:05:23

Next poll will query:
  From: 2025-01-28T10:30:01
  To:   2025-01-28T10:35:23
============================================================
```

### When to Use This Approach

✅ **Use when:**
- You need real-time or near-real-time data
- You're building live monitoring systems
- You want to detect events as they happen
- You need continuous data feeds
- You're feeding a live dashboard or alerting system

❌ **Don't use when:**
- You only need daily summaries (use daily scripts instead)
- You need historical data (use manual queries)
- Bandwidth/API costs are a concern (daily scripts use less)

### Example Use Cases

1. **Live Price Monitor**: "I need to track LMP prices as they're published every 5 minutes"
   ```bash
   # Cron runs every 15 minutes, captures all new price updates
   */15 * * * * cd /path && python3 scripts/incremental_rtm_spp.py
   ```

2. **Event Detection**: "Alert me when prices spike above $100/MWh"
   ```bash
   # Incremental poller feeds analysis script that checks for spikes
   */15 * * * * cd /path && python3 scripts/incremental_rtm_spp.py
   */15 * * * * cd /path && python3 scripts/check_price_spikes.py
   ```

3. **Real-Time Dashboard**: "My dashboard shows current market conditions"
   ```bash
   # Poller runs every 15 minutes, dashboard refreshes from latest data
   */15 * * * * cd /path && python3 scripts/incremental_rtm_spp.py
   ```

### State File Location

```
state/incremental_rtm_lmp_state.json
```

**Example state file:**
```json
{
  "last_timestamp": "2025-01-28T10:30:00",
  "last_poll_time": "2025-01-28T10:30:02.123456",
  "last_records_retrieved": 275,
  "endpoint": "np6-788-cd/lmp_node_zone_hub"
}
```

### Output Location

```
output/incremental/rtm_lmp/
└── 2025-01-28/
    ├── 09/
    │   └── lmp_20250128_094500_to_20250128_100000.json
    ├── 10/
    │   ├── lmp_20250128_100001_to_20250128_101500.json
    │   ├── lmp_20250128_101501_to_20250128_103000.json
    │   └── lmp_20250128_103001_to_20250128_104500.json
    └── ...
```

Files are organized by date and hour for easy navigation.

### Recovery and Troubleshooting

**Reset state if something goes wrong:**
```bash
python3 scripts/incremental_rtm_spp.py --reset
# Next run will start fresh with last 15 minutes
```

**Debug issues:**
```bash
python3 scripts/incremental_rtm_spp.py --debug
```

---

## Comparison Table

| Feature | Manual Queries | Daily Collection | Incremental Polling |
|---------|---------------|------------------|---------------------|
| **Frequency** | On-demand | Once per day | Every 15 minutes |
| **Date Range** | Custom | Previous day (automatic) | Since last poll |
| **Automation** | No (manual) | Yes (cron) | Yes (cron) |
| **Use Case** | Research, ad-hoc | Daily reports | Real-time monitoring |
| **Duplicates** | Possible (if you rerun) | No (unique dates) | No (state tracked) |
| **Setup Complexity** | Simple | Medium | Advanced |
| **Resource Usage** | Low | Medium | Higher |
| **Best For** | Historical analysis | Compliance archives | Live dashboards |

---

## Creating Custom Scripts

### New Daily Collection Script

Use the template to collect a different endpoint daily:

```bash
# Copy template
cp scripts/TEMPLATE_daily_collector.py scripts/daily_my_endpoint.py

# Edit the configuration section (top of file):
# - Set ENDPOINT
# - Set parameters
# - Set output location

# Test it
python3 scripts/daily_my_endpoint.py --debug

# Add to cron
crontab -e
# Add: 0 1 * * * cd /path && python3 scripts/daily_my_endpoint.py
```

### New Incremental Polling Script

Use the template to create an incremental poller:

```bash
# Copy template
cp scripts/TEMPLATE_incremental_poller.py scripts/incremental_my_endpoint.py

# Edit the configuration section (top of file):
# - Set ENDPOINT
# - Set STATE_FILE (make it unique!)
# - Set OUTPUT_DIR_BASE
# - Set PARAMETER_TYPE ("SCED" or "DAM")
# - Set POLL_INTERVAL_MINUTES

# Test it
python3 scripts/incremental_my_endpoint.py --debug

# Check status
python3 scripts/incremental_my_endpoint.py --status

# Add to cron
crontab -e
# Add: */15 * * * * cd /path && python3 scripts/incremental_my_endpoint.py
```

---

## Complete Example: Building a Monitoring System

Let's say you want to monitor Houston's electricity market:

### Step 1: Daily Historical Archive
```bash
# Set up daily collection for complete daily records
crontab -e
# Add:
0 1 * * * cd /home/user/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_HOUSTON
```

### Step 2: Real-Time Monitoring
```bash
# Set up incremental polling for real-time prices
crontab -e
# Add:
*/15 * * * * cd /home/user/ercot-api-query && python3 scripts/incremental_rtm_spp.py
```

### Step 3: Ad-Hoc Analysis
```bash
# When you need custom date ranges or special queries
python3 ercot_query.py --config queries/houston_analysis.json
```

**Result:** You have both:
- Complete daily archives for long-term analysis
- Real-time data for immediate monitoring
- Flexibility for custom research

---

## Quick Decision Guide

**"Which approach should I use?"**

👉 **Use Manual Queries if:**
- "I need to analyze a specific week from last month"
- "I want to compare different parameters"
- "I'm just exploring the API"

👉 **Use Daily Collection if:**
- "I need yesterday's data every morning"
- "I'm building a compliance archive"
- "I want daily reports"

👉 **Use Incremental Polling if:**
- "I need to know prices as soon as they're published"
- "I'm building a live dashboard"
- "I want to detect events in real-time"

---

## Getting More Help

- **scripts/README.md** - Detailed automation documentation
- **README.md** - Main project documentation
- **EXAMPLES.md** - Real endpoint examples
- **TROUBLESHOOTING.md** - Common issues and solutions

---

**Ready to get started?** Pick your scenario above and follow the steps!
