import pandas as pd
import plotly.express as px
import argparse
import os


def generate_pie_chart(csv_file, value_column, label_column, title, output_html):
    """CSVファイルから円グラフを作成"""

    data = pd.read_csv(csv_file)

    # Ensure necessary columns exist
    if value_column not in data.columns or label_column not in data.columns:
        raise KeyError(f"CSV must contain specified columns '{value_column}' and '{label_column}'.")

    # Exclude the 'SUM' row
    data = data[data[label_column] != 'SUM']

    # Create a pie chart with custom order
    fig = px.pie(
        data,
        values=value_column,  # Values for pie sections
        names=label_column,   # Labels for each section
        title=title,          # Title of the chart
        hole=0.0,             # Adjust for a donut chart if needed (0 for pie, >0 for donut)
        category_orders={label_column: data[label_column].tolist()}  # Custom order
    )

    # Display labels and percentages inside the pie chart
    fig.update_traces(textinfo='label+percent', textposition='inside')

    # Ensure the output directory exists before saving
    output_dir = os.path.dirname(output_html)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Save the chart as an HTML file
    fig.write_html(output_html)
    print(f"Generated interactive pie chart HTML file: {output_html}")


if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate a pie chart from a CSV file and output to HTML (Plotly-based)")
    parser.add_argument('csv_file', help="Path to the input CSV file")
    parser.add_argument('value_column', help="Column name for the values (size of pie sections)")
    parser.add_argument('label_column', help="Column name for the labels (names of pie sections)")
    parser.add_argument('title', help="Title of the chart")
    parser.add_argument('--output', default='output.html', help="Path to the output HTML file (default: output.html)")

    args = parser.parse_args()

    # Run the function
    generate_pie_chart(args.csv_file, args.value_column, args.label_column, args.title, args.output)
