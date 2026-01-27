#!/bin/bash

# API Testing Script
# Test barcha endpoints va auth qismi

BASE_URL="http://localhost:8000/api"
USERNAME="trest"
PASSWORD="trest2026"

echo "============================================"
echo "🔐 AUTHENTICATION TEST"
echo "============================================"

# 1. Login
echo -e "\n1️⃣ Login test..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .

# Extract tokens
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access // empty')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh // empty')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo "✅ Login successful!"
echo "Access Token: ${ACCESS_TOKEN:0:20}..."
echo "Refresh Token: ${REFRESH_TOKEN:0:20}..."

echo -e "\n============================================"
echo "🔄 TOKEN REFRESH TEST"
echo "============================================"

# 2. Refresh Token
echo -e "\n2️⃣ Token refresh test..."
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}")

echo "$REFRESH_RESPONSE" | jq .

NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access // empty')
if [ -z "$NEW_ACCESS_TOKEN" ]; then
  echo "❌ Token refresh failed!"
else
  echo "✅ Token refresh successful!"
  ACCESS_TOKEN=$NEW_ACCESS_TOKEN
fi

echo -e "\n============================================"
echo "📊 ANALYSIS API TEST"
echo "============================================"

# 3. Save analysis result (requires auth)
echo -e "\n3️⃣ Save analysis result test..."
SAVE_RESPONSE=$(curl -s -X POST "$BASE_URL/evaluations/save-result/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "tender": {"name": "Test Tender", "type": "open_bid"},
    "participants": [
      {"participant_name": "Company A", "total_weighted_score": 85},
      {"participant_name": "Company B", "total_weighted_score": 90}
    ],
    "ranking": [],
    "winner": {"participant_name": "Company B", "total_weighted_score": 90},
    "summary": "Test analysis"
  }')

echo "$SAVE_RESPONSE" | jq .

# 4. Get analysis history (requires auth)
echo -e "\n4️⃣ Get analysis history test..."
HISTORY_RESPONSE=$(curl -s -X GET "$BASE_URL/evaluations/history/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$HISTORY_RESPONSE" | jq .

echo -e "\n============================================"
echo "✅ ALL TESTS COMPLETED"
echo "============================================"
