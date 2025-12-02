#!/bin/bash
# Test script for OSRM container health check endpoint

# Configuration
SERVER_URL="http://127.0.0.1:5000"
ENDPOINT="/health/osrm"

echo "======================================================"
echo "OSRM Container Health Check Test"
echo "======================================================"
echo ""
echo "Server: $SERVER_URL"
echo "Endpoint: $ENDPOINT"
echo ""

# Test the OSRM health check endpoint
echo "Testing OSRM health check..."
echo "Command: curl -s '$SERVER_URL$ENDPOINT' | python3 -m json.tool"
echo ""

curl -s "$SERVER_URL$ENDPOINT" | python3 -m json.tool

echo ""
echo "======================================================"
echo "Expected responses:"
echo "- 200 OK: OSRM is healthy and responding"
echo "- 503 Service Unavailable: OSRM container is not responding"
echo "- 504 Gateway Timeout: OSRM request timed out"
echo "======================================================"
