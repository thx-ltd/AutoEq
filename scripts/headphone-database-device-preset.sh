#!/usr/bin/env bash

# Batch processing for headphone database device.

PARAMETRIC_EQ_CONFIG='THX_DEVICE_PRESET' # based on 8_PEAKING_WITH_SHELVES

# Headphone model measurement file
MEASUREMENT_SOURCE='oratory1990'
DEVICE='AKG K52'

MEASUREMENT_FILE="./measurements/$MEASUREMENT_SOURCE/data/over-ear/$DEVICE.csv"

# Target files
HARMAN_OE_2018="Harman over-ear 2018"
HARMAN_OE_2018_NO_BASS="Harman over-ear 2018 without bass"
DIFFUSE_FIELD_MINUS_1dB="Diffuse field 5128 -1dB per octave"
FLAT="zero"

TARGET=$HARMAN_OE_2018

# output directory
OUTPUT_DIR="./output"

# Script must be run from the ./scripts directory, i.e., ~/src/github.com/thx-ltd/AutoEq/scripts

uv run autoeq \
    --parametric-eq \
    --parametric-eq-config $PARAMETRIC_EQ_CONFIG \
    --fs 48000 --bit-depth 24 \
    --input-file "$MEASUREMENT_FILE" \
    --target "./targets/$TARGET.csv" \
    --output-dir "$OUTPUT_DIR"/"$DEVICE"/"$MEASUREMENT_SOURCE-$TARGET"
