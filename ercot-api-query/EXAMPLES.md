# Examples and Use Cases

This document provides practical examples of using the ERCOT API Query Tool for various data retrieval scenarios using real ERCOT Public Reports API endpoints.

## Basic Examples

### Example 1: Day-Ahead Market Settlement Point Prices

**Use Case**: Get DAM settlement point prices for a specific trading hub

**Configuration** (`queries/settlement_point_prices.json`):
```json
{
  "endpoint": "np4-190-cd/dam_stlmnt_pnt_prices",
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

**Available Settlement Points**: HB_NORTH, HB_SOUTH, HB_WEST, HB_HOUSTON, HB_BUSAVG, HB_PAN

---

### Example 2: Real-Time LMP by Settlement Point

**Use Case**: Get real-time locational marginal prices for resource nodes, load zones, and trading hubs

**Configuration** (`queries/realtime_lmp.json`):
```json
{
  "endpoint": "np6-788-cd/lmp_node_zone_hub",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T00:00:00",
    "SCEDTimestampTo": "2025-01-27T23:59:59"
  },
  "output_file": "output/realtime_lmp_jan27.json"
}
```

**Run**:
```bash
python3 ercot_query.py --config queries/realtime_lmp.json
```

**Note**: Real-time endpoints typically use `SCEDTimestamp` parameters instead of `deliveryDate`.

---

### Example 3: 15-Minute Settlement Point Prices (Real-Time)

**Use Case**: Get real-time settlement point prices updated every 15 minutes

**Configuration** (`queries/spp_15min.json`):
```json
{
  "endpoint": "np6-905-cd/spp_node_zone_hub",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T06:00:00",
    "SCEDTimestampTo": "2025-01-27T18:00:00"
  },
  "output_file": "output/spp_15min_jan27.json"
}
```

---

## Advanced Examples

### Example 4: Day-Ahead Market Hourly LMP

**Use Case**: Get hourly locational marginal prices from the day-ahead market

**Configuration** (`queries/dam_hourly_lmp.json`):
```json
{
  "endpoint": "np4-183-cd/dam_hourly_lmp",
  "parameters": {
    "deliveryDateFrom": "2025-01-27",
    "deliveryDateTo": "2025-01-31"
  },
  "output_file": "output/dam_hourly_lmp_jan2025.json"
}
```

---

### Example 5: LMP by Electrical Bus

**Use Case**: Get locational marginal prices at specific electrical buses

**Configuration** (`queries/lmp_electrical_bus.json`):
```json
{
  "endpoint": "np6-787-cd/lmp_electrical_bus",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T00:00:00",
    "SCEDTimestampTo": "2025-01-27T12:00:00"
  },
  "output_file": "output/lmp_electrical_bus_jan27.json"
}
```

**Note**: This endpoint provides more granular location-specific pricing data.

---

### Example 6: Shadow Prices (Day-Ahead Market)

**Use Case**: Get shadow prices for constraints in the day-ahead market

**Configuration** (`queries/dam_shadow_prices.json`):
```json
{
  "endpoint": "np4-191-cd/dam_shadow_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27"
  },
  "output_file": "output/dam_shadow_prices_jan2025.json"
}
```

---

### Example 7: Shadow Prices (SCED/Real-Time)

**Use Case**: Get shadow prices for binding transmission constraints from SCED

**Configuration** (`queries/sced_shadow_prices.json`):
```json
{
  "endpoint": "np6-86-cd/shdw_prices_bnd_trns_const",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T00:00:00",
    "SCEDTimestampTo": "2025-01-27T23:59:59"
  },
  "output_file": "output/sced_shadow_prices_jan27.json"
}
```

---

### Example 8: DAM Generation Resource AS Offers

**Use Case**: Get ancillary service offers from generation resources in the day-ahead market

**Configuration** (`queries/dam_gen_as_offers.json`):
```json
{
  "endpoint": "np3-966-er/60_dam_gen_res_as_offers",
  "parameters": {
    "deliveryDateFrom": "2025-01-27",
    "deliveryDateTo": "2025-01-27"
  },
  "output_file": "output/dam_gen_as_offers_jan27.json"
}
```

**Note**: This is a 60-day historical data endpoint.

---

### Example 9: Using Archive API for Bulk Downloads

**Use Case**: Query archive metadata and download multiple files

**Step 1 - Query Archive** (`queries/archive_query.json`):
```json
{
  "endpoint": "archive/np6-788-cd",
  "parameters": {
    "postDatetimeFrom": "2025-01-20T00:00:00",
    "postDatetimeTo": "2025-01-27T23:59:59"
  },
  "output_file": "output/archive_metadata_np6-788.json"
}
```

**Step 2 - Download specific file**:
```json
{
  "endpoint": "archive/np6-788-cd",
  "parameters": {
    "download": "1016533754"
  },
  "output_file": "output/np6-788-doc-1016533754.zip"
}
```

**Note**: The archive API returns metadata with document IDs that can be used for downloads.

---

## Workflow Examples

### Workflow 1: Daily Price Monitoring

**Use Case**: Monitor prices across different markets daily

**Create queries for each market**:

**DAM Prices** (`queries/daily_dam_prices.json`):
```json
{
  "endpoint": "np4-190-cd/dam_stlmnt_pnt_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-27",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_HOUSTON"
  },
  "output_file": "output/daily/dam_houston_20250127.json"
}
```

**Real-Time Prices** (`queries/daily_rtm_prices.json`):
```json
{
  "endpoint": "np6-905-cd/spp_node_zone_hub",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T00:00:00",
    "SCEDTimestampTo": "2025-01-27T23:59:59"
  },
  "output_file": "output/daily/rtm_prices_20250127.json"
}
```

**Add to crontab**:
```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/ercot-api-query && python3 ercot_query.py --config queries/daily_dam_prices.json
0 2 * * * cd /path/to/ercot-api-query && python3 ercot_query.py --config queries/daily_rtm_prices.json
```

---

### Workflow 2: Compare Hub Prices

**Use Case**: Compare prices across all trading hubs

**Create separate configs** for each hub:

**Houston Hub** (`queries/houston_prices.json`):
```json
{
  "endpoint": "np4-190-cd/dam_stlmnt_pnt_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_HOUSTON"
  },
  "output_file": "output/hubs/houston_prices.json"
}
```

**North Hub** (`queries/north_prices.json`):
```json
{
  "endpoint": "np4-190-cd/dam_stlmnt_pnt_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_NORTH"
  },
  "output_file": "output/hubs/north_prices.json"
}
```

**Run all hubs**:
```bash
python3 ercot_query.py --config queries/houston_prices.json
python3 ercot_query.py --config queries/north_prices.json
python3 ercot_query.py --config queries/west_prices.json
python3 ercot_query.py --config queries/south_prices.json
```

---

### Workflow 3: Batch Script for Market Analysis

**Use Case**: Collect comprehensive market data for analysis

**Create bash script** (`run_market_analysis.sh`):
```bash
#!/bin/bash

