import pandas as pd
import plotly.express as px
import numpy as np


def plot_treemap_by_path(
    df,
    file_col: str,
    size_col: str,
    color_col: str,
    prefix_to_remove: str = None,  # <-- 引数を追加
    title="Treemap",
    vmin=None,
    vmax=None,
    max_depth=None,
):
    """
    ディレクトリ階層に基づくTreemapを描画（プレフィックス削除機能付き）

    Parameters:
    - df: pandas.DataFrame
    - file_col: ファイルパスを表す列名
    - size_col: Treemapのサイズに使う数値列
    - color_col: Treemapの色に使う数値列
    - prefix_to_remove: パスから削除したい共通のプレフィックス（例: "/workspace/src/"）
    - title: グラフタイトル
    - vmin: カラースケールの最小値
    - vmax: カラースケールの最大値
    - max_depth: Treemapに表示する階層の深さ
    """
    df = df.copy()
    df[size_col] = pd.to_numeric(df[size_col], errors="coerce")
    df[color_col] = pd.to_numeric(df[color_col], errors="coerce")
    df = df[df[size_col] > 0].dropna(subset=[size_col, color_col])

    # パスを文字列として扱うSeriesを作成
    paths = df[file_col].astype(str)

    # プレフィックスが指定されている場合、各パスの先頭から削除
    if prefix_to_remove:
        paths = paths.apply(lambda p: (p[len(prefix_to_remove) :] if p.startswith(prefix_to_remove) else p))

    # パスを分割
    path_parts = paths.str.strip("/").str.split("/")

    # 実際の最大深さ
    full_depth = path_parts.map(len).max()
    use_depth = max_depth if max_depth is not None else full_depth

    for i in range(use_depth):
        df[f"level_{i}"] = path_parts.map(lambda x: x[i] if i < len(x) else np.nan)

    color_min = vmin if vmin is not None else df[color_col].min()
    color_max = vmax if vmax is not None else df[color_col].max()

    fig = px.treemap(
        df,
        path=[f"level_{i}" for i in range(use_depth)],
        values=size_col,
        color=color_col,
        color_continuous_scale="OrRd",
        range_color=[color_min, color_max],
    )

    fig.update_traces(marker=dict(line=dict(width=2, color="black")))
    fig.update_layout(title=title, margin=dict(t=50, l=25, r=25, b=25))

    return fig
