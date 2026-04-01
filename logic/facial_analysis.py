"""Facial analysis logic for the EmoTrack app using on-device ML."""

import os
import cv2
import numpy as np
import onnxruntime as ort

EMOTION_LABELS = ["ANGRY", "DISGUSTED", "FEAR", "HAPPY", "SAD", "SURPRISED", "CALM"]

# Load ONNX model
_model_path = os.path.join(os.path.dirname(__file__), "..", "models", "emotion_model.onnx")
session = ort.InferenceSession(_model_path)

# Load OpenCV face detector
_cascade_path = os.path.join(
    os.path.dirname(cv2.__file__), "data", "haarcascade_frontalface_default.xml"
)
face_cascade = cv2.CascadeClassifier(_cascade_path)


def detect_emotion(frame):
    """Detects the emotion of a face in a frame using on-device ML.

    Args:
        frame: BGR image as numpy array from OpenCV.

    Returns:
        Emotion label string (e.g. "HAPPY") or "NO FACE" if no face detected.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return "NO FACE"

    # Use the largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_roi = gray[y : y + h, x : x + w]

    # Preprocess for model: resize to 48x48, normalize
    face_resized = cv2.resize(face_roi, (48, 48))
    face_normalized = face_resized.astype(np.float32) / 255.0
    face_input = face_normalized.reshape(1, 1, 48, 48)

    # Run inference
    outputs = session.run(None, {"input": face_input})
    emotion_idx = int(np.argmax(outputs[0], axis=1)[0])

    return EMOTION_LABELS[emotion_idx]
