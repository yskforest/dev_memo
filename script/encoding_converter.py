import argparse
import codecs
import csv
from glob import glob
from tqdm import tqdm
from chardet.universaldetector import UniversalDetector
from pathlib import Path


def is_probably_text_file(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" not in chunk
    except:
        return False


def detect_file_encoding(file_path: Path) -> str:
    """
    ファイルのエンコーディングを判定（UTF-8の場合はBOMあり/なしを厳密に）
    """
    detector = UniversalDetector()
    with open(file_path, "rb") as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()

    encoding = detector.result["encoding"]
    if encoding and encoding.lower() == "utf-8":
        with open(file_path, "rb") as f:
            if f.read(3) == b"\xef\xbb\xbf":
                return "utf-8-sig"
        return "utf-8"

    return encoding or "unknown"


def convert_file_encoding(file_path: Path, src_encoding: str, dest_encoding: str) -> bool:
    try:
        read_encoding = "utf-8-sig" if src_encoding.lower() == "utf-8-sig" else src_encoding
        with codecs.open(file_path, "r", encoding=read_encoding) as f:
            text = f.read()
        with codecs.open(file_path, "w", encoding=dest_encoding) as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"[ERROR] Conversion failed for {file_path}: {e}")
        return False


def process_all_files(file_paths, old_encoding, new_encoding, convert_enabled, csv_output_path):
    results = []

    for file_path in tqdm(file_paths):
        file_path = Path(file_path)
        if not is_probably_text_file(file_path):
            tqdm.write(f"[SKIP] Binary file: {file_path}")
            results.append((str(file_path), "binary"))
            continue

        detected_encoding = detect_file_encoding(file_path)
        results.append((str(file_path), detected_encoding))

        if convert_enabled:
            should_convert = False
            if detected_encoding and detected_encoding.lower() != new_encoding.lower():
                if old_encoding:
                    should_convert = detected_encoding.lower() == old_encoding.lower()
                else:
                    should_convert = True  # 変換対象：new_encoding 以外すべて

            if should_convert:
                if convert_file_encoding(file_path, detected_encoding, new_encoding):
                    tqdm.write(f"[OK] Converted: {file_path}")
                else:
                    tqdm.write(f"[FAIL] Failed to convert: {file_path}")

    with open(csv_output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File", "Encoding"])
        writer.writerows(results)

    print(f"\n[INFO] Encoding report saved to: {csv_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect and optionally convert file encodings (UTF-8 BOM aware).")
    parser.add_argument("-i", "--input_files", required=True, help='Input files (e.g., "src/**/*.txt")')
    parser.add_argument(
        "-o",
        "--old_encode",
        default=None,
        help="Only convert from this encoding. If omitted, all encodings except new_encode are converted.",
    )
    parser.add_argument("-n", "--new_encode", default="utf-8", help="Target encoding (default: utf-8 without BOM)")
    parser.add_argument(
        "-c", "--convert", action="store_true", help="Actually convert files. If omitted, only detect encodings."
    )
    parser.add_argument(
        "--csv_output", default="encoding_report.csv", help="CSV output file name (default: encoding_report.csv)"
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive glob search")
    args = parser.parse_args()

    file_paths = sorted(glob(args.input_files, recursive=args.recursive))
    file_paths = [f for f in file_paths if Path(f).is_file()]

    if not file_paths:
        print("[ERROR] No matching files found.")
    else:
        process_all_files(
            file_paths=file_paths,
            old_encoding=args.old_encode,
            new_encoding=args.new_encode,
            convert_enabled=args.convert,
            csv_output_path=args.csv_output,
        )
