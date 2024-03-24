
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

def read_pmd_csv(files, csv_outpath=None, json_outpath=None, min_lines=10, delete_path=None):
    """pmc-cpdのcsvファイルパスのリストを受け取り集計する"""

    file_dict = {}
    total_lines = 0
    total_tokens = 0
    rows = []
    new_rows = []
    header = None

    for file in files:
        with open(file, 'r') as file:
            # https://pmd.github.io/pmd/pmd_userdocs_cpd_report_formats.html#csv
            # lines,tokens,occurrences, ...
            read_rows = list(csv.reader(file))
            if header is None:
                header = read_rows[0]
            rows += read_rows[1:]

    # linesでソート
    rows = sorted(rows[1:], key=lambda x: int(x[0]), reverse=True)

    for i, row in enumerate(rows):
        lines = int(row[0])
        if lines < min_lines:
            continue

        tokens = int(row[1])
        occurrences = int(row[2])

        # 検出数に応じて列数可変、filepathをdictへ
        for i in range(occurrences):
            index = 3 + 2 * i
            start_line = int(row[index])
            filepath = str(row[index + 1])
            if delete_path:
                filepath = filepath.replace(delete_path, "")

            if filepath in file_dict:
                file_dict[filepath].append((start_line, lines))
            else:
                file_dict[filepath] = []
                file_dict[filepath].append((start_line, lines))

        # lines_volume, tokens_volume列を追加
        lines_volume = lines * occurrences
        tokens_volume = tokens * occurrences
        row[5:] = row[3:]
        row[3] = str(lines_volume)
        row[4] = str(tokens_volume)

        total_lines += lines
        total_tokens += tokens
        new_rows.append(row)

    if csv_outpath:
        with open(csv_outpath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header + ["lines_volume", "tokens_volume"])
            writer.writerows(new_rows)

    if json_outpath:
        with open(json_outpath, mode="wt", encoding="utf-8") as f:
	        json.dump(file_dict, f, indent=2)

    return total_lines, total_tokens