import streamlit as st
import cv2
import sqlite3
from datetime import datetime
import numpy as np

EMOTIONS = ["happy", "sad", "neutral", "angry", "surprised"]
BATCH_SIZE = 60


# Mock function for emotion detection
def detect_emotion(frame):
    return np.random.choice(EMOTIONS)


# Function to save a list of emotions to SQLite
def save_emotions_batch(emotions_batch):
    with sqlite3.connect("emotions.db") as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)", emotions_batch
        )
        conn.commit()


# Create SQLite database if it doesn't exist
with sqlite3.connect("emotions.db") as conn:
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS emotions 
                  (timestamp INTEGER, emotion TEXT)"""
    )

st.title("Emotion Detector App")
st.write("## Webcam Feed")

# Initialize session state variable for running
if "running" not in st.session_state:
    st.session_state.running = False

# Side by side buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Start", key="start_button"):
        st.session_state.running = True

with col2:
    if st.button("Stop", key="stop_button"):
        st.session_state.running = False

# Style buttons
st.markdown(
    """
<style>
    [data-testid="stButton"][aria-label="Start"] {
        background-color: green;
        color: white;
    }
    [data-testid="stButton"][aria-label="Stop"] {
        background-color: red;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Webcam Feed Logic
if st.session_state.running:
    frame_slot = st.empty()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_count = 0
    current_emotion = None
    emotions_batch = []

    while st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            st.warning("Failed to get frame from webcam.")
            st.session_state.running = False
            break

        frame_count += 1

        if frame_count % 24 == 0:
            current_emotion = detect_emotion(frame)
            emotions_batch.append((datetime.now().timestamp(), current_emotion))

            if len(emotions_batch) == BATCH_SIZE:
                save_emotions_batch(emotions_batch)
                emotions_batch = []

        if current_emotion:
            cv2.putText(
                frame,
                current_emotion,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

        frame_slot.image(frame, channels="BGR", use_column_width=True)

    if emotions_batch:
        save_emotions_batch(emotions_batch)

    cap.release()
