import json

# JSONファイルからデータを読み込む
with open("data.json", "r") as f:
    data = json.load(f)

# 与えられた範囲のリストを開始位置でソート
sorted_duplicate = sorted(data["duplicate"], key=lambda x: x["begintoken"])

# 重複しない全体の範囲を計算して合計する
total_tokens = 0
current_begin = None
current_end = None

for item in sorted_duplicate:
    if current_begin is None:  # 初めての範囲の場合
        current_begin = item["begintoken"]
        current_end = item["begintoken"] + item["tokens"] - 1
    else:
        if item["begintoken"] > current_end:  # 新しい範囲が前の範囲と重複しない場合
            total_tokens += current_end - current_begin + 1  # 前の範囲を加算
            current_begin = item["begintoken"]
            current_end = item["begintoken"] + item["tokens"] - 1
        else:  # 新しい範囲が前の範囲と重複する場合
            current_end = max(current_end, item["begintoken"] + item["tokens"] - 1)

# 最後の範囲を加算
if current_begin is not None:
    total_tokens += current_end - current_begin + 1

# 結果を出力
print("重複しない総数:", total_tokens)
