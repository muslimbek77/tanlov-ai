#!/bin/bash

echo "=== Two Participants Analysis Test ==="

# Get token
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"trest","password":"trest2026"}')

TOKEN=$(echo "$TOKEN_RESP" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:30}..."
echo ""

# Create a test PDF (using a text file as tender)
cat > /tmp/tender.txt << 'EOF'
TENDER DOCUMENT

Purpose: Software Development Services
Type: Open Tender
Requirements:
- Experience with React
- Experience with Python/Django
- 3+ years of experience
- Budget: 50,000 USD

Key Conditions:
- Delivery: 3 months
- Payment: 50% advance, 50% on completion
EOF

# Create participant files
cat > /tmp/participant1.txt << 'EOF'
PARTICIPANT 1 PROPOSAL

Name: TechCorp LLC
Experience: 5 years with React and Django
Team Size: 10 developers
Portfolio:
- Built 5 React applications
- 3 Django projects
Proposed Price: 45,000 USD
Timeline: 12 weeks
Strengths: Strong team, on-budget, experienced
EOF

cat > /tmp/participant2.txt << 'EOF'
PARTICIPANT 2 PROPOSAL

Name: Digital Solutions Inc
Experience: 8 years in web development
Team Size: 15 developers
Portfolio:
- 12 React applications
- 8 Django projects
Proposed Price: 48,000 USD
Timeline: 10 weeks
Strengths: More experience, faster delivery, proven track record
EOF

echo "1️⃣ Analyze Tender..."
TENDER_RESP=$(curl -s -X POST http://localhost:8000/api/evaluations/analyze-tender/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/tender.txt" \
  -F "language=uz_latn")

echo "Tender response: $(echo $TENDER_RESP | head -c 150)..."
echo ""

# Check if analysis was successful
if echo "$TENDER_RESP" | grep -q '"success":true'; then
  echo "✅ Tender analyzed successfully"
  echo ""
  
  echo "2️⃣ Analyze Participant 1..."
  P1_RESP=$(curl -s -X POST http://localhost:8000/api/evaluations/analyze-participant/ \
    -H "Authorization: Bearer $TOKEN" \
    -F "name=TechCorp LLC" \
    -F "file=@/tmp/participant1.txt" \
    -F "language=uz_latn")
  
  if echo "$P1_RESP" | grep -q '"success":true'; then
    echo "✅ Participant 1 analyzed"
  else
    echo "❌ Participant 1 analysis failed"
    echo "$P1_RESP" | head -c 200
  fi
  echo ""
  
  echo "3️⃣ Analyze Participant 2..."
  P2_RESP=$(curl -s -X POST http://localhost:8000/api/evaluations/analyze-participant/ \
    -H "Authorization: Bearer $TOKEN" \
    -F "name=Digital Solutions Inc" \
    -F "file=@/tmp/participant2.txt" \
    -F "language=uz_latn")
  
  if echo "$P2_RESP" | grep -q '"success":true'; then
    echo "✅ Participant 2 analyzed"
  else
    echo "❌ Participant 2 analysis failed"
    echo "$P2_RESP" | head -c 200
  fi
  
else
  echo "❌ Tender analysis failed"
  echo "$TENDER_RESP"
fi

echo ""
echo "Done!"

