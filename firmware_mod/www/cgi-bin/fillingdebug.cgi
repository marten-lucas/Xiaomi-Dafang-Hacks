#!/bin/sh

# Parse the QUERY_STRING environment variable to get the step parameter
QUERY_STRING=${QUERY_STRING:-""}
PARAMS=$(echo $QUERY_STRING | tr '&' '\n')

# Initialize variable to hold the step value
step=""

# Loop through the parameters to find the step value
for param in $PARAMS; do
    case $param in
        step=*) step="${param#step=}" ;; # Extract value after 'step='
    esac
done

# Define the path to the temporary file
INPUT_FILE="/tmp/filling_image_input.jpg"

# Define the path for the output file
OUTPUT_FILE="/tmp/filling_image_debug_${step}.webp"

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

# Ensure debug ends with a "/"
if [ "${server_debug: -1}" != "/" ]; then
  server_debug="${server_debug}/"
fi

# Capture the image and save it to the temporary file
/system/sdcard/bin/getimage > "$INPUT_FILE"

# Use curl to send the original image to the REST API silently
curl -s -X 'POST' \
  "${server_debug}?region=${ENCODED_REGION}&threshold_min=${threshold_min}&threshold_max=${threshold_max}&process_step=${step}" \
  -o "$OUTPUT_FILE" \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F "image=@$INPUT_FILE;type=image/jpeg"


# Set the content type for the response
echo "Content-type: image/webp"
echo ""

# Output the output file path
cat "$OUTPUT_FILE"