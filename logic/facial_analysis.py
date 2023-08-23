import boto3
import cv2
import numpy as np

client = boto3.client("rekognition")


def detect_emotion(frame):
    # Encode the frame as JPG
    ret, jpg_data = cv2.imencode(".jpg", frame)
    if not ret:
        raise ValueError("Failed to encode frame")

    # Convert the frame to bytes
    image_bytes = jpg_data.tobytes()

    response = client.detect_faces(
        Image={"Bytes": image_bytes}, Attributes=["EMOTIONS"]
    )

    # Check if any faces were detected
    if not response["FaceDetails"]:
        return "NO FACE"

    return response["FaceDetails"][0]["Emotions"][0]["Type"]
