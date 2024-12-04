import cv2
from ultralytics import YOLO
import os
import time
import requests

# Load YOLO model
model = YOLO('yolov8s.pt')

# Camera indices
camera_indices = [0, 1, 2]  # Adjust based on your setup
output_folder = "raspberry_images"
os.makedirs(output_folder, exist_ok=True)

# Server configuration
post_url = "http://127.0.0.1:8000/pictures"  # Replace with your Django server URL


def fetch_search_object():
    """
    Fetch the object to search for from the Django server or input.
    This function can be updated to poll a Django API or database.
    """
    try:
        # Example: Poll a Django API endpoint for the search object
        response = requests.get("http://127.0.0.1:8000/get_search_object")  # Replace with your endpoint
        if response.status_code == 200 and response.json().get("search_object"):
            return response.json()["search_object"].lower()
    except Exception as e:
        print(f"Error fetching search object: {e}")
    return None


while True:
    # Fetch the search object
    search_object = fetch_search_object()
    if not search_object:
        print("No search object received. Retrying in 5 seconds...")
        time.sleep(5)
        continue

    print(f"Searching for: {search_object}")
    found = False
    object_data = []  # Store object data for all cameras

    # Dynamically open cameras
    cameras = [cv2.VideoCapture(idx) for idx in camera_indices]
    try:
        for idx, cap in enumerate(cameras):
            ret, frame = cap.read()
            if not ret:
                print(f"Camera {idx + 1} failed to capture a frame.")
                continue

            camera_name = f"Camera {idx + 1}"
            results = model(frame)
            for result in results:
                for obj in result.boxes.data:
                    class_id = int(obj[5])
                    label = result.names[class_id]
                    if search_object == label.lower():
                        found = True

                        x1, y1, x2, y2 = map(int, obj[:4])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        # Save snapshot
                        output_path = os.path.join(output_folder, f"{search_object}_Camera{idx}.jpg")
                        cv2.imwrite(output_path, frame)
                        print(f"Object '{search_object}' found in {camera_name}. Saved snapshot to {output_path}.")

                        # Post the image to the server
                        files = {'file': open(output_path, 'rb')}
                        data = {'camera_index': idx}
                        try:
                            post_response = requests.post(post_url, files=files, data=data)
                            print(f"Posted image to server with status code: {post_response.status_code}")
                        except Exception as e:
                            print(f"Error posting image: {e}")
        
        if not found:
            print(f"Object '{search_object}' not found in any camera frames.")
    finally:
        # Release cameras after the search
        for cap in cameras:
            cap.release()
        print("Cameras released.")

    # Pause for a while before the next iteration
    time.sleep(5)
