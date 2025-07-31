def path_split_df(df: pd.DataFrame, split_column: str, split_str="\\"):
    """指定の列を指定の文字列で分割して新規列として追加する"""
    df["split"] = df[split_column].apply(os.path.dirname).str.split(split_str)
    df_expand = df["split"].apply(pd.Series)

    directory_depth = len(df_expand.columns)
    tmp_columns = []
    for i in range(1, directory_depth + 1):
        tmp_columns.append(f"level{i}")
    df_expand = df_expand.set_axis(tmp_columns, axis=1)
    df = pd.concat([df, df_expand], axis=1)
    df = df.drop(columns="split")
    return df, directory_depth


def parse_cloc_csv(cloc_csv_filepath: str, remove_prefix_path: str = "") -> pd.DataFrame:
    """cloc出力のcsvファイルを読み込んでDataFrameに入れる"""

    df = pd.read_csv(cloc_csv_filepath, sep=",", na_filter=False, dtype={
        "blank": "int",
        "comment": "int",
        "code": "int",
    })

    df = df[["language", "filename", "blank", "comment", "code"]]
    # sum行の削除
    df = df[df['language'] != 'SUM']
    # df[["blank", "comment", "code"]] = df[["blank", "comment", "code"]].astype(int)
    df["count_line"] = df["blank"] + df["comment"] + df["code"]
    df["relative_filepath"] = df["filename"].str.replace(remove_prefix_path, "")
    df['directory'] = df['relative_filepath'].apply(lambda x: os.path.dirname(x))

    return df


class UnderstandMetrics():
    def __init__(self, csv_filepath: str, remove_prefix_path: str = ""):
        df_und_src = pd.read_csv(csv_filepath, sep=",", na_filter=False)

        df_und_src["File"] = df_und_src["File"].str.replace(remove_prefix_path, "")
        df_und_src['Directory'] = df_und_src['File'].apply(lambda x: os.path.dirname(x))

        self.selected_file_metrics = ['CountLine', 'CountLineCode', 'CountLineComment', 'MaxCyclomatic', 'MaxNesting']
        self.selected_func_metrics = [
            'CountLine',
            'CountLineCode',
            'CountLineComment',
            'CountLine',
            'Cyclomatic',
            'MaxNesting',
            'Essential']

        # ファイルの必要なメトリクスを抽出
        self.df_und_file = df_und_src[df_und_src["Kind"].str.contains("File")].copy().reset_index(drop=True)
        self.df_und_file = self.df_und_file.loc[:, ['Kind',
                                                    'Name',
                                                    'File',
                                                    'Directory',
                                                    'CountLine',
                                                    'CountLineCode',
                                                    'CountLineComment',
                                                    'MaxCyclomatic',
                                                    'MaxNesting']].copy().reset_index(drop=True)
        self.df_und_file[['CountLine', 'CountLineCode', 'MaxCyclomatic', 'MaxNesting', 'CountLineComment']] = self.df_und_file[[
            'CountLine', 'CountLineCode', 'MaxCyclomatic', 'MaxNesting', 'CountLineComment']].astype(int)
        self.df_und_file["CountLineCommentRatio"] = self.df_und_file["CountLineComment"] / self.df_und_file["CountLine"]

        # 関数の必要なメトリクスを抽出
        self.df_und_func = df_und_src[~df_und_src['Kind'].str.contains('Unknown') & df_und_src['Kind'].str.contains(
            'Method') | df_und_src['Kind'].str.contains('Function')].copy().reset_index(drop=True)
        self.df_und_func = self.df_und_func.loc[:,
                                                ['Kind',
                                                 'Name',
                                                 'File',
                                                 'Directory',
                                                 'CountLine',
                                                 'CountLineCode',
                                                 'CountLineComment',
                                                 'Cyclomatic',
                                                 'Essential',
                                                 'MaxNesting']].copy().reset_index(drop=True)
        self.df_und_func[['CountLine', 'Cyclomatic', 'MaxNesting', 'Essential', 'CountLineComment']] = self.df_und_func[[
            'CountLine', 'Cyclomatic', 'MaxNesting', 'Essential', 'CountLineComment']].astype(int)
        self.df_und_func["CountLineCommentRatio"] = self.df_und_func["CountLineComment"] / self.df_und_func["CountLine"]

        self.df_und_class = df_und_src[df_und_src["Kind"].str.contains("Class")].copy().reset_index(drop=True)


und_metrics = UnderstandMetrics(und_csv, remove_prefix_path="/var/jenkins_home/workspace/TEST/")
und_metrics.df_und_func
und_metrics.df_und_func.to_csv("func.csv")

und_metrics.df_und_func.groupby('Kind').sum().reset_index()
und_metrics.df_und_func.sum()

df = und_metrics.df_und_func.groupby('Directory').agg({'CountLine': 'sum'}).reset_index()
df, _ = path_split_df(df, "Directory", "/")
df
