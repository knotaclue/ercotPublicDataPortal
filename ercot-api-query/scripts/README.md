# Automated Data Collection Scripts

This directory contains Python scripts for automated, intelligent data collection from the ERCOT API.

**Two Types of Collection:**
1. **Daily Scripts** - Collect previous day's complete data (run once daily at 1 AM)
2. **Incremental Scripts** - Collect only new data since last poll (run every 15 minutes)

---

## Incremental Polling Scripts (✨ NEW!)

### incremental_rtm_spp.py (Real-Time LMP)
**Purpose**: Polls every 15 minutes and retrieves ONLY new data since the last successful poll.

**Key Features:**
- ✅ **State Tracking**: Remembers last timestamp retrieved
- ✅ **No Duplicates**: Only fetches data you haven't seen before
- ✅ **Efficient**: Doesn't waste resources re-downloading old data
- ✅ **Self-Healing**: First run gets last 15 minutes, then incremental

**Example Scenario:**
```
12:00 PM Poll → Retrieves 11:45 AM - 12:00 PM (1000 records)
12:15 PM Poll → Retrieves 12:00:01 PM - 12:15 PM (300 new records only!)
12:30 PM Poll → Retrieves 12:15:01 PM - 12:30 PM (275 new records only!)
```

**Usage:**
```bash
# First run (gets last 15 minutes)
python3 scripts/incremental_rtm_spp.py

# Subsequent runs (gets only new data)
python3 scripts/incremental_rtm_spp.py

# Check status
python3 scripts/incremental_rtm_spp.py --status

# Reset state (start fresh)
python3 scripts/incremental_rtm_spp.py --reset

# Debug mode
python3 scripts/incremental_rtm_spp.py --debug
```

**Cron Setup** (every 15 minutes):
```bash
*/15 * * * * cd /path/to/ercot-api-query && python3 scripts/incremental_rtm_spp.py
```

**Output Location**: `output/incremental/rtm_lmp/YYYY-MM-DD/HH/lmp_YYYYMMDD_HHMMSS_to_YYYYMMDD_HHMMSS.json`

**State File**: `state/incremental_rtm_lmp_state.json`

---

## Daily Collection Scripts

### Available Scripts

### 1. `daily_dam_settlement_prices.py`
Collects Day-Ahead Market settlement point prices for yesterday.

**Endpoint**: `np4-190-cd/dam_stlmnt_pnt_prices`

**Usage**:
```bash
# Default (HB_HOUSTON)
python3 scripts/daily_dam_settlement_prices.py

# Specific settlement point
python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_NORTH

# With debug output
python3 scripts/daily_dam_settlement_prices.py --debug
```

**Available Settlement Points**: HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON, HB_BUSAVG, HB_PAN

**Output Location**: `output/daily/dam/YYYY/MM/settlement_prices_HB_HOUSTON_2025-01-27.json`

---

### 2. `daily_rtm_lmp.py`
Collects Real-Time Market LMP data (by node, zone, hub) for yesterday.

**Endpoint**: `np6-788-cd/lmp_node_zone_hub`

**Usage**:
```bash
# Collect RTM LMP data
python3 scripts/daily_rtm_lmp.py

# With debug output
python3 scripts/daily_rtm_lmp.py --debug
```

**Output Location**: `output/daily/rtm/YYYY/MM/lmp_node_zone_hub_2025-01-27.json`

---

### 3. `daily_spp_15min.py`
Collects 15-minute Settlement Point Prices for yesterday.

**Endpoint**: `np6-905-cd/spp_node_zone_hub`

**Usage**:
```bash
# Collect 15-minute SPP data
python3 scripts/daily_spp_15min.py

# With debug output
python3 scripts/daily_spp_15min.py --debug
```

**Output Location**: `output/daily/spp/YYYY/MM/spp_15min_2025-01-27.json`

**Note**: This can be a large dataset (15-minute intervals for all locations).

---

## How It Works

### Date Calculation
All scripts automatically calculate yesterday's date when run:

- **DAM Endpoints**: Use `deliveryDateFrom` and `deliveryDateTo` with format `YYYY-MM-DD`
- **RTM Endpoints**: Use `SCEDTimestampFrom` and `SCEDTimestampTo` with format `YYYY-MM-DDTHH:MM:SS`

For example, if run at 1 AM on January 28, 2025, the script collects data for January 27, 2025:
- DAM: `2025-01-27` to `2025-01-27`
- RTM: `2025-01-27T00:00:00` to `2025-01-27T23:59:59`

### Output Organization
Data is automatically organized by:
- Collection type (dam, rtm, spp)
- Year (YYYY)
- Month (MM)
- Filename includes date

Example structure:
```
output/
├── daily/
│   ├── dam/
│   │   └── 2025/
│   │       └── 01/
│   │           ├── settlement_prices_HB_HOUSTON_2025-01-27.json
│   │           └── settlement_prices_HB_HOUSTON_2025-01-28.json
│   ├── rtm/
│   │   └── 2025/
│   │       └── 01/
│   │           └── lmp_node_zone_hub_2025-01-27.json
│   └── spp/
│       └── 2025/
│           └── 01/
│               └── spp_15min_2025-01-27.json
```

