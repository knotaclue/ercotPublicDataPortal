# Examples and Use Cases

This document provides practical examples of using the ERCOT API Query Tool for various data retrieval scenarios.

## Basic Examples

### Example 1: Query Real-Time System Load

**Use Case**: Get actual system load data for a specific date range

**Configuration** (`queries/realtime_system_load.json`):
```json
{
  "endpoint": "/api/v1/actual_system_load",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-27"
  },
  "output_file": "output/system_load_jan2025.json"
}
```

**Run**:
```bash
python3 ercot_query.py --config queries/realtime_system_load.json
```

---

### Example 2: Query Settlement Point Prices

**Use Case**: Get hourly pricing data for a specific settlement point

**Configuration** (`queries/settlement_point_prices.json`):
```json
{
  "endpoint": "/api/v1/settlement_point_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_NORTH"
  },
  "output_file": "output/settlement_prices_hb_north.json"
}
```

**Run**:
```bash
python3 ercot_query.py --config queries/settlement_point_prices.json
```

---

### Example 3: Query Wind Power Production

**Use Case**: Get wind generation data by region

**Configuration** (`queries/wind_power_production.json`):
```json
{
  "endpoint": "/api/v1/wind_power_production",
  "parameters": {
    "deliveryDateFrom": "2025-01-25",
    "deliveryDateTo": "2025-01-27",
    "region": "ERCOT"
  },
  "output_file": "output/wind_power_jan25-27.json"
}
```

**Run**:
```bash
python3 ercot_query.py --config queries/wind_power_production.json
```

---

## Advanced Examples

### Example 4: Day-Ahead Market Clearing Prices

**Use Case**: Get DAM clearing prices for price analysis

**Configuration** (`queries/dam_clearing_prices.json`):
```json
{
  "endpoint": "/api/v1/dam_clearing_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-31",
    "marketType": "DAM"
  },
  "output_file": "output/dam_prices_january_2025.json"
}
```

---

### Example 5: Specific Hour Query

**Use Case**: Get data for a specific hour of the day

**Configuration** (`queries/peak_hour_prices.json`):
```json
{
  "endpoint": "/api/v1/settlement_point_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-31",
    "hourEnding": "17",
    "settlementPoint": "HB_HOUSTON"
  },
  "output_file": "output/houston_peak_hour_prices.json"
}
```

**Note**: `hourEnding` 17 represents the 5 PM hour (peak demand time)

---

### Example 6: Solar Power Production

**Use Case**: Track solar generation across all regions

**Configuration** (`queries/solar_production.json`):
```json
{
  "endpoint": "/api/v1/solar_power_production",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-31"
  },
  "output_file": "output/solar_production_jan2025.json"
}
```

---

### Example 7: Minimal Parameters (Let API Use Defaults)

**Use Case**: Query with minimum required parameters

**Configuration** (`queries/minimal_query.json`):
```json
{
  "endpoint": "/api/v1/actual_system_load",
  "parameters": {
    "deliveryDateFrom": "2025-01-27"
  },
  "output_file": "output/load_today.json"
}
```

**Note**: API will use defaults for parameters not specified

---

### Example 8: Auto-Generated Output Filename

**Use Case**: Let the script generate the output filename automatically

**Configuration** (`queries/auto_filename.json`):
```json
{
  "endpoint": "/api/v1/wind_power_production",
  "parameters": {
    "deliveryDateFrom": "2025-01-27",
    "deliveryDateTo": "2025-01-27"
  }
}
```

**Note**: `output_file` is omitted, so the script will create a filename like:
`output/wind_power_production_20250127_143022.json`

---

## Workflow Examples

### Workflow 1: Daily Data Collection

**Use Case**: Automate daily data collection with cron

**Create query** (`queries/daily_load.json`):
```json
{
  "endpoint": "/api/v1/actual_system_load",
  "parameters": {
    "deliveryDateFrom": "2025-01-27",
    "deliveryDateTo": "2025-01-27"
  }
}
```

