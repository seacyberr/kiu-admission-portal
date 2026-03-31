#!/bin/bash
# Test script to register users and submit applications for all exam levels via API

BASE_URL="http://localhost:5001/api"

echo "================================================================================"
echo "TESTING APPLICATION SUBMISSION FOR ALL EXAM LEVELS VIA API"
echo "================================================================================"

# Get available programs
echo ""
echo "1. Fetching available programs..."
PROGRAMS=$(curl -s "$BASE_URL/admission/programs")
echo "   Found programs: $(echo $PROGRAMS | jq '.programs | length')"

# Get first program of each level
DEGREE_PROG=$(echo $PROGRAMS | jq '.programs[] | select(.level == "degree") | .id' | head -1)
DIPLOMA_PROG=$(echo $PROGRAMS | jq '.programs[] | select(.level == "diploma") | .id' | head -1)
HEC_PROG=$(echo $PROGRAMS | jq '.programs[] | select(.level == "hec") | .id' | head -1)

echo "   Degree program ID: $DEGREE_PROG"
echo "   Diploma program ID: $DIPLOMA_PROG"
echo "   HEC program ID: $HEC_PROG"

# Function to register and apply
test_exam_level() {
    local LEVEL=$1
    local EMAIL=$2
    local PASSWORD="TestPass123!"
    local FIRST_NAME=$3
    local LAST_NAME=$4
    local PROG_ID=$5
    local EXAM_YEAR=$6
    local INDEX_NUM=$7
    local DOB=$8
    local GENDER=$9
    local DISTRICT=${10}
    local KIN_NAME=${11}
    local KIN_PHONE=${12}
    local KIN_REL=${13}
    local UNEB_GRADES=${14}
    
    echo ""
    echo "============================================================"
    echo "Testing $LEVEL exam level"
    echo "============================================================"
    
    # Register user
    echo ""
    echo "1. Registering user: $EMAIL"
    REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"firstName\":\"$FIRST_NAME\",\"lastName\":\"$LAST_NAME\"}")
    
    if echo $REGISTER | grep -q "token"; then
        echo "   ✓ User registered successfully"
    elif echo $REGISTER | grep -q "needsVerification"; then
        echo "   ℹ User registered, OTP verification required"
        # Get OTP from database (for testing purposes)
        OTP_CODE=$(sqlite3 /home/sea/Downloads/Kiu-Admission-Portal/artifacts/flask-api/instance/kiu_admissions.db \
            "SELECT code FROM otp_codes WHERE user_id = (SELECT id FROM users WHERE email = '$EMAIL') ORDER BY created_at DESC LIMIT 1" 2>/dev/null)
        if [ -z "$OTP_CODE" ]; then
            echo "   ✗ Could not retrieve OTP from database"
            return 1
        fi
        echo "   ℹ Verifying OTP: $OTP_CODE"
        VERIFY=$(curl -s -X POST "$BASE_URL/auth/verify-otp" \
            -H "Content-Type: application/json" \
            -d "{\"email\":\"$EMAIL\",\"code\":\"$OTP_CODE\"}")
        if echo $VERIFY | grep -q "token"; then
            echo "   ✓ OTP verified successfully"
        else
            echo "   ✗ OTP verification failed: $VERIFY"
            return 1
        fi
    elif echo $REGISTER | grep -q "already exists"; then
        echo "   ℹ User already exists, proceeding to login"
    else
        echo "   ✗ Registration failed: $REGISTER"
        return 1
    fi
    
    # Login user
    echo ""
    echo "2. Logging in user: $EMAIL"
    LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
    
    TOKEN=$(echo $LOGIN | jq -r '.token')
    
    if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
        echo "   ✓ Login successful, token obtained"
    elif echo $LOGIN | grep -q "needsVerification"; then
        echo "   ℹ Login requires OTP verification"
        # Wait a moment for OTP to be saved to database
        sleep 1
        # Get OTP from database
        OTP_CODE=$(sqlite3 /home/sea/Downloads/Kiu-Admission-Portal/artifacts/flask-api/instance/kiu_admissions.db \
            "SELECT code FROM otp_codes WHERE user_id = (SELECT id FROM users WHERE email = '$EMAIL') ORDER BY created_at DESC LIMIT 1" 2>/dev/null)
        if [ -z "$OTP_CODE" ]; then
            echo "   ✗ Could not retrieve OTP from database"
            return 1
        fi
        echo "   ℹ Verifying OTP: $OTP_CODE"
        VERIFY=$(curl -s -X POST "$BASE_URL/auth/verify-otp" \
            -H "Content-Type: application/json" \
            -d "{\"email\":\"$EMAIL\",\"code\":\"$OTP_CODE\"}")
        if echo $VERIFY | grep -q "token"; then
            TOKEN=$(echo $VERIFY | jq -r '.token')
            echo "   ✓ OTP verified successfully, token obtained"
        else
            echo "   ✗ OTP verification failed: $VERIFY"
            return 1
        fi
    else
        echo "   ✗ Login failed: $LOGIN"
        return 1
    fi
    
    # Create application
    echo ""
    echo "3. Submitting application..."
    APP_DATA="{\"programIds\":[$PROG_ID],\"examLevel\":\"$LEVEL\",\"examYear\":$EXAM_YEAR,\"indexNumber\":\"$INDEX_NUM\",\"unebGrades\":$UNEB_GRADES,\"dateOfBirth\":\"$DOB\",\"gender\":\"$GENDER\",\"nationality\":\"Ugandan\",\"district\":\"$DISTRICT\",\"nextOfKinName\":\"$KIN_NAME\",\"nextOfKinPhone\":\"$KIN_PHONE\",\"nextOfKinRelationship\":\"$KIN_REL\"}"
    
    APP_RESPONSE=$(curl -s -X POST "$BASE_URL/admission/applications" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "$APP_DATA")
    
    if echo $APP_RESPONSE | grep -q "applicationNumber"; then
        APP_NUM=$(echo $APP_RESPONSE | jq -r '.applicationNumber')
        APP_ID=$(echo $APP_RESPONSE | jq -r '.id')
        echo "   ✓ Application submitted successfully"
        echo "   ✓ Application Number: $APP_NUM"
        echo "   ✓ Application ID: $APP_ID"
        echo "   ✓ Status: $(echo $APP_RESPONSE | jq -r '.status')"
        echo "   ✓ Exam Level: $(echo $APP_RESPONSE | jq -r '.examLevel')"
    else
        echo "   ✗ Application submission failed: $APP_RESPONSE"
        return 1
    fi
    
    # Verify application
    echo ""
    echo "4. Verifying application..."
    MY_APP=$(curl -s "$BASE_URL/admission/applications/mine" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo $MY_APP | grep -q "applicationNumber"; then
        echo "   ✓ Application found in database"
        echo "   ✓ Application Number: $(echo $MY_APP | jq -r '.application.applicationNumber')"
    else
        echo "   ✗ Application not found"
        return 1
    fi
    
    return 0
}

