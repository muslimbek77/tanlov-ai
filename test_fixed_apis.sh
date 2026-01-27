#!/bin/bash

echo "=== API Test - After Fix ==="
echo ""

# Login
echo "1️⃣ Login as trest..."
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"trest","password":"trest2026"}')

TOKEN=$(echo "$TOKEN_RESP" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi

echo "✅ Login successful"
echo ""

# Test history
echo "2️⃣ Testing /api/evaluations/history/ WITH token..."
HISTORY_RESP=$(curl -s http://localhost:8000/api/evaluations/history/ \
  -H "Authorization: Bearer $TOKEN")
echo "$HISTORY_RESP" | python3 -m json.tool 2>/dev/null || echo "$HISTORY_RESP"
echo ""

# Test stats
echo "3️⃣ Testing /api/stats/ WITH token..."
STATS_RESP=$(curl -s http://localhost:8000/api/stats/ \
  -H "Authorization: Bearer $TOKEN")
echo "$STATS_RESP" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESP"
echo ""

echo "✅ Test completed!"

