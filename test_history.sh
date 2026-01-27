#!/bin/bash

echo "=== Testing History Endpoint ==="
echo ""

# Login
echo "1️⃣ Login..."
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"trest","password":"trest2026"}')

TOKEN=$(echo "$TOKEN_RESP" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  echo "Response: $TOKEN_RESP"
  exit 1
fi

echo "✅ Login successful"
echo "Token: ${TOKEN:0:50}..."
echo ""

# Test history without token
echo "2️⃣ Testing history WITHOUT token..."
NO_TOKEN_RESP=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/evaluations/history/)
echo "$NO_TOKEN_RESP"
echo ""

# Test history with token
echo "3️⃣ Testing history WITH token..."
WITH_TOKEN_RESP=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/evaluations/history/ \
  -H "Authorization: Bearer $TOKEN")
echo "$WITH_TOKEN_RESP"
echo ""

# Test stats
echo "4️⃣ Testing stats WITH token..."
STATS_RESP=$(curl -s http://localhost:8000/api/stats/ \
  -H "Authorization: Bearer $TOKEN")
echo "$STATS_RESP" | head -20
echo ""

