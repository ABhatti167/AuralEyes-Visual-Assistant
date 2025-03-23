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
model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")

# Camera parameters (calibrate these for your camera)
FOCAL_LENGTH = 800  # Pixels (example value - calibrate for your camera)
KNOWN_WIDTHS = {  # Real-world widths in centimeters
    "pumpkin": 30,  # Example width, change to actual known object width
}


def calculate_distance(pixel_width, real_width):
    """Calculate distance using perspective projection formula"""
    return (real_width * FOCAL_LENGTH) / pixel_width


def get_pixel_width(image):
    """Use OpenCV to detect object width for each bounding box"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.append((x, y, w, h))

    return bounding_boxes


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

    # Convert numpy ndarray to PIL Image for Gemini
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Get object detection from Gemini
    response = model.generate_content(
        ["Describe the main object in this image and its approximate size.", image_pil]
    )

    # Parse Gemini response for object names and distances (optional)
    response_text = response.text.lower()
    print("Gemini Response:", response_text)  # See how Gemini responds

    detected_objects = []
    for obj in KNOWN_WIDTHS:
        if obj in response_text:
            detected_objects.append(obj)

    if not detected_objects:
        print("No known objects detected")
        return

    # Get pixel measurements and calculate distances for each bounding box
    bounding_boxes = get_pixel_width(image)
    for i, (x, y, w, h) in enumerate(bounding_boxes):
        if i < len(detected_objects):
            detected_object = detected_objects[i]
            pixel_width = w
            real_width = KNOWN_WIDTHS[detected_object]
            distance = calculate_distance(pixel_width, real_width)

            print(f"Detected {detected_object} ({real_width}cm wide)")
            print(f"Bounding Box: {x}, {y}, {w}, {h}")
            print(f"Estimated distance: {distance/100:.2f} meters")
            print(f"Distance in cm: {distance:.2f} cm")


if __name__ == "__main__":
    main()