**Add to crontab**:
```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/ercot-api-query && python3 ercot_query.py --config queries/daily_load.json
```

---

### Workflow 2: Compare Multiple Settlement Points

**Use Case**: Get prices for multiple locations

**Create separate configs** for each settlement point:

**queries/houston_prices.json**:
```json
{
  "endpoint": "/api/v1/settlement_point_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_HOUSTON"
  },
  "output_file": "output/houston_prices.json"
}
```

**queries/north_prices.json**:
```json
{
  "endpoint": "/api/v1/settlement_point_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_NORTH"
  },
  "output_file": "output/north_prices.json"
}
```

**Run both**:
```bash
python3 ercot_query.py --config queries/houston_prices.json
python3 ercot_query.py --config queries/north_prices.json
```

---

### Workflow 3: Batch Script for Multiple Queries

**Use Case**: Run several queries in sequence

**Create bash script** (`run_all_queries.sh`):
```bash
#!/bin/bash

echo "Running all ERCOT queries..."

python3 ercot_query.py --config queries/realtime_system_load.json
python3 ercot_query.py --config queries/settlement_point_prices.json
python3 ercot_query.py --config queries/wind_power_production.json
python3 ercot_query.py --config queries/solar_production.json

echo "All queries completed!"
```

**Make it executable and run**:
```bash
chmod +x run_all_queries.sh
./run_all_queries.sh
```

---

## Parameter Reference

### Common Date Parameters

```json
{
  "deliveryDateFrom": "2025-01-01",  // Start date (inclusive)
  "deliveryDateTo": "2025-01-31",    // End date (inclusive)
  "hourEnding": "12"                  // Specific hour (1-24)
}
```

### Common Location Parameters

```json
{
  "settlementPoint": "HB_NORTH",     // Settlement point name
  "region": "ERCOT",                 // Region identifier
  "zone": "LZ_HOUSTON"               // Load zone
}
```

### Common Filter Parameters

```json
{
  "marketType": "DAM",               // DAM (Day-Ahead Market)
  "resourceType": "WIND",            // Resource type filter
  "unit": "MW"                       // Unit of measurement
}
```

**Note**: Available parameters vary by endpoint. Always consult ERCOT API documentation for endpoint-specific parameters.

---

## Tips and Best Practices

### 1. Date Range Selection

**Good Practice**:
```json
// Query one week at a time
"deliveryDateFrom": "2025-01-20",
"deliveryDateTo": "2025-01-27"
```

**Avoid**:
```json
// Querying entire years may timeout or return too much data
"deliveryDateFrom": "2024-01-01",
"deliveryDateTo": "2024-12-31"
```

### 2. File Organization

Organize output files by date or category:

```json
"output_file": "output/2025/january/system_load.json"
"output_file": "output/prices/houston/jan20-jan27.json"
```

### 3. Descriptive Filenames

Use clear, descriptive output filenames:

```json
// ✅ Good
"output_file": "output/houston_settlement_prices_jan2025.json"

// ❌ Less clear
"output_file": "output/data.json"
```

### 4. Query Naming Convention

Name your query files descriptively:

```
queries/
├── daily_system_load.json
├── houston_prices_hourly.json
├── wind_production_weekly.json
└── solar_production_monthly.json
```

---

## Testing Your Queries

Before running production queries, test with a small date range:

```json
{
  "endpoint": "/api/v1/actual_system_load",
  "parameters": {
    "deliveryDateFrom": "2025-01-27",
    "deliveryDateTo": "2025-01-27"  // Just one day
  },
  "output_file": "output/test_load.json"
}
```

Once confirmed working, expand the date range as needed.

---

## Need More Examples?

- Check the ERCOT API documentation for all available endpoints
- Review the `queries/` directory for included examples
- See TROUBLESHOOTING.md for common issues
- Read README.md for complete documentation
