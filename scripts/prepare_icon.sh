#!/bin/bash
# scripts/prepare_icon.sh - Converts a PNG to ICNS for macOS

SOURCE_PNG=$1
DEST_ICNS=$2

if [ -z "$SOURCE_PNG" ] || [ -z "$DEST_ICNS" ]; then
    echo "Usage: ./scripts/prepare_icon.sh source.png destination.icns"
    exit 1
fi

if [ ! -f "$SOURCE_PNG" ]; then
    echo "Error: Source image $SOURCE_PNG not found."
    exit 1
fi

echo "Converting $SOURCE_PNG to $DEST_ICNS..."

# Create iconset directory
ICONSET="icon.iconset"
mkdir -p "$ICONSET"

# Resize images for various icon sizes
sips -z 16 16     "$SOURCE_PNG" --out "${ICONSET}/icon_16x16.png"
sips -z 32 32     "$SOURCE_PNG" --out "${ICONSET}/icon_16x16@2x.png"
sips -z 32 32     "$SOURCE_PNG" --out "${ICONSET}/icon_32x32.png"
sips -z 64 64     "$SOURCE_PNG" --out "${ICONSET}/icon_32x32@2x.png"
sips -z 128 128   "$SOURCE_PNG" --out "${ICONSET}/icon_128x128.png"
sips -z 256 256   "$SOURCE_PNG" --out "${ICONSET}/icon_128x128@2x.png"
sips -z 256 256   "$SOURCE_PNG" --out "${ICONSET}/icon_256x256.png"
sips -z 512 512   "$SOURCE_PNG" --out "${ICONSET}/icon_256x256@2x.png"
sips -z 512 512   "$SOURCE_PNG" --out "${ICONSET}/icon_512x512.png"
sips -z 1024 1024 "$SOURCE_PNG" --out "${ICONSET}/icon_512x512@2x.png"

# Convert iconset to icns
iconutil -c icns "$ICONSET" -o "$DEST_ICNS"

# Clean up
rm -rf "$ICONSET"

echo "Icon conversion complete: $DEST_ICNS"
