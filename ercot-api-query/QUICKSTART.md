# Quick Start Guide

Get up and running with the ERCOT API Query Tool in 5 minutes!

> **📚 New to this tool?** Check out [USAGE_GUIDE.md](USAGE_GUIDE.md) to learn about the three different ways to use this tool (manual queries, daily collection, and incremental polling).

## 1️⃣ Install Dependencies

```bash
pip3 install -r requirements.txt
```

## 2️⃣ Set Up Credentials

```bash
# Copy the template
cp .env.template .env

# Edit with your credentials
nano .env
```

Add your actual credentials to `.env`:
```bash
ERCOT_USERNAME=your_username
ERCOT_PASSWORD=your_password
ERCOT_SUBSCRIPTION_KEY=your_subscription_key
```

## 3️⃣ Run Your First Query

```bash
python3 ercot_query.py --config queries/realtime_system_load.json
```

## 4️⃣ Check the Output

Your data is saved in the `output/` directory!

```bash
cat output/system_load_jan2025.json
```

## 5️⃣ Create Your Own Query

```bash
# Copy an existing query
cp queries/realtime_system_load.json queries/my_query.json

# Edit it
nano queries/my_query.json

# Run it
python3 ercot_query.py --config queries/my_query.json
```

---

## 📖 Need More Help?

- Read the full [README.md](README.md) for detailed documentation
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Review example queries in the `queries/` directory

## 🎯 Common Query Patterns

### Day-Ahead Market Query

```json
{
  "endpoint": "np4-190-cd/dam_stlmnt_pnt_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-20",
    "deliveryDateTo": "2025-01-27",
    "settlementPoint": "HB_HOUSTON"
  },
  "output_file": "output/dam_prices_houston.json"
}
```

### Real-Time Market Query

```json
{
  "endpoint": "np6-788-cd/lmp_node_zone_hub",
  "parameters": {
    "SCEDTimestampFrom": "2025-01-27T00:00:00",
    "SCEDTimestampTo": "2025-01-27T23:59:59"
  },
  "output_file": "output/realtime_lmp.json"
}
```

That's it! Happy querying! 🚀

**See [EXAMPLES.md](EXAMPLES.md) for more real endpoint examples!**
