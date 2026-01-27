# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python tool for querying the ERCOT Public Data Portal API. The tool handles authentication, automatic token refresh (30-minute expiry), and flexible query configuration through JSON files.

## Core Architecture

### Single-Script Design
The entire application is in `ercot_query.py` (400 lines). This is intentional - the design philosophy is to have one well-documented script rather than multiple modules. All API logic, authentication, and token management is in the `ERCOTAPIClient` class.

### Configuration-Driven
Queries are defined as JSON files in `queries/` directory, not in code. Each query config specifies:
- `endpoint`: API endpoint path
- `parameters`: Query parameters (optional)
- `output_file`: Where to save response (optional, auto-generated if not specified)

### Token Management
The ERCOT API tokens expire every 30 minutes. The client automatically refreshes tokens at 28 minutes (2-minute safety buffer) via the `_ensure_authenticated()` method called before each API request.

### Credentials
All credentials are stored in `.env` file (never committed). The `.env.template` shows the required variables:
- `ERCOT_USERNAME`
- `ERCOT_PASSWORD`
- `ERCOT_SUBSCRIPTION_KEY`
- `ERCOT_BASE_URL`

## Common Commands

### Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Or use automated setup script
./setup.sh

# Create .env file
cp .env.template .env
# Then edit .env with actual credentials
```

### Running Queries
```bash
# Basic query
python3 ercot_query.py --config queries/realtime_system_load.json

# With verbose output
python3 ercot_query.py --config queries/settlement_point_prices.json --verbose
```

### Creating New Queries
```bash
# Copy an existing query config
cp queries/realtime_system_load.json queries/my_new_query.json
# Edit the JSON file to change endpoint and parameters
# Run it
python3 ercot_query.py --config queries/my_new_query.json
```

## Code Modification Guidelines

### Adding New Features
When adding features to `ercot_query.py`:
- Maintain the extensive inline comments (this is a beginner-friendly codebase)
- Keep all logic in the single script (don't split into modules)
- Add error handling with user-friendly messages
- Update the docstrings

### Authentication Changes
ERCOT uses Azure B2C authentication (ROPC flow). If changes are needed:
- Modify the `authenticate()` method in `ERCOTAPIClient` class (line ~88)
- Authentication URL: `https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token`
- Client ID: `fec253ea-0d06-4272-a5e6-b478baeecd70`
- Token expiry: 60 minutes (refresh at 55 minutes for safety buffer)

### Parameter Handling
The script accepts ANY parameters from the JSON config and passes them to the API. No code changes needed for new parameters - just add them to the query config file.

## Important Context

### No Tests
There are no unit tests. This is a simple utility script with a single class. Testing happens by running actual queries.

### No Virtual Environment in Repo
The project doesn't include a venv/ directory. Users create their own virtual environment during setup.

### Extensive Documentation
The project has 9 markdown files totaling ~51KB of documentation. When making changes, consider updating:
- README.md (main docs)
- TROUBLESHOOTING.md (if adding error scenarios)
- EXAMPLES.md (if adding new usage patterns)

### Security First
The `.gitignore` explicitly excludes `.env` files. Never commit credentials or suggest changes that would expose secrets.

## API Details

### ERCOT Authentication Flow
1. POST to Azure B2C endpoint: `https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token`
2. Send form-urlencoded parameters:
   - `username`: User's email
   - `password`: User's password
   - `grant_type`: "password"
   - `scope`: "openid fec253ea-0d06-4272-a5e6-b478baeecd70 offline_access"
   - `client_id`: "fec253ea-0d06-4272-a5e6-b478baeecd70"
   - `response_type`: "id_token"
3. Receive bearer token valid for 60 minutes (3600 seconds)
4. Include token in `Authorization: Bearer <token>` header for all API requests
5. Include subscription key in `Ocp-Apim-Subscription-Key` header

### Common ERCOT Public Reports Endpoints
- `np6-345-cd/act_sys_load_by_wzn` - Actual system load by weather zone
- `np4-190-cd/dam_stlmnt_pnt_prices` - DAM settlement point prices
- `np4-732-cd/wpp_hrly_avrg_actl_fcast` - Wind power hourly average actual/forecast

### Common Parameters
- `deliveryDateFrom` - Start date (YYYY-MM-DD)
- `deliveryDateTo` - End date (YYYY-MM-DD)
- Additional parameters vary by endpoint

## File Structure Reference

```
ercot-api-query/
├── ercot_query.py          # Main script - ERCOTAPIClient class + main()
├── requirements.txt        # requests>=2.31.0, python-dotenv>=1.0.0
├── .env.template           # Template for credentials
├── .env                    # Actual credentials (never committed)
├── queries/                # Query configuration JSON files
│   ├── realtime_system_load.json
│   ├── settlement_point_prices.json
│   └── wind_power_production.json
└── output/                 # API responses saved here (auto-created)
```

## Working with This Codebase

### When Debugging Issues
1. Check if `.env` file exists and has valid credentials
2. Verify token expiry handling in `_ensure_authenticated()` (line ~148)
3. Check API request/response in `query_api()` method (line ~160)
4. Review error messages - they're designed to be user-friendly

### When Adding Endpoints
Don't modify Python code. Instead:
1. Create new JSON file in `queries/` directory
2. Specify the endpoint path and parameters
3. Run with `python3 ercot_query.py --config queries/your_new_query.json`

### Code Style
- Extensive comments (aimed at non-developers)
- Docstrings for all classes and methods
- Descriptive variable names
- Error messages with checkmarks (✓/✗) for visual clarity
