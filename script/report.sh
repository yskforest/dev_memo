#!/bin/bash

# ===== 設定 =====
BLACKDUCK_URL="https://your-blackduck-instance.com"
API_TOKEN="your-api-token"
PROJECT_VERSION_URL="https://your-blackduck-instance.com/api/projects/12345/versions/67890"
REPORT_TYPE="VULNERABILITY"  # "VULNERABILITY", "LICENSE", "BOM"
MAX_ATTEMPTS=30  # 最大試行回数
SLEEP_TIME=10    # ポーリング間隔
REPORT_FILE="blackduck_report.pdf"

# ===== レポートをリクエスト =====
echo "Requesting report generation..."
REPORT_ID=$(curl -s -X POST "$BLACKDUCK_URL/api/reports" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "My_Report",
        "reportFormat": "PDF",
        "reportType": "'"$REPORT_TYPE"'",
        "projectVersion": "'"$PROJECT_VERSION_URL"'"
    }' | jq -r '.reportId')

if [ -z "$REPORT_ID" ] || [ "$REPORT_ID" == "null" ]; then
    echo "Failed to request report."
    exit 1
fi

echo "Report requested successfully. Report ID: $REPORT_ID"

# ===== レポートの生成完了をポーリング =====
echo "Waiting for report generation..."
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    REPORT_STATUS=$(curl -s -X GET "$BLACKDUCK_URL/api/reports/$REPORT_ID" \
        -H "Authorization: Bearer $API_TOKEN" | jq -r '.status')

    if [ "$REPORT_STATUS" == "COMPLETED" ]; then
        echo "Report generation completed."
        break
    fi

    echo "Report status: $REPORT_STATUS. Retrying in ${SLEEP_TIME} seconds..."
    sleep $SLEEP_TIME
    ((ATTEMPT++))
done

if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
    echo "Report generation did not complete in the expected time."
    exit 1
fi

# ===== レポートをダウンロード =====
echo "Downloading report..."
curl -o "$REPORT_FILE" -X GET "$BLACKDUCK_URL/api/reports/$REPORT_ID/download" \
    -H "Authorization: Bearer $API_TOKEN"

if [ $? -eq 0 ]; then
    echo "Report downloaded successfully: $REPORT_FILE"
else
    echo "Failed to download report."
    exit 1
fi
