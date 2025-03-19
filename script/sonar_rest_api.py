import requests
import csv

# SonarQubeの設定
SONARQUBE_URL = "http://<sonarqube-server>"
PROJECT_KEY = "<your_project_key>"
AUTH_TOKEN = "<your-auth-token>"

# API URL
api_url = f"{SONARQUBE_URL}/api/issues/search?types=CODE_SMELL&rules=duplicated_blocks&componentKeys={PROJECT_KEY}"

# APIリクエスト
headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
response = requests.get(api_url, headers=headers)

# JSON取得
if response.status_code == 200:
    data = response.json()
    issues = data.get("issues", [])

    # CSV保存
    csv_filename = f"{PROJECT_KEY}_duplicated_code.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)

        # ヘッダー行
        csv_writer.writerow(["Key", "File", "Line", "Message"])

        # データ行
        for issue in issues:
            csv_writer.writerow(
                [issue.get("key"), issue.get("component"), issue.get("line", "N/A"), issue.get("message")]
            )

    print(f"CSVファイルが作成されました: {csv_filename}")
else:
    print(f"APIリクエスト失敗: {response.status_code} - {response.text}")
