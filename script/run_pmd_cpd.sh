#!/bin/bash

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <source_directory> <output_directory> <language1> [<language2> ... <languageN>]"
  exit 1
fi

SRC_DIR="$1"
OUTPUT_DIR="$2"
echo "Running CPD on source directory: $SRC_DIR"
echo "Output will be saved in: $OUTPUT_DIR"
shift 2
LANGUAGES=("$@")

mkdir -p "$OUTPUT_DIR"

MINIMUM_TOKENS=100

for LANGUAGE in "${LANGUAGES[@]}"; do
  OUTPUT_FILE="$OUTPUT_DIR/cpd-results-$LANGUAGE.xml"

  echo "Running CPD for language: $LANGUAGE"

  pmd cpd \
    --minimum-tokens $MINIMUM_TOKENS \
    --dir "$SRC_DIR" \
    --language "$LANGUAGE" \
    --format xml \
    --encoding UTF-8 \
    >"$OUTPUT_FILE"

  xalan -in "$OUTPUT_FILE" -xsl ~/cpdhtml.xslt -out "${OUTPUT_FILE}.html" -param lines 10
  xalan -in "$OUTPUT_FILE" -xsl ~/cpdhtml-v2.xslt -out "${OUTPUT_FILE}-v2.html"

  if [ $? -eq 0 ]; then
    echo "CPD analysis for $LANGUAGE completed successfully. Results are saved in $OUTPUT_DIR"
  else
    echo "CPD analysis for $LANGUAGE failed."
  fi
done
