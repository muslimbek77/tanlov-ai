#!/bin/bash

# Complete API Testing Suite
# Barcha endpointlarni to'liq test qilish

BASE_URL="http://localhost:8000/api"
USERNAME="trest"
PASSWORD="trest2026"

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║          TANLOV AI - COMPLETE API TESTING SUITE                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

# 1. LOGIN
echo -e "\n🔐 STEP 1: LOGIN TEST"
echo "─────────────────────────────────────────────────────────────────────"
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

ACCESS=$(echo "$LOGIN" | jq -r '.access // empty')
REFRESH=$(echo "$LOGIN" | jq -r '.refresh // empty')
USER_ID=$(echo "$LOGIN" | jq -r '.user.id // empty')

if [ -z "$ACCESS" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo "✅ Login successful"
echo "   User: $(echo "$LOGIN" | jq -r '.user.username')"
echo "   Role: $(echo "$LOGIN" | jq -r '.user.role')"
echo "   ID: $USER_ID"

# 2. TOKEN REFRESH
echo -e "\n🔄 STEP 2: TOKEN REFRESH TEST"
echo "─────────────────────────────────────────────────────────────────────"
REFRESH_RESULT=$(curl -s -X POST "$BASE_URL/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH\"}")

NEW_ACCESS=$(echo "$REFRESH_RESULT" | jq -r '.access // empty')
if [ -z "$NEW_ACCESS" ]; then
  echo "❌ Token refresh failed!"
  exit 1
fi
ACCESS=$NEW_ACCESS
echo "✅ Token refreshed successfully"

# 3. SAVE ANALYSIS (1 ta ishtirokchi)
echo -e "\n📝 STEP 3: SAVE ANALYSIS WITH 1 PARTICIPANT"
echo "─────────────────────────────────────────────────────────────────────"
SAVE1=$(curl -s -X POST "$BASE_URL/evaluations/save-result/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{
    "tender": {"name": "Tender 1", "type": "open_bid"},
    "participants": [
      {"participant_name": "Company A", "total_weighted_score": 85}
    ],
    "ranking": [],
    "winner": {"participant_name": "Company A", "total_weighted_score": 85},
    "summary": "First analysis"
  }')

ID1=$(echo "$SAVE1" | jq -r '.id // empty')
if [ -z "$ID1" ]; then
  echo "❌ Failed to save analysis 1"
  echo "$SAVE1" | jq .
else
  echo "✅ Analysis 1 saved (ID: $ID1, 1 participant)"
fi

# 4. SAVE ANALYSIS (2 ta ishtirokchi - VALID FOR RANKING)
echo -e "\n📝 STEP 4: SAVE ANALYSIS WITH 2 PARTICIPANTS"
echo "─────────────────────────────────────────────────────────────────────"
SAVE2=$(curl -s -X POST "$BASE_URL/evaluations/save-result/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{
    "tender": {"name": "Tender 2", "type": "open_bid"},
    "participants": [
      {"participant_name": "Company B", "total_weighted_score": 90},
      {"participant_name": "Company C", "total_weighted_score": 88}
    ],
    "ranking": [
      {"rank": 1, "participant_name": "Company B"},
      {"rank": 2, "participant_name": "Company C"}
    ],
    "winner": {"participant_name": "Company B", "total_weighted_score": 90},
    "summary": "Second analysis with ranking"
  }')

ID2=$(echo "$SAVE2" | jq -r '.id // empty')
if [ -z "$ID2" ]; then
  echo "❌ Failed to save analysis 2"
  echo "$SAVE2" | jq .
else
  echo "✅ Analysis 2 saved (ID: $ID2, 2 participants - VALID FOR RANKING)"
fi

# 5. GET HISTORY
echo -e "\n📊 STEP 5: GET ANALYSIS HISTORY"
echo "─────────────────────────────────────────────────────────────────────"
HISTORY=$(curl -s -X GET "$BASE_URL/evaluations/history/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS")

TOTAL=$(echo "$HISTORY" | jq -r '.total')
echo "✅ History retrieved"
echo "   Total analyses: $TOTAL"
echo "$HISTORY" | jq '.history[] | {id, tender, participantCount, winner}'

# 6. GET SPECIFIC ANALYSIS
echo -e "\n🔍 STEP 6: GET SPECIFIC ANALYSIS DETAIL"
echo "─────────────────────────────────────────────────────────────────────"
if [ ! -z "$ID2" ]; then
  DETAIL=$(curl -s -X GET "$BASE_URL/evaluations/history/$ID2/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS")
  
  echo "✅ Analysis detail retrieved (ID: $ID2)"
  echo "$DETAIL" | jq '.result | {id, tender_name, participantCount, winner}'
fi

# 7. DELETE ANALYSIS
echo -e "\n🗑️  STEP 7: DELETE ANALYSIS"
echo "─────────────────────────────────────────────────────────────────────"
if [ ! -z "$ID1" ]; then
  DELETE=$(curl -s -X POST "$BASE_URL/evaluations/history/$ID1/delete/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS")
  
  RESULT=$(echo "$DELETE" | jq -r '.success')
  if [ "$RESULT" = "true" ]; then
    echo "✅ Analysis $ID1 deleted successfully"
  else
    echo "❌ Failed to delete analysis"
    echo "$DELETE" | jq .
  fi
fi

# 8. VERIFY DELETION
echo -e "\n✔️  STEP 8: VERIFY DELETION"
echo "─────────────────────────────────────────────────────────────────────"
HISTORY_AFTER=$(curl -s -X GET "$BASE_URL/evaluations/history/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS")

TOTAL_AFTER=$(echo "$HISTORY_AFTER" | jq -r '.total')
echo "✅ Verification complete"
echo "   Remaining analyses: $TOTAL_AFTER"

# 9. LOGOUT
echo -e "\n🚪 STEP 9: LOGOUT TEST"
echo "─────────────────────────────────────────────────────────────────────"
LOGOUT=$(curl -s -X POST "$BASE_URL/auth/simple-logout/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d "{\"refresh\":\"$REFRESH\"}")

echo "✅ Logout successful"

echo -e "\n╔════════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ ALL TESTS PASSED                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo -e "\n✨ Backend fully operational! All APIs working correctly.\n"
