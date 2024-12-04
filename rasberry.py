import cv2
from ultralytics import YOLO
import os
import time
import requests

# Load YOLO model
model = YOLO('yolov8s.pt')

# Camera and output settings
camera_indices = [0, 1, 2]  # Adjust based on your setup
output_folder = "raspberry_images"
os.makedirs(output_folder, exist_ok=True)

# Open cameras
cameras = [cv2.VideoCapture(idx) for idx in camera_indices]
time.sleep(2)  # Allow cameras to stabilize

# Collect object data
object_data = []
for idx, cap in enumerate(cameras):
    ret, frame = cap.read()
    if not ret:
        print(f"Camera {idx + 1} failed to capture a frame.")
        continue

    results = model(frame)
    for result in results:
        for obj in result.boxes.data:
            class_id = int(obj[5])
            label = result.names[class_id]

            x1, y1, x2, y2 = map(int, obj[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            object_data.append({
                "camera": f"Camera {idx + 1}",
                "camera_index": idx,
                "frame": frame.copy(),
                "object": label
            })

    print(f"Objects detected by Camera {idx + 1}: {', '.join(set([data['object'] for data in object_data]))}")

# Release all cameras
for cap in cameras:
    cap.release()

# Search and send data
search_object = input("Enter the object to search: ").lower()
found = False

for data in object_data:
    if search_object == data["object"].lower():
        found = True
        camera_index = data["camera_index"]
        frame = data["frame"]

        # Save frame locally
        output_path = os.path.join(output_folder, f"{search_object}_Camera{camera_index}.jpg")
        cv2.imwrite(output_path, frame)

        # Send image to server
        url = "http://127.0.0.1:8000/pictures/"
        files = {'file': open(output_path, 'rb')}
        data = {'camera_index': camera_index}
        response = requests.post(url, files=files, data=data)

        print(f"Sent image from Camera {camera_index} with status code: {response.status_code}")
        print(response.json())

if not found:
    print(f"Object '{search_object}' not found.")
