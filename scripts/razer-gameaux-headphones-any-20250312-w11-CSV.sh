#!/usr/bin/env bash

# Batch processing for legacy v3 CSV content preset FastEqualizer-based EQ settings
# through AutoEq analysis, to 10_BAND_GRAPHIC_EQ ParametricEQ settings.

PARAMETRIC_EQ_CONFIG='10_BAND_GRAPHIC_EQ'

# Script must be run from ~/src/github.com/thx-ltd/AutoEq
WORKING_DIRECTORY='../../../../Downloads'

MEASUREMENT_FILE='converted.csv'
CSV_TARGET_FILE_DIRECTORY="$WORKING_DIRECTORY/razer-gameaux-headphones-any-20250312-w11-CSV"

if [ ! -d "$CSV_TARGET_FILE_DIRECTORY" ]; then
  echo "Error: Directory '$CSV_TARGET_FILE_DIRECTORY' not found."
  exit 1
fi

for file in "$CSV_TARGET_FILE_DIRECTORY"/*; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    echo "Processing file: $filename"

    uv run autoeq \
        --parametric-eq \
        --parametric-eq-config $PARAMETRIC_EQ_CONFIG \
        --fs 48000 --bit-depth 24 \
        --max-gain 12.0 \
        --input-file $WORKING_DIRECTORY/$MEASUREMENT_FILE \
        --target $CSV_TARGET_FILE_DIRECTORY/$filename \
        --output-dir $WORKING_DIRECTORY/out/"${filename%.*}"

    cp "$WORKING_DIRECTORY/out/${filename%.*}/converted/converted ParametricEQ.txt" \
        "$WORKING_DIRECTORY/razer-gameaux-headphones-any-20250312-w11-peq/${filename%.*}.peq"
  fi
done
