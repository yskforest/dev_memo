
def read_cpd_csv(filepaths, min_lines=10):
    try:
        # リスト内のすべてのCSVファイルを読み込む
        df_list = []
        for filepath in filepaths:
            # linesがmin_lines行以上の行のみを読み込む
            df = dd.read_csv(filepath, usecols=['lines', 'tokens', 'occurrences'])
            df = df[df['lines'] >= min_lines]
            
            # DataFrameの型を整数に変更する
            df = df.map_partitions(lambda partition: partition.astype(int))

            df_list.append(df)
        
        # 読み込んだすべてのデータフレームを結合する
        df_combined = dd.concat(df_list)

        return df_combined
    except Exception as e:
        print(f"Error reading CPD CSV output: {e}")
        return None

def aggregate_cpd_df(df):
    try:
        duplication_count = df[['lines', 'occurrences']].groupby('lines').sum().compute()
        print("集計結果:")
        print(f"総行数: {duplication_count['lines'].sum()}")
        print("行数, 重複回数")
        for index, row in duplication_count.iterrows():
            print(f"{index}, {row['occurrences']}")
    except Exception as e:
        print(f"Error aggregating CPD DataFrame: {e}")

def aggregate_cpd_csv(csv_files, min_lines=10):
    try:
        total_lines = 0
        total_occurrences = 0

        for csv_file in csv_files:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    lines = int(row['lines'])
                    occurrences = int(row['occurrences'])

                    if lines >= min_lines:
                        total_lines += lines
                        total_occurrences += occurrences

        print("集計結果:")
        print(f"総行数: {total_lines}")
        print(f"総重複回数: {total_occurrences}")

    except Exception as e:
        print(f"Error aggregating CPD CSV output: {e}")