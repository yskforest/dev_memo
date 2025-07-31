from glob import glob
import sys
import os
import csv
import json

import pandas as pd
import plotly.express as px

df_und_org = pd.read_csv(understand_csv, sep=",", dtype=object, na_filter=False)
df_und_file = df_und_org[df_und_org["Kind"].str.contains("File")].copy().reset_index(drop=True)
df_und_file = df_und_file[["File", "CountLineCode", "CountLine", "CountLineComment", "RatioCommentToCode"]]
df_und_file[["CountLineCode", "CountLine", "CountLineComment"]] = df_und_file[[
    "CountLineCode", "CountLine", "CountLineComment"]].astype(int)
df_und_file[["RatioCommentToCode"]] = df_und_file[["RatioCommentToCode"]].astype(float)

df_und_file["File"] = df_und_file["File"].str.replace(remove_prefix_path, "")
df_und_file = path_split_df(df_und_file, "File", "/")

df_groupby = df_und_file.groupby(['level1', 'level2', 'level3', 'level4', 'level5'], as_index=False).sum()
df_groupby

# ツリーマップの作成
fig = px.treemap(
    df_groupby[df_groupby['RatioCommentToCode'] > 0],
    path=['level1', 'level2', 'level3'],  # 階層化されたフォルダ構造
    values='CountLineCode',  # 面積はCountLineCode
    color='RatioCommentToCode',  # 色はRatioCommentToCode（クローンコード率）
    color_continuous_scale='OrRd',  # 色のスケール
    title="CountLineCode(Area) - PmdCloneRatio(Color)",  # タイトル
)

# フォントサイズを調整
fig.update_traces(textfont_size=15)

# グラフ表示
fig.show()
