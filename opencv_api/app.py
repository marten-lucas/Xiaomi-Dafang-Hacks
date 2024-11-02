from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import numpy as np
import cv2
import imutils
from datetime import datetime
import matplotlib.pyplot as plt
from enum import Enum 
import io

app = FastAPI()

def parse_region(region):
    """Parse and validate region string input to ensure it contains four integers."""
    region_split = list(map(int, region.split(',')))
    if len(region_split) != 4:
        raise ValueError("Region must contain four integers: x1,y1,x2,y2")
    return region_split

def image_preprocess(image, region):
    # Parse region and extract coordinates
    x1, y1, x2, y2 = parse_region(region)
    
    # Convert to grayscale
    img_ready = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur
    img_ready = cv2.GaussianBlur(img_ready, (7, 7), 0)

    # Crop the image based on the region of interest
    img_ready = img_ready[y1:y2, x1:x2]
    # Invert the image
    img_ready = cv2.bitwise_not(img_ready)

    return img_ready

def apply_threshold(image, min_limit, max_limit):
    # Apply binary threshold
    _, img_ready = cv2.threshold(image, min_limit, max_limit, cv2.THRESH_BINARY)

    # Apply morphological opening to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    img_ready = cv2.morphologyEx(img_ready, cv2.MORPH_OPEN, kernel)

    return img_ready

def find_contours(image):
    contours = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    return contours

def get_biggest_contour(image):
    # Find contours
    contours = find_contours(image)

    # Sort contours by area (largest last)
    if contours:
        contours = sorted(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contours[-1])
        return x, y, w, h
    else:
        raise ValueError("No contours found in image.")

def hex_to_bgr(hex):
    hex = hex.lstrip('#')
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    return rgb[::-1]  # Reverse to get BGR


def draw_contour(image, region, h, color):
    # Parse region and extract coordinates
    x1, y1, x2, y2 = parse_region(region)
    # Draw a rectangle around the detected contour
    cv2.rectangle(image, (x2, y2), (x1, y2 - h), hex_to_bgr(color), 2)
    return image

def draw_region(image_cv, region, color):
    # Parse region and extract coordinates
    x1, y1, x2, y2 = parse_region(region)
    # Draw a rectangle indicating the specified region
    cv2.rectangle(image_cv, (x1, y1), (x2, y2), hex_to_bgr(color), 2)

def filling_level_get(height, region):
    # Parse region and extract coordinates
    _, _, _, y2 = parse_region(region)
    # Calculate filling level as a percentage of the total height
    filling_level = (height / y2) * 100 if y2 else 0
    return round(filling_level, 1)  # Round to 1 decimal place


def filling_color_get(level, valueLow, valueMid, colorLow, colorMedium, colorFull):
    if level <= valueLow:
        return colorLow
    elif level <= valueMid:
        return colorMedium
    else:
        return colorFull

def calculate_capacity(filling_level, capacity):
    used_capacity = round((filling_level / 100) * capacity)
    remaining_capacity = round(capacity - used_capacity)
    return used_capacity, remaining_capacity



@app.post("/filling-image/")
async def filling_image(
    image: UploadFile = File(...),
    region: str = "",
    threshold_min: int = 0,
    threshold_max: int = 255,
    levelLow: int = 10,
    levelMedium: int = 50,
    colorLow: str = "#FF0000",  
    colorMedium: str = "#FFFF00",  
    colorFull: str = "#00FF00",  
    colorBox: str = "#0000FF"
):
    # Read the uploaded image
    image_data = await image.read()
    
    # Save the uploaded image temporarily
    processed_image_path = "uploaded_image.jpg"
    with open(processed_image_path, "wb") as f:
        f.write(image_data)

    # Load the image with OpenCV
    image_cv = cv2.imread(processed_image_path)

    if region:
        # Draw a rectangle around the region of interest
        draw_region(image_cv, region, colorBox)

        # Preprocess the image for filling detection
        image_ready = image_preprocess(image_cv, region)

        # Apply thresholding
        image_thresh = apply_threshold(image_ready, threshold_min, threshold_max)

        # Find and draw contour
        try:
            x, y, w, h = get_biggest_contour(image_thresh)
            filling_level = filling_level_get(h, region)
            filling_color = filling_color_get(filling_level, levelLow, levelMedium, colorLow, colorMedium, colorFull)
            img_result = draw_contour(image_cv, region, h, filling_color)

        except ValueError as e:
            return {"error": str(e)}

        # Save the annotated image as PNG
        modified_image_path = "modified_image.webp"
        cv2.imwrite(modified_image_path, img_result, [cv2.IMWRITE_WEBP_QUALITY, 90])  # Set quality between 0 and 100

        # Return the modified image with the rectangle and contour
        return FileResponse(modified_image_path, media_type='image/webp')

    # Return the uploaded image if no region was provided
    return FileResponse(processed_image_path, media_type='image/webp')

