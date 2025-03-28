#!/bin/bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <source_directory> <output_directory> <language1> [<language2> ... <languageN>]"
    exit 1
fi

CPD_SRC_DIR="$1"
CPD_OUTPUT_DIR="$2"
shift 2
LANGUAGES=("$@")

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

XSLT_FILE="${SCRIPT_DIR}/cpdhtml.xslt"
if [ ! -f "${XSLT_FILE}" ]; then
    wget -O "${XSLT_FILE}" https://raw.githubusercontent.com/pmd/pmd/master/pmd-core/etc/xslt/cpdhtml.xslt ||
        {
            echo "${XSLT_FILE} のダウンロードに失敗しました。"
            exit 1
        }
fi

XSLT_FILE_V2="${SCRIPT_DIR}/cpdhtml-v2.xslt"
if [ ! -f "${XSLT_FILE_V2}" ]; then
    wget -O "${XSLT_FILE_V2}" https://raw.githubusercontent.com/pmd/pmd/master/pmd-core/etc/xslt/cpdhtml-v2.xslt ||
        {
            echo "${XSLT_FILE_V2} のダウンロードに失敗しました。"
            exit 1
        }
fi

MINIMUM_TOKENS=100
MINIMUM_LINES=10

mkdir -p "${CPD_OUTPUT_DIR}"

run_cpd_analysis() {
    local lang="$1"
    local output_file="${CPD_OUTPUT_DIR}/cpd-results-${lang}.xml"
    local filtered_file="${CPD_OUTPUT_DIR}/filtered_cpd-results-${lang}.xml"

    echo "Running CPD for language: ${lang}"

    pmd cpd --minimum-tokens "${MINIMUM_TOKENS}" \
        --no-fail-on-violation \
        --dir "${CPD_SRC_DIR}" \
        --language "${lang}" \
        --format xml \
        --encoding UTF-8 >"${output_file}" || {
        status=$?
        if [ "$status" -eq 5 ]; then
            echo "PMD CPD returned ${status}, continuing anyway..."
        else
            echo "PMD CPD failed with status ${status}, exiting."
            exit "$status"
        fi
    }

    python3 "${SCRIPT_DIR}/cpd_xml_filter.py" "${output_file}" \
        -o "${CPD_OUTPUT_DIR}" -l "${MINIMUM_LINES}"

    xalan -in "${output_file}" \
        -xsl "${XSLT_FILE}" \
        -out "${CPD_OUTPUT_DIR}/cpd-results-${lang}_min_line${MINIMUM_LINES}.html" \
        -param lines $((MINIMUM_LINES - 1))

    xalan -in "${filtered_file}" \
        -xsl "${XSLT_FILE_V2}" \
        -out "${CPD_OUTPUT_DIR}/cpd-results-${lang}-v2.html"

    echo "CPD analysis for ${lang} completed successfully."
}

for lang in "${LANGUAGES[@]}"; do
    run_cpd_analysis "${lang}"
done

python3 "${SCRIPT_DIR}/culc_clone_ratio.py" "${CPD_OUTPUT_DIR}/cpd-results-*.xml" -o "${CPD_OUTPUT_DIR}/pmd_clone_ratio.csv"
