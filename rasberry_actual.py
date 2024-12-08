from flask import Flask, request, jsonify
import cv2
from ultralytics import YOLO
import os
import time
import requests

# Flask app
app = Flask(__name__)

# Load YOLO model
model = YOLO('yolov8s.pt')

# Camera indices
camera_indices = [0, 1, 2]  # Adjust based on your setup
output_folder = "raspberry_images"
os.makedirs(output_folder, exist_ok=True)

# Server configuration
post_url = "http://127.0.0.1:8000/receive_picture"  # Replace with your Django server URL

def search_object(search_object):
    """
    Search for the object in camera feeds.
    """
    attempts = 3
    found = False

    for attempt in range(attempts):
        print(f"Attempt {attempt + 1} of {attempts} to search for: {search_object}")
        cameras = [cv2.VideoCapture(idx) for idx in camera_indices]
        try:
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
                        if search_object.lower() == label.lower():
                            found = True

                            # Draw bounding box and label
                            x1, y1, x2, y2 = map(int, obj[:4])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                            # Save snapshot
                            output_path = os.path.join(output_folder, f"{search_object}_Camera{idx}.jpg")
                            cv2.imwrite(output_path, frame)
                            print(f"Object '{search_object}' found. Saved snapshot to {output_path}.")

                            # Post the image to the server
                            files = {'file': open(output_path, 'rb')}
                            data = {'camera_index': idx}
                            try:
                                post_response = requests.post(post_url, files=files, data=data)
                                print(f"Posted image to server with status code: {post_response.status_code}")
                            except Exception as e:
                                print(f"Error posting image: {e}")
                            break

                if found:
                    break
            if found:
                return True

        finally:
            # Release cameras after the search
            for cap in cameras:
                cap.release()

        print(f"Object '{search_object}' not found. Retrying...")
        time.sleep(5)

    # If not found after all attempts
    if not found:
        try:
            data = {'message': f"Object '{search_object}' not found in any camera frames."}
            post_response = requests.post(post_url, json=data)
            print(f"Posted absence message to server with status code: {post_response.status_code}")
        except Exception as e:
            print(f"Error posting absence message: {e}")

    return False


@app.route('/search_object', methods=['POST'])
def handle_request():
    """
    Handle incoming POST requests to search for an object.
    """
    data = request.json
    if not data or 'item_name' not in data:
        return jsonify({"error": "Invalid request. Please provide 'item_name'."}), 400

    item_name = data['item_name']
    print(f"Received request to search for: {item_name}")
    success = search_object(item_name)

    if success:
        return jsonify({"message": f"Object '{item_name}' found and processed."}), 200
    else:
        return jsonify({"message": f"Object '{item_name}' not found after 3 attempts."}), 404


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
