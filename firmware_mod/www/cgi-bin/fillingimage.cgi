#!/bin/sh

# Define the path to the temporary file
INPUT_FILE="/tmp/filling_image_input.jpg"

# Define the path for the output file
OUTPUT_FILE="/tmp/filling_image_output.webp"

if [ ! -f "/system/sdcard/config/filling.conf" ]; then
  $(cp /system/sdcard/config/filling.conf.dist /system/sdcard/config/filling.conf)
fi
source /system/sdcard/config/filling.conf

# echo "currentRegion:${region_of_interest}"
# echo "serverImage:${server_image}"
# echo "thresholdMin:${threshold_min}"
# echo "thresholdMax:${threshold_max}"
# echo "levelLow:${level_low}"
# echo "levelMedium:${level_medium}"
# echo "colorLow:${color_low}"
# echo "colorMedium:${color_medium}"
# echo "colorFull:${color_full}"
ENCODED_REGION=$(echo "${region_of_interest}" | jq -sRr @uri)
ENCODED_COLOR_LOW=$(echo "${color_low}" | jq -sRr @uri)
ENCODED_COLOR_MEDIUM=$(echo "${color_medium}" | jq -sRr @uri)
ENCODED_COLOR_FULL=$(echo "${color_full}" | jq -sRr @uri)
ENCODED_COLOR_BOX=$(echo "${color_box}" | jq -sRr @uri)

# Ensure server_image ends with a "/"
if [ "${server_image: -1}" != "/" ]; then
  server_image="${server_image}/"
fi

# Capture the image and save it to the temporary file
/system/sdcard/bin/getimage > "$INPUT_FILE"

# Use curl to send the original image to the REST API silently
curl -s -X 'POST' \
  "${server_image}?region=${ENCODED_REGION}&threshold_min=${threshold_min}&threshold_max=${threshold_max}&levelLow=${level_low}&levelMedium=${level_medium}&colorLow=${ENCODED_COLOR_LOW}&colorMedium=${ENCODED_COLOR_MEDIUM}&colorFull=${ENCODED_COLOR_FULL}&colorBox=${ENCODED_COLOR_BOX}" \
  -o "$OUTPUT_FILE" \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F "image=@$INPUT_FILE;type=image/jpeg"


# Set the content type for the response
echo "Content-type: image/webp"
echo ""

# Output the output file path
cat "$OUTPUT_FILE"
