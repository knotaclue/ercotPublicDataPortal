#!/bin/bash
# Example Cron Setup Script
#
# This script shows example cron entries for automated data collection.
# DO NOT run this script directly - it's for reference only!
#
# To use:
# 1. Edit this file with your actual paths
# 2. Copy the desired cron entries
# 3. Add them to your crontab: crontab -e

# IMPORTANT: Replace /path/to/ercot-api-query with your actual path!
PROJECT_PATH="/path/to/ercot-api-query"

cat << 'EOF'
#============================================================
# ERCOT API Automated Data Collection
#
# These cron jobs run daily at 1 AM to collect previous day's data
# Edit the paths below to match your installation
#============================================================

# Set up email notifications (optional)
# MAILTO=your-email@example.com

#------------------------------------------------------------
# Day-Ahead Market (DAM) Data - Runs at 1:00 AM
#------------------------------------------------------------

# Collect DAM Settlement Prices for Houston Hub
0 1 * * * cd /path/to/ercot-api-query && /usr/bin/python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_HOUSTON >> logs/cron_dam_houston.log 2>&1

# Collect DAM Settlement Prices for North Hub
0 1 * * * cd /path/to/ercot-api-query && /usr/bin/python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_NORTH >> logs/cron_dam_north.log 2>&1

# Collect DAM Settlement Prices for South Hub
0 1 * * * cd /path/to/ercot-api-query && /usr/bin/python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_SOUTH >> logs/cron_dam_south.log 2>&1

# Collect DAM Settlement Prices for West Hub
0 1 * * * cd /path/to/ercot-api-query && /usr/bin/python3 scripts/daily_dam_settlement_prices.py --settlement-point HB_WEST >> logs/cron_dam_west.log 2>&1

#------------------------------------------------------------
# Real-Time Market (RTM) Data - Runs at 1:15 AM
#------------------------------------------------------------

# Collect Real-Time LMP (Node, Zone, Hub)
15 1 * * * cd /path/to/ercot-api-query && /usr/bin/python3 scripts/daily_rtm_lmp.py >> logs/cron_rtm_lmp.log 2>&1

#------------------------------------------------------------
# 15-Minute Settlement Point Prices - Runs at 1:30 AM
#------------------------------------------------------------

# Collect 15-minute SPP data (WARNING: Large dataset!)
30 1 * * * cd /path/to/ercot-api-query && /usr/bin/python3 scripts/daily_spp_15min.py >> logs/cron_spp_15min.log 2>&1

#------------------------------------------------------------
# Minimal Example (Just Houston DAM prices, no logging)
#------------------------------------------------------------

# 0 1 * * * cd /path/to/ercot-api-query && python3 scripts/daily_dam_settlement_prices.py

#============================================================
# End of ERCOT API Cron Jobs
#============================================================

EOF

echo ""
echo "To add these to your crontab:"
echo "1. Create logs directory: mkdir -p logs"
echo "2. Edit this file and replace /path/to/ercot-api-query with your actual path"
echo "3. Copy the cron entries you want"
echo "4. Edit your crontab: crontab -e"
echo "5. Paste and save"
echo ""
echo "To view current crontab: crontab -l"
echo "To edit crontab: crontab -e"
