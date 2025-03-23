import os
import asyncio
import json
import cv2
import numpy as np
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
import av
from ultralytics import YOLO
import mediapipe as mp
import math
import time
from aiohttp import web
import socketio

# Create Socket.io server
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
app = web.Application()
sio.attach(app)

# Load models
yolo_model = YOLO("yolov8n.pt")
mp_pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Store active peer connections
active_connections = {}

# Reference sizes for common objects (cm)
reference_sizes = {
    "person": 170, "chair": 80, "dining table": 75, "couch": 90,
    "bed": 60, "refrigerator": 180, "tv": 55, "laptop": 35,
    "cell phone": 15, "book": 25, "bottle": 25,
}

def estimate_distance_from_size(obj_class, bbox_height, frame_height):
    """Estimate distances based on object size and camera parameters"""
    if obj_class not in reference_sizes:
        return None

    real_height_cm = reference_sizes[obj_class]
    focal_length_pix = frame_height / (2 * math.tan(math.radians(30)))
    distance_cm = (real_height_cm * focal_length_pix) / bbox_height
    calib_factor = 0.01  # converts to meters and applies calibration
    distance_m = distance_cm * calib_factor

    return distance_m

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from another track.
    """

    kind = "video"

    def __init__(self, track, sid):
        super().__init__()
        self.track = track
        self.sid = sid
        self.frame_count = 0
        self.frame_times = []
        self.last_sent_time = 0

    async def recv(self):
        frame = await self.track.recv()

        # Convert frame to CV2 format
        img = frame.to_ndarray(format="bgr24")
        frame_height, frame_width = img.shape[0], img.shape[1]

        current_time = time.time()
        # Only process every N frames to maintain performance
        # or process at most X times per second
        if current_time - self.last_sent_time >= 0.2:  # 5 times per second
            try:
                # Process with YOLO
                yolo_results = yolo_model(img)
                detected_objects = []

                for result in yolo_results:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        label = result.names[cls_id]

                        if conf < 0.4:  # Filter out low confidence detections
                            continue

                        bbox_height = y2 - y1
                        distance = estimate_distance_from_size(label, bbox_height, frame_height)

                        detected_objects.append({
                            "label": label,
                            "confidence": float(conf),
                            "distance": float(distance) if distance else None,
                            "bbox": [int(x1), int(y1), int(x2), int(y2)]
                        })

                # Process with MediaPipe Pose
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pose_results = mp_pose.process(img_rgb)
                person_data = None

                if pose_results.pose_landmarks:
                    # Get person distance from shoulder width
                    nose = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE]
                    left_shoulder = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
                    right_shoulder = pose_results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]

                    if left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5:
                        shoulder_width_px = abs(left_shoulder.x - right_shoulder.x) * frame_width
                        focal_length_px = frame_width / (2 * math.tan(math.radians(30)))
                        distance_cm = (40 * focal_length_px) / shoulder_width_px
                        distance_m = distance_cm / 100 * 0.8  # Apply calibration factor

                        # Add person data to detections if a person isn't already in the list
                        person_exists = False
                        for obj in detected_objects:
                            if obj["label"] == "person":
                                person_exists = True
                                if not obj["distance"] and distance_m:
                                    obj["distance"] = float(distance_m)
                                break

                        if not person_exists:
                            detected_objects.append({
                                "label": "person",
                                "confidence": 0.95,
                                "distance": float(distance_m)
                            })

                # Calculate FPS
                self.frame_count += 1
                self.frame_times.append(time.time())

                # Keep only last 30 frames for FPS calculation
                if len(self.frame_times) > 31:
                    self.frame_times.pop(0)

                if len(self.frame_times) > 1:
                    fps = (len(self.frame_times) - 1) / (self.frame_times[-1] - self.frame_times[0])
                else:
                    fps = 0

                # Send results to the client
                results = {
                    "detections": detected_objects,
                    "fps": float(fps)
                }

                asyncio.ensure_future(sio.emit('detection-results', results, room=self.sid))
                self.last_sent_time = current_time

            except Exception as e:
                print(f"Error processing frame: {e}")

        # Return the frame unmodified for streaming
        # Or you could add annotations if you want to send processed frames back
        return frame

@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")
    active_connections[sid] = {
        "pc": None
    }

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    if sid in active_connections:
        pc = active_connections[sid].get("pc")
        if pc:
            await pc.close()
        del active_connections[sid]

@sio.event
async def offer(sid, data):
    try:
        print(f"Received offer from {sid}")
        pc = RTCPeerConnection()
        active_connections[sid]["pc"] = pc

        # Set the remote description
        await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))

        # Register data channel callback
        @pc.on("datachannel")
        def on_datachannel(channel):
            print(f"Data channel established for {sid}")
            active_connections[sid]["data_channel"] = channel

        # Register track callback
        @pc.on("track")
        def on_track(track):
            print(f"Track received from {sid}: {track.kind}")
            if track.kind == "video":
                # Create video processor track
                processor = VideoTransformTrack(track, sid)
                pc.addTrack(processor)

        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await sio.emit("answer", {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }, room=sid)

    except Exception as e:
        print(f"Error handling offer: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)

@sio.event
async def answer(sid, data):
    try:
        pc = active_connections[sid].get("pc")
        if pc:
            await pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))
    except Exception as e:
        print(f"Error handling answer: {e}")

@sio.event
async def ice_candidate(sid, data):
    try:
        pc = active_connections[sid].get("pc")
        if pc:
            candidate = RTCIceCandidate(
                sdpMLineIndex=data.get("sdpMLineIndex", 0),
                sdpMid=data.get("sdpMid", "0"),
                candidate=data["candidate"]
            )
            await pc.addIceCandidate(candidate)
    except Exception as e:
        print(f"Error handling ICE candidate: {e}")

async def cleanup_connections():
    """Periodic task to clean up stale connections"""
    while True:
        for sid in list(active_connections.keys()):
            pc = active_connections[sid].get("pc")
            if pc and pc.connectionState in ["failed", "closed"]:
                print(f"Cleaning up connection for {sid}")
                await pc.close()
                if sid in active_connections:
                    del active_connections[sid]
        await asyncio.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Start periodic cleanup task
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_connections())

    # Start the server
    web.run_app(app, host='0.0.0.0', port=port)
