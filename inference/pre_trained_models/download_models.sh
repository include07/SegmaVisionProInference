#!/bin/bash
set -e  # Exit on any error
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v ngc &> /dev/null; then
    echo -e "${RED}Error: NGC CLI is not installed.${NC}"
    exit 1
fi

if ! ngc config current &> /dev/null; then
    echo -e "${RED}Error: Not logged in to NGC.${NC}"
    exit 1
fi

echo -e "${YELLOW}Downloading Mask Grounding DINO model...${NC}"

# Download first model to a temporary directory
TEMP_DIR1=$(mktemp -d)
ngc registry model download-version "nvidia/tao/mask_grounding_dino:mask_grounding_dino_swin_tiny_commercial_trainable_v1.0" \
    --dest "$TEMP_DIR1"

# Find the .pth model file and move it to script directory
MODEL_FILE1=$(find "$TEMP_DIR1" -name "*.pth" -type f | head -1)

if [ -n "$MODEL_FILE1" ]; then
    MODEL_NAME1=$(basename "$MODEL_FILE1")
    mv "$MODEL_FILE1" "$SCRIPT_DIR/$MODEL_NAME1"
    echo -e "${GREEN}✓ Mask Grounding DINO model saved to: $SCRIPT_DIR/$MODEL_NAME1${NC}"
    
    # Clean up temporary directory
    rm -rf "$TEMP_DIR1"
else
    echo -e "${RED}Error: No .pth file found in Mask Grounding DINO download${NC}"
    rm -rf "$TEMP_DIR1"
    exit 1
fi

echo -e "${YELLOW}Downloading Grounding DINO model...${NC}"

# Download second model to a temporary directory
TEMP_DIR2=$(mktemp -d)
ngc registry model download-version "nvidia/tao/grounding_dino:grounding_dino_swin_tiny_commercial_trainable_v1.0" \
    --dest "$TEMP_DIR2"

# Find the .pth model file and move it to script directory
MODEL_FILE2=$(find "$TEMP_DIR2" -name "*.pth" -type f | head -1)

if [ -n "$MODEL_FILE2" ]; then
    MODEL_NAME2=$(basename "$MODEL_FILE2")
    mv "$MODEL_FILE2" "$SCRIPT_DIR/$MODEL_NAME2"
    echo -e "${GREEN}✓ Grounding DINO model saved to: $SCRIPT_DIR/$MODEL_NAME2${NC}"
    
    # Clean up temporary directory
    rm -rf "$TEMP_DIR2"
else
    echo -e "${RED}Error: No .pth file found in Grounding DINO download${NC}"
    rm -rf "$TEMP_DIR2"
    exit 1
fi

echo -e "${GREEN}All downloads complete!${NC}"