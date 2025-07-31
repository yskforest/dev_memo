import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
import argparse
import glob
import os


def strip_ns(tag):
    """XMLタグから名前空間を除去する"""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def merge_ranges(ranges):
    """重複するトークン範囲をマージする"""
    if not ranges:
        return []
    ranges.sort()
    merged = [list(ranges[0])]
    for start, end in ranges[1:]:
        last = merged[-1]
        if start <= last[1] + 1:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged


def calc_clone_ratio(input_files, output_file, min_lines):
    """複数のCPD XMLファイルからクローンカバレッジを計算し、CSVに出力する"""
    token_data = defaultdict(lambda: {"total": 0, "ranges": []})

    for input_file in input_files:
        print(f"input file:{input_file}")
        tree = ET.parse(input_file)
        root = tree.getroot()

        # 各ファイルの総トークン数を取得
        for elem in root:
            if strip_ns(elem.tag) == "file" and "totalNumberOfTokens" in elem.attrib:
                path = elem.attrib["path"]
                total = int(elem.attrib["totalNumberOfTokens"])
                token_data[path]["total"] += total

        # duplicationセクション処理
        for elem in root:
            if strip_ns(elem.tag) != "duplication":
                continue

            lines = int(elem.attrib.get("lines", 0))
            if lines < min_lines:
                continue  # フィルタ

            for f in elem:
                if strip_ns(f.tag) != "file":
                    continue
                path = f.attrib["path"]
                begin = int(f.attrib["begintoken"])
                end = int(f.attrib["endtoken"])
                token_data[path]["ranges"].append((begin, end))

    # 結果集計
    total_project_tokens = 0
    total_project_clone_tokens = 0
    results = []

    for path, info in token_data.items():
        total = info["total"]
        if total == 0:
            continue
        total_project_tokens += total

        merged = merge_ranges(info["ranges"])
        clone_tokens = sum(end - start + 1 for start, end in merged)
        total_project_clone_tokens += clone_tokens
        ratio = (clone_tokens / total) * 100

        results.append(
            {"file": path, "total_tokens": total, "clone_tokens": clone_tokens, "clone_ratio(%)": round(ratio, 2)}
        )

    # CSV出力
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "total_tokens", "clone_tokens", "clone_ratio(%)"])
        writer.writeheader()
        writer.writerows(results)

    # プロジェクト全体のクローン率出力
    if total_project_tokens == 0:
        coverage = 0.0
    else:
        coverage = (total_project_clone_tokens / total_project_tokens) * 100

    print(f"出力完了: {output_file}")
    print(f"プロジェクト全体のクローンカバレッジ: {coverage:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CPD XMLからクローンカバレッジを集計（ファイル単位 & プロジェクト全体）"
    )
    parser.add_argument("input_pattern", help="入力XMLファイルのパターン（例: 'data/*.xml'）")
    parser.add_argument("--output", "-o", required=True, help="出力CSVファイルパス")
    parser.add_argument("--min-lines", "-l", type=int, default=10, help="対象とする最小クローン行数（デフォルト: 10）")
    args = parser.parse_args()

    input_files = glob.glob(args.input_pattern)
    if not input_files:
        print(f"エラー: パターン '{args.input_pattern}' に一致するファイルが見つかりませんでした。")
        exit(1)

    calc_clone_ratio(input_files, args.output, args.min_lines)
