#!/bin/sh

# Define the path to the temporary file
INPUT_FILE="/tmp/filling_image_input.jpg"
OUTPUT_FILE="/tmp/filling_data_output.json"

if [ ! -f "/system/sdcard/config/filling.conf" ]; then
  $(cp /system/sdcard/config/filling.conf.dist /system/sdcard/config/filling.conf)
fi
source /system/sdcard/config/filling.conf

# echo "currentRegion:${region_of_interest}"
# echo "serverData:${server_data}"
# echo "thresholdMin:${threshold_min}"
# echo "thresholdMax:${threshold_max}"
ENCODED_REGION=$(echo "${region_of_interest}" | jq -sRr @uri)

# Ensure server_data ends with a "/"
if [ "${server_data: -1}" != "/" ]; then
  server_data="${server_data}/"
fi

# Capture the image and save it to the temporary file
/system/sdcard/bin/getimage > "$INPUT_FILE"

# Use curl to send the original image to the REST API silently
curl -s -X 'POST' \
  "${server_data}?region=${ENCODED_REGION}&threshold_min=${threshold_min}&threshold_max=${threshold_max}" \
  -o "$OUTPUT_FILE" \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F "image=@$INPUT_FILE;type=image/jpeg"


# Set the content type for the response
echo "Content-type: application/json"
echo ""

# Output the output file path
cat "$OUTPUT_FILE"
