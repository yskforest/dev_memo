import glob
import os
import argparse
import sys

import pandas as pd


def merge_csv_files(csv_files, output_file):
    if not csv_files:
        print("No CSV files to merge.")
        return

    merged_df = None

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        print(f"Processing: {csv_file}")

        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        df = df.rename(columns={col: f"{base_name}_{col}" for col in df.columns if col != "File"})

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="File", how="outer")

    merged_df.to_csv(output_file, index=False)
    print(f"Merged CSV saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Merge CSV files by 'File' column.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dir", help="Directory containing CSV files to merge")
    group.add_argument("--files", nargs="+", help="List of CSV files to merge")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    if args.dir:
        csv_files = glob.glob(os.path.join(args.dir, "*.csv"))
    else:
        csv_files = args.files

    merge_csv_files(csv_files, args.output)


if __name__ == "__main__":
    main()
