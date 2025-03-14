import requests
import argparse
import sys
import subprocess
import os
import time

class BlackDuckAPI:
    def __init__(self, base_url: str, api_token: str):
        """
        Black Duck API クライアントの初期化
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.session = requests.Session()
        self.bearer_token = self.get_bearer_token()
        self.session.headers.update(self._get_headers())

    def get_bearer_token(self):
        """
        API トークンを使用してベアラートークンを取得
        """
        auth_url = f"{self.base_url}/api/tokens/authenticate"
        headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = self.session.post(auth_url, headers=headers)

        if response.status_code == 200:
            return response.json().get("bearerToken")
        else:
            raise Exception(f"Failed to obtain bearer token: {response.status_code} - {response.text}")

    def _get_headers(self):
        """
        API リクエスト用のヘッダーを設定（ベアラートークン使用）
        """
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def run_scan(self, project_name: str, version_name: str, target_dir: str):
        """
        Black Duck のスキャンを実行 (Detect スクリプト使用)
        """
        if not target_dir:
            raise ValueError("Scan target directory is required.")

        command = [
            "bash", "-c",
            f"curl -s -L https://detect.blackduck.com/detect10.sh | bash -s -- "
            f"--blackduck.url={self.base_url} "
            f"--blackduck.api.token={self.api_token} "
            f"--detect.project.name={project_name} "
            f"--detect.project.version.name={version_name} "
            f"--detect.source.path={target_dir}"
        ]

        print(f"Running scan command:\n{' '.join(command)}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print("Scan completed successfully.")
        else:
            print(f"Scan failed: {result.stderr}")
            sys.exit(1)

    def request_report_via_api(self, project_name: str, version_name: str):
        """
        REST API でバージョンレポートの作成をリクエスト
        """
        version_url = self.get_project_version_url(project_name, version_name)
        report_request_url = f"{version_url}/versionBomPolicyStatus"

        response = self.session.post(report_request_url, headers=self._get_headers())

        if response.status_code == 201:
            print(f"Report for {project_name} version {version_name} requested successfully.")
        else:
            raise Exception(f"Failed to request report: {response.status_code} - {response.text}")

    def delete_report_via_api(self, project_name: str, version_name: str):
        """
        REST API でバージョンレポートを削除
        """
        version_url = self.get_project_version_url(project_name, version_name)
        report_url = f"{version_url}/versionBomPolicyStatus"

        response = self.session.delete(report_url, headers=self._get_headers())

        if response.status_code in [200, 204]:
            print(f"Report for {project_name} version {version_name} deleted successfully.")
        else:
            raise Exception(f"Failed to delete report: {response.status_code} - {response.text}")

    def delete_scan_via_api(self, project_name: str, version_name: str):
        """
        REST API でスキャンデータを削除
        """
        version_url = self.get_project_version_url(project_name, version_name)
        scan_url = f"{version_url}/components"

        response = self.session.delete(scan_url, headers=self._get_headers())

        if response.status_code in [200, 204]:
            print(f"Scan data for {project_name} version {version_name} deleted successfully.")
        else:
            raise Exception(f"Failed to delete scan: {response.status_code} - {response.text}")

    def delete_version_via_api(self, project_name: str, version_name: str):
        """
        REST API でプロジェクトのバージョンを削除
        """
        version_url = self.get_project_version_url(project_name, version_name)

        response = self.session.delete(version_url, headers=self._get_headers())

        if response.status_code in [200, 204]:
            print(f"Version {version_name} of {project_name} deleted successfully.")
        else:
            raise Exception(f"Failed to delete version: {response.status_code} - {response.text}")

    def get_project_version_url(self, project_name: str, version_name: str):
        """
        指定したプロジェクトとバージョンの API URL を取得
        """
        projects = self.session.get(f"{self.base_url}/api/projects", headers=self._get_headers()).json().get("items", [])
        for project in projects:
            if project["name"] == project_name:
                versions = self.session.get(f"{project['_meta']['href']}/versions", headers=self._get_headers()).json().get("items", [])
                for version in versions:
                    if version["versionName"] == version_name:
                        return version["_meta"]["href"]
        raise Exception(f"Project '{project_name}' with version '{version_name}' not found.")

def main():
    parser = argparse.ArgumentParser(description="Black Duck REST API クライアント")

    parser.add_argument("--url", default="https://your-default-blackduck-server", help="Black Duck のベース URL")
    parser.add_argument("--token", default="your-default-api-token", help="Black Duck の API トークン")

    parser.add_argument("--scan", type=str, help="指定したプロジェクトに対してスキャンを実施")
    parser.add_argument("--scan-version", type=str, default="latest", help="スキャン対象のプロジェクトバージョン")
    parser.add_argument("--scan-dir", type=str, default=".", help="スキャン対象のディレクトリ")

    parser.add_argument("--report", type=str, help="指定したプロジェクトのレポートを作成")
    parser.add_argument("--report-version", type=str, default="latest", help="レポート対象のプロジェクトバージョン")

    parser.add_argument("--delete-report", type=str, help="指定したプロジェクトのレポートを削除")
    parser.add_argument("--delete-scan", type=str, help="指定したプロジェクトのスキャンデータを削除")
    parser.add_argument("--delete-version", type=str, help="指定したプロジェクトのバージョンを削除")

    args = parser.parse_args()

    bd_api = BlackDuckAPI(args.url, args.token)

    if args.scan:
        bd_api.run_scan(args.scan, args.scan_version, args.scan_dir)
    elif args.report:
        bd_api.request_report_via_api(args.report, args.report_version)
    elif args.delete_report:
        bd_api.delete_report_via_api(args.delete_report, args.report_version)
    elif args.delete_scan:
        bd_api.delete_scan_via_api(args.delete_scan, args.scan_version)
    elif args.delete_version:
        bd_api.delete_version_via_api(args.delete_version, args.scan_version)

if __name__ == "__main__":
    main()
