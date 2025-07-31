from lxml import etree as ET
import argparse
import glob
import os


def remove_namespace(tree):
    for elem in tree.getiterator():
        if not hasattr(elem.tag, "find"):
            continue
        i = elem.tag.find("}")
        if i >= 0:
            elem.tag = elem.tag[i + 1 :]


def filter_cpd_xml(input_pattern, output_dir, min_lines):
    os.makedirs(output_dir, exist_ok=True)

    parser = ET.XMLParser(strip_cdata=False)

    for input_file in glob.glob(input_pattern):
        tree = ET.parse(input_file, parser)
        root = tree.getroot()

        remove_namespace(tree)

        for duplication in root.findall("duplication"):
            lines = int(duplication.get("lines"))
            if lines < min_lines:
                root.remove(duplication)

        # 出力ファイル名を入力ファイル名に "_filtered.xml" を付加
        base_name = os.path.basename(input_file)
        output_file_name = f"filtered_{os.path.splitext(base_name)[0]}.xml"
        output_path = os.path.join(output_dir, output_file_name)

        tree.write(output_path, encoding="utf-8", pretty_print=True, xml_declaration=True)

        print(f"finish filter: {input_file} -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PMD CPD XMLから指定行数未満の重複を削除する")
    parser.add_argument("input", help="入力XMLファイルのGlobパターン")
    parser.add_argument("-o", "--output_dir", default=".", help="出力ファイルの保存先ディレクトリ")
    parser.add_argument("-l", "--min_lines", type=int, default=10, help="残す重複の最小行数（デフォルト: 10）")
    args = parser.parse_args()

    filter_cpd_xml(args.input, args.output_dir, args.min_lines)
