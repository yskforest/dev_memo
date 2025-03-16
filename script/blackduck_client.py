import argparse
import sys
import subprocess
import time
import logging
from typing import Dict, Any, List

import requests


class RestApiClient:
    def __init__(self, base_url: str, headers: Dict[str, str] | None = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(headers or {})
        self.timeout = timeout

        # ロギング設定
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
        self.logger = logging.getLogger(__name__)

    def set_auth_token(self, token: str):
        """Bearer トークン認証を設定"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _log(self, message: str, level: str = "info"):
        """ログメッセージを出力"""
        log_levels = {
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "debug": self.logger.debug,
        }
        log_levels.get(level, self.logger.info)(message)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any] | List[Any] | None:
        """HTTPリクエストを実行"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)

        try:
            self._log(f"{method} request to {url} with {kwargs}", "debug")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            # JSONレスポンスの処理
            if "application/json" in response.headers.get("Content-Type", ""):
                try:
                    json_data = response.json()
                    self._log(f"Response: {response.status_code} (JSON)", "debug")
                    return json_data
                except ValueError:
                    self._log(f"Failed to parse JSON response from {url}", "warning")
                    return None

            # JSON以外のレスポンス
            self._log(f"Response: {response.status_code} (Text)", "debug")
            return {"status_code": response.status_code, "content": response.text}

        except requests.exceptions.Timeout:
            self._log(f"Timeout Error: {method} {url}", "error")
            return None
        except requests.exceptions.HTTPError as e:
            self._log(f"HTTP Error: {method} {url} → {e.response.status_code}: {e.response.text}", "error")
            return None
        except requests.exceptions.RequestException as e:
            self._log(f"Request Error: {method} {url} → {e}", "error")
            return None
        except Exception as e:
            self._log(f"Unexpected Error: {method} {url} → {e}", "error")
            raise

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any] | List[Any] | None:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[str, Any] | List[Any] | None:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Dict[str, Any] | List[Any] | None:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> Dict[str, Any] | List[Any] | None:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any] | List[Any] | None:
        return self._request("DELETE", endpoint, **kwargs)