---

## Setting Up Cron Jobs

### Run Daily at 1 AM

Edit your crontab:
```bash
crontab -e
```

Add entries for each script:
```bash
# Collect DAM settlement prices daily at 1 AM (Houston Hub)
0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py

# Collect DAM settlement prices for multiple hubs
0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_NORTH
0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_SOUTH
0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_WEST

# Collect RTM LMP data daily at 1:15 AM
15 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_rtm_lmp.py

# Collect 15-minute SPP data daily at 1:30 AM
30 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_spp_15min.py
```

### Logging Output

Redirect output to log files:
```bash
# With logging
0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py >> logs/daily_dam.log 2>&1

# Create logs directory first
mkdir -p /path/to/ercot-api-query/logs
```

---

## Creating New Incremental Scripts

Use the incremental template to create new intelligent pollers:

1. **Copy the template**:
```bash
cp scripts/TEMPLATE_incremental_poller.py scripts/incremental_your_endpoint.py
```

2. **Edit the configuration section** (top of file):
   - Update `ENDPOINT` (e.g., "np6-xxx-cd/your_endpoint")
   - Update `STATE_FILE` (make it unique)
   - Update `OUTPUT_DIR_BASE`
   - Set `PARAMETER_TYPE` ("SCED" for real-time, "DAM" for day-ahead)
   - Set `POLL_INTERVAL_MINUTES` (typically 15)

3. **Test it**:
```bash
python3 scripts/incremental_your_endpoint.py --debug
```

4. **Check state**:
```bash
python3 scripts/incremental_your_endpoint.py --status
```

5. **Add to cron**:
```bash
*/15 * * * * cd /path/to/ercot-api-query && python3 scripts/incremental_your_endpoint.py
```

---

## Creating New Daily Collection Scripts

Use the daily template to create new retrospective collectors:

1. **Copy the template**:
```bash
cp scripts/TEMPLATE_daily_collector.py scripts/daily_your_endpoint.py
```

2. **Edit the new script**:
   - Update the endpoint in `collect_data()`
   - Choose `get_yesterday_dates()` (DAM) or `get_yesterday_timestamps()` (RTM)
   - Update parameters for your endpoint
   - Update output directory and filename
   - Update docstrings and help text

3. **Test it**:
```bash
python3 scripts/daily_your_endpoint.py --debug
```

4. **Add to cron**:
```bash
0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_your_endpoint.py
```

---

## Testing Scripts

### Test Date Calculation
Run with debug to see what dates are being used:
```bash
python3 scripts/daily_dam_settlement_prices.py --debug
```

### Manual Date Testing
To test with specific dates, you can temporarily modify the script's date calculation, or use the main `ercot_query.py` with a config file.

### Verify Output
Check that data is being saved correctly:
```bash
# List recent files
ls -lht output/daily/dam/2025/01/

# Check file contents
cat output/daily/dam/2025/01/settlement_prices_HB_HOUSTON_2025-01-27.json | head -20
```

---

## Troubleshooting

### Script Fails Silently in Cron
**Cause**: Environment variables (like .env file) may not be loaded correctly in cron.

**Solution**: Use absolute paths in crontab:
```bash
0 1 * * * cd /home/user/ercot-api-query && /usr/bin/python3 scripts/daily_dam_settlement_prices.py
```

### Authentication Fails
**Cause**: .env file not found or credentials incorrect.

**Solution**:
1. Ensure .env file exists in the project root
2. Check credentials are valid
3. Test manually first: `python3 scripts/daily_dam_settlement_prices.py`

### Large Data Files
**Cause**: Some endpoints return large amounts of data.

**Solution**:
- Use date ranges carefully (yesterday only)
- Consider filtering by specific locations
- Monitor disk space

### Token Expiry During Collection
**Cause**: Collection takes longer than token lifetime (60 minutes).

**Solution**: The script automatically handles token refresh. If issues persist, check:
- Network connectivity
- API response times
- Consider splitting large queries

---

## Best Practices

1. **Test First**: Always test scripts manually before adding to cron
2. **Stagger Times**: Run different scripts at different times to avoid API rate limits
3. **Monitor Logs**: Check logs regularly for failures
4. **Disk Space**: Monitor output directory size
5. **Backup Data**: Regularly backup collected data
6. **Error Notifications**: Consider email notifications for cron failures:
   ```bash
   MAILTO=your-email@example.com
   0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py
   ```

---

## Script Features

All scripts include:
- ✅ Automatic date calculation (previous 24 hours)
- ✅ Organized output directory structure (year/month)
- ✅ Descriptive filenames with dates
- ✅ Debug mode for troubleshooting
- ✅ Proper error handling and exit codes
- ✅ Command-line help text
- ✅ Cron-ready (silent on success, errors to stderr)

---

## Need Help?

- Check the main [README.md](../README.md) for general usage
- See [EXAMPLES.md](../EXAMPLES.md) for more endpoint examples
- Review [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues
- Use `--debug` flag to see detailed output