@app.post("/filling-data/")
async def filling_data(
    image: UploadFile = File(...),
    region: str = "",
    threshold_min: int = 0,
    threshold_max: int = 255,
    capacity: int = 1000,  # Default tank capacity in liters
    zipcode: str = ""
):
    # Read and save the uploaded image
    image_data = await image.read()
    processed_image_path = "uploaded_image.jpg"
    with open(processed_image_path, "wb") as f:
        f.write(image_data)
    image_cv = cv2.imread(processed_image_path)

    # Process the image to detect filling level
    if region:
        image_ready = image_preprocess(image_cv, region)
        image_thresh = apply_threshold(image_ready, threshold_min, threshold_max)

        try:
            x, y, w, h = get_biggest_contour(image_thresh)
            filling_level = filling_level_get(h, region)
            used_capacity, remaining_capacity = calculate_capacity(filling_level, capacity)

        except ValueError as e:
            return {"error": str(e)}

        return {
            "filling_level": filling_level,
            "remaining_capacity": remaining_capacity,
            "used_capacity": used_capacity,
            "oilprice": "0",
            "refillprice": "0",
            "ts_lastupdate": datetime.utcnow().isoformat()
        }

    return {"error": "Region parameter is required"}

# Enum for process steps
class ProcessStep(str, Enum):
    preprocess = "preprocess"
    threshold = "threshold"
    contour = "contour"

# Debug endpoint
@app.post("/filling-debug/")
async def debug_image(
    image: UploadFile = File(...),
    threshold_min: int = 0,
    threshold_max: int = 255,
    process_step: ProcessStep = ProcessStep.preprocess,
    region: str = "692,21,712,681"  # Default region for simplicity
):
    # Read the uploaded image
    image_data = await image.read()
    nparr = np.frombuffer(image_data, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Process the image based on step
    if process_step == ProcessStep.preprocess:
        img_ready = image_preprocess(img_cv, region)
        modified_image_path = "debug_preprocess_image.webp"
        cv2.imwrite(modified_image_path, img_ready, [cv2.IMWRITE_WEBP_QUALITY, 90])  # Set quality between 0 and 100
        return FileResponse(modified_image_path, media_type='image/webp')

    elif process_step == ProcessStep.threshold:
        img_ready = image_preprocess(img_cv, region)
        # Generate histogram as an image
        plt.hist(img_ready.ravel(), bins=256, range=(0, 256), color="gray")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.axvline(threshold_min, color='r', linestyle='dashed', linewidth=2, label='Threshold Min')
        plt.axvline(threshold_max, color='r', linestyle='dashed', linewidth=2, label='Threshold Max')
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        temp_file_path = "/tmp/debug_histogram_image.webp"
        with open(temp_file_path, "wb") as f:
            f.write(buf.getvalue())
        return FileResponse(temp_file_path, media_type="image/webp")

    elif process_step == ProcessStep.contour:
        img_ready = image_preprocess(img_cv, region)
        img_thresholded = apply_threshold(img_ready, threshold_min, threshold_max)
        contours = find_contours(img_thresholded)
        img_contours = cv2.cvtColor(img_thresholded, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 2)
        
        modified_image_path = "debug_contours_image.webp"
        cv2.imwrite(modified_image_path, img_contours, [cv2.IMWRITE_WEBP_QUALITY, 90])  # Set quality between 0 and 100
        return FileResponse(modified_image_path, media_type='image/webp')

    return JSONResponse({"error": "Invalid process step"}, status_code=400)