class BlackDuckAPI(RestApiClient):
    def __init__(self, base_url: str, api_token: str, scan_timeout: int = 600, report_timeout: int = 300):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        super().__init__(base_url, headers=headers)

        self.api_token = api_token
        self.scan_timeout = scan_timeout
        self.report_timeout = report_timeout
        self.bearer_token = self.get_bearer_token()
        self.session.headers.update(self._get_headers())

    def get_bearer_token(self) -> str:
        """APIトークンを使用してBearerトークンを取得"""
        auth_url = f"{self.base_url}/api/tokens/authenticate"
        headers = {"Authorization": f"token {self.api_token}", "Accept": "application/json"}

        response = self.post(auth_url, headers=headers)
        if response and "bearerToken" in response:
            return response["bearerToken"]
        raise Exception("Failed to obtain bearer token.")

    def _get_headers(self) -> Dict[str, str]:
        """Bearerトークンを含むヘッダーを取得"""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_project_version_url(self, project_name: str, version_name: str) -> str:
        """プロジェクトのバージョンURLを取得"""
        projects = self.get("/api/projects").get("items", [])
        for project in projects:
            if project["name"] == project_name:
                versions = self.get(f"{project['_meta']['href']}/versions").get("items", [])
                for version in versions:
                    if version["versionName"] == version_name:
                        return version["_meta"]["href"]
        raise Exception(f"Project '{project_name}' with version '{version_name}' not found.")

    def list_projects(self):
        """すべてのプロジェクトを一覧表示"""
        projects = self.get("/api/projects").get("items", [])
        for project in projects:
            self._log(f"Project: {project['name']}, URL: {project['_meta']['href']}")

    def list_project_versions(self, project_name: str):
        """特定のプロジェクトのバージョンを一覧表示"""
        project_url = self.get_project_version_url(project_name, "")
        versions = self.get(f"{project_url}/versions").get("items", [])
        for version in versions:
            self._log(f"Version: {version['versionName']}, URL: {version['_meta']['href']}")

    def run_scan(self, project_name: str, version_name: str, target_dir: str):
        if not target_dir:
            raise ValueError("Scan target directory is required.")

        command = [
            "bash",
            "-c",
            f"curl -s -L https://detect.blackduck.com/detect10.sh | bash -s -- "
            f"--blackduck.url={self.base_url} "
            f"--blackduck.api.token={self.api_token} "
            f"--detect.project.name={project_name} "
            f"--detect.project.version.name={version_name} "
            f"--detect.source.path={target_dir}",
        ]

        print(f"Running scan command:\n{' '.join(command)}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print("Scan completed successfully.")
        else:
            print(f"Scan failed return code {result.returncode}: {result.stderr}")
            sys.exit(1)

    def check_scan_status(self, project_name: str, version_name: str) -> str:
        """特定のプロジェクトバージョンのスキャン状況を取得"""
        codelocations = self.get("/api/codelocations").get("items", [])
        for location in codelocations:
            if location.get("projectName") == project_name and location.get("versionName") == version_name:
                return location.get("scanStatus", "UNKNOWN")
        return "NOT_FOUND"

    def request_version_report(self, project_name: str, version_name: str) -> str:
        """バージョンレポートの作成を要求しレポートURLを返す"""
        version_url = self.get_project_version_url(project_name, version_name)
        report_request_url = f"{version_url}/reports"
        json_data = {"reportFormat": "CSV", "locale": "ja_JP", "categories": ["VERSION"], "includeSubprojects": "true"}

        response = self.post(report_request_url, json=json_data)
        if response:
            return response.headers.get("Location", "")
        raise Exception("Failed to request report.")

    def check_report_status(self, report_url: str, timeout_seconds: int = 300) -> str:
        """レポートの生成状況を監視"""
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            time.sleep(5)
            response = self.get(report_url)
            if response and response.get("status") == "COMPLETED":
                return response["_meta"]["href"] + "/download"
            elif response and response.get("status") == "FAILED":
                raise Exception("Report generation failed.")
        raise TimeoutError(f"Report generation timed out after {timeout_seconds} seconds.")

    def delete_report(self, report_url: str):
        """レポートを削除"""
        response = self.delete(report_url)
        if response is not None:
            self._log(f"Report deleted successfully: {report_url}")

    def delete_scan_by_project_version(self, project_name: str, version_name: str):
        """特定のプロジェクトバージョンのスキャンを削除"""
        codelocations = self.get("/api/codelocations").get("items", [])
        deleted_count = 0

        for location in codelocations:
            if location.get("projectName") == project_name and location.get("versionName") == version_name:
                scan_url = location["_meta"]["href"]
                if self.delete(scan_url) is not None:
                    deleted_count += 1

        self._log(
            f"Successfully deleted {deleted_count} scan(s) for project '{project_name}' version '{version_name}'."
        )

    def delete_version(self, project_name: str, version_name: str):
        """プロジェクトバージョンを削除"""
        version_url = self.get_project_version_url(project_name, version_name)
        response = self.delete(version_url)
        if response is not None:
            self._log(f"Version {version_name} of {project_name} deleted successfully.")


def main():
    parser = argparse.ArgumentParser(description="Black Duck REST API クライアント")

    parser.add_argument("--url", default="https://your-default-blackduck-server", help="Black Duck のベース URL")
    parser.add_argument("--token", default="your-default-api-token", help="Black Duck の API トークン")
    parser.add_argument("--list-projects", action="store_true", help="プロジェクト一覧を取得")
    parser.add_argument("--list-versions", type=str, help="指定したプロジェクトのバージョン一覧を取得")

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

    if args.list_projects:
        bd_api.list_projects()
    if args.list_versions:
        bd_api.list_project_versions(args.scan)

    if args.scan:
        bd_api.run_scan(args.scan, args.scan_version, args.scan_dir)
    elif args.report:
        bd_api.request_version_report(args.report, args.report_version)
    elif args.delete_report:
        bd_api.delete_report(args.delete_report)
    elif args.delete_scan:
        bd_api.delete_scan(args.delete_scan, args.scan_version)
    elif args.delete_version:
        bd_api.delete_version(args.delete_version, args.scan_version)


if __name__ == "__main__":
    main()
