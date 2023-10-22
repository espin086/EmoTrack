"""EmoTrack"""


import streamlit as st
import cv2
import sqlite3
from datetime import datetime
import pytz

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from logic.facial_analysis import detect_emotion


BATCH_SIZE = 60


# Function to save a list of emotions to SQLite
def save_emotions_batch(emotions_batch):
    """Save a list of emotions to SQLite"""
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

st.title("EmoTrack")
# Sidebar for navigation
menu = st.sidebar.radio("Choose a Function", ["Webcam Feed", "Display Graph"])


if menu == "Webcam Feed":
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
                if current_emotion != "NO FACE":
                    emotions_batch.append(
                        (
                            datetime.now().timestamp(),
                            current_emotion,
                        )
                    )

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
        conn.close()

elif menu == "Display Graph":
    st.write("## Emotion Variation per Day")

    with sqlite3.connect("emotions.db") as conn:
        query = """
        SELECT
            DATE(DATETIME(timestamp, 'unixepoch')) as date,
            emotion,
            COUNT(emotion) as emotion_count
        FROM
            emotions
        GROUP BY
            date,
            emotion
        ORDER BY
            date DESC,
            emotion_count DESC;
        """
        df = pd.read_sql_query(query, conn)

    # Calculate the total counts for each date
    total_counts = df.groupby("date")["emotion_count"].sum().reset_index()
    total_counts.rename(columns={"emotion_count": "total_count"}, inplace=True)

    # Merge the total counts back into the original dataframe
    df = pd.merge(df, total_counts, on="date")

    # Calculate the percentage for each emotion on each date
    df["percentage"] = (df["emotion_count"] / df["total_count"]) * 100

    # Initialize the figure and axis
    fig, ax = plt.subplots(figsize=(14, 6))
    bottom_values = {date: 0 for date in df["date"].unique()}

    emotion_colors = {
        "CALM": "#D3D3D3",
        "SURPRISED": "#A9A9A9",
        "CONFUSED": "#808080",
        "HAPPY": "#696969",
        "SAD": "#800000",
        "ANGRY": "#8B0000",
        "FEAR": "#A52A2A",
    }

    for emotion in df["emotion"].unique():
        emotion_data = df[df["emotion"] == emotion].copy()
        bottoms = [bottom_values.get(date, 0) for date in emotion_data["date"]]
        bars = ax.bar(
            emotion_data["date"],
            emotion_data["percentage"],
            bottom=bottoms,
            color=emotion_colors.get(emotion, "white"),
        )

        for i, date in enumerate(emotion_data["date"]):
            bottom_values[date] += emotion_data.iloc[i]["percentage"]

        # Adding text labels
        for bar, percentage in zip(bars, emotion_data["percentage"]):
            height = bar.get_height()
            position = bar.get_y()
            if height > 0:
                text_color = (
                    "black"
                    if emotion in ["CALM", "SURPRISED", "CONFUSED", "HAPPY"]
                    else "white"
                )
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    position + height / 2,
                    emotion,
                    ha="center",
                    va="center",
                    color=text_color,
                )

    ax.set_title("Emotion Variation in the Past 7 Days (100% Stacked)")
    ax.set_xticklabels(df["date"].unique(), rotation=45)
    plt.legend(df["emotion"].unique())
    st.pyplot(fig)
