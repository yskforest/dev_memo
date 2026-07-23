#!/usr/bin/env bash
set -e

# PATH の通し（opencode がインストールされている可能性のあるパスを追加）
export PATH="$PATH:$HOME/.local/bin:$HOME/.opencode/bin"

# デフォルト値
REPO_PATH="/workspace/Open3D"
COUNT=3
PROMPT_FILE="/workspace/summarize_commit.prompt"
OUTPUT_DIR="/workspace/commit_summaries"
TEMP_DIR="/workspace/workspace_temp"

# オプション引数 & 位置引数の柔軟なパース
while [[ $# -gt 0 ]]; do
  case $1 in
    -r|--repo-path)
      REPO_PATH="$2"
      shift 2
      ;;
    -n|--count)
      COUNT="$2"
      shift 2
      ;;
    -p|--prompt)
      PROMPT_FILE="$2"
      shift 2
      ;;
    -o|--output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    -t|--temp-dir)
      TEMP_DIR="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [options] or $0 [repo_path] [count] [prompt_file] [output_dir] [temp_dir]"
      echo "Options:"
      echo "  -r, --repo-path PATH   Gitリポジトリパス (default: /workspace/Open3D)"
      echo "  -n, --count N          対象コミット数 (default: 3)"
      echo "  -p, --prompt FILE      プロンプトファイルパス (default: /workspace/summarize_commit.prompt)"
      echo "  -o, --output-dir DIR   成果物出力ディレクトリ (default: /workspace/commit_summaries)"
      echo "  -t, --temp-dir DIR     一時解析ディレクトリ (default: /workspace/workspace_temp)"
      exit 0
      ;;
    *)
      # 位置引数フォールバック
      if [ -z "$POSITIONAL_INDEX" ]; then POSITIONAL_INDEX=1; fi
      case $POSITIONAL_INDEX in
        1) REPO_PATH="$1" ;;
        2) COUNT="$1" ;;
        3) PROMPT_FILE="$1" ;;
        4) OUTPUT_DIR="$1" ;;
        5) TEMP_DIR="$1" ;;
      esac
      POSITIONAL_INDEX=$((POSITIONAL_INDEX + 1))
      shift
      ;;
  esac
done

# パス・依存関係チェック
if [ ! -d "$REPO_PATH" ]; then
    echo "[ERROR] Gitリポジトリが見つかりません: $REPO_PATH"
    exit 1
fi

if ! command -v opencode &> /dev/null; then
    echo "[ERROR] opencode コマンドが見つかりません。PATHを確認してください。"
    exit 1
fi

echo "=== コミットサマリ自動生成開始 (コンテナ内実行) ==="
echo "対象リポジトリ: $REPO_PATH"
echo "対象コミット数: $COUNT"
echo "プロンプト: $PROMPT_FILE"
echo "出力先ディレクトリ: $OUTPUT_DIR"
echo "一時解析ディレクトリ: $TEMP_DIR"

mkdir -p "$OUTPUT_DIR"

# 最新 N 件のコミットハッシュを取得（新しい順）
COMMITS=$(git -C "$REPO_PATH" log -n "$COUNT" --format="%H")

# プロンプトファイルの存在チェック
if [ ! -f "$PROMPT_FILE" ]; then
    echo "[ERROR] プロンプトファイルが見つかりません: $PROMPT_FILE"
    exit 1
fi

PROMPT_CONTENT=$(cat "$PROMPT_FILE")

# 各コミットを順次処理
INDEX=0
for COMMIT_HASH in $COMMITS; do
    INDEX=$((INDEX + 1))

    # 再現性と一意性のあるディレクトリ名（コミット日時_コミットハッシュ短縮形）
    # 例: 20260721_131333_d206cdb6
    COMMIT_DATE_HASH=$(git -C "$REPO_PATH" log -1 --format="%cd_%h" --date=format:"%Y%m%d_%H%M%S" "$COMMIT_HASH")
    TARGET_COMMIT_DIR="$OUTPUT_DIR/$COMMIT_DATE_HASH"
    SUMMARY_FILE="$TARGET_COMMIT_DIR/summary.md"

    echo ""
    echo "--------------------------------------------------"
    echo "[$INDEX/$COUNT] コミット処理中: $COMMIT_DATE_HASH ($COMMIT_HASH)"
    echo "--------------------------------------------------"

    # すでにサマリが存在する場合はスキップ
    if [ -f "$SUMMARY_FILE" ]; then
        echo "[SKIP] すでに成果物が存在するためスキップします: $TARGET_COMMIT_DIR"
        continue
    fi

    # 一時解析ディレクトリの初期化・クリーンアップ
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"

    # 1. numstat を純粋なTSV（追加行\t削除行\tファイル名）として出力
    git -C "$REPO_PATH" show --format="" --numstat "$COMMIT_HASH" | grep -v '^$' > "$TEMP_DIR/numstat.tsv"

    # 2. diff.patch の出力
    git -C "$REPO_PATH" show "$COMMIT_HASH" > "$TEMP_DIR/diff.patch"

    # 3. 変更のあったファイル群の抽出と元の相対ディレクトリ構造の復元
    CHANGED_FILES=$(git -C "$REPO_PATH" diff-tree --no-commit-id -r --name-only --diff-filter=ACMRT "$COMMIT_HASH")

    for FILE_PATH in $CHANGED_FILES; do
        TARGET_FILE_PATH="$TEMP_DIR/$FILE_PATH"
        mkdir -p "$(dirname "$TARGET_FILE_PATH")"
        git -C "$REPO_PATH" show "$COMMIT_HASH:$FILE_PATH" > "$TARGET_FILE_PATH" 2>/dev/null || true
    done

    # 4. opencode run の実行と summary.md の出力保存 (PROMPT_FILE の内容を使用)
    echo "[INFO] opencode run を実行中 (プロンプト: $PROMPT_FILE)..."
    (
        cd "$TEMP_DIR"
        opencode run "$PROMPT_CONTENT" > summary.md
    )

    # 5. 成果物の保存と一時ディレクトリの全削除
    if [ -s "$TEMP_DIR/summary.md" ]; then
        mkdir -p "$TARGET_COMMIT_DIR"
        cp "$TEMP_DIR/numstat.tsv" "$TARGET_COMMIT_DIR/"
        cp "$TEMP_DIR/diff.patch" "$TARGET_COMMIT_DIR/"
        cp "$TEMP_DIR/summary.md" "$TARGET_COMMIT_DIR/"
        echo "[SUCCESS] 成果物を保存しました: $TARGET_COMMIT_DIR"
    else
        echo "[ERROR] summary.md の生成に失敗しました: $COMMIT_HASH"
    fi

    # 解析対象ディレクトリ以下は削除して次のコミットを実施
    rm -rf "$TEMP_DIR"
    echo "[CLEANUP] 一時解析ディレクトリを削除しました: $TEMP_DIR"
done

echo ""
echo "=== 全コミット処理完了 ==="
