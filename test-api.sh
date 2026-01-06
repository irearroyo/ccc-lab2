#!/bin/bash

# API Testing Script
# Usage: ./test-api.sh <API_GATEWAY_URL>

if [ -z "$1" ]; then
    echo "Usage: ./test-api.sh <API_GATEWAY_URL>"
    echo "Example: ./test-api.sh https://abc123.execute-api.us-east-1.amazonaws.com/prod/products"
    exit 1
fi

API_URL="$1"

echo "========================================="
echo "Testing Product Inventory API"
echo "========================================="
echo ""

echo "Test 1: Get all products"
echo "Command: curl \"$API_URL\""
curl -s "$API_URL" | jq '.'
echo ""
echo ""

echo "Test 2: Filter by category (Machinery)"
echo "Command: curl \"$API_URL?category=Machinery\""
curl -s "$API_URL?category=Machinery" | jq '.'
echo ""
echo ""

echo "Test 3: Search by name (Drill)"
echo "Command: curl \"$API_URL?name=Drill\""
curl -s "$API_URL?name=Drill" | jq '.'
echo ""
echo ""

echo "Test 4: Filter by price range (100-2000)"
echo "Command: curl \"$API_URL?minPrice=100&maxPrice=2000\""
curl -s "$API_URL?minPrice=100&maxPrice=2000" | jq '.'
echo ""
echo ""

echo "Test 5: Combined filters (Safety Equipment, max price 50)"
echo "Command: curl \"$API_URL?category=Safety%20Equipment&maxPrice=50\""
curl -s "$API_URL?category=Safety%20Equipment&maxPrice=50" | jq '.'
echo ""
echo ""

echo "Test 6: Filter by minimum price (5000)"
echo "Command: curl \"$API_URL?minPrice=5000\""
curl -s "$API_URL?minPrice=5000" | jq '.'
echo ""
echo ""

echo "========================================="
echo "All tests completed!"
echo "========================================="
