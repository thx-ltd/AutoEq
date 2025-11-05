#!/usr/bin/env bash

# razer-v3-CSV-gameaux-conversion

# Batch processing for legacy v3 CSV content preset FastEqualizer-based EQ settings
# through AutoEq analysis, to 10_BAND_GRAPHIC_EQ_THX_EQ_PRESET ParametricEQ settings.

FIXED_BAND_EQ_CONFIG='THX_EQ_PRESET'

# Script must be run from ~/src/github.com/thx-ltd/AutoEq
WORKING_DIRECTORY='../../../../Downloads'

MEASUREMENT_FILE='scripts/flat.csv'
CSV_TARGET_FILE_DIRECTORY="../go-pkg/v4presets/testdata/out/measurement"
#"$WORKING_DIRECTORY/razer-gameaux-headphones-ANY-V3-20251007-w41_measurement/HP+SPKR"

if [ ! -d "$CSV_TARGET_FILE_DIRECTORY" ]; then
  echo "Error: Directory '$CSV_TARGET_FILE_DIRECTORY' not found."
  exit 1
fi

for file in "$CSV_TARGET_FILE_DIRECTORY"/*; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    echo "Processing file: $filename"

    uv run autoeq \
        --fixed-band-eq \
        --fixed-band-eq-config $FIXED_BAND_EQ_CONFIG \
        --fs 48000 --bit-depth 24 \
        --max-gain 12.0 \
        --input-file $MEASUREMENT_FILE \
        --target $CSV_TARGET_FILE_DIRECTORY/"$filename" \
        --output-dir $WORKING_DIRECTORY/out/HP+SPKR/"${filename%.*}"

    b="${filename%.*}"

    echo "Renaming eq_preset_values_only file"

    cp "$WORKING_DIRECTORY/out/HP+SPKR/${b}/flat/thx_eq_preset_values_only.json" \
        "$WORKING_DIRECTORY/out/HP+SPKR/${b}_eq_preset_values_only.json"

    # cp "$WORKING_DIRECTORY/out/${filename}/converted/converted ParametricEQ.txt" \
    #     "$WORKING_DIRECTORY/razer-gameaux-speakers-V3-20250908-w37-peq/${filename%.*}.peq"
  fi
done
