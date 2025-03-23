import os
import cv2
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Change this line:
model = genai.GenerativeModel("gemini-1.5-flash")


# Camera parameters (calibrate these for your camera)
FOCAL_LENGTH = 800  # Pixels (example value - calibrate for your camera)
KNOWN_WIDTHS = {  # Real-world widths in centimeters
    "person": 50,
    "bottle": 10,
    "chair": 40,
    "cup": 8,
}


def calculate_distance(pixel_width, real_width):
    """Calculate distance using perspective projection formula"""
    return (real_width * FOCAL_LENGTH) / pixel_width


def get_pixel_width(image):
    """Use OpenCV to detect object width (simplified example)"""
    # Convert to grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Get largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    return w


def capture_image():
    """Capture image from webcam"""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None


def main():
    # Capture image
    image = capture_image()
    if image is None:
        print("Failed to capture image")
        return

    # Convert numpy ndarray to PIL Image
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Get object detection from Gemini
    response = model.generate_content(
        ["Describe the main object in this image and its approximate size.", image_pil]
    )

    # Parse Gemini response
    response_text = response.text.lower()
    detected_object = next((obj for obj in KNOWN_WIDTHS if obj in response_text), None)

    if not detected_object:
        print("No known object detected")
        return

    # Get pixel measurements
    pixel_width = get_pixel_width(image)
    if not pixel_width:
        print("Couldn't measure object width")
        return

    # Calculate distance
    real_width = KNOWN_WIDTHS[detected_object]
    distance = calculate_distance(pixel_width, real_width)

    print(f"Detected {detected_object} ({real_width}cm wide)")
    print(f"Pixel width: {pixel_width}px")
    print(f"Estimated distance: {distance/100:.2f} meters")


if __name__ == "__main__":
    main()