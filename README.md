# ERCOT Public API Query Tool

A Python 3 tool for querying the ERCOT Public Data Portal API with automatic token management and flexible configuration.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Creating New Queries](#creating-new-queries)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [API Documentation](#api-documentation)

## 🌟 Overview

This tool provides a simple, reusable way to query the ERCOT Public Data Portal API. It handles authentication, automatic token refresh (tokens expire every 30 minutes), and saves responses in JSON format.

Key benefits:
- **No code duplication**: One main script handles all queries
- **Easy to use**: Simple JSON configuration files for each query
- **Secure**: Credentials stored in `.env` file (never committed to git)
- **Automatic token management**: Refreshes authentication tokens as needed
- **Flexible**: Supports any endpoint and parameter combination

## ✨ Features

- ✅ Automatic authentication and token refresh
- ✅ Bearer token management (30-minute expiry handling)
- ✅ Flexible parameter support (reads all parameters from config)
- ✅ Secure credential storage using `.env` file
- ✅ JSON configuration files for different queries
- ✅ Comprehensive error handling
- ✅ Detailed logging and status messages
- ✅ Automatic output directory creation
- ✅ Response validation

## 📦 Prerequisites

- Python 3.7 or higher
- ERCOT Public Data Portal account with:
  - Username
  - Password
  - Subscription Key (API key)

## 🚀 Installation

### 1. Clone this repository

```bash
git clone <your-repo-url>
cd ercot-api-query
```

### 2. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

Or if you're using a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up your credentials

```bash
# Copy the template
cp .env.template .env

# Edit the .env file and add your credentials
nano .env  # or use your preferred editor
```

Edit `.env` to include your actual credentials:

```bash
ERCOT_USERNAME=your_actual_username
ERCOT_PASSWORD=your_actual_password
ERCOT_SUBSCRIPTION_KEY=your_actual_subscription_key
ERCOT_BASE_URL=https://data.ercot.com
```

**⚠️ IMPORTANT**: Never commit the `.env` file to git! It contains your secrets.

## ⚙️ Configuration

### Query Configuration Files

Each query is defined in a JSON file in the `queries/` directory. Here's the structure:

```json
{
  "endpoint": "/api/v1/your_endpoint",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-27",
    "anyOtherParameter": "value"
  },
  "output_file": "output/your_output_file.json"
}
```

**Required fields:**
- `endpoint`: The API endpoint you want to query

**Optional fields:**
- `parameters`: Any query parameters (deliveryDateFrom, deliveryDateTo, etc.)
- `output_file`: Where to save the response (default: auto-generated name)

### Example Query Configurations

Three example configurations are included:

1. **realtime_system_load.json** - Query actual system load data
2. **settlement_point_prices.json** - Query settlement point prices with specific location
3. **wind_power_production.json** - Query wind power production by region

## 🎯 Usage

### Basic Usage

```bash
python3 ercot_query.py --config queries/realtime_system_load.json
```

### With Verbose Output

```bash
python3 ercot_query.py --config queries/settlement_point_prices.json --verbose
```

### What Happens When You Run It

1. **Loads credentials** from `.env` file
2. **Authenticates** with ERCOT API and obtains access token
3. **Reads query configuration** from the specified JSON file
4. **Makes API request** with your parameters
5. **Saves response** to the specified output file
6. **Displays status** messages throughout the process

### Example Output

```
============================================================
ERCOT Public API Query Tool
============================================================

Configuration loaded from: queries/realtime_system_load.json
Authenticating with ERCOT API...
✓ Authentication successful. Token valid until 2025-01-27 15:30:00

Querying endpoint: /api/v1/actual_system_load
Parameters: {
  "deliveryDateFrom": "2025-01-01",
  "deliveryDateTo": "2025-01-27"
}
✓ Request successful (HTTP 200)
✓ Data saved to: output/system_load_jan2025.json
  File size: 45,678 bytes (44.61 KB)

============================================================
✓ Query completed successfully!
============================================================
```

## 📝 Creating New Queries

To query a different endpoint or with different parameters:

### Option 1: Copy an Existing Configuration

```bash
cp queries/realtime_system_load.json queries/my_new_query.json
```

Then edit `my_new_query.json`:

```json
{
  "endpoint": "/api/v1/your_new_endpoint",
  "parameters": {
    "deliveryDateFrom": "2025-01-15",
    "deliveryDateTo": "2025-01-20",
    "customParameter1": "value1",
    "customParameter2": "value2"
  },
  "output_file": "output/my_custom_output.json"
}
```

### Option 2: Create From Scratch

Create a new file in the `queries/` directory with any parameters you need:

```json
{
  "endpoint": "/api/v1/dam_clearing_prices",
  "parameters": {
    "deliveryDateFrom": "2025-01-01",
    "deliveryDateTo": "2025-01-31",
    "hourEnding": "12",
    "marketType": "DAM"
  },
  "output_file": "output/dam_prices_january.json"
}
```

### Run Your New Query

```bash
python3 ercot_query.py --config queries/my_new_query.json
```

**That's it!** No Python code changes needed.

## 📁 Project Structure

```
ercot-api-query/
├── ercot_query.py              # Main script (handles all API logic)
├── .env                         # Your credentials (DO NOT COMMIT!)
├── .env.template               # Template for credentials
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── queries/                    # Query configuration files
│   ├── realtime_system_load.json
│   ├── settlement_point_prices.json
│   └── wind_power_production.json
│
└── output/                     # API responses saved here (created automatically)
    ├── system_load_jan2025.json
    └── ...
```

## 🔧 Troubleshooting

### "ERROR: ERCOT_USERNAME not found in .env file"

**Solution**: Make sure you've created the `.env` file (copy from `.env.template`) and filled in your credentials.

### "Authentication failed with status code: 401"

**Solutions**:
- Verify your username and password in `.env` are correct
- Check that your subscription key is valid
- Ensure your ERCOT account is active

### "Configuration file not found"

**Solution**: Make sure the path to your configuration file is correct:
```bash
python3 ercot_query.py --config queries/your_file.json
```

### "ModuleNotFoundError: No module named 'requests'"

**Solution**: Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

### Token expires during long queries

**Solution**: The script automatically refreshes the token! It checks before each request and renews if needed (tokens are valid for 30 minutes, script refreshes at 28 minutes).

### "Request failed with status code: 404"

**Solutions**:
- Verify the endpoint path is correct in your configuration file
- Check ERCOT API documentation for the correct endpoint name
- Some endpoints may require specific parameters

## 📚 API Documentation

For complete ERCOT Public Data Portal API documentation, visit:
- **API Portal**: https://data.ercot.com
- **Developer Docs**: https://developer.ercot.com (check for latest endpoints and parameters)

### Common Parameters

Most endpoints accept these parameters:
- `deliveryDateFrom` - Start date (YYYY-MM-DD format)
- `deliveryDateTo` - End date (YYYY-MM-DD format)
- Additional parameters vary by endpoint (check API docs)

## 🔐 Security Notes

1. **Never commit `.env` to git** - It contains your credentials
2. **The `.gitignore` file prevents this** - But always double-check
3. **Keep your subscription key private** - Treat it like a password
4. **Rotate credentials regularly** - Good security practice

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License.

---

**Questions?** Check the ERCOT API documentation or open an issue in this repository.
