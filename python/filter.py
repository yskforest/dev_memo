import pandas as pd
import argparse


def extract_columns_from_cloc_csv(input_csv_path, output_csv_path, columns_to_extract, prefix=None):
    """
    Extract specific columns from a cloc CSV file and save the result to another CSV file.

    :param input_csv_path: Path to the input cloc CSV file
    :param output_csv_path: Path to save the output CSV file
    :param columns_to_extract: List of column names to extract
    :param prefix: Optional prefix to remove from the 'filename' column
    """
    try:
        df = pd.read_csv(input_csv_path)

        # Check if the columns exist in the DataFrame
        missing_columns = [col for col in columns_to_extract if col not in df.columns]
        if missing_columns:
            raise ValueError(f"The following columns are missing in the input file: {missing_columns}")

        # Filter out rows where 'language' is 'SUM'
        df = df[df['language'] != 'SUM']

        # Remove the prefix from the 'filename' column if specified
        if prefix and 'filename' in df.columns:
            df['filename'] = df['filename'].apply(
                lambda x: x[len(prefix):] if x.startswith(prefix) else x)

        # Extract the specified columns
        extracted_df = df[columns_to_extract]

        extracted_df.to_csv(output_csv_path, index=False)
        print(f"Extracted columns saved to {output_csv_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract specific columns from a cloc CSV file.")
    parser.add_argument("input_csv", help="Path to the input cloc CSV file.")
    parser.add_argument("output_csv", help="Path to save the output CSV file.")
    parser.add_argument(
        "--columns",
        nargs="+",
        default=[
            "language",
            "filename",
            "blank",
            "comment",
            "code"],
        help="List of column names to extract from the input file (default: language, filename, blank, comment, code).")
    parser.add_argument("--prefix", default=None, help="Optional prefix to remove from the 'filename' column.")
    args = parser.parse_args()

    # Extract columns using the provided arguments
    extract_columns_from_cloc_csv(args.input_csv, args.output_csv, args.columns, args.prefix)
