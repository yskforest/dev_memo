import argparse
import pandas as pd
import sys
from collections import defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="指定パターンのCSVをExcelにまとめるスクリプト")
    parser.add_argument("directory", help="CSVファイルを検索するディレクトリ")
    parser.add_argument("output", help="出力するExcelファイル名（例: result.xlsx）")
    parser.add_argument(
        "-p",
        "--patterns",
        nargs="+",
        default=["aaa", "bbb"],
        help="検索キーワード。指定したキーワードがファイル名に含まれるCSVを検索します。（例: aaa bbb）",
    )
    args = parser.parse_args()

    search_dir = Path(args.directory)
    if not search_dir.is_dir():
        print(f"エラー: ディレクトリ '{search_dir}' が見つかりません。", file=sys.stderr)
        sys.exit(1)

    # キーワードごとにCSVファイルをまとめる
    prefix_to_files = defaultdict(list)
    for keyword in args.patterns:
        # キーワードをシート名（プレフィックス）とし、検索パターンを生成
        prefix = keyword
        glob_pattern = f"*{prefix}*.csv"

        for filepath in search_dir.glob(glob_pattern):
            prefix_to_files[prefix].append(filepath)

    if not prefix_to_files:
        print("該当するCSVファイルが見つかりませんでした。")
        return

    with pd.ExcelWriter(args.output) as writer:
        # プレフィックスのアルファベット順でシートを作成するためにソート
        for prefix in sorted(prefix_to_files.keys()):
            # ファイルリストから重複を削除し、パス順にソート
            file_list = sorted(list(set(prefix_to_files[prefix])))

            print(f"\n[{prefix}] に含まれるCSVファイル:")
            for f in file_list:
                print(f"  - {f}")

            df_list = []
            for file in file_list:
                try:
                    df = pd.read_csv(file)
                    df_list.append(df)
                except pd.errors.EmptyDataError:
                    print(f"警告: ファイル '{file}' は空のためスキップします。")
                except Exception as e:
                    print(f"エラー: ファイル '{file}' の読み込み中にエラーが発生しました: {e}", file=sys.stderr)

            if not df_list:
                print(f"警告: [{prefix}] には読み込めるCSVがなかったため、シートは作成されません。")
                continue

            combined_df = pd.concat(df_list, ignore_index=True)
            combined_df.to_excel(writer, sheet_name=prefix, index=False)

    print(f"\n✅ Excelファイル '{args.output}' を作成しました。")


if __name__ == "__main__":
    main()
