#!/bin/bash

echo "=== Workflow Test ==="
echo ""

# Step 1: Login
echo "1️⃣ Login..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"trest","password":"trest2026"}')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"refresh":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"
echo "Access Token: ${ACCESS_TOKEN:0:20}..."
echo ""

# Step 2: Get API endpoints to verify they exist
echo "2️⃣ Checking API endpoints..."
curl -s http://localhost:8000/api/evaluations/ -H "Authorization: Bearer $ACCESS_TOKEN" | head -20
echo ""
echo ""

# Step 3: Check what endpoints are available
echo "3️⃣ Available endpoints:"
curl -s http://localhost:8000/api/schema/ | grep -o '"operationId":"[^"]*' | head -10
echo ""

