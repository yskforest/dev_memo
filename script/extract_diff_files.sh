#!/bin/bash

# === 設定項目 ===
BRANCH="main"
TARGET_COMMIT="abaa45c0ec9a5a85e249e97945cb5984c099cc28"
DIFF_PAIRS=(
    "35beb51169769897f1974b2e223b2ae0a0a78e9d abaa45c0ec9a5a85e249e97945cb5984c099cc28"
#   "789abc 012def"
)

OUTPUT_LIST="existing_diff_files.txt"
OUTPUT_DIR="diff_files"

# === 初期化 ===
> all_diff_files.txt

# === 各ペアの差分ファイルを取得 ===
for pair in "${DIFF_PAIRS[@]}"; do
    read COMMIT1 COMMIT2 <<< "$pair"
    echo "🔍 Diff: $COMMIT1 ↔ $COMMIT2"
    git diff --name-only "$COMMIT1" "$COMMIT2" >> all_diff_files.txt
done

# === 重複除去 ===
sort -u all_diff_files.txt > merged_diff_files.txt

# === 指定コミット（または HEAD）に存在するファイルだけ抽出 ===
git checkout "$BRANCH" > /dev/null 2>&1
grep -Fxf merged_diff_files.txt <(git ls-tree -r --name-only "$TARGET_COMMIT") > "$OUTPUT_LIST"

# === ファイルを取得（必要な場合） ===
mkdir -p "$OUTPUT_DIR"
while IFS= read -r file; do
    mkdir -p "$OUTPUT_DIR/$(dirname "$file")"
    cp "$file" "$OUTPUT_DIR/$file"
done < "$OUTPUT_LIST"

echo "✅ 完了: $OUTPUT_LIST に一覧出力、$OUTPUT_DIR にファイルコピー済み"