# Test A-Level
test_exam_level "a_level" "applicant_alevel@test.com" "Alice" "A-Level" \
    "$DEGREE_PROG" 2020 "U0001/001" "2000-04-04" "male" "Kampala" \
    "John Doe" "0701240315" "Father" \
    '{"olevel":[{"subject":"Mathematics","grade":"D1","points":1},{"subject":"English Language","grade":"D2","points":2},{"subject":"Physics","grade":"C3","points":3},{"subject":"Chemistry","grade":"C4","points":4},{"subject":"Biology","grade":"C5","points":5}],"alevel":[{"subject":"Mathematics","grade":"A","points":6,"subjectType":"principal"},{"subject":"Physics","grade":"B","points":5,"subjectType":"principal"},{"subject":"General Paper","grade":"C","points":4,"subjectType":"subsidiary"}]}'
ALEVEL_RESULT=$?

# Test O-Level
test_exam_level "o_level" "applicant_olevel@test.com" "Bob" "O-Level" \
    "$DIPLOMA_PROG" 2020 "U0002/001" "2001-05-05" "female" "Wakiso" \
    "Jane Doe" "0701240316" "Mother" \
    '{"olevel":[{"subject":"Mathematics","grade":"D1","points":1},{"subject":"English Language","grade":"D2","points":2},{"subject":"Physics","grade":"C3","points":3},{"subject":"Chemistry","grade":"C4","points":4},{"subject":"Biology","grade":"C5","points":5}]}'
OLEVEL_RESULT=$?

# Test HEC
test_exam_level "hec" "applicant_hec@test.com" "Charlie" "HEC" \
    "$HEC_PROG" 2021 "U0003/001" "2002-06-06" "male" "Mukono" \
    "Peter Doe" "0701240317" "Guardian" \
    '{"olevel":[{"subject":"Mathematics","grade":"D1","points":1},{"subject":"English Language","grade":"D2","points":2},{"subject":"Physics","grade":"C3","points":3},{"subject":"Chemistry","grade":"C4","points":4}]}'
HEC_RESULT=$?

# Test Diploma
test_exam_level "diploma" "applicant_diploma@test.com" "Diana" "Diploma" \
    "$DIPLOMA_PROG" 2021 "U0004/001" "2000-07-07" "female" "Jinja" \
    "Mary Doe" "0701240318" "Sister" \
    '{"olevel":[{"subject":"Mathematics","grade":"D1","points":1},{"subject":"English Language","grade":"D2","points":2},{"subject":"Physics","grade":"C3","points":3},{"subject":"Chemistry","grade":"C4","points":4},{"subject":"Biology","grade":"C5","points":5}]}'
DIPLOMA_RESULT=$?

# Print summary
echo ""
echo "================================================================================"
echo "TEST SUMMARY"
echo "================================================================================"
echo "A_LEVEL         : $([ $ALEVEL_RESULT -eq 0 ] && echo '✓ PASSED' || echo '✗ FAILED')"
echo "O_LEVEL         : $([ $OLEVEL_RESULT -eq 0 ] && echo '✓ PASSED' || echo '✗ FAILED')"
echo "HEC             : $([ $HEC_RESULT -eq 0 ] && echo '✓ PASSED' || echo '✗ FAILED')"
echo "DIPLOMA         : $([ $DIPLOMA_RESULT -eq 0 ] && echo '✓ PASSED' || echo '✗ FAILED')"

ALL_PASSED=0
[ $ALEVEL_RESULT -ne 0 ] && ALL_PASSED=1
[ $OLEVEL_RESULT -ne 0 ] && ALL_PASSED=1
[ $HEC_RESULT -ne 0 ] && ALL_PASSED=1
[ $DIPLOMA_RESULT -ne 0 ] && ALL_PASSED=1

echo ""
if [ $ALL_PASSED -eq 0 ]; then
    echo "Overall Result: ✓ ALL TESTS PASSED"
else
    echo "Overall Result: ✗ SOME TESTS FAILED"
fi

exit $ALL_PASSED