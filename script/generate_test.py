import pandas as pd


def calculate_params(param_a: str, param_b: str) -> str:
    try:
        # 空文字・None・"-" の場合はNG
        if not param_a or not param_b or param_a.strip() in ["", "-"] or param_b.strip() in ["", "-"]:
            return "NG: ParamAまたはParamBが未入力"

        a = float(param_a)
        b = float(param_b)

        # 範囲チェック（例：0～1000）
        if not (0 <= a <= 1000):
            return "NG: ParamAが範囲外です"
        if not (0 <= b <= 1000):
            return "NG: ParamBが範囲外です"

        # 小数点以下1桁まで表示（必要なら）
        return f"ParamA + ParamB = {round(a + b, 1)}"

    except (ValueError, AttributeError):
        return ""


def convert_csv_to_scenario(input_csv_path: str, output_csv_path: str) -> pd.DataFrame:

    column_names = pd.read_csv(input_csv_path, nrows=0).columns.tolist()
    dtype = {col: str for col in column_names}
    column_types = {}
    # 特定の型指定で読み込む
    # column_types = {
    #     "ParamC": float,
    #     "NO": int,
    # }
    dtype.update(column_types)
    df = pd.read_csv(input_csv_path, dtype=dtype)

    scenario_rows = []
    for _, row in df.iterrows():
        no = row["NO"]
        category1 = row["カテゴリ1"]
        category2 = row["カテゴリ2"]
        check_items = str(row["チェック項目"]).split("、") if pd.notna(row["チェック項目"]) else []

        test_name_base = f"{category1}_{category2}_{no}"
        param_cols = [col for col in df.columns if col not in ["NO", "カテゴリ1", "カテゴリ2", "チェック項目"]]

        params = "\n".join(
            f"{col}={row[col]}" for col in param_cols if pd.notna(row[col]) and str(row[col]).strip() not in ["", "-"]
        )

        for idx, check in enumerate(check_items, 1):
            remarks = ""
            ret = calculate_params(row.get("ParamA", ""), row.get("ParamB", ""))
            if ret:
                remarks += "\n" + ret

            operation = ""
            expectation = ""

            if category1 == "ログイン":
                operation = "ログインボタンを押す"
                expectation = "ログイン成功画面が表示される" if category2 == "正常" else "エラーメッセージが表示される"

            elif category1 == "検索":
                if category2 == "正常":
                    operation = "検索キーワードを入力して検索を実行"
                    expectation = "検索結果が表示される"
                else:
                    operation = "空のキーワードで検索を実行"
                    expectation = "検索エラーが表示される"

            else:
                operation = f"{category1}操作を実行する"
                expectation = "期待する結果が得られる"

            if check and check.strip():
                expectation = check.strip()

            scenario_rows.append(
                {
                    "NO": f"{no}-{idx}" if len(check_items) > 1 else no,
                    "テスト名": test_name_base,
                    "テストデータ": params,
                    "操作": operation or "",
                    "期待値": expectation or "",
                    "Debug": remarks.strip() or "",
                }
            )

    scenario_df = pd.DataFrame(scenario_rows).fillna("")
    scenario_df

    return scenario_df


if __name__ == "__main__":
    df = convert_csv_to_scenario("test_parameters.csv", "scenario_test.csv")
    df.to_csv("scenario_test.csv", index=False, encoding="utf-8-sig")
