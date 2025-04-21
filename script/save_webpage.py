import os
import shutil
import subprocess
from urllib.parse import urlparse
from glob import glob
import re
import argparse


def sanitize_filename(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def run_wget(wget_path: str, url: str, temp_dir: str):
    os.makedirs(temp_dir, exist_ok=True)
    result = subprocess.run(
        [
            wget_path,
            "--convert-links",
            "--page-requisites",
            "--adjust-extension",
            "--no-host-directories",
            "--cut-dirs=100",
            "--directory-prefix",
            temp_dir,
            url,
        ]
    )
    if result.returncode != 0:
        print(f"⚠️ wget exited with code {result.returncode}")


def detect_html_file(download_dir: str) -> str:
    html_files = glob(os.path.join(download_dir, "**/*.html"), recursive=True)
    if not html_files:
        raise FileNotFoundError("❌ HTMLファイルが見つかりません。")
    return html_files[0]


def move_resources(html_path: str, base_dir: str, output_dir: str):
    html_name = os.path.basename(html_path)
    base_name = sanitize_filename(html_name)
    files_dir = os.path.join(output_dir, base_name + "_files")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(files_dir, exist_ok=True)

    for filepath in glob(os.path.join(base_dir, "**/*"), recursive=True):
        if os.path.isdir(filepath) or filepath == html_path:
            continue
        shutil.move(filepath, os.path.join(files_dir, os.path.basename(filepath)))

    final_html_path = os.path.join(output_dir, html_name)
    shutil.move(html_path, final_html_path)
    return final_html_path, files_dir


def fix_links(html_file: str, files_folder: str):
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    def replacer(match):
        attr, quote, path = match.groups()
        if path.startswith(("http", "//", "/", "#")):
            return match.group(0)
        new_name = os.path.basename(path)
        return f"{attr}={quote}{os.path.basename(files_folder)}/{new_name}{quote}"

    html = re.sub(r'(href|src)=(["\'])([^"\']+?)\2', replacer, html)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)


def save_webpage_as_complete(wget_path: str, url: str, output_dir: str):
    temp_dir = "__temp_wget__"
    print(f"🌐 URL: {url}")
    print("🚀 wgetでダウンロード中...")
    run_wget(wget_path, url, output_dir)

    # print("🔍 HTMLファイルを検出中...")
    # html_path = detect_html_file(temp_dir)

    # print("🗂 ファイル整理中...")
    # final_html, files_dir = move_resources(html_path, temp_dir, output_dir)

    # print("🔗 リンク書き換え中...")
    # fix_links(final_html, files_dir)

    # shutil.rmtree(temp_dir)
    # print(f"✅ 完了: {final_html} + {os.path.basename(files_dir)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a webpage like browser 'Save As Complete'.")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("--wget", required=True, help="Path to wget.exe")
    parser.add_argument("--output", default="saved_page", help="Output directory (default: saved_page)")

    args = parser.parse_args()
    save_webpage_as_complete(args.wget, args.url, args.output)
