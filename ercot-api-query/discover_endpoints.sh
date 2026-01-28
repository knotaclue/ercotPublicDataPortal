#!/bin/bash
#
# ERCOT API Endpoint Discovery Script
#
# This script authenticates to the ERCOT API and attempts to discover
# all available endpoints by querying the API Explorer.
#

set -e  # Exit on error

# Load environment variables
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

source .env

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "ERCOT API Endpoint Discovery"
echo "=========================================="
echo

# Step 1: Authenticate and get bearer token
echo "Step 1: Authenticating..."

AUTH_URL="https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"
CLIENT_ID="fec253ea-0d06-4272-a5e6-b478baeecd70"

AUTH_RESPONSE=$(curl -s -X POST "$AUTH_URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ERCOT_USERNAME" \
    -d "password=$ERCOT_PASSWORD" \
    -d "grant_type=password" \
    -d "scope=openid $CLIENT_ID offline_access" \
    -d "client_id=$CLIENT_ID" \
    -d "response_type=id_token")

# Extract access token using grep and sed
ACCESS_TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "Response: $AUTH_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Authentication successful${NC}"
echo "Token: ${ACCESS_TOKEN:0:20}..."
echo

# Step 2: Try to discover endpoints through the API
echo "Step 2: Attempting to discover endpoints..."
echo

# Method 1: Query the base API URL to see if there's a discovery endpoint
echo "Method 1: Checking base API for endpoint list..."
BASE_API_URL="https://api.ercot.com/api/public-reports"

DISCOVERY_RESPONSE=$(curl -s -X GET "$BASE_API_URL" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Ocp-Apim-Subscription-Key: $ERCOT_SUBSCRIPTION_KEY" \
    -H "Accept: application/json")

if echo "$DISCOVERY_RESPONSE" | grep -q "np[0-9]"; then
    echo -e "${GREEN}✓ Found endpoints in base API response${NC}"
    echo "$DISCOVERY_RESPONSE" | grep -o "np[0-9]-[0-9]*-[a-z]*" | sort -u > discovered_endpoints.txt
    echo "Saved to: discovered_endpoints.txt"
else
    echo -e "${YELLOW}⚠ No endpoints found in base API${NC}"
fi
echo

# Method 2: Try known endpoint patterns to discover what's available
echo "Method 2: Testing known endpoint patterns..."
echo

# Create array of known endpoint prefixes
PREFIXES=("np3" "np4" "np6")
OUTPUT_FILE="discovered_endpoints_detailed.txt"
> "$OUTPUT_FILE"  # Clear file

echo "Testing endpoint patterns (this may take a moment)..."
echo "Format: PREFIX-ID-TYPE/endpoint_name" >> "$OUTPUT_FILE"
echo "================================================" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"

# Test a range of IDs for each prefix
for PREFIX in "${PREFIXES[@]}"; do
    echo "Testing $PREFIX series..."

    # Test some common IDs (you can expand this range)
    for ID in 33 86 183 190 191 732 787 788 905 965 966 970; do
        for TYPE in "cd" "er" "m"; do
            ENDPOINT_BASE="$PREFIX-$ID-$TYPE"
            TEST_URL="$BASE_API_URL/$ENDPOINT_BASE"

            # Try to HEAD the endpoint to see if it exists
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$TEST_URL" \
                -H "Authorization: Bearer $ACCESS_TOKEN" \
                -H "Ocp-Apim-Subscription-Key: $ERCOT_SUBSCRIPTION_KEY" \
                -H "Accept: application/json")

            if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "400" ]; then
                # 200 = success, 400 = exists but needs parameters
                echo -e "  ${GREEN}✓ Found: $ENDPOINT_BASE${NC}"

                # Try to get the endpoint details
                DETAIL_RESPONSE=$(curl -s -X GET "$TEST_URL" \
                    -H "Authorization: Bearer $ACCESS_TOKEN" \
                    -H "Ocp-Apim-Subscription-Key: $ERCOT_SUBSCRIPTION_KEY" \
                    -H "Accept: application/json" | head -c 500)

                echo "$ENDPOINT_BASE" >> "$OUTPUT_FILE"
                echo "  HTTP Code: $HTTP_CODE" >> "$OUTPUT_FILE"
                echo "  Response preview: ${DETAIL_RESPONSE:0:200}" >> "$OUTPUT_FILE"
                echo >> "$OUTPUT_FILE"
            fi
        done
    done
done

echo
echo -e "${GREEN}✓ Discovery complete${NC}"
echo "Results saved to: $OUTPUT_FILE"
echo

# Method 3: Try to fetch the API Explorer HTML and parse it
echo "Method 3: Attempting to scrape API Explorer page..."
API_EXPLORER_URL="https://apiexplorer.ercot.com/api-details#api=pubapi-apim-api"

EXPLORER_HTML=$(curl -s "$API_EXPLORER_URL")

if echo "$EXPLORER_HTML" | grep -q "np[0-9]"; then
    echo -e "${GREEN}✓ Found endpoint references in API Explorer${NC}"
    echo "$EXPLORER_HTML" | grep -o "np[0-9]-[0-9]*-[a-z]*[^\"]*" | sort -u > discovered_endpoints_explorer.txt
    echo "Saved to: discovered_endpoints_explorer.txt"
else
    echo -e "${YELLOW}⚠ Could not extract endpoints from API Explorer (may require JavaScript)${NC}"
fi
echo

# Summary
echo "=========================================="
echo "Discovery Summary"
echo "=========================================="
echo

if [ -f discovered_endpoints.txt ]; then
    ENDPOINT_COUNT=$(wc -l < discovered_endpoints.txt)
    echo "Found $ENDPOINT_COUNT unique endpoint IDs in API"
    echo
    echo "Sample endpoints:"
    head -10 discovered_endpoints.txt
fi

if [ -f discovered_endpoints_detailed.txt ]; then
    DETAILED_COUNT=$(grep -c "^np[0-9]" discovered_endpoints_detailed.txt || true)
    echo
    echo "Tested and found $DETAILED_COUNT working endpoints"
fi

echo
echo "=========================================="
echo "Output Files:"
echo "  - discovered_endpoints.txt (unique IDs)"
echo "  - discovered_endpoints_detailed.txt (full test results)"
echo "  - discovered_endpoints_explorer.txt (from web scraping)"
echo "=========================================="
