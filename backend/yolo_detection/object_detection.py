import os

from ultralytics import YOLO
import cv2
import mediapipe as mp
import time
import math
from flask import Flask, request
from flask_cors import CORS

app = Flask("aural_eyes_app")
CORS(app)

@app.route("/detect", methods=['POST'])
def detect_objects():

    yolo_model = YOLO("yolov8n.pt")

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    # Reference sizes for common objects (cm)
    reference_sizes = {
        "person": 170,
        "chair": 80,
        "dining table": 75,
        "couch": 90,
        "bed": 60,
        "refrigerator": 180,
        "tv": 55,
        "laptop": 35,
        "cell phone": 15,
        "book": 25,
        "bottle": 25,
    }

    def estimate_distance_from_size(obj_class, bbox_height, frame_height):
        """
        Estimate distanes based on object size and comera parameters

        """

        if obj_class not in reference_sizes:
            return None

        real_height_cm = reference_sizes[obj_class]

        # Simple pinhole camera model approximation
        # Assuming 60 degree vertical FOV
        # Would need proper calibration for specific camera and better results
        focal_length_pix = frame_height / (2 * math.tan(math.radians(30)))

        distance_cm = (real_height_cm * focal_length_pix) / bbox_height

        calib_factor = 0.01 # converts to meters and applies calibration
        distance_m = distance_cm * calib_factor

        return distance_m

    cap = cv2.VideoCapture(0)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # MediaPipe Posing
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:

        # Performance tracking
        frame_times = []

        while cap.isOpened():

            start_time = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pose_results = pose.process(frame_rgb)

            yolo_results = yolo_model(frame)

            for result in yolo_results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0]) # confidence score
                    cls_id = int(box.cls[0])
                    label = result.names[cls_id]

                    bbox_height = y2 - y1

                    distance = estimate_distance_from_size(label, bbox_height, frame_height)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    cv2.putText(frame, f"{label}: {conf:.2f}",
                                (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    if distance is not None:
                        cv2.putText(frame, f"Dist: {distance:.2f}m",
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # display mp pose results if detected
            if pose_results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    pose_results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                if pose_results.pose_landmarks:

                    # get nose landmark
                    nose = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]

                    # use shoulder width as reference
                    left_shoulder =  pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                    right_shoulder =  pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]

                    if left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5:

                        shoulder_width_px = abs(left_shoulder.x - right_shoulder.x) * frame_width

                        # average human shoulder width is 40cm
                        # using pinhole camera mdoel
                        focal_length_px = frame_width / (2 * math.tan(math.radians(30)))
                        distance_cm = (40 * focal_length_px) / shoulder_width_px
                        distance_m = distance_cm / 100

                        # calibration factor
                        calibrated_distance = distance_m * 0.8

                        # Display person distance
                        nose_x = int(nose.x * frame_width)
                        nose_y = int(nose.y * frame_height)
                        cv2.putText(frame, f"Person: {calibrated_distance:.2f}m",
                                    (nose_x, nose_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


            # calculate FPS
            end_time = time.time()
            frame_time = end_time - start_time
            frame_times.append(frame_time)

            if len(frame_times) > 30:
                frame_times.pop(0)

            avg_frame_time = sum(frame_times) / len(frame_times)

            fps = 1 / avg_frame_time

            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Object Detection with Distance", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
    # detect_objects()

