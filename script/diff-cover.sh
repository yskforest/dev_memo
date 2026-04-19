#/bin/bash

for file in coverage_xml/*.xml; do
    echo "Processing $file..."
    # 文字列を削除
    sed -i 's|YYY||g' "$file"
    sed -i 's|YYY||g' "$file"
done

diff-cover coverage_xml/*.xml --html-report report_all.html --compare-branch=XXX

for file in coverage_xml/*.xml; do
    # ファイル名からベース名を取得してレポート名を決定
    filename=$(basename "$file" .xml)
    diff-cover "$file" --html-report "report_${filename}.html" --compare-branch=XXX
done
