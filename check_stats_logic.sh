#!/bin/bash

echo "=== Checking /api/stats/ logic ==="
echo ""

# Login
echo "1️⃣ Login..."
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"trest","password":"trest2026"}')

TOKEN=$(echo "$TOKEN_RESP" | grep -o '"access":"[^"]*' | cut -d'"' -f4)
USER_ID=$(echo "$TOKEN_RESP" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

echo "✅ Login successful (User ID: $USER_ID)"
echo ""

# Call stats without token
echo "2️⃣ Stats WITHOUT token..."
curl -s http://localhost:8000/api/stats/ | python3 -m json.tool
echo ""

# Call stats with token
echo "3️⃣ Stats WITH token..."
curl -s http://localhost:8000/api/stats/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

