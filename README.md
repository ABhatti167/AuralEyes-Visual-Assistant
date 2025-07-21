# AuralEyes

**AuralEyes** is a mobile assistive application designed to help visually impaired users better understand their surroundings. Using real-time object detection and natural language description, the app captures scenes through the device’s camera and provides audio feedback to describe what it sees.

## 🧠 How It Works

1. The user captures an image via the app.
2. The image is sent to a Flask backend.
3. YOLOv7 performs object detection on the image.
4. Detected objects and context are passed to the Gemini API.
5. Gemini generates a natural-language description.
6. The description is converted to speech and played back to the user.

## 🔧 Tech Stack

- **Frontend:** React Native
- **Backend:** Flask (Python)
- **AI/ML:**
  - YOLOv7 for object detection
  - Gemini API for language generation
- **Audio:** Native Text-to-Speech modules

## 🚀 Features

- Real-time object detection from the camera
- Intelligent scene understanding
- Descriptive, natural-sounding voice feedback
- Lightweight and mobile-friendly design
- Easy deployment and modular backend

## 📦 Use Cases

- Assisting blind and low-vision users with daily tasks
- Real-time awareness in unfamiliar environments
- Indoor object identification and navigation support
