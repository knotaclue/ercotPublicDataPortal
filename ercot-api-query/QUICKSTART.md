# Quick Start Guide

Get up and running with the ERCOT API Query Tool in 5 minutes!

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

## 🎯 Common Query Pattern

All queries follow this simple pattern:

```json
{
  "endpoint": "/api/v1/your_endpoint",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-27"
  },
  "output_file": "output/your_output.json"
}
```

That's it! Happy querying! 🚀
