# Troubleshooting Guide

Common issues and how to resolve them.

## Authentication Issues

### ❌ "ERROR: ERCOT_USERNAME not found in .env file"

**Cause**: The `.env` file doesn't exist or doesn't contain credentials.

**Solution**:
```bash
# Make sure you created .env from the template
cp .env.template .env

# Edit it with your credentials
nano .env
```

### ❌ "Authentication failed with status code: 401"

**Cause**: Invalid credentials or subscription key.

**Solutions**:
1. Double-check your username and password in `.env`
2. Verify your subscription key is correct
3. Log into https://data.ercot.com to confirm your account is active
4. Check for extra spaces or newlines in your `.env` file

### ❌ "Authentication failed with status code: 403"

**Cause**: Your account doesn't have permission to access the API.

**Solutions**:
1. Verify your ERCOT account has API access enabled
2. Check that your subscription is active
3. Contact ERCOT support if the issue persists

---

## Configuration Issues

### ❌ "Configuration file not found: queries/myfile.json"

**Cause**: File path is incorrect or file doesn't exist.

**Solutions**:
```bash
# Check if file exists
ls -la queries/

# Make sure you're running from the project directory
cd ercot-api-query/

# Use the correct path
python3 ercot_query.py --config queries/myfile.json
```

### ❌ "Invalid JSON in configuration file"

**Cause**: Syntax error in your JSON configuration.

**Solutions**:
1. Validate your JSON at https://jsonlint.com
2. Common issues:
   - Missing comma between items
   - Extra comma after last item
   - Missing quotes around strings
   - Unbalanced brackets `{}` or `[]`

**Example of INVALID JSON**:
```json
{
  "endpoint": "/api/v1/test"
  "parameters": {  // ❌ Missing comma above
    "date": "2025-01-01",  // ❌ Extra comma below
  }
}
```

**Example of VALID JSON**:
```json
{
  "endpoint": "/api/v1/test",
  "parameters": {
    "date": "2025-01-01"
  }
}
```

---

## API Request Issues

### ❌ "Request failed with status code: 404"

**Cause**: Endpoint doesn't exist or URL is incorrect.

**Solutions**:
1. Verify the endpoint in ERCOT API documentation
2. Check for typos in the endpoint path
3. Ensure you're using the correct API version (e.g., `/api/v1/`)

**Example**:
```json
// ❌ WRONG
"endpoint": "/api/actual_system_load"

// ✅ CORRECT
"endpoint": "/api/v1/actual_system_load"
```

### ❌ "Request failed with status code: 400"

**Cause**: Invalid parameters sent to the API.

**Solutions**:
1. Check parameter names match API documentation exactly
2. Verify date format is correct (YYYY-MM-DD)
3. Ensure required parameters are included
4. Check parameter values are valid

**Example**:
```json
// ❌ WRONG - invalid date format
"deliveryDateFrom": "01/01/2025"

// ✅ CORRECT
"deliveryDateFrom": "2025-01-01"
```

### ❌ "Request failed with status code: 429"

**Cause**: Too many API requests (rate limiting).

**Solutions**:
1. Wait a few minutes before retrying
2. Reduce the frequency of your queries
3. Contact ERCOT if you need higher rate limits

### ❌ "Token expired or not available"

**Cause**: This is normal! The script will automatically refresh.

**What you'll see**:
```
Token expired or not available. Refreshing...
Authenticating with ERCOT API...
✓ Authentication successful
```

**No action needed** - this is handled automatically.

---

## Python / Dependency Issues

### ❌ "ModuleNotFoundError: No module named 'requests'"

**Cause**: Required Python packages not installed.

**Solution**:
```bash
pip3 install -r requirements.txt
```

If using a virtual environment:
```bash
# Activate your virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Then install
pip install -r requirements.txt
```

### ❌ "python3: command not found"

**Cause**: Python 3 not installed or not in PATH.

**Solutions**:
- On Ubuntu/Debian: `sudo apt install python3`
- On Mac: `brew install python3`
- On Windows: Download from https://python.org

Try `python --version` instead of `python3`.

### ❌ "Permission denied"

**Cause**: Script doesn't have execute permissions.

**Solution**:
```bash
# Make script executable
chmod +x ercot_query.py

# Run it
./ercot_query.py --config queries/myfile.json
```

---

## Output Issues

### ❌ "Error saving data to file"

**Cause**: No permission to write to output directory.

**Solutions**:
```bash
# Create output directory if it doesn't exist
mkdir -p output

# Check permissions
ls -la output/

# Fix permissions if needed
chmod 755 output/
```

### ❌ Output file is empty or contains only "null"

**Cause**: API returned no data or request failed.

**Solutions**:
1. Check that your date range has available data
2. Verify your parameters are correct
3. Check the script output for error messages
4. Try a different date range

---

## General Debugging

### Enable Verbose Mode

Get more detailed information about what's happening:

```bash
python3 ercot_query.py --config queries/myfile.json --verbose
```

### Check Your Configuration

Print your configuration to verify it's correct:

```bash
cat queries/myfile.json | python3 -m json.tool
```

### Test Your .env File

Verify your credentials are loaded:

```bash
# This will fail if .env is not set up correctly
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Username:', os.getenv('ERCOT_USERNAME'))"
```

### View Full Error Messages

If you get an error, read the complete output. The script provides detailed error messages that often indicate exactly what's wrong.

---

## Still Having Issues?

1. **Check the README.md** for detailed documentation
2. **Review example queries** in the `queries/` directory
3. **Consult ERCOT API documentation** at https://developer.ercot.com
4. **Open an issue** on GitHub with:
   - What you're trying to do
   - The exact command you ran
   - The complete error message
   - Your Python version (`python3 --version`)

---

## Common Workflow Reminders

✅ **Always run from the project directory**:
```bash
cd ercot-api-query/
python3 ercot_query.py --config queries/myfile.json
```

✅ **Use correct date format**: YYYY-MM-DD
```json
"deliveryDateFrom": "2025-01-01"
```

✅ **Check .env file has no extra spaces**:
```bash
# Good
ERCOT_USERNAME=myusername

# Bad (has spaces)
ERCOT_USERNAME = myusername
```

✅ **Remember to activate virtual environment** (if using one):
```bash
source venv/bin/activate
```
