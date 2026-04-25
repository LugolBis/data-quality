#!/bin/bash

URL="https://yago-knowledge.org/data/yago3/yago-3.0.2-native.7z"
ARCHIVE_NAME="yago-3.0.2-native.7z"
TARGET_FILE="yagoDateFacts.tsv"

if command -v wget &> /dev/null; then
    echo "|- Downloading YAGO3 data (this may take a while depending on your connection)..."
    wget -O "$ARCHIVE_NAME" "$URL"

    if command -v 7z &> /dev/null; then
        echo "|- Extracting $TARGET_FILE from the archive..."
        # Extracts only the specific target file, ignoring the full folder structure (-r searches recursively)
        7z e "$ARCHIVE_NAME" "*$TARGET_FILE" -r

        echo "|- Cleaning up the archive."
        rm "$ARCHIVE_NAME"

        echo "\- Extraction done ! $TARGET_FILE is ready to use."
    else
        echo "Command '7z' isn't available."
        exit 1
    fi
else
    echo "Command 'wget' isn't available."
    exit 1
fi