DATE=$(date +%Y-%m-%d)
echo "Collecting market data for $DATE..."

# Day-Ahead Market data
python3 ercot_query.py --config queries/dam_prices.json
python3 ercot_query.py --config queries/dam_lmp.json
python3 ercot_query.py --config queries/dam_shadow_prices.json

# Real-Time Market data
python3 ercot_query.py --config queries/rtm_lmp.json
python3 ercot_query.py --config queries/rtm_spp.json
python3 ercot_query.py --config queries/sced_shadow_prices.json

echo "Market data collection completed!"
```

**Make it executable and run**:
```bash
chmod +x run_market_analysis.sh
./run_market_analysis.sh
```

---

## Parameter Reference

### Day-Ahead Market Endpoints

Most DAM endpoints use these parameters:
```json
{
  "deliveryDateFrom": "2025-01-01",  // Start date (YYYY-MM-DD)
  "deliveryDateTo": "2025-01-31",    // End date (YYYY-MM-DD)
  "hourEnding": "17",                 // Optional: Specific hour (1-24)
  "settlementPoint": "HB_NORTH"      // Optional: Specific settlement point
}
```

### Real-Time Market Endpoints

Most RTM/SCED endpoints use these parameters:
```json
{
  "SCEDTimestampFrom": "2025-01-27T00:00:00",  // Start timestamp
  "SCEDTimestampTo": "2025-01-27T23:59:59"     // End timestamp
}
```

### Archive Endpoints

Archive queries use these parameters:
```json
{
  "postDatetimeFrom": "2025-01-20T00:00:00",  // When file was posted (from)
  "postDatetimeTo": "2025-01-27T23:59:59",    // When file was posted (to)
  "download": "1016533754"                     // Optional: Document ID to download
}
```

### Common Settlement Points

```
HB_NORTH       - North Hub
HB_SOUTH       - South Hub
HB_WEST        - West Hub
HB_HOUSTON     - Houston Hub
HB_BUSAVG      - Bus Average Hub
HB_PAN         - Panhandle Hub
LZ_HOUSTON     - Houston Load Zone
LZ_NORTH       - North Load Zone
LZ_SOUTH       - South Load Zone
LZ_WEST        - West Load Zone
```

---

## Endpoint Categories

### Pricing Endpoints

**Day-Ahead Market:**
- `np4-190-cd/dam_stlmnt_pnt_prices` - DAM Settlement Point Prices
- `np4-183-cd/dam_hourly_lmp` - DAM Hourly LMP
- `np4-191-cd/dam_shadow_prices` - DAM Shadow Prices

**Real-Time Market:**
- `np6-788-cd/lmp_node_zone_hub` - LMP by Node/Zone/Hub
- `np6-905-cd/spp_node_zone_hub` - SPP (15-min intervals)
- `np6-787-cd/lmp_electrical_bus` - LMP by Electrical Bus
- `np6-86-cd/shdw_prices_bnd_trns_const` - SCED Shadow Prices

### Resource/Generation Endpoints

- `np3-965-er/60_sced_smne_gen_res` - SCED 60-Day Gen Resource
- `np3-966-er/60_dam_gen_res_as_offers` - DAM Gen Resource AS Offers
- `np3-966-er/60_dam_load_res_as_offers` - DAM Load Resource AS Offers

### Archive Endpoints

- `archive/{PRODUCT_ID}` - Query archive metadata
- `archive/{PRODUCT_ID}?download={docId}` - Download specific file

---

## Tips and Best Practices

### 1. Date Range Selection

**Good Practice**:
```json
// Query one week at a time for detailed data
"deliveryDateFrom": "2025-01-20",
"deliveryDateTo": "2025-01-27"
```

**Avoid**:
```json
// Large date ranges may timeout or exceed API limits
"deliveryDateFrom": "2024-01-01",
"deliveryDateTo": "2024-12-31"
```

### 2. Real-Time vs Day-Ahead Parameters

**Day-Ahead** endpoints use `deliveryDate`:
```json
"deliveryDateFrom": "2025-01-27",
"deliveryDateTo": "2025-01-27"
```

**Real-Time** endpoints use `SCEDTimestamp`:
```json
"SCEDTimestampFrom": "2025-01-27T00:00:00",
"SCEDTimestampTo": "2025-01-27T23:59:59"
```

### 3. File Organization

Organize output files by market and date:

```json
"output_file": "output/2025/january/dam/settlement_prices.json"
"output_file": "output/2025/january/rtm/lmp_realtime.json"
```

### 4. Testing Queries

Always test with a small date range first:

```json
{
  "endpoint": "np6-788-cd/lmp_node_zone_hub",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T12:00:00",
    "SCEDTimestampTo": "2025-01-27T13:00:00"  // Just one hour
  },
  "output_file": "output/test_lmp.json"
}
```

### 5. Using Debug Mode

For troubleshooting, use the `--debug` flag:

```bash
python3 ercot_query.py --config queries/your_query.json --debug
```

This shows:
- Authentication details
- Full request headers
- Complete API responses
- Token information

---

## Common Use Cases

### Energy Trader
- Monitor DAM and RTM prices across hubs
- Track shadow prices for constraint analysis
- Download historical price data for modeling

### Grid Analyst
- Analyze LMP patterns by location
- Study constraint impacts via shadow prices
- Compare DAM forecasts vs RTM actuals

### Renewable Developer
- Track hub prices for project economics
- Monitor congestion through shadow prices
- Analyze historical price patterns

### Researcher
- Access historical market data
- Study price formation mechanisms
- Analyze market efficiency

---

## Need More Examples?

- **API Documentation**: https://apiexplorer.ercot.com/
- **Data Products**: https://www.ercot.com/mp/data-products
- **Support**: https://apiexplorer.ercot.com/support
- Check TROUBLESHOOTING.md for common issues
- Read README.md for complete documentation

---

## Sources

This documentation uses real ERCOT Public Reports API endpoints. For the most up-to-date endpoint information:

- [ERCOT API Explorer](https://apiexplorer.ercot.com/)
- [ERCOT Public API Applications](https://www.ercot.com/services/mdt/data-portal)
- [ERCOT Developer Portal](https://developer.ercot.com/applications/pubapi/user-guide/using-api/)
- [ERCOT Data Products](https://www.ercot.com/mp/data-products)
